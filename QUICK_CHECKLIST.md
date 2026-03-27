# 🎯 DO THIS RIGHT NOW - Visual Checklist
## Follow in order. Don't skip steps.

---

## ✅ CHECKLIST: Getting Started (5 minutes)

### Step 1: Open Terminal in Cursor
```
Press: Ctrl + ` (backtick)
You should see a terminal at the bottom of Cursor
```
✅ Check: Terminal is open

---

### Step 2: Create Folder & Virtual Environment
```bash
mkdir atlas-ai-demo
cd atlas-ai-demo
python -m venv venv

# Activate virtual environment
# Mac/Linux:
source venv/bin/activate

# Windows:
# venv\Scripts\activate
```

✅ Check: Terminal shows `(venv)` at the start

---

### Step 3: Install Packages
```bash
pip install streamlit google-generativeai python-dotenv plotly
```

✅ Check: No errors, shows "Successfully installed"

---

### Step 4: Create .env File
1. Click **File → New File**
2. Name it: `.env`
3. Copy-paste (replace YOUR_KEY_HERE with your actual key):
```
GEMINI_API_KEY=YOUR_KEY_HERE
```
4. Save: Ctrl+S

✅ Check: `.env` file appears in sidebar

---

### Step 5: Test Gemini (Quick Verification)
1. Click **File → New File**
2. Name it: `test_gemini.py`
3. Copy-paste this:
```python
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content("Say 'Hello from Gemini!' exactly.")
print(response.text)
```
4. Save: Ctrl+S
5. In terminal, run: `python test_gemini.py`

✅ Check: See "Hello from Gemini!" printed

If you don't see it, **STOP** and fix the API key.

---

## 🧠 CHECKLIST: Core Brain (10 minutes)

### Step 6: Create brain.py
1. Click **File → New File**
2. Name it: `brain.py`
3. Copy the ENTIRE code from CURSOR_IMPLEMENTATION.md → STEP 5
4. Save: Ctrl+S
5. In terminal, run: `python brain.py`

✅ Check: See JSON output with "summary", "asam", "risk_score", "stage_of_change"

---

## 💻 CHECKLIST: Dashboard (10 minutes)

### Step 7: Create app.py
1. Click **File → New File**
2. Name it: `app.py`
3. Copy the ENTIRE code from CURSOR_IMPLEMENTATION.md → STEP 6
4. Save: Ctrl+S
5. In terminal, run: `streamlit run app.py`

✅ Check: 
- Browser opens to http://localhost:8501
- You see "Atlas Clinical Insights Engine"
- Sidebar has "Load Example" dropdown
- Click dropdown, select "Example: Opioid Treatment"
- Click "🔍 Analyze Entries"
- Wait 30-60 seconds
- See results in 4 tabs (Summary, ASAM, Risk, Insights)

If it doesn't work:
- Press Ctrl+C in terminal to stop
- Check for errors in terminal
- Fix and run again

---

## 📦 CHECKLIST: Setup Files (5 minutes)

### Step 8: Create requirements.txt
1. Click **File → New File**
2. Name it: `requirements.txt`
3. Copy-paste:
```
streamlit==1.28.0
google-generativeai==0.3.0
python-dotenv==1.0.0
plotly==5.17.0
```
4. Save: Ctrl+S

✅ Check: `requirements.txt` appears in sidebar

---

### Step 9: Create .gitignore
1. Click **File → New File**
2. Name it: `.gitignore`
3. Copy-paste:
```
.env
__pycache__/
*.pyc
venv/
.DS_Store
*.egg-info/
dist/
build/
```
4. Save: Ctrl+S

✅ Check: `.gitignore` appears in sidebar

---

### Step 10: Create README.md
1. Click **File → New File**
2. Name it: `README.md`
3. Copy the README content from CURSOR_IMPLEMENTATION.md → STEP 10
4. Save: Ctrl+S

✅ Check: `README.md` appears in sidebar

---

## 🎉 CHECKLIST: Final Setup (5 minutes)

### Step 11: Initialize Git
In terminal:
```bash
git init
git add .
git commit -m "feat: initial atlas ai demo"
```

✅ Check: No errors

---

## 📁 Your Folder Should Show This in Sidebar

```
atlas-ai-demo
├── venv/
├── .env                    ← API key
├── .gitignore
├── brain.py                ← AI logic
├── app.py                  ← Dashboard
├── test_gemini.py          ← Test (can delete)
├── requirements.txt
├── README.md
└── .git/
```

---

## 🚀 HOW TO USE THE APP

**Starting the app:**
```bash
streamlit run app.py
```

**Using the app:**
1. Sidebar: Click "Load Example: Opioid Treatment"
2. Click "🔍 Analyze Entries"
3. Wait 30-60 seconds
4. Explore 4 tabs:
   - Tab 1: Clinical Summary (professional case note)
   - Tab 2: ASAM Dimensions (which criteria are present)
   - Tab 3: Risk Assessment (dropout risk gauge)
   - Tab 4: Insights (recommendations)

**Stopping the app:**
- Press Ctrl+C in terminal

---

## ✅ SUCCESS CHECKLIST

By end of today, you should have:

- [ ] Gemini API key saved in `.env`
- [ ] `python test_gemini.py` → Shows "Hello from Gemini!"
- [ ] `python brain.py` → Shows JSON output
- [ ] `streamlit run app.py` → Opens browser, shows dashboard
- [ ] App loads example, analyzes, shows all 4 tabs
- [ ] All files created (brain.py, app.py, requirements.txt, README.md, .gitignore)
- [ ] Git initialized with first commit

**If all checkmarks are ✅: You're done with Day 1!**

---

## 🐛 QUICK FIXES

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: streamlit` | Run: `pip install streamlit` |
| `(venv) not in terminal` | Run: `source venv/bin/activate` (Mac/Linux) or `venv\Scripts\activate` (Windows) |
| `GEMINI_API_KEY not found` | Check `.env` has correct format: `GEMINI_API_KEY=AIza...` |
| `403 Access Denied` | API key is wrong. Get new one from https://aistudio.google.com/apikey |
| App shows blank page | Refresh browser. Wait 10 seconds. Check terminal for errors. |
| `Address already in use` | Run: `pkill streamlit` then try again |

---

## 📖 REFERENCE

- **CURSOR_IMPLEMENTATION.md** - Full step-by-step with all code
- **ATLAS_4DAY_PLAN.md** - Days 2-4 roadmap
- **INTERVIEW_PREP_GUIDE.md** - Interview prep (Days 5-6)

---

## 🎯 NEXT STEPS

**When you finish this checklist (usually 30-45 min):**

1. ✅ Verify app works
2. ✅ Celebrate 🎉
3. ✅ Read ATLAS_4DAY_PLAN.md Day 2 section
4. ✅ Tomorrow: Deploy to Streamlit Cloud

**You're on track for Days 1-4 build → Days 5-6 prep.**

---

## 💪 YOU'VE GOT THIS

This is completely doable. Just follow the checklist step-by-step.

**Stuck?** The error message will tell you what's wrong. Google it + the package name.

**Time estimate:** 30-45 minutes from start to working app.

**Now go open Cursor and start with Step 1.** 🚀
