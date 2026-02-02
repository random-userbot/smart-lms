# Quick Start: New AI Features

## Installation (1 minute)

```powershell
# Install new dependencies
pip install youtube-transcript-api gTTS
```

## Usage

### 1. Better Quizzes (Uses Video Transcripts)
```powershell
# Generate quizzes - now uses video content!
python bulk_quiz_generator.py --questions 5
```
**Before:** Questions from video titles only  
**Now:** Questions from actual video content ✅

### 2. Audio Practice (NEW!)
1. Run app: `streamlit run app/main.py`
2. Go to **🎧 Audio Practice** page
3. Choose:
   - **Listening:** Listen and answer
   - **Speaking:** Record and get feedback
   - **Conversation:** Chat with audio

### 3. AI Tutor (NEW!)
1. Go to **🤖 AI Tutor** page
2. Select your course
3. AI auto-detects subject:
   - Japanese → Language mode
   - History → Subject tutor
   - Math → Problem solving
4. Features:
   - ❓ Ask questions (doubt solving)
   - 📝 Generate quiz from transcript
   - 📖 Explain concepts
   - 💬 Chat

## Examples

### Japanese Course
```
Select: "Japanese for Beginners"
Ask: "How do は and が work?"
Get: Japanese grammar explanation ✅
```

### History Course
```
Select: "World History"
Ask: "What caused WW1?"
Get: Historical analysis (no Japanese!) ✅
```

## That's it!
The AI now reads video content and adapts to your subject automatically. 🚀
