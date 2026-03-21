# Claude Code Quick-Start Guide

**Copy this into Claude Code to begin immediately**

---

## 🎯 IMMEDIATE CONTEXT

User: Jigar, Senior Java Backend Engineer transitioning to AI/LLM Engineer  
Project: Week 1 COMPLETE (Intelligent Task Router)  
Current Task: Starting Week 2 (Production Polish)  
Returning after: Few weeks break

---

## ✅ WEEK 1 STATUS (What Works)

Location: `~/ai-llm-engineer/project1-task-router/`

**Files that should exist:**
- `models.py` - Pydantic schemas
- `config.py` - Configuration with prompts, GEMINI_MODEL = "gemini-3-flash-preview"
- `router.py` - ClassicalRouter, LLMRouter, IntelligentRouter
- `main.py` - FastAPI application
- `requirements.txt` - Dependencies
- `.env` - Contains GOOGLE_API_KEY

**Key Feature:** Dual-mode routing (classical_first vs llm_first)

---

## 🚀 YOUR FIRST ACTIONS

### Step 1: Validate Week 1 (5 minutes)

```bash
cd ~/ai-llm-engineer/project1-task-router
source ../venv/bin/activate

# Quick validation
python -c "
from router import IntelligentRouter
router = IntelligentRouter()
result = router.route('Production DB is down!')
print(f'✅ Works: {result.category} via {result.method_used}')
"
```

**Expected output:**
```
✅ Works: URGENT via CLASSICAL
```

### Step 2: Check What's Been Started

```bash
# Check for Week 2 files
ls -la | grep -E "(logging_config|Dockerfile|docker-compose)"

# Check if router.py has logging
grep -n "logging_config" router.py
grep -n "request_id" router.py
```

**Report findings to user:**
- Do you have `logging_config.py`? YES/NO
- Does `router.py` import logging_config? YES/NO
- Status: Week 2 [NOT STARTED / PARTIALLY STARTED / NEARLY DONE]

### Step 3: Understand User's Goals

Ask user to choose:

**A) Complete Week 2 (Logging + Docker + Docs)**  
Time: 12-18 hours  
Result: Production-ready, portfolio-worthy Project 1

**B) Move to Project 2 (Code Reviewer with LangChain)**  
Time: 20-30 hours  
Result: More breadth, new technologies

**C) Custom plan based on job search timeline**  
Ask about: interview timeline, hours/week available

---

## 📋 WEEK 2 ROADMAP

### Phase 1: Logging (4-6 hours)
- Create `logging_config.py`
- Update `router.py` with decision tracking
- Add request IDs, input hashing
- Track p95/p99 latencies

### Phase 2: Docker (4-6 hours)
- Create `Dockerfile`
- Create `docker-compose.yml`
- Test containerized deployment

### Phase 3: Documentation (3-4 hours)
- Professional README.md
- Architecture diagram
- API documentation
- Setup instructions

### Phase 4: Performance (4-6 hours)
- Load testing
- Final polish
- Screenshot for portfolio

---

## 🎓 CRITICAL TECHNICAL DETAILS

### SDK Pattern (MUST USE THIS)
```python
# ✅ CORRECT
from google import genai
from google.genai import types

client = genai.Client(api_key=api_key)
response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=prompt,
    config=types.GenerateContentConfig(
        response_schema=PydanticModel,
    )
)
data = response.parsed  # Already validated!
```

### Hybrid Routing (THE KEY DIFFERENTIATOR)
```python
# Classical-first mode (default):
# 1. Try classical (fast, free)
# 2. If confident → use it
# 3. If uncertain → call LLM
# Result: 70% cost savings!
```

---

## 💬 COMMUNICATION STYLE

Jigar prefers:
- ✅ Natural language, no buzzwords
- ✅ Deep explanations (WHY not just WHAT)
- ✅ Production quality over speed
- ✅ Type safety and proper error handling
- ❌ No "spearheaded", "leveraged", "robust"
- ❌ No surface-level answers

---

## 🔍 VALIDATION COMMANDS

```bash
# Test router
python router.py

# Start API
python main.py

# Test endpoints
curl http://localhost:8000/health
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "Production is down!"}'

# Check logs (if Phase 1 done)
ls logs/
cat logs/task-router-decisions.log | python -m json.tool
```

---

## 📦 DELIVERABLES CHECKLIST

### Week 2 Complete When:
- [ ] Logging with JSON structured format
- [ ] Decision tracking with request IDs
- [ ] Docker container builds and runs
- [ ] Professional README with examples
- [ ] Performance metrics (p95/p99)
- [ ] All tests passing
- [ ] Portfolio screenshots taken

---

## 🎯 START HERE

1. **Validate Week 1 works** (run commands above)
2. **Check for Week 2 files** (logging_config.py, etc.)
3. **Report status to user**
4. **Ask which path: Complete Week 2 OR Move to Project 2**
5. **Begin implementation** based on user's choice

---

## 📚 REFERENCE DOCS

Full context: See `CLAUDE_CODE_HANDOFF.md` in this directory

Key sections:
- Week 1 implementation details
- Week 2 phase-by-phase plan
- Interview talking points
- Technical architecture

---

**Ready to guide Jigar through Week 2!** 🚀

Your advantages over Claude.ai:
- ✅ Can see actual code files
- ✅ Can validate what exists vs what's planned
- ✅ Can provide grounded, specific guidance
- ✅ Can test changes immediately

Start by validating Week 1, then ask user: "Continue Week 2 or start Project 2?"
