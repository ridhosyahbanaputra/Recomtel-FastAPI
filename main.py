from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ml_engine import load_models_startup
from routes import recommendation_router, analysis_router,analysis_chat_router

app = FastAPI(title="Recomtel API")

origins = [
    "http://localhost:3000",
    "https://recomtel.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    load_models_startup()

app.include_router(recommendation_router)

app.include_router(analysis_router)

app.include_router(analysis_chat_router)

@app.get("/")
def root():
    return {"message": "Server is running🚀"}