import sys
import os

# Add parent directory to path
sys.path.append(os.getcwd())

from services.nlp import get_nlp_service

def test_sentiment():
    nlp = get_nlp_service()
    
    test_cases = [
        "The audio quality must be improved for better clarity.",
        "The screen froze multiple times - please check your network.",
        "The pace was too fast, and it was hard to keep up.",
        "Examples were too few; more illustration is needed."
    ]
    
    print("--- Testing Sentiment Analysis ---")
    for text in test_cases:
        result = nlp.analyze_sentiment(text)
        print(f"\nText: {text}")
        print(f"Label: {result['label']}")
        print(f"Compound: {result['compound']}")
        print(f"Pos: {result['positive']}, Neg: {result['negative']}, Neu: {result['neutral']}")

if __name__ == "__main__":
    test_sentiment()
