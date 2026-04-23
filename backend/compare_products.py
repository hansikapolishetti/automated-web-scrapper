import argparse
import json
import os
import sys


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from utils.comparison import comparison_payload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", default="")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--category", default="laptops")
    args = parser.parse_args()

    payload = comparison_payload(query=args.query.strip(), limit=args.limit, category=args.category.strip().lower())
    print(json.dumps(payload, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
