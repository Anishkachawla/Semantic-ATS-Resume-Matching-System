"""
FastAPI app entry point.

Run with: uvicorn main:app --reload
Docs at:  http://127.0.0.1:8000/docs
"""
from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="Semantic ATS",
    description="Hybrid keyword + semantic resume-to-job-description matching",
    version="0.1.0",
)

app.include_router(router, prefix="/api/v1", tags=["scoring"])


@app.get("/health")
def health():
    return {"status": "ok"}
