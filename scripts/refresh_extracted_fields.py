import os
import sys


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from database.db import get_collection
from utils.feature_extractor import extract_features, get_rating
from utils.mobile_feature_extractor import extract_mobile_features
from utils.tv_feature_extractor import extract_tv_features


def best_source_text(product):
    return " ".join(
        part
        for part in [
            product.get("source_text", ""),
            product.get("name", ""),
            product.get("link", ""),
        ]
        if part
    ).strip()


def refresh_laptops():
    collection = get_collection("laptops")
    updated = 0
    for product in collection.find({}, {"_id": 1, "source_text": 1, "name": 1, "link": 1, "rating": 1}):
        text = best_source_text(product)
        if not text:
            continue

        features = extract_features(text)
        rating = product.get("rating")
        if rating in ("Unknown", None, ""):
            rating = get_rating(text)

        collection.update_one(
            {"_id": product["_id"]},
            {
                "$set": {
                    "brand": features["brand"],
                    "ram": features["ram"],
                    "storage": features["storage"],
                    "processor": features["processor"],
                    "screen_size": features["screen_size"],
                    "gpu": features["gpu"],
                    "model_code": features["model_code"],
                    "rating": rating,
                }
            },
        )
        updated += 1

    print(f"Refreshed laptop fields for {updated} products")


def refresh_mobiles():
    collection = get_collection("mobiles")
    updated = 0
    for product in collection.find({}, {"_id": 1, "source_text": 1, "name": 1, "link": 1, "rating": 1}):
        text = best_source_text(product)
        if not text:
            continue

        features = extract_mobile_features(text)
        rating = product.get("rating")
        if rating in ("Unknown", None, ""):
            rating = get_rating(text)
        collection.update_one(
            {"_id": product["_id"]},
            {
                "$set": {
                    "brand": features["brand"],
                    "ram": features["ram"],
                    "storage": features["storage"],
                    "processor": features["processor"],
                    "display_size": features["display_size"],
                    "camera": features["camera"],
                    "battery": features["battery"],
                    "network": features["network"],
                    "rating": rating,
                }
            },
        )
        updated += 1

    print(f"Refreshed mobile fields for {updated} products")


def refresh_tvs():
    collection = get_collection("tvs")
    updated = 0
    for product in collection.find({}, {"_id": 1, "source_text": 1, "name": 1, "link": 1, "rating": 1}):
        text = best_source_text(product)
        if not text:
            continue

        features = extract_tv_features(text)
        rating = product.get("rating")
        if rating in ("Unknown", None, ""):
            rating = get_rating(text)
        collection.update_one(
            {"_id": product["_id"]},
            {
                "$set": {
                    "brand": features["brand"],
                    "screen_size": features["screen_size"],
                    "resolution": features["resolution"],
                    "display_type": features["display_type"],
                    "smart_tv": features["smart_tv"],
                    "refresh_rate": features["refresh_rate"],
                    "audio_output": features["audio_output"],
                    "operating_system": features["operating_system"],
                    "rating": rating,
                }
            },
        )
        updated += 1

    print(f"Refreshed TV fields for {updated} products")


if __name__ == "__main__":
    refresh_laptops()
    refresh_mobiles()
    refresh_tvs()
