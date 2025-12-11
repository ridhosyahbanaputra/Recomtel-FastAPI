from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import text
import pandas as pd

# Import Services
from services.gemini_vision import analyze_image
from services.offer_engine import get_offer_from_category, TARGET_OFFERS
from services.data_analysis import calculate_usage_metrics
from services.groq_chat import interpret_report_metrics
from services.pdf_generator import generate_pdf_report
from db_connection import db_engine

router = APIRouter(prefix="/api", tags=["Analysis"])

@router.post("/analyze_images")
async def analyze_images_route(image: UploadFile = File(...)): 
    analysis = await analyze_image(image) 
    
    offer = get_offer_from_category(analysis.dominantCategory)

    return {
        "analysis": analysis.model_dump(),
        "recommendation": offer
    }

@router.get("/report/user/{user_id}")
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

    report_text = interpret_report_metrics(metrics, available_offers=TARGET_OFFERS)
    pdf_buffer = generate_pdf_report(report_text, user_data)
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=laporan_{user_id}.pdf"}
    )