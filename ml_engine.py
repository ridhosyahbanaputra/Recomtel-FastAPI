import joblib
import os
import sys

# Variabel Global penampung model
models = {} 
MODEL_DIR = "models"

def load_models_startup():
    """Memuat semua model .pkl ke memori."""
    expected_files = [
        "clf_model.pkl", "knn_model.pkl", "svd_model.pkl", "scaler.pkl",
        "le_device.pkl", "le_offer.pkl", "le_plan.pkl", "user_item_matrix.pkl"
    ]

    print("Loading ML model...")

    for filename in expected_files:
        filepath = os.path.join(MODEL_DIR, filename)
        if not os.path.exists(filepath):
            print(f"⚠️ WARNING: {filename} not found.")
            continue 

        try:
            with open(filepath, 'rb') as file:
                key = filename.replace(".pkl", "")
                obj = joblib.load(file)
                
                if key == "clf_model":
                    try:
                        obj.use_label_encoder = False
                        obj.gpu_id = -1
                        obj.predictor = "cpu_predictor"
                        obj.sampling_method = "uniform"
                    except: pass

                models[key] = obj
                print(f"   - {filename} OK")
        except Exception as e:
            print(f"Faill load {filename}: {e}")
            
    print("🚀 ML Engine Ready.")