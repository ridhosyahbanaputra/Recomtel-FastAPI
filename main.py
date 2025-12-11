from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ml_engine import load_models_startup
from routers import recommendation, analysis, chat

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

app.include_router(recommendation.router)

app.include_router(analysis.router)

app.include_router(chat.router)

@app.get("/")
def root():
    return {"Server is running"}