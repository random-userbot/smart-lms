import sys
import os
import yaml

# Add parent directory to path
sys.path.append(os.getcwd())

from services.nlp import get_nlp_service

def verify_negative_feedback():
    print("\n--- Verifying Negative Feedback ---")
    
    nlp = get_nlp_service()
    
    test_cases = [
        "The instructor speaks too fast.",
        "Recorded videos are too long and confusing.",
        "Technical issues happen in almost every session.",
        "too fast",
        "too long",
        "confusing",
        "technical issues"
    ]
    
    with open("verification_negative.txt", "w") as f:
        f.write("--- Verification Results ---\n")
        for text in test_cases:
            res = nlp.analyze_sentiment(text)
            f.write(f"\nText: '{text}'\n")
            f.write(f"  Label={res['label']}, Comp={res['compound']}\n")
            f.write(f"  Pos={res['positive']}, Neu={res['neutral']}, Neg={res['negative']}\n")

if __name__ == "__main__":
    verify_negative_feedback()
