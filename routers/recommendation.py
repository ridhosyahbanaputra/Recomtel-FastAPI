from fastapi import APIRouter, HTTPException
from sqlalchemy import text
import pandas as pd
import numpy as np

from db_connection import db_engine
from ml_engine import models

router = APIRouter(prefix="/api", tags=["Recommendation"])

def safe_transform(encoder, value):
    try:
        return encoder.transform([value])[0]
    except:
        return 0

@router.get("/recommend/user/{user_id}")
def recommend_by_id(user_id: str):
    query = text("SELECT * FROM public.customers WHERE id = :uid")
    df_db = pd.read_sql(query, db_engine, params={"uid": user_id})
    if df_db.empty:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_data = df_db.copy()

    try:
        svd = models.get("svd_model")
        knn = models.get("knn_model")
        clf = models.get("clf_model")
        scaler = models.get("scaler")
        le_offer = models.get("le_offer")
        le_plan = models.get("le_plan")
        le_device = models.get("le_device")
        user_item = models.get("user_item_matrix")
        features = models.get("feature_list")
        
        if features is None:
            raise HTTPException(status_code=500, detail="Feature list not loaded")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model error: {str(e)}")

    new_data['plan_type_encoded'] = safe_transform(le_plan, new_data['plan_type'].iloc[0])
    new_data['device_brand_encoded'] = safe_transform(le_device, new_data['device_brand'].iloc[0])

    cf_scores = []
    
    if user_id in user_item.index:
        try:
            user_vector = user_item.loc[[user_id]]
            user_emb = svd.transform(user_vector)
            _, idx = knn.kneighbors(user_emb)
            neighbor_indices = idx[0]
            neighbor_ratings = user_item.iloc[neighbor_indices].mean(axis=0)
            max_rating = neighbor_ratings.max()
            cf_scores = neighbor_ratings / (max_rating if max_rating > 0 else 1.0)
            cf_scores = cf_scores.values
        except Exception as e:
            print(f"CF Error: {e}, fallback to mean.")
            cf_scores = user_item.mean().values
            cf_scores = cf_scores / cf_scores.max()
    else:
        cf_scores = user_item.mean().values
        cf_scores = cf_scores / (cf_scores.max() if cf_scores.max() > 0 else 1.0)

    new_data['cf_similarity'] = cf_scores.mean()

    try:
        X_input_df = pd.DataFrame([new_data.iloc[0]])
        for col in features:
            if col not in X_input_df.columns:
                X_input_df[col] = 0
        X_input_df = X_input_df[features] 

        X_scaled = scaler.transform(X_input_df)
        clf_proba = clf.predict_proba(X_scaled)[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification Error: {str(e)}")

    alpha = 0.75
    min_len = min(len(clf_proba), len(cf_scores))
    hybrid_scores = alpha * clf_proba[:min_len] + (1 - alpha) * cf_scores[:min_len]

    top_n = 3
    top_idx = np.argsort(hybrid_scores)[::-1][:top_n]
    top_packages = le_offer.inverse_transform(top_idx)
    top_scores = hybrid_scores[top_idx]

    recommendations = []
    for pkg, score in zip(top_packages, top_scores):
        recommendations.append({
            "package_id": pkg,
            "score": round(float(score), 6) 
        })

    return {
        "user_id": user_id,
        "recommend": recommendations,
    }