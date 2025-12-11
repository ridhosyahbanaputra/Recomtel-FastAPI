def calculate_usage_metrics(user_data):
    metrics = {
        "total_data_gb": round(user_data.get('avg_data_usage_gb', 0) * 30, 2),
        "video_pct": round(user_data.get('pct_video_usage', 0) * 100, 1),
        "call_duration_min": round(user_data.get('avg_call_duration', 0), 1),
        "topup_freq": user_data.get('topup_freq', 0),
    }
    return metrics
