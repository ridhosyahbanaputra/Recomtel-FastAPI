import os 
from google import genai
from google.genai import types
from fastapi import UploadFile
from pydantic import BaseModel

try:
    gemini_client = genai.Client()
except Exception as e:
    print(f"Warning: Gemini client failed to initialize: {e}")
    gemini_client = None


class UsageAnalysis(BaseModel):
    totalUsageGB: float
    dominantCategory: str
    recommendationReason: str

async def analyze_image(image: UploadFile):
    
    if not gemini_client:
        raise ValueError("AI Client is not initialized. Check GEMINI_API_KEY.")

    image_bytes = await image.read()

    image_part = types.Part.from_bytes(
        data=image_bytes,
        mime_type=image.content_type
    )

    system_instruction = (
            "Anda adalah AI analis data untuk Recomtel. "
            "Selalu berikan hasil analisis Anda dan semua teks deskriptif (termasuk recommendationReason) "
            "SECARA EKSKLUSIF dalam BAHASA INDONESIA FORMAL. "
            "Analisis screenshot penggunaan data ini. Ekstrak data kuota, hitung total, dan tentukan kategori dominan."
        )
        
    response = gemini_client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[
            image_part,
            system_instruction
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=UsageAnalysis,
            temperature=0.1
        ),
    )

    return UsageAnalysis.model_validate_json(response.text)