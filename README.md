# Atlas Clinical Insights Engine

*Repository: [Interactive_Journaling_AI](https://github.com/namrathamurarikar/Interactive_Journaling_AI)*

Proof-of-concept dashboard for behavioral health programs: turn participant journal text into draft clinical summaries, ASAM dimension mapping, dropout-risk signals, and curriculum ideas aligned to an Atlas-style module catalog.

## Problem

Facilitators and clinical staff often read large volumes of journal-style entries. They need **faster triage**, **consistent ASAM framing**, and **early signals of disengagement**—without replacing professional judgment.

## Solution

- **Participant analysis:** Gemini structured JSON analysis per journal set (summary, six ASAM slots with quotes, risk 0–1, stage of change).
- **Cohort view (Day 3):** Batch the demo cohort to show dimension coverage, risk distribution, and org-level curriculum priorities (extra Gemini call).
- **Curriculum matching:** Module picks are constrained to a fixed in-app catalog (MOUD/MAT, coping skills, relapse prevention, relationships, etc.).

## Features

| Area | What you get |
|------|----------------|
| Participant | Clinical summary, ASAM map, risk gauge, facilitator-style next steps |
| Voice (Custom input) | Record or upload audio → Gemini transcribes and translates to **English**, appends to the journal box |
| Curriculum | Three Gemini-chosen modules from the catalog + short rationale |
| Cohort | Horizontal bar chart of ASAM presence rates, pie chart of risk buckets, org curriculum priorities |
| Explainer | “How it works” tab for facilitators vs admins |

See **`VOICE_INPUT_GUIDE.md`** for mic/HTTPS, the **alternate microphone** widget, and dependency notes.

## Run locally

```bash
cd "path/to/project"
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_key_here
```

Get a key from [Google AI Studio](https://aistudio.google.com/apikey).

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501).

## Repo layout

| Path | Role |
|------|------|
| `app.py` | Streamlit UI (How it works, Participant, Cohort) |
| `brain.py` | Gemini calls: `analyze_journals`, curriculum recommenders |
| `demo_data.json` | Participant examples + synthetic cohort for org tab |
| `.streamlit/config.toml` | Atlas-themed Streamlit colors |
| `requirements.txt` | Python dependencies |
| `.env` | API secret (**do not commit**) |

## Deploy (Streamlit Cloud)

1. Push this repo to GitHub (without `.env`).
2. [Streamlit Community Cloud](https://streamlit.io/cloud) → New app → select repo and `app.py`.
3. Add a secret `GEMINI_API_KEY` in the app settings.
4. Redeploy and test the live URL.

## Stack

- Python 3.9+
- Streamlit, Plotly
- `google-generativeai` with **Gemini 2.5 Flash** (model IDs in code; update if Google deprecates)

## Disclaimer

Demo data is synthetic. Model output is **not** medical advice or a substitute for licensed clinical review.
