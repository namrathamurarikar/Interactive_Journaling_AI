# 📌 ULTIMATE QUICK REFERENCE
## Print this. Keep it. You'll need it.

---

## 🎯 THE FOUR THINGS YOU NEED

### 1. API Key ✅
- Get from: https://aistudio.google.com/apikey
- Save in: `.env` file
- Format: `GEMINI_API_KEY=AIza...`

### 2. Folder Structure
```
atlas-ai-demo/
├── venv/
├── .env               (API key)
├── brain.py           (AI logic)
├── app.py             (Dashboard)
├── requirements.txt
├── README.md
└── .gitignore
```

### 3. Files You Create
- `brain.py` - Copy from CURSOR_IMPLEMENTATION.md STEP 5
- `app.py` - Copy from CURSOR_IMPLEMENTATION.md STEP 6
- `.env` - Put API key here
- `requirements.txt` - Copy from CURSOR_IMPLEMENTATION.md STEP 8
- `.gitignore` - Copy from CURSOR_IMPLEMENTATION.md STEP 9
- `README.md` - Copy from CURSOR_IMPLEMENTATION.md STEP 10

### 4. Commands You Run
```bash
# Setup
mkdir atlas-ai-demo && cd atlas-ai-demo
python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate (Windows)
pip install streamlit google-generativeai python-dotenv plotly

# Test
python test_gemini.py          # Should see: Hello from Gemini!
python brain.py               # Should see JSON output

# Run app
streamlit run app.py          # Opens browser, shows dashboard

# Save code
git init
git add .
git commit -m "feat: initial atlas ai demo"
```

---

## 📋 WHERE TO FIND WHAT

### "I need step-by-step instructions"
→ Open **QUICK_CHECKLIST.md**

### "I need the full code for brain.py"
→ Open **CURSOR_IMPLEMENTATION.md** → STEP 5

### "I need the full code for app.py"
→ Open **CURSOR_IMPLEMENTATION.md** → STEP 6

### "I'm getting an error, help!"
→ Open **CURSOR_IMPLEMENTATION.md** → "Troubleshooting"

### "What do I do tomorrow (Day 2)?"
→ Open **ATLAS_4DAY_PLAN.md** → "DAY 2"

### "How do I prepare for the interview (Days 5-6)?"
→ Open **INTERVIEW_PREP_GUIDE.md**

### "What should I do each day?"
→ Open **MASTER_CHECKLIST.md**

---

## 🐛 QUICK FIXES (Most Common)

| Error | Fix |
|-------|-----|
| `ModuleNotFoundError: streamlit` | `pip install streamlit` |
| `GEMINI_API_KEY not found` | Check `.env` file format: `GEMINI_API_KEY=AIza...` (no quotes) |
| `(venv) not showing` | Not in virtual environment. Run: `source venv/bin/activate` |
| `403 Access Denied` | API key is wrong/expired. Get new one from https://aistudio.google.com/apikey |
| `Address already in use` | Kill old process: `pkill streamlit` |
| `JSON parsing error` | Rerun. Gemini sometimes returns bad JSON. There's a fallback in brain.py. |

---

## ✅ DAILY CHECKLIST

### DAY 1: Build Core
- [ ] API key created and saved in `.env`
- [ ] Virtual environment activated (shows `(venv)` in terminal)
- [ ] Dependencies installed (no errors)
- [ ] `test_gemini.py` works (shows "Hello from Gemini!")
- [ ] `brain.py` works (shows JSON output)
- [ ] `streamlit run app.py` opens browser
- [ ] App loads example, analyzes, shows 4 tabs
- [ ] `git init` + first commit done

### DAY 2: Deploy
- [ ] Code pushed to GitHub
- [ ] Streamlit Cloud account created
- [ ] App deployed to public URL
- [ ] Live demo works (other people can access it)

### DAY 3: Polish
- [ ] Cohort view added
- [ ] Content recommendations working
- [ ] UI polished with colors + icons
- [ ] All demo examples tested

### DAY 4: Finalize
- [ ] README.md complete
- [ ] Code cleaned up + commented
- [ ] Demo video recorded (3 min)
- [ ] GitHub repo is presentation-ready

### DAY 5: Interview Prep
- [ ] 2-minute pitch memorized (can say without notes)
- [ ] 10 questions + answers practiced (out loud)
- [ ] Dry run interview done (with friend or mock)

### DAY 6: Final Prep
- [ ] Demo video ready
- [ ] Interview materials printed
- [ ] Sleep 8 hours
- [ ] Confidence level: 8/10+

---

## 💻 TERMINAL COMMANDS YOU NEED

### Setup
```bash
mkdir atlas-ai-demo
cd atlas-ai-demo
python -m venv venv
source venv/bin/activate
pip install streamlit google-generativeai python-dotenv plotly
```

### Test
```bash
python test_gemini.py
python brain.py
```

### Run
```bash
streamlit run app.py
# Ctrl+C to stop
```

### Deploy
```bash
git init
git add .
git commit -m "message"
git push origin main
# Then deploy to Streamlit Cloud via web UI
```

---

## 🎤 THE 30-SECOND PITCH

**Problem:** Atlas facilitators read 100s of pages of journals manually.

**Solution:** AI auto-generates summaries, ASAM mapping, and risk flags.

**Impact:** Saves 3+ hours per client per month. Reduces burnout. Improves outcomes.

**Why:** Per-seat model = dropout = lost revenue. Predicting risk + preventing dropouts = direct ROI.

---

## 📊 SUCCESS METRICS

| Metric | Target | Status |
|--------|--------|--------|
| API key working | ✅ See "Hello from Gemini!" | |
| brain.py working | ✅ Returns JSON | |
| App runs locally | ✅ Streamlit opens browser | |
| Demo examples work | ✅ All 3 load + analyze | |
| Deployed live | ✅ Public URL works | |
| Interview ready | ✅ 2-min pitch memorized | |
| Sleep before interview | ✅ 8 hours | |

---

## 🚨 DO NOT DO THESE THINGS

❌ **Don't:**
- Commit `.env` to GitHub (it has your API key!)
- Spend days perfecting the UI (functional is enough)
- Skip testing each step (test before moving on)
- Overthink the code (it's designed to be simple)
- Go to interview tired (sleep is critical)
- Try to understand every line (just follow the plan)
- Modify code until the basic version works
- Use a paid Gemini tier (free tier is enough)

✅ **Do:**
- Test each step before moving on
- Commit code daily (shows progress)
- Use `.gitignore` to exclude `.env`
- Deploy to free tiers (Streamlit Cloud, Gemini free)
- Sleep well before interview
- Follow the checklist
- Copy-paste code exactly
- Ask for help if stuck

---

## 📞 WHEN YOU GET STUCK

**Step 1:** Read the error message in terminal (usually tells you what's wrong)

**Step 2:** Google the error + package name (e.g., "ModuleNotFoundError streamlit")

**Step 3:** If still stuck, check CURSOR_IMPLEMENTATION.md → Troubleshooting

**Step 4:** If STILL stuck, the error is likely:
- API key format wrong
- Virtual environment not activated
- Packages not installed

**Restart approach:**
```bash
# Deactivate virtual env
deactivate

# Reactivate it
source venv/bin/activate

# Reinstall packages
pip install -r requirements.txt

# Try again
python brain.py
```

---

## 🎯 YOUR NORTH STAR

**Remember:** You're building a proof-of-concept in 4 days to show CPOs you:
1. Understand their business problem
2. Can ship working code fast
3. Think like a PM, not just engineer
4. Can interview well

**You don't need perfect code. You need working code + smart thinking.**

---

## ⏱️ TIME BREAKDOWN

| Activity | Time | Total |
|----------|------|-------|
| Day 1: Core logic | 6-8 hrs | 6-8 hrs |
| Day 2: Dashboard | 6-8 hrs | 12-16 hrs |
| Day 3: Polish | 6 hrs | 18-22 hrs |
| Day 4: Deploy + docs | 6 hrs | 24-28 hrs |
| Day 5: Interview prep | 4 hrs | 28-32 hrs |
| Day 6: Final polish + rest | 4 hrs | 32-36 hrs |
| **Total** | | **32-36 hrs** |

**That's doable in 6 days if you focus.** 💪

---

## 🎁 BONUS: What CPOs Will Believe

✅ **They'll believe you:**
- Understand their product (you reference ASAM, per-seat model, facilitator pain)
- Can ship code (you have working demo)
- Think strategically (you connect tech to business metrics)
- Know your limitations (you're honest about trade-offs)

❌ **They won't believe:**
- "I built this overnight" (don't say this, it sounds unprepared)
- "This is production-ready" (say "This is a proof-of-concept")
- "I did zero research" (you clearly studied the brochure)

---

## 🏁 FINISH LINE

**By Day 4:** Live demo + GitHub repo + README

**By Day 6:** Interview confidence + sleep schedule

**Interview day:** Tell story → Show demo → Answer questions → Get offer

---

## 💪 FINAL REMINDER

You have:
✅ Clear roadmap
✅ Copy-paste code
✅ Detailed instructions
✅ Troubleshooting guide
✅ Interview prep

**You don't need to be a genius. You need to follow the plan.**

**Now open QUICK_CHECKLIST.md and start building.** 🚀

---

*Questions? The answer is in one of these docs. I promise.*

*Good luck.* 💪
