# 🎯 Step-by-Step Cursor Implementation Guide
## Day 1: Get Working Code in Cursor (No Mistakes)

---

## ✅ Prerequisites Check

Before you start, make sure you have:
- [ ] Cursor installed (or VS Code)
- [ ] Python 3.9+ installed (`python --version`)
- [ ] Gemini API key ready (from https://aistudio.google.com/apikey)
- [ ] Terminal/Command Prompt open
- [ ] 30 minutes of focus time

---

## 📁 STEP 1: Create Folder Structure in Cursor

**In Cursor, open Terminal:**
- Mac/Linux: `Ctrl+` (backtick)
- Windows: `Ctrl+` (backtick)

**Copy-paste this entire block:**

```bash
# Create project folder
mkdir atlas-ai-demo
cd atlas-ai-demo

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# On Mac/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Verify venv is active (you should see (venv) in terminal)
```

**Expected result:** Terminal shows `(venv)` at the start of the line.

If it doesn't, you're not in the virtual environment. Stop and fix this before proceeding.

---

## 📦 STEP 2: Install Dependencies

**Still in the same terminal (with (venv) active), copy-paste:**

```bash
pip install streamlit google-generativeai python-dotenv plotly
```

**Wait for it to finish.** You'll see:
```
Successfully installed streamlit-1.28.0 google-generativeai-0.3.0 ...
```

---

## 🔑 STEP 3: Create .env File with API Key

**In Cursor, create a new file:**

1. Click **File → New File**
2. Name it: `.env`
3. Copy-paste this (replace `YOUR_API_KEY_HERE`):

```
GEMINI_API_KEY=YOUR_API_KEY_HERE
```

**Example (NOT real):**
```
GEMINI_API_KEY=AIzaSyD1234567890abcdefghijklmnopqrstuvwxyz
```

**Save it** (Ctrl+S)

---

## ✅ STEP 4: Test Gemini Works (5 minutes)

**In Cursor, create a new file:**

1. Click **File → New File**
2. Name it: `test_gemini.py`
3. Copy-paste this entire code:

```python
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load API key from .env
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Test
model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content("Say 'Hello from Gemini!' exactly.")
print(response.text)
```

**Save it** (Ctrl+S)

**In terminal, run:**
```bash
python test_gemini.py
```

**Expected output:**
```
Hello from Gemini!
```

✅ **If you see that message: Gemini is working. Continue.**

❌ **If you see an error:**
- `ModuleNotFoundError`: Run `pip install google-generativeai` again
- `GEMINI_API_KEY not found`: Check your `.env` file has the exact format above
- `403 Access Denied`: Your API key is wrong, get a new one

---

## 🧠 STEP 5: Create brain.py (The AI Logic)

**In Cursor, create a new file:**

1. Click **File → New File**
2. Name it: `brain.py`
3. Copy-paste this entire code (it's complete, don't modify):

```python
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

ASAM_DIMENSIONS = [
    "Acute Intoxication/Withdrawal Potential",
    "Biomedical Conditions & Complications",
    "Emotional/Behavioral Conditions",
    "Relapse/Recurrence Potential",
    "Recovery/Living Environment",
    "Readiness to Change"
]

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
    
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content([system_prompt, combined_text])
    
    try:
        result = json.loads(response.text)
        return result
    except json.JSONDecodeError:
        # Fallback if Gemini response isn't valid JSON
        print("Warning: JSON parsing failed, returning defaults")
        return {
            "summary": "Error parsing response",
            "asam": {f"dimension_{i}": {"present": False, "quote": ""} for i in range(1, 7)},
            "risk_score": 0.5,
            "stage_of_change": "Unknown"
        }


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
```

**Save it** (Ctrl+S)

**Test it in terminal:**
```bash
python brain.py
```

**Expected output:**
```json
{
  "summary": "Participant is showing positive progress...",
  "asam": {
    "dimension_1": {"present": false, "quote": ""},
    ...
  },
  "risk_score": 0.25,
  "stage_of_change": "Action"
}
```

✅ **If you see JSON output: Your brain.py works. Continue to Step 6.**

---

## 💻 STEP 6: Create app.py (The Streamlit Dashboard)

**In Cursor, create a new file:**

1. Click **File → New File**
2. Name it: `app.py`
3. Copy-paste this entire code:

```python
import streamlit as st
import json
from brain import analyze_journals, ASAM_DIMENSIONS
import plotly.graph_objects as go

st.set_page_config(page_title="Atlas Clinical Insights", layout="wide")

# ============ STYLING ============
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 16px;
        font-weight: bold;
    }
    .risk-low {
        background-color: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 5px;
    }
    .risk-medium {
        background-color: #fff3cd;
        color: #856404;
        padding: 10px;
        border-radius: 5px;
    }
    .risk-high {
        background-color: #f8d7da;
        color: #721c24;
        padding: 10px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# ============ SIDEBAR ============
st.sidebar.title("📋 Atlas Clinical Insights Engine")
st.sidebar.markdown("---")

# Demo data selector
demo_data = {
    "Example: Opioid Treatment": [
        "Day 1: I'm struggling with cravings. My family wants to help but I feel ashamed. Started NA meetings this week.",
        "Day 5: Attended 3 meetings. Feeling more confident. Still have withdrawal symptoms but the counselor is helping.",
        "Day 10: Two weeks clean now. Learned about my triggers - stress and loneliness. Started calling sponsor daily."
    ],
    "Example: Adolescent Treatment": [
        "I don't really know why I'm here. My parents say I have a 'problem' but it's not that bad.",
        "Talked with counselor about why weed felt necessary. Started realizing I was avoiding feeling sad about dad.",
        "Made a plan to call dad this week. Scared but ready to try."
    ],
    "Example: Trauma": [
        "Had another nightmare about the accident. Can't sleep without anxiety medication.",
        "Counselor taught me breathing exercises. They actually helped during the panic attack yesterday.",
        "Used my grounding technique when triggered today. Felt empowering to manage it myself."
    ]
}

selected_demo = st.sidebar.selectbox(
    "Load Example (optional):",
    ["Custom Input"] + list(demo_data.keys())
)

st.sidebar.markdown("---")

# ============ MAIN CONTENT ============
st.title("Atlas Clinical Insights Engine")
st.markdown("**Purpose:** Analyze participant journals to generate clinical summaries, ASAM dimension mapping, and dropout risk flags.")

# Get input
if selected_demo == "Custom Input":
    journal_text = st.text_area(
        "Paste journal entries (one per line, separated by line breaks):",
        height=200,
        placeholder="Day 1: I'm struggling...\nDay 5: Feeling better..."
    )
else:
    journal_text = "\n".join(demo_data[selected_demo])
    st.info(f"✓ Loaded: {selected_demo}")

# Process button
if st.button("🔍 Analyze Entries", use_container_width=True):
    if not journal_text.strip():
        st.error("Please enter at least one journal entry.")
    else:
        with st.spinner("Analyzing with AI..."):
            entries = [e.strip() for e in journal_text.split("\n") if e.strip()]
            result = analyze_journals(entries)
        
        st.session_state.result = result
        st.success("Analysis complete!")

# ============ DISPLAY RESULTS ============
if "result" in st.session_state:
    result = st.session_state.result
    
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📝 Clinical Summary", "🎯 ASAM Dimensions", "⚠️ Risk Assessment", "📊 Insights"]
    )
    
    # TAB 1: Summary
    with tab1:
        st.subheader("Clinical Summary")
        st.markdown(f"> {result['summary']}")
        st.caption("Use this as a draft for your case note.")
    
    # TAB 2: ASAM Dimensions
    with tab2:
        st.subheader("ASAM Criteria Dimensions")
        cols = st.columns(2)
        for i in range(6):
            dimension = ASAM_DIMENSIONS[i]
            key = f"dimension_{i+1}"
            with cols[i % 2]:
                if key in result.get('asam', {}):
                    info = result['asam'][key]
                    status = "✅ Present" if info.get('present') else "⬜ Not detected"
                    st.markdown(f"**{dimension}**")
                    st.markdown(f"{status}")
                    if info.get('quote'):
                        st.caption(f"*\"{info['quote']}\"*")
                else:
                    st.markdown(f"**{dimension}**")
                    st.markdown("⬜ Not detected")
    
    # TAB 3: Risk Assessment
    with tab3:
        st.subheader("Dropout Risk Assessment")
        risk_score = result.get('risk_score', 0.5)
        stage = result.get('stage_of_change', 'Unknown')
        
        # Risk gauge
        col1, col2 = st.columns([2, 1])
        with col1:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=risk_score * 100,
                title={'text': "Dropout Risk Score"},
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 33], 'color': "#d4edda"},
                        {'range': [33, 67], 'color': "#fff3cd"},
                        {'range': [67, 100], 'color': "#f8d7da"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if risk_score < 0.33:
                st.markdown('<div class="risk-low"><b>🟢 LOW RISK</b></div>', unsafe_allow_html=True)
            elif risk_score < 0.67:
                st.markdown('<div class="risk-medium"><b>🟡 MEDIUM RISK</b></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="risk-high"><b>🔴 HIGH RISK</b></div>', unsafe_allow_html=True)
        
        st.markdown(f"**Stage of Change:** {stage}")
        st.info("💡 **Recommendation:** Consider a check-in call or re-engagement activity if risk is high.")
    
    # TAB 4: Insights
    with tab4:
        st.subheader("Clinical Insights & Next Steps")
        
        st.markdown("### Recommended Next Actions:")
        if risk_score > 0.67:
            st.markdown("- 📞 Schedule immediate check-in call")
            st.markdown("- 🎯 Revisit treatment goals")
        
        if stage == "Pre-Contemplation":
            st.markdown("- 📚 Introduce motivational materials")
            st.markdown("- 💬 Focus on engagement activities")
        elif stage == "Contemplation":
            st.markdown("- 🤝 Explore ambivalence in next session")
            st.markdown("- 📋 Co-create action plan")
        elif stage == "Action":
            st.markdown("- ✨ Reinforce progress and successes")
            st.markdown("- 📈 Build on momentum")
        
        st.markdown("### Suggested Curriculum Topics:")
        st.markdown("Based on ASAM dimensions, consider these Atlas modules:")
        st.markdown("- 🚨 Coping Skills")
        st.markdown("- 👥 Relationships & Communication")
        st.markdown("- 🏡 Building Support Networks")

st.markdown("---")
st.caption("Atlas Clinical Insights Engine | Powered by Gemini AI")
```

**Save it** (Ctrl+S)

---

## 🚀 STEP 7: Test Streamlit App Locally

**In terminal, run:**
```bash
streamlit run app.py
```

**Expected:**
- A new browser window opens
- Dashboard appears with purple/orange colors
- Sidebar shows "Load Example" dropdown

**Test the app:**
1. Click dropdown: "Load Example: Opioid Treatment"
2. You should see 3 journal entries appear
3. Click "🔍 Analyze Entries" button
4. Wait 30-60 seconds (Gemini is thinking)
5. You should see:
   - Tab 1: Summary text
   - Tab 2: ASAM dimensions with checkmarks
   - Tab 3: Risk gauge (colored)
   - Tab 4: Insights

✅ **If all tabs populate: Your app works!**

**Stop the app:**
- Press `Ctrl+C` in terminal

---

## 📋 STEP 8: Create requirements.txt

**In Cursor, create a new file:**

1. Click **File → New File**
2. Name it: `requirements.txt`
3. Copy-paste this:

```
streamlit==1.28.0
google-generativeai==0.3.0
python-dotenv==1.0.0
plotly==5.17.0
```

**Save it** (Ctrl+S)

---

## 📚 STEP 9: Create .gitignore (For GitHub)

**In Cursor, create a new file:**

1. Click **File → New File**
2. Name it: `.gitignore`
3. Copy-paste this:

```
.env
__pycache__/
*.pyc
venv/
.DS_Store
*.egg-info/
dist/
build/
.pytest_cache/
.streamlit/
```

**Save it** (Ctrl+S)

---

## 📄 STEP 10: Create README.md

**In Cursor, create a new file:**

1. Click **File → New File**
2. Name it: `README.md`
3. Copy-paste this:

```markdown
# Atlas Clinical Insights Engine

## Problem
Behavioral health facilitators read 100s of pages of journals. They need summaries, ASAM mapping, and risk flags **fast**.

## Solution
AI that auto-generates clinical insights from participant journal entries in seconds.

## Features
- **Clinical Summarization**: Converts journals into concise professional summaries
- **ASAM Dimension Mapping**: Auto-categorizes entries against 6 ASAM criteria
- **Risk Assessment**: Flags dropout/AMA risk on a 0-1 scale
- **Stage of Change Tracking**: Identifies Pre-Contemplation, Contemplation, or Action
- **Content Recommendations**: Suggests modules based on ASAM gaps

## How to Run Locally

```bash
# Clone repo
git clone <your-repo-url>
cd atlas-ai-demo

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with API key
echo "GEMINI_API_KEY=YOUR_KEY_HERE" > .env

# Run app
streamlit run app.py
```

Open http://localhost:8501 in your browser.

## Architecture

- `brain.py` - Gemini API logic (analyzes journals, returns JSON)
- `app.py` - Streamlit UI (dashboard with 4 tabs)
- `.env` - API key (not committed)
- `requirements.txt` - Dependencies

## Stack
- Python 3.9+
- Streamlit (UI)
- Gemini 1.5 Flash (LLM)
- Plotly (charts)

## Example Usage

1. Select "Load Example: Opioid Treatment"
2. Click "🔍 Analyze Entries"
3. Wait 30-60 seconds for AI analysis
4. View results in tabs:
   - Clinical Summary
   - ASAM Dimensions
   - Risk Assessment
   - Insights & Recommendations

## Next Steps
- Deploy to Streamlit Cloud
- Fine-tune on real clinical data
- Add facilitator feedback loop
- Integrate into Atlas workflow
```

**Save it** (Ctrl+S)

---

## ✅ STEP 11: Initialize Git (Optional but Recommended)

**In terminal:**

```bash
git init
git add .
git commit -m "feat: initial atlas ai demo with streamlit + gemini"
```

---

## 📁 Your Folder Should Look Like This

```
atlas-ai-demo/
├── venv/                    (virtual environment)
├── brain.py                 (AI logic)
├── app.py                   (Streamlit dashboard)
├── test_gemini.py          (test file - can delete later)
├── .env                     (API key - NEVER commit this)
├── .gitignore              (git ignore rules)
├── requirements.txt        (dependencies)
├── README.md               (documentation)
└── .git/                   (git repo)
```

---

## 🎉 You're Done with Day 1!

**What you've accomplished:**
✅ Gemini API key working
✅ `brain.py` analyzes journals → returns JSON
✅ `app.py` dashboard with 4 tabs
✅ Streamlit app runs locally
✅ 3 demo examples included
✅ Code committed to Git

**Next:** Read ATLAS_4DAY_PLAN.md Day 2 section when ready.

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'streamlit'"
```bash
pip install streamlit
```

### "(venv) not showing in terminal"
You're not in the virtual environment. Run:
```bash
# Mac/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### "GEMINI_API_KEY not found"
1. Check `.env` file exists in root folder
2. Check format: `GEMINI_API_KEY=AIza...` (no quotes, no spaces)
3. Restart terminal after creating `.env`

### "Streamlit app won't start"
```bash
# Kill any old process
pkill streamlit

# Try again
streamlit run app.py
```

### "Gemini returns 403 error"
Your API key is invalid or has been rotated. Get a new one: https://aistudio.google.com/apikey

### "JSON parsing error from Gemini"
Gemini sometimes returns non-JSON. This is handled in `brain.py` with a fallback. Re-run and it should work.

---

## ✨ You're Ready for Day 2

Once you confirm the app works locally:
1. Push code to GitHub
2. Move to Day 2: Deploy to Streamlit Cloud
3. Then Days 3-4: Polish + interview prep

**You're ahead of schedule.** 🚀

---

*If you get stuck on any step, the error message will tell you what's wrong. Copy the error message and Google it + the package name.*

*Most common issues: API key format, virtual environment not active, missing package install.*

*You've got this.* 💪
