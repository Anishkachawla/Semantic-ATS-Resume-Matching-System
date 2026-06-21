"""
Section extraction: splits raw resume/JD text into labeled chunks
(summary, skills, experience, education, other).

This is heuristic by nature — resume formats vary enormously. The approach:
1. Scan line by line for lines that look like section headers (short, often
   ALL CAPS or Title Case, matching a known set of synonyms).
2. Everything between two headers belongs to the section started by the
   first header.
3. Anything before the first detected header goes into "summary".

If you find this misclassifying real resumes, the fix is almost always to
extend SECTION_HEADERS with more synonyms — don't rewrite the algorithm.
"""
import re

# canonical_section -> header phrases that indicate that section is starting
SECTION_HEADERS = {
    "summary": [
        "summary", "professional summary", "profile", "objective",
        "about me", "career objective",
    ],
    "skills": [
        "skills", "technical skills", "core competencies", "competencies",
        "key skills", "areas of expertise", "technologies",
    ],
    "experience": [
        "experience", "work experience", "professional experience",
        "employment history", "work history", "career history",
    ],
    "education": [
        "education", "academic background", "qualifications",
        "educational qualifications",
    ],
    "projects": [
        "projects", "personal projects", "key projects",
    ],
    "certifications": [
        "certifications", "certificates", "licenses",
    ],
}

# Flatten into a single lookup: normalized header text -> canonical section name
_HEADER_LOOKUP = {
    phrase.lower(): section
    for section, phrases in SECTION_HEADERS.items()
    for phrase in phrases
}


def _looks_like_header(line: str) -> str | None:
    """
    Return the canonical section name if `line` looks like a section header,
    else None. A header is a short line whose normalized text matches (or
    closely matches) a known header phrase.
    """
    stripped = line.strip()
    if not stripped or len(stripped) > 40:
        return None

    # Normalize: lowercase, strip trailing colons/punctuation
    normalized = re.sub(r"[:\-–—]+$", "", stripped.lower()).strip()

    if normalized in _HEADER_LOOKUP:
        return _HEADER_LOOKUP[normalized]

    # Loose match: header phrase is the dominant content of the line
    # (handles cases like "SKILLS & TOOLS" or "* Skills *")
    for phrase, section in _HEADER_LOOKUP.items():
        if phrase in normalized and len(normalized) <= len(phrase) + 15:
            return section

    return None


def extract_sections(text: str) -> dict[str, str]:
    """
    Split text into sections. Returns a dict with at least these keys
    (empty string if not found): summary, skills, experience, education,
    projects, certifications, other.
    """
    sections: dict[str, list[str]] = {key: [] for key in SECTION_HEADERS}
    sections["other"] = []

    current_section = "summary"  # default bucket until first header is seen
    seen_any_header = False

    for line in text.splitlines():
        header_match = _looks_like_header(line)
        if header_match:
            current_section = header_match
            seen_any_header = True
            continue  # don't include the header line itself in the body

        # Before any header is found, content goes to summary by default
        target = current_section if seen_any_header or current_section == "summary" else "other"
        sections[target].append(line)

    return {key: "\n".join(lines).strip() for key, lines in sections.items()}
