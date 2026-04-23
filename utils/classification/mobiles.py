from utils.classification.helpers import same_brand

def classify_mobile(left, right):
    return "similar" if same_brand(left, right) else "recommended"
