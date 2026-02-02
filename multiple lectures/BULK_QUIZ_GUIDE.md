# Bulk Quiz Generation - Quick Guide

## What It Does

Automatically reads ALL your lectures and generates AI-powered quizzes for each one based on the lecture content!

## Features

✅ **Reads lecture content**: Title, description, materials
✅ **Generates contextual quizzes**: Questions based on actual lecture topics
✅ **Bulk processing**: Generate quizzes for all lectures at once
✅ **Smart skipping**: Skip lectures that already have quizzes
✅ **Progress tracking**: See real-time progress as quizzes generate
✅ **Customizable**: Choose difficulty, question count, and more

## How to Use

### Option 1: UI (Easiest)

1. **Set up AI** (if not done yet):
   ```powershell
   $env:GROQ_API_KEY="your_groq_key_here"
   ```

2. **Open Japanese Assistant**:
   - Log in as Teacher/Admin
   - Navigate to "🇯🇵 Japanese AI Assistant"

3. **Go to Quiz Generator**:
   - Select "📝 Quiz Generator" from tool dropdown
   - Click on "🚀 Bulk Generate" tab

4. **Configure settings**:
   - **Course**: Select specific course or "All Courses"
   - **Difficulty**: beginner/intermediate/advanced
   - **Questions per Quiz**: 3-15 (default: 5)
   - **Skip existing**: Check to skip lectures with quizzes

5. **Click "🎯 Generate Quizzes for All Lectures"**

6. **Wait for completion**:
   - Progress bar shows real-time status
   - See results summary when done

### Option 2: Command Line (Advanced)

```powershell
# Set API key
$env:GROQ_API_KEY="your_key"

# Generate for all lectures (beginner, 5 questions each)
python bulk_quiz_generator.py

# Generate for specific course
python bulk_quiz_generator.py --course "course_abc123"

# Advanced options
python bulk_quiz_generator.py --difficulty intermediate --questions 10

# Regenerate even if quizzes exist
python bulk_quiz_generator.py --regenerate

# Use different AI provider
python bulk_quiz_generator.py --provider gemini
```

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--course` | Specific course ID (optional) | All courses |
| `--difficulty` | beginner/intermediate/advanced | beginner |
| `--questions` | Questions per quiz (3-30) | 5 |
| `--regenerate` | Regenerate existing quizzes | False (skip) |
| `--provider` | groq/openai/gemini | groq |

## Example Scenarios

### Generate for 100 YouTube Lectures

```powershell
# You have 100 YouTube lectures imported
# Generate 5-question beginner quizzes for all

python bulk_quiz_generator.py --questions 5 --difficulty beginner
```

**Result**: 100 quizzes generated in ~10 minutes (with Groq)
**Cost**: $0 (free tier)

### Generate Advanced Quizzes

```powershell
# For advanced Japanese course
python bulk_quiz_generator.py --course "jap_advanced_123" --difficulty advanced --questions 10
```

### Regenerate All Quizzes

```powershell
# Replace all existing quizzes with new ones
python bulk_quiz_generator.py --regenerate --questions 8
```

## How It Works

1. **Reads lecture data**:
   - Title: "Introduction to Hiragana"
   - Description: "Learn the basics of Hiragana..."
   - Materials: Lecture notes, worksheets

2. **Creates context**:
   ```
   Topic: Introduction to Hiragana
   Context: Learn the basics of Hiragana writing system,
            including あ, い, う, え, お characters...
   ```

3. **AI generates quiz**:
   - Q1: What is Hiragana used for?
   - Q2: Which character represents "a"?
   - Q3: How many basic Hiragana characters are there?
   - etc.

4. **Saves to lecture**:
   - Quiz automatically attached to lecture
   - Students can take it immediately
   - Appears in "My Lectures" page

## Performance & Cost

### With Groq (FREE)

**Speed**: ~5 seconds per quiz
- 10 lectures = ~1 minute
- 50 lectures = ~5 minutes
- 100 lectures = ~10 minutes

**Cost**: $0 (within 14,400/day limit)

**Daily capacity**: Up to 2,880 quizzes per day (with 30/min limit)

### With OpenAI (PAID)

**Speed**: ~8 seconds per quiz
- 100 lectures = ~15 minutes

**Cost**: ~$3.00 per 100 quizzes

## Tips & Best Practices

### For Best Results

1. **Use descriptive lecture titles**:
   - ✅ "JLPT N5 Vocabulary - Food and Dining"
   - ❌ "Lecture 1"

2. **Add lecture descriptions**:
   - More context = better quiz questions
   - Include key topics, grammar points, vocabulary

3. **Start small**:
   - Test with 1 course first
   - Review quiz quality
   - Adjust difficulty/question count as needed

4. **Skip existing by default**:
   - Prevents duplicate quizzes
   - Saves API calls
   - Faster processing

5. **Monitor API limits**:
   - Groq: 30 requests/minute
   - If you hit limit, wait 1 minute and continue

### Quality Control

After bulk generation:
1. **Review sample quizzes**: Check 5-10 random quizzes for quality
2. **Edit if needed**: You can manually edit quiz questions
3. **Student testing**: Have 1-2 students test quizzes
4. **Adjust settings**: Regenerate with different difficulty if needed

## Troubleshooting

### "API rate limit exceeded"

**Problem**: Groq free tier is 30 requests/minute

**Solution**:
```python
# In bulk_quiz_generator.py, add delay:
import time
time.sleep(2)  # 2 seconds between requests
```

Or use UI which has built-in rate limiting.

### "Quiz generation failed"

**Possible causes**:
1. API key not set correctly
2. No lecture description/context
3. Network timeout

**Solution**:
- Check API key: `echo $env:GROQ_API_KEY`
- Add more lecture descriptions
- Re-run for failed lectures only

### "Low quality quizzes"

**Solution**:
1. Increase difficulty level
2. Add more detailed lecture descriptions
3. Try different AI provider (OpenAI for premium quality)

## Results Example

After running on 50 lectures:

```
📊 BULK QUIZ GENERATION SUMMARY
================================================
Total lectures: 50
✅ Quizzes generated: 48
⏭️  Skipped: 0
❌ Failed: 2
================================================

Results saved to: quiz_generation_results_20260130_143022.json
```

**Output file includes**:
- Detailed results for each lecture
- Success/failure reasons
- Quiz titles and question counts
- Timestamp and settings used

## Integration with LMS

Generated quizzes automatically:
- ✅ Appear in lecture pages
- ✅ Available in "Take Quiz" section
- ✅ Track student scores
- ✅ Show in analytics
- ✅ Award gamification points

No manual steps needed - it's fully integrated!

## Advanced: Scheduled Generation

To auto-generate quizzes for new lectures:

```powershell
# Create scheduled task (Windows)
# Run daily at 2 AM to generate quizzes for any new lectures

$action = New-ScheduledTaskAction -Execute "python" -Argument "bulk_quiz_generator.py"
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "AutoGenerateQuizzes"
```

## Summary

✅ **One-click quiz generation** for ALL lectures
✅ **Contextual questions** based on actual content  
✅ **FREE with Groq** (up to 2,880 quizzes/day)
✅ **Fast processing** (~5 seconds per quiz)
✅ **Smart skipping** (avoid duplicates)
✅ **Quality output** (review and adjust as needed)

**Time saved**: Generate 100 quizzes in 10 minutes vs. 20+ hours manually!

---

**Ready to generate?**

1. Set API key: `$env:GROQ_API_KEY="your_key"`
2. Run: `python bulk_quiz_generator.py`
3. Or use UI: Japanese Assistant → Quiz Generator → Bulk Generate

🎉 **Transform your LMS with AI-powered quizzes!**
