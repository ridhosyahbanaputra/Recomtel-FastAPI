def interpret_report_metrics(metrics: dict) -> str:
    """
    Mengubah metrics pengguna menjadi teks laporan singkat.
    """
    user_id = metrics.get('user_id', 'Unknown')
    
    report_lines = [
        f"Laporan Pemakaian Kuota Recomtel",
        f"Pengguna ID: {user_id}",
        "",
        "Berdasarkan data penggunaan, kami memberikan rekomendasi berikut:",
        f"- Tingkatkan kapasitas kuota, karena total data yang digunakan mencapai {metrics.get('total_data', 0)} GB.",
        f"- Perhatikan dominasi aktivitas video/streaming ({metrics.get('pemakaian_video', 0)}%), untuk paket kuota lebih sesuai.",
        f"- Pantau durasi panggilan rata-rata ({metrics.get('durasi_panggilan', 0)} menit/hari) dan frekuensi top-up ({metrics.get('top_up', 0)} kali).",
    ]

    return "\n".join(report_lines)
