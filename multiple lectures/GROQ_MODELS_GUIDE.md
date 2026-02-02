# Groq Models Guide

## Available Groq Models (as of Jan 2026)

### 🧠 REASONING / TEXT TO TEXT
**Best for:** General questions, tutoring, explanations, chat

- **GPT OSS 120B** ✅ Currently using
  - Most powerful reasoning model
  - Best for complex explanations
  - Used for: AI Tutor, Japanese Assistant, Doubt Solving
  
- **GPT OSS 20B**
  - Faster, lighter alternative
  - Good balance of speed and quality
  
- **Llama 3.3 70B**
  - Strong multilingual support
  - Good for Japanese and other languages
  
- **Llama 4 Scout**
  - Latest model with vision capabilities
  - Can analyze images
  
- **Qwen 3 32B**
  - Excellent for Asian languages
  - Great for Japanese/Chinese/Korean
  
- **Kimi K2**
  - Long context window
  - Good for processing long transcripts

### 🎤 SPEECH TO TEXT
**Best for:** Converting audio recordings to text

- **Whisper Large v3** ✅ Recommended
  - Most accurate transcription
  - Supports 99+ languages including Japanese
  - Best for high-quality transcription
  
- **Whisper Large v3 Turbo**
  - Faster version
  - Good balance of speed and accuracy
  - Best for real-time transcription

### 🔊 TEXT TO SPEECH
**Best for:** Converting text to audio (listening practice)

- **Orpheus English**
  - Natural English pronunciation
  - Best for English audio practice
  
- **Orpheus Arabic Saudi**
  - Arabic pronunciation
  - For Arabic language courses

### 👁️ VISION MODELS
**Best for:** Analyzing images, diagrams, screenshots

- **Llama 4 Scout**
  - Can analyze lecture screenshots
  - OCR for handwritten notes
  
- **Llama 4 Maverick**
  - Advanced vision capabilities

### 🌐 MULTILINGUAL MODELS
**Best for:** Language learning (Japanese, Spanish, etc.)

- **GPT OSS 120B** ✅ Currently using
- **Llama 3.3 70B**
- **Qwen 3 32B** (Best for Asian languages)
- **Whisper Large v3** (For audio)

### 🛠️ FUNCTION CALLING / TOOL USE
**Best for:** Complex workflows, integrations

- **GPT OSS 120B** ✅ Currently using
- **Llama 4 Scout**
- **Qwen 3 32B**

### 🛡️ SAFETY / CONTENT MODERATION
**Best for:** Filtering inappropriate content

- **Safety GPT OSS 20B**
- **Llama Guard**

## Current Implementation

### Text Generation (AI Tutor, Japanese Assistant)
```python
model="openai/gpt-oss-120b"  # ✅ Optimal choice
```

### Audio Transcription (Speech Recognition)
```python
# TODO: Implement Groq Whisper
model="whisper-large-v3-turbo"  # Faster
# OR
model="whisper-large-v3"  # More accurate
```

### Text-to-Speech (Audio Practice)
```python
# Currently using gTTS (Google TTS)
# Groq Orpheus not yet integrated
```

## Recommendations by Feature

### 1. Japanese Learning
- **Text explanations:** `openai/gpt-oss-120b` ✅ or `qwen-3-32b`
- **Pronunciation:** `whisper-large-v3` (transcription)
- **Audio generation:** `gTTS` (current) or explore Orpheus

### 2. Transcript-Based Quizzes
- **Text generation:** `openai/gpt-oss-120b` ✅
- **Long transcripts:** `moonshotai/kimi-k2-instruct` (long context)

### 3. Doubt Solving
- **Reasoning:** `openai/gpt-oss-120b` ✅
- **Quick answers:** `openai/gpt-oss-20b` (faster)

### 4. Audio Practice
- **Speech-to-Text:** `whisper-large-v3-turbo` 
- **Text-to-Speech:** `gTTS` (current)

### 5. Image Analysis (Future)
- **Diagrams/Screenshots:** `llama-4-scout`
- **OCR/Handwriting:** `llama-4-maverick`

## Speed vs Quality

### Fastest (Real-time)
- `openai/gpt-oss-20b` (text)
- `whisper-large-v3-turbo` (audio)

### Best Quality (Accuracy)
- `openai/gpt-oss-120b` (text) ✅ Current
- `whisper-large-v3` (audio)

### Best for Japanese
- `qwen-3-32b` (text - Asian languages specialist)
- `whisper-large-v3` (audio - multilingual)

## Cost (All FREE with Groq!)
- All models are FREE with generous rate limits
- No credit card required
- Perfect for educational use

## Next Steps

1. ✅ Currently using `openai/gpt-oss-120b` for text
2. ⏳ Integrate `whisper-large-v3-turbo` for speech recognition
3. ⏳ Consider `qwen-3-32b` for Japanese-specific tasks
4. ⏳ Add `llama-4-scout` for image analysis (future)
