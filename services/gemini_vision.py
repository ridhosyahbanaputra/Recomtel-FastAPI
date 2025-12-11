import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from fastapi import UploadFile
from pydantic import BaseModel

try:
    from services.offer_engine import TARGET_OFFERS
except ImportError:
    TARGET_OFFERS = [{"name": "General Offer", "category": "General"}]

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

try:
    if not API_KEY:
        print("Warning: GEMINI_API_KEY not found.")
        gemini_client = None
    else:
        gemini_client = genai.Client(api_key=API_KEY)
except Exception as e:
    print(f"Warning: Gemini init failed: {e}")
    gemini_client = None

offers_text_list = [f"- {o['name']} (Fokus: {o['category']})" for o in TARGET_OFFERS]
OFFERS_CONTEXT_STRING = "\n".join(offers_text_list)


class UsageAnalysis(BaseModel):
    totalUsageGB: float
    dominantCategory: str
    recommendationReason: str  

async def analyze_image(image: UploadFile):
    if not gemini_client:
        raise ValueError("AI Client error. Check API Key.")

    image_bytes = await image.read()

    system_instruction = f"""
    Bertindaklah sebagai AI Analis Data untuk Provider Seluler "RecomTel".
    
    TUGAS UTAMA:
    1. Analisis gambar screenshot penggunaan data aplikasi (App Usage).
    2. Identifikasi total kuota yang terpakai (Total Usage).
    3. Tentukan kategori aplikasi yang paling boros (Streaming, Social, Gaming, dll).
    4. Berikan rekomendasi paket yang TEPAT dari daftar di bawah ini.
    
    DAFTAR PAKET TERSEDIA (Pilih Salah Satu):
    {OFFERS_CONTEXT_STRING}

    ATURAN OUTPUT:
    - totalUsageGB: Ambil angka total GB (float).
    - dominantCategory: Kategori aplikasi terboros.
    - recommendationReason: Jelaskan analisis singkat, lalu sebutkan nama paket yang Anda sarankan.
    Format: "Terlihat penggunaan dominan di [Aplikasi/Kategori]. Kami menyarankan [Nama Paket] karena paket ini cocok untuk kategori [Kategori Paket]."
    
    Gunakan Bahasa Indonesia Formal.
    """

    try:
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=system_instruction),
                        types.Part.from_bytes(data=image_bytes, mime_type=image.content_type),
                    ]
                )
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=UsageAnalysis,
                temperature=0.2 
            ),
        )

        if response.parsed:
            return response.parsed
        else:
            return UsageAnalysis.model_validate_json(response.text)

    except Exception as e:
        print(f"Gemini Error: {e}")
        return UsageAnalysis(
            totalUsageGB=0.0,
            dominantCategory="General",
            recommendationReason=f"Gagal analisis: {str(e)}. Rekomendasi: General Offer."
        )