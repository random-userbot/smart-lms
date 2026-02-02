"""
Test AI Provider Connectivity
Tests Groq and Gemini API connections
"""

import os
import sys
from groq import Groq

def test_groq_direct():
    """Test Groq API directly with simple streaming"""
    print("=" * 60)
    print("Groq API Direct Test")
    print("=" * 60)
    
    try:
        from services.config_loader import get_api_key
        api_key = get_api_key("groq")
        
        if not api_key:
            print("\n❌ No Groq API key found!")
            print("Add to config.yaml:")
            print('  groq_api_key: "your-key-here"')
            return False
        
        print(f"\n✅ API Key found: {api_key[:20]}...")
        print("\n🔍 Testing Groq API...")
        print("-" * 60)
        
        client = Groq(api_key=api_key)
        
        print("Query: Say hello in one sentence\n")
        print("Response: ", end="", flush=True)
        
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "user",
                    "content": "Say 'Hello, I am working!' in one sentence."
                }
            ],
            temperature=1,
            max_completion_tokens=100,
            top_p=1,
            stream=True,
            stop=None
        )
        
        response_text = ""
        for chunk in completion:
            content = chunk.choices[0].delta.content or ""
            print(content, end="", flush=True)
            response_text += content
        
        print("\n")
        
        if response_text:
            print("\n✅ Groq API is working!")
            return True
        else:
            print("\n❌ No response received")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def test_gemini_direct():
    """Test Gemini API directly"""
    print("\n" + "=" * 60)
    print("Gemini API Test")
    print("=" * 60)
    
    try:
        import google.generativeai as genai
        from services.config_loader import get_api_key
        
        api_key = get_api_key("gemini")
        
        if not api_key:
            print("\n❌ No Gemini API key found!")
            return False
        
        print(f"\n✅ API Key found: {api_key[:20]}...")
        print("\n🔍 Testing Gemini API...")
        print("-" * 60)
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        print("Query: Say hello in one sentence\n")
        
        response = model.generate_content("Say 'Hello, I am working!' in one sentence.")
        
        print(f"Response: {response.text}\n")
        
        print("✅ Gemini API is working!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


if __name__ == "__main__":
    groq_works = test_groq_direct()
    gemini_works = test_gemini_direct()
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Groq:   {'✅ Working' if groq_works else '❌ Failed'}")
    print(f"Gemini: {'✅ Working' if gemini_works else '❌ Failed'}")
    print("=" * 60)
    
    sys.exit(0 if (groq_works or gemini_works) else 1)
