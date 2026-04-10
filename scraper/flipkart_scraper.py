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


def extract_rating_from_card_text(text):
    patterns = [
        r"\b(\d(?:\.\d)?)\s*(?:★|star|stars)\b",
        r"\b(\d(?:\.\d)?)\b(?=\s+\d[\d,]*\s+Ratings?)",
        r"\b(\d(?:\.\d)?)\b(?=\s+\d[\d,]*\s+Reviews?)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text or "", re.IGNORECASE)
        if match:
            return float(match.group(1))
    return UNKNOWN_RATING


def extract_review_count_from_card_text(text):
    patterns = [
        r"\b([\d,]+)\s+Ratings?\b",
        r"\b([\d,]+)\s+Reviews?\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text or "", re.IGNORECASE)
        if match:
            return clean_review_count(match.group(1))
    return 0


def build_flipkart_link(link):
    if not link:
        return UNKNOWN_LINK
    if link.startswith("http://") or link.startswith("https://"):
        return link
    return f"https://www.flipkart.com{link}"


def matches_brand_query(search_query, text):
    expected_brand = BRAND_QUERY_MAP.get(search_query)
    if not expected_brand:
        return True
    normalized = (text or "").lower()
    return expected_brand in normalized


async def scrape_flipkart():
    seen = set()
    max_pages = 3

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

                for product in products:
                    try:
                        name_el = await product.query_selector("div.RG5Slk")
                        name = await name_el.inner_text() if name_el else None
                        name = name.strip() if name else None

                        text = await product.inner_text()

                        spec_els = await product.query_selector_all("li.DTBslk")
                        specs = []
                        for spec_el in spec_els:
                            spec_text = await spec_el.inner_text()
                            if spec_text:
                                specs.append(spec_text.strip())

                        price_el = await product.query_selector(
                            "div.hZ3P6w, div.Nx9bqj, div._30jeq3"
                        )
                        price_text = await price_el.inner_text() if price_el else None
                        price_match = re.search("\u20b9\\s*([\\d,]+)", text)
                        if not price_text and price_match:
                            price_text = price_match.group(0)

                        price_value = clean_price(price_text)
                        if not name or not price_value:
                            continue

                        original_price_el = await product.query_selector(
                            "div.yRaY8j, div._3I9_wc, div._1_WHN1"
                        )
                        original_price_text = (
                            await original_price_el.inner_text() if original_price_el else None
                        )
                        original_price = clean_price(original_price_text) or price_value

                        discount_el = await product.query_selector(
                            "div.UkUFwK, div._3Ay6Sb, span.UkUFwK"
                        )
                        discount_text = await discount_el.inner_text() if discount_el else None
                        discount_percent = clean_discount_percent(discount_text)

                        rating_el = await product.query_selector(
                            "div.XQDdHH, div._3LWZlK, span[id^='productRating_']"
                        )
                        rating_text = await rating_el.inner_text() if rating_el else None
                        rating = clean_rating(rating_text)
                        if rating == UNKNOWN_RATING:
                            rating = extract_rating_from_card_text(text)

                        review_count_el = await product.query_selector(
                            "span.Wphh3N, span._2_R_DZ, span[id^='productRatingCount_']"
                        )
                        review_count_text = (
                            await review_count_el.inner_text() if review_count_el else None
                        )
                        review_count = clean_review_count(review_count_text)
                        if review_count == 0:
                            review_count = extract_review_count_from_card_text(text)

                        link_el = await product.query_selector("a[href]")
                        link = await link_el.get_attribute("href") if link_el else None
                        full_link = build_flipkart_link(link)

                        img_el = await product.query_selector("img")
                        image = await img_el.get_attribute("src") if img_el else None

                        text_for_features = " ".join(
                            part for part in [name or "", text or "", *specs, full_link]
                            if part
                        ).strip()
                        unique_key = f"{name}|{full_link}"
                        if unique_key in seen or not matches_brand_query(search_query, text_for_features):
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
                            "website": "flipkart",
                            "category": "laptop",
                            "currency": "INR",
                            "source_text": text_for_features or name or UNKNOWN_TEXT,
                            "search_query": search_query,
                            "last_seen_at": datetime.now(timezone.utc).isoformat(),
                        }

                        product_data.update(extract_features(text_for_features))

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
    asyncio.run(scrape_flipkart())
