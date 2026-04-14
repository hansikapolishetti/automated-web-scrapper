import sys
import os
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
from playwright.async_api import async_playwright
from utils.refrigerator_feature_extractor import extract_refrigerator_features

try:
    from pymongo.errors import PyMongoError
    from database.db import collection
except Exception:
    PyMongoError = Exception
    collection = None

UNKNOWN_TEXT = "Unknown"
UNKNOWN_LINK = "Unavailable"
UNKNOWN_IMAGE = "Unavailable"
SPEC_FIELDS = [
    "brand",
    "capacity",
    "star_rating",
    "door_type",
    "defrost_system",
    "compressor",
    "convertible",
    "color",
]
SEARCH_QUERIES = [
    "refrigerator",
    "fridge",
    "mini fridge",
    "double door refrigerator",
    "single door refrigerator",
    "bottom freezer refrigerator",
    "top freezer refrigerator",
    "convertible refrigerator",
    "frost free refrigerator",
    "samsung refrigerator",
    "lg refrigerator",
    "whirlpool refrigerator",
    "godrej refrigerator",
    "haier refrigerator",
]
BRAND_QUERY_MAP = {
    "samsung refrigerator": "samsung",
    "lg refrigerator": "lg",
    "whirlpool refrigerator": "whirlpool",
    "godrej refrigerator": "godrej",
    "haier refrigerator": "haier",
}


def clean_price(price):
    digits = re.sub(r"[^\d]", "", price or "")
    return int(digits) if digits else None


def looks_like_valid_product_name(name):
    if not name:
        return False

    cleaned = name.strip()
    if len(cleaned) < 12:
        return False

    if len(cleaned.split()) < 3:
        return False

    generic_names = {"fridge", "refrigerator", "double door refrigerator", "single door refrigerator"}
    return cleaned.lower() not in generic_names


def looks_like_refrigerator_result(text):
    normalized = (text or "").lower()
    required_terms = [
        "refrigerator",
        "fridge",
        "mini fridge",
        "frost free",
        "direct cool",
        "single door",
        "double door",
        "side by side",
        "bottom freezer",
        "top freezer",
        "convertible refrigerator",
        "convertible fridge",
    ]
    return any(term in normalized for term in required_terms)


def matches_brand_query(search_query, text):
    expected_brand = BRAND_QUERY_MAP.get(search_query)
    if not expected_brand:
        return True
    normalized = (text or "").lower()
    return expected_brand in normalized


def build_amazon_link(link):
    if not link:
        return UNKNOWN_LINK
    if link.startswith("http://") or link.startswith("https://"):
        return link
    return f"https://www.amazon.in{link}"


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
            text = " ".join((await element.inner_text()).split())
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


async def scrape_amazon_refrigerator():
    seen = set()
    max_pages = 3
    db_available = can_write_to_database()
    total_products = 0
    total_unknown_fields = 0

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
                print(f"\nScraping Amazon query '{search_query}' page {page_num}...\n")

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
                            part
                            for part in [
                                name or "",
                                card_text or "",
                                " ".join(card_specs),
                                detail_text,
                                full_link,
                            ]
                            if part
                        ).strip()
                        unique_key = f"{name}|{full_link}"
                        if (
                            not looks_like_valid_product_name(name)
                            or not looks_like_refrigerator_result(feature_text)
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
                            "category": "refrigerator",
                            "source_text": feature_text or UNKNOWN_TEXT,
                            "search_query": search_query,
                        }

                        product_data.update(extract_refrigerator_features(product_data["source_text"]))
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

        print(f"Total refrigerators scraped: {total_products}")
        print(f"Total unknown fields: {total_unknown_fields}")
        await detail_page.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(scrape_amazon_refrigerator())
