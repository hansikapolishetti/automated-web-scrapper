import os
import sys


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from database.db import collection
from utils.feature_extractor import extract_features, get_rating


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


def main():
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

    print(f"Refreshed extracted fields for {updated} products")


if __name__ == "__main__":
    main()
