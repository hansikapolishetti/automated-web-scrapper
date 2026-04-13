import re


UNKNOWN_BRAND = "Unknown"
UNKNOWN_RAM = "Unknown"
UNKNOWN_STORAGE = "Unknown"
UNKNOWN_PROCESSOR = "Unknown"
UNKNOWN_DISPLAY_SIZE = "Unknown"
UNKNOWN_CAMERA = "Unknown"
UNKNOWN_BATTERY = "Unknown"
UNKNOWN_NETWORK = "Unknown"

KNOWN_BRANDS = {
    "apple": "Apple",
    "samsung": "Samsung",
    "oneplus": "OnePlus",
    "xiaomi": "Xiaomi",
    "redmi": "Redmi",
    "realme": "Realme",
    "oppo": "OPPO",
    "vivo": "Vivo",
    "iqoo": "iQOO",
    "motorola": "Motorola",
    "nothing": "Nothing",
    "poco": "POCO",
    "google": "Google",
    "tecno": "Tecno",
    "infinix": "Infinix",
}


def normalize_text(text):
    normalized = text or ""

    replacements = {
        "\u2013": "-",
        "\u2014": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2022": " ",
        "\u00a0": " ",
        "\ufffd": " ",
    }

    for source, target in replacements.items():
        normalized = normalized.replace(source, target)

    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def get_brand(text):
    normalized = normalize_text(text).lower()
    if not normalized:
        return UNKNOWN_BRAND

    for brand_key, brand_name in KNOWN_BRANDS.items():
        if re.search(rf"\b{re.escape(brand_key)}\b", normalized):
            return brand_name

    first = normalized.split()[0]
    return first.capitalize() if first else UNKNOWN_BRAND


def get_ram(text):
    normalized = normalize_text(text)
    patterns = [
        r"\b(\d+)\s*GB\s*RAM\b",
        r"\bRAM\s*[:\-]?\s*(\d+)\s*GB\b",
        r"\b(\d+)\s*GB\s*/\s*(128|256|512|\d+)\s*(GB|TB)\b",
        r"\b(\d+)\s*-\s*(128|256|512|\d+)\s*(GB|TB)\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, normalized, re.IGNORECASE)
        if match:
            return f"{match.group(1)}GB"

    return UNKNOWN_RAM


def get_storage(text):
    normalized = normalize_text(text)
    patterns = [
        r"\b\d+\s*GB\s*/\s*(\d+)\s*(TB|GB)\b",
        r"\b\d+\s*-\s*(\d+)\s*(TB|GB)\b",
        r"\b(64|128|256|512|1024)\s*GB\s*(?:Storage|ROM|Internal Storage)?\b",
        r"\b(1|2)\s*TB\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, normalized, re.IGNORECASE)
        if not match:
            continue

        if match.lastindex == 2:
            return f"{match.group(1)}{match.group(2).upper()}"

        value = match.group(1)
        unit = "TB" if "TB" in match.group(0).upper() else "GB"
        return f"{value}{unit}"

    return UNKNOWN_STORAGE


def get_processor(text):
    normalized = normalize_text(text)
    patterns = [
        r"\bSnapdragon\s+\d+\+?\s*(?:Gen\s*\d+)?\b",
        r"\bSnapdragon\s+[A-Z]?\d+\b",
        r"\bDimensity\s+\d{3,4}\b",
        r"\bMediaTek\s+Dimensity\s+\d{3,4}\b",
        r"\bHelio\s+[A-Z]?\d+\b",
        r"\bMediaTek\s+Helio\s+[A-Z]?\d+\b",
        r"\bTensor\s+[Gg]\d\b",
        r"\bExynos\s+\d{4}\b",
        r"\bA1[0-9]\s+Bionic\b",
        r"\bA\d+\s*Pro\b",
        r"\bBionic\s+A1[0-9]\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, normalized, re.IGNORECASE)
        if match:
            return " ".join(match.group().split())

    return UNKNOWN_PROCESSOR


def get_display_size(text):
    normalized = normalize_text(text)
    patterns = [
        r"\b(\d\.\d{1,2})\s*(?:inch|inches)\b",
        r"\b(\d\.\d{1,2})\s*\"\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, normalized, re.IGNORECASE)
        if match:
            return f'{match.group(1)}"'

    return UNKNOWN_DISPLAY_SIZE


def get_camera(text):
    normalized = normalize_text(text)
    patterns = [
        r"\b(\d{2,3})\s*MP\b",
        r"\bCamera\s*[:\-]?\s*(\d{2,3})\s*MP\b",
    ]

    matches = []
    for pattern in patterns:
        for match in re.finditer(pattern, normalized, re.IGNORECASE):
            value = f"{match.group(1)}MP"
            if value not in matches:
                matches.append(value)

    if matches:
        return "/".join(matches[:3])

    return UNKNOWN_CAMERA


def get_battery(text):
    normalized = normalize_text(text)
    match = re.search(r"\b(\d{4,5})\s*mAh\b", normalized, re.IGNORECASE)
    if match:
        return f"{match.group(1)}mAh"
    return UNKNOWN_BATTERY


def get_network(text):
    normalized = normalize_text(text).upper()
    if "5G" in normalized:
        return "5G"
    if "4G" in normalized:
        return "4G"
    return UNKNOWN_NETWORK


def extract_mobile_features(text):
    return {
        "brand": get_brand(text),
        "ram": get_ram(text),
        "storage": get_storage(text),
        "processor": get_processor(text),
        "display_size": get_display_size(text),
        "camera": get_camera(text),
        "battery": get_battery(text),
        "network": get_network(text),
    }
