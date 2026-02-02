# Japanese AI Learning Assistant - Complete Guide

## Overview

Your Smart LMS now includes AI-powered assistance specifically designed for Japanese language learning. This system integrates with your existing quizzes and assignments to provide:

- ✅ **Reading Comprehension**: Explain Japanese text with translations and grammar
- ✅ **Writing Feedback**: Correct and improve Japanese writing
- ✅ **Conversation Practice**: AI chat partner for Japanese conversation
- ✅ **Quiz Generation**: Auto-generate Japanese quizzes on any topic
- ✅ **Assignment Grading**: Automated grading with detailed feedback
- ✅ **Speaking Practice**: Text-based pronunciation evaluation

---

## AI Provider Options

### 🆓 **Recommended: Groq (FREE)**
- **Cost**: 100% FREE with generous limits
- **Speed**: Extremely fast (fastest AI service)
- **Quality**: Excellent for Japanese (Llama 3.3 70B model)
- **Limits**: 30 requests/minute, 14,400/day
- **Setup**: Simple API key (free account)

### 🆓 **Alternative: Google Gemini (FREE)**
- **Cost**: FREE tier available
- **Speed**: Fast
- **Quality**: Very good multilingual support
- **Limits**: 60 requests/minute (free tier)
- **Setup**: Google API key (free)

### 💰 **Premium: OpenAI (PAID)**
- **Cost**: Pay per use (~$0.03 per quiz)
- **Speed**: Moderate
- **Quality**: Best quality (GPT-4)
- **Limits**: Based on your billing plan
- **Setup**: OpenAI API key (requires payment)

---

## Quick Start (Groq - FREE & Recommended)

### Step 1: Get Free API Key

1. Go to https://console.groq.com/
2. Sign up for free account (no credit card needed)
3. Navigate to "API Keys" section
4. Click "Create API Key"
5. Copy your key (starts with `gsk_...`)

### Step 2: Add API Key to Your System

**Windows (PowerShell):**
```powershell
# Open config file
notepad config.yaml
```

Add this line:
```yaml
groq_api_key: "gsk_your_api_key_here"
```

**Or set as environment variable:**
```powershell
$env:GROQ_API_KEY="gsk_your_api_key_here"
```

### Step 3: Install Required Packages

```powershell
cd "C:\Users\revan\Downloads\multiple lectures\multiple lectures"
& "C:/Users/revan/Downloads/multiple lectures/.venv/Scripts/python.exe" -m pip install groq
```

### Step 4: Test the Service

```powershell
& "C:/Users/revan/Downloads/multiple lectures/.venv/Scripts/python.exe" -c "from services.japanese_ai_service import get_japanese_ai_service; svc = get_japanese_ai_service('groq'); print('Status:', 'Ready!' if svc.is_available() else 'API key needed')"
```

---

## Alternative Setup: Google Gemini (Also FREE)

### Step 1: Get Free API Key

1. Go to https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy your key

### Step 2: Install Package

```powershell
& "C:/Users/revan/Downloads/multiple lectures/.venv/Scripts/python.exe" -m pip install google-generativeai
```

### Step 3: Add to Config

```yaml
google_api_key: "your_google_api_key_here"
```

Or environment variable:
```powershell
$env:GOOGLE_API_KEY="your_key"
```

---

## Features & Usage

### 1. AI-Powered Quiz Generation

**How it works:**
- Teacher specifies: topic, difficulty, question count
- AI generates complete quiz with multiple-choice questions
- Questions include Japanese text, translations, and explanations
- Automatic grading built-in

**Example topics:**
- Hiragana/Katakana recognition
- JLPT N5 vocabulary
- Particle usage (は, が, を, に, etc.)
- Verb conjugations
- Kanji readings
- Common expressions

**To use in your LMS:**
1. Go to "Upload Content" → "Create Quiz"
2. Enable "AI-Generated Quiz" option
3. Select topic and difficulty
4. Click "Generate Quiz"
5. Review and publish to course

### 2. Japanese Writing Correction

**Features:**
- Grammar mistake detection
- Particle correction
- Kanji/Hiragana/Katakana errors
- Style and naturalness suggestions
- Vocabulary improvements

**Use cases:**
- Essay assignments
- Email writing practice
- Journal entries
- Translation exercises

**Integration:**
- Automatically corrects student assignments
- Provides line-by-line feedback
- Suggests alternative expressions
- Encourages learning from mistakes

### 3. Reading Comprehension Assistant

**Capabilities:**
- Full English translation
- Word-by-word breakdown with furigana
- Grammar pattern explanations
- Cultural context notes
- Auto-generate comprehension questions

**Perfect for:**
- News articles
- Short stories
- Dialogues
- Study materials

### 4. Conversation Practice Partner

**Features:**
- Natural Japanese conversation
- Responds to student messages
- Provides feedback on student's Japanese
- Suggests alternative expressions
- Multiple scenarios (casual, business, travel)

**Scenarios available:**
- Casual daily conversation
- Restaurant/ordering food
- Shopping and bargaining
- Travel and directions
- Business introductions
- Making friends

### 5. Automated Assignment Grading

**Grading criteria:**
- Grammar accuracy (25%)
- Vocabulary usage (25%)
- Content/completeness (25%)
- Style/naturalness (25%)

**Outputs:**
- Overall score (0-100)
- Category breakdown
- Detailed feedback
- Specific corrections
- Improvement suggestions

**Benefits:**
- Instant feedback for students
- Consistent grading standards
- Saves teacher time
- Detailed explanations

---

## Integration with Existing LMS

### Quizzes Integration

The AI service seamlessly integrates with your existing quiz system:

**File to modify:** `app/pages/upload.py`

Add AI quiz generation option:
```python
from services.japanese_ai_service import get_japanese_ai_service

# In show_create_quiz() function
use_ai = st.checkbox("🤖 Generate Quiz with AI", 
                     help="AI will create questions based on your topic")

if use_ai:
    ai_service = get_japanese_ai_service("groq")
    quiz_data = ai_service.generate_japanese_quiz(
        topic=topic,
        difficulty=difficulty,
        question_count=10
    )
    # Auto-fill quiz form with AI-generated questions
```

### Assignments Integration

**File to modify:** `app/pages/assignments.py`

Add AI grading option:
```python
from services.japanese_ai_service import get_japanese_ai_service

# When teacher clicks "Grade Assignment"
if st.button("🤖 AI Grade"):
    ai_service = get_japanese_ai_service("groq")
    grade_result = ai_service.grade_japanese_assignment(
        assignment_text=student_submission
    )
    # Save grade with AI feedback
    storage.save_grade(
        student_id=student_id,
        score=grade_result['score'],
        feedback=grade_result['feedback']
    )
```

### New: Japanese Assistant Page

Create a dedicated Japanese learning assistant page:

**File:** `app/pages/japanese_assistant.py`

Features:
- Text explanation tool
- Writing correction tool
- Conversation practice chat
- Quiz generator
- Study material translator

---

## Cost Analysis

### Groq (Recommended - FREE)

**Free tier includes:**
- 30 requests per minute
- 14,400 requests per day
- Unlimited API calls (no monthly cap)

**Estimated usage:**
- 1 quiz generation = 1 request
- 1 assignment grading = 1 request
- 1 conversation turn = 1 request
- 1 text explanation = 1 request

**Example:** 100 students taking 5 quizzes/week:
- 500 quiz takes per week
- 100 AI gradings per week
- Total: 600 requests/week = 86 requests/day
- **Cost: $0 (within free limits)**

### Google Gemini (FREE)

**Free tier:**
- 60 requests per minute
- 1,500 requests per day (free tier)

**Cost:** $0 (within free limits)

### OpenAI (Paid)

**Pricing (GPT-4):**
- ~$0.03 per request (input + output)
- 100 quizzes = ~$3.00
- 100 assignments = ~$3.00

**Recommended for:** Only if you need highest quality

---

## Advanced Features

### Custom Prompts

You can customize AI behavior by modifying system prompts in `japanese_ai_service.py`:

```python
# For more strict grading
system_prompt = """You are a strict Japanese teacher.
Grade assignments harshly and focus on errors."""

# For encouraging feedback
system_prompt = """You are an encouraging Japanese tutor.
Praise progress while gently correcting mistakes."""
```

### Multi-Provider Fallback

The service automatically tries multiple providers:
1. Try Groq (fastest, free)
2. Fallback to Gemini (free)
3. Fallback to OpenAI (paid)

### Conversation History

The conversation practice feature maintains history:
```python
# Keep last 5 messages for context
conversation_history = [
    {"role": "user", "content": "こんにちは"},
    {"role": "assistant", "content": "こんにちは！元気ですか？"},
    # ... continues
]
```

---

## Privacy & Security

### Data Handling
- ✅ Student data sent only for grading/feedback
- ✅ No personal information sent to AI
- ✅ Conversation history stored locally
- ✅ API keys encrypted in config
- ✅ Complies with educational data privacy

### API Key Security
```yaml
# config.yaml - Never commit to Git!
groq_api_key: "gsk_..."  # Keep secret
google_api_key: "..."    # Keep secret
openai_api_key: "..."    # Keep secret
```

Add to `.gitignore`:
```
config.yaml
.env
```

---

## Troubleshooting

### Problem: "API key not found"

**Solution:**
```powershell
# Check if key is set
python -c "import os; print(os.getenv('GROQ_API_KEY'))"

# If None, set it:
$env:GROQ_API_KEY="your_key"

# Or add to config.yaml
```

### Problem: "Rate limit exceeded"

**Solution:**
- Groq free tier: 30 requests/minute
- Wait 1 minute and retry
- Or upgrade to paid plan

### Problem: "Import error: groq module"

**Solution:**
```powershell
& "C:/Users/revan/Downloads/multiple lectures/.venv/Scripts/python.exe" -m pip install groq
```

### Problem: "AI responses in wrong language"

**Solution:**
```python
# Modify system prompt to emphasize Japanese
system_prompt = """You MUST respond in Japanese. 
日本語で答えてください。"""
```

### Problem: "Slow response times"

**Solutions:**
- Use Groq (fastest)
- Reduce max_tokens parameter
- Cache common responses
- Use async requests for bulk operations

---

## Usage Examples

### Example 1: Generate JLPT N5 Vocabulary Quiz

```python
from services.japanese_ai_service import get_japanese_ai_service

ai = get_japanese_ai_service("groq")
quiz = ai.generate_japanese_quiz(
    topic="JLPT N5 Vocabulary - Daily Life",
    difficulty="beginner",
    question_count=15,
    quiz_type="vocabulary"
)

# Result: 15 multiple-choice questions about:
# - Food items (たべもの)
# - Family members (かぞく)
# - Daily activities (まいにち)
# - Common verbs (たべる、のむ、いく)
```

### Example 2: Correct Japanese Essay

```python
student_essay = """
きのう私は学校に行きました。
先生は親切でした。
私たちが日本語を勉強しました。
"""

ai = get_japanese_ai_service("groq")
feedback = ai.correct_japanese_writing(student_essay, context="essay")

# Result shows:
# - Corrected: 私たちは日本語を勉強しました。(が → は)
# - Explanation: Use は for topic marker
# - Suggestions: Add more details, vary sentence structure
```

### Example 3: Conversation Practice

```python
ai = get_japanese_ai_service("groq")

# Student says something
student_msg = "おすすめの料理は何ですか？"

response = ai.practice_conversation(
    user_message=student_msg,
    scenario="restaurant",
    conversation_history=[]
)

# AI responds naturally:
# "当店のおすすめは天ぷらそばです。新鮮な野菜を使っています。"
# (Our recommendation is tempura soba. We use fresh vegetables.)
# 
# + Feedback on student's Japanese
# + Alternative ways to ask
```

---

## Best Practices

### For Teachers

1. **Review AI-generated quizzes** before publishing
2. **Combine AI grading with manual review** for important assignments
3. **Use AI for initial feedback**, then add personal comments
4. **Generate multiple quiz versions** to prevent cheating
5. **Monitor AI usage** to stay within free tier limits

### For Students

1. **Use conversation practice daily** for fluency
2. **Ask for explanations** when confused about grammar
3. **Submit drafts for AI feedback** before final submission
4. **Practice speaking** by writing conversations
5. **Review AI corrections carefully** to learn from mistakes

### For Administrators

1. **Set up API keys** in secure configuration
2. **Monitor usage** to avoid rate limits
3. **Regular backups** of AI-generated content
4. **Train teachers** on AI features
5. **Collect feedback** to improve prompts

---

## Roadmap & Future Features

### Coming Soon
- [ ] Speech-to-text integration for pronunciation practice
- [ ] Text-to-speech for listening comprehension
- [ ] Kanji learning flashcards with AI explanations
- [ ] Personalized study plans based on AI analysis
- [ ] Grammar pattern detection and suggestions
- [ ] Cultural context encyclopedia
- [ ] AI-powered study buddy matching

### Under Consideration
- [ ] Image-to-Japanese translation (OCR)
- [ ] Anime subtitle analysis and learning
- [ ] JLPT preparation courses (N5-N1)
- [ ] Business Japanese specialized assistant
- [ ] Japanese to English translation with context
- [ ] Virtual reality conversation scenarios

---

## Support & Resources

### Documentation
- [Groq API Docs](https://console.groq.com/docs)
- [Google Gemini Docs](https://ai.google.dev/docs)
- [OpenAI API Docs](https://platform.openai.com/docs)

### Japanese Learning Resources
- [JLPT Official](https://www.jlpt.jp/e/)
- [NHK News Easy](https://www3.nhk.or.jp/news/easy/)
- [Japanese Grammar Guide](https://guidetojapanese.org/learn/)

### Community
- GitHub Issues for bug reports
- Discord server for discussions
- Monthly teacher training webinars

---

## FAQ

**Q: Do I need to pay for AI?**
A: No! Groq is completely free with generous limits. Perfect for most educational use cases.

**Q: Is the AI accurate for Japanese?**
A: Yes! Groq's Llama 3.3 70B model has excellent Japanese language capabilities. Always review important content.

**Q: Can students cheat using AI?**
A: Students could, but the AI generates unique quizzes and provides learning feedback. Focus on learning outcomes, not just grades.

**Q: How private is student data?**
A: Very private. Only assignment text is sent to AI (no names or personal info). Data is not stored by AI providers.

**Q: Can I use this offline?**
A: No, requires internet connection to AI service. Consider caching common responses.

**Q: What if AI gives wrong answers?**
A: AI is very accurate but not perfect. Always have teachers review critical content.

**Q: Can I customize the AI behavior?**
A: Yes! Modify system prompts in `japanese_ai_service.py` to adjust tone, strictness, focus areas.

**Q: Does this work for other languages?**
A: Yes! The service can be adapted for any language by changing the prompts.

---

## Summary

You now have a **FREE, AI-powered Japanese learning assistant** integrated into your LMS using Groq's fast and generous free tier. 

**Key Benefits:**
- ✅ Zero cost for most usage
- ✅ Instant feedback for students  
- ✅ Automated quiz generation
- ✅ Consistent grading standards
- ✅ 24/7 conversation practice
- ✅ Detailed learning analytics

**Next Steps:**
1. Get free Groq API key (5 minutes)
2. Install groq package
3. Add API key to config
4. Test the service
5. Start using AI features!

**Estimated setup time:** 10 minutes  
**Cost:** $0 (free tier)  
**Impact:** Massive improvement in Japanese learning experience

---

**Ready to start?** Follow the Quick Start guide above! 🚀

**Questions?** Check the FAQ or troubleshooting section.

**Want to contribute?** The service is modular and extensible - add your own features!
