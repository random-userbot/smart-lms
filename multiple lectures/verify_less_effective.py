import sys
import os
import yaml

# Add parent directory to path
sys.path.append(os.getcwd())

from services.nlp import get_nlp_service

def verify_less_effective():
    print("\n--- Verifying 'less effective' ---")
    
    nlp = get_nlp_service()
    
    test_cases = [
        "Online lectures feel less effective than offline classes",
        "less effective",
        "not effective",
        "effective",
        "much less effective"
    ]
    
    with open("verification_less_effective.txt", "w") as f:
        f.write("--- Verification Results ---\n")
        for text in test_cases:
            res = nlp.analyze_sentiment(text)
            f.write(f"\nText: '{text}'\n")
            f.write(f"  Label={res['label']}, Comp={res['compound']}\n")
            f.write(f"  Pos={res['positive']}, Neu={res['neutral']}, Neg={res['negative']}\n")
            
            # Check aspect sentiment too
            aspects = nlp.analyze_aspect_sentiment(text)
            f.write(f"  Aspects: {aspects}\n")

if __name__ == "__main__":
    verify_less_effective()
