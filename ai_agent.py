import os
from pydantic import BaseModel
from google import genai
from google.genai import types
from fastapi import UploadFile

try:
    client = genai.Client()
except Exception as e:
    print(f"Warning: Gemini client failed to initialize: {e}")
    client = None


class UsageAnalysis(BaseModel):
    totalUsageGB: float
    dominantCategory: str
    recommendationReason: str

TARGET_OFFERS = [
    {"id": 1, "name": "General Offer", "category": "General", "keywords": ["general", "work", "browsing"]},
    {"id": 2, "name": "Data Booster", "category": "Booster", "keywords": ["social", "media", "booster"]},
    {"id": 3, "name": "Top-up Promo", "category": "Promo", "keywords": ["gaming", "promo", "top-up"]},
    {"id": 4, "name": "Device Upgrade Offer", "category": "Device", "keywords": ["device", "upgrade", "hp"]},
    {"id": 5, "name": "Retention Offer", "category": "Loyalty", "keywords": ["retention", "loyalty", "setia"]},
    {"id": 6, "name": "Roaming Pass", "category": "Roaming", "keywords": ["roaming", "travel", "luar negeri"]},
    {"id": 7, "name": "Streaming Partner Pack", "category": "Streaming", "keywords": ["streaming", "netflix", "youtube"]},
    {"id": 8, "name": "Family Plan Offer", "category": "Family", "keywords": ["family", "keluarga", "sharing"]},
    {"id": 9, "name": "Voice Bundle", "category": "Voice", "keywords": ["voice", "nelpon", "call"]},
]

CATEGORY_MAP = {
    "Streaming": "Streaming",
    "Social Media": "Booster",
    "Gaming": "Promo",
    "Browsing/Work": "General",
    "Other": "General",
}

def match_offer_from_text(user_query: str):
    query = user_query.lower()
    best_offer = None
    best_score = 0

    for offer in TARGET_OFFERS:
        score = 0
        for kw in offer.get("keywords", []):
            if kw.lower() in query:
                score += 1
        if offer["category"].lower() in query:
            score += 2
        if score > best_score:
            best_score = score
            best_offer = offer

    if not best_offer:
        best_offer = TARGET_OFFERS[0]
    return best_offer

async def analyze_images_service(image: UploadFile):
    if not client:
        raise ValueError("AI Client is not initialized.")

    image_bytes = await image.read()
    image_part = types.Part.from_bytes(
        data=image_bytes,
        mime_type=image.content_type
    )

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[
            image_part,
            "Analisis screenshot penggunaan data ini dan kembalikan JSON terstruktur."
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=UsageAnalysis,
             temperature=0
        ),
    )


    analysis_data = UsageAnalysis.model_validate_json(response.text)


    dominant_category = analysis_data.dominantCategory
    mapped_category = CATEGORY_MAP.get(dominant_category, "General")
    recommended_offer = next((o for o in TARGET_OFFERS if o["category"] == mapped_category), TARGET_OFFERS[0])

    return {
        "analysis": analysis_data.model_dump(),
        "keywords": [dominant_category],  
        "recommendation": recommended_offer
    }
