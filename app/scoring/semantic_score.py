"""
Semantic scoring: embeds resume and JD sections separately and compares
them section-to-section (skills-to-skills, experience-to-responsibilities,
etc) rather than embedding whole documents.

Whole-document embedding similarity is the most common mistake in "AI ATS"
projects — it scores resumes high just for being topically adjacent
(e.g. a Data Analyst resume against a Data Scientist JD). Section-wise
comparison is more precise because it forces like-for-like comparison.

The model loads once per process (module-level singleton) since loading
a sentence-transformer is expensive — don't reload it per request.
"""
from functools import lru_cache

from sentence_transformers import SentenceTransformer, util

from config import Config


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(Config.EMBEDDING_MODEL)


def _cosine_sim(text_a: str, text_b: str) -> float:
    if not text_a.strip() or not text_b.strip():
        return 0.0
    model = get_embedding_model()
    embeddings = model.encode([text_a, text_b], convert_to_tensor=True)
    sim = util.cos_sim(embeddings[0], embeddings[1]).item()
    # cosine similarity is in [-1, 1]; clip negatives to 0 since they're
    # not meaningful here (resume/JD text is never "opposite" in any useful sense)
    return max(0.0, min(sim, 1.0))


def semantic_score(resume_sections: dict, jd_sections: dict) -> dict:
    """
    Compare resume and JD section-by-section using the weights in
    Config.SEMANTIC_SECTION_WEIGHTS. JD's "experience" section is compared
    against the JD's responsibilities — in practice the JD's "summary"
    section often contains the actual role responsibilities, so we fall
    back to summary if experience is empty on the JD side.
    """
    weights = Config.SEMANTIC_SECTION_WEIGHTS
    section_scores = {}

    for section, weight in weights.items():
        resume_text = resume_sections.get(section, "")
        jd_text = jd_sections.get(section, "")

        # JDs rarely have a literal "experience" section — they describe
        # responsibilities in summary/other. Fall back gracefully.
        if section == "experience" and not jd_text.strip():
            jd_text = jd_sections.get("summary", "") or jd_sections.get("other", "")

        section_scores[section] = round(_cosine_sim(resume_text, jd_text), 4)

    total_weight = sum(weights.values())
    combined = sum(section_scores[s] * weights[s] for s in weights) / total_weight

    return {
        "score": round(combined, 4),
        "section_scores": section_scores,
    }
