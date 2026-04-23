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
    # Should be similar because same brand, same family (Core 5 == i5), same ram, price close
    assert classify_product(a,b,"laptops") == "similar"

