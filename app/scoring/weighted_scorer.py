"""
Weighted scorer: the single entry point that runs the full pipeline and
produces a final 0-100 ATS score plus a full breakdown for explainability.

This is the file you call from the API layer or the CLI demo script —
everything upstream (parsing, extraction, individual scorers) is plumbing
this function wires together.
"""
from config import Config
from app.parsing.section_extractor import extract_sections
from app.extraction.skill_extractor import skill_gap_analysis
from app.scoring.keyword_score import keyword_score
from app.scoring.semantic_score import semantic_score
from app.scoring.structural_score import structural_score


def compute_ats_score(resume_text: str, jd_text: str) -> dict:
    """
    Run the full hybrid ATS pipeline on raw resume and JD text.

    Returns a dict with:
      - final_score: 0-100
      - breakdown: per-component scores (keyword, semantic, structural)
      - gap_analysis: matched/missing/extra skills
    """
    resume_sections = extract_sections(resume_text)
    jd_sections = extract_sections(jd_text)

    kw = keyword_score(resume_text, jd_text)
    sem = semantic_score(resume_sections, jd_sections)
    struct = structural_score(resume_text, jd_text, resume_sections, jd_sections)
    gaps = skill_gap_analysis(resume_text, jd_text)

    final_0_to_1 = (
        Config.WEIGHT_KEYWORD * kw["score"]
        + Config.WEIGHT_SEMANTIC * sem["score"]
        + Config.WEIGHT_STRUCTURAL * struct["score"]
    )
    final_score = round(final_0_to_1 * 100, 1)

    return {
        "final_score": final_score,
        "breakdown": {
            "keyword": kw,
            "semantic": sem,
            "structural": struct,
            "weights_used": {
                "keyword": Config.WEIGHT_KEYWORD,
                "semantic": Config.WEIGHT_SEMANTIC,
                "structural": Config.WEIGHT_STRUCTURAL,
            },
        },
        "gap_analysis": gaps,
        "resume_sections": resume_sections,
        "jd_sections": jd_sections,
    }
