import json
import os
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from database.db import get_collection, COLLECTION_BY_CATEGORY
from utils.comparison import comparison_payload


CATEGORIES = list(COLLECTION_BY_CATEGORY.keys())


def serialize(obj):
    """Make MongoDB documents JSON-serialisable."""
    if isinstance(obj, dict):
        return {k: serialize(v) for k, v in obj.items() if k != "_id"}
    if isinstance(obj, list):
        return [serialize(i) for i in obj]
    # ObjectId, datetime, etc.
    try:
        json.dumps(obj)
        return obj
    except (TypeError, ValueError):
        return str(obj)


# ---------------------------------------------------------------------------
# Route handlers
# ---------------------------------------------------------------------------

def handle_health():
    return 200, {"status": "OK", "message": "Python backend is healthy"}


def _generate_slug(name):
    """Generate a URL-safe slug from a product name."""
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug


def handle_categories():
    counts = []
    for cat in CATEGORIES:
        col = get_collection(cat)
        # Try slug field first; fall back to counting by name when slugs are absent
        has_slug = col.count_documents({"slug": {"$exists": True}}, limit=1) > 0
        if has_slug:
            count = len(col.distinct("slug"))
        else:
            count = len(col.distinct("name"))
        counts.append({
            "id": cat,
            "name": cat.capitalize(),
            "count": count
        })
    return 200, counts


def handle_brands(params):
    category = (params.get("category", ["laptops"])[0] or "laptops").strip().lower()
    col = get_collection(category)
    brands = sorted([b for b in col.distinct("brand") if b])
    return 200, brands


def handle_products(params):
    category = (params.get("category", ["laptops"])[0] or "laptops").strip().lower()
    limit = min(int(params.get("limit", ["24"])[0] or 24), 100)
    
    # Selected brands filter
    selected_brands = params.get("brands", [])
    if selected_brands and len(selected_brands) == 1 and "," in selected_brands[0]:
        selected_brands = [b.strip() for b in selected_brands[0].split(",") if b.strip()]

    col = get_collection(category)
    has_slug = col.count_documents({"slug": {"$exists": True}}, limit=1) > 0
    group_key = "$slug" if has_slug else "$name"

    # Match stage for brands
    match_stage = {}
    if selected_brands:
        match_stage = {"$match": {"brand": {"$in": selected_brands}}}

    # Common grouping stage
    group_stage = {
        "$group": {
            "_id":            group_key,
            "name":           {"$first": "$name"},
            "brand":          {"$first": "$brand"},
            "image":          {"$first": "$image"},
            "images":         {"$first": "$images"},
            "price":          {"$min": "$price"},
            "original_price": {"$first": "$original_price"},
            "rating":         {"$first": "$rating"},
            "category":       {"$first": "$category"},
            "website":        {"$first": "$website"},
            "slug":           {"$first": "$slug"} if has_slug else {"$first": "$name"},
        }
    }

    # 1. Get Top Rated
    pipeline_top_rated = []
    if match_stage: pipeline_top_rated.append(match_stage)
    pipeline_top_rated.extend([
        {"$sort": {"rating": -1}},
        group_stage,
        {"$sort": {"rating": -1}},
        {"$limit": limit // 2}
    ])
    top_rated = list(col.aggregate(pipeline_top_rated))
    for p in top_rated: p["tag"] = "Top Rated"

    # 2. Get Lowest Price
    pipeline_lowest_price = []
    if match_stage: pipeline_lowest_price.append(match_stage)
    pipeline_lowest_price.extend([
        {"$sort": {"price": 1}},
        group_stage,
        {"$sort": {"price": 1}},
        {"$limit": limit // 2}
    ])
    lowest_price = list(col.aggregate(pipeline_lowest_price))
    for p in lowest_price: p["tag"] = "Best Price"

    # Combine and remove duplicates based on slug
    seen_slugs = set()
    products = []
    
    for p in top_rated:
        if p["slug"] not in seen_slugs:
            products.append(p)
            seen_slugs.add(p["slug"])
    
    for p in lowest_price:
        if p["slug"] not in seen_slugs:
            products.append(p)
            seen_slugs.add(p["slug"])

    for p in products:
        if not p.get("slug"):
            p["slug"] = _generate_slug(p.get("name", ""))

    total_query = {}
    if selected_brands:
        total_query["brand"] = {"$in": selected_brands}
        
    total = len(col.distinct("slug" if has_slug else "name", total_query))
    return 200, {"products": serialize(products), "total": total}


def handle_product_detail(slug):
    for cat in CATEGORIES:
        col = get_collection(cat)
        variants = list(col.find({"slug": slug}))
        if variants:
            first = variants[0]
            stores = []
            for v in variants:
                website = v.get("website", "")
                stores.append({
                    "name":         "Amazon" if website == "amazon" else "Flipkart" if website == "flipkart" else website,
                    "price":        v.get("price"),
                    "oldPrice":     v.get("original_price"),
                    "link":         v.get("link"),
                    "rating":       v.get("rating"),
                    "review_count": v.get("review_count"),
                    "logo":         "/images/amazon-logo.png" if website == "amazon" else "/images/flipkart-logo.png",
                })
            product = {
                "title":          first.get("name"),
                "slug":           first.get("slug"),
                "brand":          first.get("brand"),
                "images":         first.get("images") or [first.get("image")],
                "specifications": first.get("specifications") or {},
                "category":       first.get("category"),
                "rating":         first.get("rating"),
                "review_count":   first.get("review_count"),
                "description":    first.get("source_text", ""),
                "stores":         stores,
            }
            return 200, serialize(product)
    return 404, {"error": "Product not found"}


def handle_product_prices(slug):
    query = slug.replace("-", " ")
    result = comparison_payload(query=query, limit=20)
    return 200, serialize(result)


def handle_similar(slug, params):
    category = (params.get("category", ["laptops"])[0] or "laptops").strip().lower()
    col = get_collection(category)
    product = col.find_one({"slug": slug})
    if not product:
        return 200, []
    similar = list(col.find({
        "category": product.get("category"),
        "brand":    product.get("brand"),
        "slug":     {"$ne": slug}
    }).limit(6))
    return 200, serialize(similar)


def handle_search(params):
    query = (params.get("q", [""])[0] or "").strip()
    category = (params.get("category", ["laptops"])[0] or "laptops").strip().lower()
    if not query:
        return 200, {"products": [], "total": 0}
    result = comparison_payload(query=query, category=category, limit=20)
    return 200, serialize(result)


def handle_api_compare(params):
    slug = (params.get("id", [""])[0] or "").strip()
    if not slug:
        return 400, {"error": "Missing product id (slug)"}

    # 1. Fetch anchor product
    product_data = None
    category = None
    anchor_docs = []
    
    for cat in CATEGORIES:
        col = get_collection(cat)
        docs = list(col.find({"slug": slug}))
        if docs:
            category = cat
            anchor_docs = docs
            _, product_data = handle_product_detail(slug)
            break

    # Case 3: Product Not Found
    if not product_data:
        # Return empty list for matches but maybe some global fallbacks
        results = comparison_payload(query="", limit=5, category="laptops")
        return 200, {
            "product": None,
            "exact_matches": [],
            "variant_matches": [],
            "spec_comparable_matches": [],
            "fallback_matches": serialize(results.get("fallback_matches", []))[:5]
        }

    # 2. Get full comparison payload for the category
    results = comparison_payload(category=category, limit=9999)

    anchor_ids = {str(d.get("_id", "")) for d in anchor_docs}

    def _id(p): return str(p.get("_id", "") or p.get("id", ""))

    def _filter_matches(match_list):
        seen_counterpart = set()
        out = []
        for m in match_list:
            amz = m.get("amazon", {}) or {}
            fk  = m.get("flipkart", {}) or {}
            amz_id = _id(amz)
            fk_id  = _id(fk)

            anchor_is_amz = (amz_id in anchor_ids) or (amz.get("slug") == slug)
            anchor_is_fk  = (fk_id in anchor_ids) or (fk.get("slug") == slug)

            # Keep only if anchor is in this pair
            if not anchor_is_amz and not anchor_is_fk:
                continue

            # Counterpart is the other side
            counterpart = fk if anchor_is_amz else amz
            c_id = _id(counterpart)

            if not c_id:
                continue

            # Cross-site rule: counterpart must be from a diff website
            anchor_website = amz.get("website") if anchor_is_amz else fk.get("website")
            if counterpart.get("website") == anchor_website:
                continue

            # Skip same product itself
            if (c_id in anchor_ids) or (counterpart.get("slug") == slug):
                continue

            if c_id in seen_counterpart:
                continue

            seen_counterpart.add(c_id)
            out.append(m)
        return out

    exact_matches          = _filter_matches(results.get("exact_matches", []))
    variant_matches        = _filter_matches(results.get("variant_matches", []))
    spec_comparable_matches = _filter_matches(results.get("spec_comparable_matches", []))
    fallback_matches       = _filter_matches(results.get("fallback_matches", []))

    # ENFORCE AT LEAST ONE FALLBACK
    if not (exact_matches or variant_matches or spec_comparable_matches or fallback_matches):
        col = get_collection(category)
        anchor_brand = product_data.get("brand") if product_data else None
        anchor_website = anchor_docs[0].get("website") if anchor_docs else None
        target_website = "flipkart" if anchor_website == "amazon" else "amazon"
        
        fallback_query = {"website": target_website}
        if anchor_brand:
            fallback_query["brand"] = anchor_brand
        
        fbs_pool = list(col.find(fallback_query).limit(50))
        if not fbs_pool:
            fbs_pool = list(col.find({"website": target_website}).limit(50))
            
        from utils.comparison import get_fallback_score
        is_mob = category.lower() == "mobiles"
        is_tv = category.lower() == "tvs"

        ranked_fbs = []
        for f in fbs_pool:
            sc = get_fallback_score(product_data, f, is_mobile_category=is_mob, is_tv_category=is_tv)
            ranked_fbs.append((sc, f))
            
        ranked_fbs.sort(key=lambda x: x[0], reverse=True)
        
        seen_names = set()
        final_fbs = []
        for _, f in ranked_fbs:
            nm = (f.get("name") or "").strip().lower()
            if nm in seen_names:
                continue
            seen_names.add(nm)
            final_fbs.append(f)
            if len(final_fbs) >= 3:
                break
            
        # Manually create fallback match objects
        for f in final_fbs:
            amz_side = anchor_docs[0] if anchor_website == "amazon" else f
            fk_side = f if anchor_website == "amazon" else anchor_docs[0]
            
            fallback_matches.append({
                "score": 10,
                "match_reasons": ["fallback"],
                "amazon": amz_side,
                "flipkart": fk_side,
                "cheaper_site": "none",
                "price_difference": 0
            })

    # Logging for verification (can be removed later)
    print(f"[DEBUG] Comparison for {slug}:")
    print(f"  - Exact: {len(exact_matches)}")
    print(f"  - Variants: {len(variant_matches)}")
    print(f"  - Spec Comparable: {len(spec_comparable_matches)}")
    print(f"  - Fallback: {len(fallback_matches)}")

    # 3. Combine and return serialized data
    return 200, {
        "product": product_data,
        "exact_matches": serialize(exact_matches),
        "variant_matches": serialize(variant_matches),
        "spec_comparable_matches": serialize(spec_comparable_matches),
        "fallback_matches": serialize(fallback_matches)
    }


def handle_compare(params):
    query = (params.get("query", [""])[0] or "").strip()
    category = (params.get("category", ["laptops"])[0] or "laptops").strip().lower()
    try:
        limit = int(params.get("limit", ["20"])[0])
    except ValueError:
        limit = 20
    limit = max(1, min(limit, 50))
    result = comparison_payload(query=query, limit=limit, category=category)
    return 200, serialize(result)


# ---------------------------------------------------------------------------
# HTTP Handler
# ---------------------------------------------------------------------------

# Pre-compiled pattern:  /api/products/<slug>/prices  or  /api/products/<slug>/similar
SLUG_PRICES_RE  = re.compile(r"^/api/products/([^/]+)/prices$")
SLUG_SIMILAR_RE = re.compile(r"^/api/products/([^/]+)/similar$")
SLUG_DETAIL_RE  = re.compile(r"^/api/products/([^/]+)$")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # suppress default noisy logs
        print(f"{self.address_string()} - {fmt % args}")

    def _send_json(self, status_code, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path   = parsed.path
        params = parse_qs(parsed.query)

        try:
            if path == "/health":
                status, data = handle_health()

            elif path == "/api/categories":
                status, data = handle_categories()

            elif path == "/api/products":
                status, data = handle_products(params)

            elif path == "/api/brands":
                status, data = handle_brands(params)

            elif m := SLUG_PRICES_RE.match(path):
                status, data = handle_product_prices(m.group(1))

            elif m := SLUG_SIMILAR_RE.match(path):
                status, data = handle_similar(m.group(1), params)

            elif m := SLUG_DETAIL_RE.match(path):
                status, data = handle_product_detail(m.group(1))

            elif path == "/api/search":
                status, data = handle_search(params)

            elif path == "/api/compare":
                status, data = handle_api_compare(params)

            elif path == "/compare":
                status, data = handle_compare(params)

            else:
                status, data = 404, {"error": "Not found"}

        except Exception as exc:
            import traceback
            traceback.print_exc()
            status, data = 500, {"error": "Internal server error", "detail": str(exc)}

        self._send_json(status, data)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Python API server running on http://localhost:{PORT}")
    server.serve_forever()
