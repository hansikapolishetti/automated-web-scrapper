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


def clean_price(price):
    digits = re.sub(r"[^\d]", "", price or "")
    return int(digits) if digits else None


def build_amazon_link(link):
    if not link:
        return UNKNOWN_LINK
    if link.startswith("http://") or link.startswith("https://"):
        return link
    return f"https://www.amazon.in{link}"


async def scrape_amazon():
    seen = set()
    max_pages = 5

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0.0.0 Safari/537.36"
            )
        )

        for page_num in range(1, max_pages + 1):
            print(f"\nScraping Amazon Page {page_num}...\n")

            url = f"https://www.amazon.in/s?k=laptops&page={page_num}"
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

                    if not name or not price_value or name in seen:
                        continue

                    seen.add(name)

                    product_data = {
                        "name": name,
                        "price": price_value,
                        "link": full_link,
                        "image": image or UNKNOWN_IMAGE,
                        "website": "amazon",
                        "source_text": name or UNKNOWN_TEXT
                    }

                    product_data.update(extract_features(product_data["name"]))

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
