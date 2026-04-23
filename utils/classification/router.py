from utils.classification.laptops import classify_laptop
from utils.classification.mobiles import classify_mobile
from utils.classification.tvs import classify_tv

def classify_product(left, right, category):
    category = (category or "").lower()

    if category == "laptops":
        return classify_laptop(left, right)
    elif category == "mobiles":
        return classify_mobile(left, right)
    elif category == "tvs":
        return classify_tv(left, right)

    return "recommended"
