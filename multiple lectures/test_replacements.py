import sys
import os
import yaml

# Add parent directory to path
sys.path.append(os.getcwd())

from services.nlp import get_nlp_service

def test_replacements():
    print("\n--- Testing Replacements ---")
    
    nlp = get_nlp_service()
    
    candidates = [
        "rushed",
        "too rushed",
        "boring",
        "too lengthy",
        "failures",
        "technical failures",
        "badly paced",
        "bad",
        "confusing",
        "very confusing"
    ]
    
    for text in candidates:
        res = nlp.analyze_sentiment(text)
        print(f"'{text}': Comp={res['compound']}")

if __name__ == "__main__":
    test_replacements()
