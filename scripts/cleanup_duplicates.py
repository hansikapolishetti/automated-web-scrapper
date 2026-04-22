import sys
import os
import re
from pathlib import Path
from collections import defaultdict

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from database.db import collection

def canonicalize_amazon_url(url):
    if not url: return None
    asin_match = re.search(r'/(?:dp|gp/product)/([A-Z0-9]{10})', url)
    if asin_match:
        asin = asin_match.group(1)
        return f"https://www.amazon.in/dp/{asin}"
    return url.split("?")[0]

def canonicalize_flipkart_url(url):
    if not url: return None
    pid_match = re.search(r'[?&]pid=([A-Z0-9]{16})', url)
    base_url = url.split("?")[0]
    if pid_match:
        pid = pid_match.group(1)
        return f"{base_url}?pid={pid}"
    return base_url

def cleanup_duplicates():
    print("=== STARTING DATABASE CLEANUP ===")
    
    # 1. Update all existing records to have canonical links first (optional but good for consistency)
    all_laptops = list(collection.find({}))
    print(f"Total laptops in DB initially: {len(all_laptops)}")
    
    # Group by: (canonical_link, name, price, ram, storage, processor, website)
    # This follows the user's strict rule: "even if 1 field differs then they are unique"
    groups = defaultdict(list)
    
    for doc in all_laptops:
        website = doc.get("website", "amazon")
        link = doc.get("link", "")
        
        if website == "amazon":
            canon_link = canonicalize_amazon_url(link)
        else:
            canon_link = canonicalize_flipkart_url(link)
            
        # The key for perfect duplicates includes ALL data fields
        key = (
            canon_link,
            doc.get("name"),
            doc.get("price"),
            doc.get("ram"),
            doc.get("storage"),
            doc.get("processor"),
            doc.get("screen_size"),
            website
        )
        groups[key].append(doc)
    
    to_delete = []
    merges_count = 0
    
    for key, docs in groups.items():
        if len(docs) > 1:
            # Sort by last_seen_at or just take the first
            docs.sort(key=lambda x: x.get("last_seen_at", ""), reverse=True)
            # Keep the first one, delete the rest
            keep_id = docs[0]["_id"]
            for d in docs[1:]:
                to_delete.append(d["_id"])
            merges_count += 1

    print(f"Found {len(to_delete)} perfect duplicates across {merges_count} product groups.")
    
    if to_delete:
        print(f"Deleting {len(to_delete)} redundant records...")
        result = collection.delete_many({"_id": {"$in": to_delete}})
        print(f"Successfully deleted {result.deleted_count} records.")
    else:
        print("No duplicates found according to strict criteria.")

    # 2. Canonicalize existing links in remaining records
    print("\nUpdating links to canonical format...")
    remaining_laptops = collection.find({})
    updated_count = 0
    for doc in remaining_laptops:
        website = doc.get("website")
        link = doc.get("link")
        if website == "amazon":
            new_link = canonicalize_amazon_url(link)
        else:
            new_link = canonicalize_flipkart_url(link)
        
        if new_link != link:
            collection.update_one({"_id": doc["_id"]}, {"$set": {"link": new_link}})
            updated_count += 1
    
    print(f"Canonicalized {updated_count} URLs.")
    print("=== CLEANUP COMPLETE ===")

if __name__ == "__main__":
    cleanup_duplicates()
