# 📡 Recomtel Recommendation API

This is the backend API for the **Recomtel** project. It serves personalized product recommendations (Data Plans & Devices) based on user usage behavior.

The system uses a **Hybrid Recommendation Engine** combining:

- **XGBoost Classifier** (for targeted offer prediction)
- **KNN (K-Nearest Neighbors)** (for finding similar user profiles)
- **SVD (Singular Value Decomposition)** (for latent feature matching)

Built with **FastAPI** and connected to **Supabase (PostgreSQL)**.

---

## 🔌 API Endpoints

### 1. Health Check

Checks if the server is running and accessible.

- **URL:** `/`
- **Method:** `GET`
- **Description:** Returns a simple JSON message to confirm the API is online.

### 2. Get Recommendation byID

Recommend quota based on usage

- **URL:** `/api/recommend/user/{user_id}`
- **Method:** `GET`
- **Description:** Fetches the user's profile from the Supabase database, processes the data through ML models, and returns personalized recommendations.

### 3. Post questions to AI

Recommend quota based on usage

- **URL:** `/api/chat_query`
- **Method:** `POST`
- **Description:** Endpoint to request AI assistance to request internet quota recommendations based on user input.

### 4. Post images to analyze quota usage

Recommend quota based on image

- **URL:** `/api/analyze_images`
- **Method:** `POST`
- **Description:** Users can request a quota usage analysis by simply uploading an image and the AI ​​will then recommend an appropriate internet quota.
---

## 🛠️ Tech Stack

- **Framework:** FastAPI
- **Server:** Uvicorn
- **Language:** Python 3.14+
- **Database ORM:** SQLAlchemy
- **Database:** PostgreSQL (Supabase)
- **Machine Learning:** Scikit-Learn, XGBoost, Pandas, NumPy
-**AI:** Google-gemini

---

## 📂 Project Structure

```text
recomtel-fast-api/
├── models/             # Pre-trained ML models (.pkl files)
├── database.py         # Database connection logic
├── ml_engine.py        # Logic to load and patch ML models
├── routes.py           # API Endpoints
├── main.py             # Entry point of the application
├── requirements.txt    # List of dependencies
├── .env                # Environment variables (Not uploaded to GitHub)
└── .gitignore          # Files to ignore
```
