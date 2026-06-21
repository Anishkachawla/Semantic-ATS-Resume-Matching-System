"""
CLI demo: run the full ATS pipeline on two local files and print the result.

Usage:
    python scripts/run_demo.py
    python scripts/run_demo.py --resume path/to/resume.pdf --jd path/to/jd.txt
    python scripts/run_demo.py --explain   # also calls Gemini for a written explanation

Run from the project root (so `config` and `app` imports resolve):
    cd semantic-ats && python scripts/run_demo.py
"""
import argparse
import json
import os
import sys

# Allow running as `python scripts/run_demo.py` from the project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.parsing.document_parser import extract_text
from app.scoring.weighted_scorer import compute_ats_score


def main():
    parser = argparse.ArgumentParser(description="Run the semantic ATS pipeline on two files.")
    parser.add_argument(
        "--resume", default="tests/sample_data/sample_resume.txt",
        help="Path to resume file (.pdf, .docx, or .txt)",
    )
    parser.add_argument(
        "--jd", default="tests/sample_data/sample_jd.txt",
        help="Path to job description file (.pdf, .docx, or .txt)",
    )
    parser.add_argument(
        "--explain", action="store_true",
        help="Call Gemini to generate a written explanation (requires GEMINI_API_KEY in .env)",
    )
    args = parser.parse_args()

    resume_text = extract_text(args.resume)
    jd_text = extract_text(args.jd)

    result = compute_ats_score(resume_text, jd_text)

    print("\n=== FINAL SCORE ===")
    print(f"{result['final_score']} / 100")

    print("\n=== BREAKDOWN ===")
    print(json.dumps(result["breakdown"], indent=2))

    print("\n=== GAP ANALYSIS ===")
    print(json.dumps(result["gap_analysis"], indent=2))

    if args.explain:
        from app.explainability.gemini_explainer import generate_explanation
        explanation = generate_explanation(result, resume_text, jd_text)
        print("\n=== EXPLANATION (Gemini) ===")
        print(json.dumps(explanation, indent=2))


if __name__ == "__main__":
    main()
