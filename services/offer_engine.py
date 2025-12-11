from typing import List, Dict, Any

TARGET_OFFERS: List[Dict[str, Any]] = [
    {
        "id": 1, 
        "name": "General Offer", 
        "category": "General",
        "description": "Paket internet standar harian untuk segala kebutuhanmu."
    },
    {
        "id": 2, 
        "name": "Data Booster", 
        "category": "Booster",
        "description": "Kuota darurat tambahan saat paket utamamu habis."
    },
    {
        "id": 3, 
        "name": "Top-up Promo", 
        "category": "Promo",
        "description": "Bonus ekstra kuota setiap pengisian pulsa nominal tertentu."
    },
    {
        "id": 4, 
        "name": "Device Upgrade Offer", 
        "category": "Device",
        "description": "Tukar tambah HP baru dengan harga spesial."
    },
    {
        "id": 5, 
        "name": "Retention Offer", 
        "category": "Loyalty",
        "description": "Paket super murah khusus untuk pelanggan setia."
    },
    {
        "id": 6, 
        "name": "Roaming Pass", 
        "category": "Roaming",
        "description": "Internet luar negeri tanpa ganti kartu SIM."
    },
    {
        "id": 7, 
        "name": "Streaming Partner Pack", 
        "category": "Streaming",
        "description": "Akses Netflix, Disney+, & YouTube sepuasnya tanpa potong kuota utama."
    },
    {
        "id": 8, 
        "name": "Family Plan Offer", 
        "category": "Family",
        "description": "Satu kuota besar yang bisa dibagi ke seluruh anggota keluarga."
    },
    {
        "id": 9, 
        "name": "Voice Bundle", 
        "category": "Voice",
        "description": "Paket nelpon sepuasnya ke semua operator."
    },
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
