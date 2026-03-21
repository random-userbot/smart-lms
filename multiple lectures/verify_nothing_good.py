import sys
import os
import yaml

# Add parent directory to path
sys.path.append(os.getcwd())

from services.nlp import get_nlp_service

def verify_nothing_good():
    print("\n--- Verifying 'nothing good' ---")
    
    nlp = get_nlp_service()
    
    test_cases = [
        "nothing",
        "nothing good",
        "nothing good about the lecture",
        "there was nothing good",
        "not good",
        "nothing interesting",
        "nothing wrong" # Should remain positive
    ]
    
    for text in test_cases:
        res = nlp.analyze_sentiment(text)
        print(f"'{text}': Label={res['label']}, Comp={res['compound']}, Pos={res['positive']}, Neg={res['negative']}, Mixed={res.get('is_mixed', False)}")

if __name__ == "__main__":
    verify_nothing_good()
