from utils.feature_extractor import normalize_text

UNKNOWN_VALUES = {"", None, "Unknown", "Unavailable"}

def is_known(value):
    return value not in UNKNOWN_VALUES

def normalize_value(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return normalize_text(value).lower()
    return str(value).strip().lower()

def normalized_model_code(value):
    code = normalize_value(value).replace(" ", "")
    return code

def processor_family(processor):
    if not processor:
        return "unknown"
    p = str(processor).lower()

    # Intel Old
    if "core i3" in p: return "i3"
    if "core i5" in p: return "i5"
    if "core i7" in p: return "i7"
    if "core i9" in p: return "i9"

    # Intel New
    if "core 3" in p: return "i3"
    if "core 5" in p: return "i5"
    if "core 7" in p: return "i7"

    # AMD
    if "ryzen 3" in p: return "ryzen_3"
    if "ryzen 5" in p: return "ryzen_5"
    if "ryzen 7" in p: return "ryzen_7"
    if "ryzen 9" in p: return "ryzen_9"

    # Basic Fallback
    if "i3" in p: return "i3"
    if "i5" in p: return "i5"
    if "i7" in p: return "i7"
    if "i9" in p: return "i9"

    return p



def same_brand(a, b):
    a_brand = normalize_value(a.get("brand"))
    b_brand = normalize_value(b.get("brand"))
    return bool(a_brand and b_brand and a_brand == b_brand)

def same_model_code(a, b):
    m1 = a.get("model_code")
    m2 = b.get("model_code")

    if not m1 or not m2 or m1 == "Unknown" or m2 == "Unknown":
        return False

    return m1 == m2

def same_ram(a, b):
    a_ram = normalize_value(a.get("ram"))
    b_ram = normalize_value(b.get("ram"))
    return bool(a_ram and b_ram and a_ram == b_ram)

def same_storage(a, b):
    a_st = normalize_value(a.get("storage"))
    b_st = normalize_value(b.get("storage"))
    return bool(a_st and b_st and a_st == b_st)

def price_close(a, b, threshold=0.15):
    try:
        p1 = float(a.get("price") or 0)
        p2 = float(b.get("price") or 0)
        return abs(p1 - p2) / max(p1, p2, 1) <= threshold
    except:
        return False

def ram_close(a, b):
    import re
    try:
        a_ram_match = re.search(r'(\d+)', str(a.get("ram") or ""))
        b_ram_match = re.search(r'(\d+)', str(b.get("ram") or ""))
        if a_ram_match and b_ram_match:
            a_ram = int(a_ram_match.group(1))
            b_ram = int(b_ram_match.group(1))
            if a_ram == b_ram or abs(a_ram - b_ram) <= 8:
                return True
    except:
        pass
    return False
