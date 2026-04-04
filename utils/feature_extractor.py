import re


UNKNOWN_BRAND = "Unknown"
UNKNOWN_RAM = "Unknown"
UNKNOWN_STORAGE = "Unknown"
UNKNOWN_PROCESSOR = "Unknown"


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
    return normalized.split()[0] if normalized else UNKNOWN_BRAND


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


def extract_features(name):
    return {
        "brand": get_brand(name),
        "ram": get_ram(name),
        "storage": get_storage(name),
        "processor": get_processor(name)
    }
