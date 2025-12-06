from fastapi import APIRouter, HTTPException
from sqlalchemy import text
import pandas as pd
import numpy as np

from db_connection import db_engine
from ml_engine import models

# Kita pakai APIRouter, bukan FastAPI app langsung
router = APIRouter()

@router.get("/api/recommend/user/{user_id}")
def recommend_by_id(user_id: str):
    
    if not db_engine:
        raise HTTPException(status_code=500, detail="Database not connected yet.")

    query = text("SELECT * FROM public.customers WHERE id = :uid")
    
    try:
        df = pd.read_sql(query, db_engine, params={"uid": user_id})
        if df.empty:
            raise HTTPException(status_code=404, detail="User ID not found.")
        user_data = df.iloc[0]
    except Exception as e:
        print(f"DB Error: {e}")
        raise HTTPException(status_code=500, detail="Database Error.")

    try:
        le_device = models.get('le_device')
        le_plan = models.get('le_plan')
        
        if not le_device or not le_plan:
             raise HTTPException(status_code=503, detail="ML model has not been loaded.")

        plan_raw = str(user_data['plan_type']).strip()
        device_raw = str(user_data['device_brand']).strip()
        
        # Safe Transform
        try: plan_enc = le_plan.transform([plan_raw])[0]
        except: plan_enc = 0
            
        try: device_enc = le_device.transform([device_raw])[0]
        except: device_enc = 0

        # Susun 10 Fitur (Sesuai Training)
        features = [
            plan_enc, device_enc,
            float(user_data['avg_data_usage_gb']),
            float(user_data['pct_video_usage']),
            float(user_data['avg_call_duration']),
            float(user_data['sms_freq']),
            float(user_data['monthly_spend']),
            float(user_data['topup_freq']),
            float(user_data['travel_score']),
            float(user_data['complaint_count'])
        ]
        X_final = np.array([features])

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing Error: {e}")

    results = {}
    
    clf = models.get('clf_model')
    le_offer = models.get('le_offer')
    if clf and le_offer:
        try:
            pred = clf.predict(X_final)[0]
            results["classification_offer"] = le_offer.inverse_transform([pred])[0]
        except: results["classification_offer"] = "Promo Default"

    # KNN
    knn = models.get('knn_model')
    user_matrix = models.get('user_item_matrix')
    if knn:
        try:
            X_knn = X_final[:, :8] # Slicing 8 fitur
            distances, indices = knn.kneighbors(X_knn)
            idx = indices[0][0]
            if isinstance(user_matrix, pd.DataFrame):
                results["knn_offer"] = f"Similar to: {user_matrix.index[idx]}"
            else:
                results["knn_offer"] = f"Similar Index: {idx}"
        except: results["knn_offer"] = "General Offer"

    # SVD
    svd = models.get('svd_model')
    if svd and le_offer:
        try:
            X_svd = X_final[:, :9] # Slicing 9 fitur
            matrix = svd.transform(X_svd)
            best = np.argmax(matrix)
            safe = best % len(le_offer.classes_)
            results["svd_offer"] = le_offer.inverse_transform([safe])[0]
        except: results["svd_offer"] = "Special Deal"

    return {
        "user_id": user_id,
        "source": "Live Supabase",
        "profile": { "device": device_raw, "usage": user_data['avg_data_usage_gb'] },
        "recommendations": [
        {"type": "classification_offer", "offer": results.get("classification_offer")},
        {"type": "knn_offer", "offer": results.get("knn_offer")},
        {"type": "svd_offer", "offer": results.get("svd_offer")},
    ]
    }