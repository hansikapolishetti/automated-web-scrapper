import re
from collections import defaultdict

from database.db import collection
from utils.feature_extractor import normalize_text


UNKNOWN_VALUES = {"", None, "Unknown", "Unavailable"}
NOISE_TOKENS = {
    "laptop",
    "laptops",
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


def is_known(value):
    return value not in UNKNOWN_VALUES


def normalize_value(value):
    return normalize_text(value).lower() if value else ""


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
        "kompanio",
        "helio",
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


def variant_family(name):
    cleaned = comparable_name(name)
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


def score_products(left, right):
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
    if is_known(left_model) and is_known(right_model):
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

    left_variant = variant_family(left.get("name", ""))
    right_variant = variant_family(right.get("name", ""))
    if left_variant and right_variant:
        if left_variant == right_variant:
            score += 18
            reasons.append("variant_family")
        else:
            return 0, []

    left_tokens = tokenize_name(left.get("name", ""))
    right_tokens = tokenize_name(right.get("name", ""))
    title_similarity = jaccard_similarity(left_tokens, right_tokens)
    if title_similarity >= 0.4:
        title_points = min(30, round(title_similarity * 35))
        score += title_points
        reasons.append(f"title:{title_points}")
    elif not (is_known(left_model) and is_known(right_model)):
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
        else:
            return 0, []

    for field, points in (("ram", 12), ("storage", 12), ("screen_size", 10), ("gpu", 10)):
        left_value = left.get(field)
        right_value = right.get(field)
        if is_known(left_value) and is_known(right_value) and normalize_value(left_value) == normalize_value(right_value):
            score += points
            reasons.append(field)
        elif field in {"screen_size", "gpu"} and is_known(left_value) and is_known(right_value):
            return 0, []

    return score, reasons


def compare_field(left, right, field):
    left_value = left.get(field)
    right_value = right.get(field)
    if not is_known(left_value) or not is_known(right_value):
        return {"status": "unknown", "amazon": left_value, "flipkart": right_value}

    if field == "price":
        same = left_value == right_value
    else:
        same = normalize_value(left_value) == normalize_value(right_value)
    return {
        "status": "same" if same else "different",
        "amazon": left_value,
        "flipkart": right_value,
    }


def build_differences(left, right):
    fields = ["model_code", "screen_size", "gpu", "price", "processor", "ram", "storage"]
    differences = {}
    for field in fields:
        result = compare_field(left, right, field)
        if result["status"] != "same":
            differences[field] = result
    return differences


def score_spec_match(left, right):
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
    if not (is_known(left_processor) and is_known(right_processor)):
        return 0, []

    left_proc_family = processor_family(left_processor)
    right_proc_family = processor_family(right_processor)
    if left_proc_family != right_proc_family:
        return 0, []

    left_tokens = tokenize_name(left.get("name", ""))
    right_tokens = tokenize_name(right.get("name", ""))
    title_similarity = jaccard_similarity(left_tokens, right_tokens)

    score = 0
    reasons = ["brand", "ram", "storage", "processor_family"]
    score += 20 + 15 + 15 + 20

    left_variant = variant_family(left.get("name", ""))
    right_variant = variant_family(right.get("name", ""))
    if left_variant and right_variant and left_variant == right_variant:
        score += 12
        reasons.append("variant_family")

    if title_similarity >= 0.12:
        title_points = min(12, round(title_similarity * 18))
        score += title_points
        reasons.append(f"title:{title_points}")

    for field, points in (("screen_size", 8), ("gpu", 8), ("model_code", 12)):
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


def score_variant_match(left, right):
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
    if not (is_known(left_processor) and is_known(right_processor)):
        return 0, []

    left_proc_family = processor_family(left_processor)
    right_proc_family = processor_family(right_processor)
    if left_proc_family != right_proc_family:
        return 0, []

    score = 0
    reasons = ["brand", "ram", "storage", "processor_family"]
    score += 20 + 15 + 15 + 18

    left_variant = variant_family(left.get("name", ""))
    right_variant = variant_family(right.get("name", ""))
    if left_variant and right_variant and left_variant == right_variant:
        score += 14
        reasons.append("variant_family")

    left_tokens = tokenize_name(left.get("name", ""))
    right_tokens = tokenize_name(right.get("name", ""))
    title_similarity = jaccard_similarity(left_tokens, right_tokens)
    if title_similarity >= 0.18:
        title_points = min(16, round(title_similarity * 22))
        score += title_points
        reasons.append(f"title:{title_points}")

    left_model = left.get("model_code")
    right_model = right.get("model_code")
    model_signal = False
    if is_known(left_model) and is_known(right_model):
        if normalized_model_code(left_model) == normalized_model_code(right_model):
            score += 20
            reasons.append("model_code_exact")
            model_signal = True
        elif model_code_prefix(left_model) == model_code_prefix(right_model):
            score += 14
            reasons.append("model_code_family")
            model_signal = True

    for field, points in (("screen_size", 8), ("gpu", 6)):
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


def choose_variant_match(left, candidates):
    best_match = None
    best_score = 0
    best_reasons = []

    for candidate in candidates:
        score, reasons = score_variant_match(left, candidate)
        if score > best_score:
            best_match = candidate
            best_score = score
            best_reasons = reasons

    if best_score < 68:
        return None

    return {
        "match": best_match,
        "score": best_score,
        "reasons": best_reasons,
    }


def choose_spec_match(left, candidates):
    best_match = None
    best_score = 0
    best_reasons = []

    for candidate in candidates:
        score, reasons = score_spec_match(left, candidate)
        if score > best_score:
            best_match = candidate
            best_score = score
            best_reasons = reasons

    if best_score < 50:
        return None

    return {
        "match": best_match,
        "score": best_score,
        "reasons": best_reasons,
    }


def choose_match(left, candidates):
    best_match = None
    best_score = 0
    best_reasons = []

    for candidate in candidates:
        score, reasons = score_products(left, candidate)
        if score > best_score:
            best_match = candidate
            best_score = score
            best_reasons = reasons

    if best_score < 55:
        return None

    category = "possible"
    if best_score >= 85:
        category = "high_confidence"

    return {
        "match": best_match,
        "score": best_score,
        "reasons": best_reasons,
        "category": category,
    }


def comparison_payload(query=None, limit=20):
    mongo_query = {}
    if query:
        mongo_query["name"] = {"$regex": re.escape(query), "$options": "i"}

    products = list(
        collection.find(
            mongo_query,
            {
                "_id": 0,
                "name": 1,
                "price": 1,
                "link": 1,
                "image": 1,
                "website": 1,
                "brand": 1,
                "ram": 1,
                "storage": 1,
                "processor": 1,
                "screen_size": 1,
                "gpu": 1,
                "model_code": 1,
            },
        )
    )

    amazon_products = [product for product in products if product.get("website") == "amazon"]
    flipkart_products = [product for product in products if product.get("website") == "flipkart"]
    flipkart_by_brand = build_candidate_groups(flipkart_products)

    exact_matches = []
    variant_matches = []
    possible_matches = []
    spec_comparable_matches = []
    for amazon_product in amazon_products:
        brand_key = normalize_value(amazon_product.get("brand"))
        if not brand_key:
            continue

        candidate_group = flipkart_by_brand.get(brand_key, [])
        if not candidate_group:
            continue

        variant_result = choose_variant_match(amazon_product, candidate_group)
        spec_result = choose_spec_match(amazon_product, candidate_group)
        result = choose_match(amazon_product, candidate_group)

        if result:
            flipkart_product = result["match"]
            amazon_price = amazon_product.get("price") or 0
            flipkart_price = flipkart_product.get("price") or 0

            match_payload = {
                "score": result["score"],
                "match_reasons": result["reasons"],
                "amazon": amazon_product,
                "flipkart": flipkart_product,
                "differences": build_differences(amazon_product, flipkart_product),
                "price_difference": abs(amazon_price - flipkart_price),
                "cheaper_site": (
                    "same"
                    if amazon_price == flipkart_price
                    else "amazon"
                    if amazon_price < flipkart_price
                    else "flipkart"
                ),
            }

            if result["category"] == "high_confidence":
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
            amazon_price = amazon_product.get("price") or 0
            flipkart_price = matched.get("price") or 0
            variant_matches.append({
                "score": variant_result["score"],
                "match_reasons": variant_result["reasons"],
                "amazon": amazon_product,
                "flipkart": matched,
                "differences": build_differences(amazon_product, matched),
                "price_difference": abs(amazon_price - flipkart_price),
                "cheaper_site": (
                    "same"
                    if amazon_price == flipkart_price
                    else "amazon"
                    if amazon_price < flipkart_price
                    else "flipkart"
                ),
                "match_type": "variant",
                "confidence_label": "Variant Match",
            })
            continue

        if spec_result:
            matched = spec_result["match"]
            amazon_price = amazon_product.get("price") or 0
            flipkart_price = matched.get("price") or 0
            spec_comparable_matches.append({
                "score": spec_result["score"],
                "match_reasons": spec_result["reasons"],
                "amazon": amazon_product,
                "flipkart": matched,
                "differences": build_differences(amazon_product, matched),
                "price_difference": abs(amazon_price - flipkart_price),
                "cheaper_site": (
                    "same"
                    if amazon_price == flipkart_price
                    else "amazon"
                    if amazon_price < flipkart_price
                    else "flipkart"
                ),
                "match_type": "similar_specs",
                "confidence_label": "Similar Specs",
            })

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
        "query": query or "",
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
