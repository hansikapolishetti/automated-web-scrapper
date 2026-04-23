import re
from collections import defaultdict

from database.db import get_collection
from utils.feature_extractor import normalize_text
from utils.classification.router import classify_product
from utils.classification.helpers import (
    normalize_value, normalized_model_code, processor_family, is_known, UNKNOWN_VALUES
)


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


def comparable_name(name):

    cleaned = normalize_value(name)
    cleaned = re.sub(r"[^a-z0-9\s]", " ", cleaned)
    return " ".join(token for token in cleaned.split() if token not in NOISE_TOKENS)


def model_code_prefix(value):

    code = normalized_model_code(value)
    if not code:
        return ""
    return code.split("-")[0]


def extract_series(name):
    """Extract a laptop series identifier from a product name (laptops only)."""
    name = normalize_value(name)
    
    # Lenovo
    if "slim 3" in name: return "slim3"
    if "slim 5" in name: return "slim5"
    if "slim 7" in name: return "slim7"
    if "ideapad 3" in name: return "ideapad3"
    if "ideapad 5" in name: return "ideapad5"
    if "v14" in name: return "v14"
    if "v15" in name: return "v15"
    if "thinkpad" in name: return "thinkpad"
    if "loq" in name: return "loq"
    if "legion" in name: return "legion"

    # HP
    if "pavilion" in name: return "pavilion"
    if "spectre" in name: return "spectre"
    if "envy" in name: return "envy"
    if "victus" in name: return "victus"
    if "omen" in name: return "omen"
    if "probook" in name: return "probook"
    if "elitebook" in name: return "elitebook"
    if "omnibook" in name: return "omnibook"
    if "chromebook" in name: return "chromebook"
    
    # HP numbered specific overlaps
    if re.search(r'\b250\b.*?\bg\d{1,2}\b|\b250\b', name): return "hp250"
    if re.search(r'\b255\b.*?\bg\d{1,2}\b|\b255\b', name): return "hp255"
    if re.search(r'\b15s\b', name): return "hp15s"
    if re.search(r'\b14s\b', name): return "hp14s"
    if re.search(r'\bhp\b.*?\b15\b', name) and "15s" not in name: return "hp15"
    if re.search(r'\bhp\b.*?\b14\b', name) and "14s" not in name: return "hp14"

    # Apple
    if "macbook air" in name: return "macbookair"
    if "macbook pro" in name: return "macbookpro"

    # Asus
    if "vivobook go" in name: return "vivobook_go"
    match = re.search(r'vivobook\s+\d+', name)
    if match: return match.group().replace(" ", "")
    if "vivobook" in name: return "vivobook"
    if "zenbook" in name: return "zenbook"
    if "tuf" in name: return "tuf"
    if "rog" in name: return "rog"

    # Dell
    if "inspiron" in name: return "inspiron"
    if "vostro" in name: return "vostro"
    if "xps" in name: return "xps"
    if "alienware" in name: return "alienware"
    
    # Acer
    if "aspire" in name: return "aspire"
    if "nitro" in name: return "nitro"
    if "predator" in name: return "predator"
    if "swift" in name: return "swift"

    return None


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
    return " ".join(tokens[:1])


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
    """Score two laptop products for matching (laptops only)."""
    score = 0
    reasons = []

    # 1. Brand gate (MUST MATCH)
    left_brand = normalize_value(left.get("brand"))
    right_brand = normalize_value(right.get("brand"))
    if left_brand and right_brand and left_brand == right_brand:
        score += 20
        reasons.append("brand")
    else:
        return 0, []

    # 2. Strict series rejection
    left_series = extract_series(left.get("name", ""))
    right_series = extract_series(right.get("name", ""))
    if left_series and right_series and left_series != right_series:
        return 0, []

    # 3. Processor Family gate (MUST MATCH if known)
    left_processor = left.get("processor")
    right_processor = right.get("processor")
    if is_known(left_processor) and is_known(right_processor):
        if processor_family(left_processor) != processor_family(right_processor):
            return 0, []
        if normalize_value(left_processor) == normalize_value(right_processor):
            score += 30
            reasons.append("processor_exact")
        else:
            score += 18
            reasons.append("processor_family")

    # 4. RAM & Storage gate (MUST MATCH if known)
    left_ram = left.get("ram")
    right_ram = right.get("ram")
    if is_known(left_ram) and is_known(right_ram) and normalize_value(left_ram) != normalize_value(right_ram):
        return 0, []

    left_storage = left.get("storage")
    right_storage = right.get("storage")
    if is_known(left_storage) and is_known(right_storage) and normalize_value(left_storage) != normalize_value(right_storage):
        return 0, []

    # 5. Model Code Bonus (No longer short-circuits)
    left_code = normalized_model_code(left.get("model_code"))
    right_code = normalized_model_code(right.get("model_code"))
    if left_code and right_code and left_code == right_code:
        score += 65
        reasons.append("model_code_exact")

    # 6. Variant Family matching
    left_variant = variant_family(left.get("name", ""))
    right_variant = variant_family(right.get("name", ""))
    if left_variant and right_variant and left_variant == right_variant:
        score += 15
        reasons.append("variant_family")

    # 7. Title similarity
    left_tokens = tokenize_name(left.get("name", ""))
    right_tokens = tokenize_name(right.get("name", ""))
    title_similarity = jaccard_similarity(left_tokens, right_tokens)
    if title_similarity >= 0.4:
        title_points = min(30, round(title_similarity * 35))
        score += title_points
        reasons.append(f"title:{title_points}")
    elif not (is_known(left.get("model_code")) and is_known(right.get("model_code"))):
        # If model codes unknown, fallback to needing better title match
        if title_similarity < 0.25:
            return 0, []

    # 8. Extra spec bonuses
    for field, points in (("ram", 10), ("storage", 10), ("screen_size", 8), ("gpu", 8)):
        left_val = left.get(field)
        right_val = right.get(field)
        if is_known(left_val) and is_known(right_val) and normalize_value(left_val) == normalize_value(right_val):
            if field not in reasons: # avoid double counting ramp/storage if matched above
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
    """Score two laptops for similar-spec matching (laptops only)."""
    # HARD FILTER: RAM must match exactly
    if normalize_value(left.get("ram")) != normalize_value(right.get("ram")):
        return 0, []

    left_brand = normalize_value(left.get("brand"))
    right_brand = normalize_value(right.get("brand"))
    if not left_brand or left_brand != right_brand:
        return 0, []

    left_processor = left.get("processor")
    right_processor = right.get("processor")
    
    # Must have same processor family for "Similar Specs"
    if is_known(left_processor) and is_known(right_processor):
        if processor_family(left_processor) != processor_family(right_processor):
            return 0, []

    score = 20 # brand
    reasons = ["brand"]
    
    if is_known(left_processor) and is_known(right_processor):
        score += 20
        reasons.append("processor_family")

    # RAM and Storage SHOULD be identical for it to be a "Spec Match" usually, 
    # but we don't hard reject. We just give heavy points if they do match.
    left_ram = left.get("ram")
    right_ram = right.get("ram")
    if is_known(left_ram) and is_known(right_ram) and normalize_value(left_ram) == normalize_value(right_ram):
        score += 15
        reasons.append("ram")

    left_storage = left.get("storage")
    right_storage = right.get("storage")
    if is_known(left_storage) and is_known(right_storage) and normalize_value(left_storage) == normalize_value(right_storage):
        score += 15
        reasons.append("storage")

    left_tokens = tokenize_name(left.get("name", ""))
    right_tokens = tokenize_name(right.get("name", ""))
    title_similarity = jaccard_similarity(left_tokens, right_tokens)

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
                # Exact model code match only; prefix matching disabled for laptops
                if normalized_model_code(left_value) == normalized_model_code(right_value):
                    score += points
                    reasons.append("model_code_exact")
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
    """Score two laptops for variant matching (laptops only)."""
    # HARD FILTER: RAM & Storage must match exactly
    if normalize_value(left.get("ram")) != normalize_value(right.get("ram")):
        return 0, []
    if normalize_value(left.get("storage")) != normalize_value(right.get("storage")):
        return 0, []

    left_brand = normalize_value(left.get("brand"))
    right_brand = normalize_value(right.get("brand"))
    if not left_brand or left_brand != right_brand:
        return 0, []

    left_processor = left.get("processor")
    right_processor = right.get("processor")

    score = 20 # brand
    reasons = ["brand"]
    
    if is_known(left_processor) and is_known(right_processor):
        score += 18
        reasons.append("processor_family")

    left_ram = left.get("ram")
    right_ram = right.get("ram")
    left_storage = left.get("storage")
    right_storage = right.get("storage")

    if is_known(left_ram) and is_known(right_ram) and normalize_value(left_ram) == normalize_value(right_ram):
        score += 15
        reasons.append("ram")
        
    if is_known(left_storage) and is_known(right_storage) and normalize_value(left_storage) == normalize_value(right_storage):
        score += 15
        reasons.append("storage")

    left_variant = variant_family(left.get("name", ""))
    right_variant = variant_family(right.get("name", ""))
    
    # FOR A VARIANT: the product family is the most important signal!
    if left_variant and right_variant and left_variant == right_variant:
        score += 35 # heavily weighted!
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
        # model_code_prefix match intentionally disabled for laptops
        # (was causing cross-model grouping of unrelated models)

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
    """Placeholder or mobile logic if needed in future."""
    return 0, []
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

def get_fallback_score(anchor, candidate, is_mobile_category=False, is_tv_category=False):
    score = 0

    # 1. Brand (must match)
    anchor_brand = normalize_value(anchor.get("brand"))
    candidate_brand = normalize_value(candidate.get("brand"))
    if anchor_brand and candidate_brand and anchor_brand == candidate_brand:
        score += 20
    else:
        return 0  # reject different brand

    # 2. Processor family
    if is_known(anchor.get("processor")) and is_known(candidate.get("processor")):
        if processor_family(anchor.get("processor")) == processor_family(candidate.get("processor")):
            score += 25

    # 3. RAM match / closeness
    try:
        a_ram_match = re.search(r'(\d+)', str(anchor.get("ram") or ""))
        c_ram_match = re.search(r'(\d+)', str(candidate.get("ram") or ""))
        if a_ram_match and c_ram_match:
            a_ram = int(a_ram_match.group(1))
            c_ram = int(c_ram_match.group(1))
            if a_ram == c_ram:
                score += 15
            elif abs(a_ram - c_ram) <= 8:
                score += 8
    except: pass

    # 4. Storage
    try:
        a_st_match = re.search(r'(\d+)', str(anchor.get("storage") or ""))
        c_st_match = re.search(r'(\d+)', str(candidate.get("storage") or ""))
        if a_st_match and c_st_match:
            a_st = int(a_st_match.group(1))
            c_st = int(c_st_match.group(1))
            if a_st == c_st:
                score += 10
    except: pass

    # 5. SERIES / PRODUCT TYPE (VERY IMPORTANT)
    if is_mobile_category:
        a_ser = mobile_variant_family(anchor.get("name", ""))
        c_ser = mobile_variant_family(candidate.get("name", ""))
    elif is_tv_category:
        a_ser = tv_variant_family(anchor.get("name", ""))
        c_ser = tv_variant_family(candidate.get("name", ""))
    else:
        a_ser = extract_series(anchor.get("name", ""))
        c_ser = extract_series(candidate.get("name", ""))

    if a_ser and c_ser and a_ser == c_ser:
        score += 30

    # 6. Screen size proximity
    try:
        a_scr_match = re.search(r'(\d+\.?\d*)', str(anchor.get("screen_size") or ""))
        c_scr_match = re.search(r'(\d+\.?\d*)', str(candidate.get("screen_size") or ""))
        if a_scr_match and c_scr_match:
            a_scr = float(a_scr_match.group(1))
            c_scr = float(c_scr_match.group(1))
            if abs(a_scr - c_scr) <= 1:
                score += 10
    except: pass

    # 7. Price proximity
    a_price = anchor.get("price") or 0
    c_price = candidate.get("price") or 0
    if a_price > 0 and c_price > 0:
        price_diff = abs(a_price - c_price)
        if price_diff / max(a_price, 1) < 0.2:
            score += 15

    return score


def comparison_payload(query=None, limit=20, category="laptops"):
    mongo_query = {}
    if query:
        mongo_query["name"] = {"$regex": re.escape(query), "$options": "i"}

    collection = get_collection(category)
    normalized_category = (category or "laptops").strip().lower()
    is_mobile_category = normalized_category == "mobiles"
    is_tv_category = normalized_category == "tvs"

    projection = {
        "name": 1,
        "brand": 1,
        "price": 1,
        "original_price": 1,
        "discount_percent": 1,
        "rating": 1,
        "review_count": 1,
        "image": 1,
        "images": 1,
        "link": 1,
        "website": 1,
        "slug": 1,
        "specifications": 1,
    }

    if is_mobile_category:
        projection.update({
            "ram": 1,
            "storage": 1,
            "processor": 1,
            "display_size": 1,
            "battery": 1,
            "network": 1,
            "camera": 1,
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
            "ram": 1,
            "storage": 1,
            "processor": 1,
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

    from utils.classification.router import classify_product

    exact_matches = []
    variant_matches = []
    possible_matches = []
    spec_comparable_matches = []
    fallback_matches = []
    
    seen_flipkart_ids = set()

    for amazon_product in amazon_products:
        brand_key = normalize_value(amazon_product.get("brand"))
        candidates = flipkart_by_brand.get(brand_key, [])
        if not candidates:
            candidates = flipkart_products[:20] # basic fallback if no brand match

        for candidate in candidates:
            candidate_id = str(candidate.get("_id")) or candidate.get("link")
            if candidate_id in seen_flipkart_ids:
                continue

            match_type = classify_product(amazon_product, candidate, normalized_category)

            amazon_price = amazon_product.get("price") or 0
            flipkart_price = candidate.get("price") or 0
            price_difference = abs(amazon_price - flipkart_price)
            cheaper_site = "amazon" if amazon_price < flipkart_price else "flipkart" if flipkart_price < amazon_price else "same"
            differences = build_differences(amazon_product, candidate) if not is_mobile_category and not is_tv_category else {}

            if match_type == "exact":
                score, reasons = score_products(amazon_product, candidate)
                exact_matches.append({
                    "score": score,
                    "match_reasons": reasons,
                    "amazon": amazon_product,
                    "flipkart": candidate,
                    "differences": differences,
                    "price_difference": price_difference,
                    "cheaper_site": cheaper_site,
                    "match_type": "exact",
                    "confidence_label": "Exact Match",
                })
                seen_flipkart_ids.add(candidate_id)

            elif match_type == "variant":
                score, reasons = score_variant_match(amazon_product, candidate)
                variant_matches.append({
                    "score": score,
                    "match_reasons": reasons,
                    "amazon": amazon_product,
                    "flipkart": candidate,
                    "differences": differences,
                    "price_difference": price_difference,
                    "cheaper_site": cheaper_site,
                    "match_type": "variant",
                    "confidence_label": "Variant Match",
                })
                seen_flipkart_ids.add(candidate_id)

            elif match_type == "similar":
                score, reasons = score_spec_match(amazon_product, candidate)
                spec_comparable_matches.append({
                    "score": score,
                    "match_reasons": reasons,
                    "amazon": amazon_product,
                    "flipkart": candidate,
                    "differences": differences,
                    "price_difference": price_difference,
                    "cheaper_site": cheaper_site,
                    "match_type": "similar_specs",
                    "confidence_label": "Similar Specs",
                })
                seen_flipkart_ids.add(candidate_id)

            else:
                score = get_fallback_score(amazon_product, candidate, is_mobile_category, is_tv_category)
                if score > 0: # Only add somewhat relevant recommended fallbacks
                    possible_matches.append({
                        "score": score,
                        "match_reasons": ["fallback"],
                        "amazon": amazon_product,
                        "flipkart": candidate,
                        "differences": differences,
                        "price_difference": price_difference,
                        "cheaper_site": cheaper_site,
                        "match_type": "fallback",
                        "confidence_label": "Recommended Alternatives",
                    })

                    # DO NOT add to seen_flipkart_ids for fallback, so they can be reused if needed


    exact_matches.sort(key=lambda item: (-item["score"], item["price_difference"]))
    variant_matches.sort(key=lambda item: (-item["score"], item["price_difference"]))
    possible_matches.sort(key=lambda item: (-item["score"], item["price_difference"]))
    spec_comparable_matches.sort(key=lambda item: (-item["score"], item["price_difference"]))
    fallback_matches.sort(key=lambda item: (-item["score"], item["price_difference"]))
    
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
        "all_comparable_matches": all_comparable_matches[:limit],

        "best_value_matches": best_value_matches[:limit],
    }
