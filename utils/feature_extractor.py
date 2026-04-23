import re


UNKNOWN_BRAND = "Unknown"
UNKNOWN_RAM = "Unknown"
UNKNOWN_STORAGE = "Unknown"
UNKNOWN_PROCESSOR = "Unknown"
UNKNOWN_SCREEN_SIZE = "Unknown"
UNKNOWN_GPU = "Unknown"
UNKNOWN_MODEL_CODE = "Unknown"
KNOWN_BRANDS = {
    "asus": "ASUS",
    "acer": "Acer",
    "hp": "HP",
    "lenovo": "Lenovo",
    "dell": "Dell",
    "msi": "MSI",
    "samsung": "Samsung",
    "primebook": "Primebook",
}
MODEL_CODE_STOPWORDS = {
    "WINDOWS",
    "LAPTOP",
    "BACKLIT",
    "KEYBOARD",
    "OFFICE",
    "BASIC",
    "THIN",
    "LIGHT",
    "HOME",
    "INTEL",
    "AMD",
    "RYZEN",
    "CORE",
    "GEN",
    "SSD",
    "YEAR",
}
MODEL_CODE_BLACKLIST = {
    "ITM",
    "COM",
    "COMH",
    "LPDDR5X",
    "LPDDR5",
    "LPDDR4X",
    "LPDDR4",
    "DDR5",
    "DDR4",
    "SSD",
    "HDD",
    "EMMC",
    "UFS",
    "NVME",
    "PCIE",
    "WIN11",
    "WINDOWS11",
    "M365",
    "M365-BASIC",
    "OFFICE2024",
    "OFFICE2021",
    "N4020",
    "N4500",
    "N100",
    "N95",
    "N97",
    "100U",
    "120U",
    "1305U",
    "1315U",
    "1335U",
    "7435HS",
    "7730U",
    "8840H",
    "8840HS",
    "7320U",
}


def normalize_text(name):
    normalized = name or ""

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
        "®": "",
        "™": "",
        "InteI": "Intel",
        "AINow": "AI Now",
        "NVME": "NVMe",
    }

    for source, target in replacements.items():
        normalized = normalized.replace(source, target)

    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def get_brand(name):
    normalized = normalize_text(name)
    if not normalized:
        return UNKNOWN_BRAND
    first = normalized.split()[0]
    return KNOWN_BRANDS.get(first.lower(), first)


def get_ram(name):
    normalized = normalize_text(name)

    patterns = [
        r'(\d+)[\s-]?GB\s*(?:DDR\d|LPDDR\d|RAM|Memory)',
        r'(?:RAM|Memory)\s*[:\-]?\s*(\d+)[\s-]?GB',
        r'[\(\[]\s*(\d+)[\s-]?GB\s*/',
        r'\b(\d+)[\s-]?GB\s*/\s*(?:128|256|512|\d+)\s?(?:TB|GB)\b',
        r'\b(\d+)[\s-]?gb-(?:128|256|512|\d+)-(?:tb|gb)\b',
        r'\b(\d+)[\s-]?GB\b(?!\s*(?:SSD|HDD|eMMC|UFS|Storage|ROM))'
    ]

    for pattern in patterns:
        match = re.search(pattern, normalized, re.IGNORECASE)
        if match:
            return match.group(1) + "GB"

    return UNKNOWN_RAM


def get_storage(name):
    normalized = normalize_text(name)

    patterns = [
        r'\b\d+[\s-]?GB\s*/\s*(\d+)\s?(TB|GB)\b',
        r'\b\d+[\s-]?GB\s*,\s*(\d+)\s?(TB|GB)\b',
        r'\b\d+[\s-]?gb-(\d+)-(tb|gb)\b',
        r'(\d+)[\s-]?TB\s*(?:SSD|HDD|NVMe|PCIe|eMMC|UFS)',
        r'(\d+)[\s-]?GB\s*(?:SSD|HDD|NVMe|PCIe|eMMC|UFS)',
        r'\b(128|256|512)\s+SSD\b',
        r'(?:SSD|HDD|NVMe|PCIe|eMMC|UFS)\s*[:\-]?\s*(\d+)[\s-]?(TB|GB)',
        r'/\s*(\d+)\s?(TB|GB)\s*(?:SSD|HDD|NVMe|PCIe|eMMC|UFS)?',
        r'\b(\d+)\s?(TB|GB)\s+Storage\b'
    ]

    for pattern in patterns:
        match = re.search(pattern, normalized, re.IGNORECASE)
        if match:
            if len(match.groups()) == 2 and match.lastindex == 2:
                value, unit = match.group(1), match.group(2).upper()
                return f"{value}{unit}"

            unit_match = re.search(r'(TB|GB)', match.group(), re.IGNORECASE)
            unit = unit_match.group(1).upper() if unit_match else "GB"
            return f"{match.group(1)}{unit}"

    return UNKNOWN_STORAGE


def get_processor(name):
    normalized = normalize_text(name)

    patterns = [
        r'\bIntel\s+Core\s+Ultra\s+\d+\s+\d+[A-Z]*\b',
        r'\bCore\s+Ultra\s+\d+\s+\d+[A-Z]*\b',
        r'\bIntel\s+Core\s+Ultra\s+\d+\b',
        r'\bCore\s+Ultra\s+\d+\b',
        r'\bIntel\s+Core\s+i[3579]\s+\d{1,2}(?:th|nd|rd|st)\s+Gen\s+\d+[A-Z]*\b',
        r'\bIntel\s+Core\s+i[3579][\-\s]?\d{3,5}[A-Z]*\b',
        r'\bIntel\s+Core\s+i[3579]\s+\d+[A-Z]*\b',
        r'\bIntel\s+Core\s+i[3579]\s+\d{1,2}(?:th|nd|rd|st)\s+Gen\b',
        r'\bIntel\s+Core\s+i[3579]\b',
        r'\bCore\s+i[3579]\s+\d{1,2}(?:th|nd|rd|st)\s+Gen\s+\d+[A-Z]*\b',
        r'\bCore\s+i[3579][\-\s]?\d{3,5}[A-Z]*\b',
        r'\bCore\s+i[3579]\s+\d+[A-Z]*\b',
        r'\bCore\s+i[3579]\s+\d{1,2}(?:th|nd|rd|st)\s+Gen\b',
        r'\bi[3579][\-\s]?\d{3,5}[A-Z]*\b',
        r'\bIntel\s+Core\s+\d+\s+\d+[A-Z]*\b',
        r'\bIntel\s+Core\s+\d+\b',
        r'\bRyzen\s+AI\s+\d+\s+(?:Quad|Hexa|Octa)\s+Core\s+\d+[A-Z]*\b',
        r'\bRyzen\s+AI\s+Now\s+\d+\s+\d+[A-Z]*\b',
        r'\bRyzen\s+AI\s+\d+\s+\d+[A-Z]*\b',
        r'\bRyzen\s+AI\s+\d+\b',
        r'\bRyzen\s+\d+\s+(?:Quad|Hexa|Octa)\s+Core\s+\d+[A-Z]*\b',
        r'\bRyzen\s+\d+\s+(?:Quad|Hexa|Octa)\s+Core\b',
        r'\bRyzen\s+\d+\s+\d+[A-Z]*\b',
        r'\bRyzen\s+\d+\b',
        r'\bXeon\s+[A-Z]?\d[\-\dA-Z]*\s*v\d+\b',
        r'\bXeon\s+[A-Z]?\d[\-\dA-Z]*\b',
        r'\bAthlon(?:\s+Silver|\s+Gold)?(?:\s+\d+[A-Z]*)?\b',
        r'\bCeleron(?:\s+(?:Dual|Quad)\s+Core)?(?:\s+[A-Z]?\d+[A-Z]*)?\b',
        r'\bIntel\s+N\d{2,4}\b',
        r'\bN\d{2,4}\s+Processor\b',
        r'\bPentium(?:\s+(?:Dual|Quad)\s+Core)?(?:\s+[A-Z]?\d+[A-Z]*)?\b',
        r'\bMediaTek\s+Helio\s+\w+\b',
        r'\bMediaTek\s+Kompanio\s+\d+\b',
        r'\bSnapdragon\s+X\s+\w+\b',
        r'\bSnapdragon\s+X\b',
        r'\bSnapdragon\s+[A-Z]?\w*\b',
        r'\bM[1234](?:\s+(?:Pro|Max|Ultra))?\b'
    ]

    for pattern in patterns:
        match = re.search(pattern, normalized, re.IGNORECASE)
        if match:
            return " ".join(match.group().split())

    return UNKNOWN_PROCESSOR


def get_screen_size(name):
    normalized = normalize_text(name)

    patterns = [
        r'(\d{1,2}(?:\.\d)?)\s*(?:"|\'\'|inch|inches)',
        r'(\d{1,2}(?:\.\d)?)\s*/\s*\d{2,3}\s*Hz\b',
        r'(\d{1,2}(?:\.\d)?)\b(?=\s*,\s*\d{2,3}\s*Hz)',
        r'(\d{1,2}(?:\.\d)?)\s*(?:cm)\b',
    ]

    match = re.search(patterns[0], normalized, re.IGNORECASE)
    if match:
        size = float(match.group(1))
        if 10 <= size <= 18:
            return f'{match.group(1)}"'

    match = re.search(patterns[1], normalized, re.IGNORECASE)
    if match:
        size = float(match.group(1))
        if 10 <= size <= 18:
            return f'{match.group(1)}"'

    match = re.search(patterns[2], normalized, re.IGNORECASE)
    if match:
        size = float(match.group(1))
        if 10 <= size <= 18:
            return f'{match.group(1)}"'

    match = re.search(patterns[3], normalized, re.IGNORECASE)
    if match:
        size_cm = float(match.group(1))
        if size_cm < 25 or size_cm > 50:
            return UNKNOWN_SCREEN_SIZE
        size_in = round(size_cm / 2.54, 1)
        if size_in.is_integer():
            return f'{int(size_in)}"'
        return f'{size_in}"'

    return UNKNOWN_SCREEN_SIZE


def get_gpu(name):
    normalized = normalize_text(name).lower()

    if "rtx" in normalized:
        return "RTX"
    if "gtx" in normalized:
        return "GTX"
    if "radeon" in normalized:
        return "AMD Radeon"
    if "iris xe" in normalized:
        return "Intel Iris Xe"

    return "Unknown"


SERIES_KEYWORDS = [
    "v14", "e14", "ideapad", "thinkpad", "vivobook",
    "inspiron", "pavilion", "victus", "loq"
]


def is_valid_model_code(code):
    if not code:
        return False

    code = code.strip()

    # Must contain both letters and digits
    has_letter = any(c.isalpha() for c in code)
    has_digit = any(c.isdigit() for c in code)

    if not (has_letter and has_digit):
        return False

    # Reject known series names explicitly
    if code.lower() in SERIES_KEYWORDS:
        return False

    # Reject very short generic codes (like "i3", "i5")
    if len(code) <= 3:
        return False

    upper_code = code.upper()
    if upper_code in MODEL_CODE_BLACKLIST:
        return False
        
    if upper_code.startswith("ITM") or upper_code.startswith("COM"):
        return False

    return True

def get_model_code(name):
    tokens = name.split()

    for token in tokens:
        cleaned = token.strip(",()")

        if is_valid_model_code(cleaned):
            return cleaned.upper()

    return UNKNOWN_MODEL_CODE


def extract_features(name):
    return {
        "brand": get_brand(name),
        "ram": get_ram(name),
        "storage": get_storage(name),
        "processor": get_processor(name),
        "screen_size": get_screen_size(name),
        "gpu": get_gpu(name),
        "model_code": get_model_code(name),
    }


def get_rating(text):
    normalized = normalize_text(text)
    patterns = [
        r'(\d(?:\.\d)?)\s*out of 5',
        r'(\d(?:\.\d)?)\s*/\s*5',
        r'\b(\d(?:\.\d)?)\b(?=\s*(?:star|stars))',
    ]
    for pattern in patterns:
        match = re.search(pattern, normalized, re.IGNORECASE)
        if match:
            value = float(match.group(1))
            if 0 <= value <= 5:
                return value
    return "Unknown"
