import os
from pathlib import Path

from pymongo import MongoClient


def load_env_file():
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env_file()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "price_comparison")
DEFAULT_PRODUCT_CATEGORY = os.getenv("DEFAULT_PRODUCT_CATEGORY", "laptops")

COLLECTION_BY_CATEGORY = {
    "laptops": os.getenv("MONGODB_LAPTOPS_COLLECTION", "laptops"),
    "mobiles": os.getenv("MONGODB_MOBILES_COLLECTION", "mobiles"),
    "tvs": os.getenv("MONGODB_TVS_COLLECTION", "tvs"),
    "audio": os.getenv("MONGODB_AUDIO_COLLECTION", "audio"),
}

if not MONGODB_URI:
    raise RuntimeError("MONGODB_URI is not set. Add your MongoDB Atlas URI to the .env file.")

client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)

# Force an early connection check so Atlas/local config issues fail fast.
client.admin.command("ping")

db = client[MONGODB_DB_NAME]


def get_collection(category=DEFAULT_PRODUCT_CATEGORY):
    normalized_category = (category or DEFAULT_PRODUCT_CATEGORY).strip().lower()
    collection_name = COLLECTION_BY_CATEGORY.get(normalized_category, normalized_category)
    return db[collection_name]


# Backward-compatible alias used by current laptop scrapers/comparison code.
collection = get_collection("laptops")
