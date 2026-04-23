import os
import sys

# Set up path to import utils
PROJECT_ROOT = os.path.abspath(os.path.join(os.getcwd()))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from database.db import get_collection
from utils.comparison import comparison_payload

def get_stats():
    print("Running Global Comparison Engine for Laptops...")
    
    # Passing query="" and limit=9999 runs the global brand-based matching loop
    res = comparison_payload(query="", category="laptops", limit=9999)
    
    exact_total = len(res.get("exact_matches", []))
    variant_total = len(res.get("variant_matches", []))
    similar_total = len(res.get("spec_comparable_matches", []))
    
    col = get_collection("laptops")
    amazon_count = col.count_documents({"website": "amazon"})
    flipkart_count = col.count_documents({"website": "flipkart"})

    print("\n--- Current Database Statistics ---")
    print(f"Total Products: {amazon_count + flipkart_count}")
    print(f"  - Amazon: {amazon_count}")
    print(f"  - Flipkart: {flipkart_count}")
    print("\n--- Global Match Coverage ---")
    print(f"Total Comparable Pairs Found: {exact_total + variant_total + similar_total}")
    print(f"  - Exact Matches: {exact_total}")
    print(f"  - Variant Matches: {variant_total}")
    print(f"  - Similar Spec Matches: {similar_total}")
    print("-----------------------------------")

if __name__ == "__main__":
    get_stats()
