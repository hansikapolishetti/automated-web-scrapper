# Project Progress

This file records the main implementation stages so commits stay easy to understand later.

## Stage 1: Scraper and Data Foundation

Goal:
- get Amazon and Flipkart laptop data into MongoDB

Main work:
- added Python scraper flow for Amazon and Flipkart
- added MongoDB connection and product upsert flow
- added base feature extraction for `brand`, `ram`, `storage`, and `processor`

Outcome:
- products from both sites can be stored in category-specific collections, starting with `laptops`

Suggested commit theme:
- `Add scraper pipeline and normalized product storage`

## Stage 2: Scraping Coverage and Cleanup

Goal:
- increase overlap between both sites and reduce noisy rows

Main work:
- added multi-query scraping:
  - `laptops`
  - `gaming laptop`
  - `business laptop`
  - `thin and light laptop`
  - brand-specific laptop queries
- added cross-run dedupe keys using `name + link`
- added brand-query filtering so brand searches keep relevant rows only
- improved stored `source_text` with richer text for extraction
- ignored Python cache files in git
- cleaned obvious junk and brand-mismatched rows from MongoDB

Outcome:
- broader product coverage
- cleaner database rows
- stronger cross-site overlap

Suggested commit theme:
- `Improve scraper coverage and clean noisy laptop records`

## Stage 3: Strict Feature Extraction

Goal:
- make product fields more useful for matching and comparison

Main work:
- improved normalization in `feature_extractor.py`
- expanded extraction for:
  - `screen_size`
  - `gpu`
  - `model_code`
- improved handling for multiple spec formats like slash, comma, and hyphenated forms

Outcome:
- stronger structured data for comparison

Suggested commit theme:
- `Enhance laptop feature extraction for matching`

## Stage 4: Comparison Engine

Goal:
- compare overlapping laptops from Amazon and Flipkart in meaningful levels

Main work:
- added `utils/comparison.py`
- added comparison API helper in `backend/compare_products.py`
- added Python comparison server in `backend/server.py`
- added comparison tiers:
  - `exact_matches`
  - `variant_matches`
  - `spec_comparable_matches`
  - `all_comparable_matches`
  - `best_value_matches`
- made tiers hierarchical so each Amazon product lands in one main comparable bucket
- added difference analysis for fields like:
  - `model_code`
  - `screen_size`
  - `gpu`
  - `price`
  - `processor`
  - `ram`
  - `storage`

Outcome:
- usable comparison dataset for frontend/backend work
- clearer distinction between exact, variant, and broader similar-spec matches

Suggested commit theme:
- `Add hierarchical laptop comparison and value matching`

## Stage 5: PriceScout Frontend and Product UI

Goal:
- introduce the first real frontend for the project and present comparison results in a user-facing way

Main work:
- introduced the `PriceScout` product name
- built the first React frontend experience for the project
- added:
  - landing homepage
  - search-first hero section
  - category cards
  - laptop comparison workspace
  - comparison tabs for exact, variant, similar-spec, and best-deal views
- added light and dark theme support
- improved homepage/search behavior so:
  - no results load by default on empty input
  - short weak text queries are ignored
  - pasted Amazon/Flipkart product links can be used as search input
- hid noisy unknown values from the product UI to keep cards cleaner

Outcome:
- the project now has its first branded frontend experience
- comparison data can be explored visually instead of only through raw API output

Suggested commit theme:
- `Build PriceScout frontend and introduce project branding`

## Current Backend Note

Current active testing backend:
- `backend/server.py`

Reason:
- scraping, comparison, and database logic are currently handled in Python

Planned app architecture:
- Python for scraping and comparison
- Node/Express for main app backend APIs later
- frontend should eventually call Express, not the Python test server directly
