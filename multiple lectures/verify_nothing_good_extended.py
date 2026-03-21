import sys
import os
import yaml

# Add parent directory to path
sys.path.append(os.getcwd())

from services.nlp import get_nlp_service

def verify_nothing_good_extended():
    nlp = get_nlp_service()
    
    test_cases = [
        "nothing good about the lecture",
        "nothing good about the content",
        "nothing good about the teaching"
    ]
    
    with open("verification_extended.txt", "w") as f:
        f.write("--- Extended Verification Results ---\n")
        for text in test_cases:
            # General Sentiment
            res = nlp.analyze_sentiment(text)
            f.write(f"\nText: '{text}'\n")
            f.write(f"  General Sentiment: Label={res['label']}, Comp={res['compound']}\n")
            
            # Aspect Sentiment
            aspects = nlp.analyze_aspect_sentiment(text)
            f.write(f"  Aspect Sentiment: {aspects}\n")

if __name__ == "__main__":
    verify_nothing_good_extended()
