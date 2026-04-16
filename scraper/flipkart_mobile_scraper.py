import sys
import os
import re
from datetime import datetime, timezone

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
from playwright.async_api import async_playwright
from database.db import get_collection

UNKNOWN_TEXT = "Unknown"
UNKNOWN_LINK = "Unavailable"
UNKNOWN_IMAGE = "Unavailable"
UNKNOWN_VALUE = "Unknown"
PRODUCT_CATEGORY = "mobile"

SEARCH_QUERIES = [
    "smartphones",
    "5g mobile",
    "android phone",
    "iphone",
    "apple iphone",
    "iphone 16",
    "iphone 15",
    "iphone pro",
    "samsung mobile",
    "samsung galaxy phone",
    "oneplus mobile",
    "vivo mobile",
    "oppo mobile",
    "realme mobile",
    "xiaomi mobile",
    "motorola mobile",
    "nothing phone",
]

BRAND_QUERY_MAP = {
    "iphone": "apple",
    "apple iphone": "apple",
    "iphone 16": "apple",
    "iphone 15": "apple",
    "iphone pro": "apple",
    "samsung mobile": "samsung",
    "samsung galaxy phone": "samsung",
    "oneplus mobile": "oneplus",
    "vivo mobile": "vivo",
    "oppo mobile": "oppo",
    "realme mobile": "realme",
    "xiaomi mobile": "xiaomi",
    "motorola mobile": "motorola",
    "nothing phone": "nothing",
}


def clean_price(price):
    digits = re.sub(r"[^\d]", "", price or "")
    return int(digits) if digits else None


def normalize_text(text):
    normalized = text or ""
    replacements = {
        "\u2013": "-",
        "\u2014": "-",
        "\u00a0": " ",
    }

    for source, target in replacements.items():
        normalized = normalized.replace(source, target)

    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def build_flipkart_link(link):
    if not link:
        return UNKNOWN_LINK
    if link.startswith("http://") or link.startswith("https://"):
        return link
    return f"https://www.flipkart.com{link}"


def looks_like_valid_product_name(name):
    if not name:
        return False

    cleaned = name.strip()

    if len(cleaned) < 8:
        return False

    if len(cleaned.split()) < 2:
        return False

    blocked_names = {
        "samsung",
        "apple",
        "oneplus",
        "vivo",
        "oppo",
        "realme",
        "xiaomi",
        "motorola",
        "nothing",
        "iphone",
    }

    return cleaned.lower() not in blocked_names


def matches_brand_query(search_query, text):
    expected_brand = BRAND_QUERY_MAP.get(search_query)

    if not expected_brand:
        return True

    normalized = (text or "").lower()

    if expected_brand == "apple":
        return "apple" in normalized or "iphone" in normalized

    return expected_brand in normalized


def get_brand(text):
    normalized = normalize_text(text).lower()

    known_brands = {
        "apple": "Apple",
        "iphone": "Apple",
        "samsung": "Samsung",
        "oneplus": "OnePlus",
        "vivo": "Vivo",
        "oppo": "OPPO",
        "realme": "Realme",
        "xiaomi": "Xiaomi",
        "redmi": "Redmi",
        "motorola": "Motorola",
        "nothing": "Nothing",
        "iqoo": "iQOO",
        "poco": "POCO",
        "google": "Google",
    }

    for brand_key, brand_name in known_brands.items():
        if re.search(rf"\b{re.escape(brand_key)}\b", normalized):
            return brand_name

    return UNKNOWN_VALUE


def extract_regex_value(text, patterns, suffix=""):
    normalized = normalize_text(text)

    for pattern in patterns:
        match = re.search(pattern, normalized, re.IGNORECASE)
        if match:
            return f"{match.group(1)}{suffix}" if suffix else " ".join(match.group(0).split())

    return UNKNOWN_VALUE


def extract_mobile_specs(text):
    normalized = normalize_text(text)

    ram = extract_regex_value(
        normalized,
        [
            r"\b(\d+)\s*GB\s*(?:RAM|LPDDR\dX?|Memory)\b",
            r"\bRAM\s*[:\-]?\s*(\d+)\s*GB\b",
            r"\b(\d+)\s*GB\s*/\s*(64|128|256|512|1024)\s*(?:GB|TB)\b",
        ],
        "GB",
    )

    storage = UNKNOWN_VALUE
    storage_patterns = [
        r"\b\d+\s*GB\s*/\s*(\d+)\s*(TB|GB)\b",
        r"\b(64|128|256|512|1024)\s*GB\b",
        r"\b(1|2)\s*TB\b",
    ]

    for pattern in storage_patterns:
        match = re.search(pattern, normalized, re.IGNORECASE)

        if match:
            if match.lastindex == 2:
                storage = f"{match.group(1)}{match.group(2).upper()}"
            else:
                unit = "TB" if "TB" in match.group(0).upper() else "GB"
                storage = f"{match.group(1)}{unit}"
            break

    processor = extract_regex_value(
        normalized,
        [
            r"\bSnapdragon\s+\d+\+?\s*(?:Elite|Gen\s*\d+)?\b",
            r"\bMediaTek\s+Dimensity\s+\d{3,4}\b",
            r"\bDimensity\s+\d{3,4}\b",
            r"\bExynos\s+\d{4}\b",
            r"\bTensor\s+G\d\b",
            r"\bA1[5-9]\s*(?:Bionic|Pro)?\b",
        ],
    )

    display_size = extract_regex_value(
        normalized,
        [
            r"\b(\d\.\d{1,2})\s*(?:inch|inches)\b",
            r"\b(\d\.\d{1,2})\s*\"\b",
        ],
        "\"",
    )

    battery = extract_regex_value(
        normalized,
        [r"\b(\d{4,5})\s*mAh\b"],
        "mAh",
    )

    network = "5G" if "5G" in normalized.upper() else "4G" if "4G" in normalized.upper() else UNKNOWN_VALUE

    camera_matches = re.findall(r"\b(\d{2,3})\s*MP\b", normalized, re.IGNORECASE)

    camera = "/".join(f"{value}MP" for value in camera_matches[:3]) if camera_matches else UNKNOWN_VALUE

    return {
        "brand": get_brand(normalized),
        "ram": ram,
        "storage": storage,
        "processor": processor,
        "display_size": display_size,
        "camera": camera,
        "battery": battery,
        "network": network,
    }


async def scrape_flipkart_mobile():

    seen = set()
    max_pages = 5
    collection = get_collection(PRODUCT_CATEGORY)

    async with async_playwright() as p:

        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        for search_query in SEARCH_QUERIES:

            for page_num in range(1, max_pages + 1):

                print(f"\nScraping Flipkart mobile query '{search_query}' page {page_num}...\n")

                url = f"https://www.flipkart.com/search?q={search_query.replace(' ', '+')}&page={page_num}"

                await page.goto(url, wait_until="domcontentloaded", timeout=60000)

                await page.keyboard.press("Escape")

                await page.wait_for_selector("div[data-id]", timeout=20000)

                await page.wait_for_timeout(2000)

                products = await page.query_selector_all("div[data-id]")

                print("Products found:", len(products))

                for product in products:

                    try:

                        name_el = await product.query_selector("div.KzDlHZ, div.RG5Slk")

                        name = await name_el.inner_text() if name_el else None
                        name = normalize_text(name)

                        text = normalize_text(await product.inner_text())

                        price_match = re.search(r"\u20b9\s*([\d,]+)", text)

                        price_text = price_match.group(0) if price_match else None

                        price_value = clean_price(price_text)

                        if not looks_like_valid_product_name(name) or not price_value:
                            continue

                        link_el = await product.query_selector("a[href]")

                        link = await link_el.get_attribute("href") if link_el else None

                        full_link = build_flipkart_link(link)

                        img_el = await product.query_selector("img")

                        image = await img_el.get_attribute("src") if img_el else None

                        text_for_features = " ".join(
                            part for part in [name or "", text or "", full_link]
                            if part
                        ).strip()

                        unique_key = f"{name}|{full_link}"

                        if unique_key in seen or not matches_brand_query(search_query, text_for_features):
                            continue

                        seen.add(unique_key)

                        product_data = {
                            "name": name,
                            "price": price_value,
                            "link": full_link,
                            "image": image or UNKNOWN_IMAGE,
                            "website": "flipkart",
                            "category": PRODUCT_CATEGORY,
                            "currency": "INR",
                            "source_text": text_for_features or name or UNKNOWN_TEXT,
                            "search_query": search_query,
                            "last_seen_at": datetime.now(timezone.utc).isoformat(),
                        }

                        product_data.update(extract_mobile_specs(text_for_features))

                        collection.update_one(
                            {
                                "name": product_data["name"],
                                "website": product_data["website"],
                            },
                            {"$set": product_data},
                            upsert=True
                        )

                        print(product_data)
                        print("------")

                    except Exception as e:

                        print("Error:", e)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(scrape_flipkart_mobile())
