"""
Test Context-Aware Quiz Generator
Shows automatic model selection based on course subject
"""

from bulk_quiz_generator import detect_optimal_model

print("=" * 70)
print("CONTEXT-AWARE QUIZ GENERATOR TEST")
print("=" * 70)

# Test different course types
test_cases = [
    {
        'title': 'Japanese for Beginners',
        'description': 'Learn hiragana, katakana, and basic grammar',
        'expected': 'qwen/qwen3-32b'
    },
    {
        'title': 'Chinese Mandarin Course',
        'description': 'Learn Chinese characters and pronunciation',
        'expected': 'qwen/qwen3-32b'
    },
    {
        'title': 'World History 101',
        'description': 'From ancient civilizations to modern era',
        'expected': 'openai/gpt-oss-120b'
    },
    {
        'title': 'Advanced Calculus',
        'description': 'Derivatives, integrals, and differential equations',
        'expected': 'openai/gpt-oss-120b'
    },
    {
        'title': 'Spanish Grammar',
        'description': 'Vocabulary and conjugation practice',
        'expected': 'qwen/qwen3-32b'
    },
    {
        'title': 'Physics 201',
        'description': 'Classical mechanics and thermodynamics',
        'expected': 'openai/gpt-oss-120b'
    }
]

print("\n🧪 TESTING MODEL AUTO-SELECTION:\n")

all_passed = True
for i, test in enumerate(test_cases, 1):
    lecture = {
        'title': test['title'],
        'description': test['description']
    }
    
    detected_model = detect_optimal_model(lecture)
    expected_model = test['expected']
    
    status = "✅" if detected_model == expected_model else "❌"
    emoji = "🌏" if detected_model == 'qwen/qwen3-32b' else "🧠"
    
    print(f"{status} {emoji} {test['title']}")
    print(f"     → Detected: {detected_model}")
    
    if detected_model != expected_model:
        print(f"     ⚠️  Expected: {expected_model}")
        all_passed = False
    print()

print("=" * 70)
if all_passed:
    print("✅ ALL TESTS PASSED!")
else:
    print("❌ SOME TESTS FAILED")
print("=" * 70)

print("\n📊 MODEL SELECTION LOGIC:")
print("""
Language Keywords Detected → qwen/qwen3-32b (🌏 Multilingual specialist)
  • japanese, chinese, korean, spanish, french, german
  • language, vocabulary, grammar, hiragana, katakana, kanji

Other Subjects → openai/gpt-oss-120b (🧠 Best reasoning)
  • history, math, science, calculus, physics, etc.
  • Default for general education content
""")

print("\n💡 USAGE:")
print("""
# Generate quizzes with auto-model selection:
python bulk_quiz_generator.py --questions 5 --difficulty beginner

# The generator will automatically:
1. Detect course subject from title/description
2. Choose optimal Groq model (qwen-3-32b or gpt-oss-120b)
3. Generate contextually-aware quizzes
4. Use video transcripts for better questions
""")
