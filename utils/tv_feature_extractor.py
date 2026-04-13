import re


UNKNOWN_BRAND = "Unknown"
UNKNOWN_SCREEN_SIZE = "Unknown"
UNKNOWN_RESOLUTION = "Unknown"
UNKNOWN_DISPLAY_TYPE = "Unknown"
UNKNOWN_SMART_TV = "Unknown"
UNKNOWN_REFRESH_RATE = "Unknown"
UNKNOWN_AUDIO_OUTPUT = "Unknown"
UNKNOWN_OPERATING_SYSTEM = "Unknown"

KNOWN_BRANDS = {
    "samsung": "Samsung",
    "lg": "LG",
    "sony": "Sony",
    "xiaomi": "Xiaomi",
    "redmi": "Redmi",
    "oneplus": "OnePlus",
    "tcl": "TCL",
    "hisense": "Hisense",
    "acer": "Acer",
    "vu": "Vu",
    "haier": "Haier",
    "panasonic": "Panasonic",
    "thomson": "Thomson",
    "kodak": "Kodak",
    "blaupunkt": "Blaupunkt",
    "iffalcon": "iFFALCON",
    "toshiba": "Toshiba",
    "philips": "Philips",
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


def get_screen_size(text):
    normalized = normalize_text(text)
    patterns = [
        r"\b(\d{2,3})\s*(?:cm)\b",
        r"\b(\d{2}(?:\.\d)?)\s*(?:inch|inches)\b",
        r"\b(\d{2}(?:\.\d)?)\s*\"\b",
    ]

    match = re.search(patterns[0], normalized, re.IGNORECASE)
    if match:
        size_cm = float(match.group(1))
        size_in = round(size_cm / 2.54, 1)
        if size_in.is_integer():
            return f'{int(size_in)}"'
        return f'{size_in}"'

    for pattern in patterns[1:]:
        match = re.search(pattern, normalized, re.IGNORECASE)
        if match:
            return f'{match.group(1)}"'

    return UNKNOWN_SCREEN_SIZE


def get_resolution(text):
    normalized = normalize_text(text)
    patterns = [
        r"\b8K\b",
        r"\b4K\b",
        r"\bUltra HD\b",
        r"\bUHD\b",
        r"\bFull HD\b",
        r"\bFHD\b",
        r"\bHD Ready\b",
        r"\b2K\b",
        r"\b1366\s*x\s*768\b",
        r"\b1920\s*x\s*1080\b",
        r"\b3840\s*x\s*2160\b",
        r"\b7680\s*x\s*4320\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, normalized, re.IGNORECASE)
        if not match:
            continue

        value = " ".join(match.group(0).split())
        normalized_value = value.lower()
        if normalized_value in {"ultra hd", "uhd", "3840 x 2160"}:
            return "4K"
        if normalized_value in {"full hd", "fhd", "1920 x 1080"}:
            return "Full HD"
        if normalized_value in {"hd ready", "1366 x 768"}:
            return "HD Ready"
        if normalized_value in {"7680 x 4320"}:
            return "8K"
        return value.upper() if normalized_value == "8k" else value

    return UNKNOWN_RESOLUTION


def get_display_type(text):
    normalized = normalize_text(text)
    patterns = [
        r"\bQLED\b",
        r"\bOLED\b",
        r"\bNeo QLED\b",
        r"\bMini LED\b",
        r"\bQD-Mini LED\b",
        r"\bLED\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, normalized, re.IGNORECASE)
        if match:
            value = " ".join(match.group(0).split())
            if value.lower() == "mini led":
                return "Mini LED"
            if value.lower() == "neo qled":
                return "Neo QLED"
            if value.lower() == "qd-mini led":
                return "QD-Mini LED"
            return value.upper()

    return UNKNOWN_DISPLAY_TYPE


def get_smart_tv(text):
    normalized = normalize_text(text).lower()
    if "smart tv" in normalized or "smart television" in normalized:
        return "Yes"
    if "non-smart" in normalized:
        return "No"
    if any(
        term in normalized
        for term in ["google tv", "android tv", "webos", "tizen", "vidaa", "fire tv"]
    ):
        return "Yes"
    return UNKNOWN_SMART_TV


def get_refresh_rate(text):
    normalized = normalize_text(text)
    match = re.search(r"\b(\d{2,3})\s*Hz\b", normalized, re.IGNORECASE)
    if match:
        return f"{match.group(1)}Hz"
    return UNKNOWN_REFRESH_RATE


def get_audio_output(text):
    normalized = normalize_text(text)
    match = re.search(r"\b(\d{1,3})\s*W(?:att|atts)?\b", normalized, re.IGNORECASE)
    if match:
        return f"{match.group(1)}W"
    return UNKNOWN_AUDIO_OUTPUT


def get_operating_system(text):
    normalized = normalize_text(text)
    patterns = [
        r"\bGoogle TV\b",
        r"\bAndroid TV\b",
        r"\bTizen\b",
        r"\bwebOS\b",
        r"\bVIDAA\b",
        r"\bFire TV\b",
        r"\bCoolita\b",
        r"\bLinux\b",
        r"\bPatchWall\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, normalized, re.IGNORECASE)
        if match:
            return " ".join(match.group(0).split())

    return UNKNOWN_OPERATING_SYSTEM


def extract_tv_features(text):
    return {
        "brand": get_brand(text),
        "screen_size": get_screen_size(text),
        "resolution": get_resolution(text),
        "display_type": get_display_type(text),
        "smart_tv": get_smart_tv(text),
        "refresh_rate": get_refresh_rate(text),
        "audio_output": get_audio_output(text),
        "operating_system": get_operating_system(text),
    }
