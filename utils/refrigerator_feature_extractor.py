import re


UNKNOWN_BRAND = "Unknown"
UNKNOWN_CAPACITY = "Unknown"
UNKNOWN_STAR_RATING = "Unknown"
UNKNOWN_DOOR_TYPE = "Unknown"
UNKNOWN_DEFROST_SYSTEM = "Unknown"
UNKNOWN_COMPRESSOR = "Unknown"
UNKNOWN_CONVERTIBLE = "Unknown"
UNKNOWN_COLOR = "Unknown"

KNOWN_BRANDS = {
    "samsung": "Samsung",
    "lg": "LG",
    "whirlpool": "Whirlpool",
    "godrej": "Godrej",
    "haier": "Haier",
    "panasonic": "Panasonic",
    "bosch": "Bosch",
    "siemens": "Siemens",
    "hisense": "Hisense",
    "croma": "Croma",
    "sharp": "Sharp",
    "voltas beko": "Voltas Beko",
    "beko": "Beko",
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

    for brand_key, brand_name in sorted(KNOWN_BRANDS.items(), key=lambda item: -len(item[0])):
        if re.search(rf"\b{re.escape(brand_key)}\b", normalized):
            return brand_name

    first = normalized.split()[0]
    return first.capitalize() if first else UNKNOWN_BRAND


def get_capacity(text):
    normalized = normalize_text(text)
    match = re.search(r"\b(\d{2,4})\s*L(?:iters?|itres?)?\b", normalized, re.IGNORECASE)
    if match:
        return f"{match.group(1)}L"
    return UNKNOWN_CAPACITY


def get_star_rating(text):
    normalized = normalize_text(text)
    patterns = [
        r"\b([1-5])\s*Star\b",
        r"\b([1-5])\s*Star\s+Rating\b",
        r"\b([1-5])\s*-\s*Star\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, normalized, re.IGNORECASE)
        if match:
            return f"{match.group(1)} Star"

    return UNKNOWN_STAR_RATING


def get_door_type(text):
    normalized = normalize_text(text)
    patterns = [
        r"\bSide by Side\b",
        r"\bFrench Door\b",
        r"\bDouble Door\b",
        r"\bSingle Door\b",
        r"\bMulti Door\b",
        r"\bTriple Door\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, normalized, re.IGNORECASE)
        if match:
            return " ".join(match.group(0).split()).title()

    return UNKNOWN_DOOR_TYPE


def get_defrost_system(text):
    normalized = normalize_text(text)
    patterns = [
        r"\bFrost Free\b",
        r"\bDirect Cool\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, normalized, re.IGNORECASE)
        if match:
            return " ".join(match.group(0).split()).title()

    return UNKNOWN_DEFROST_SYSTEM


def get_compressor(text):
    normalized = normalize_text(text)
    patterns = [
        r"\bInverter Compressor\b",
        r"\bDigital Inverter\b",
        r"\bNormal Compressor\b",
        r"\bReciprocating Compressor\b",
        r"\bSmart Inverter Compressor\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, normalized, re.IGNORECASE)
        if match:
            return " ".join(match.group(0).split()).title()

    return UNKNOWN_COMPRESSOR


def get_convertible(text):
    normalized = normalize_text(text).lower()
    if "convertible" in normalized:
        return "Yes"
    return UNKNOWN_CONVERTIBLE


def get_color(text):
    normalized = normalize_text(text)
    patterns = [
        r"\b(?:Steel|Silver|Blue|Black|Red|Wine|Grey|Gray|Purple|Green|White)\b(?:\s+\w+){0,2}\s+\b(?:Color|Glass|Finish)\b",
        r"\b(?:Steel|Silver|Blue|Black|Red|Wine|Grey|Gray|Purple|Green|White)\b(?:\s+\w+){0,2}\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, normalized, re.IGNORECASE)
        if match:
            value = " ".join(match.group(0).split())
            if len(value.split()) <= 4:
                return value.title()

    return UNKNOWN_COLOR


def extract_refrigerator_features(text):
    return {
        "brand": get_brand(text),
        "capacity": get_capacity(text),
        "star_rating": get_star_rating(text),
        "door_type": get_door_type(text),
        "defrost_system": get_defrost_system(text),
        "compressor": get_compressor(text),
        "convertible": get_convertible(text),
        "color": get_color(text),
    }
