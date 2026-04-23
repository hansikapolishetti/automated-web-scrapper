from utils.classification.router import classify_product

def test_exact_model_code():
    a = {"brand":"ASUS","processor":"i5-1334U","ram":"16GB","storage":"512GB","model_code":"X123","gpu":"Intel","price":50000}
    b = {"brand":"ASUS","processor":"i5 1334U","ram":"16GB","storage":"512GB","model_code":"X123","gpu":"Intel","price":50500}
    assert classify_product(a,b,"laptops") == "exact"


def test_not_exact_cpu_diff():
    a = {"brand":"Acer","processor":"i5-13420H","ram":"16GB","storage":"512GB","model_code":"AL15","gpu":"Intel","price":55000}
    b = {"brand":"Acer","processor":"i7-12650H","ram":"16GB","storage":"512GB","model_code":"AL15","gpu":"Intel","price":65000}
    assert classify_product(a,b,"laptops") != "exact"


def test_fallback_exact():
    a = {"brand":"HP","processor":"i3-1215U","ram":"8GB","storage":"512GB","model_code":None,"gpu":"Intel","price":40000}
    b = {"brand":"HP","processor":"i3 1215U","ram":"8GB","storage":"512GB","model_code":None,"gpu":"Intel","price":40500}
    assert classify_product(a,b,"laptops") == "exact"


def test_similar_segment_diff():
    a = {"brand":"HP","processor":"Ryzen 5 7535HS","ram":"16GB","storage":"512GB","model_code":"A","gpu":"RTX","price":70000}
    b = {"brand":"HP","processor":"Ryzen 5 5625U","ram":"16GB","storage":"512GB","model_code":"B","gpu":"Integrated","price":65000}
    assert classify_product(a,b,"laptops") == "similar"


def test_intel_vs_amd_not_similar():
    a = {"brand":"Dell","processor":"i5-1334U","ram":"16GB","storage":"512GB","model_code":"A","gpu":"Intel","price":60000}
    b = {"brand":"Dell","processor":"Ryzen 5 5625U","ram":"16GB","storage":"512GB","model_code":"B","gpu":"AMD","price":58000}
    assert classify_product(a,b,"laptops") != "similar"


def test_intel_new_naming():
    a = {"brand":"Lenovo","processor":"Intel Core 5 120U","ram":"16GB","storage":"512GB","model_code":"A","gpu":"Intel","price":60000}
    b = {"brand":"Lenovo","processor":"Intel Core i5-1335U","ram":"16GB","storage":"512GB","model_code":"B","gpu":"Intel","price":58000}
    # Should be similar: same brand, same cpu family (Core 5 == i5), same ram, price close
    assert classify_product(a,b,"laptops") == "similar"


# ─── EDGE CASE TESTS ────────────────────────────────────────────────────────────

def test_variant_ram_diff_not_variant():
    # is_variant_laptop requires same_ram AND same_storage.
    # RAM mismatch (8GB vs 16GB) breaks the variant gate → falls through to similar/recommended.
    a = {"brand":"HP","name":"HP Pavilion 15","processor":"i5-1335U","ram":"8GB","storage":"512GB","model_code":"X1","gpu":"Intel","price":50000}
    b = {"brand":"HP","name":"HP Pavilion 15","processor":"i5-1335U","ram":"16GB","storage":"512GB","model_code":"X1","gpu":"Intel","price":55000}
    result = classify_product(a, b, "laptops")
    assert result in ["similar", "recommended"], (
        f"RAM diff should produce similar/recommended, got '{result}'"
    )


def test_variant_same_series_and_specs():
    # True variant: same brand, same series name (IdeaPad 5), same cpu family, same ram+storage
    a = {"brand":"Lenovo","name":"Lenovo IdeaPad 5","processor":"i5-1335U","ram":"16GB","storage":"512GB","model_code":"A1","gpu":"Intel","price":60000}
    b = {"brand":"Lenovo","name":"Lenovo IdeaPad 5","processor":"i5-1235U","ram":"16GB","storage":"512GB","model_code":"A2","gpu":"Intel","price":62000}
    assert classify_product(a, b, "laptops") == "variant"


def test_different_brand_not_similar():
    # Cross-brand products fail the same_brand gate → can never be "similar"
    a = {"brand":"HP","processor":"i5-1335U","ram":"16GB","storage":"512GB","model_code":"A","gpu":"Intel","price":60000}
    b = {"brand":"Dell","processor":"i5-1335U","ram":"16GB","storage":"512GB","model_code":"B","gpu":"Intel","price":60000}
    assert classify_product(a, b, "laptops") != "similar"


def test_large_price_gap_not_similar():
    # price_close() uses a 15% threshold. ₹50k vs ₹90k is an ~80% gap → never similar.
    a = {"brand":"Lenovo","processor":"i5-1335U","ram":"16GB","storage":"512GB","model_code":"A","gpu":"Intel","price":50000}
    b = {"brand":"Lenovo","processor":"i5-1335U","ram":"16GB","storage":"512GB","model_code":"B","gpu":"Intel","price":90000}
    assert classify_product(a, b, "laptops") != "similar"


def test_missing_processor_robustness():
    # None processor resolves to family "unknown" → similar gate fails (same_cpu_family=False).
    # Result must still be a valid string and not raise any exception.
    a = {"brand":"HP","processor":None,"ram":"16GB","storage":"512GB","model_code":None,"gpu":"Intel","price":50000}
    b = {"brand":"HP","processor":"i5-1335U","ram":"16GB","storage":"512GB","model_code":None,"gpu":"Intel","price":52000}
    result = classify_product(a, b, "laptops")
    assert result in ["exact", "variant", "similar", "recommended"], (
        f"Missing processor must not crash; got '{result}'"
    )


def test_gpu_difference_not_exact():
    # Dedicated GPU (RTX 3050) vs Integrated GPU — different model codes → primary exact fails.
    # Fallback exact requires same_gpu which also fails → must not return "exact".
    a = {"brand":"Lenovo","processor":"i7-13700H","ram":"16GB","storage":"1TB","model_code":"A","gpu":"RTX 3050","price":90000}
    b = {"brand":"Lenovo","processor":"i7-13700H","ram":"16GB","storage":"1TB","model_code":"B","gpu":"Integrated","price":80000}
    assert classify_product(a, b, "laptops") != "exact"


def test_same_specs_different_model_code():
    # Different model codes but identical processor SKU, same gpu (Intel), price identical.
    # Fallback exact path: same_brand + same_cpu_exact + same_ram + same_storage + same_gpu + price ≤10% → exact.
    a = {"brand":"ASUS","processor":"i5-1335U","ram":"16GB","storage":"512GB","model_code":"X1","gpu":"Intel","price":60000}
    b = {"brand":"ASUS","processor":"i5-1335U","ram":"16GB","storage":"512GB","model_code":"X2","gpu":"Intel","price":60000}
    result = classify_product(a, b, "laptops")
    assert result in ["exact", "similar", "variant"], (
        f"Same specs/diff model_code should be exact/similar/variant, got '{result}'"
    )


def test_noisy_processor_name_similar():
    # "i5 1335U" vs "Intel i5-1335U" → SKU regex extracts "1335u" for both → same_cpu_exact = True.
    # Same brand + cpu + ram + price → at minimum "similar", possibly "exact" via fallback.
    a = {"brand":"Acer","processor":"i5 1335U","ram":"16GB","storage":"512GB","model_code":"A","gpu":"Intel","price":60000}
    b = {"brand":"Acer","processor":"Intel i5-1335U","ram":"16GB","storage":"512GB","model_code":"B","gpu":"Intel","price":60000}
    result = classify_product(a, b, "laptops")
    assert result in ["exact", "similar"], (
        f"Noisy processor names for same CPU should classify as exact/similar, got '{result}'"
    )


def test_case_insensitive_brand():
    # normalize_value() lowercases brand strings before comparison.
    # "HP" and "hp" resolve to the same normalized value → same_brand returns True.
    # With same cpu SKU + gpu + price, the fallback exact path fires → result is "exact".
    a = {"brand":"HP","processor":"i5-1335U","ram":"16GB","storage":"512GB","model_code":"A","gpu":"Intel","price":60000}
    b = {"brand":"hp","processor":"i5-1335U","ram":"16GB","storage":"512GB","model_code":"B","gpu":"Intel","price":60000}
    result = classify_product(a, b, "laptops")
    assert result == "exact", (
        f"Brand case difference should not affect classification. Expected 'exact', got '{result}'"
    )
