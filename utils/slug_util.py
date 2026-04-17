import re

def generate_slug(brand, name):
    """
    Generates a URL-friendly slug from brand and name.
    Example: "ASUS", "Vivobook 16X M1603" -> "asus-vivobook-16x-m1603"
    """
    if not brand:
        brand = "product"
    
    combined = f"{brand} {name}"
    # Convert to lowercase
    slug = combined.lower()
    # Remove special characters
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    # Replace whitespace/underscores with -
    slug = re.sub(r'[\s_]+', '-', slug)
    # Remove multiple -
    slug = re.sub(r'-+', '-', slug)
    # Strip leading/trailing -
    return slug.strip('-')
