from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import fungsi dari file lain
from ml_engine import load_models_startup
from routes import router as recommendation_router

app = FastAPI(title="Recomtel API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Event Startup: Load Model
@app.on_event("startup")
def startup_event():
    load_models_startup()

# Router (Endpoint) dari file routes.py
app.include_router(recommendation_router)

@app.get("/")
def root():
    return {"message": "Server is running🚀"}