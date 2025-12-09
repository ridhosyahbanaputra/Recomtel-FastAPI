TARGET_OFFERS = [
    {"id": 1, "name": "General Offer", "category": "General"},
    {"id": 2, "name": "Data Booster", "category": "Booster"},
    {"id": 3, "name": "Top-up Promo", "category": "Promo"},
    {"id": 4, "name": "Device Upgrade", "category": "Device"},
    {"id": 5, "name": "Loyalty Retention", "category": "Loyalty"},
    {"id": 6, "name": "Roaming Pass", "category": "Roaming"},
    {"id": 7, "name": "Streaming Pack", "category": "Streaming"},
    {"id": 8, "name": "Family Plan", "category": "Family"},
    {"id": 9, "name": "Voice Bundle", "category": "Voice"},
]

CATEGORY_MAP = {
    "Streaming": "Streaming",
    "Social Media": "Booster",
    "Gaming": "Promo",
    "Browsing/Work": "General",
    "Other": "General",
}

def get_offer_from_category(category: str):
    mapped = CATEGORY_MAP.get(category, "General")
    return next((o for o in TARGET_OFFERS if o["category"] == mapped), TARGET_OFFERS[0])
