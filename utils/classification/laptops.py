import re
from utils.classification.helpers import (
    same_brand, same_model_code, same_ram, same_storage, price_close, ram_close,
    normalize_value, processor_family, is_known
)


def extract_cpu_family(processor):
    if not processor:
        return "unknown"

    p = str(processor).lower()

    # INTEL OLD NAMING
    if "core i3" in p:
        return "i3"
    if "core i5" in p:
        return "i5"
    if "core i7" in p:
        return "i7"
    if "core i9" in p:
        return "i9"

    # INTEL NEW NAMING (IMPORTANT FIX)
    if "core 3" in p:
        return "i3"
    if "core 5" in p:
        return "i5"
    if "core 7" in p:
        return "i7"

    # AMD
    if "ryzen 3" in p:
        return "ryzen_3"
    if "ryzen 5" in p:
        return "ryzen_5"
    if "ryzen 7" in p:
        return "ryzen_7"
    if "ryzen 9" in p:
        return "ryzen_9"

    # Fallback to direct substring match if above specific patterns miss
    if "i3" in p: return "i3"
    if "i5" in p: return "i5"
    if "i7" in p: return "i7"
    if "i9" in p: return "i9"

    return "unknown"

def parse_processor(processor):
    if not processor:
        return {
            "brand": "unknown",
            "family": "unknown",
            "generation": None,
            "sku": None,
            "segment": "unknown"
        }

    p = str(processor).lower()
    brand = "intel" if "intel" in p else "amd" if "ryzen" in p else "unknown"
    family = extract_cpu_family(p)


    # SKU extraction
    sku_match = re.search(r'(\d{4,5}[a-z]{0,2})', p)
    sku = sku_match.group(1) if sku_match else None

    # Generation
    generation = None
    if sku:
        generation = int(str(sku)[:2])
    else:
        gen_match = re.search(r'(\d{2})(?:th)? gen', p)
        if gen_match:
            generation = int(gen_match.group(1))

    # Segment
    segment = "unknown"
    if sku:
        if "hx" in sku:
            segment = "hx"
        elif "h" in sku:
            segment = "h"
        elif "u" in sku:
            segment = "u"
        elif "p" in sku:
            segment = "p"

    return {
        "brand": brand,
        "family": family,
        "generation": generation,
        "sku": sku,
        "segment": segment
    }

def same_cpu_family(a, b):
    p1 = parse_processor(a.get("processor"))
    p2 = parse_processor(b.get("processor"))

    if p1["family"] == "unknown" or p2["family"] == "unknown":
        return False

    return p1["family"] == p2["family"]

def same_cpu_exact(a, b):
    p1 = parse_processor(a.get("processor"))
    p2 = parse_processor(b.get("processor"))

    return bool(p1["sku"] and p1["sku"] == p2["sku"])


def extract_series(name):
    name = (name or "").lower()

    known_series = [
        "vivobook", "vostro", "inspiron", "victus",
        "pavilion", "thinkpad", "ideapad", "loq",
        "hp 15", "hp 14"
    ]


    for series in known_series:
        if series in name:
            return series

    return None

def same_series(a, b):
    s1 = extract_series(a.get("name"))
    s2 = extract_series(b.get("name"))

    if not s1 or not s2:
        return False

    return s1 == s2

def cpu_generation_close(a, b):
    p1 = parse_processor(a.get("processor"))
    p2 = parse_processor(b.get("processor"))

    if p1["generation"] is None or p2["generation"] is None:
        return False

    return abs(p1["generation"] - p2["generation"]) <= 1

def same_cpu_segment(a, b):
    p1 = parse_processor(a.get("processor"))
    p2 = parse_processor(b.get("processor"))

    return p1["segment"] == p2["segment"]


def gpu_same_category(g1, g2):
    if "rtx" in g1 and "rtx" in g2:
        return True
    if "gtx" in g1 and "gtx" in g2:
        return True
    if "intel" in g1 and "intel" in g2:
        return True
    if "radeon" in g1 and "radeon" in g2:
        return True

    return False

def gpu_comparable(a, b):
    g1 = (a.get("gpu") or "").lower()
    g2 = (b.get("gpu") or "").lower()

    if not g1 or not g2 or g1 == "unknown" or g2 == "unknown":
        return True   # safely ignore GPU

    return gpu_same_category(g1, g2)

def same_gpu(a, b):
    g1 = (a.get("gpu") or "").lower()
    g2 = (b.get("gpu") or "").lower()

    # If GPU missing or unknown, do NOT allow fallback
    if not g1 or not g2 or "unknown" in g1 or "unknown" in g2:
        return False

    return g1 == g2


def is_exact_laptop(left, right):
    # Primary condition (model_code and core specs must all match)
    if (
        same_brand(left, right) and
        same_model_code(left, right) and
        same_cpu_exact(left, right) and
        same_ram(left, right) and
        same_storage(left, right)
    ):
        return True

    # Fallback exact detection (Strict specs match when model_code is missing or mismatched)
    if (
        same_brand(left, right) and
        same_cpu_exact(left, right) and
        same_ram(left, right) and
        same_storage(left, right) and
        same_gpu(left, right) and
        price_close(left, right, threshold=0.1)
    ):
        return True

    return False


def is_variant_laptop(left, right):
    return (
        same_brand(left, right) and
        same_series(left, right) and
        same_ram(left, right) and
        same_storage(left, right) and
        same_cpu_family(left, right)
    )


def storage_close(a, b):
    return a.get("storage") == b.get("storage")

def screen_close(a, b):
    try:
        s1 = float(str(a.get("screen_size")).replace('"',''))
        s2 = float(str(b.get("screen_size")).replace('"',''))
        return abs(s1 - s2) <= 1.0
    except:
        return False

def is_similar_laptop(left, right):
    return (
        same_brand(left, right) and
        same_cpu_family(left, right) and
        same_ram(left, right) and
        price_close(left, right)
    )


def is_recommended_laptop(left, right):
    # Recommended is the catch-all fallback
    return True


def validate_processor(product):
    name = (product.get("name") or "").lower()
    proc = (product.get("processor") or "").lower()

    if "i3" in name and "i5" in proc:
        product["processor"] = "intel_i3"
    elif "i5" in name and "i3" in proc:
        product["processor"] = "intel_i5"
    elif "i7" in name and "i5" in proc:
        product["processor"] = "intel_i7"

    return product

def classify_laptop(left, right):
    left = validate_processor(left.copy())
    right = validate_processor(right.copy())

    if is_exact_laptop(left, right):
        return "exact"
    elif is_variant_laptop(left, right):
        return "variant"
    elif is_similar_laptop(left, right):
        return "similar"
    elif is_recommended_laptop(left, right):
        return "recommended"
    else:
        return None
