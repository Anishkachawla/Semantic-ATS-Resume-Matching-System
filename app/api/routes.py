"""FastAPI routes for the ATS scoring service."""
import tempfile
import os

from fastapi import APIRouter, File, HTTPException, UploadFile, Form

from app.models.schemas import ScoreTextRequest, ScoreResponse
from app.parsing.document_parser import extract_text
from app.scoring.weighted_scorer import compute_ats_score
from app.explainability.gemini_explainer import generate_explanation

router = APIRouter()


def _run_pipeline(resume_text: str, jd_text: str, include_explanation: bool) -> dict:
    result = compute_ats_score(resume_text, jd_text)

    if include_explanation:
        result["explanation"] = generate_explanation(result, resume_text, jd_text)
    else:
        result["explanation"] = None

    return result


@router.post("/score/text", response_model=ScoreResponse)
def score_text(payload: ScoreTextRequest):
    """Score a resume against a JD given as raw text (no file upload)."""
    return _run_pipeline(payload.resume_text, payload.jd_text, payload.include_explanation)


@router.post("/score/upload", response_model=ScoreResponse)
async def score_upload(
    resume_file: UploadFile = File(...),
    jd_file: UploadFile = File(...),
    include_explanation: bool = Form(default=False),
):
    """Score a resume against a JD, both uploaded as PDF/DOCX/TXT files."""
    try:
        resume_text = await _extract_uploaded_text(resume_file)
        jd_text = await _extract_uploaded_text(jd_file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return _run_pipeline(resume_text, jd_text, include_explanation)


async def _extract_uploaded_text(upload: UploadFile) -> str:
    suffix = os.path.splitext(upload.filename or "")[1].lower()
    content = await upload.read()

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        return extract_text(tmp_path)
    finally:
        os.unlink(tmp_path)
