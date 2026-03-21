
import sys
import os

# Add parent directory to path to import services
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.nlp import NLPService

def test_sentiment():
    nlp = NLPService("config.yaml")
    
    test_cases = [
        ("Pace should be increased.", "negative"),
        ("The pace is perfect.", "positive"),
        ("Pace is perfect.", "positive"),
        ("The lecture pace is moderate.", "neutral"),
        ("Lecture pace is moderate.", "neutral")
    ]
    
    print(f"Active Sentiment Model: {nlp.sentiment_model}")
    print("-" * 50)
    
    all_passed = True
    for text, expected in test_cases:
        result = nlp.analyze_sentiment(text)
        label = result['label']
        compound = result['compound']
        
        print(f"Text: '{text}'")
        print(f"Expected: {expected}, Got: {label} (Compound: {compound})")
        
        if label != expected:
            print("❌ FIXED NEEDED")
            all_passed = False
        else:
            print("✅ PASSED")
        print("-" * 50)

    if all_passed:
        print("\nAll test cases passed!")
    else:
        print("\nSome test cases failed.")

if __name__ == "__main__":
    test_sentiment()
