from fastapi import APIRouter, HTTPException, status, File, UploadFile
from pydantic import BaseModel
from sqlalchemy import text
import pandas as pd
import numpy as np

from db_connection import db_engine
from ml_engine import models
from ai_agent import analyze_images_service
from ai_agent import client as gemini_client


recommendation_router = APIRouter(prefix="/api", tags=["recommendation"])
analysis_router = APIRouter(prefix="/api", tags=["analysis"])
analysis_chat_router = APIRouter(prefix="/api", tags=["chat"])


class QueryBody(BaseModel):
    query: str


TARGET_OFFERS = [
    {"id": 1, "name": "General Offer", "price": 50000, "category": "General",
     "description": "Paket internet standar harian untuk segala kebutuhanmu.",
     "keywords": ["general", "promo default", "standard"]},
    {"id": 2, "name": "Data Booster", "price": 25000, "category": "Booster",
     "description": "Kuota darurat tambahan saat paket utamamu habis.",
     "keywords": ["booster", "data", "extra"]},
    {"id": 3, "name": "Top-up Promo", "price": 100000, "category": "Promo",
     "description": "Bonus ekstra kuota setiap pengisian pulsa nominal tertentu.",
     "keywords": ["top-up", "bonus"]},
    {"id": 4, "name": "Device Upgrade Offer", "price": 100000, "category": "Device",
     "description": "Tukar tambah HP baru dengan harga spesial.",
     "keywords": ["device", "upgrade", "hp"]},
    {"id": 5, "name": "Retention Offer", "price": 20000, "category": "Loyalty",
     "description": "Paket super murah untuk pelanggan setia.",
     "keywords": ["retention", "loyalty", "setia"]},
    {"id": 6, "name": "Roaming Pass", "price": 150000, "category": "Roaming",
     "description": "Internet luar negeri tanpa ganti kartu.",
     "keywords": ["roaming", "travel", "luar negeri"]},
    {"id": 7, "name": "Streaming Partner Pack", "price": 45000, "category": "Streaming",
     "description": "Netflix & Disney+ sepuasnya tanpa potong kuota utama.",
     "keywords": ["streaming", "netflix", "youtube"]},
    {"id": 8, "name": "Family Plan Offer", "price": 200000, "category": "Family",
     "description": "Satu kuota besar untuk dibagi ke keluarga.",
     "keywords": ["family", "keluarga", "sharing"]},
    {"id": 9, "name": "Voice Bundle", "price": 30000, "category": "Voice",
     "description": "Nelpon sepuasnya ke semua operator.",
     "keywords": ["voice", "nelpon", "call"]},
]

def match_offer_from_text(text: str):
    text_lower = text.lower()
    for offer in TARGET_OFFERS:
        keywords = offer.get("keywords", [])
        for key in keywords:
            if key.lower() in text_lower:
                return offer
    return TARGET_OFFERS[0]  

def match_offer_from_keywords(keywords: list):
    if not keywords:
        return TARGET_OFFERS[0]
    for kw in keywords:
        kw_lower = kw.lower()
        for offer in TARGET_OFFERS:
            for key in offer.get("keywords", []):
                if kw_lower in key.lower():
                    return offer
    return TARGET_OFFERS[0]


def svd_score(svd_model, X, offers, le_offer):
    try:
        user_vec = svd_model.transform(X)[0]
    except Exception as e:
        print("SVD Model Transform Error:", e)
        return []

    scores = []
    for offer in offers:
        score = 0.0
        try:
            offer_enc = le_offer.transform([offer])[0]
            offer_vec = np.ones_like(user_vec) * (offer_enc * 0.1)
            score = float(np.dot(user_vec, offer_vec)/(np.linalg.norm(user_vec)+1e-8))
        except Exception:
            score = 0.0
        scores.append((offer, score))
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores


@recommendation_router.get("/recommend/user/{user_id}")
def recommend_by_id(user_id: str):
    query = text("SELECT * FROM public.customers WHERE id = :uid")
    df = pd.read_sql(query, db_engine, params={"uid": user_id})
    if df.empty:
        raise HTTPException(status_code=404, detail="User not found")
    user = df.iloc[0]

    le_device = models.get("le_device")
    le_plan = models.get("le_plan")
    le_offer = models.get("le_offer")
    svd = models.get("svd_model")

    try: plan_enc = le_plan.transform([user["plan_type"]])[0]
    except: plan_enc = 0
    try: device_enc = le_device.transform([user["device_brand"]])[0]
    except: device_enc = 0

    X_full = np.array([[
        plan_enc,
        device_enc,
        float(user["avg_data_usage_gb"]),
        float(user["pct_video_usage"]),
        float(user["avg_call_duration"]),
        float(user["sms_freq"]),
        float(user["monthly_spend"]),
        float(user["topup_freq"]),
        float(user["travel_score"]),
        float(user["complaint_count"]),
    ]])
    X_svd = X_full[:, :9]
    offers = list(le_offer.classes_)
    scores = svd_score(svd, X_svd, offers, le_offer)
    top3 = scores[:3]

    return {
        "user_id": user_id,
        "recommend": [{"package_id": o, "score": s} for o, s in top3],
        "all_scores": [{"package_id": o, "score": s} for o, s in scores]
    }


@analysis_router.post("/analyze_images")
async def analyze_images_route(image: UploadFile = File(...)):
    try:
        print("DEBUG: image filename =", image.filename)
        result = await analyze_images_service(image)

        analysis_text = result.get("analysis", "")
        keywords = result.get("keywords", [])

        matched_offer = match_offer_from_keywords(keywords)

        return {
            "status": "success",
            "analysis": analysis_text,
            "recommendation": matched_offer,
            "offers_available": TARGET_OFFERS
        }

    except ValueError as e:
        print("DEBUG ValueError:", e)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Gagal memproses AI: {e}")


@analysis_chat_router.post("/chat_query")
async def chat_query_route(body: QueryBody):
    try:
        user_text = body.query
        matched = match_offer_from_text(user_text)

        system_instruction = (
            "Anda adalah asisten virtual Recomtel. Jawab singkat, jelas, dan ramah. "
            "Gunakan referensi paket berikut untuk rekomendasi:\n"
            + "\n".join([f"- {o['name']} ({o['category']})" for o in TARGET_OFFERS])
        )

        if not gemini_client:
            raise HTTPException(status_code=503, detail="AI Client not initialized")

        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                f"SYSTEM: {system_instruction}",
                f"USER: {user_text}"
            ]
        )
        reply = getattr(response, "text", str(response))

        return {
            "answer": reply,
            "recommendation": matched,
            "offers_available": TARGET_OFFERS
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Gagal memproses chat: {e}")
