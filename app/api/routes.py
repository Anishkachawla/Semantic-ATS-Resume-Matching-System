"""FastAPI routes for the ATS scoring service."""
import tempfile
import os

from fastapi import APIRouter, File, HTTPException, UploadFile, Form

from app.models.schemas import ScoreTextRequest, ScoreResponse
from app.parsing.document_parser import extract_text
from app.scoring.weighted_scorer import compute_ats_score
from app.explainability.gemini_explainer import generate_explanation

router = APIRouter()


def run_pipeline(resume_text: str, jd_text: str, include_explanation: bool) -> dict:
    result = compute_ats_score(resume_text, jd_text)

    if include_explanation:
        result["explanation"] = generate_explanation(result, resume_text, jd_text)
    else:
        result["explanation"] = None

    return result


SAMPLE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "tests", "sample_data",
)


@router.get("/sample")
def get_sample():
    """Bundled sample resume + JD (powers the 'Load sample' button in the UI)."""
    return {
        "resume_text": extract_text(os.path.join(SAMPLE_DIR, "sample_resume.txt")),
        "jd_text": extract_text(os.path.join(SAMPLE_DIR, "sample_jd.txt")),
    }


@router.post("/score", response_model=ScoreResponse)
async def score_combined(
    resume_file: UploadFile | None = File(default=None),
    resume_text: str = Form(default=""),
    jd_file: UploadFile | None = File(default=None),
    jd_text: str = Form(default=""),
    include_explanation: bool = Form(default=False),
):
    """Used by the React UI: each side can be an uploaded file OR pasted text."""
    try:
        resume = await _resolve(resume_file, resume_text, "resume")
        jd = await _resolve(jd_file, jd_text, "job description")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return run_pipeline(resume, jd, include_explanation)


async def _resolve(upload: UploadFile | None, pasted: str, label: str) -> str:
    if upload is not None and upload.filename:
        return await extract_uploaded_text(upload)
    if pasted and pasted.strip():
        return pasted
    raise ValueError(f"Add a {label}: upload a file or paste the text in.")


@router.post("/score/text", response_model=ScoreResponse)
def score_text(payload: ScoreTextRequest):
    """Score a resume against a JD given as raw text (no file upload)."""
    return run_pipeline(payload.resume_text, payload.jd_text, payload.include_explanation)


@router.post("/score/upload", response_model=ScoreResponse)
async def score_upload(
    resume_file: UploadFile = File(...),
    jd_file: UploadFile = File(...),
    include_explanation: bool = Form(default=False),
):
    """Score a resume against a JD, both uploaded as PDF/DOCX/TXT files."""
    try:
        resume_text = await extract_uploaded_text(resume_file)
        jd_text = await extract_uploaded_text(jd_file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return run_pipeline(resume_text, jd_text, include_explanation)


async def extract_uploaded_text(upload: UploadFile) -> str:
    suffix = os.path.splitext(upload.filename or "")[1].lower()
    content = await upload.read()

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        return extract_text(tmp_path)
    finally:
        os.unlink(tmp_path)