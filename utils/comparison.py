import re
from collections import defaultdict

from database.db import get_collection
from utils.feature_extractor import normalize_text


UNKNOWN_VALUES = {"", None, "Unknown", "Unavailable"}
NOISE_TOKENS = {
    "laptop",
    "laptops",
    "mobile",
    "mobiles",
    "phone",
    "phones",
    "smartphone",
    "smartphones",
    "android",
    "notebook",
    "thin",
    "light",
    "windows",
    "window",
    "home",
    "office",
    "basic",
    "backlit",
    "keyboard",
    "display",
    "screen",
    "inch",
    "inches",
    "wifi",
    "bluetooth",
    "year",
    "with",
    "for",
    "and",
    "plus",
    "gen",
    "fhd",
    "wuxga",
    "oled",
    "qhd",
    "uhd",
    "displayport",
}
SEARCH_NOISE_TOKENS = {
    *NOISE_TOKENS,
    "smartphone",
    "storage",
    "gb",
    "tb",
    "black",
    "white",
    "blue",
    "green",
    "silver",
    "gray",
    "grey",
    "titanium",
    "elegant",
    "mobile",
    "phone",
}

CATEGORY_CONFIG = {
    "laptop": {
        "projection_fields": [
            "name",
            "price",
            "original_price",
            "discount_amount",
            "discount_percent",
            "rating",
            "review_count",
            "link",
            "image",
            "website",
            "category",
            "currency",
            "brand",
            "ram",
            "storage",
            "processor",
            "screen_size",
            "gpu",
            "model_code",
            "last_seen_at",
        ],
        "difference_fields": [
            "model_code",
            "screen_size",
            "gpu",
            "price",
            "original_price",
            "discount_percent",
            "rating",
            "review_count",
            "processor",
            "ram",
            "storage",
        ],
        "choose_match_threshold": 55,
        "high_confidence_threshold": 85,
        "variant_threshold": 68,
        "spec_threshold": 50,
    },
    "mobile": {
        "projection_fields": [
            "name",
            "price",
            "original_price",
            "discount_amount",
            "discount_percent",
            "rating",
            "review_count",
            "link",
            "image",
            "website",
            "category",
            "currency",
            "brand",
            "ram",
            "storage",
            "processor",
            "display_size",
            "camera",
            "battery",
            "network",
            "last_seen_at",
        ],
        "difference_fields": [
            "display_size",
            "camera",
            "battery",
            "network",
            "price",
            "original_price",
            "discount_percent",
            "rating",
            "review_count",
            "processor",
            "ram",
            "storage",
        ],
        "choose_match_threshold": 46,
        "high_confidence_threshold": 74,
        "variant_threshold": 48,
        "spec_threshold": 42,
    },
}


def normalized_category(category):
    text = normalize_value(category)
    if text.startswith("mobile"):
        return "mobile"
    if text.startswith("laptop"):
        return "laptop"
    return "laptop"


def category_config(category):
    return CATEGORY_CONFIG[normalized_category(category)]


def is_known(value):
    return value not in UNKNOWN_VALUES


def normalize_value(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return normalize_text(value).lower()
    return str(value).strip().lower()


def comparable_name(name):
    cleaned = normalize_value(name)
    cleaned = re.sub(r"[^a-z0-9\s]", " ", cleaned)
    return " ".join(token for token in cleaned.split() if token not in NOISE_TOKENS)


def normalized_model_code(value):
    code = normalize_value(value).replace(" ", "")
    return code


def model_code_prefix(value):
    code = normalized_model_code(value)
    if not code:
        return ""
    return code.split("-")[0]


def tokenize_name(name):
    cleaned = comparable_name(name)
    tokens = []
    for token in cleaned.split():
        if len(token) <= 1 or token in NOISE_TOKENS:
            continue
        tokens.append(token)
    return set(tokens)


def search_terms(query):
    cleaned = normalize_value(query)
    cleaned = re.sub(r"[^a-z0-9\s]", " ", cleaned)
    tokens = []
    for token in cleaned.split():
        if token in SEARCH_NOISE_TOKENS:
            continue
        if len(token) <= 1 and not token.isdigit():
            continue
        tokens.append(token)
    return tokens


def matches_search_query(product, query):
    if not query:
        return True

    haystack = normalize_value(
        " ".join(
            str(part)
            for part in [
                product.get("name", ""),
                product.get("source_text", ""),
                product.get("link", ""),
                product.get("brand", ""),
                product.get("model_code", ""),
            ]
            if part
        )
    )
    normalized_query = normalize_value(query)

    if normalized_query and normalized_query in haystack:
        return True

    tokens = search_terms(query)
    if not tokens:
        return False

    matched = sum(1 for token in tokens if token in haystack)
    if len(tokens) <= 2:
        return matched == len(tokens)
    if len(tokens) <= 4:
        return matched >= len(tokens) - 1
    return matched >= max(3, len(tokens) // 2)


def processor_family(processor):
    text = normalize_value(processor)
    families = [
        "core ultra",
        "core i9",
        "core i7",
        "core i5",
        "core i3",
        "core 9",
        "core 7",
        "core 5",
        "core 3",
        "ryzen ai 9",
        "ryzen ai 7",
        "ryzen ai 5",
        "ryzen 9",
        "ryzen 7",
        "ryzen 5",
        "ryzen 3",
        "celeron",
        "pentium",
        "athlon",
        "snapdragon",
        "dimensity",
        "exynos",
        "tensor",
        "bionic",
        "a18",
        "a17",
        "a16",
        "a15",
        "a14",
        "kompanio",
        "helio",
        "unisoc",
        "xeon",
        "m4",
        "m3",
        "m2",
        "m1",
    ]

    for family in families:
        if family in text:
            return family

    return text


def normalized_processor(processor):
    text = normalize_value(processor)
    if not text:
        return ""

    replacements = {
        "intel core": "core",
        "amd ryzen": "ryzen",
        "13th gen": "",
        "14th gen": "",
        "12th gen": "",
        "11th gen": "",
        "10th gen": "",
        "gen 1": "",
        "gen 2": "",
        "gen 3": "",
        "gen 4": "",
    }

    for source, target in replacements.items():
        text = text.replace(source, target)

    text = re.sub(r"\bprocessor\b", "", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    tokens = text.split()

    compact_tokens = []
    for token in tokens:
        if token in {"intel", "amd", "qualcomm", "mediatek"}:
            continue
        compact_tokens.append(token)

    return " ".join(compact_tokens)


def normalized_gpu(gpu):
    text = normalize_value(gpu)
    if not text:
        return ""

    replacements = {
        "nvidia geforce": "",
        "amd radeon": "",
        "intel iris xe": "iris xe",
        "intel uhd graphics": "uhd",
        "intel uhd": "uhd",
        "graphics": "",
        "graphic": "",
        "gpu": "",
        "igpu": "",
        "gddr6": "",
        "gb": "",
    }

    for source, target in replacements.items():
        text = text.replace(source, target)

    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def jaccard_similarity(left, right):
    if not left or not right:
        return 0.0
    intersection = len(left & right)
    union = len(left | right)
    return intersection / union if union else 0.0


def build_candidate_groups(products):
    groups = defaultdict(list)
    for product in products:
        groups[normalize_value(product.get("brand"))].append(product)
    return groups


def variant_family(name, category="laptop"):
    cleaned = comparable_name(name)
    category = normalized_category(category)

    if category == "mobile":
        patterns = [
            r'\biphone\s+\d+(?:\s+(?:pro|max|plus|mini))?\b',
            r'\bgalaxy\s+[amsf]\d+\b',
            r'\bgalaxy\s+s\d+\s+(?:ultra|plus|fe)\b',
            r'\bredmi\s+note\s+\d+\b',
            r'\bnote\s+\d+\b',
            r'\bnord\s+\w+\b',
            r'\breno\s+\d+\b',
            r'\bvivo\s+[vty]\d+\w*\b',
            r'\boppo\s+[afkr]\w+\b',
            r'\brealme\s+\w+\b',
            r'\bpoco\s+\w+\b',
            r'\bmoto\s+g\w+\b',
            r'\bedge\s+\d+\b',
        ]
    else:
        patterns = [
            r'\bvivobook(?:\s+go)?\s+\d+\b',
            r'\baspire\s+\w+\b',
            r'\bzenbook\s+\w+\b',
            r'\bchromebook\s+\w+\b',
            r'\bomnibook\s+\d+\b',
            r'\bpavilion\s+\w+\b',
            r'\binspiron\s+\d+\b',
            r'\bideapad\s+\w+\b',
            r'\bv\d{2}\s+g\d\b',
            r'\bprobook\s+\w+\b',
            r'\belitebook\s+\w+\b',
        ]

    for pattern in patterns:
        match = re.search(pattern, cleaned, re.IGNORECASE)
        if match:
            return match.group()

    tokens = cleaned.split()
    return " ".join(tokens[:3])


def score_products(left, right, category="laptop"):
    category = normalized_category(category)
    score = 0
    reasons = []

    left_brand = normalize_value(left.get("brand"))
    right_brand = normalize_value(right.get("brand"))
    if left_brand and right_brand and left_brand == right_brand:
        score += 20
        reasons.append("brand")
    else:
        return 0, []

    left_model = left.get("model_code")
    right_model = right.get("model_code")
    if category == "laptop" and is_known(left_model) and is_known(right_model):
        left_code = normalized_model_code(left_model)
        right_code = normalized_model_code(right_model)
        if left_code == right_code:
            score += 45
            reasons.append("model_code_exact")
        elif model_code_prefix(left_model) == model_code_prefix(right_model):
            score += 30
            reasons.append("model_code_family")
        else:
            return 0, []

    left_variant = variant_family(left.get("name", ""), category)
    right_variant = variant_family(right.get("name", ""), category)
    if left_variant and right_variant:
        if left_variant == right_variant:
            score += 24 if category == "mobile" else 18
            reasons.append("variant_family")
        elif category == "laptop":
            return 0, []

    left_tokens = tokenize_name(left.get("name", ""))
    right_tokens = tokenize_name(right.get("name", ""))
    title_similarity = jaccard_similarity(left_tokens, right_tokens)
    minimum_title_similarity = 0.28 if category == "mobile" else 0.4
    if title_similarity >= minimum_title_similarity:
        title_points = min(30, round(title_similarity * (42 if category == "mobile" else 35)))
        score += title_points
        reasons.append(f"title:{title_points}")
    elif category == "laptop" and not (is_known(left_model) and is_known(right_model)):
        return 0, []
    elif category == "mobile":
        return 0, []

    left_processor = left.get("processor")
    right_processor = right.get("processor")
    if is_known(left_processor) and is_known(right_processor):
        if normalize_value(left_processor) == normalize_value(right_processor):
            score += 30
            reasons.append("processor_exact")
        elif processor_family(left_processor) == processor_family(right_processor):
            score += 18
            reasons.append("processor_family")
        elif category == "laptop":
            return 0, []

    field_points = (
        [("ram", 12), ("storage", 12), ("screen_size", 10), ("gpu", 10)]
        if category == "laptop"
        else [("ram", 12), ("storage", 12), ("display_size", 10), ("camera", 8), ("battery", 8), ("network", 8)]
    )
    strict_fields = {"screen_size", "gpu"} if category == "laptop" else set()
    for field, points in field_points:
        left_value = left.get(field)
        right_value = right.get(field)
        if is_known(left_value) and is_known(right_value) and normalize_value(left_value) == normalize_value(right_value):
            score += points
            reasons.append(field)
        elif field in strict_fields and is_known(left_value) and is_known(right_value):
            return 0, []

    return score, reasons


def compare_field(left, right, field):
    left_value = left.get(field)
    right_value = right.get(field)
    if not is_known(left_value) or not is_known(right_value):
        return {"status": "unknown", "amazon": left_value, "flipkart": right_value}

    if field == "price":
        same = left_value == right_value
    elif field == "processor":
        same = (
            normalized_processor(left_value) == normalized_processor(right_value)
            or processor_family(left_value) == processor_family(right_value)
        )
    elif field == "gpu":
        same = normalized_gpu(left_value) == normalized_gpu(right_value)
    else:
        same = normalize_value(left_value) == normalize_value(right_value)
    return {
        "status": "same" if same else "different",
        "amazon": left_value,
        "flipkart": right_value,
    }


def core_hardware_fields(category):
    category = normalized_category(category)
    if category == "mobile":
        return ["processor", "ram", "storage", "display_size", "camera", "battery", "network"]
    return ["processor", "ram", "storage", "screen_size", "gpu"]


def differences_for_exact_evaluation(left, right, category):
    significant = []
    for field in core_hardware_fields(category):
        result = compare_field(left, right, field)
        if result["status"] == "different":
            significant.append(field)
    return significant


def is_exact_candidate(left, right, category):
    category = normalized_category(category)
    significant_differences = differences_for_exact_evaluation(left, right, category)
    if significant_differences:
        return False

    left_variant = variant_family(left.get("name", ""), category)
    right_variant = variant_family(right.get("name", ""), category)
    title_similarity = jaccard_similarity(
        tokenize_name(left.get("name", "")),
        tokenize_name(right.get("name", "")),
    )

    if category == "mobile":
        return (
            (left_variant and right_variant and left_variant == right_variant)
            or title_similarity >= 0.42
        )

    left_model = left.get("model_code")
    right_model = right.get("model_code")
    if is_known(left_model) and is_known(right_model):
        if normalized_model_code(left_model) == normalized_model_code(right_model):
            return True
        if model_code_prefix(left_model) == model_code_prefix(right_model) and title_similarity >= 0.3:
            return True

    return (
        (left_variant and right_variant and left_variant == right_variant and title_similarity >= 0.3)
        or title_similarity >= 0.28
        or (
            title_similarity >= 0.2
            and is_known(left.get("ram"))
            and is_known(right.get("ram"))
            and is_known(left.get("storage"))
            and is_known(right.get("storage"))
            and normalize_value(left.get("ram")) == normalize_value(right.get("ram"))
            and normalize_value(left.get("storage")) == normalize_value(right.get("storage"))
        )
        or title_similarity >= 0.5
    )


def build_differences(left, right, category="laptop"):
    fields = category_config(category)["difference_fields"]
    differences = {}
    for field in fields:
        result = compare_field(left, right, field)
        if result["status"] != "same":
            differences[field] = result
    return differences


def score_spec_match(left, right, category="laptop"):
    category = normalized_category(category)
    left_brand = normalize_value(left.get("brand"))
    right_brand = normalize_value(right.get("brand"))
    if not left_brand or left_brand != right_brand:
        return 0, []

    left_ram = left.get("ram")
    right_ram = right.get("ram")
    left_storage = left.get("storage")
    right_storage = right.get("storage")
    if not (
        is_known(left_ram) and is_known(right_ram) and normalize_value(left_ram) == normalize_value(right_ram)
        and is_known(left_storage) and is_known(right_storage) and normalize_value(left_storage) == normalize_value(right_storage)
    ):
        return 0, []

    left_processor = left.get("processor")
    right_processor = right.get("processor")
    if category == "laptop" and not (is_known(left_processor) and is_known(right_processor)):
        return 0, []
    if category == "mobile" and not (is_known(left_processor) or is_known(right_processor)):
        return 0, []

    left_proc_family = processor_family(left_processor)
    right_proc_family = processor_family(right_processor)
    if is_known(left_processor) and is_known(right_processor) and left_proc_family != right_proc_family:
        return 0, []

    left_tokens = tokenize_name(left.get("name", ""))
    right_tokens = tokenize_name(right.get("name", ""))
    title_similarity = jaccard_similarity(left_tokens, right_tokens)

    score = 0
    reasons = ["brand", "ram", "storage"]
    score += 20 + 15 + 15
    if is_known(left_processor) and is_known(right_processor):
        reasons.append("processor_family")
        score += 20

    left_variant = variant_family(left.get("name", ""), category)
    right_variant = variant_family(right.get("name", ""), category)
    if left_variant and right_variant and left_variant == right_variant:
        score += 12
        reasons.append("variant_family")

    if title_similarity >= (0.15 if category == "mobile" else 0.12):
        title_points = min(14 if category == "mobile" else 12, round(title_similarity * 18))
        score += title_points
        reasons.append(f"title:{title_points}")

    fields = (
        [("screen_size", 8), ("gpu", 8), ("model_code", 12)]
        if category == "laptop"
        else [("display_size", 8), ("network", 8), ("camera", 6), ("battery", 6)]
    )
    for field, points in fields:
        left_value = left.get(field)
        right_value = right.get(field)
        if is_known(left_value) and is_known(right_value):
            if field == "model_code":
                if normalized_model_code(left_value) == normalized_model_code(right_value):
                    score += points
                    reasons.append("model_code_exact")
                elif model_code_prefix(left_value) == model_code_prefix(right_value):
                    score += points - 4
                    reasons.append("model_code_family")
            elif normalize_value(left_value) == normalize_value(right_value):
                score += points
                reasons.append(field)

    return score, reasons


def score_variant_match(left, right, category="laptop"):
    category = normalized_category(category)
    left_brand = normalize_value(left.get("brand"))
    right_brand = normalize_value(right.get("brand"))
    if not left_brand or left_brand != right_brand:
        return 0, []

    left_ram = left.get("ram")
    right_ram = right.get("ram")
    left_storage = left.get("storage")
    right_storage = right.get("storage")
    if not (
        is_known(left_ram) and is_known(right_ram) and normalize_value(left_ram) == normalize_value(right_ram)
        and is_known(left_storage) and is_known(right_storage) and normalize_value(left_storage) == normalize_value(right_storage)
    ):
        return 0, []

    left_processor = left.get("processor")
    right_processor = right.get("processor")
    if category == "laptop" and not (is_known(left_processor) and is_known(right_processor)):
        return 0, []
    if category == "mobile" and not (is_known(left_processor) or is_known(right_processor)):
        return 0, []

    left_proc_family = processor_family(left_processor)
    right_proc_family = processor_family(right_processor)
    if is_known(left_processor) and is_known(right_processor) and left_proc_family != right_proc_family:
        return 0, []

    score = 0
    reasons = ["brand", "ram", "storage"]
    score += 20 + 15 + 15
    if is_known(left_processor) and is_known(right_processor):
        reasons.append("processor_family")
        score += 18

    left_variant = variant_family(left.get("name", ""), category)
    right_variant = variant_family(right.get("name", ""), category)
    if left_variant and right_variant and left_variant == right_variant:
        score += 14
        reasons.append("variant_family")

    left_tokens = tokenize_name(left.get("name", ""))
    right_tokens = tokenize_name(right.get("name", ""))
    title_similarity = jaccard_similarity(left_tokens, right_tokens)
    if title_similarity >= (0.2 if category == "mobile" else 0.18):
        title_points = min(18 if category == "mobile" else 16, round(title_similarity * 22))
        score += title_points
        reasons.append(f"title:{title_points}")

    left_model = left.get("model_code")
    right_model = right.get("model_code")
    model_signal = False
    if category == "laptop" and is_known(left_model) and is_known(right_model):
        if normalized_model_code(left_model) == normalized_model_code(right_model):
            score += 20
            reasons.append("model_code_exact")
            model_signal = True
        elif model_code_prefix(left_model) == model_code_prefix(right_model):
            score += 14
            reasons.append("model_code_family")
            model_signal = True

    fields = [("screen_size", 8), ("gpu", 6)] if category == "laptop" else [("display_size", 8), ("network", 6)]
    for field, points in fields:
        left_value = left.get(field)
        right_value = right.get(field)
        if is_known(left_value) and is_known(right_value) and normalize_value(left_value) == normalize_value(right_value):
            score += points
            reasons.append(field)

    has_name_signal = (
        (left_variant and right_variant and left_variant == right_variant)
        or title_similarity >= 0.18
        or model_signal
    )
    if not has_name_signal:
        return 0, []

    return score, reasons


def choose_variant_match(left, candidates, category="laptop"):
    best_match = None
    best_score = 0
    best_reasons = []

    for candidate in candidates:
        score, reasons = score_variant_match(left, candidate, category)
        if score > best_score:
            best_match = candidate
            best_score = score
            best_reasons = reasons

    if best_score < category_config(category)["variant_threshold"]:
        return None

    return {
        "match": best_match,
        "score": best_score,
        "reasons": best_reasons,
    }


def choose_spec_match(left, candidates, category="laptop"):
    best_match = None
    best_score = 0
    best_reasons = []

    for candidate in candidates:
        score, reasons = score_spec_match(left, candidate, category)
        if score > best_score:
            best_match = candidate
            best_score = score
            best_reasons = reasons

    if best_score < category_config(category)["spec_threshold"]:
        return None

    return {
        "match": best_match,
        "score": best_score,
        "reasons": best_reasons,
    }


def choose_match(left, candidates, category="laptop"):
    best_match = None
    best_score = 0
    best_reasons = []

    for candidate in candidates:
        score, reasons = score_products(left, candidate, category)
        if score > best_score:
            best_match = candidate
            best_score = score
            best_reasons = reasons

    config = category_config(category)
    if best_score < config["choose_match_threshold"]:
        return None

    category = "possible"
    if best_score >= config["high_confidence_threshold"]:
        category = "high_confidence"

    return {
        "match": best_match,
        "score": best_score,
        "reasons": best_reasons,
        "category": category,
    }


def comparison_payload(query=None, limit=20, category="laptop"):
    category = normalized_category(category)
    collection = get_collection(category)
    projection = {field: 1 for field in category_config(category)["projection_fields"]}
    projection["_id"] = 0
    projection["source_text"] = 1
    products = list(
        collection.find(
            {},
            projection,
        )
    )

    source_products = [product for product in products if matches_search_query(product, query)]
    amazon_products = [product for product in source_products if product.get("website") == "amazon"]
    flipkart_products = [product for product in source_products if product.get("website") == "flipkart"]
    all_amazon_products = [product for product in products if product.get("website") == "amazon"]
    all_flipkart_products = [product for product in products if product.get("website") == "flipkart"]
    flipkart_by_brand = build_candidate_groups(all_flipkart_products)
    amazon_by_brand = build_candidate_groups(all_amazon_products)

    exact_matches = []
    variant_matches = []
    possible_matches = []
    spec_comparable_matches = []
    seen_pairs = set()

    def pair_key(left, right):
        return tuple(sorted([left.get("link", ""), right.get("link", "")]))

    def evaluate_products(left_products, right_by_brand):
        nonlocal exact_matches, variant_matches, possible_matches, spec_comparable_matches

        for left_product in left_products:
            brand_key = normalize_value(left_product.get("brand"))
            if not brand_key:
                continue

            candidate_group = right_by_brand.get(brand_key, [])
            if not candidate_group:
                continue

            variant_result = choose_variant_match(left_product, candidate_group, category)
            spec_result = choose_spec_match(left_product, candidate_group, category)
            result = choose_match(left_product, candidate_group, category)

            if result:
                right_product = result["match"]
                key = pair_key(left_product, right_product)
                if key in seen_pairs:
                    continue
                seen_pairs.add(key)
                left_price = left_product.get("price") or 0
                right_price = right_product.get("price") or 0

                match_payload = {
                    "score": result["score"],
                    "match_reasons": result["reasons"],
                    "amazon": left_product if left_product.get("website") == "amazon" else right_product,
                    "flipkart": right_product if right_product.get("website") == "flipkart" else left_product,
                    "differences": build_differences(
                        left_product if left_product.get("website") == "amazon" else right_product,
                        right_product if right_product.get("website") == "flipkart" else left_product,
                        category,
                    ),
                    "price_difference": abs(left_price - right_price),
                    "cheaper_site": (
                        "same"
                        if left_price == right_price
                        else left_product.get("website")
                        if left_price < right_price
                        else right_product.get("website")
                    ),
                }

                if result["category"] == "high_confidence" or is_exact_candidate(
                    match_payload["amazon"],
                    match_payload["flipkart"],
                    category,
                ):
                    exact_matches.append({
                        **match_payload,
                        "match_type": "exact",
                        "confidence_label": "High Confidence",
                    })
                    continue

                possible_matches.append({
                    **match_payload,
                    "match_type": "possible",
                    "confidence_label": "Close Match",
                })
                continue

            if variant_result:
                matched = variant_result["match"]
                key = pair_key(left_product, matched)
                if key in seen_pairs:
                    continue
                seen_pairs.add(key)
                left_price = left_product.get("price") or 0
                right_price = matched.get("price") or 0
                variant_payload = {
                    "score": variant_result["score"],
                    "match_reasons": variant_result["reasons"],
                    "amazon": left_product if left_product.get("website") == "amazon" else matched,
                    "flipkart": matched if matched.get("website") == "flipkart" else left_product,
                    "differences": build_differences(
                        left_product if left_product.get("website") == "amazon" else matched,
                        matched if matched.get("website") == "flipkart" else left_product,
                        category,
                    ),
                    "price_difference": abs(left_price - right_price),
                    "cheaper_site": (
                        "same"
                        if left_price == right_price
                        else left_product.get("website")
                        if left_price < right_price
                        else matched.get("website")
                    ),
                    "match_type": "variant",
                    "confidence_label": "Variant Match",
                }
                if is_exact_candidate(variant_payload["amazon"], variant_payload["flipkart"], category):
                    exact_matches.append({
                        **variant_payload,
                        "match_type": "exact",
                        "confidence_label": "High Confidence",
                    })
                else:
                    variant_matches.append(variant_payload)
                continue

            if spec_result:
                matched = spec_result["match"]
                key = pair_key(left_product, matched)
                if key in seen_pairs:
                    continue
                seen_pairs.add(key)
                left_price = left_product.get("price") or 0
                right_price = matched.get("price") or 0
                spec_payload = {
                    "score": spec_result["score"],
                    "match_reasons": spec_result["reasons"],
                    "amazon": left_product if left_product.get("website") == "amazon" else matched,
                    "flipkart": matched if matched.get("website") == "flipkart" else left_product,
                    "differences": build_differences(
                        left_product if left_product.get("website") == "amazon" else matched,
                        matched if matched.get("website") == "flipkart" else left_product,
                        category,
                    ),
                    "price_difference": abs(left_price - right_price),
                    "cheaper_site": (
                        "same"
                        if left_price == right_price
                        else left_product.get("website")
                        if left_price < right_price
                        else matched.get("website")
                    ),
                    "match_type": "similar_specs",
                    "confidence_label": "Similar Specs",
                }
                if is_exact_candidate(spec_payload["amazon"], spec_payload["flipkart"], category):
                    exact_matches.append({
                        **spec_payload,
                        "match_type": "exact",
                        "confidence_label": "High Confidence",
                    })
                else:
                    spec_comparable_matches.append(spec_payload)

    evaluate_products(amazon_products, flipkart_by_brand)
    evaluate_products(flipkart_products, amazon_by_brand)

    exact_matches.sort(key=lambda item: (-item["score"], item["price_difference"]))
    variant_matches.sort(key=lambda item: (-item["score"], item["price_difference"]))
    possible_matches.sort(key=lambda item: (-item["score"], item["price_difference"]))
    spec_comparable_matches.sort(key=lambda item: (-item["score"], item["price_difference"]))
    all_comparable_matches = [*exact_matches, *variant_matches, *spec_comparable_matches]
    all_comparable_matches.sort(key=lambda item: (-item["score"], item["price_difference"]))
    best_value_matches = sorted(
        [
            item
            for item in all_comparable_matches
            if item["cheaper_site"] != "same"
        ],
        key=lambda item: (
            -round(item["price_difference"] / max(item["amazon"].get("price") or 1, item["flipkart"].get("price") or 1), 4),
            -item["score"],
        ),
    )
    return {
        "category": category,
        "query": query or "",
        "amazon_source_total": len(amazon_products),
        "flipkart_source_total": len(flipkart_products),
        "high_confidence_total": len(exact_matches),
        "exact_total": len(exact_matches),
        "variant_total": len(variant_matches),
        "possible_total": len(possible_matches),
        "spec_comparable_total": len(spec_comparable_matches),
        "all_comparable_total": len(all_comparable_matches),
        "best_value_total": len(best_value_matches),
        "high_confidence_matches": exact_matches[:limit],
        "exact_matches": exact_matches[:limit],
        "variant_matches": variant_matches[:limit],
        "possible_matches": possible_matches[:limit],
        "spec_comparable_matches": spec_comparable_matches[:limit],
        "all_comparable_matches": all_comparable_matches[:limit],
        "best_value_matches": best_value_matches[:limit],
    }
