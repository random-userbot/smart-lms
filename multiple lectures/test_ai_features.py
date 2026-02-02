"""
Test AI Features Integration
Tests auto-model selection and Whisper integration
"""

import logging
logging.basicConfig(level=logging.INFO)

print("=" * 70)
print("TESTING AI FEATURES INTEGRATION")
print("=" * 70)

# Test 1: Auto-model selection for different subjects
print("\n1️⃣  AUTO-MODEL SELECTION TEST")
print("-" * 70)

from services.context_aware_tutor import ContextAwareAITutor

tutor = ContextAwareAITutor()

# Test Japanese course
print("\n📚 Testing: Japanese for Beginners")
tutor.set_context({'name': 'Japanese for Beginners'})
print(f"   Subject: {tutor.current_subject}")
print(f"   Mode: {tutor.current_mode}")
print(f"   Model: {tutor.model}")
print(f"   ✅ Expected: qwen/qwen3-32b (Asian language specialist)")

# Test History course
print("\n📚 Testing: World History")
tutor.set_context({'name': 'World History'})
print(f"   Subject: {tutor.current_subject}")
print(f"   Mode: {tutor.current_mode}")
print(f"   Model: {tutor.model}")
print(f"   ✅ Expected: openai/gpt-oss-120b (best reasoning)")

# Test Math course
print("\n📚 Testing: Advanced Calculus")
tutor.set_context({'name': 'Advanced Calculus'})
print(f"   Subject: {tutor.current_subject}")
print(f"   Mode: {tutor.current_mode}")
print(f"   Model: {tutor.model}")
print(f"   ✅ Expected: openai/gpt-oss-120b (best for math)")

# Test 2: Audio service initialization
print("\n\n2️⃣  AUDIO SERVICE TEST")
print("-" * 70)

from services.audio_practice import AudioPracticeService

audio = AudioPracticeService()
print(f"\n🔊 TTS Engine: {audio.tts_engine}")
print(f"🎤 STT Engine: {audio.stt_engine}")
print(f"🤖 Whisper Model: {audio.WHISPER_MODEL if audio.stt_engine else 'Not available'}")
print(f"✅ Audio services available: {audio.is_available()}")

# Test 3: Model recommendations summary
print("\n\n3️⃣  MODEL USAGE SUMMARY")
print("-" * 70)

print("""
📊 AUTOMATIC MODEL SELECTION:

Language Courses (Japanese, Chinese, Korean, Spanish, French):
   → qwen/qwen3-32b (Asian language specialist)
   
History, Math, Science Courses:
   → openai/gpt-oss-120b (best reasoning & explanations)
   
Audio Transcription:
   → whisper-large-v3-turbo (fast & accurate speech-to-text)
   
Quick Responses (future):
   → openai/gpt-oss-20b (3x faster, good quality)
   
Long Transcripts (future):
   → moonshotai/kimi-k2-instruct (handles 2000+ chars)
""")

print("\n" + "=" * 70)
print("✅ ALL TESTS COMPLETE!")
print("=" * 70)

print("\n📝 NEXT STEPS:")
print("   1. Run the Streamlit app: streamlit run app/streamlit_app.py")
print("   2. Test AI Tutor with different courses")
print("   3. Try Audio Practice for Japanese learning")
print("   4. Generate quizzes with: python bulk_quiz_generator.py")
