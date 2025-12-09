import os
from groq import Groq
from typing import List, Dict

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def interpret_text(text: str, available_offers: List[Dict]) -> str:
    
    offer_list_str = "\n".join([
        f"- **{offer['name']}** ({offer['category']}): {offer['description']}" 
        for offer in available_offers
    ])
    
    system_prompt = f"""
        Anda adalah sales consultant profesional di Recomtel.
        Tugas Anda adalah memahami kebutuhan pengguna, lalu menawarkan paket yang paling cocok secara persuasif namun tetap sopan.

        ATURAN:

            1. Anda HANYA boleh merekomendasikan paket dari daftar di bawah ini.
                DILARANG menyebut, menebak, atau membuat paket lain di luar daftar tersebut.

            2. Jawaban WAJIB dimulai dengan SATU kalimat observasi.
                DILARANG membuat observasi yang tidak relevan.
                Gaya Santai / Gen Z:
                - "Dari vibe yang kamu kasih, kayaknya kamu anaknya sering online banget ya?"
                - "Kayaknya kamu butuh paket yang nggak bikin was-was kuota nih."
                - "Kayaknya kamu tipe yang harus selalu terhubung."
                - "Wah, kayaknya kamu butuh paket yang ‘gas terus’ tanpa takut habis."
                - "Sepertinya kamu butuh paket yang value-nya maksimal banget."

            3. Setelah observasi, Anda WAJIB menawarkan hanya SATU paket.
                Format rekomendasi HARUS seperti ini:
                **Nama Paket**

            4. Jelaskan manfaat paket dalam MAKSIMAL 1–2 kalimat:
                - Ringkas
                - Jelas
                - Fokus pada kebutuhan
                DILARANG menulis paragraf panjang.

            5. Nama paket hanya boleh disebut SATU KALI.
                DILARANG mengulang, menekankan ulang, atau menuliskan ulang nama paket.

            6. Gaya komunikasi:
                - Ramah, profesional, persuasif seperti sales handal.
                - Bahasa Indonesia natural, tidak kaku.
                - Tidak bertele-tele.
                - Tidak menjelaskan hal yang tidak diminta.

            7. Jika pertanyaan pengguna TIDAK relevan dengan layanan:
                - Beri jawaban sopan dan jujur.
                - Arahkan kembali bahwa Anda hanya bisa memberikan rekomendasi paket Recomtel.
                - DILARANG memaksa pengguna membeli paket.

            8. DILARANG memunculkan informasi palsu, estimasi liar, asumsi berlebihan, atau analisis yang tidak relevan.

            DAFTAR PAKET YANG BOLEH DIREKOMENDASIKAN:
            ---
            {offer_list_str}
            ---
            Tujuan Anda: memberikan rekomendasi paling tepat, sopan, cepat, dan akurat
"""


    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant", 
        messages=[
            {"role": "system", "content": system_prompt}, 
            {"role": "user", "content": text}
        ],
        temperature=0.4 
    )
    
    return response.choices[0].message.content

def interpret_report_metrics(metrics: dict, available_offers: List[Dict]) -> str:
    
    offers_str = "\n".join([
        f"- {o['name']} (Kategori: {o['category']}, Harga: {o['price']})" 
        for o in available_offers
    ])

    data_str = (
        f"Total Data: {metrics.get('total_data_gb', 0)} GB.\n"
        f"Video/Streaming: {metrics.get('video_pct', 0)} %.\n"
        f"Durasi Panggilan: {metrics.get('call_duration_min', 0)} menit.\n"
        f"Frekuensi Top-up: {metrics.get('topup_freq', 0)} kali.\n"
        f"Risiko Churn: {metrics.get('churn_risk', 'Unknown')}."
    )
    
    system_prompt = (
        "Anda adalah Konsultan Telekomunikasi Recomtel. Tugas Anda memberikan wawasan berdasarkan data."
        
        "\n\nATURAN KRITIS (WAJIB DIPATUHI):"
        "1. Pada bagian 'Rekomendasi Paket', Anda HANYA BOLEH menyarankan paket dari DAFTAR DI BAWAH INI."
        "2. DILARANG KERAS mengarang nama paket sendiri (seperti 'Hiburan Plus', dll)."
        "3. Pilih 1 paket dari daftar yang paling relevan dengan data user (misal: Streaming tinggi -> Streaming Pack)."
        
        f"\n\nDAFTAR PAKET TERSEDIA (HANYA PILIH DARI SINI):\n{offers_str}"
        
        "\n\nFORMAT OUTPUT:"
        "**Analisis Perilaku:** (Jelaskan gaya hidup digital user dalam 3 kalimat)"
        "**Rekomendasi Paket:** (Sebutkan nama paket dari daftar di atas dan alasan kenapa cocok)"
    )
    
    user_prompt = f"Data Pemakaian User:\n{data_str}\n\nBerikan analisis dan rekomendasi produk yang tepat."

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        return "Gagal memuat analisis AI."