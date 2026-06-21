# Semantic ATS

A resume-to-job-description matcher that combines classic keyword matching
with semantic (embedding-based) similarity, plus structural checks
(experience, education, title), into a single explainable ATS score.

## Why hybrid

Pure keyword ATS systems miss paraphrased skills ("led a team" vs "managed
engineers"). Pure embedding similarity over-scores resumes that are merely
*topically* close to a JD (e.g. Data Analyst vs Data Scientist). This
project compares resume/JD **section by section** (skills-to-skills,
experience-to-responsibilities) and blends three signals:

| Signal      | Catches                                  | Weight (default) |
|-------------|-------------------------------------------|-------------------|
| Keyword     | Exact terms, certifications, tool names   | 0.35              |
| Semantic    | Paraphrased/related skills and experience | 0.45              |
| Structural  | Years of experience, education, title     | 0.20              |

Weights are configurable in `.env`.

## Setup

```bash
cd semantic-ats
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env and add your GEMINI_API_KEY (only needed for --explain / include_explanation)
```

The first run will download the sentence-transformer model
(`all-mpnet-base-v2`, ~420MB) — this happens once and is cached locally.

## Run the CLI demo (fastest way to test)

```bash
python scripts/run_demo.py
```

Runs the pipeline on the bundled sample resume/JD in `tests/sample_data/`
and prints the score, breakdown, and gap analysis. Use your own files:

```bash
python scripts/run_demo.py --resume path/to/resume.pdf --jd path/to/jd.txt --explain
```

`--explain` calls Gemini for a written explanation + suggestions (requires
`GEMINI_API_KEY`); omit it to get the numeric score only, with no API calls.

## Run the Gradio UI

```bash
python gradio_app.py
```

Opens at `http://127.0.0.1:7860`. Upload or paste a resume and JD (there's a
"Load sample data" button to try it instantly), optionally tick "Generate
written explanation" to call Gemini, and hit "Score resume." Shows the
final score, a per-signal breakdown, and matched/missing skill chips.

## Run the API

```bash
uvicorn main:app --reload
```

Interactive docs at `http://127.0.0.1:8000/docs`. Two endpoints:

- `POST /api/v1/score/text` — JSON body `{resume_text, jd_text, include_explanation}`
- `POST /api/v1/score/upload` — multipart upload of `resume_file` + `jd_file` (PDF/DOCX/TXT)

## Project layout

See module docstrings — every file explains its own role and the reasoning
behind it. Start reading at `app/scoring/weighted_scorer.py`, which is the
orchestrator that calls everything else.

## The highest-leverage file to edit

`data/skills_taxonomy.json` — skill extraction quality depends entirely on
this taxonomy's coverage. The sample has ~50 entries; extend it with
skills relevant to your target domain. This matters more than any
algorithm tweak.

## Known limitations (worth stating in any writeup)

- Section detection is regex/heuristic-based and will misparse unusual
  resume formats — see `app/parsing/section_extractor.py` for the header
  list to extend.
- No ground truth: weights are heuristic defaults, not learned from
  labeled data. If you want to validate/tune them, hand-label a small set
  of resume/JD pairs with a relevance score and grid-search the weights
  against it.
- Real ATS systems face documented bias concerns (filtering on proxies
  for protected characteristics). This project doesn't filter/reject —
  it only scores — but if you extend it to auto-reject candidates, audit
  for disparate impact first.
