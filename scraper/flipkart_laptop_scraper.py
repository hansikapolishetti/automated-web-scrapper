import sys
import os
import re
import json
from datetime import datetime, timezone

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
from playwright.async_api import async_playwright
from database.db import collection
from utils.feature_extractor import extract_features
from utils.slug_util import generate_slug

UNKNOWN_TEXT = "Unknown"
UNKNOWN_LINK = "Unavailable"
UNKNOWN_IMAGE = "Unavailable"
UNKNOWN_RATING = "Unknown"
SEARCH_QUERIES = [
    "i3 laptop",
    "i5 laptop",
    "i7 laptop",
    "ryzen laptop",
    "gaming laptop rtx",
    "16gb ram laptop",
    "512gb ssd laptop",
    "budget laptop",
    "student laptop",
]
BRAND_QUERY_MAP = {
}

VALID_LAPTOP_KEYWORDS = [
    "laptop", "notebook", "thinkpad", "ideapad", "vivobook", 
    "inspiron", "legion", "macbook", "zenbook"
]

INVALID_LAPTOP_KEYWORDS = [
    "charger", "adapter", "battery", "keyboard", "mouse", 
    "bag", "cover", "sleeve", "screen guard", "stand", "cable",
    "desktop", "motherboard", "cooling pad", "docking station",
    "skin", "decal", "protector", "case", "backpack"
]

MAX_ITEMS_PER_RUN = 400

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


def canonicalize_flipkart_url(url):
    if not url:
        return UNKNOWN_LINK
    # Extract PID parameter if exists
    pid_match = re.search(r'[?&]pid=([A-Z0-9]{16})', url)
    # Remove all query params first
    base_url = url.split("?")[0]
    if pid_match:
        pid = pid_match.group(1)
        return f"{base_url}?pid={pid}"
    return base_url


def build_flipkart_link(link):
    if not link:
        return UNKNOWN_LINK
    if link.startswith("http://") or link.startswith("https://"):
        full_url = link
    else:
        full_url = f"https://www.flipkart.com{link}"
    return canonicalize_flipkart_url(full_url)


def matches_brand_query(search_query, text):
    expected_brand = BRAND_QUERY_MAP.get(search_query)
    if not expected_brand:
        return True
    normalized = (text or "").lower()
    return expected_brand in normalized

def is_strict_laptop(name, text):
    combined_text = f"{name or ''} {text or ''}".lower()
    has_valid = any(kw in combined_text for kw in VALID_LAPTOP_KEYWORDS)
    has_invalid = any(kw in combined_text for kw in INVALID_LAPTOP_KEYWORDS)
    return has_valid and not has_invalid

async def scrape_product_page(browser, full_link):
    page = await browser.new_page(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0.0.0 Safari/537.36"
        )
    )
    
    extra_text = ""
    structured_data = {}
    success = False
    
    for attempt in range(2):
        try:
            await page.goto(full_link, wait_until="domcontentloaded", timeout=45000)
            
            try:
                await page.wait_for_selector("table, div.X3BRgc, div._1UhVsV", timeout=15000)
            except Exception:
                pass
                
            scripts = await page.query_selector_all('script[type="application/ld+json"]')
            for script in scripts:
                content = await script.inner_text()
                if content:
                    try:
                        data = json.loads(content)
                        if isinstance(data, list):
                            data = data[0]
                        if data.get("@type") == "Product":
                            if "name" in data:
                                structured_data["name"] = data["name"]
                            if "brand" in data:
                                brand_val = data["brand"]
                                if isinstance(brand_val, dict) and "name" in brand_val:
                                    structured_data["brand"] = brand_val["name"]
                                elif isinstance(brand_val, str):
                                    structured_data["brand"] = brand_val
                    except Exception:
                        pass
            
            tables = await page.query_selector_all("table")
            for table in tables:
                extra_text += " " + (await table.inner_text() or "")
                
            cells_td = await page.query_selector_all("table td, table th")
            for cell in cells_td:
                extra_text += " " + (await cell.inner_text() or "")
                
            lists = await page.query_selector_all("ul li")
            for li in lists:
                innerText = await li.inner_text() or ""
                if len(innerText) < 150:
                    extra_text += " " + innerText

            success = True
            break
        except Exception as e:
            print(f"    Page load failed: {e}. Retrying...")
            await asyncio.sleep(2)
            
    await page.close()
    return success, extra_text, structured_data

async def scrape_flipkart():
    seen = set()
    processed_count = 0
    max_pages = 6

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        main_page = await browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0.0.0 Safari/537.36"
            )
        )

        for search_query in SEARCH_QUERIES:
            if processed_count >= MAX_ITEMS_PER_RUN:
                break
                
            for page_num in range(1, max_pages + 1):
                if processed_count >= MAX_ITEMS_PER_RUN:
                    break
                    
                print(f"\nScraping Flipkart query '{search_query}' page {page_num}...\n")

                url = f"https://www.flipkart.com/search?q={search_query.replace(' ', '+')}&page={page_num}"
                await main_page.goto(url, wait_until="domcontentloaded", timeout=60000)

                await main_page.keyboard.press("Escape")
                try:
                    await main_page.wait_for_selector("div[data-id]", timeout=20000)
                except Exception:
                    print("No results on this page.")
                    continue
                    
                await main_page.wait_for_timeout(2000)

                products = await main_page.query_selector_all("div[data-id]")
                print("Products found:", len(products))

                for product in products:
                    if processed_count >= MAX_ITEMS_PER_RUN:
                        break
                        
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
                        clean_link = build_flipkart_link(link)
                        img_el = await product.query_selector("img")
                        image = await img_el.get_attribute("src") if img_el else None

                        text_for_features = " ".join(
                            part for part in [name or "", text or "", *specs, clean_link]
                            if part
                        ).strip()
                        unique_key = f"{name}|{clean_link}"
                        
                        if unique_key in seen:
                            continue
                            
                        seen.add(unique_key)
                        
                        if not is_strict_laptop(name, text_for_features):
                            print(f"Skipping non-laptop accessory: {name[:50]}")
                            continue

                        if not matches_brand_query(search_query, text_for_features):
                            continue

                        existing = collection.find_one({
                            "link": clean_link
                        })
                        
                        if existing and existing.get("flipkart_detailed_scraped"):
                            print(f"Already detailed: {name[:50]}")
                            continue

                        print(f"Scraping product page: {name[:50]}")
                        success, extra_text, structured_data = await scrape_product_page(browser, clean_link)
                        
                        if not success:
                            print(f"Skipping due to page fetch failure.")
                            continue

                        combined_source_text = text_for_features + " " + extra_text
                        final_name = structured_data.get("name", name)

                        product_data = {
                            "name": final_name,
                            "price": price_value,
                            "original_price": max(original_price or 0, price_value or 0),
                            "discount_amount": max((original_price or price_value or 0) - (price_value or 0), 0),
                            "discount_percent": discount_percent,
                            "rating": rating,
                            "review_count": review_count,
                            "link": clean_link,
                            "image": image or UNKNOWN_IMAGE,
                            "images": [image] if image else [UNKNOWN_IMAGE],
                            "store": "Flipkart",
                            "website": "flipkart",
                            "category": "laptops",
                            "currency": "INR",
                            "source_text": combined_source_text,
                            "search_query": search_query,
                            "last_seen_at": datetime.now(timezone.utc).isoformat(),
                            "flipkart_detailed_scraped": True
                        }

                        extracted_specs = extract_features(combined_source_text)
                        
                        if structured_data.get("brand") and extracted_specs.get("brand") == "Unknown":
                            extracted_specs["brand"] = structured_data["brand"]
                            
                        if existing:
                            specs_existing = existing.get("specifications", {})
                            for k, v in extracted_specs.items():
                                if v == "Unknown" and specs_existing.get(k) and specs_existing.get(k) != "Unknown":
                                    extracted_specs[k] = specs_existing[k]

                        product_data["specifications"] = extracted_specs
                        product_data.update(extracted_specs)
                        
                        product_data["slug"] = generate_slug(product_data.get("brand"), product_data["name"])

                        collection.update_one(
                            {
                                "link": clean_link
                            },
                            {"$set": product_data},
                            upsert=True
                        )

                        print("Added:", product_data.get("name", "")[:50], "| Price:", price_value)
                        print("Specs:", {k:v for k,v in extracted_specs.items() if k in ["gpu", "processor", "ram", "storage", "screen_size"]})
                        print("------")
                        processed_count += 1
                        
                        await asyncio.sleep(2)

                    except Exception as e:
                        print("Error on item loop:", e)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(scrape_flipkart())
