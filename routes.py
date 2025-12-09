from fastapi import APIRouter, HTTPException, status, File, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import text
import pandas as pd
import numpy as np
from typing import List, Dict, Any 

from db_connection import db_engine
from ml_engine import models

from services.gemini_vision import analyze_image
from services.offer_engine import get_offer_from_category
from services.groq_chat import interpret_text
from services.data_analysis import calculate_usage_metrics
from services.groq_chat import interpret_report_metrics

from services.pdf_generator import generate_pdf_report


recommendation_router = APIRouter(prefix="/api", tags=["recommendation"])
analysis_router = APIRouter(prefix="/api", tags=["analysis"])
analysis_chat_router = APIRouter(prefix="/api", tags=["chat"])


class QueryBody(BaseModel):
    query: str
    user_id: str


TARGET_OFFERS: List[Dict[str, Any]] = [
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

def match_offer_from_keywords(keywords: List[str]):
    if not keywords:
        return TARGET_OFFERS[0]
    for kw in keywords:
        kw_lower = kw.lower()
        for offer in TARGET_OFFERS:
            for key in offer.get("keywords", []):
                if kw_lower in key.lower():
                    return offer
    return TARGET_OFFERS[0]


def svd_score(svd_model: Any, X: np.ndarray, offers: List[str], le_offer: Any) -> List[tuple]:
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
    # Logika SVD
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
    analysis = await analyze_image(image) 
    offer = get_offer_from_category(analysis.dominantCategory)

    return {
        "analysis": analysis.model_dump(),
        "recommendation": offer
    }

@analysis_chat_router.post("/chat_query")
def chat_route(payload: QueryBody):
    user_text = payload.query
    user_text_lower = user_text.lower()
    
    actual_user_id = payload.user_id if payload.user_id else "guest"

    trigger_keywords = [
        "laporan", "buat laporan", "pdf", "cetak laporan", "unduh laporan",
        "laporan kuota", "report kuota", "laporan bulan ini", "download"
    ]
    is_report_request = any(kw in user_text_lower for kw in trigger_keywords)

    if is_report_request:
        download_url = f"/api/report/user/{actual_user_id}" 
        
        return {
            "answer": "Baik, laporan pemakaian data Anda siap. Silakan klik tombol unduh di bawah.",
            "download_url": download_url, 
            "analysis": None,
            "recommendation": None
        }

    result = interpret_text(user_text, available_offers=TARGET_OFFERS)

    return {
        "answer": result,
        "analysis": None,
        "recommendation": None
    }


@analysis_router.get("/report/user/{user_id}")
def generate_usage_report(user_id: str):
    if user_id.lower() == "guest":
        raise HTTPException(status_code=403, detail="Akses ditolak untuk guest")

    query = text("SELECT * FROM public.customers WHERE id = :uid")
    df = pd.read_sql(query, db_engine, params={"uid": user_id})
    
    if df.empty:
        raise HTTPException(status_code=404, detail=f"User ID {user_id} tidak ditemukan")

    user_data = df.iloc[0].to_dict()

    metrics = calculate_usage_metrics(user_data)
    user_data.update(metrics) 

    report_text = interpret_report_metrics(metrics,available_offers=TARGET_OFFERS)
    pdf_buffer = generate_pdf_report(report_text, user_data)
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=laporan_{user_id}.pdf"}
    )