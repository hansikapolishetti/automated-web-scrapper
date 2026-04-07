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
        r'(\d{2}(?:\.\d)?)\s*(?:"|\'\'|inch|inches)\b',
        r'(\d{2}(?:\.\d)?)\s*/\s*\d{2,3}\s*Hz\b',
        r'(\d{2}(?:\.\d)?)\b(?=\s*,\s*\d{2,3}\s*Hz)',
        r'(\d{2}(?:\.\d)?)\s*(?:cm)\b',
    ]

    match = re.search(patterns[0], normalized, re.IGNORECASE)
    if match:
        return f'{match.group(1)}"'

    match = re.search(patterns[1], normalized, re.IGNORECASE)
    if match:
        return f'{match.group(1)}"'

    match = re.search(patterns[2], normalized, re.IGNORECASE)
    if match:
        return f'{match.group(1)}"'

    match = re.search(patterns[3], normalized, re.IGNORECASE)
    if match:
        size_cm = float(match.group(1))
        size_in = round(size_cm / 2.54, 1)
        if size_in.is_integer():
            return f'{int(size_in)}"'
        return f'{size_in}"'

    return UNKNOWN_SCREEN_SIZE


def get_gpu(name):
    normalized = normalize_text(name)

    patterns = [
        r'\bNVIDIA\s+GeForce\s+RTX\s?\d{3,4}\b',
        r'\bNVIDIA\s+GeForce\s+GTX\s?\d{3,4}\b',
        r'\bRTX\s?\d{3,4}\b',
        r'\bGTX\s?\d{3,4}\b',
        r'\bMX\s?\d{2,3}\b',
        r'\bArc\s+[A-Z]\d+\b',
        r'\bIntel\s+Arc\b',
        r'\bIntel\s+Iris\s+Xe\b',
        r'\bIris\s+Xe\b',
        r'\bIntel\s+UHD(?:\s+Graphics)?\b',
        r'\bUHD\s+Graphics\b',
        r'\bIntel\s+iGPU\b',
        r'\biGPU\b',
        r'\bAMD\s+Radeon\s+\d+[A-Z]*M?\b',
        r'\bAMD\s+Radeon\b',
        r'\bAMD\s+Radeon\s+iGPU\b',
        r'\bRadeon\s+\d+[A-Z]*M?\b',
        r'\bRadeon\s+Graphics\b',
    ]

    for pattern in patterns:
        match = re.search(pattern, normalized, re.IGNORECASE)
        if match:
            return " ".join(match.group().split())

    return UNKNOWN_GPU


def get_model_code(name):
    normalized = normalize_text(name)

    priority_patterns = [
        r'\b[A-Z]{1,4}\d{2,6}[A-Z]{0,4}-[A-Z0-9]{2,}\b',
        r'\b[A-Z]{2,}\d{2,}[A-Z0-9]*-[A-Z0-9]{2,}\b',
        r'\b[a-z]{2}\d{4}[a-z]{2}\b',
    ]

    for pattern in priority_patterns:
        matches = re.findall(pattern, normalized, re.IGNORECASE)
        for match in matches:
            candidate = match.upper().strip(" ,.)(")
            if len(candidate) <= 32 and "ITM" not in candidate:
                return candidate

    candidates = re.findall(r'\b[A-Z0-9][A-Z0-9-]{4,}\b', normalized.upper())
    filtered = []
    for candidate in candidates:
        if len(candidate) > 32:
            continue
        if "-" not in candidate and len(candidate) > 16:
            continue
        if candidate.count("-") > 2:
            continue
        if not any(char.isdigit() for char in candidate):
            continue
        if not any(char.isalpha() for char in candidate):
            continue
        if re.fullmatch(r'[A-Z]{6,}\d{8,}', candidate):
            continue
        if any(stopword in candidate for stopword in MODEL_CODE_STOPWORDS):
            continue
        filtered.append(candidate.strip(" ,.)("))

    filtered.sort(key=lambda value: (value.count("-") == 0, -len(value)))
    if filtered:
        return filtered[0]

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
