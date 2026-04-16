import os
import re
from pathlib import Path

from pymongo import MongoClient


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"
DEFAULT_BASE_DB_NAME = "price_comparison"
DEFAULT_COLLECTION_NAME = "products"
CATEGORY_ALIASES = {
    "laptop": "laptops",
    "laptops": "laptops",
    "mobile": "mobiles",
    "mobiles": "mobiles",
    "tv": "tvs",
    "tvs": "tvs",
    "audio": "audio",
}
BASE_ENV_KEYS = {
    "MONGODB_URI",
    "MONGODB_DB_NAME",
    "DEFAULT_PRODUCT_CATEGORY",
}


def _load_env_file():
    if not ENV_FILE.exists():
        return

    content = None
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            content = ENV_FILE.read_text(encoding=encoding)
            break
        except UnicodeDecodeError:
            continue

    if content is None:
        return

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def _sanitize_name(value):
    normalized = re.sub(r"[^a-z0-9]+", "_", (value or "").strip().lower())
    return normalized.strip("_")


def normalize_category(category=None):
    default_category = os.getenv("DEFAULT_PRODUCT_CATEGORY", "laptop")
    raw_category = category or default_category
    sanitized = _sanitize_name(raw_category)

    if sanitized in CATEGORY_ALIASES:
        return CATEGORY_ALIASES[sanitized]

    if sanitized.endswith("s"):
        return sanitized

    return f"{sanitized}s" if sanitized else "products"


def category_label(category=None):
    normalized = normalize_category(category)
    if normalized.endswith("ies"):
        return f"{normalized[:-3]}y"
    if normalized.endswith("s") and normalized not in {"tvs"}:
        return normalized[:-1]
    return normalized


def _category_env_prefix(category=None):
    return f"MONGODB_{normalize_category(category).upper()}"


def get_database_name(category=None):
    env_prefix = _category_env_prefix(category)
    configured = os.getenv(f"{env_prefix}_DB_NAME")
    if configured:
        return configured

    return os.getenv("MONGODB_DB_NAME", DEFAULT_BASE_DB_NAME)


def get_collection_name(category=None):
    env_prefix = _category_env_prefix(category)
    return os.getenv(f"{env_prefix}_COLLECTION", DEFAULT_COLLECTION_NAME)


def get_mongodb_uri():
    uri = os.getenv("MONGODB_URI", "").strip()
    if not uri:
        raise RuntimeError("MONGODB_URI is not configured. Add it to your .env file.")
    if "<db_password>" in uri:
        raise RuntimeError("MONGODB_URI still contains <db_password>. Replace it with your Atlas password.")
    return uri


def _configured_env_categories():
    categories = set()

    for key in os.environ:
        if not key.startswith("MONGODB_") or key in BASE_ENV_KEYS:
            continue
        if key.endswith("_COLLECTION"):
            raw_category = key[len("MONGODB_"):-len("_COLLECTION")]
        elif key.endswith("_DB_NAME"):
            raw_category = key[len("MONGODB_"):-len("_DB_NAME")]
        else:
            continue

        categories.add(normalize_category(raw_category.lower()))

    return categories


_load_env_file()
client = MongoClient(get_mongodb_uri())


def get_database(category=None):
    return client[get_database_name(category)]


def get_collection(category=None):
    return get_database(category)[get_collection_name(category)]


def get_all_category_collections():
    categories = _configured_env_categories()
    categories.add(normalize_category(os.getenv("DEFAULT_PRODUCT_CATEGORY", "laptop")))
    return {
        category: get_collection(category)
        for category in sorted(categories)
    }


collection = get_collection()
