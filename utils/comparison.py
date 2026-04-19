import re
from collections import defaultdict

from database.db import get_collection
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
MOBILE_NOISE_TOKENS = {
    "mobile",
    "mobiles",
    "phone",
    "phones",
    "smartphone",
    "smartphones",
    "android",
    "camera",
    "battery",
    "display",
    "storage",
    "ram",
    "inch",
    "inches",
    "with",
    "for",
    "and",
    "plus",
    "dual",
    "sim",
    "bluetooth",
}
TV_NOISE_TOKENS = {
    "tv",
    "tvs",
    "television",
    "smart",
    "smarttv",
    "smart-tv",
    "led",
    "qled",
    "oled",
    "google",
    "android",
    "ultra",
    "uhd",
    "hd",
    "full",
    "inch",
    "inches",
    "with",
    "for",
    "and",
}


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


def comparable_mobile_name(name):
    cleaned = normalize_value(name)
    cleaned = re.sub(r"[^a-z0-9\s]", " ", cleaned)
    return " ".join(token for token in cleaned.split() if token not in MOBILE_NOISE_TOKENS)


def tokenize_mobile_name(name):
    cleaned = comparable_mobile_name(name)
    return {
        token
        for token in cleaned.split()
        if len(token) > 1 and token not in MOBILE_NOISE_TOKENS
    }


def comparable_tv_name(name):
    cleaned = normalize_value(name)
    cleaned = re.sub(r"[^a-z0-9\s]", " ", cleaned)
    return " ".join(token for token in cleaned.split() if token not in TV_NOISE_TOKENS)


def tokenize_tv_name(name):
    cleaned = comparable_tv_name(name)
    return {
        token
        for token in cleaned.split()
        if len(token) > 1 and token not in TV_NOISE_TOKENS
    }


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


def mobile_variant_family(name):
    cleaned = comparable_mobile_name(name)
    patterns = [
        r"\biphone\s+\d+\b",
        r"\bgalaxy\s+[a-z]\d+\b",
        r"\bgalaxy\s+s\d+\b",
        r"\bnord\s+\w+\b",
        r"\bnote\s+\d+\b",
        r"\bredmi\s+\w+\b",
        r"\bpoco\s+\w+\b",
        r"\bmoto\s+\w+\b",
        r"\bv\d+\b",
        r"\by\d+\b",
        r"\breno\s+\w+\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, cleaned, re.IGNORECASE)
        if match:
            return match.group()

    tokens = cleaned.split()
    return " ".join(tokens[:3])


def tv_variant_family(name):
    cleaned = comparable_tv_name(name)
    patterns = [
        r"\bbravia\s+\w+\b",
        r"\bcrystal\s+\w+\b",
        r"\bqned\s+\w+\b",
        r"\bmi\s+tv\s+\w+\b",
        r"\bvu\s+\w+\b",
        r"\ba\d+\b",
        r"\bc\d+\b",
        r"\bd\d+\b",
        r"\bp\d+\b",
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

    return score, reasons


def score_mobile_products(left, right):
    left_brand = normalize_value(left.get("brand"))
    right_brand = normalize_value(right.get("brand"))
    if not left_brand or left_brand != right_brand:
        return 0, []

    score = 20
    reasons = ["brand"]

    left_ram = left.get("ram")
    right_ram = right.get("ram")
    if is_known(left_ram) and is_known(right_ram):
        if normalize_value(left_ram) != normalize_value(right_ram):
            return 0, []
        score += 14
        reasons.append("ram")
    elif is_known(left_ram) != is_known(right_ram):
        return 0, []

    left_storage = left.get("storage")
    right_storage = right.get("storage")
    if is_known(left_storage) and is_known(right_storage):
        if normalize_value(left_storage) != normalize_value(right_storage):
            return 0, []
        score += 16
        reasons.append("storage")
    elif is_known(left_storage) != is_known(right_storage):
        return 0, []

    left_processor = left.get("processor")
    right_processor = right.get("processor")
    if is_known(left_processor) and is_known(right_processor):
        if normalize_value(left_processor) == normalize_value(right_processor):
            score += 24
            reasons.append("processor_exact")
        elif processor_family(left_processor) == processor_family(right_processor):
            score += 16
            reasons.append("processor_family")
        else:
            return 0, []
    elif is_known(left_processor) != is_known(right_processor):
        return 0, []

    left_variant = mobile_variant_family(left.get("name", ""))
    right_variant = mobile_variant_family(right.get("name", ""))
    if left_variant and right_variant and left_variant == right_variant:
        score += 14
        reasons.append("variant_family")

    title_similarity = jaccard_similarity(
        tokenize_mobile_name(left.get("name", "")),
        tokenize_mobile_name(right.get("name", "")),
    )
    if title_similarity >= 0.25:
        title_points = min(18, round(title_similarity * 24))
        score += title_points
        reasons.append(f"title:{title_points}")

    for field, points in (("display_size", 8), ("battery", 8), ("network", 6), ("camera", 6)):
        left_value = left.get(field)
        right_value = right.get(field)
        if is_known(left_value) and is_known(right_value) and normalize_value(left_value) == normalize_value(right_value):
            score += points
            reasons.append(field)

    if title_similarity < 0.25 and "variant_family" not in reasons:
        return 0, []

    return score, reasons


def score_tv_products(left, right):
    left_brand = normalize_value(left.get("brand"))
    right_brand = normalize_value(right.get("brand"))
    if not left_brand or left_brand != right_brand:
        return 0, []

    score = 20
    reasons = ["brand"]

    core_equal_fields = (("screen_size", 16), ("resolution", 18))
    for field, points in core_equal_fields:
        left_value = left.get(field)
        right_value = right.get(field)
        if is_known(left_value) and is_known(right_value):
            if normalize_value(left_value) != normalize_value(right_value):
                return 0, []
            score += points
            reasons.append(field)
        elif is_known(left_value) != is_known(right_value):
            return 0, []

    left_variant = tv_variant_family(left.get("name", ""))
    right_variant = tv_variant_family(right.get("name", ""))
    if left_variant and right_variant and left_variant == right_variant:
        score += 16
        reasons.append("variant_family")

    title_similarity = jaccard_similarity(
        tokenize_tv_name(left.get("name", "")),
        tokenize_tv_name(right.get("name", "")),
    )
    if title_similarity >= 0.2:
        title_points = min(18, round(title_similarity * 24))
        score += title_points
        reasons.append(f"title:{title_points}")

    for field, points in (("display_type", 8), ("smart_tv", 8), ("refresh_rate", 8), ("operating_system", 8), ("audio_output", 6)):
        left_value = left.get(field)
        right_value = right.get(field)
        if is_known(left_value) and is_known(right_value) and normalize_value(left_value) == normalize_value(right_value):
            score += points
            reasons.append(field)

    if title_similarity < 0.2 and "variant_family" not in reasons:
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
    fields = [
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
    ]
    differences = {}
    for field in fields:
        result = compare_field(left, right, field)
        if result["status"] != "same":
            differences[field] = result
    return differences


def build_mobile_differences(left, right):
    fields = [
        "price",
        "original_price",
        "discount_percent",
        "rating",
        "review_count",
        "processor",
        "ram",
        "storage",
        "display_size",
        "battery",
        "camera",
        "network",
    ]
    differences = {}
    for field in fields:
        result = compare_field(left, right, field)
        if result["status"] != "same":
            differences[field] = result
    return differences


def build_tv_differences(left, right):
    fields = [
        "price",
        "original_price",
        "discount_percent",
        "rating",
        "review_count",
        "screen_size",
        "resolution",
        "display_type",
        "smart_tv",
        "refresh_rate",
        "audio_output",
        "operating_system",
    ]
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
    if is_known(left_ram) and is_known(right_ram) and normalize_value(left_ram) != normalize_value(right_ram):
        return 0, []

    left_storage = left.get("storage")
    right_storage = right.get("storage")
    if is_known(left_storage) and is_known(right_storage) and normalize_value(left_storage) != normalize_value(right_storage):
        return 0, []

    left_processor = left.get("processor")
    right_processor = right.get("processor")
    if is_known(left_processor) and is_known(right_processor):
        if processor_family(left_processor) != processor_family(right_processor):
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


def score_mobile_spec_match(left, right):
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
    if is_known(left_processor) and is_known(right_processor):
        if processor_family(left_processor) != processor_family(right_processor):
            return 0, []

    score = 20 + 15 + 15 + 18
    reasons = ["brand", "ram", "storage", "processor_family"]

    left_variant = mobile_variant_family(left.get("name", ""))
    right_variant = mobile_variant_family(right.get("name", ""))
    if left_variant and right_variant and left_variant == right_variant:
        score += 12
        reasons.append("variant_family")

    title_similarity = jaccard_similarity(
        tokenize_mobile_name(left.get("name", "")),
        tokenize_mobile_name(right.get("name", "")),
    )
    if title_similarity >= 0.12:
        title_points = min(12, round(title_similarity * 18))
        score += title_points
        reasons.append(f"title:{title_points}")

    for field, points in (("display_size", 8), ("battery", 8), ("network", 6), ("camera", 6)):
        left_value = left.get(field)
        right_value = right.get(field)
        if is_known(left_value) and is_known(right_value) and normalize_value(left_value) == normalize_value(right_value):
            score += points
            reasons.append(field)

    return score, reasons


def score_tv_spec_match(left, right):
    left_brand = normalize_value(left.get("brand"))
    right_brand = normalize_value(right.get("brand"))
    if not left_brand or left_brand != right_brand:
        return 0, []

    left_screen = left.get("screen_size")
    right_screen = right.get("screen_size")
    left_resolution = left.get("resolution")
    right_resolution = right.get("resolution")
    if not (
        is_known(left_screen) and is_known(right_screen) and normalize_value(left_screen) == normalize_value(right_screen)
        and is_known(left_resolution) and is_known(right_resolution) and normalize_value(left_resolution) == normalize_value(right_resolution)
    ):
        return 0, []

    score = 20 + 18 + 18
    reasons = ["brand", "screen_size", "resolution"]

    left_variant = tv_variant_family(left.get("name", ""))
    right_variant = tv_variant_family(right.get("name", ""))
    if left_variant and right_variant and left_variant == right_variant:
        score += 14
        reasons.append("variant_family")

    title_similarity = jaccard_similarity(
        tokenize_tv_name(left.get("name", "")),
        tokenize_tv_name(right.get("name", "")),
    )
    if title_similarity >= 0.12:
        title_points = min(14, round(title_similarity * 20))
        score += title_points
        reasons.append(f"title:{title_points}")

    for field, points in (("display_type", 8), ("smart_tv", 8), ("refresh_rate", 6), ("operating_system", 6)):
        left_value = left.get(field)
        right_value = right.get(field)
        if is_known(left_value) and is_known(right_value) and normalize_value(left_value) == normalize_value(right_value):
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
    if is_known(left_ram) and is_known(right_ram) and normalize_value(left_ram) != normalize_value(right_ram):
        return 0, []

    if is_known(left_storage) and is_known(right_storage) and normalize_value(left_storage) != normalize_value(right_storage):
        return 0, []

    left_processor = left.get("processor")
    right_processor = right.get("processor")
    if is_known(left_processor) and is_known(right_processor):
        if processor_family(left_processor) != processor_family(right_processor):
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


def score_mobile_variant_match(left, right):
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

    if processor_family(left_processor) != processor_family(right_processor):
        return 0, []

    score = 20 + 15 + 15 + 18
    reasons = ["brand", "ram", "storage", "processor_family"]

    left_variant = mobile_variant_family(left.get("name", ""))
    right_variant = mobile_variant_family(right.get("name", ""))
    if left_variant and right_variant and left_variant == right_variant:
        score += 16
        reasons.append("variant_family")

    title_similarity = jaccard_similarity(
        tokenize_mobile_name(left.get("name", "")),
        tokenize_mobile_name(right.get("name", "")),
    )
    if title_similarity >= 0.18:
        title_points = min(16, round(title_similarity * 22))
        score += title_points
        reasons.append(f"title:{title_points}")

    for field, points in (("display_size", 8), ("battery", 8), ("network", 6)):
        left_value = left.get(field)
        right_value = right.get(field)
        if is_known(left_value) and is_known(right_value) and normalize_value(left_value) == normalize_value(right_value):
            score += points
            reasons.append(field)

    if "variant_family" not in reasons and title_similarity < 0.18:
        return 0, []

    return score, reasons


def score_tv_variant_match(left, right):
    left_brand = normalize_value(left.get("brand"))
    right_brand = normalize_value(right.get("brand"))
    if not left_brand or left_brand != right_brand:
        return 0, []

    left_screen = left.get("screen_size")
    right_screen = right.get("screen_size")
    if not (
        is_known(left_screen) and is_known(right_screen) and normalize_value(left_screen) == normalize_value(right_screen)
    ):
        return 0, []

    score = 20 + 16
    reasons = ["brand", "screen_size"]

    left_resolution = left.get("resolution")
    right_resolution = right.get("resolution")
    if is_known(left_resolution) and is_known(right_resolution):
        if normalize_value(left_resolution) != normalize_value(right_resolution):
            return 0, []
        score += 16
        reasons.append("resolution")

    left_variant = tv_variant_family(left.get("name", ""))
    right_variant = tv_variant_family(right.get("name", ""))
    if left_variant and right_variant and left_variant == right_variant:
        score += 16
        reasons.append("variant_family")

    title_similarity = jaccard_similarity(
        tokenize_tv_name(left.get("name", "")),
        tokenize_tv_name(right.get("name", "")),
    )
    if title_similarity >= 0.18:
        title_points = min(16, round(title_similarity * 22))
        score += title_points
        reasons.append(f"title:{title_points}")

    for field, points in (("display_type", 8), ("smart_tv", 8), ("refresh_rate", 6)):
        left_value = left.get(field)
        right_value = right.get(field)
        if is_known(left_value) and is_known(right_value) and normalize_value(left_value) == normalize_value(right_value):
            score += points
            reasons.append(field)

    if "variant_family" not in reasons and title_similarity < 0.18:
        return 0, []

    return score, reasons


def choose_mobile_variant_match(left, candidates):
    best_match = None
    best_score = 0
    best_reasons = []

    for candidate in candidates:
        score, reasons = score_mobile_variant_match(left, candidate)
        if score > best_score:
            best_match = candidate
            best_score = score
            best_reasons = reasons

    if best_score < 70:
        return None

    return {
        "match": best_match,
        "score": best_score,
        "reasons": best_reasons,
    }


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

    if best_score < 80:
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

    if best_score < 72:
        return None

    return {
        "match": best_match,
        "score": best_score,
        "reasons": best_reasons,
    }


def choose_mobile_spec_match(left, candidates):
    best_match = None
    best_score = 0
    best_reasons = []

    for candidate in candidates:
        score, reasons = score_mobile_spec_match(left, candidate)
        if score > best_score:
            best_match = candidate
            best_score = score
            best_reasons = reasons

    if best_score < 70:
        return None

    return {
        "match": best_match,
        "score": best_score,
        "reasons": best_reasons,
    }


def choose_tv_spec_match(left, candidates):
    best_match = None
    best_score = 0
    best_reasons = []

    for candidate in candidates:
        score, reasons = score_tv_spec_match(left, candidate)
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

    if best_score < 80:
        return None

    category = "possible"
    if best_score >= 95:
        category = "high_confidence"

    return {
        "match": best_match,
        "score": best_score,
        "reasons": best_reasons,
        "category": category,
    }


def choose_mobile_match(left, candidates):
    best_match = None
    best_score = 0
    best_reasons = []

    for candidate in candidates:
        score, reasons = score_mobile_products(left, candidate)
        if score > best_score:
            best_match = candidate
            best_score = score
            best_reasons = reasons

    if best_score < 78:
        return None

    category = "possible"
    if best_score >= 92:
        category = "high_confidence"

    return {
        "match": best_match,
        "score": best_score,
        "reasons": best_reasons,
        "category": category,
    }


def choose_tv_match(left, candidates):
    best_match = None
    best_score = 0
    best_reasons = []

    for candidate in candidates:
        score, reasons = score_tv_products(left, candidate)
        if score > best_score:
            best_match = candidate
            best_score = score
            best_reasons = reasons

    if best_score < 76:
        return None

    category = "possible"
    if best_score >= 90:
        category = "high_confidence"

    return {
        "match": best_match,
        "score": best_score,
        "reasons": best_reasons,
        "category": category,
    }


def choose_tv_variant_match(left, candidates):
    best_match = None
    best_score = 0
    best_reasons = []

    for candidate in candidates:
        score, reasons = score_tv_variant_match(left, candidate)
        if score > best_score:
            best_match = candidate
            best_score = score
            best_reasons = reasons

    if best_score < 72:
        return None

    return {
        "match": best_match,
        "score": best_score,
        "reasons": best_reasons,
    }


def comparison_payload(query=None, limit=20, category="laptops"):
    mongo_query = {}
    if query:
        mongo_query["name"] = {"$regex": re.escape(query), "$options": "i"}

    collection = get_collection(category)
    normalized_category = (category or "laptops").strip().lower()
    is_mobile_category = normalized_category == "mobiles"
    is_tv_category = normalized_category == "tvs"

    projection = {
        "_id": 1,
        "name": 1,
        "price": 1,
        "original_price": 1,
        "discount_amount": 1,
        "discount_percent": 1,
        "rating": 1,
        "review_count": 1,
        "link": 1,
        "image": 1,
        "website": 1,
        "category": 1,
        "currency": 1,
        "brand": 1,
        "ram": 1,
        "storage": 1,
        "processor": 1,
        "last_seen_at": 1,
    }
    if is_mobile_category:
        projection.update({
            "display_size": 1,
            "camera": 1,
            "battery": 1,
            "network": 1,
        })
    elif is_tv_category:
        projection.update({
            "screen_size": 1,
            "resolution": 1,
            "display_type": 1,
            "smart_tv": 1,
            "refresh_rate": 1,
            "audio_output": 1,
            "operating_system": 1,
        })
    else:
        projection.update({
            "screen_size": 1,
            "gpu": 1,
            "model_code": 1,
        })

    products = list(
        collection.find(mongo_query, projection)
    )

    amazon_products = [product for product in products if product.get("website") == "amazon" and normalize_value(product.get("brand"))]
    flipkart_products = [product for product in products if product.get("website") == "flipkart" and normalize_value(product.get("brand"))]
    flipkart_by_brand = build_candidate_groups(flipkart_products)

    exact_matches = []
    variant_matches = []
    possible_matches = []
    spec_comparable_matches = []
    fallback_matches = []
    
    # Tracking for 100% coverage
    amazon_matched_ids = set()
    flipkart_matched_ids = set()
    
    def _get_processor_family(proc_str):
        if not proc_str or proc_str == "Unknown":
            return None
        text = proc_str.lower()
        if "i3" in text: return "i3"
        if "i5" in text: return "i5"
        if "i7" in text: return "i7"
        if "i9" in text: return "i9"
        if "ryzen 3" in text: return "ryzen 3"
        if "ryzen 5" in text: return "ryzen 5"
        if "ryzen 7" in text: return "ryzen 7"
        if "ryzen 9" in text: return "ryzen 9"
        if "m1" in text: return "m1"
        if "m2" in text: return "m2"
        if "m3" in text: return "m3"
        if "celeron" in text: return "celeron"
        if "pentium" in text: return "pentium"
        return None

    def _get_fallback_score(anchor, candidate):
        score = 0
        
        # 1. Processor Family (Highest Weight)
        a_proc = _get_processor_family(anchor.get("processor") or anchor.get("name"))
        c_proc = _get_processor_family(candidate.get("processor") or candidate.get("name"))
        if a_proc and c_proc and a_proc == c_proc:
            score += 50
            
        # 2. RAM Proximity
        try:
            a_ram = int(re.search(r'(\d+)', anchor.get("ram") or "").group(1))
            c_ram = int(re.search(r'(\d+)', candidate.get("ram") or "").group(1))
            if a_ram == c_ram:
                score += 20
        except: pass
        
        # 3. Storage Proximity
        try:
            a_st = int(re.search(r'(\d+)', anchor.get("storage") or "").group(1))
            c_st = int(re.search(r'(\d+)', candidate.get("storage") or "").group(1))
            if a_st == c_st:
                score += 10
        except: pass
        
        # 4. Price Proximity (Lower absolute diff is better)
        a_price = anchor.get("price") or 0
        c_price = candidate.get("price") or 0
        if a_price > 0 and c_price > 0:
            diff_ratio = abs(a_price - c_price) / a_price
            if diff_ratio < 0.1: score += 20
            elif diff_ratio < 0.25: score += 10
            
        return score

    for amazon_product in amazon_products:
        brand_key = normalize_value(amazon_product.get("brand"))
        if not brand_key:
            continue

        candidate_group = flipkart_by_brand.get(brand_key, [])
        if not candidate_group:
            continue

        variant_result = (
            choose_mobile_variant_match(amazon_product, candidate_group)
            if is_mobile_category
            else choose_tv_variant_match(amazon_product, candidate_group)
            if is_tv_category
            else choose_variant_match(amazon_product, candidate_group)
        )
        spec_result = (
            choose_mobile_spec_match(amazon_product, candidate_group)
            if is_mobile_category
            else choose_tv_spec_match(amazon_product, candidate_group)
            if is_tv_category
            else choose_spec_match(amazon_product, candidate_group)
        )
        result = (
            choose_mobile_match(amazon_product, candidate_group)
            if is_mobile_category
            else choose_tv_match(amazon_product, candidate_group)
            if is_tv_category
            else choose_match(amazon_product, candidate_group)
        )

        if result:
            flipkart_product = result["match"]
            amazon_price = amazon_product.get("price") or 0
            flipkart_price = flipkart_product.get("price") or 0

            match_payload = {
                "score": result["score"],
                "match_reasons": result["reasons"],
                "amazon": amazon_product,
                "flipkart": flipkart_product,
                "differences": (
                    build_mobile_differences(amazon_product, flipkart_product)
                    if is_mobile_category
                    else build_tv_differences(amazon_product, flipkart_product)
                    if is_tv_category
                    else build_differences(amazon_product, flipkart_product)
                ),
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
                amazon_matched_ids.add(str(amazon_product.get("_id")))
                flipkart_matched_ids.add(str(flipkart_product.get("_id")))
                continue

            possible_matches.append({
                **match_payload,
                "match_type": "possible",
                "confidence_label": "Close Match",
            })
            amazon_matched_ids.add(str(amazon_product.get("_id")))
            flipkart_matched_ids.add(str(flipkart_product.get("_id")))
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
                "differences": (
                    build_mobile_differences(amazon_product, matched)
                    if is_mobile_category
                    else build_tv_differences(amazon_product, matched)
                    if is_tv_category
                    else build_differences(amazon_product, matched)
                ),
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
            amazon_matched_ids.add(str(amazon_product.get("_id")))
            flipkart_matched_ids.add(str(matched.get("_id")))
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
                "differences": (
                    build_mobile_differences(amazon_product, matched)
                    if is_mobile_category
                    else build_tv_differences(amazon_product, matched)
                    if is_tv_category
                    else build_differences(amazon_product, matched)
                ),
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
            amazon_matched_ids.add(str(amazon_product.get("_id")))
            flipkart_matched_ids.add(str(matched.get("_id")))

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

    # === FALLBACK LOGIC AMZ -> FK ===
    amazon_orphans = [p for p in amazon_products if str(p.get("_id")) not in amazon_matched_ids]
    
    # Pre-fetch some global Flipkart items for the "Rare Case" fallback
    global_flipkart = []
    if amazon_orphans:
        global_flipkart = list(collection.find(
            {"website": "flipkart", "category": "laptops"},
            projection
        ).limit(10))

    for amazon_product in amazon_orphans:
        brand_key = normalize_value(amazon_product.get("brand"))
        candidates = flipkart_by_brand.get(brand_key, [])
        if not candidates:
            # Fallback to current search results
            candidates = flipkart_products[:10]
        if not candidates:
            # Fallback to global database
            candidates = global_flipkart

        ranked = []
        for c in candidates:
            score = _get_fallback_score(amazon_product, c)
            price_diff = abs((amazon_product.get("price") or 0) - (c.get("price") or 0))
            ranked.append((score, price_diff, c))
            
        ranked.sort(key=lambda x: (-x[0], x[1]))
        
        for score, p_diff, matched in ranked[:3]:
            fallback_matches.append({
                "score": score,
                "match_reasons": ["fallback"],
                "amazon": amazon_product,
                "flipkart": matched,
                "differences": (
                    build_differences(amazon_product, matched) 
                    if not is_mobile_category and not is_tv_category 
                    else {}
                ),
                "price_difference": p_diff,
                "cheaper_site": "amazon" if (amazon_product.get("price") or 0) < (matched.get("price") or 0) else "flipkart",
                "match_type": "fallback",
                "confidence_label": "Recommended Alternatives",
            })

    # === FALLBACK LOGIC FK -> AMZ ===
    flipkart_orphans = [p for p in flipkart_products if str(p.get("_id")) not in flipkart_matched_ids]
    
    global_amazon = []
    if flipkart_orphans:
        global_amazon = list(collection.find(
            {"website": "amazon", "category": "laptops"},
            projection
        ).limit(10))

    amazon_by_brand = build_candidate_groups(amazon_products)
    for flipkart_product in flipkart_orphans:
        brand_key = normalize_value(flipkart_product.get("brand"))
        candidates = amazon_by_brand.get(brand_key, [])
        if not candidates:
            candidates = amazon_products[:10]
        if not candidates:
            candidates = global_amazon

        ranked = []
        for c in candidates:
            score = _get_fallback_score(flipkart_product, c)
            price_diff = abs((flipkart_product.get("price") or 0) - (c.get("price") or 0))
            ranked.append((score, price_diff, c))
            
        ranked.sort(key=lambda x: (-x[0], x[1]))
        
        for score, p_diff, matched in ranked[:3]:
            fallback_matches.append({
                "score": score,
                "match_reasons": ["fallback"],
                "amazon": matched,
                "flipkart": flipkart_product,
                "differences": (
                    build_differences(matched, flipkart_product) 
                    if not is_mobile_category and not is_tv_category 
                    else {}
                ),
                "price_difference": p_diff,
                "cheaper_site": "amazon" if (matched.get("price") or 0) < (flipkart_product.get("price") or 0) else "flipkart",
                "match_type": "fallback",
                "confidence_label": "Recommended Alternatives",
            })
    return {
        "query": query or "",
        "category": normalized_category,
        "high_confidence_total": len(exact_matches),
        "exact_total": len(exact_matches),
        "variant_total": len(variant_matches),
        "possible_total": len(possible_matches),
        "spec_comparable_total": len(spec_comparable_matches),
        "fallback_total": len(fallback_matches),
        "all_comparable_total": len(all_comparable_matches),
        "best_value_total": len(best_value_matches),
        "high_confidence_matches": exact_matches[:limit],
        "exact_matches": exact_matches[:limit],
        "variant_matches": variant_matches[:limit],
        "possible_matches": possible_matches[:limit],
        "spec_comparable_matches": spec_comparable_matches[:limit],
        "fallback_matches": fallback_matches[:limit],
        "all_comparable_matches": all_comparable_matches[:limit],
        "best_value_matches": best_value_matches[:limit],
    }
