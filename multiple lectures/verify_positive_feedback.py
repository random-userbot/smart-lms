import sys
import os
import yaml

# Add parent directory to path
sys.path.append(os.getcwd())

from services.nlp import get_nlp_service

def verify_positive_feedback():
    print("\n--- Verifying Positive Feedback ---")
    
    nlp = get_nlp_service()
    
    test_cases = [
        "The sessions are interactive and engaging.",
        "Audio and video quality are excellent.",
        "The lecturer answers questions patiently."
    ]
    
    with open("verification_positive.txt", "w") as f:
        f.write("--- Verification Results ---\n")
        for text in test_cases:
            res = nlp.analyze_sentiment(text)
            f.write(f"\nText: '{text}'\n")
            f.write(f"  Label={res['label']}, Comp={res['compound']}\n")
            f.write(f"  Pos={res['positive']}, Neu={res['neutral']}, Neg={res['negative']}\n")
            
            # Check if cleaning is affecting it
            cleaned = nlp.clean_text(text)
            f.write(f"  Cleaned: '{cleaned}'\n")

if __name__ == "__main__":
    verify_positive_feedback()
