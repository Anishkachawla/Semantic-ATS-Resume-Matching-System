"""
Keyword scoring: the "legacy ATS" signal, made slightly smarter.

Two components, combined:
1. Skill coverage — what fraction of the JD's required (taxonomy) skills
   appear in the resume. High precision, but only as good as the taxonomy.
2. Weighted term overlap — what fraction of the JD's *important* terms
   (weighted by how often the JD repeats them) appear anywhere in the
   resume. Catches keyword overlap outside the taxonomy (company-specific
   tools, jargon not yet catalogued).

   Note on BM25: a natural first instinct here is classic BM25 (rank_bm25).
   Don't — BM25's IDF term is defined relative to a *corpus* of documents,
   and with a corpus of one (just the resume), the IDF math degenerates
   (it goes negative for any term that appears in "more than half" of a
   1-document corpus, which is most terms). BM25 only makes sense once you
   have many resumes to compare against each other. For single resume-vs-JD
   comparison, simple log-frequency-weighted term coverage is both more
   robust and more transparent.
"""
import math
import re
from collections import Counter

from config import Config
from app.extraction.skill_extractor import extract_skills

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "is", "are", "was", "were", "be",
    "been", "being", "to", "of", "in", "on", "at", "for", "with", "by",
    "from", "as", "this", "that", "these", "those", "it", "its", "we",
    "you", "your", "our", "will", "shall", "should", "would", "can",
    "could", "may", "might", "must", "have", "has", "had", "do", "does",
    "did", "i", "not", "no",
}


def _tokenize(text: str) -> list[str]:
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9+#./-]*", text.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 1]


def skill_coverage_score(resume_text: str, jd_text: str) -> float:
    """Fraction of JD's required skills present in the resume. Range 0-1."""
    required = extract_skills(jd_text)
    if not required:
        return 1.0  # JD names no extractable skills -> don't penalize on this axis
    present = extract_skills(resume_text)
    return len(required & present) / len(required)


def weighted_term_overlap_score(resume_text: str, jd_text: str) -> float:
    """
    What fraction of the JD's term "weight" is covered by the resume.
    Each JD term is weighted by log(1 + frequency) so repeated/emphasized
    terms count more, then we sum the weight of terms that also appear
    anywhere in the resume, divided by total weight. Range 0-1.
    """
    resume_tokens = set(_tokenize(resume_text))
    jd_tokens = _tokenize(jd_text)

    if not jd_tokens:
        return 0.0

    term_freq = Counter(jd_tokens)
    weights = {term: math.log(1 + count) for term, count in term_freq.items()}
    total_weight = sum(weights.values())

    if total_weight == 0:
        return 0.0

    matched_weight = sum(w for term, w in weights.items() if term in resume_tokens)
    return matched_weight / total_weight


def keyword_score(resume_text: str, jd_text: str) -> dict:
    """Combined keyword score with breakdown for explainability."""
    coverage = skill_coverage_score(resume_text, jd_text)
    term_overlap = weighted_term_overlap_score(resume_text, jd_text)

    combined = (
        Config.KEYWORD_SKILL_COVERAGE_WEIGHT * coverage
        + Config.KEYWORD_BM25_WEIGHT * term_overlap
    )

    return {
        "score": round(combined, 4),
        "skill_coverage": round(coverage, 4),
        "weighted_term_overlap": round(term_overlap, 4),
    }
