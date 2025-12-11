from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

# Import Services
from services.groq_chat import interpret_text
from services.offer_engine import TARGET_OFFERS

router = APIRouter(prefix="/api", tags=["Chat"])

class QueryBody(BaseModel):
    query: str
    user_id: Optional[str] = None

@router.post("/chat_query")
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