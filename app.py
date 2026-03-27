import hashlib
import json
import re
import time
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

try:
    from audio_recorder_streamlit import audio_recorder
except ImportError:
    audio_recorder = None

from brain import (
    ASAM_DIMENSIONS,
    ATLAS_CURRICULUM_MODULES,
    analyze_journals,
    recommend_cohort_modules_from_rates,
    recommend_modules_for_analysis,
    transcribe_audio_to_english,
)

st.set_page_config(
    page_title="Atlas Clinical Insights",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Splash: 3D book — closed beat → slow cover open → 5s hold (lined journal inside) → zoom → fade.
# Timings (ms): SPLASH_MS = hard hide; Python sleep must finish after last transition.
_SPLASH_CLOSED_MS = 1200
_SPLASH_COVER_OPEN_MS = 2800
# Pages fade in after the cover has rotated this many degrees (full open = 180°).
_SPLASH_COVER_OPEN_ROTATION_DEG = 180
_SPLASH_PAGES_REVEAL_AFTER_DEG = 30
# Delay is applied when `.open` is added (after CLOSED beat). Do NOT add _SPLASH_CLOSED_MS
# here — that double-counts and leaves ~CLOSED_MS of dead air after the cover finishes.
_SPLASH_PAGES_REVEAL_DELAY_MS = _SPLASH_COVER_OPEN_MS
_SPLASH_PAGES_FADE_MS = 500
# Typewriter + headline reveal: start immediately when cover-open ends.
_SPLASH_TYPEWRITER_DELAY_AFTER_OPEN_MS = _SPLASH_COVER_OPEN_MS
_SPLASH_HOLD_OPEN_MS = 5000
_SPLASH_ZOOM_MS = 2000
_SPLASH_FADE_MS = 800
_SPLASH_MS = (
    _SPLASH_CLOSED_MS
    + _SPLASH_COVER_OPEN_MS
    + _SPLASH_HOLD_OPEN_MS
    + _SPLASH_ZOOM_MS
    + _SPLASH_FADE_MS
)

_ATLAS_DEBUG_LOG = Path(__file__).resolve().parent / "debug-b9c62c.log"

if not st.session_state.get("intro_played", False):
    try:
        with _ATLAS_DEBUG_LOG.open("a", encoding="utf-8") as _dbg:
            _dbg.write(
                json.dumps(
                    {
                        "sessionId": "b9c62c",
                        "runId": "py-splash",
                        "hypothesisId": "H0",
                        "location": "app.py:intro",
                        "message": "splash_components_html_dispatched",
                        "data": {
                            "splash_ms": _SPLASH_MS,
                            "pages_reveal_delay_ms": _SPLASH_PAGES_REVEAL_DELAY_MS,
                            "pages_fade_ms": _SPLASH_PAGES_FADE_MS,
                            "typewriter_delay_after_open_ms": _SPLASH_TYPEWRITER_DELAY_AFTER_OPEN_MS,
                        },
                        "timestamp": int(time.time() * 1000),
                    }
                )
                + "\n"
            )
    except OSError:
        pass
    components.html(
        f"""
        <style>
            html, body {{
                margin: 0;
                height: 100%;
                min-height: 100vh;
                overflow: hidden;
                background: #1a1428;
                font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
            }}
            .book-wrapper {{
                position: fixed;
                inset: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                background: radial-gradient(circle at center, #2d1b4e 0%, #0a0a0a 100%);
                perspective: 1500px;
                perspective-origin: 50% 50%;
                transform-style: preserve-3d;
                z-index: 99999;
            }}
            .book {{
                position: relative;
                width: min(560px, 92vw);
                height: min(360px, 52vh);
                transform-style: preserve-3d;
                border-radius: 10px;
                transition: transform {_SPLASH_ZOOM_MS / 1000}s ease-in, opacity {_SPLASH_ZOOM_MS / 1000}s ease-in;
            }}
            .book-wrapper.zoom .book {{
                transform: scale(2.6) translateZ(180px);
                opacity: 0;
            }}
            .paper {{
                background:
                    repeating-linear-gradient(transparent, transparent 22px, rgba(102, 51, 153, 0.07) 23px),
                    linear-gradient(165deg, #fffefb 0%, #faf6ff 100%);
            }}
            .book-pages {{
                position: absolute;
                inset: 0;
                z-index: 5;
                transform: translateZ(0.25px);
                border-radius: 10px;
                opacity: 0;
                pointer-events: none;
                box-shadow: none;
                transition: opacity {_SPLASH_PAGES_FADE_MS / 1000}s ease, box-shadow {_SPLASH_PAGES_FADE_MS / 1000}s ease;
            }}
            .book-wrapper.open .book-pages {{
                opacity: 1;
                pointer-events: auto;
                box-shadow: 0 14px 40px rgba(0, 0, 0, 0.35);
                transition-delay: {_SPLASH_PAGES_REVEAL_DELAY_MS / 1000}s, {_SPLASH_PAGES_REVEAL_DELAY_MS / 1000}s;
            }}
            .book-pages::after {{
                content: "";
                position: absolute;
                left: 50%;
                top: 0;
                bottom: 0;
                width: 18px;
                transform: translateX(-50%);
                z-index: 4;
                pointer-events: none;
                background: linear-gradient(90deg, rgba(0, 0, 0, 0) 0%, rgba(30, 20, 45, 0.14) 35%, rgba(20, 12, 35, 0.28) 50%, rgba(30, 20, 45, 0.14) 65%, rgba(0, 0, 0, 0) 100%);
            }}
            .page-left {{
                position: absolute;
                left: 0;
                top: 0;
                width: 50%;
                height: 100%;
                border-radius: 10px 0 0 10px;
                box-shadow: inset -8px 0 14px rgba(0, 0, 0, 0.08);
                border-right: 1px solid rgba(102, 51, 153, 0.12);
            }}
            .page-right {{
                position: absolute;
                right: 0;
                top: 0;
                width: 50%;
                height: 100%;
                border-radius: 0 10px 10px 0;
                box-shadow: inset 8px 0 14px rgba(0, 0, 0, 0.06);
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 18px 14px 16px 16px;
                box-sizing: border-box;
            }}
            .page-right-content {{
                display: flex;
                flex-direction: column;
                flex: 1;
                width: 100%;
                align-items: center;
                justify-content: center;
                gap: 10px;
                opacity: 0;
                visibility: hidden;
                pointer-events: none;
                transition: opacity 0.55s ease, visibility 0s linear 0.55s;
            }}
            .book-wrapper.open .page-right-content {{
                opacity: 1;
                visibility: visible;
                pointer-events: auto;
                transition: opacity 0.55s ease {_SPLASH_TYPEWRITER_DELAY_AFTER_OPEN_MS / 1000}s, visibility 0s linear {_SPLASH_TYPEWRITER_DELAY_AFTER_OPEN_MS / 1000}s;
            }}
            .book-cover-full {{
                position: absolute;
                left: 50%;
                top: 0;
                width: 50%;
                height: 100%;
                z-index: 10;
                transform-origin: left center;
                transform: rotateY(0deg) translateZ(1px);
                transition: transform {_SPLASH_COVER_OPEN_MS / 1000}s cubic-bezier(0.45, 0.05, 0.55, 0.95);
            }}
            .book-wrapper.open .book-cover-full {{
                transform: rotateY(-180deg) translateZ(-8px);
            }}
            .book-wrapper.cover-behind .book-cover-full {{
                z-index: 0;
                pointer-events: none;
            }}
            .cover-face {{
                position: absolute;
                inset: 0;
                border-radius: 0 10px 10px 0;
                backface-visibility: hidden;
            }}
            .cover-outside {{
                background: linear-gradient(135deg, #663399 0%, #4a2670 100%);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-left: none;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.12), 6px 10px 28px rgba(0, 0, 0, 0.45);
            }}
            .cover-outside .label {{
                color: #fff;
                font-weight: 800;
                text-align: center;
                font-size: 1.25rem;
                line-height: 1.25;
                text-shadow: 0 2px 12px rgba(0, 0, 0, 0.4);
            }}
            .cover-inside {{
                transform: rotateY(180deg);
                background: linear-gradient(165deg, #5b3d7a 0%, #4a2670 45%, #3d1f5c 100%);
                border: 1px solid rgba(0, 0, 0, 0.15);
            }}
            .journal-head {{
                margin: 0 0 12px 0;
                text-align: center;
                width: 100%;
            }}
            .journal-head .line1 {{
                font-size: clamp(16px, 4.2vw, 22px);
                font-weight: 800;
                color: #4a2670;
                min-height: 1.2em;
                line-height: 1.15;
            }}
            .journal-head .line2 {{
                font-size: clamp(17px, 5vw, 26px);
                font-weight: 800;
                color: #4a2670;
                margin-top: 2px;
                min-height: 1.2em;
                line-height: 1.1;
            }}
            .cursor {{
                display: inline-block;
                width: 8px;
                height: 1.2em;
                background-color: #ff8c00;
                margin-left: 4px;
                vertical-align: middle;
                animation: atlas-cursor-blink 0.8s step-end infinite;
                box-shadow: 0 0 8px rgba(255, 140, 0, 0.6);
            }}
            @keyframes atlas-cursor-blink {{
                50% {{ opacity: 0; }}
            }}
        </style>
        <div id="wrapper" class="book-wrapper">
            <div id="book" class="book">
                <div class="book-pages">
                    <div class="page-left paper" aria-hidden="true"></div>
                    <div class="page-right paper">
                        <div class="page-right-content">
                            <div class="journal-head">
                                <div class="line1" id="tw-interactive"></div>
                                <div class="line2" id="tw-journaling"></div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="book-cover-full">
                    <div class="cover-face cover-outside"><div class="label">ATLAS<br>INSIGHTS</div></div>
                    <div class="cover-face cover-inside" aria-hidden="true"></div>
                </div>
            </div>
        </div>
        <script>
            const closed = {_SPLASH_CLOSED_MS};
            const coverMs = {_SPLASH_COVER_OPEN_MS};
            const hold = {_SPLASH_HOLD_OPEN_MS};
            const zoom = {_SPLASH_ZOOM_MS};
            const wrap = document.getElementById('wrapper');
            const openDone = closed + coverMs;
            const zoomStart = openDone + hold;
            function typeLine(el, text, speed, done) {{
                if (!el) {{
                    if (done) done();
                    return;
                }}
                let i = 0;
                const cursor = document.createElement('span');
                cursor.className = 'cursor';
                function tick() {{
                    i += 1;
                    el.textContent = text.slice(0, i);
                    el.appendChild(cursor);
                    if (i < text.length) {{
                        const randomSpeed = speed + (Math.random() * 20 - 10);
                        setTimeout(tick, Math.max(16, randomSpeed));
                    }} else {{
                        setTimeout(() => {{
                            cursor.style.display = 'none';
                            if (done) done();
                        }}, 500);
                    }}
                }}
                tick();
            }}
            setTimeout(() => {{ wrap.classList.add('open'); }}, closed);
            setTimeout(() => {{ wrap.classList.add('cover-behind'); }}, closed + coverMs);
            setTimeout(() => {{
                const el1 = document.getElementById('tw-interactive');
                const el2 = document.getElementById('tw-journaling');
                if (el1) el1.textContent = '';
                if (el2) el2.textContent = '';
                typeLine(el1, 'Interactive', 60, () => typeLine(el2, 'Journaling', 70, null));
            }}, closed + {_SPLASH_TYPEWRITER_DELAY_AFTER_OPEN_MS});
            setTimeout(() => wrap.classList.add('zoom'), zoomStart);
            setTimeout(() => {{
                wrap.style.opacity = '0';
                wrap.style.transition = 'opacity {_SPLASH_FADE_MS / 1000}s ease';
            }}, zoomStart + zoom);
            setTimeout(() => {{ wrap.style.display = 'none'; }}, {_SPLASH_MS});
        </script>
        """,
        height=1200,
        scrolling=False,
    )
    st.session_state.intro_played = True
    st.session_state["post_intro_fade_in"] = True
    time.sleep(_SPLASH_MS / 1000.0 + 0.12)
    st.rerun()

# FIXED SPLASH ANIMATION - counter-rotate text so it is not mirrored when the page flips
_SPLASH_TOTAL_MS = 3500
_SPLASH_BOOK_APPEAR_MS = 300
_SPLASH_BOOK_OPEN_MS = 1200
_SPLASH_TEXT_APPEAR_MS = 1800  # documented pacing (show-text uses appear+open in JS)
_SPLASH_HOLD_MS = 1000
_SPLASH_FADE_OUT_MS = 400

if False and not st.session_state.get("intro_played", False):
    components.html(
        f"""
        <style>
            html, body {{
                margin: 0;
                height: 100%;
                min-height: 100vh;
                overflow: hidden;
                background: linear-gradient(165deg, #dde0ea 0%, #e8eaf2 100%);
                font-family: "Inter", system-ui, sans-serif;
            }}
            .splash-wrapper {{
                position: fixed;
                inset: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 99999;
                background: linear-gradient(165deg, #dde0ea 0%, #e8eaf2 100%);
                opacity: 1;
                transition: opacity {_SPLASH_FADE_OUT_MS / 1000}s ease;
            }}
            .splash-wrapper.fade-out {{
                opacity: 0;
                pointer-events: none;
            }}
            .book-container {{
                position: relative;
                width: min(600px, 95vw);
                height: min(400px, 60vh);
                perspective: 1200px;
            }}
            .book {{
                position: relative;
                width: 100%;
                height: 100%;
                transform-style: preserve-3d;
                opacity: 0;
                transition: opacity {_SPLASH_BOOK_APPEAR_MS / 1000}s ease;
            }}
            .book.show {{
                opacity: 1;
            }}
            .book-spine {{
                position: absolute;
                left: 50%;
                top: 0;
                width: 1px;
                height: 100%;
                background: rgba(0, 0, 0, 0.1);
                z-index: 10;
            }}
            /* Left side (closed, stays still) */
            .book-left {{
                position: absolute;
                left: 0;
                top: 0;
                width: 50%;
                height: 100%;
                background: linear-gradient(135deg, #663399 0%, #7d3eb8 100%);
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 14px 0 0 14px;
                box-shadow: -8px 12px 40px rgba(102, 51, 153, 0.35);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 1;
            }}
            .book-left-text {{
                color: white;
                font-size: clamp(1.4rem, 5vw, 2.2rem);
                font-weight: 900;
                text-align: center;
                line-height: 1.2;
                text-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
                padding: 0 20px;
            }}
            /* Right side (opens) */
            .book-right {{
                position: absolute;
                left: 50%;
                top: 0;
                width: 50%;
                height: 100%;
                background: linear-gradient(165deg, #fffef9 0%, #faf4ea 100%);
                border: 2px solid rgba(102, 51, 153, 0.25);
                border-radius: 0 14px 14px 0;
                transform-origin: left center;
                transform-style: preserve-3d;
                transform: rotateY(0deg);
                transition: transform {_SPLASH_BOOK_OPEN_MS / 1000}s cubic-bezier(0.34, 1.56, 0.64, 1);
                z-index: 2;
                box-shadow: inset 8px 0 20px rgba(0, 0, 0, 0.08);
                display: flex;
                align-items: center;
                justify-content: center;
                overflow: hidden;
            }}
            .book.open .book-right {{
                transform: rotateY(-180deg);
            }}
            /* Lined paper pattern on right */
            .book-right::before {{
                content: "";
                position: absolute;
                inset: 0;
                background:
                    repeating-linear-gradient(
                        transparent,
                        transparent 24px,
                        rgba(102, 51, 153, 0.08) 25px
                    );
                pointer-events: none;
                z-index: 1;
            }}
            /* Text container - counter-rotate so copy is not mirrored */
            .book-right-content {{
                position: absolute;
                inset: 0;
                display: flex;
                align-items: center;
                justify-content: center;
                opacity: 0;
                transition: opacity 0.6s ease;
                z-index: 2;
                transform: rotateY(180deg);
            }}
            .book.open .book-right-content {{
                transform: rotateY(180deg);
            }}
            .book.show-text .book-right-content {{
                opacity: 1;
            }}
            .interactive-text {{
                color: #663399;
                font-size: clamp(2rem, 7vw, 3.2rem);
                font-weight: 900;
                text-align: center;
                line-height: 1.15;
                letter-spacing: -0.02em;
                text-shadow: 0 2px 8px rgba(102, 51, 153, 0.15);
                padding: 0 30px;
            }}
            .interactive-text .line1 {{
                display: block;
                color: #663399;
            }}
            .interactive-text .line2 {{
                display: block;
                color: #FF8C00;
                margin-top: 8px;
            }}
        </style>
        <div class="splash-wrapper" id="splash">
            <div class="book-container">
                <div class="book" id="book">
                    <!-- Left side (static) -->
                    <div class="book-left">
                        <div class="book-left-text">ATLAS<br>INSIGHTS</div>
                    </div>
                    <!-- Right side (opens) -->
                    <div class="book-right">
                        <div class="book-right-content">
                            <div class="interactive-text">
                                <span class="line1">Interactive</span>
                                <span class="line2">Journaling</span>
                            </div>
                        </div>
                    </div>
                    <!-- Spine -->
                    <div class="book-spine"></div>
                </div>
            </div>
        </div>
        <script>
            const book = document.getElementById('book');
            const splash = document.getElementById('splash');

            // Step 1: Book appears (fade in)
            setTimeout(() => {{
                book.classList.add('show');
            }}, 100);

            // Step 2: Book opens
            setTimeout(() => {{
                book.classList.add('open');
            }}, {_SPLASH_BOOK_APPEAR_MS});

            // Step 3: Text appears on right page
            setTimeout(() => {{
                book.classList.add('show-text');
            }}, {_SPLASH_BOOK_APPEAR_MS + _SPLASH_BOOK_OPEN_MS});

            // Step 4: Everything fades out
            setTimeout(() => {{
                splash.classList.add('fade-out');
            }}, {_SPLASH_BOOK_APPEAR_MS + _SPLASH_BOOK_OPEN_MS + _SPLASH_HOLD_MS});

            // Step 5: Hide splash completely
            setTimeout(() => {{
                splash.style.display = 'none';
            }}, {_SPLASH_TOTAL_MS});
        </script>
        """,
        height=600,
        scrolling=False,
    )
    st.session_state.intro_played = True
    time.sleep(_SPLASH_TOTAL_MS / 1000.0 + 0.15)
    st.rerun()

# One-time app fade-in right after splash rerun (book fade-out remains unchanged).
if st.session_state.pop("post_intro_fade_in", False):
    st.markdown(
        f"""
<style>
@keyframes atlas-app-fade-in {{
  from {{ opacity: 0; transform: translateY(4px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}
.stApp {{
  animation: atlas-app-fade-in {_SPLASH_FADE_MS / 1000}s ease-out both;
}}
</style>
""",
        unsafe_allow_html=True,
    )


def _typewriter_line_html(text: str, speed_ms: int = 42) -> None:
    """Letter-by-letter line (runs in iframe JS; Streamlit does not flush a Python loop per char)."""
    safe = json.dumps(text)
    components.html(
        f"""
        <style>
            #atlas-tw {{
                font-size: 1.4rem;
                font-weight: 600;
                color: #663399;
                min-height: 1.6em;
                font-family: "Inter", "Segoe UI", system-ui, sans-serif;
                letter-spacing: 0.02em;
                margin: 0 0 0.15rem 0;
            }}
            #atlas-tw .cursor {{
                display: inline-block;
                margin-left: 1px;
                color: #ff8c00;
                animation: atlasBlink 0.75s step-end infinite;
            }}
            @keyframes atlasBlink {{
                50% {{ opacity: 0; }}
            }}
        </style>
        <div id="atlas-tw"><span id="atlas-tw-inner"></span><span class="cursor">▍</span></div>
        <script>
            const full = {safe};
            const el = document.getElementById('atlas-tw-inner');
            const cursor = document.querySelector('#atlas-tw .cursor');
            let i = 0;
            function step() {{
                i += 1;
                el.textContent = full.slice(0, i);
                if (i < full.length) {{
                    setTimeout(step, {speed_ms});
                }} else if (cursor) {{
                    cursor.style.display = 'none';
                }}
            }}
            setTimeout(step, 100);
        </script>
        """,
        height=72,
        scrolling=False,
    )


def _app_dir() -> Path:
    return Path(__file__).resolve().parent


@st.cache_data
def load_demo_pack() -> dict:
    p = _app_dir() / "demo_data.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def parse_journal_entries(text: str, mode: str) -> list[str]:
    text = (text or "").strip()
    if not text:
        return []
    if mode == "Commas (between Day N: blocks)":
        parts = re.split(r",\s*(?=Day\s+\d+:)", text, flags=re.IGNORECASE)
        return [p.strip() for p in parts if p.strip()]
    return [e.strip() for e in text.split("\n") if e.strip()]


def _risk_float(val, default: float = 0.5) -> float:
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def _microphone_blocked_by_browser_origin() -> tuple[bool, str | None]:
    """
    Mic APIs require a *secure context*: HTTPS, or http://localhost / 127.0.0.1 only.
    Plain http://192.168.x.x (LAN IP) → browsers block microphone → purple UI, no audio.
    """
    try:
        url = st.context.url
    except Exception:
        return False, None
    if not url:
        return False, None
    u = url.strip().lower()
    if u.startswith("https://"):
        return False, url
    if u.startswith("http://localhost") or u.startswith("http://127.0.0.1"):
        return False, url
    if u.startswith("http://"):
        return True, url
    return False, url


def aggregate_cohort_results(rows: list[dict]) -> tuple[list[dict], dict]:
    """Per-dimension presence rate + risk bucket counts."""
    n = len(rows)
    if n == 0:
        return [], {"low": 0, "medium": 0, "high": 0}

    dim_rows = []
    for i, name in enumerate(ASAM_DIMENSIONS):
        key = f"dimension_{i + 1}"
        present = sum(
            1
            for r in rows
            if (r.get("asam") or {}).get(key, {}).get("present")
        )
        dim_rows.append(
            {
                "dimension": name,
                "presence_rate": present / n,
                "present_count": present,
                "n": n,
            }
        )

    risks = [_risk_float(r.get("risk_score"), 0.5) for r in rows]
    low = sum(1 for x in risks if x < 0.33)
    high = sum(1 for x in risks if x >= 0.67)
    medium = n - low - high
    return dim_rows, {"low": low, "medium": medium, "high": high}


def _html_journal_desk_closed() -> str:
    """Closed desk: cat with glasses writing on paper."""
    return """
<!DOCTYPE html><html><head><meta charset="utf-8"><style>
  * { box-sizing: border-box; }
  body { margin: 0; font-family: 'Segoe UI', system-ui, sans-serif; overflow: hidden; }
  .scene {
    height: 100%; min-height: 260px;
    background: linear-gradient(155deg, #ede6fa 0%, #f7f0e8 42%, #e2ecf8 100%);
    border-radius: 18px;
    position: relative;
    overflow: hidden;
    box-shadow: inset 0 0 100px rgba(102, 51, 153, 0.07);
  }
  .paper {
    position: absolute; inset: 10px;
    background:
      repeating-linear-gradient(
        transparent, transparent 26px,
        rgba(102, 51, 153, 0.07) 27px
      ),
      linear-gradient(180deg, #fffefb 0%, #faf6ef 100%);
    border-radius: 14px;
    border: 1px solid rgba(102, 51, 153, 0.12);
  }
  .desk-paper {
    position: absolute;
    left: 52%;
    top: 50%;
    transform: translate(-50%, -50%) rotate(-1deg);
    width: min(360px, 84%);
    height: 185px;
    border-radius: 12px;
    border: 1px solid rgba(102, 51, 153, 0.2);
    background:
      repeating-linear-gradient(
        transparent, transparent 24px,
        rgba(102, 51, 153, 0.08) 25px
      ),
      linear-gradient(180deg, rgba(255,255,255,0.94) 0%, rgba(255,250,245,0.94) 100%);
    box-shadow: 0 14px 30px rgba(102, 51, 153, 0.12);
    z-index: 2;
  }
  .scribble {
    position: absolute;
    left: 61%;
    top: 47%;
    width: 120px;
    height: 60px;
    z-index: 3;
    opacity: 0.75;
  }
  .scribble path {
    fill: none;
    stroke: rgba(86, 58, 122, 0.7);
    stroke-width: 2.3;
    stroke-linecap: round;
    stroke-dasharray: 120;
    stroke-dashoffset: 120;
    animation: writeLine 2s ease-in-out infinite;
  }
  .scribble path:nth-child(2) { animation-delay: 0.35s; }
  .scribble path:nth-child(3) { animation-delay: 0.7s; }
  .cat {
    position: absolute; left: 13%; bottom: 21%;
    font-size: 4.1rem;
    z-index: 5;
    filter: drop-shadow(2px 6px 10px rgba(0,0,0,0.18));
    animation: catWrite 2.2s ease-in-out infinite;
  }
  .glasses {
    position: absolute;
    left: calc(13% + 37px);
    bottom: calc(21% + 44px);
    font-size: 1.05rem;
    z-index: 7;
    transform-origin: center;
    animation: glassesBob 2.2s ease-in-out infinite;
    filter: drop-shadow(0 1px 2px rgba(0,0,0,0.25));
  }
  .paw {
    position: absolute; left: 28%; bottom: 34%;
    font-size: 1.25rem;
    z-index: 6;
    opacity: 0.95;
    transform-origin: left center;
    animation: pawTap 2.2s ease-in-out infinite;
  }
  @keyframes catWrite {
    0%, 100% { transform: translate(0, 0) rotate(-3deg); }
    50% { transform: translate(12px, -7px) rotate(2deg); }
  }
  @keyframes glassesBob {
    0%, 100% { transform: translate(0, 0) rotate(-2deg); }
    50% { transform: translate(10px, -5px) rotate(2deg); }
  }
  @keyframes pawTap {
    0%, 100% { transform: translate(0, 0) rotate(-18deg); opacity: 0.78; }
    40% { opacity: 1; }
    50% { transform: translate(28px, 8px) rotate(7deg); opacity: 1; }
    60% { opacity: 0.85; }
  }
  @keyframes writeLine {
    0% { stroke-dashoffset: 120; opacity: 0.2; }
    35% { opacity: 0.95; }
    100% { stroke-dashoffset: 0; opacity: 0.7; }
  }
  .bubble {
    position: absolute;
    bottom: 12px;
    left: 50%;
    transform: translateX(-50%);
    width: 90%;
    max-width: 420px;
    font-size: 0.78rem;
    line-height: 1.45;
    color: #3d2858;
    background: rgba(255,255,255,0.88);
    backdrop-filter: blur(8px);
    padding: 10px 14px;
    border-radius: 12px;
    border: 1px solid rgba(102, 51, 153, 0.22);
    box-shadow: 0 6px 20px rgba(102, 51, 153, 0.12);
    z-index: 6;
    text-align: center;
  }
  .bubble em { color: #663399; font-style: normal; font-weight: 600; }
</style></head><body>
  <div class="scene" role="img" aria-label="Cat with glasses writing on paper">
    <div class="paper"></div>
    <div class="desk-paper"></div>
    <svg class="scribble" viewBox="0 0 120 60" aria-hidden="true">
      <path d="M4 10 C28 2, 46 20, 78 12"></path>
      <path d="M8 28 C30 18, 50 36, 86 28"></path>
      <path d="M10 46 C36 38, 57 56, 98 44"></path>
    </svg>
    <div class="cat" aria-hidden="true">🐱</div>
    <div class="glasses" aria-hidden="true">👓</div>
    <div class="paw" aria-hidden="true">✍️</div>
    <div class="bubble">
      <em>Day 1:</em> &ldquo;I&rsquo;m struggling&hellip;&rdquo;
      &nbsp;&middot;&nbsp;
      <em>Day 5:</em> &ldquo;A little better today&hellip;&rdquo;
      <br><span style="opacity:0.85;font-size:0.92em">Open the box below to write your real entries.</span>
    </div>
  </div>
</body></html>
"""


# --- Load demo JSON (Day 4); fall back if file missing ---
_pack = load_demo_pack()
_DEFAULT_EXAMPLES = {
    "Example: Opioid Treatment": [
        "Day 1: I'm struggling with cravings. My family wants to help but I feel ashamed. Started NA meetings this week.",
        "Day 5: Attended 3 meetings. Feeling more confident. Still have withdrawal symptoms but the counselor is helping.",
        "Day 10: Two weeks clean now. Learned about my triggers - stress and loneliness. Started calling sponsor daily.",
    ],
    "Example: Adolescent Treatment": [
        "I don't really know why I'm here. My parents say I have a 'problem' but it's not that bad.",
        "Talked with counselor about why weed felt necessary. Started realizing I was avoiding feeling sad about dad.",
        "Made a plan to call dad this week. Scared but ready to try.",
    ],
    "Example: Trauma": [
        "Had another nightmare about the accident. Can't sleep without anxiety medication.",
        "Counselor taught me breathing exercises. They actually helped during the panic attack yesterday.",
        "Used my grounding technique when triggered today. Felt empowering to manage it myself.",
    ],
}
demo_data = _pack.get("participant_examples") or _DEFAULT_EXAMPLES
cohort_participants = _pack.get("cohort") or []

# Day 3: Atlas branding + glass / Inter / centered canvas
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,400;0,14..32,500;0,14..32,600;0,14..32,700;1,14..32,400&display=swap');
</style>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<style>
    html, body, [class*="css"] {
        font-family: "Inter", "Segoe UI", system-ui, sans-serif;
    }
    .stApp {
        background: linear-gradient(165deg, #dde0ea 0%, #e8eaf2 40%, #e4e0f0 100%);
    }
    /* Rich purple sidebar (not plain white) */
    section[data-testid="stSidebar"] {
        background: linear-gradient(165deg, #3d2463 0%, #4e2f7a 22%, #5c3888 50%, #4a2f68 78%, #5a3d52 100%) !important;
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border-right: 1px solid rgba(255, 255, 255, 0.12);
        box-shadow: inset -8px 0 24px rgba(0, 0, 0, 0.12);
    }
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span:not([data-testid]),
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] small {
        color: rgba(255, 250, 255, 0.94) !important;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] [data-testid="stHeader"] {
        color: #fff !important;
        text-shadow: 0 1px 8px rgba(0,0,0,0.25);
    }
    section[data-testid="stSidebar"] [data-baseweb="select"] > div,
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background: rgba(255, 255, 255, 0.14) !important;
        border: 1px solid rgba(255, 255, 255, 0.28) !important;
        color: #fff !important;
    }
    section[data-testid="stSidebar"] [data-baseweb="select"] svg {
        fill: rgba(255,255,255,0.85) !important;
    }
    section[data-testid="stSidebar"] [data-baseweb="radio"] label,
    section[data-testid="stSidebar"] [data-baseweb="radio"] span {
        color: rgba(255, 250, 255, 0.95) !important;
    }
    section[data-testid="stSidebar"] [data-baseweb="radio"] svg {
        fill: #ffb366 !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.18) !important;
    }
    :root {
        --atlas-purple: #663399;
        --atlas-orange: #FF8C00;
    }
    div[data-testid="stSidebarHeader"] {
        background: linear-gradient(90deg, #663399 0%, #7d3eb8 40%, #FF8C00 100%);
        padding: 0.5rem 0.75rem;
        margin: -1rem -1rem 1rem -1rem;
        border-radius: 0 0.25rem 0.25rem 0;
    }
    .main .block-container {
        max-width: 1200px !important;
        margin-left: auto !important;
        margin-right: auto !important;
        padding: 1.25rem 1.5rem 2rem 1.5rem;
        background: rgba(255, 255, 255, 0.42);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.55);
        box-shadow: 0 12px 40px rgba(31, 38, 135, 0.08);
    }
    .main .block-container h1 {
        color: #663399;
        border-bottom: 3px solid #FF8C00;
        padding-bottom: 0.35rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.35rem;
        background: rgba(255,255,255,0.55);
        backdrop-filter: blur(8px);
        border-radius: 14px;
        padding: 0.4rem 0.55rem;
        border: 1px solid rgba(102, 51, 153, 0.12);
        box-shadow: 0 4px 20px rgba(31, 38, 135, 0.06);
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 15px;
        font-weight: 600;
        border-radius: 11px !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .stTabs [data-baseweb="tab-list"] button:hover {
        transform: translateY(-1px);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, rgba(102,51,153,0.14), rgba(255,140,0,0.12)) !important;
        color: #4a1f7a !important;
    }
    /* Primary / secondary buttons — gradient + hover scale */
    div[data-testid="stButton"] > button {
        transition: transform 0.2s ease, box-shadow 0.2s ease, filter 0.2s ease !important;
        border-radius: 12px !important;
    }
    div[data-testid="stButton"] > button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 8px 24px rgba(102, 51, 153, 0.28) !important;
    }
    div[data-testid="stButton"] > button[kind="primary"],
    div[data-testid="stButton"] > button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #663399 0%, #8b4fc9 45%, #c76b1a 130%) !important;
        border: none !important;
        color: #fff !important;
    }
    div[data-testid="stButton"] > button[kind="secondary"] {
        background: rgba(255,255,255,0.75) !important;
        border: 1px solid rgba(102, 51, 153, 0.25) !important;
    }
    /* Bento / bordered Streamlit containers */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        transition: transform 0.25s ease, box-shadow 0.25s ease;
        border-radius: 16px !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 14px 36px rgba(31, 38, 135, 0.12) !important;
    }
    .atlas-callout {
        background: rgba(255, 255, 255, 0.38) !important;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.45);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.18);
        padding: 1rem 1.25rem;
        border-radius: 15px;
        margin: 0.5rem 0 1rem 0;
    }
    .atlas-metric-strip {
        display: flex;
        flex-wrap: wrap;
        gap: 0.75rem;
        margin: 0.5rem 0 1rem 0;
    }
    .atlas-metric-chip {
        background: linear-gradient(135deg, rgba(102,51,153,0.1), rgba(255,140,0,0.08));
        border: 1px solid rgba(102, 51, 153, 0.18);
        border-radius: 12px;
        padding: 0.65rem 0.9rem;
        font-size: 0.92rem;
    }
    .atlas-metric-chip strong { color: #663399; }
    .risk-low {
        background: linear-gradient(135deg, rgba(212, 237, 218, 0.95), rgba(212, 237, 218, 0.6));
        color: #155724;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid rgba(21, 87, 36, 0.15);
    }
    .risk-medium {
        background: linear-gradient(135deg, rgba(255, 243, 205, 0.95), rgba(255, 243, 205, 0.55));
        color: #856404;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid rgba(133, 100, 4, 0.12);
    }
    .risk-high {
        background: linear-gradient(135deg, rgba(248, 215, 218, 0.95), rgba(248, 215, 218, 0.55));
        color: #721c24;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid rgba(114, 28, 36, 0.12);
    }
    /* Journal desk: paper-style textarea after box opens */
    .atlas-journal-dialogue {
        background: rgba(255, 255, 255, 0.55);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(102, 51, 153, 0.22);
        border-radius: 14px;
        padding: 12px 16px;
        margin: 0 0 10px 0;
        font-size: 0.95rem;
        line-height: 1.5;
        color: #3d2858;
        box-shadow: 0 6px 20px rgba(102, 51, 153, 0.08);
    }
    .atlas-journal-dialogue em { color: #663399; font-style: normal; font-weight: 600; }
    section.main [data-testid="stTextArea"] textarea {
        background: linear-gradient(180deg, #fffef9 0%, #faf4ea 100%) !important;
        border: 2px solid rgba(102, 51, 153, 0.38) !important;
        border-radius: 14px !important;
        box-shadow:
          inset 0 0 0 1px rgba(255,255,255,0.6),
          inset 0 0 48px rgba(255, 220, 180, 0.12),
          0 8px 28px rgba(102, 51, 153, 0.14) !important;
        font-family: "Georgia", "Palatino Linotype", "Book Antiqua", serif !important;
        line-height: 1.55 !important;
        color: #2d2438 !important;
        min-height: 200px !important;
        transition: box-shadow 0.25s ease, border-color 0.25s ease !important;
    }
    section.main [data-testid="stTextArea"] textarea:focus {
        border-color: rgba(255, 140, 0, 0.65) !important;
        box-shadow:
          inset 0 0 0 1px rgba(255,255,255,0.7),
          0 0 0 3px rgba(102, 51, 153, 0.2),
          0 10px 32px rgba(102, 51, 153, 0.18) !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ============ SIDEBAR (participant flow) ============
st.sidebar.title("Atlas Clinical Insights")
st.sidebar.caption("Participant journals → summaries, ASAM map, risk, curriculum fit.")
st.sidebar.markdown("---")

selected_demo = st.sidebar.selectbox(
    "Load example (optional):",
    ["Custom Input"] + list(demo_data.keys()),
)

entry_split_mode = st.sidebar.radio(
    "How are entries separated?",
    (
        "Line breaks (one entry per line)",
        "Commas (between Day N: blocks)",
    ),
    help="Use commas only for a single line like: Day 1: ..., Day 5: ...",
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Why this matters:** cuts manual chart review time and surfaces dropout risk before AMAs."
)

# One-time typewriter after splash (above tabs so it isn’t skipped if another tab is visible first)
if st.session_state.get("intro_played") and not st.session_state.get(
    "atlas_typewriter_done", False
):
    _typewriter_line_html("Interactive Journaling…", speed_ms=42)
    st.session_state["atlas_typewriter_done"] = True
elif st.session_state.get("intro_played"):
    st.markdown("### Interactive Journaling…")

# ============ TOP-LEVEL NAV ============
# st.tabs() does not keep the selected tab across reruns; any button (e.g. Open your journal)
# triggers a rerun and the UI jumps back to the first tab. Use session-backed navigation instead.
_NAV_MAIN = ("how", "participant", "cohort")
_NAV_LABELS = {
    "how": "📖 How it works",
    "participant": "🧑‍⚕️ Participant analysis",
    "cohort": "📊 Cohort & org insights",
}
st.session_state.setdefault("atlas_main_nav", "how")
st.radio(
    "main_section",
    options=list(_NAV_MAIN),
    format_func=lambda v: _NAV_LABELS[v],
    horizontal=True,
    key="atlas_main_nav",
    label_visibility="collapsed",
)
main_nav = st.session_state["atlas_main_nav"]

if main_nav == "how":
    st.markdown(
        '<div class="atlas-callout"><strong>For facilitators:</strong> '
        "Paste or load sample journals, run <strong>Analyze</strong>, then use the "
        "summary and ASAM quotes as a <em>draft</em> for case notes—always apply your "
        "clinical judgment.</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="atlas-callout"><strong>For admins / clinical directors:</strong> '
        "The <strong>Cohort & org insights</strong> tab batches demo participants to show "
        "dimension coverage, risk distribution, and Gemini-suggested curriculum priorities "
        "across the sample.</div>",
        unsafe_allow_html=True,
    )
    st.subheader("What the app produces")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**1. Clinical summary**")
        st.caption("3–4 sentence case-manager-style narrative from journals.")
    with c2:
        st.markdown("**2. ASAM dimension map**")
        st.caption("Six criteria with present / not detected + supporting quotes.")
    with c3:
        st.markdown("**3. Risk & stage**")
        st.caption("Dropout risk 0–1, stage of change, and facilitator-style next steps.")
    st.markdown("---")
    st.subheader("Curriculum recommendations (Gemini)")
    st.markdown(
        f"Modules are chosen only from this catalog: **{len(ATLAS_CURRICULUM_MODULES)}** "
        "Atlas-style topics (e.g. MOUD education, coping skills, relapse prevention)."
    )
    st.dataframe(
        [{"Module": m} for m in ATLAS_CURRICULUM_MODULES],
        width="stretch",
        hide_index=True,
    )

elif main_nav == "participant":
    st.title("Atlas Clinical Insights Engine")
    st.markdown(
        "**Purpose:** Analyze participant journals for summaries, ASAM mapping, dropout risk, "
        "and AI-matched curriculum ideas."
    )

    if selected_demo == "Custom Input":
        # Append transcript *before* st.text_area: Streamlit forbids mutating a widget's
        # session key after that widget is rendered in the same run.
        transcribe_just_appended = False
        if "pending_journal_append" in st.session_state:
            append = st.session_state.pop("pending_journal_append")
            cur = st.session_state.get("participant_journal_text", "")
            st.session_state["participant_journal_text"] = (
                (cur + "\n" + append).strip() if cur else append
            )
            transcribe_just_appended = True

        st.session_state.setdefault("journal_desk_open", False)
        if transcribe_just_appended:
            st.session_state["journal_desk_open"] = True

        st.caption(
            "Open the journal desk to type or dictate. Speech in any language is transcribed and "
            "translated to **English** with Gemini (same API key as analysis)."
        )

        if not st.session_state["journal_desk_open"]:
            components.html(_html_journal_desk_closed(), height=380, scrolling=False)
            st.markdown(
                '<p style="text-align:center;color:#5a4578;font-size:0.9rem;margin:0.35rem 0 0.15rem 0;">'
                "The box is <strong>shut</strong> — click to open it and start journaling.</p>",
                unsafe_allow_html=True,
            )
            if st.button("📖 Open your journal", key="atlas_open_journal_desk", type="primary", width="stretch"):
                st.session_state["journal_desk_open"] = True
        if st.session_state["journal_desk_open"]:
            st.markdown(
                '<div class="atlas-journal-dialogue">'
                "<strong>Example rhythm:</strong> <em>Day 1:</em> what feels hardest right now — "
                "<em>Day 5:</em> what shifted, even a little. One line per entry, or commas between "
                "<em>Day N:</em> blocks.</div>",
                unsafe_allow_html=True,
            )
            st.text_area(
                "Journal entries (line breaks, or comma-separated between Day N: blocks):",
                height=200,
                placeholder="Day 1: I'm struggling...\nDay 5: Feeling better...",
                key="participant_journal_text",
            )
            if transcribe_just_appended:
                st.success("Transcribed text was added to the journal box. Edit if needed, then **Analyze**.")

            mic_blocked, page_url = _microphone_blocked_by_browser_origin()
            if mic_blocked:
                st.error(
                    "**Microphone will not work on this URL (browser security).**\n\n"
                    f"You opened: `{page_url}` — **Not secure** HTTP on a LAN IP. Chrome/Edge **block** "
                    "microphone access unless you use **HTTPS** or **`http://localhost:8501`** / **`http://127.0.0.1:8501`**.\n\n"
                    "**What you see:** recorders may turn purple or show an error, but **no audio is captured**.\n\n"
                    "**Fix (pick one):**  \n"
                    "• On the PC running Streamlit, use **`http://localhost:8501`** in the browser.  \n"
                    "• Or put the app behind **HTTPS** (e.g. reverse proxy + TLS).  \n"
                    "• **Workaround:** use **Upload audio file** — it does not need the microphone."
                )

            with st.expander("How to enable the microphone (Windows / browser)", expanded=False):
                st.markdown(
                    """
1. **Use a supported browser:** Chrome or Edge usually work best with microphone capture.
2. **Run the app on `http://localhost:8501`** (or HTTPS). Mic access needs a *secure context* (localhost counts).
3. When the browser asks **“Allow microphone?”**, choose **Allow** for this site.
4. **Windows:** Settings → Privacy → Microphone → let desktop apps / Chrome access the mic.
5. **Do not use** `http://192.168.x.x:8501` or another LAN IP over plain HTTP — the **mic will be blocked** (browser policy). Use **`localhost`** or **HTTPS** instead.
6. If Streamlit’s built-in recorder shows an error, use **Upload audio** (always works).

**What happens after recording:** audio is sent to Gemini (same API key as analysis), transcribed, and translated to **English** for the journal box.
                    """
                )

            v_col1, v_col2 = st.columns([1, 1])
            with v_col1:
                if getattr(st, "audio_input", None):
                    st.caption(
                        "**Built-in recorder** — when you stop recording, audio is transcribed automatically "
                        "(any language → English)."
                    )
                    voice = st.audio_input(
                        "Record voice (Streamlit)",
                        key="participant_voice_audio",
                        help="Stops trigger processing. Same clip is not transcribed twice (tracked by hash).",
                        disabled=mic_blocked,
                    )
                    if not mic_blocked and voice is not None:
                        if hasattr(voice, "seek"):
                            voice.seek(0)
                        raw = voice.read()
                        if raw:
                            audio_hash = hashlib.sha256(raw).hexdigest()
                            if st.session_state.get("last_streamlit_audio_hash") != audio_hash:
                                try:
                                    with st.spinner("Translating speech to English…"):
                                        mime = getattr(voice, "type", None)
                                        txt = transcribe_audio_to_english(raw, mime)
                                    st.session_state["last_streamlit_audio_hash"] = audio_hash
                                    st.session_state["pending_journal_append"] = txt
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Mic transcription failed: {e}")
                                    st.session_state["last_streamlit_audio_hash"] = audio_hash
                else:
                    st.warning(
                        "Upgrade Streamlit for built-in recording: `pip install 'streamlit>=1.33'`"
                    )
            with v_col2:
                st.caption("**Upload** — choosing a file transcribes it once (same file won’t duplicate).")
                up_audio = st.file_uploader(
                    "Upload audio file",
                    type=["wav", "webm", "mp3", "m4a", "ogg"],
                    key="participant_voice_upload",
                    help="Processed automatically when you pick a new file.",
                )
                if up_audio is not None:
                    raw = up_audio.read()
                    if raw:
                        upload_hash = hashlib.sha256(raw).hexdigest()
                        if st.session_state.get("last_upload_audio_hash") != upload_hash:
                            try:
                                with st.spinner("Translating uploaded audio to English…"):
                                    mime = getattr(up_audio, "type", None)
                                    txt = transcribe_audio_to_english(raw, mime)
                                st.session_state["last_upload_audio_hash"] = upload_hash
                                st.session_state["pending_journal_append"] = txt
                                st.rerun()
                            except Exception as e:
                                st.error(f"Upload transcription failed: {e}")
                                st.session_state["last_upload_audio_hash"] = upload_hash

            if audio_recorder is not None:
                with st.expander(
                    "Alternate microphone (recommended if Streamlit recorder shows an error)",
                    expanded=False,
                ):
                    st.caption(
                        "Hold the mic to speak, release to finish — transcription runs automatically (English output)."
                    )
                    if mic_blocked:
                        st.warning("Alternate mic is disabled here because the browser blocks microphone on this URL.")
                    alt_wav = None if mic_blocked else audio_recorder(
                        text="Hold to record",
                        recording_color="#663399",
                        neutral_color="#94a3b8",
                        icon_name="microphone",
                        pause_threshold=3.0,
                        energy_threshold=0.008,
                        sample_rate=None,
                        key="atlas_alt_mic",
                    )
                    if alt_wav:
                        st.audio(alt_wav, format="audio/wav")
                        alt_hash = hashlib.sha256(alt_wav).hexdigest()
                        if st.session_state.get("last_alt_mic_hash") != alt_hash:
                            try:
                                with st.spinner("Translating speech to English…"):
                                    txt = transcribe_audio_to_english(alt_wav, "audio/wav")
                                st.session_state["last_alt_mic_hash"] = alt_hash
                                st.session_state["pending_journal_append"] = txt
                                st.rerun()
                            except Exception as e:
                                st.error(f"Alternate mic transcription failed: {e}")
                                st.session_state["last_alt_mic_hash"] = alt_hash
            else:
                st.caption(
                    "Optional: `pip install audio-recorder-streamlit` for an alternate mic that works in more browsers."
                )

        journal_text = st.session_state.get("participant_journal_text", "")
    else:
        journal_text = "\n".join(demo_data[selected_demo])
        st.info(f"Loaded: **{selected_demo}**")

    if st.button("Analyze", type="primary", width="stretch"):
        if not journal_text.strip():
            if selected_demo == "Custom Input" and not st.session_state.get("journal_desk_open", False):
                st.error("Open your journal first (**📖 Open your journal**), then type or dictate entries.")
            else:
                st.error("Please enter at least one journal entry.")
        else:
            entries = parse_journal_entries(journal_text, entry_split_mode)
            if not entries:
                st.error("Could not parse any journal entries. Check separators or add text.")
            else:
                with st.status("AI analysis", expanded=True) as ai_status:
                    ai_status.write("Analyzing journals with Gemini…")
                    result = analyze_journals(entries)
                    ai_status.write("Matching curriculum modules to Atlas catalog…")
                    mod_rec = recommend_modules_for_analysis(result)
                st.session_state.result = result
                st.session_state.module_rec = mod_rec
                st.success("Analysis complete!")

    if "result" in st.session_state:
        result = st.session_state.result
        mod_rec = st.session_state.get("module_rec") or {}

        tab1, tab2, tab3, tab4 = st.tabs(
            ["Clinical Summary", "ASAM dimensions", "Risk assessment", "Insights & curriculum"]
        )

        with tab1:
            st.subheader("Clinical summary")
            st.markdown(f"> {result.get('summary', 'No summary returned.')}")
            st.caption("Draft only—edit to fit your program’s documentation standards.")

        with tab2:
            with st.container(border=True):
                st.subheader("ASAM criteria dimensions")
                cols = st.columns(2)
                for i in range(6):
                    dimension = ASAM_DIMENSIONS[i]
                    key = f"dimension_{i + 1}"
                    with cols[i % 2]:
                        if key in result.get("asam", {}):
                            info = result["asam"][key]
                            status = "Present" if info.get("present") else "Not detected"
                            st.markdown(f"**{dimension}**")
                            st.markdown(status)
                            if info.get("quote"):
                                st.caption(f"*\"{info['quote']}\"*")
                        else:
                            st.markdown(f"**{dimension}**")
                            st.markdown("Not detected")

        with tab3:
            risk_score = _risk_float(result.get("risk_score"), 0.5)
            risk_score = max(0.0, min(1.0, risk_score))
            stage = result.get("stage_of_change", "Unknown")
            with st.container(border=True):
                st.subheader("Dropout risk assessment")
                col1, col2 = st.columns([2, 1])
                with col1:
                    fig = go.Figure(
                        go.Indicator(
                            mode="gauge+number",
                            value=risk_score * 100,
                            title={"text": "Dropout risk score (%)"},
                            domain={"x": [0, 1], "y": [0, 1]},
                            gauge={
                                "axis": {"range": [0, 100]},
                                "bar": {"color": "#663399"},
                                "steps": [
                                    {"range": [0, 33], "color": "#d4edda"},
                                    {"range": [33, 67], "color": "#fff3cd"},
                                    {"range": [67, 100], "color": "#f8d7da"},
                                ],
                                "threshold": {
                                    "line": {"color": "red", "width": 4},
                                    "thickness": 0.75,
                                    "value": 90,
                                },
                            },
                        )
                    )
                    fig.update_layout(height=300, transition=dict(duration=900, easing="cubic-in-out"))
                    st.plotly_chart(fig, width="stretch")

                with col2:
                    if risk_score < 0.33:
                        st.markdown(
                            '<div class="risk-low"><b>LOW RISK</b></div>',
                            unsafe_allow_html=True,
                        )
                    elif risk_score < 0.67:
                        st.markdown(
                            '<div class="risk-medium"><b>MEDIUM RISK</b></div>',
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            '<div class="risk-high"><b>HIGH RISK</b></div>',
                            unsafe_allow_html=True,
                        )

                st.markdown(f"**Stage of change:** {stage}")
                st.info("Consider a check-in or re-engagement plan when risk is elevated.")

        with tab4:
            with st.container(border=True):
                st.subheader("Clinical insights & curriculum")
                st.markdown("#### Suggested next actions")
                if risk_score > 0.67:
                    st.markdown("- Schedule a timely check-in or outreach")
                    st.markdown("- Revisit treatment goals collaboratively")
                if stage == "Pre-Contemplation":
                    st.markdown("- Low-pressure engagement and motivational content")
                elif stage == "Contemplation":
                    st.markdown("- Explore ambivalence; co-create a small action step")
                elif stage == "Action":
                    st.markdown("- Reinforce wins; build on routines that are working")

                st.markdown("#### Gemini curriculum picks (from Atlas-style catalog)")
                for m in mod_rec.get("modules", []):
                    st.markdown(f"- **{m}**")
                if mod_rec.get("rationale"):
                    st.caption(mod_rec["rationale"])

    st.markdown("---")
    st.caption("Atlas Clinical Insights Engine · Powered by Gemini")

else:
    st.title("Cohort & organizational insights")
    st.markdown(
        "**Day 3:** Run each demo participant through the same journal brain, then view "
        "aggregate ASAM coverage, risk mix, and org-level curriculum priorities."
    )

    if not cohort_participants:
        st.warning(
            "No cohort data found. Add a `cohort` array to `demo_data.json` next to `app.py`."
        )
    else:
        st.subheader("Demo cohort")
        st.dataframe(
            [
                {
                    "ID": p.get("id"),
                    "Label": p.get("label"),
                    "Program": p.get("program", ""),
                    "Entries": len(p.get("entries") or []),
                }
                for p in cohort_participants
            ],
            width="stretch",
            hide_index=True,
        )

        n_participants = len(cohort_participants)
        est_calls = n_participants + 1
        st.caption(
            f"This uses **~{est_calls}** Gemini calls per run ({n_participants} analyses + 1 cohort recommendation). "
            "Stay within your API quota."
        )

        if st.button("Run cohort analysis", type="primary", width="stretch"):
            rows_out = []
            with st.status("Cohort analysis pipeline", expanded=True) as cohort_status:
                cohort_status.write("Running each participant through Gemini…")
                for idx, p in enumerate(cohort_participants):
                    entries = p.get("entries") or []
                    cohort_status.write(
                        f"**{idx + 1}/{n_participants}** · {p.get('label', p.get('id'))}"
                    )
                    analyzed = analyze_journals(entries)
                    rows_out.append(
                        {
                            **analyzed,
                            "_meta": {
                                "id": p.get("id"),
                                "label": p.get("label"),
                                "program": p.get("program"),
                            },
                        }
                    )
                cohort_status.write("Aggregating ASAM coverage & dropout risk…")
                dim_rows, risk_buckets = aggregate_cohort_results(rows_out)
                rates_tuples = [(d["dimension"], d["presence_rate"]) for d in dim_rows]
                cohort_status.write("Org-level curriculum recommendations (Gemini)…")
                cohort_mod = recommend_cohort_modules_from_rates(rates_tuples)

            st.session_state.cohort_rows = rows_out
            st.session_state.cohort_dim_rows = dim_rows
            st.session_state.cohort_risk_buckets = risk_buckets
            st.session_state.cohort_mod = cohort_mod
            st.success("Cohort analysis complete.")

        if st.session_state.get("cohort_dim_rows"):
            dim_rows = st.session_state.cohort_dim_rows
            risk_buckets = st.session_state.cohort_risk_buckets
            cohort_mod = st.session_state.get("cohort_mod") or {}

            with st.container(border=True):
                st.markdown("### 🎯 ASAM coverage (cohort)")
                n_cohort = dim_rows[0]["n"] if dim_rows else 0
                avg_cov = sum(d["presence_rate"] for d in dim_rows) / max(len(dim_rows), 1) * 100
                best = max(dim_rows, key=lambda d: d["presence_rate"]) if dim_rows else None
                worst = min(dim_rows, key=lambda d: d["presence_rate"]) if dim_rows else None

                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    st.metric("👥 Participants", f"{n_cohort}")
                with m2:
                    st.metric("📈 Avg coverage", f"{avg_cov:.1f}%", help="Mean % of participants with evidence per dimension")
                with m3:
                    if best:
                        st.metric("✅ Highest", best["dimension"][:28] + "…" if len(best["dimension"]) > 28 else best["dimension"], f"{best['presence_rate']*100:.0f}%")
                    else:
                        st.metric("✅ Highest", "—", "—")
                with m4:
                    if worst:
                        st.metric("📌 Lowest", worst["dimension"][:28] + "…" if len(worst["dimension"]) > 28 else worst["dimension"], f"{worst['presence_rate']*100:.0f}%")
                    else:
                        st.metric("📌 Lowest", "—", "—")

                categories = [d["dimension"] for d in dim_rows]
                values = [d["presence_rate"] * 100 for d in dim_rows]
                r_closed = values + [values[0]] if values else []
                theta_closed = categories + [categories[0]] if categories else []

                cov_col, radar_col = st.columns([1, 1.15])
                with cov_col:
                    st.caption("Per-dimension: % of participants with journal evidence")
                    st.dataframe(
                        [
                            {
                                "Dimension": d["dimension"],
                                "With evidence": f"{d['present_count']}/{d['n']}",
                                "%": f"{d['presence_rate']*100:.0f}%",
                            }
                            for d in dim_rows
                        ],
                        width="stretch",
                        hide_index=True,
                        height=360,
                    )
                with radar_col:
                    if not values or max(values) <= 0:
                        st.info("📭 All dimensions are at **0%** for this cohort run — the radar stays collapsed at the center. Check journal content or run analysis again.")
                    fig_radar = go.Figure(
                        data=go.Scatterpolar(
                            r=r_closed,
                            theta=theta_closed,
                            fill="toself",
                            fillcolor="rgba(102, 51, 153, 0.22)",
                            line=dict(color="#663399", width=2.5),
                            marker=dict(color="#FF8C00", size=6, symbol="circle"),
                            hovertemplate="<b>%{theta}</b><br>%{r:.0f}%<extra></extra>",
                        )
                    )
                    fig_radar.update_layout(
                        polar=dict(
                            radialaxis=dict(visible=True, range=[0, 100], tickformat=".0f", ticksuffix="%"),
                            bgcolor="rgba(255,255,255,0.35)",
                        ),
                        paper_bgcolor="rgba(0,0,0,0)",
                        height=420,
                        margin=dict(l=30, r=30, t=30, b=30),
                        showlegend=False,
                        title=dict(text="Radar (same numbers as table)", font=dict(size=14, color="#663399")),
                        transition=dict(duration=1100, easing="cubic-in-out"),
                    )
                    st.plotly_chart(fig_radar, width="stretch")

                st.markdown("### ⚠️ Dropout risk distribution")
                pr1, pr2, pr3 = st.columns(3)
                with pr1:
                    st.metric("🟢 Low (<33%)", f"{risk_buckets['low']}", delta=None)
                with pr2:
                    st.metric("🟡 Medium", f"{risk_buckets['medium']}", delta=None)
                with pr3:
                    st.metric("🔴 High (≥67%)", f"{risk_buckets['high']}", delta=None)

                pie_labels = ["Low (<33%)", "Medium", "High (≥67%)"]
                pie_values = [
                    risk_buckets["low"],
                    risk_buckets["medium"],
                    risk_buckets["high"],
                ]
                fig_pie = go.Figure(
                    data=[
                        go.Pie(
                            labels=pie_labels,
                            values=pie_values,
                            hole=0.42,
                            marker=dict(colors=["#b8e0c8", "#ffe4a8", "#f5b8c0"], line=dict(color="#fff", width=2)),
                            textinfo="label+percent+value",
                            textposition="outside",
                        )
                    ]
                )
                fig_pie.update_layout(
                    height=360,
                    paper_bgcolor="rgba(0,0,0,0)",
                    margin=dict(t=30, b=30, l=20, r=20),
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.15, x=0.5, xanchor="center"),
                    transition=dict(duration=900, easing="cubic-in-out"),
                )
                st.plotly_chart(fig_pie, width="stretch")

                st.markdown("### 📚 Top org curriculum priorities (Gemini)")
                for m in cohort_mod.get("modules", []):
                    st.markdown(f"- 📌 **{m}**")
                if cohort_mod.get("rationale"):
                    st.info(cohort_mod["rationale"])

                with st.expander("Per-participant risk scores"):
                    st.dataframe(
                        [
                            {
                                "Label": r.get("_meta", {}).get("label"),
                                "Risk": round(_risk_float(r.get("risk_score"), 0.5), 3),
                                "Stage": r.get("stage_of_change", ""),
                            }
                            for r in st.session_state.cohort_rows
                        ],
                        width="stretch",
                        hide_index=True,
                    )

