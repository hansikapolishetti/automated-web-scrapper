from utils.classification.laptops import extract_series, same_series, same_cpu_family, is_variant_laptop

a = {"name": "HP Professional 15 (2026), Intel (i5 14th Gen) Core 5 120U", "processor": "Intel Core 5 120U", "ram": "8GB", "storage": "512GB", "brand": "HP"}
b = {"name": "HP 15s Metal Intel Core i3 13th Gen 1315U", "processor": "Intel Core i3 13th Gen 1315U", "ram": "8GB", "storage": "512GB", "brand": "HP"}

print(f"Series A: {extract_series(a['name'])}")
print(f"Series B: {extract_series(b['name'])}")
print(f"Same Series: {same_series(a, b)}")
print(f"Same CPU Family: {same_cpu_family(a, b)}")
print(f"Is Variant: {is_variant_laptop(a, b)}")
