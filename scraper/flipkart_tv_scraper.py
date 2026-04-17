import sys
import os
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
from playwright.async_api import async_playwright
from utils.tv_feature_extractor import extract_tv_features

try:
    from pymongo.errors import PyMongoError
    from database.db import get_collection
except Exception:
    PyMongoError = Exception
    collection = None
else:
    collection = get_collection("tvs")

UNKNOWN_TEXT = "Unknown"
UNKNOWN_LINK = "Unavailable"
UNKNOWN_IMAGE = "Unavailable"
SPEC_FIELDS = [
    "brand",
    "screen_size",
    "resolution",
    "display_type",
    "smart_tv",
    "refresh_rate",
    "audio_output",
    "operating_system",
]
SEARCH_QUERIES = [
    "television",
    "smart tv",
    "android tv",
    "4k tv",
    "led tv",
    "samsung tv",
    "lg tv",
    "sony tv",
    "xiaomi tv",
    "oneplus tv",
    "tcl tv",
]
BRAND_QUERY_MAP = {
    "samsung tv": "samsung",
    "lg tv": "lg",
    "sony tv": "sony",
    "xiaomi tv": "xiaomi",
    "oneplus tv": "oneplus",
    "tcl tv": "tcl",
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
    if len(cleaned) < 12:
        return False

    if len(cleaned.split()) < 3:
        return False

    generic_names = {"tv", "television", "smart tv", "led tv"}
    return cleaned.lower() not in generic_names


def looks_like_tv_result(text):
    normalized = (text or "").lower()
    required_terms = [
        "tv",
        "television",
        "smart tv",
        "google tv",
        "android tv",
        "led tv",
        "qled",
        "oled",
    ]
    return any(term in normalized for term in required_terms)


def matches_brand_query(search_query, text):
    expected_brand = BRAND_QUERY_MAP.get(search_query)
    if not expected_brand:
        return True
    normalized = (text or "").lower()
    return expected_brand in normalized


def can_write_to_database():
    if collection is None:
        print("MongoDB support not available. Continuing without saving data.")
        return False

    try:
        collection.database.client.admin.command("ping")
        return True
    except PyMongoError as error:
        print(f"MongoDB not reachable. Continuing without saving data. Reason: {error}")
        return False


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


async def scrape_flipkart_tv():
    seen = set()
    max_pages = 3
    db_available = can_write_to_database()
    total_products = 0
    total_unknown_fields = 0

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        for search_query in SEARCH_QUERIES:
            for page_num in range(1, max_pages + 1):
                print(f"\nScraping Flipkart query '{search_query}' page {page_num}...\n")

                url = f"https://www.flipkart.com/search?q={search_query.replace(' ', '+')}&page={page_num}"
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)

                await page.keyboard.press("Escape")
                await page.wait_for_selector("div[data-id]", timeout=20000)
                await page.wait_for_timeout(2000)

                products = await page.query_selector_all("div[data-id]")
                print("Products found:", len(products))
                print()

                for product in products:
                    try:
                        name_el = await product.query_selector("div.KzDlHZ, div.RG5Slk")
                        name = await name_el.inner_text() if name_el else None
                        name = normalize_text(name)

                        text = normalize_text(await product.inner_text())

                        spec_texts = await collect_texts(
                            product,
                            [
                                "li.G4BRas",
                                "li.DTBslk",
                                "div._6NESgJ",
                                "div._6jtvI4",
                            ],
                        )

                        price_el = await product.query_selector(
                            "div.hZ3P6w, div.Nx9bqj, div._30jeq3"
                        )
                        price_text = await price_el.inner_text() if price_el else None
                        price_match = re.search(r"\u20b9\s*([\d,]+)", text)
                        if not price_text and price_match:
                            price_text = price_match.group(0)

                        price_value = clean_price(price_text)
                        if not looks_like_valid_product_name(name) or not price_value:
                            continue

                        link_el = await product.query_selector("a[href]")
                        link = await link_el.get_attribute("href") if link_el else None
                        full_link = build_flipkart_link(link)

                        img_el = await product.query_selector("img")
                        image = await img_el.get_attribute("src") if img_el else None

                        feature_text = " ".join(
                            part
                            for part in [name or "", text or "", " ".join(spec_texts), full_link]
                            if part
                        ).strip()
                        unique_key = f"{name}|{full_link}"

                        if (
                            unique_key in seen
                            or not looks_like_tv_result(feature_text)
                            or not matches_brand_query(search_query, feature_text)
                        ):
                            continue

                        seen.add(unique_key)

                        product_data = {
                            "name": name,
                            "price": price_value,
                            "link": full_link,
                            "image": image or UNKNOWN_IMAGE,
                            "website": "flipkart",
                            "category": "tvs",
                            "source_text": feature_text or name or UNKNOWN_TEXT,
                            "search_query": search_query,
                        }

                        product_data.update(extract_tv_features(product_data["source_text"]))
                        product_data["unknown_field_count"] = count_unknown_fields(product_data)
                        total_unknown_fields += product_data["unknown_field_count"]
                        total_products += 1

                        if db_available:
                            collection.update_one(
                                {
                                    "name": product_data["name"],
                                    "website": product_data["website"],
                                    "category": product_data["category"],
                                },
                                {"$set": product_data},
                                upsert=True
                            )

                        print(product_data)
                        print("------")

                    except Exception as e:
                        print("Error:", e)

        print(f"Total TVs scraped: {total_products}")
        print(f"Total unknown fields: {total_unknown_fields}")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(scrape_flipkart_tv())
