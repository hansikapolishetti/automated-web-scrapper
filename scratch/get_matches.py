import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.comparison import comparison_payload

def main():
    print("Fetching matches...")
    # Laptops category by default
    payload = comparison_payload(limit=50, category="laptops")
    
    exact = payload.get("exact_matches", [])
    variant = payload.get("variant_matches", [])
    similar = payload.get("spec_comparable_matches", [])
    fallback = payload.get("possible_matches", [])
    
    print("--- EXACT MATCH ---")
    if exact:
        m = exact[0]
        print("Amazon:", m['amazon'].get('link'))
        print("Amazon Title:", m['amazon'].get('name'))
        print("Flipkart:", m['flipkart'].get('link'))
        print("Flipkart Title:", m['flipkart'].get('name'))
        print("Reasons:", m['match_reasons'])
    else:
        print("None found")
        
    print("\n--- VARIANT MATCH ---")
    if variant:
        m = variant[0]
        print("Amazon:", m['amazon'].get('link'))
        print("Amazon Title:", m['amazon'].get('name'))
        print("Flipkart:", m['flipkart'].get('link'))
        print("Flipkart Title:", m['flipkart'].get('name'))
        print("Reasons:", m['match_reasons'])
    else:
        print("None found")

    print("\n--- SIMILAR SPECS MATCH ---")
    if similar:
        m = similar[0]
        print("Amazon:", m['amazon'].get('link'))
        print("Amazon Title:", m['amazon'].get('name'))
        print("Flipkart:", m['flipkart'].get('link'))
        print("Flipkart Title:", m['flipkart'].get('name'))
        print("Reasons:", m['match_reasons'])
    else:
        print("None found")

    print("\n--- RECOMMENDED ALTERNATIVES (FALLBACK) ---")
    if fallback:
        m = fallback[0]
        print("Amazon:", m['amazon'].get('link'))
        print("Amazon Title:", m['amazon'].get('name'))
        print("Flipkart:", m['flipkart'].get('link'))
        print("Flipkart Title:", m['flipkart'].get('name'))
        print("Reasons:", m['match_reasons'])
    else:
        print("None found")

if __name__ == "__main__":
    main()
