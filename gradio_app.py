import os
import gradio as gr

from app.parsing.document_parser import extract_text
from app.scoring.weighted_scorer import compute_ats_score
from app.explainability.gemini_explainer import generate_explanation

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SAMPLE_RESUME = os.path.join(PROJECT_ROOT, "tests", "sample_data", "sample_resume.txt")
SAMPLE_JD = os.path.join(PROJECT_ROOT, "tests", "sample_data", "sample_jd.txt")

def _resolve_text(file_path: str | None, pasted_text: str, label: str) -> str:
    if file_path:
        return extract_text(file_path)
    if pasted_text and pasted_text.strip():
        return pasted_text
    raise gr.Error(f"Add a {label} — upload a file or paste the text in.")


def _score_badge_html(score: float) -> str:
    if score >= 75:
        color, bg, label = "#15803d", "#dcfce7", "Strong match"
    elif score >= 50:
        color, bg, label = "#b45309", "#fef3c7", "Partial match"
    else:
        color, bg, label = "#b91c1c", "#fee2e2", "Weak match"

    return f"""
    <div style="text-align:center; padding:20px 0 8px;">
      <div style="font-size:52px; font-weight:700; color:{color}; line-height:1;">{score:.1f}</div>
      <div style="font-size:13px; color:#64748b; margin-top:2px;">out of 100</div>
      <div style="display:inline-block; margin-top:10px; padding:4px 14px; border-radius:999px;
                  background:{bg}; color:{color}; font-weight:600; font-size:13px;">{label}</div>
    </div>
    """


def _breakdown_html(breakdown: dict) -> str:
    rows = [
        ("Keyword match", breakdown["keyword"]["score"], breakdown["weights_used"]["keyword"], "#6366f1"),
        ("Semantic similarity", breakdown["semantic"]["score"], breakdown["weights_used"]["semantic"], "#0ea5e9"),
        ("Structural fit", breakdown["structural"]["score"], breakdown["weights_used"]["structural"], "#8b5cf6"),
    ]
    bars = ""
    for label, score, weight, color in rows:
        pct = round(score * 100)
        bars += f"""
        <div style="margin-bottom:12px;">
          <div style="display:flex; justify-content:space-between; font-size:13px; color:#334155; margin-bottom:4px;">
            <span>{label} <span style="color:#94a3b8;">(weight {weight:.0%})</span></span>
            <span style="font-weight:600;">{pct}%</span>
          </div>
          <div style="background:#e2e8f0; border-radius:6px; height:8px; overflow:hidden;">
            <div style="width:{pct}%; background:{color}; height:100%; border-radius:6px;"></div>
          </div>
        </div>
        """
    return bars


def _chips_html(skills: list, color: str, bg: str) -> str:
    if not skills:
        return '<span style="color:#94a3b8; font-size:13px;">None</span>'
    spans = "".join(
        f'<span style="display:inline-block; margin:3px; padding:4px 10px; border-radius:999px; '
        f'background:{bg}; color:{color}; font-size:12px; font-weight:500;">{s}</span>'
        for s in skills
    )
    return f"<div>{spans}</div>"


def _explanation_markdown(explanation: dict | None) -> str:
    if not explanation:
        return "_Not requested — tick \"Generate written explanation\" and re-run to get one from Gemini._"

    lines = [explanation.get("summary", "")]
    for heading, key in (("Strengths", "strengths"), ("Gaps", "gaps"), ("Suggestions", "suggestions")):
        items = explanation.get(key) or []
        if items:
            lines.append(f"\n**{heading}**")
            lines.extend(f"- {item}" for item in items)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Event handlers
# ---------------------------------------------------------------------------

def run_scoring(resume_file, resume_pasted, jd_file, jd_pasted, include_explanation):
    resume_text = _resolve_text(resume_file, resume_pasted, "resume")
    jd_text = _resolve_text(jd_file, jd_pasted, "job description")

    result = compute_ats_score(resume_text, jd_text)
    explanation = generate_explanation(result, resume_text, jd_text) if include_explanation else None

    gaps = result["gap_analysis"]

    return (
        _score_badge_html(result["final_score"]),
        _breakdown_html(result["breakdown"]),
        _chips_html(gaps["matched_skills"], "#15803d", "#dcfce7"),
        _chips_html(gaps["missing_skills"], "#b91c1c", "#fee2e2"),
        _explanation_markdown(explanation),
    )


def load_sample_data():
    return extract_text(SAMPLE_RESUME), extract_text(SAMPLE_JD)


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

theme = gr.themes.Soft(
    primary_hue=gr.themes.colors.indigo,
    secondary_hue=gr.themes.colors.slate,
    neutral_hue=gr.themes.colors.slate,
    font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui"],
    font_mono=[gr.themes.GoogleFont("JetBrains Mono"), "ui-monospace"],
)

with gr.Blocks(title="Semantic ATS Scorer") as demo:
    gr.Markdown(
        "# Semantic ATS Scorer\n"
        "Score a resume against a job description on keyword overlap, semantic similarity, "
        "and structural fit — with a skill-gap breakdown."
    )

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Resume")
            resume_file = gr.File(label="Upload (PDF / DOCX / TXT)", file_types=[".pdf", ".docx", ".txt"], type="filepath")
            resume_text = gr.Textbox(label="...or paste resume text", lines=8, placeholder="Paste resume text here")

            gr.Markdown("### Job description")
            jd_file = gr.File(label="Upload (PDF / DOCX / TXT)", file_types=[".pdf", ".docx", ".txt"], type="filepath")
            jd_text = gr.Textbox(label="...or paste job description text", lines=8, placeholder="Paste job description text here")

            include_explanation = gr.Checkbox(label="Generate written explanation (calls Gemini)", value=False)

            with gr.Row():
                sample_btn = gr.Button("Load sample data")
                run_btn = gr.Button("Score resume", variant="primary")

        with gr.Column(scale=1):
            score_display = gr.HTML()

            gr.Markdown("### Score breakdown")
            breakdown_display = gr.HTML()

            with gr.Row():
                with gr.Column():
                    gr.Markdown("**Matched skills**")
                    matched_display = gr.HTML()
                with gr.Column():
                    gr.Markdown("**Missing skills**")
                    missing_display = gr.HTML()

            with gr.Accordion("Written explanation", open=False):
                explanation_display = gr.Markdown()

    run_btn.click(
        fn=run_scoring,
        inputs=[resume_file, resume_text, jd_file, jd_text, include_explanation],
        outputs=[score_display, breakdown_display, matched_display, missing_display, explanation_display],
    )

    sample_btn.click(fn=load_sample_data, outputs=[resume_text, jd_text])


if __name__ == "__main__":
    demo.launch(theme=theme)
