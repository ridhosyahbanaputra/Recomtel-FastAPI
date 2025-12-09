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

- **URL:** `/recommend/user/{user_id}`
- **Method:** `GET`
- **Description:** Fetches the user's profile from the Supabase database, processes the data through ML models, and returns personalized recommendations.

### 3. Post questions to AI

Recommend quota based on usage

- **URL:** `/chat_query`
- **Method:** `POST`
- **Description:** Endpoint to request AI assistance to request internet quota recommendations based on user input.

### 4. Post images to analyze quota usage

Recommend quota based on image

- **URL:** `/analyze_images`
- **Method:** `POST`
- **Description:** Users can request a quota usage analysis by simply uploading an image and the AI ​​will then recommend an appropriate internet quota.

### 5. Ask AI to make a report

Create usage reports

- **URL:** `/report/user/{user_id}`
- **Method:** `GET`
- **Description:** Ask AI to generate a Usage report and make it a PDF.

---

## 🛠️ Tech Stack

- **Framework:** FastAPI
- **Server:** Uvicorn
- **Language:** Python 3.14+
- **Database ORM:** SQLAlchemy
- **Database:** PostgreSQL (Supabase)
- **Machine Learning:** Scikit-Learn, XGBoost, Pandas, NumPy
-**AI:** GROQ
-**AI:** Google-gemini

---

## 📂 Project Structure

```text
recomtel-fast-api/
├── models/                 # Pre-trained ML models (.pkl files)
├── services/               # Business Logic & External Integrations (NEW)
│   ├── __init__.py         # (Important so this folder is recognized as a package)
│   ├── gemini_vision.py    # AI Vision Logic (Image Analysis)
│   ├── groq_chat.py        # AI Chat Logic (Raw Text)
│   ├── offer_engine.py     # Product Matching Logic (Target Offers)
│   ├── pdf_generator.py    # PDF Report Generation Logic
│   └── data_analysis.py    # (Optional) User Metrics Calculation Logic
├── venv/                   # Virtual Environment
├── db_connection.py        # Database Connection Logic (SQLAlchemy engine)
├── ml_engine.py            # Logic to load and process ML Models (SVD/KNN)
├── routes.py               # Router & API Endpoint Definitions
├── main.py                 # Application Entry Point (FastAPI app & Middleware)
├── requirements.txt        # Python Dependencies List
├── .env                    # Environment Variables (DB URL, API Keys) Not Sending To Github
└── .gitignore              # Files Ignored by Git
```
