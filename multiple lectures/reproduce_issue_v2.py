import sys
import os
import yaml

# Add parent directory to path
sys.path.append(os.getcwd())

from services.nlp import get_nlp_service

def test_vader_modification():
    nlp = get_nlp_service()
    
    # Bypassing length check by mocking config
    nlp.nlp_config['min_feedback_length'] = 0
    
    print("\n--- Baseline VADER (min_length=0) ---")
    cases = [
        "nothing",
        "nothing.",
        "nothing wrong", 
        "nothing bad",
        "nothing special",
        "bad"
    ]
    
    for text in cases:
        res = nlp.analyze_sentiment(text)
        print(f"'{text}': Label={res['label']}, Comp={res['compound']}")

    # Now modify lexicon
    print("\n--- Modified VADER (nothing = -1.5) ---")
    if hasattr(nlp, 'vader'):
        nlp.vader.lexicon['nothing'] = -1.5
    
    for text in cases:
        res = nlp.analyze_sentiment(text)
        print(f"'{text}': Label={res['label']}, Comp={res['compound']}")

if __name__ == "__main__":
    test_vader_modification()
