import os
import sys
from datetime import datetime, timezone


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from database.db import get_collection


def backfill_collection(category):
    collection = get_collection(category)
    now = datetime.now(timezone.utc).isoformat()
    updates = 0

    for product in collection.find(
        {},
        {
            "_id": 1,
            "price": 1,
            "category": 1,
            "currency": 1,
            "original_price": 1,
            "discount_amount": 1,
            "discount_percent": 1,
            "rating": 1,
            "review_count": 1,
            "last_seen_at": 1,
        },
    ):
        price = product.get("price") or 0
        update_fields = {
            "category": product.get("category") or category,
            "currency": product.get("currency") or "INR",
            "original_price": product.get("original_price") or price,
            "discount_amount": product.get("discount_amount") or 0,
            "discount_percent": product.get("discount_percent") or 0,
            "rating": product.get("rating") or "Unknown",
            "review_count": product.get("review_count") or 0,
            "last_seen_at": product.get("last_seen_at") or now,
        }

        collection.update_one({"_id": product["_id"]}, {"$set": update_fields})
        updates += 1

    print(f"Backfilled {updates} {category} products")


if __name__ == "__main__":
    for category in ("laptops", "mobiles", "tvs"):
        backfill_collection(category)
