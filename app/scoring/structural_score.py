"""
Structural scoring: the "hard requirements" that keyword/semantic matching
handle poorly — years of experience, education level, job title alignment.
These are cheap to compute and surprisingly high-signal for filtering.
"""
import re

from rapidfuzz import fuzz

EDUCATION_LEVELS = {
    "phd": 5, "doctorate": 5, "ph.d": 5,
    "master": 4, "msc": 4, "m.s.": 4, "mba": 4, "m.tech": 4,
    "bachelor": 3, "bsc": 3, "b.s.": 3, "b.tech": 3, "be": 3, "undergraduate": 3,
    "associate": 2, "diploma": 2,
    "high school": 1,
}


def _max_years_mentioned(text: str) -> int:
    """Find the largest 'N years' figure mentioned in the text."""
    matches = re.findall(r"(\d+)\+?\s*(?:years|yrs)", text.lower())
    years = [int(m) for m in matches]
    return max(years) if years else 0


def years_of_experience_score(resume_text: str, jd_text: str) -> dict:
    """
    Compare years of experience claimed in the resume against years
    required by the JD. Score is 1.0 if resume meets or exceeds requirement,
    scaled down proportionally if it falls short, 1.0 if JD specifies no requirement.
    """
    required_years = _max_years_mentioned(jd_text)
    resume_years = _max_years_mentioned(resume_text)

    if required_years == 0:
        return {"score": 1.0, "required_years": 0, "resume_years": resume_years}

    score = min(resume_years / required_years, 1.0)
    return {
        "score": round(score, 4),
        "required_years": required_years,
        "resume_years": resume_years,
    }


def _highest_education_level(text: str) -> int:
    text_lower = text.lower()
    levels_found = [
        level for keyword, level in EDUCATION_LEVELS.items() if keyword in text_lower
    ]
    return max(levels_found) if levels_found else 0


def education_score(resume_text: str, jd_text: str) -> dict:
    """
    Score is 1.0 if resume's highest education level meets or exceeds the
    level implied by the JD, scaled down if it falls short, 1.0 if the JD
    doesn't mention education requirements at all.
    """
    required_level = _highest_education_level(jd_text)
    resume_level = _highest_education_level(resume_text)

    if required_level == 0:
        return {"score": 1.0, "required_level": 0, "resume_level": resume_level}

    score = min(resume_level / required_level, 1.0)
    return {
        "score": round(score, 4),
        "required_level": required_level,
        "resume_level": resume_level,
    }


def _first_nonempty_line(text: str) -> str:
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return ""


def title_similarity_score(resume_sections: dict, jd_sections: dict) -> dict:
    """
    Fuzzy-match the JD's likely title (first line of its summary, often the
    job title in practice) against the resume's most recent role (first
    line of its experience section). This is a weak heuristic — treat it as
    a minor signal, not a hard filter.
    """
    jd_title_line = _first_nonempty_line(
        jd_sections.get("summary", "") or jd_sections.get("other", "")
    )
    resume_title_line = _first_nonempty_line(resume_sections.get("experience", ""))

    if not jd_title_line or not resume_title_line:
        return {"score": 0.5, "note": "insufficient text to compare titles"}  # neutral, not penalizing

    ratio = fuzz.token_set_ratio(jd_title_line, resume_title_line) / 100.0
    return {"score": round(ratio, 4)}


def structural_score(
    resume_text: str, jd_text: str, resume_sections: dict, jd_sections: dict
) -> dict:
    """Combine structural sub-signals into a single score with breakdown."""
    years = years_of_experience_score(resume_text, jd_text)
    education = education_score(resume_text, jd_text)
    title = title_similarity_score(resume_sections, jd_sections)

    # Equal weight across the three sub-signals by default — adjust if one
    # matters more for your use case (e.g. drop title matching for career-changers)
    combined = (years["score"] + education["score"] + title["score"]) / 3

    return {
        "score": round(combined, 4),
        "years_of_experience": years,
        "education": education,
        "title_similarity": title,
    }
