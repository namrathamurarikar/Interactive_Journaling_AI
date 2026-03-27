import os
import re
import json
import tempfile
import time
import warnings
from typing import Optional
from dotenv import load_dotenv
import google.generativeai as genai

warnings.filterwarnings(
    "ignore",
    message="All support for the `google.generativeai` package has ended",
    category=FutureWarning,
)

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

ASAM_DIMENSIONS = [
    "Acute Intoxication/Withdrawal Potential",
    "Biomedical Conditions & Complications",
    "Emotional/Behavioral Conditions",
    "Relapse/Recurrence Potential",
    "Recovery/Living Environment",
    "Readiness to Change",
]

# Atlas-style curriculum labels (pick recommendations from this catalog only).
ATLAS_CURRICULUM_MODULES = [
    "MOUD/MAT Education",
    "Coping Skills & Distress Tolerance",
    "Relapse Prevention Planning",
    "Relationships & Communication",
    "Building Support Networks",
    "Trauma-Informed Psychoeducation",
    "Sleep & Wellness Routines",
    "Motivational Enhancement",
    "Employment & Life Skills",
    "Parenting & Family Systems",
]


def _text_from_response(response) -> str:
    if response is None:
        return ""
    try:
        t = response.text
        if t:
            return t
    except (ValueError, AttributeError):
        pass
    try:
        for c in response.candidates or []:
            for p in c.content.parts or []:
                if getattr(p, "text", None):
                    return p.text
    except (AttributeError, TypeError):
        pass
    return ""


def _parse_json_from_model(raw: str) -> dict:
    """Parse JSON from model output; handles markdown fences and leading/trailing prose."""
    raw = (raw or "").strip()
    if not raw:
        raise json.JSONDecodeError("empty response", raw, 0)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw, re.IGNORECASE)
    if m:
        inner = m.group(1).strip()
        try:
            return json.loads(inner)
        except json.JSONDecodeError:
            raw = inner
    start = raw.find("{")
    if start == -1:
        raise json.JSONDecodeError("no JSON object in response", raw, 0)
    return json.JSONDecoder().raw_decode(raw[start:])[0]


def _gemini_json_model():
    return genai.GenerativeModel("gemini-2.5-flash")


def _json_generation_config():
    """Older google-generativeai (e.g. 0.3.x) has no response_mime_type; parsing still works."""
    try:
        return genai.GenerationConfig(response_mime_type="application/json")
    except TypeError:
        return None


def _generate_content(model, contents):
    cfg = _json_generation_config()
    if cfg is not None:
        return model.generate_content(contents, generation_config=cfg)
    return model.generate_content(contents)


def _asam_gaps_from_analysis(analysis: dict) -> list[str]:
    gaps = []
    for i, name in enumerate(ASAM_DIMENSIONS):
        key = f"dimension_{i + 1}"
        block = analysis.get("asam", {}).get(key) or {}
        if not block.get("present"):
            gaps.append(name)
    return gaps


def _normalize_module_picks(raw: list) -> list[str]:
    """Keep only catalog matches; pad with defaults if needed."""
    seen = set()
    out = []
    for item in raw or []:
        s = str(item).strip()
        if s in ATLAS_CURRICULUM_MODULES and s not in seen:
            seen.add(s)
            out.append(s)
        if len(out) >= 3:
            break
    for m in ATLAS_CURRICULUM_MODULES:
        if len(out) >= 3:
            break
        if m not in seen:
            seen.add(m)
            out.append(m)
    return out[:3]


def recommend_modules_for_analysis(analysis: dict) -> dict:
    """
    Gemini picks 3 Atlas curriculum modules from ATLAS_CURRICULUM_MODULES
    based on ASAM gaps and the clinical summary.
    """
    gaps = _asam_gaps_from_analysis(analysis)
    catalog = json.dumps(ATLAS_CURRICULUM_MODULES)
    gap_txt = json.dumps(gaps) if gaps else json.dumps(["Use foundational engagement modules"])
    summary = (analysis.get("summary") or "")[:800]

    prompt = f"""You recommend Atlas curriculum for one participant.

Allowed module names (pick exactly 3 distinct names from this list only):
{catalog}

ASAM dimensions not clearly evidenced in journals: {gap_txt}
Clinical summary excerpt: {summary}

Return JSON only:
{{"modules": ["<name1>", "<name2>", "<name3>"], "rationale": "<2-3 sentences>"}}"""

    model = _gemini_json_model()
    try:
        response = _generate_content(model, prompt)
        data = _parse_json_from_model(_text_from_response(response))
        mods = _normalize_module_picks(data.get("modules"))
        return {
            "modules": mods,
            "rationale": str(data.get("rationale") or "").strip()
            or "Modules align with observed ASAM coverage gaps.",
        }
    except (json.JSONDecodeError, TypeError, ValueError, AttributeError):
        return {
            "modules": _normalize_module_picks([]),
            "rationale": "Fallback recommendations (model error).",
        }


def recommend_cohort_modules_from_rates(
    dimension_presence_rates: list[tuple[str, float]],
) -> dict:
    """
    dimension_presence_rates: (ASAM dimension name, 0-1 presence rate across cohort).
    Returns 3 org-level curriculum priorities via Gemini.
    """
    weakest = sorted(dimension_presence_rates, key=lambda x: x[1])[:4]
    rates_blob = json.dumps(
        [{"dimension": d, "presence_rate": round(r, 3)} for d, r in weakest]
    )
    catalog = json.dumps(ATLAS_CURRICULUM_MODULES)
    prompt = f"""You support a behavioral health program director planning cohort-level curriculum.

Allowed module names (pick exactly 3 distinct names from this list only):
{catalog}

Lowest ASAM coverage in this cohort (dimension → share of participants with evidence):
{rates_blob}

Return JSON only:
{{"modules": ["<name1>", "<name2>", "<name3>"], "rationale": "<2-3 sentences on org priorities>"}}"""

    model = _gemini_json_model()
    try:
        response = _generate_content(model, prompt)
        data = _parse_json_from_model(_text_from_response(response))
        mods = _normalize_module_picks(data.get("modules"))
        return {
            "modules": mods,
            "rationale": str(data.get("rationale") or "").strip()
            or "Priorities reflect cohort-wide ASAM coverage gaps.",
        }
    except (json.JSONDecodeError, TypeError, ValueError, AttributeError):
        return {
            "modules": _normalize_module_picks([]),
            "rationale": "Fallback cohort priorities (model error).",
        }


def analyze_journals(journal_entries: list) -> dict:
    """
    Takes list of journal entries, returns structured clinical insights.
    """
    
    combined_text = "\n---JOURNAL ENTRY SEPARATOR---\n".join(journal_entries)
    
    system_prompt = f"""You are a clinical AI assistant for Atlas, a behavioral health platform.
Analyze the following journal entries and provide:

1. **Clinical Summary**: A 3-4 sentence professional summary for a case manager. 
   Sound clinical but accessible. Include key themes and progress indicators.

2. **ASAM Dimensions**: For each of these 6 ASAM Criteria dimensions, identify if it's 
   present in the entries. Include a direct quote if present.
   - {ASAM_DIMENSIONS[0]}
   - {ASAM_DIMENSIONS[1]}
   - {ASAM_DIMENSIONS[2]}
   - {ASAM_DIMENSIONS[3]}
   - {ASAM_DIMENSIONS[4]}
   - {ASAM_DIMENSIONS[5]}

3. **Risk Assessment**: On a scale of 0-1, how likely is this participant to disengage 
   (dropout/AMA)? Consider: entry length declining? Sentiment getting worse? 
   Less engagement? Return a single number 0-1.

4. **Stage of Change**: Is this person in Pre-Contemplation (not ready), 
   Contemplation (thinking about it), or Action (making changes)?

Format your response as JSON only, no other text:
{{
  "summary": "...",
  "asam": {{
    "dimension_1": {{"present": true/false, "quote": "..."}},
    "dimension_2": {{"present": true/false, "quote": "..."}},
    "dimension_3": {{"present": true/false, "quote": "..."}},
    "dimension_4": {{"present": true/false, "quote": "..."}},
    "dimension_5": {{"present": true/false, "quote": "..."}},
    "dimension_6": {{"present": true/false, "quote": "..."}}
  }},
  "risk_score": 0.6,
  "stage_of_change": "Action"
}}
"""
    
    model = _gemini_json_model()
    response = _generate_content(model, [system_prompt, combined_text])

    try:
        return _parse_json_from_model(_text_from_response(response))
    except (json.JSONDecodeError, TypeError, ValueError):
        # Fallback if Gemini response isn't valid JSON
        print("Warning: JSON parsing failed, returning defaults")
        return {
            "summary": "Error parsing response",
            "asam": {f"dimension_{i}": {"present": False, "quote": ""} for i in range(1, 7)},
            "risk_score": 0.5,
            "stage_of_change": "Unknown"
        }


def _gemini_file_state_name(file_obj) -> str:
    state_obj = getattr(file_obj, "state", None)
    if state_obj is None:
        return ""
    name = getattr(state_obj, "name", None)
    if name is not None:
        return str(name).upper()
    return str(state_obj).upper()


def _wait_until_gemini_file_active(uploaded_file, timeout_s: float = 120.0):
    """Files API uploads are async; generate_content fails if file is still PROCESSING."""
    if not hasattr(genai, "get_file"):
        return uploaded_file
    name = getattr(uploaded_file, "name", None)
    if not name:
        return uploaded_file
    deadline = time.time() + timeout_s
    f = uploaded_file
    while time.time() < deadline:
        state = _gemini_file_state_name(f)
        if state == "ACTIVE":
            return f
        if state == "FAILED":
            raise RuntimeError(
                "Gemini could not process this audio file (state=FAILED). "
                "Try WAV or MP3, a shorter clip, or use file upload instead of the browser recorder."
            )
        time.sleep(0.7)
        f = genai.get_file(name)
    raise TimeoutError(
        "Timed out waiting for Gemini to finish processing the audio. Try a shorter recording."
    )


def _infer_mime_from_bytes(b: bytes) -> Optional[str]:
    """Guess MIME when the browser omits voice.type (common with WebM/WAV)."""
    if len(b) < 12:
        return None
    if b[:4] == b"RIFF" and b[8:12] == b"WAVE":
        return "audio/wav"
    if b[:4] == b"\x1a\x45\xdf\xa3":  # EBML (WebM)
        return "audio/webm"
    if b[:4] == b"OggS":
        return "audio/ogg"
    if b[:3] == b"ID3" or (b[0] == 0xFF and len(b) > 1 and (b[1] & 0xE0) == 0xE0):
        return "audio/mpeg"
    return None


def transcribe_audio_to_english(audio_bytes: bytes, mime_type: Optional[str] = None) -> str:
    """
    Transcribe spoken audio and return English journal text.
    Uses Gemini multimodal audio (same GEMINI_API_KEY as the rest of the app).
    If speech is not English, the model translates to natural English.
    """
    if not audio_bytes:
        raise ValueError("Empty audio")

    if not (mime_type and str(mime_type).strip()):
        mime_type = _infer_mime_from_bytes(audio_bytes)

    ext = ".wav"
    if mime_type:
        mt = mime_type.lower()
        if "webm" in mt:
            ext = ".webm"
        elif "mp3" in mt or "mpeg" in mt:
            ext = ".mp3"
        elif "mp4" in mt or "m4a" in mt:
            ext = ".m4a"
        elif "ogg" in mt:
            ext = ".ogg"
        elif "wav" in mt:
            ext = ".wav"

    if not hasattr(genai, "upload_file"):
        raise RuntimeError(
            "Your google-generativeai package is too old for audio upload. "
            "Run: pip install -U 'google-generativeai>=0.8.0'"
        )

    path = None
    uploaded = None
    try:
        fd, path = tempfile.mkstemp(suffix=ext)
        os.write(fd, audio_bytes)
        os.close(fd)

        try:
            uploaded = (
                genai.upload_file(path=path, mime_type=mime_type)
                if mime_type
                else genai.upload_file(path=path)
            )
        except TypeError:
            uploaded = genai.upload_file(path=path)

        ready = _wait_until_gemini_file_active(uploaded)

        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt = (
            "Listen to this audio. Transcribe what is spoken. "
            "If the speech is not in English, translate it to natural, clear English suitable for a clinical journal. "
            "Output ONLY the English journal text. Use line breaks between distinct thoughts or days. "
            "Do not add a title, preamble, or quotation marks around the whole text."
        )
        response = model.generate_content([prompt, ready])
        if not getattr(response, "candidates", None):
            fb = getattr(response, "prompt_feedback", None)
            raise RuntimeError(
                f"Gemini returned no transcript for this audio. {fb or 'Try a shorter clip or upload WAV/MP3.'}"
            )
        text = _text_from_response(response).strip()
        if not text:
            raise RuntimeError(
                "Empty transcript from Gemini. The recording may be silent or in an unsupported format."
            )
        return text
    finally:
        if uploaded is not None:
            name = getattr(uploaded, "name", None)
            if name:
                try:
                    genai.delete_file(name)
                except Exception:
                    pass
        if path:
            try:
                os.unlink(path)
            except OSError:
                pass


# Test function
if __name__ == "__main__":
    test_entries = [
        "Day 1: I'm struggling with cravings. My family wants to help but I feel ashamed. Started NA meetings this week.",
        "Day 5: Attended 3 meetings. Feeling more confident. Still have withdrawal symptoms but the counselor is helping.",
        "Day 10: Two weeks clean now. Learned about my triggers - stress and loneliness. Started calling sponsor daily."
    ]
    
    print("Testing brain.py...")
    result = analyze_journals(test_entries)
    print(json.dumps(result, indent=2))