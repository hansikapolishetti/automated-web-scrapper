import sys
import os
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
from playwright.async_api import async_playwright
from database.db import collection
from utils.feature_extractor import extract_features

UNKNOWN_TEXT = "Unknown"
UNKNOWN_LINK = "Unavailable"
UNKNOWN_IMAGE = "Unavailable"
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

                        link_el = await product.query_selector("a[href]")
                        link = await link_el.get_attribute("href") if link_el else None
                        full_link = build_flipkart_link(link)

                        img_el = await product.query_selector("img")
                        image = await img_el.get_attribute("src") if img_el else None

                        text_for_features = " ".join(
                            part for part in [name or "", *specs, full_link]
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
                            "source_text": text_for_features or name or UNKNOWN_TEXT,
                            "search_query": search_query,
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
