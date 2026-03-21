import sys
import os
import yaml

# Add parent directory to path
sys.path.append(os.getcwd())

from services.nlp import get_nlp_service

def verify_fix():
    print("\n--- Verifying Fix for 'nothing' and short words ---")
    
    # Reload config to get new min_length
    nlp = get_nlp_service()
    
    test_cases = [
        "nothing",        # Should be Negative
        "Nothing.",       # Should be Negative
        "nothing wrong",  # Should still be Positive/Neutral
        "nothing bad",    # Should still be Positive/Neutral
        "bad",            # Should be Negative (length > 2)
        "good",           # Should be Positive (length > 2)
        "ok"              # Should be Positive/Neutral (length >= 2)
    ]
    
    for text in test_cases:
        res = nlp.analyze_sentiment(text)
        print(f"'{text}': Label={res['label']}, Comp={res['compound']}")
        
        # Assertions for automated verification
        if text.lower() in ["nothing", "nothing."]:
            if res['label'] != 'negative':
                print(f"❌ FAIL: '{text}' should be negative")
        elif text == "nothing wrong":
             if res['label'] == 'negative':
                print(f"❌ FAIL: '{text}' should NOT be negative")
        elif text == "bad":
            if res['label'] != 'negative':
                print(f"❌ FAIL: '{text}' should be negative")

if __name__ == "__main__":
    verify_fix()
