# Atlas Clinical Insights Engine - 4-Day Build Plan
**Timeline: Days 1-4 Build | Days 5-6 Interview Prep**

---

## 🎯 Core Scope (MVP)
**What you're building:**
- A Streamlit dashboard that takes journal entries → outputs:
  1. **Clinical Summary** (for case manager)
  2. **ASAM Dimension Tagging** (which of 6 dimensions mentioned)
  3. **Risk Flag** (dropout risk: Low/Medium/High)

**What you're NOT building:**
- Database, user authentication, real data
- Complex ML models or fine-tuning
- Mobile app, APIs, or microservices

**Why this wins:**
- Solves real pain (facilitator reads 100s of pages → AI summarizes)
- Directly tied to their use case ("Ensure consistency," decrease AMAs)
- Shippable in 4 days with zero cost

---

## 📅 Day-by-Day Breakdown

### **DAY 1: Setup + Core Logic (6-8 hours)**

**Goal:** Get Gemini talking to your code. Prove the AI brain works.

**Steps:**
1. **Setup Cursor project** (5 min)
   ```bash
   mkdir atlas-ai-demo
   cd atlas-ai-demo
   ```

2. **Install dependencies** (5 min) - all free/built-in
   ```bash
   pip install streamlit google-generativeai python-dotenv
   ```

3. **Get Gemini API key** (5 min)
   - Go to: https://aistudio.google.com/apikey
   - Create key (free tier, no card needed)
   - Save in `.env` file (never commit)

4. **Write `brain.py`** (2 hours) - Use Cursor Composer
   - Function: `analyze_journals(journal_list) → dict`
   - Calls Gemini with system prompt
   - Returns: `{"summary": "...", "asam_dimensions": [...], "risk_score": 0.7}`

5. **Test in Python REPL** (1 hour)
   - Create 3 fake journal entries (copy from Atlas brochure examples)
   - Call `analyze_journals()` manually
   - Verify output format works

**Deliverable:** `brain.py` that takes text → returns structured data

**Commit message:** `feat: core AI logic with Gemini integration`

---

### **DAY 2: Streamlit Dashboard (6-8 hours)**

**Goal:** Build the UI. This is what the CPO will actually see.

**Steps:**

1. **Create `app.py`** structure with Cursor (2 hours)
   ```python
   import streamlit as st
   from brain import analyze_journals
   
   st.set_page_config(page_title="Atlas Clinical Insights", layout="wide")
   
   # Three main sections:
   # 1. Input area (text box for journal)
   # 2. Summary tab
   # 3. ASAM dimensions tab
   # 4. Risk assessment tab
   ```

2. **Build upload + processing flow** (2 hours)
   - Sidebar: "Paste journal entries (comma-separated)"
   - Button: "Analyze"
   - Shows loading spinner while Gemini processes

3. **Create output tabs** (2 hours)
   - **Tab 1 - Summary:** Formatted case note (like a real clinical doc)
   - **Tab 2 - ASAM Map:** Show which 6 dimensions are flagged + quotes from entries
   - **Tab 3 - Risk Score:** Color-coded badge (Green/Yellow/Red)

4. **Add demo data** (1 hour)
   - Hardcode 1-2 example journeys in sidebar dropdown
   - "Load Example: Opioid Treatment" → auto-fills sample data
   - Users can edit and re-run

**Deliverable:** Streamlit app running locally (`streamlit run app.py`)

**Commit message:** `feat: dashboard UI with three analysis tabs`

---

### **DAY 3: Polish + Org-Level Insights (6 hours)**

**Goal:** Add one more layer that shows "organizational value," not just individual analysis.

**Steps:**

1. **Add "Cohort Summary" section** (2 hours)
   - Use 5-10 fake participant journeys (preload as JSON)
   - Run all through Gemini (batched, not real-time)
   - Show:
     - Average completion rate by ASAM dimension
     - Dropout risk distribution (pie chart)
     - Top 3 recommended topics based on gaps

2. **Add Gemini-powered content recommender** (2 hours)
   - Logic: "Based on this participant's ASAM gaps, suggest 3 modules"
   - Pull from Atlas's actual curriculum list (from brochure page 5)
   - Example: If "Relationships" is weak → suggest those 3 topics

3. **Polish UI/UX** (2 hours)
   - Add Atlas branding (purple/orange colors from brochure)
   - Add icons (using `streamlit_option_menu` or emoji)
   - Add explanatory text: "Why this matters for facilitators"

**Deliverable:** Full dashboard with individual + org views

**Commit message:** `feat: cohort insights + content recommendations`

---

### **DAY 4: Demo Data + Deployment (6 hours)**

**Goal:** Make it look polished. Have a live demo link.

**Steps:**

1. **Create compelling demo data** (2 hours)
   - Write 15-20 realistic journal entries
   - Source: Use language from Atlas brochure use cases
   - Include: opioid treatment, adolescent, trauma recovery
   - Make sure they trigger different ASAM dimensions

2. **Add "How It Works" explainer page** (1 hour)
   - First tab when you open the app
   - Show: "For Facilitators" + "For Admins" views
   - Explain the three outputs

3. **Deploy to Streamlit Cloud** (FREE) (1 hour)
   - Push code to GitHub (public repo)
   - Connect to Streamlit Cloud: https://streamlit.io/cloud
   - App is now live online (shareable URL)

4. **Create README.md** (1 hour)
   - Explain the problem
   - Show a screenshot of the dashboard
   - List the features
   - Add usage instructions

5. **Test end-to-end** (1 hour)
   - Run locally once more
   - Test deployed version
   - Make sure Gemini calls work (check free tier isn't maxed)

**Deliverable:** Live demo at `https://[your-username]-atlas-ai.streamlit.app`

**Commit message:** `deploy: streamlit cloud + demo data + docs`

---

## 🔧 Code Templates (Copy-Paste Into Cursor)

### **brain.py** (Core AI Logic)
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
   present in the entries. Include a direct quote.
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
    ...
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
        return {
            "summary": "Error parsing response",
            "asam": {},
            "risk_score": 0.5,
            "stage_of_change": "Unknown"
        }
```

### **app.py** (Streamlit Dashboard)
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
        for i, dimension in enumerate(ASAM_DIMENSIONS):
            with cols[i % 2]:
                if dimension in result.get('asam', {}):
                    info = result['asam'][dimension]
                    status = "✅ Present" if info['present'] else "⬜ Not detected"
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
        if result['asam'].get('Relapse/Recurrence Potential', {}).get('present'):
            st.markdown("- 🚨 Coping Skills")
            st.markdown("- 🔄 Relapse Prevention")
        if result['asam'].get('Recovery/Living Environment', {}).get('present'):
            st.markdown("- 👥 Relationships & Communication")
            st.markdown("- 🏡 Building Support Networks")

st.markdown("---")
st.caption("Atlas Clinical Insights Engine | Powered by Gemini AI")
```

---

## 📊 Demo Data (JSON format, save as `demo_data.json`)

```json
{
  "participants": [
    {
      "id": "P001",
      "program": "Opioid Treatment",
      "entries": [
        "Day 1: I'm struggling with cravings. My family wants to help but I feel ashamed.",
        "Day 5: Attended 3 NA meetings. Withdrawal symptoms improving with medication.",
        "Day 14: Two weeks clean. Sponsor called me today."
      ]
    },
    {
      "id": "P002",
      "program": "Adolescent Treatment",
      "entries": [
        "Don't know why I'm here. Not that bad.",
        "Talked with counselor. Maybe I do avoid feelings.",
        "Made a plan to talk to my dad."
      ]
    }
  ]
}
```

---

## 🚀 Deployment Checklist (Day 4)

- [ ] Push code to GitHub (create public repo)
- [ ] Create `.gitignore` with `.env` file
- [ ] Test locally: `streamlit run app.py`
- [ ] Deploy via Streamlit Cloud (connect GitHub repo)
- [ ] Test deployed version (wait 2 min for build)
- [ ] Get public URL (share with interview panel)
- [ ] Create README with screenshots

---

## 📝 Days 5-6: Interview Prep

### **Day 5 (4 hours): Deep Dive Prep**
1. **Know the product cold** (1 hour)
   - Reread the brochure
   - Memorize: ASAM 6 dimensions, use cases, sectors served
   
2. **Practice the pitch** (1 hour)
   - Problem: "Facilitators read 100s of pages, can't analyze for patterns"
   - Solution: "AI auto-summarizes and flags risk"
   - Impact: "Reduces burnout, improves outcomes, scales capacity"
   
3. **Prep for deep-dives** (2 hours)
   - Why did you choose Gemini 1.5 Flash? (free tier, context window)
   - Why ASAM dimensions? (they obsess over it)
   - How would this integrate? (facilitator workflow, not standalone)
   - What's the business model? (per-seat pricing, reduces churn via dropout prevention)

### **Day 6 (4 hours): Final Polish + Dry Run**
1. **Record a 3-min demo video** (using Loom, free)
   - Show: Load example → Analyze → Show summary + risk flag
   - Talk: "This solves X problem for Y users"
   
2. **Prepare talking points:**
   - "What I learned about Atlas" (person-centered, compliance-focused, understaffed)
   - "What gap I identified" (need for clinical insights at scale)
   - "Why AI matters here" (not hype, actual ROI: time savings + outcomes)
   
3. **Do a 20-min mock interview with friend/ChatGPT**
   - CPO asks: "How does this actually get built into Atlas?"
   - Your answer: "As a feature in the participant view, not a separate app"
   
4. **Get sleep** 😴

---

## ✅ Deliverables Checklist

**By end of Day 4, you have:**
- ✅ GitHub repo with code
- ✅ Live Streamlit Cloud demo (shareable URL)
- ✅ README.md explaining the project
- ✅ 3 example use cases built-in (opioid, adolescent, trauma)
- ✅ No cost (free tier: Cursor, Gemini, Streamlit Cloud)

**By end of Day 6, you have:**
- ✅ 3-min demo video
- ✅ Pitch script (2 min)
- ✅ Answers to 10 likely CPO questions
- ✅ Interview-ready confidence

---

## 🎤 The CPO Interview Pitch (Copy This)

*"I built Atlas Clinical Insights Engine to solve a problem I found in your brochure: 
'resource-limited organizations' trying to deliver individualized care at scale.*

*Right now, facilitators read hundreds of pages of journals manually. This AI system 
auto-generates a clinical summary, maps entries to your ASAM framework, and flags 
dropout risk before it happens.*

*The business case: 
- Facilitator saves 3+ hours per client per month (burnout prevention)
- Predictive dropout risk reduces AMA rates (keeps participants in programs)
- Org-level insights justify payer contracts (value-based care revenue)

*I built it with zero cost—Gemini free tier, Streamlit Cloud, local data—to prove 
the concept works before you invest engineering time. And it integrates directly 
into your existing workflow: participant uploads journal → AI drafts summary → 
facilitator reviews + edits.*

*This is why it's the right move: Atlas is already trusted by 5,000+ programs. 
Adding AI capability keeps you competitive against newer platforms while leveraging 
your real moat—evidence-based curricula and facilitator relationships."*

---

## ⚠️ Edge Cases / Troubleshooting

| Problem | Solution |
|---------|----------|
| Gemini API rate limit | Free tier = 15 req/min. Demo data = 5 entries max per run. Add caching in app. |
| JSON parse error from Gemini | Add fallback in `brain.py`. Return defaults if parse fails. |
| Streamlit Cloud deployment fails | Ensure `requirements.txt` has all packages. Add `GEMINI_API_KEY` as secret in Streamlit settings. |
| App is slow | Use `@st.cache_resource` to cache Gemini client. Cache results in session_state. |

---

**Good luck. You've got this.** 💪
