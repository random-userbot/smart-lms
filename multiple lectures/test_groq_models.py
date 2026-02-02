"""
Test Different Groq Models
Compare performance and capabilities
"""

from groq import Groq
from services.config_loader import get_api_key
import time

def test_text_models():
    """Test different text generation models"""
    api_key = get_api_key("groq")
    if not api_key:
        print("❌ No Groq API key found")
        return
    
    client = Groq(api_key=api_key)
    
    # Models to test
    models = [
        ("openai/gpt-oss-120b", "GPT OSS 120B (Current)"),
        ("openai/gpt-oss-20b", "GPT OSS 20B (Faster)"),
        ("qwen/qwen3-32b", "Qwen 3 32B (Asian languages)"),
        ("moonshotai/kimi-k2-instruct", "Kimi K2 (Long context)"),
    ]
    
    test_prompt = "Explain what is photosynthesis in 2 sentences."
    
    print("=" * 80)
    print("TEXT GENERATION MODEL COMPARISON")
    print("=" * 80)
    print(f"\nPrompt: {test_prompt}\n")
    
    for model_id, model_name in models:
        print(f"\n{'='*80}")
        print(f"🤖 {model_name}")
        print(f"   Model: {model_id}")
        print("-" * 80)
        
        try:
            start = time.time()
            
            completion = client.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": test_prompt}],
                temperature=0.7,
                max_completion_tokens=200
            )
            
            elapsed = time.time() - start
            response = completion.choices[0].message.content
            
            print(f"⏱️  Time: {elapsed:.2f}s")
            print(f"📝 Response:\n{response}")
            print(f"✅ Success")
            
        except Exception as e:
            print(f"❌ Error: {str(e)[:100]}")
    
    print("\n" + "=" * 80)


def test_japanese_models():
    """Test models for Japanese language"""
    api_key = get_api_key("groq")
    if not api_key:
        print("❌ No Groq API key found")
        return
    
    client = Groq(api_key=api_key)
    
    models = [
        ("openai/gpt-oss-120b", "GPT OSS 120B"),
        ("qwen/qwen3-32b", "Qwen 3 32B (Asian specialist)"),
    ]
    
    test_prompt = "Explain the difference between は (wa) and が (ga) particles in Japanese in simple terms."
    
    print("\n" + "=" * 80)
    print("JAPANESE LANGUAGE TEST")
    print("=" * 80)
    print(f"\nPrompt: {test_prompt}\n")
    
    for model_id, model_name in models:
        print(f"\n{'='*80}")
        print(f"🇯🇵 {model_name}")
        print("-" * 80)
        
        try:
            start = time.time()
            
            completion = client.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": test_prompt}],
                temperature=0.7,
                max_completion_tokens=300
            )
            
            elapsed = time.time() - start
            response = completion.choices[0].message.content
            
            print(f"⏱️  Time: {elapsed:.2f}s")
            print(f"📝 Response:\n{response}")
            print(f"✅ Success")
            
        except Exception as e:
            print(f"❌ Error: {str(e)[:100]}")
    
    print("\n" + "=" * 80)


def test_reasoning_models():
    """Test reasoning models for complex problems"""
    api_key = get_api_key("groq")
    if not api_key:
        print("❌ No Groq API key found")
        return
    
    client = Groq(api_key=api_key)
    
    test_prompt = "If a train travels 120 km in 2 hours, and then 90 km in 1.5 hours, what is its average speed for the entire journey?"
    
    print("\n" + "=" * 80)
    print("REASONING TEST (Math Problem)")
    print("=" * 80)
    print(f"\nPrompt: {test_prompt}\n")
    
    try:
        print("🧠 GPT OSS 120B (Reasoning model)")
        print("-" * 80)
        
        start = time.time()
        
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": test_prompt}],
            temperature=0.3,  # Lower for precise math
            max_completion_tokens=400
        )
        
        elapsed = time.time() - start
        response = completion.choices[0].message.content
        
        print(f"⏱️  Time: {elapsed:.2f}s")
        print(f"📝 Solution:\n{response}")
        print(f"✅ Success")
        
    except Exception as e:
        print(f"❌ Error: {str(e)[:100]}")
    
    print("\n" + "=" * 80)


def main():
    print("\n" + "🚀 " * 20)
    print("GROQ MODELS TESTING SUITE")
    print("🚀 " * 20 + "\n")
    
    test_text_models()
    test_japanese_models()
    test_reasoning_models()
    
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    print("""
📌 Best Models for Smart LMS:

1. **General AI Tutor & Doubt Solving:**
   ✅ openai/gpt-oss-120b (Currently using - PERFECT!)
   - Best reasoning capabilities
   - Excellent explanations
   - Handles complex queries

2. **Japanese Language Learning:**
   🔄 Consider: qwen/qwen3-32b
   - Specialized in Asian languages
   - Better Japanese grammar understanding
   - Can supplement GPT OSS 120B

3. **Quick Responses (Fast mode):**
   ⚡ openai/gpt-oss-20b
   - Much faster
   - Good for simple Q&A
   - Real-time chat

4. **Long Transcript Processing:**
   📄 moonshotai/kimi-k2-instruct
   - Longer context window
   - Better for processing full lecture transcripts
   - Great for quiz generation

5. **Audio Transcription:**
   🎤 whisper-large-v3-turbo
   - Fast and accurate
   - Supports Japanese
   - For speech-to-text

Current setup is optimal! GPT OSS 120B is the best choice for educational AI.
    """)
    print("=" * 80)


if __name__ == "__main__":
    main()
