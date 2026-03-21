import sys
import os
import yaml

# Add parent directory to path
sys.path.append(os.getcwd())

from services.nlp import get_nlp_service

def check_too_long_replacement():
    print("\n--- Checking 'too long' Replacements ---")
    
    nlp = get_nlp_service()
    
    candidates = [
        "too long",     # mapped to "too lengthy" currently
        "too lengthy",
        "boring",
        "tedious",
        "dragged on",
        "bad length",
        "too extensive"
    ]
    
    for text in candidates:
        res = nlp.analyze_sentiment(text)
        print(f"'{text}': Comp={res['compound']}")

if __name__ == "__main__":
    check_too_long_replacement()
