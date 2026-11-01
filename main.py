"""
FastAPI app entry point.

Run with: uvicorn main:app --reload
Docs at:  http://127.0.0.1:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router

app = FastAPI(
    title="Semantic ATS",
    description="Hybrid keyword + semantic resume-to-job-description matching",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Vite dev server
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1", tags=["scoring"])


@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {
        "message": "Semantic ATS API is running",
        "docs": "/docs",
        "health": "/health"
    }