"""Pydantic models for the FastAPI layer."""
from pydantic import BaseModel, Field


class ScoreTextRequest(BaseModel):
    resume_text: str = Field(..., min_length=1)
    jd_text: str = Field(..., min_length=1)
    include_explanation: bool = Field(
        default=False,
        description="If true, calls Gemini to generate a natural-language explanation. "
                    "Adds latency + API cost; keep false for batch scoring.",
    )


class KeywordBreakdown(BaseModel):
    score: float
    skill_coverage: float
    weighted_term_overlap: float


class SemanticBreakdown(BaseModel):
    score: float
    section_scores: dict[str, float]


class StructuralBreakdown(BaseModel):
    score: float
    years_of_experience: dict
    education: dict
    title_similarity: dict


class GapAnalysis(BaseModel):
    required_skills: list[str]
    matched_skills: list[str]
    missing_skills: list[str]
    extra_skills: list[str]


class Explanation(BaseModel):
    summary: str
    strengths: list[str]
    gaps: list[str]
    suggestions: list[str]


class ScoreResponse(BaseModel):
    final_score: float
    breakdown: dict
    gap_analysis: GapAnalysis
    explanation: Explanation | None = None
