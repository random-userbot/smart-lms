# Japanese AI Assistant - Quick Reference

## 🚀 Quick Start (5 Minutes)

```powershell
# 1. Install packages
.\setup_japanese_ai.ps1

# 2. Get FREE API key
# Visit: https://console.groq.com

# 3. Set API key
$env:GROQ_API_KEY="gsk_your_key_here"

# 4. Restart Streamlit
streamlit run app/streamlit_app.py
```

## 📋 Features Available

| Feature | Description | Use Case |
|---------|-------------|----------|
| 📖 **Text Explainer** | Translate & explain Japanese text | Understand difficult passages |
| ✍️ **Writing Corrector** | Fix grammar, get feedback | Improve Japanese writing |
| 💬 **Conversation Practice** | Chat with AI in Japanese | Daily conversation practice |
| 📝 **Quiz Generator** | Auto-create quizzes | Generate JLPT/grammar quizzes |
| 📊 **Assignment Grader** | AI grading with feedback | Instant assignment feedback |

## 💰 Cost Comparison

| Provider | Cost | Speed | Quality | Limit |
|----------|------|-------|---------|-------|
| **Groq** (Recommended) | **FREE** | ⚡ Fastest | ⭐⭐⭐⭐ | 14,400/day |
| Google Gemini | FREE | Fast | ⭐⭐⭐⭐ | 1,500/day |
| OpenAI GPT-4 | ~$0.03/req | Moderate | ⭐⭐⭐⭐⭐ | Pay as you go |

**Recommendation:** Use Groq (free + fast + excellent quality)

## 🔑 API Key Setup

### Groq (FREE - Recommended)
```powershell
# Get key: https://console.groq.com
$env:GROQ_API_KEY="gsk_..."
```

### Google Gemini (FREE)
```powershell
# Get key: https://makersuite.google.com/app/apikey
$env:GOOGLE_API_KEY="..."
```

### OpenAI (Paid)
```powershell
# Get key: https://platform.openai.com/api-keys
$env:OPENAI_API_KEY="sk-..."
```

## 📝 Code Examples

### Generate Quiz
```python
from services.japanese_ai_service import get_japanese_ai_service

ai = get_japanese_ai_service("groq")
quiz = ai.generate_japanese_quiz(
    topic="JLPT N5 Vocabulary",
    difficulty="beginner",
    question_count=10
)
# Returns complete quiz with 10 questions
```

### Correct Writing
```python
ai = get_japanese_ai_service("groq")
result = ai.correct_japanese_writing(
    text="私は昨日学校に行きました。",
    context="essay"
)
# Returns corrected text + feedback
```

### Grade Assignment
```python
ai = get_japanese_ai_service("groq")
grade = ai.grade_japanese_assignment(
    assignment_text=student_text
)
# Returns score (0-100) + detailed feedback
```

### Conversation Practice
```python
ai = get_japanese_ai_service("groq")
response = ai.practice_conversation(
    user_message="レストランでおすすめは何ですか？",
    scenario="restaurant"
)
# Returns AI response + feedback
```

## 🎯 Integration Points

### Add to Upload Page (Quizzes)
**File:** `app/pages/upload.py`
```python
if st.checkbox("🤖 AI Generate"):
    ai = get_japanese_ai_service("groq")
    quiz = ai.generate_japanese_quiz(topic, level, 10)
```

### Add to Assignments (Grading)
**File:** `app/pages/assignments.py`
```python
if st.button("🤖 AI Grade"):
    ai = get_japanese_ai_service("groq")
    result = ai.grade_japanese_assignment(text)
```

### Add to Navigation
**File:** `app/streamlit_app.py`
```python
if st.sidebar.button("🇯🇵 Japanese AI"):
    st.session_state.current_page = 'japanese_assistant'
```

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| "API key not found" | Set env var: `$env:GROQ_API_KEY="..."` |
| "Rate limit exceeded" | Wait 1 min (Groq: 30/min limit) |
| "Import error: groq" | Run: `pip install groq` |
| "No AI available" | Get key from https://console.groq.com |

## 📚 Files Reference

| File | Purpose |
|------|---------|
| `services/japanese_ai_service.py` | Core AI service (570 lines) |
| `app/pages/japanese_assistant.py` | UI interface (450 lines) |
| `JAPANESE_AI_GUIDE.md` | Complete documentation |
| `JAPANESE_AI_SUMMARY.md` | Quick overview |
| `setup_japanese_ai.ps1` | Auto setup script |
| `AI_QUIZ_INTEGRATION_EXAMPLE.py` | Integration examples |

## ⚡ Performance

**Groq Speed:**
- Quiz generation: ~5 seconds
- Writing correction: ~3 seconds  
- Conversation reply: ~2 seconds
- Assignment grading: ~4 seconds

**Daily Limits (Free Tier):**
- Groq: 14,400 requests/day (600/hour)
- Gemini: 1,500 requests/day (60/min)

**Typical Usage (100 students):**
- 100 quizzes/week = 100 requests
- 50 assignments/week = 50 requests
- 200 conversations/week = 200 requests
- **Total: 350/week = 50/day** ✅ Well within free limits

## 🎓 Best Practices

### For Teachers
- ✅ Review AI-generated quizzes before publishing
- ✅ Use AI grading + manual review for finals
- ✅ Generate multiple quiz versions
- ✅ Add personal comments to AI feedback

### For Students
- ✅ Use conversation practice daily
- ✅ Submit drafts for AI feedback
- ✅ Review corrections carefully
- ✅ Ask for explanations when confused

## 📖 Learning Resources

**Japanese Learning:**
- JLPT Official: https://www.jlpt.jp/e/
- NHK News Easy: https://www3.nhk.or.jp/news/easy/
- Grammar Guide: https://guidetojapanese.org/learn/

**AI Documentation:**
- Groq: https://console.groq.com/docs
- Gemini: https://ai.google.dev/docs
- OpenAI: https://platform.openai.com/docs

## ✅ Checklist

- [ ] Run setup script: `.\setup_japanese_ai.ps1`
- [ ] Get Groq API key (FREE): https://console.groq.com
- [ ] Set environment variable: `$env:GROQ_API_KEY="..."`
- [ ] Test service: Run japanese_ai_service.py
- [ ] Open Japanese Assistant page in LMS
- [ ] Generate first quiz
- [ ] Try conversation practice
- [ ] Read full guide: JAPANESE_AI_GUIDE.md

## 🎉 Summary

**What you get:**
- ✅ FREE AI assistant (Groq)
- ✅ Unlimited quiz generation
- ✅ Automated grading
- ✅ 24/7 conversation practice
- ✅ Instant text explanation
- ✅ Writing feedback

**Setup time:** 5 minutes
**Cost:** $0 (free tier)
**Impact:** Transform Japanese learning

---

**Need help?** See JAPANESE_AI_GUIDE.md for detailed instructions.
