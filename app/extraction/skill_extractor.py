"""
Skill extraction: maps free-text resume/JD content onto a canonical set of
skills, using the taxonomy in data/skills_taxonomy.json plus fuzzy matching
(via rapidfuzz) to catch near-misses like "Scikit Learn" vs "scikit-learn".

This is intentionally dictionary-driven rather than a trained NER model:
it's transparent, easy to extend (just edit the JSON), and doesn't require
labeled training data. If you outgrow it, the natural next step is a
spaCy EntityRuler seeded from this same taxonomy, or a fine-tuned NER model —
but start here; a well-maintained taxonomy beats a mediocre trained model.
"""
import json
import re
from functools import lru_cache

from rapidfuzz import fuzz, process

from config import Config


@lru_cache(maxsize=1)
def load_taxonomy() -> dict[str, list[str]]:
    with open(Config.SKILLS_TAXONOMY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _build_alias_index() -> dict[str, str]:
    """alias (lowercase) -> canonical skill name"""
    taxonomy = load_taxonomy()
    index = {}
    for canonical, aliases in taxonomy.items():
        index[canonical.lower()] = canonical
        for alias in aliases:
            index[alias.lower()] = canonical
    return index


def _candidate_phrases(text: str) -> set[str]:
    """
    Generate candidate 1-3 word phrases from text to test against the taxonomy.
    Cheap substitute for full noun-phrase chunking.
    """
    # Strip punctuation except +, #, ., / which appear inside real skill names
    # (C++, C#, Node.js, CI/CD)
    cleaned = re.sub(r"[^\w\s+#./-]", " ", text.lower())
    tokens = cleaned.split()

    phrases = set()
    for n in (1, 2, 3):
        for i in range(len(tokens) - n + 1):
            phrases.add(" ".join(tokens[i:i + n]))
    return phrases


def extract_skills(text: str, fuzzy_threshold: int | None = None) -> set[str]:
    """
    Return the set of canonical skills found in `text`.
    Combines exact alias matching with fuzzy matching for near-misses.
    """
    threshold = fuzzy_threshold or Config.SKILL_FUZZY_THRESHOLD
    alias_index = _build_alias_index()
    aliases = list(alias_index.keys())

    found: set[str] = set()
    candidates = _candidate_phrases(text)

    for phrase in candidates:
        # Exact match first (cheap, precise)
        if phrase in alias_index:
            found.add(alias_index[phrase])
            continue

        # Fuzzy fallback for near-misses (e.g. typos, minor formatting diffs)
        match = process.extractOne(
            phrase, aliases, scorer=fuzz.ratio, score_cutoff=threshold
        )
        if match:
            matched_alias, score, _ = match
            found.add(alias_index[matched_alias])

    return found


def skill_gap_analysis(resume_text: str, jd_text: str) -> dict[str, list[str]]:
    """
    Compare skills found in the resume against skills required by the JD.
    Returns matched / missing skill lists — this is the core of the
    explainability layer.
    """
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)

    matched = sorted(resume_skills & jd_skills)
    missing = sorted(jd_skills - resume_skills)
    extra = sorted(resume_skills - jd_skills)

    return {
        "required_skills": sorted(jd_skills),
        "matched_skills": matched,
        "missing_skills": missing,
        "extra_skills": extra,  # skills on the resume not asked for — not a problem, just informational
    }
