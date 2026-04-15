import sys
import os
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
from playwright.async_api import async_playwright
from database.db import get_collection
from utils.mobile_feature_extractor import extract_mobile_features

UNKNOWN_TEXT = "Unknown"
UNKNOWN_LINK = "Unavailable"
UNKNOWN_IMAGE = "Unavailable"
collection = get_collection("mobiles")

SEARCH_QUERIES = [
    "smartphones",
    "5g mobile",
    "android phone",
    "iphone",
    "samsung mobile",
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
    "samsung mobile": "samsung",
    "oneplus mobile": "oneplus",
    "vivo mobile": "vivo",
    "oppo mobile": "oppo",
    "realme mobile": "realme",
    "xiaomi mobile": "xiaomi",
    "motorola mobile": "motorola",
    "nothing phone": "nothing",
}
SPEC_FIELDS = [
    "brand",
    "ram",
    "storage",
    "processor",
    "display_size",
    "camera",
    "battery",
    "network",
]


def clean_price(price):
    digits = re.sub(r"[^\d]", "", price or "")
    return int(digits) if digits else None


def normalize_text(text):
    normalized = text or ""
    normalized = normalized.replace("\u2013", "-").replace("\u2014", "-")
    normalized = normalized.replace("\u00a0", " ")
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def looks_like_valid_product_name(name):
    if not name:
        return False

    cleaned = name.strip()
    if len(cleaned) < 8:
        return False

    tokens = cleaned.split()
    if len(tokens) < 2:
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

    if cleaned.lower() in blocked_names:
        return False

    return True


def matches_brand_query(search_query, text):
    expected_brand = BRAND_QUERY_MAP.get(search_query)

    if not expected_brand:
        return True

    normalized = (text or "").lower()

    if expected_brand == "apple":
        return "apple" in normalized or "iphone" in normalized

    return expected_brand in normalized


def build_amazon_link(link):
    if not link:
        return UNKNOWN_LINK

    if link.startswith("http://") or link.startswith("https://"):
        return link

    return f"https://www.amazon.in{link}"


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

    return "Unknown"


def extract_regex_value(text, patterns, suffix=""):
    normalized = normalize_text(text)

    for pattern in patterns:
        match = re.search(pattern, normalized, re.IGNORECASE)
        if match:
            return f"{match.group(1)}{suffix}" if suffix else " ".join(match.group(0).split())

    return "Unknown"


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

    storage = "Unknown"
    storage_patterns = [
        r"\b\d+\s*GB\s*/\s*(\d+)\s*(TB|GB)\b",
        r"\b(64|128|256|512|1024)\s*GB\s*(?:Storage|ROM|Internal Storage)?\b",
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
            r"\bSnapdragon\s+[A-Z]?\d+\b",
            r"\bMediaTek\s+Dimensity\s+\d{3,4}\b",
            r"\bDimensity\s+\d{3,4}\b",
            r"\bMediaTek\s+Helio\s+[A-Z]?\d+\b",
            r"\bHelio\s+[A-Z]?\d+\b",
            r"\bExynos\s+\d{4}\b",
            r"\bTensor\s+G\d\b",
            r"\bA1[5-9]\s*(?:Bionic|Pro)?\b",
            r"\bA\d+\s*Pro\b",
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

    network = "5G" if "5G" in normalized.upper() else "4G" if "4G" in normalized.upper() else "Unknown"

    camera_matches = re.findall(r"\b(\d{2,3})\s*MP\b", normalized, re.IGNORECASE)
    camera = "/".join(f"{value}MP" for value in camera_matches[:3]) if camera_matches else "Unknown"

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


def count_unknown_fields(product_data):
    return sum(1 for field in SPEC_FIELDS if product_data.get(field) == "Unknown")


async def collect_texts(root, selectors):
    values = []
    seen = set()

    for selector in selectors:
        elements = await root.query_selector_all(selector)
        for element in elements:
            text = normalize_text(await element.inner_text())
            if text and text not in seen:
                seen.add(text)
                values.append(text)

    return values


async def scrape_product_detail_text(detail_page, url):
    try:
        await detail_page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await detail_page.wait_for_timeout(2000)
    except Exception:
        return ""

    detail_parts = []

    detail_parts.extend(
        await collect_texts(
            detail_page,
            [
                "#feature-bullets li span.a-list-item",
                "#feature-bullets span.a-list-item",
                "table.a-normal tr",
                "#technicalSpecifications_section_1 tr",
                "#productDetails_techSpec_section_1 tr",
            ],
        )
    )

    return " ".join(detail_parts)


async def scrape_amazon_mobile():
    seen = set()
    max_pages = 3
    total_unknown_fields = 0
    total_products = 0

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        page = await browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0.0.0 Safari/537.36"
            )
        )
        detail_page = await browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0.0.0 Safari/537.36"
            )
        )

        for search_query in SEARCH_QUERIES:

            for page_num in range(1, max_pages + 1):

                print(f"\nScraping Amazon mobile query '{search_query}' page {page_num}...\n")

                url = f"https://www.amazon.in/s?k={search_query.replace(' ', '+')}&page={page_num}"

                await page.goto(url, wait_until="domcontentloaded", timeout=60000)

                await page.wait_for_selector(
                    "div[data-component-type='s-search-result']",
                    timeout=20000
                )

                await page.wait_for_timeout(3000)

                products = await page.query_selector_all(
                    "div[data-component-type='s-search-result']"
                )

                print("Products found:", len(products))
                print()

                for product in products:

                    try:
                        name_el = await product.query_selector(
                            "h2 span, h2 a span, span.a-size-medium"
                        )

                        name = await name_el.inner_text() if name_el else None
                        name = name.strip() if name else None

                        card_text = await product.inner_text()

                        price_el = await product.query_selector(
                            "span.a-price span.a-offscreen, span.a-price-whole"
                        )

                        price_text = await price_el.inner_text() if price_el else None
                        price_value = clean_price(price_text)

                        link_el = await product.query_selector(
                            "h2 a, a.a-link-normal.s-no-outline, a.a-link-normal[href]"
                        )

                        link = await link_el.get_attribute("href") if link_el else None
                        full_link = build_amazon_link(link)

                        img_el = await product.query_selector("img.s-image")
                        image = await img_el.get_attribute("src") if img_el else None

                        card_specs = await collect_texts(
                            product,
                            [
                                "div.a-row.a-size-base.a-color-secondary span",
                                "div.a-section.a-spacing-small.a-spacing-top-small li",
                                "ul.a-unordered-list.a-vertical.a-spacing-mini li",
                            ],
                        )
                        detail_text = await scrape_product_detail_text(detail_page, full_link)

                        feature_text = " ".join(
                            part for part in [
                                name or "",
                                card_text or "",
                                " ".join(card_specs),
                                detail_text,
                                full_link,
                            ] if part
                        ).strip()

                        unique_key = f"{name}|{full_link}"

                        if (
                            not looks_like_valid_product_name(name)
                            or not matches_brand_query(search_query, feature_text)
                            or not price_value
                            or unique_key in seen
                        ):
                            continue

                        seen.add(unique_key)

                        product_data = {
                            "name": name,
                            "price": price_value,
                            "link": full_link,
                            "image": image or UNKNOWN_IMAGE,
                            "website": "amazon",
                            "category": "mobiles",
                            "source_text": feature_text or UNKNOWN_TEXT,
                            "search_query": search_query,
                        }

                        product_data.update(extract_mobile_features(product_data["source_text"]))
                        product_data["unknown_field_count"] = count_unknown_fields(product_data)
                        total_unknown_fields += product_data["unknown_field_count"]
                        total_products += 1

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

        print(f"Total products scraped: {total_products}")
        print(f"Total unknown fields: {total_unknown_fields}")
        await detail_page.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(scrape_amazon_mobile())
