import joblib
import os

models = {} 
MODEL_DIR = "models"

def load_models_startup():
    expected_files = [
        "clf_model.pkl", "knn_model.pkl", "svd_model.pkl", "scaler.pkl",
        "le_device.pkl", "le_offer.pkl", "le_plan.pkl", 
        "user_item_matrix.pkl", "feature_list.pkl" 
    ]

    print("Loading ML models...")
    for filename in expected_files:
        filepath = os.path.join(MODEL_DIR, filename)
        if not os.path.exists(filepath):
            print(f"WARNING: {filename} missing.")
            continue 

        try:
            with open(filepath, 'rb') as file:
                key = filename.replace(".pkl", "")
                models[key] = joblib.load(file)
                print(f"   - {filename} OK")
        except Exception as e:
            print(f"Failed load {filename}: {e}")
            
    print("ML Engine Ready.")