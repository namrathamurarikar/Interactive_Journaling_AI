# Voice input (speech → English text)

This project uses **Gemini multimodal audio** for transcription and translation. You only need your existing **`GEMINI_API_KEY`** (no separate Google Cloud Speech-to-Text project required).

## What was implemented

1. **`st.audio_input()`** (Streamlit ≥ 1.33) — built-in “Record voice (Streamlit)”. When you **stop** recording, transcription runs **automatically** (no separate Transcribe click). Duplicate clips are skipped via a **hash** of the audio bytes.
2. **`audio-recorder-streamlit`** — **Alternate microphone** expander: hold-to-talk **WAV**; transcribes automatically when the clip changes (also hash-guarded).
3. **File upload** — choosing a file triggers **one** automatic transcription (same file hash won’t re-run until you pick another file).
4. **`brain.transcribe_audio_to_english()`** — uploads audio to the Gemini Files API, waits until **ACTIVE**, then **Gemini 2.5 Flash** transcribes and outputs **English** (translates any language).
5. **Append to journal** — text is merged via `pending_journal_append` (see app); edit, then **Analyze**.

## Setup

```bash
pip install -U -r requirements.txt
```

Minimum versions:

- `streamlit>=1.33.0` (for `st.audio_input`)
- `google-generativeai>=0.8.0` (for `genai.upload_file` + multimodal audio)

## Usage

1. Open **Participant analysis**.
2. Sidebar: **Load example → Custom Input**.
3. Record audio **or** upload a file.
4. Click **Transcribe … → append to journal**.
5. Review/edit the English text, then **Analyze**.

## Browser / HTTPS / LAN IPs

Microphone access requires a [**secure context**](https://developer.mozilla.org/en-US/docs/Web/Security/Secure_Contexts):

- **`https://`** — OK  
- **`http://localhost:8501`** or **`http://127.0.0.1:8501`** — OK  
- **`http://192.168.x.x:8501`** (or any LAN IP over plain HTTP) — **microphone is blocked**. The UI may look “active” (e.g. purple button) but **no audio is captured**.

**Fix:** Open the app on the same PC at **`http://localhost:8501`**, or use HTTPS (e.g. reverse proxy). **Upload audio** works from any URL (no mic).

Streamlit Cloud provides HTTPS automatically.

## Costs

- Uses the same Gemini API key as journal analysis (Google AI Studio / Gemini API billing applies).
- No extra **Google Cloud Speech-to-Text** API is wired in this implementation.

## Privacy

Voice is sent to Google’s Gemini service for transcription/translation. Do **not** use real PHI in demos unless your agreements allow it.

## Troubleshooting

| Issue | What to try |
|--------|----------------|
| **“An error has occurred, please try again”** on the **recorder** (before Transcribe) | Usually **browser / Streamlit**, not Python. Allow mic permission, use **localhost** or **HTTPS**, try **Chrome/Edge**, or skip the mic and use **Or upload audio** (WAV/MP3). |
| Transcribe fails after clicking the button | See the red error text—often **wait for file processing** (fixed in code), **unsupported format** (try WAV), or **empty/silent** recording. |
| `upload_file` / package errors | `pip install -U 'google-generativeai>=0.8.0'` |
| No `audio_input` | `pip install -U 'streamlit>=1.33'` or use **upload audio** only |
| Empty or bad transcript | Re-record; speak clearly; try WAV upload |
| Mic permission denied | Browser site settings; use HTTPS |

The app waits until Gemini marks the uploaded file **ACTIVE** before transcribing (required by the Files API).
