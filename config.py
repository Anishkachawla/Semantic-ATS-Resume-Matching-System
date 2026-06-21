"""
Central configuration for the semantic ATS project.
All tunable values live here so scoring behavior can be adjusted without
touching pipeline code.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # --- Gemini ---
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # --- Embeddings ---
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-mpnet-base-v2")

    # --- Scoring weights (must sum to 1.0) ---
    WEIGHT_KEYWORD: float = float(os.getenv("SCORE_WEIGHT_KEYWORD", "0.35"))
    WEIGHT_SEMANTIC: float = float(os.getenv("SCORE_WEIGHT_SEMANTIC", "0.45"))
    WEIGHT_STRUCTURAL: float = float(os.getenv("SCORE_WEIGHT_STRUCTURAL", "0.20"))

    # --- Within keyword score: skill-coverage vs raw BM25 text overlap ---
    KEYWORD_SKILL_COVERAGE_WEIGHT: float = 0.6
    KEYWORD_BM25_WEIGHT: float = 0.4

    # --- Within semantic score: per-section weights ---
    SEMANTIC_SECTION_WEIGHTS: dict = {
        "skills": 0.35,
        "experience": 0.45,
        "summary": 0.20,
    }

    # --- Fuzzy matching threshold for skill extraction (0-100, rapidfuzz scale) ---
    SKILL_FUZZY_THRESHOLD: int = 85

    # --- Paths ---
    SKILLS_TAXONOMY_PATH: str = os.getenv(
        "SKILLS_TAXONOMY_PATH", os.path.join("data", "skills_taxonomy.json")
    )

    @classmethod
    def validate_weights(cls) -> None:
        total = cls.WEIGHT_KEYWORD + cls.WEIGHT_SEMANTIC + cls.WEIGHT_STRUCTURAL
        if abs(total - 1.0) > 1e-6:
            raise ValueError(
                f"Scoring weights must sum to 1.0, got {total:.3f} "
                f"(keyword={cls.WEIGHT_KEYWORD}, semantic={cls.WEIGHT_SEMANTIC}, "
                f"structural={cls.WEIGHT_STRUCTURAL})"
            )


Config.validate_weights()
