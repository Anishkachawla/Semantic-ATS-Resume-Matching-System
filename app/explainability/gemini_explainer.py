"""
Explainability layer: turns the numeric score breakdown into a short
human-readable explanation + actionable resume suggestions, using Gemini.

This is the only place in the pipeline that calls an LLM — everything else
is deterministic so the score itself stays reproducible and auditable.
The LLM only narrates and suggests; it never changes the score.

Uses the unified `google-genai` SDK (`pip install google-genai`).
Model names on Gemini change often — Config.GEMINI_MODEL is the single
place to update it. Check https://ai.google.dev/gemini-api/docs/models
if you hit a 404/model-not-found error.
"""
import json

from google import genai

from config import Config

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        if not Config.GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Add it to your .env file to enable "
                "explanations — the numeric score still works without it."
            )
        _client = genai.Client(api_key=Config.GEMINI_API_KEY)
    return _client


PROMPT_TEMPLATE = """You are an assistant that explains ATS resume-matching results \
to a job applicant. Be specific and constructive, not generic.

JOB DESCRIPTION (excerpt):
{jd_excerpt}

RESUME (excerpt):
{resume_excerpt}

SCORE BREAKDOWN:
- Final score: {final_score}/100
- Keyword/skill match: {keyword_score} (skill coverage: {skill_coverage}, text overlap: {term_overlap})
- Semantic similarity: {semantic_score}
- Structural match (experience/education/title): {structural_score}

MATCHED SKILLS: {matched_skills}
MISSING SKILLS (required by JD, not found in resume): {missing_skills}

Respond ONLY with valid JSON, no markdown fences, no preamble, in this exact shape:
{{
  "summary": "2-3 sentence plain-English explanation of why the resume got this score",
  "strengths": ["short bullet", "short bullet"],
  "gaps": ["short bullet", "short bullet"],
  "suggestions": ["specific, actionable edit the candidate could make", "..."]
}}
"""


def generate_explanation(score_result: dict, resume_text: str, jd_text: str) -> dict:
    """
    Call Gemini to generate an explanation for a score_result produced by
    weighted_scorer.compute_ats_score(). Returns a dict matching the schema
    in PROMPT_TEMPLATE, or a fallback dict if the API call fails.
    """
    breakdown = score_result["breakdown"]
    gaps = score_result["gap_analysis"]

    prompt = PROMPT_TEMPLATE.format(
        jd_excerpt=jd_text[:1500],
        resume_excerpt=resume_text[:1500],
        final_score=score_result["final_score"],
        keyword_score=breakdown["keyword"]["score"],
        skill_coverage=breakdown["keyword"]["skill_coverage"],
        term_overlap=breakdown["keyword"]["weighted_term_overlap"],
        semantic_score=breakdown["semantic"]["score"],
        structural_score=breakdown["structural"]["score"],
        matched_skills=", ".join(gaps["matched_skills"]) or "none",
        missing_skills=", ".join(gaps["missing_skills"]) or "none",
    )

    try:
        client = _get_client()
        response = client.models.generate_content(
            model=Config.GEMINI_MODEL,
            contents=prompt,
        )
        raw_text = response.text.strip()
        # Defensive: strip markdown fences if the model adds them anyway
        if raw_text.startswith("```"):
            raw_text = raw_text.strip("`")
            raw_text = raw_text.split("\n", 1)[-1] if raw_text.lower().startswith("json") else raw_text
        return json.loads(raw_text)

    except Exception as e:  # noqa: BLE001 — explanation is best-effort, never blocks scoring
        return {
            "summary": f"Explanation unavailable ({type(e).__name__}: {e}). The numeric score above is unaffected.",
            "strengths": [],
            "gaps": [],
            "suggestions": [],
        }
