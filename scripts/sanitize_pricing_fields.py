import os
import sys


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from database.db import collection


def sane_original_price(original_price, price):
    if not price:
        return price
    if not original_price or original_price < price:
        return price
    if original_price > price * 3:
        return price
    return original_price


def main():
    updated = 0
    for product in collection.find({}, {"_id": 1, "price": 1, "original_price": 1, "discount_percent": 1}):
        price = product.get("price") or 0
        original_price = sane_original_price(product.get("original_price"), price)
        discount_amount = max(original_price - price, 0)
        discount_percent = product.get("discount_percent") or 0
        if original_price == price:
            discount_percent = 0

        collection.update_one(
            {"_id": product["_id"]},
            {
                "$set": {
                    "original_price": original_price,
                    "discount_amount": discount_amount,
                    "discount_percent": discount_percent,
                }
            },
        )
        updated += 1

    print(f"Sanitized pricing for {updated} products")


if __name__ == "__main__":
    main()
