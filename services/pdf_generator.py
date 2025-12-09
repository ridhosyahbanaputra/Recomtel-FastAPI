from fpdf import FPDF
from io import BytesIO

def generate_pdf_report(report_text: str, user_data: dict) -> BytesIO:
    

    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", 'B', 24)
    pdf.cell(0, 15, 'Recomtel Report', ln=True, align='L') 
    
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, 30, 200, 30)
    pdf.ln(10)

    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 8, f"ID User: {user_data.get('id', '-')}", ln=True)
    pdf.ln(5)

    table_data = [
        ("Total Data (30 Hari)", f"{user_data.get('total_data_gb', 0)} GB"),
        ("Video/Streaming", f"{user_data.get('video_pct', 0)}%"),
        ("Durasi Panggilan", f"{user_data.get('call_duration_min', 0)} menit"),
        ("Frekuensi Top-up", f"{user_data.get('topup_freq', 0)} kali"),
        ("Risiko Churn", f"{user_data.get('churn_risk', 'Unknown')}"),
    ]

    label_width = 80
    value_width = 80
    row_height = 8

    pdf.set_font("Helvetica", 'B', 11)
    pdf.set_fill_color(240, 240, 240) # Abu-abu muda
    pdf.cell(label_width, row_height, "Metrik", border=1, fill=True)
    pdf.cell(value_width, row_height, "Nilai", border=1, fill=True)
    pdf.ln(row_height)

    pdf.set_font("Helvetica", '', 11)
    for label, value in table_data:
        pdf.cell(label_width, row_height, str(label), border=1)
        pdf.cell(value_width, row_height, str(value), border=1)
        pdf.ln(row_height)

    pdf.ln(10)

    pdf.set_font("Helvetica", 'B', 14)
    pdf.cell(0, 10, 'Analisis & Rekomendasi AI', ln=True)
    pdf.set_font("Helvetica", '', 11)

    safe_text = report_text.encode('latin-1', 'replace').decode('latin-1')
    safe_text = safe_text.replace("**", "").replace("#", "")
    
    pdf.multi_cell(0, 7, safe_text)

    try:
        pdf_bytes = pdf.output() 
        
        if isinstance(pdf_bytes, str):
            pdf_bytes = pdf_bytes.encode('latin-1')

        buffer = BytesIO(pdf_bytes)
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        print(f"PDF Generation Error: {e}")
        raise Exception("Gagal render PDF bytes")