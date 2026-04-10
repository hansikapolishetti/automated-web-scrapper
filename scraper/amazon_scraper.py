import sys
import os
import re
from datetime import datetime, timezone

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
from playwright.async_api import async_playwright
from database.db import collection
from utils.feature_extractor import extract_features

UNKNOWN_TEXT = "Unknown"
UNKNOWN_LINK = "Unavailable"
UNKNOWN_IMAGE = "Unavailable"
UNKNOWN_RATING = "Unknown"
SEARCH_QUERIES = [
    "laptops",
    "gaming laptop",
    "business laptop",
    "thin and light laptop",
    "asus laptop",
    "hp laptop",
    "lenovo laptop",
    "dell laptop",
    "acer laptop",
    "msi laptop",
]
BRAND_QUERY_MAP = {
    "asus laptop": "asus",
    "hp laptop": "hp",
    "lenovo laptop": "lenovo",
    "dell laptop": "dell",
    "acer laptop": "acer",
    "msi laptop": "msi",
}


def clean_price(price):
    digits = re.sub(r"[^\d]", "", price or "")
    return int(digits) if digits else None


def clean_rating(text):
    match = re.search(r"(\d+(?:\.\d+)?)", text or "")
    return float(match.group(1)) if match else UNKNOWN_RATING


def clean_review_count(text):
    digits = re.sub(r"[^\d]", "", text or "")
    return int(digits) if digits else 0


def clean_discount_percent(text):
    match = re.search(r"(\d+)\s*%", text or "")
    return int(match.group(1)) if match else 0


def sanitize_original_price(original_price, current_price):
    if not current_price:
        return current_price
    if not original_price or original_price < current_price:
        return current_price
    if original_price > current_price * 3:
        return current_price
    return original_price


def looks_like_valid_product_name(name):
    if not name:
        return False

    cleaned = name.strip()
    if len(cleaned) < 12:
        return False

    tokens = cleaned.split()
    if len(tokens) < 3:
        return False

    generic_names = {"asus", "hp", "dell", "acer", "lenovo", "msi"}
    if cleaned.lower() in generic_names:
        return False

    return True


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


async def scrape_amazon():
    seen = set()
    max_pages = 3

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(
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

                        original_price_el = await product.query_selector(
                            "span.a-price.a-text-price span.a-offscreen, span[data-a-strike='true']"
                        )
                        original_price_text = (
                            await original_price_el.inner_text() if original_price_el else None
                        )
                        original_price = sanitize_original_price(
                            clean_price(original_price_text),
                            price_value,
                        )

                        discount_el = await product.query_selector(
                            "span.a-letter-space + span, span.s-coupon-unclipped, div.a-row.a-size-small span"
                        )
                        discount_text = await discount_el.inner_text() if discount_el else None
                        discount_percent = clean_discount_percent(discount_text)

                        rating_el = await product.query_selector(
                            "span.a-icon-alt, i.a-icon-star-small span.a-icon-alt"
                        )
                        rating_text = await rating_el.inner_text() if rating_el else None
                        rating = clean_rating(rating_text)

                        review_count_el = await product.query_selector(
                            "span[aria-label$='ratings'], a[href*='#customerReviews'] span.a-size-base"
                        )
                        review_count_text = (
                            await review_count_el.inner_text() if review_count_el else None
                        )
                        review_count = clean_review_count(review_count_text)

                        link_el = await product.query_selector(
                            "h2 a, a.a-link-normal.s-no-outline, a.a-link-normal[href]"
                        )
                        link = await link_el.get_attribute("href") if link_el else None
                        full_link = build_amazon_link(link)

                        img_el = await product.query_selector("img.s-image")
                        image = await img_el.get_attribute("src") if img_el else None

                        feature_text = " ".join(
                            part for part in [name or "", card_text or "", full_link] if part
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
                            "original_price": max(original_price or 0, price_value or 0),
                            "discount_amount": max((original_price or price_value or 0) - (price_value or 0), 0),
                            "discount_percent": discount_percent,
                            "rating": rating,
                            "review_count": review_count,
                            "link": full_link,
                            "image": image or UNKNOWN_IMAGE,
                            "website": "amazon",
                            "category": "laptop",
                            "currency": "INR",
                            "source_text": feature_text or UNKNOWN_TEXT,
                            "search_query": search_query,
                            "last_seen_at": datetime.now(timezone.utc).isoformat(),
                        }

                        product_data.update(extract_features(product_data["source_text"]))

                        collection.update_one(
                            {
                                "name": product_data["name"],
                                "website": product_data["website"]
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
    asyncio.run(scrape_amazon())
