"""
Test NLP Service - Comprehensive Testing
Tests sentiment analysis, keyword extraction, theme detection, and bias correction
"""

import sys
import os
from datetime import datetime
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.nlp import get_nlp_service

def test_sentiment_analysis():
    """Test sentiment analysis with various texts"""
    print("=" * 80)
    print("TEST 1: SENTIMENT ANALYSIS")
    print("=" * 80)
    
    nlp_service = get_nlp_service()
    
    test_cases = [
        {
            "text": "This lecture was amazing! The professor explained everything clearly and the examples were very helpful.",
            "expected": "positive"
        },
        {
            "text": "The content was confusing and the pace was too fast. I couldn't understand most of it.",
            "expected": "negative"
        },
        {
            "text": "The lecture covered the basics of machine learning. Topics included linear regression and decision trees.",
            "expected": "neutral"
        },
        {
            "text": "Great teacher, interesting subject, but the audio quality was poor.",
            "expected": "positive"  # Mixed but overall positive
        },
        {
            "text": "Terrible experience. The instructor was unprepared and the material was outdated.",
            "expected": "negative"
        },
        {
            "text": "I love how the professor uses real-world examples. Very engaging and easy to follow!",
            "expected": "positive"
        },
        {
            "text": "Too much information in too little time. Need more practice problems.",
            "expected": "negative"
        },
        {
            "text": "",  # Empty text
            "expected": "neutral"
        }
    ]
    
    correct_predictions = 0
    total_tests = len([tc for tc in test_cases if tc["text"]])  # Exclude empty
    
    for i, test_case in enumerate(test_cases, 1):
        text = test_case["text"]
        expected = test_case["expected"]
        
        if not text:
            print(f"\nTest {i}: [EMPTY TEXT]")
            result = nlp_service.analyze_sentiment(text)
            print(f"  Result: {result['label']} (should be neutral)")
            print(f"  Scores: {result}")
            continue
        
        result = nlp_service.analyze_sentiment(text)
        status = "✓ PASS" if result['label'] == expected else "✗ FAIL"
        
        if result['label'] == expected:
            correct_predictions += 1
        
        print(f"\nTest {i}: {status}")
        print(f"  Text: {text[:80]}...")
        print(f"  Expected: {expected} | Got: {result['label']}")
        print(f"  Compound: {result['compound']:.3f}")
        print(f"  Scores: pos={result['positive']:.3f}, neu={result['neutral']:.3f}, neg={result['negative']:.3f}")
    
    accuracy = (correct_predictions / total_tests) * 100
    print(f"\n{'=' * 80}")
    print(f"SENTIMENT ANALYSIS ACCURACY: {correct_predictions}/{total_tests} ({accuracy:.1f}%)")
    print(f"{'=' * 80}\n")
    
    return accuracy

def test_keyword_extraction():
    """Test keyword extraction"""
    print("=" * 80)
    print("TEST 2: KEYWORD EXTRACTION")
    print("=" * 80)
    
    nlp_service = get_nlp_service()
    
    test_texts = [
        """The deep learning lecture covered neural networks, backpropagation, and gradient descent. 
        The professor demonstrated convolutional neural networks for image classification. 
        We also learned about recurrent neural networks for sequence processing.""",
        
        """Great lecture on database systems! Topics included SQL queries, normalization, 
        indexing, and transaction management. The examples using real databases were very helpful.""",
        
        """The teaching style was engaging and the professor used many practical examples. 
        However, the audio quality was poor and there were some technical glitches during the video.""",
        
        "Short text."  # Edge case
    ]
    
    for i, text in enumerate(test_texts, 1):
        keywords = nlp_service.extract_keywords(text, top_n=10)
        print(f"\nTest {i}:")
        print(f"  Text: {text[:80]}...")
        print(f"  Extracted Keywords ({len(keywords)}): {', '.join(keywords)}")
    
    print(f"\n{'=' * 80}\n")

def test_theme_detection():
    """Test theme detection"""
    print("=" * 80)
    print("TEST 3: THEME DETECTION")
    print("=" * 80)
    
    nlp_service = get_nlp_service()
    
    test_cases = [
        {
            "text": "The content was well organized and the examples were practical.",
            "expected_themes": ["content_quality", "organization", "examples"]
        },
        {
            "text": "The teaching style was clear but the pace was too fast.",
            "expected_themes": ["teaching_style", "clarity", "pace"]
        },
        {
            "text": "Very engaging lecture with good visual aids and clear explanations.",
            "expected_themes": ["engagement", "visual_aids", "clarity"]
        },
        {
            "text": "Technical issues with audio and video buffering made it difficult to follow.",
            "expected_themes": ["technical_issues"]
        },
        {
            "text": "The material was too difficult and confusing for beginners.",
            "expected_themes": ["difficulty", "clarity"]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        text = test_case["text"]
        expected = test_case["expected_themes"]
        
        detected = nlp_service.detect_themes(text)
        
        # Check if at least one expected theme was detected
        found = any(theme in detected for theme in expected)
        status = "✓ PASS" if found else "✗ FAIL"
        
        print(f"\nTest {i}: {status}")
        print(f"  Text: {text}")
        print(f"  Expected themes: {', '.join(expected)}")
        print(f"  Detected themes: {', '.join(detected) if detected else 'None'}")
    
    print(f"\n{'=' * 80}\n")

def test_batch_analysis():
    """Test batch feedback analysis"""
    print("=" * 80)
    print("TEST 4: BATCH FEEDBACK ANALYSIS")
    print("=" * 80)
    
    nlp_service = get_nlp_service()
    
    feedback_texts = [
        "Excellent lecture! Very clear explanations.",
        "Great examples and engaging teaching style.",
        "The content was confusing and poorly organized.",
        "Good pace, but audio quality was bad.",
        "Amazing professor! Learned a lot today.",
        "Too fast, couldn't keep up with the material.",
        "Perfect balance of theory and practice.",
        "Boring lecture, need more interactive elements.",
        "Well structured content with helpful examples.",
        "Unclear explanations, need better visual aids."
    ]
    
    result = nlp_service.analyze_feedback_batch(feedback_texts)
    
    print(f"\nBatch Analysis Results:")
    print(f"  Total Feedbacks: {result['total_count']}")
    print(f"  Positive: {result['positive_count']} ({result['positive_percentage']:.1f}%)")
    print(f"  Neutral: {result['neutral_count']} ({result['neutral_percentage']:.1f}%)")
    print(f"  Negative: {result['negative_count']} ({result['negative_percentage']:.1f}%)")
    print(f"  Avg Compound Score: {result['avg_compound']:.3f}")
    print(f"  Top Topics: {', '.join(result['topics'])}")
    
    print(f"\n{'=' * 80}\n")

def test_bias_correction():
    """Test bias correction functionality"""
    print("=" * 80)
    print("TEST 5: BIAS CORRECTION")
    print("=" * 80)
    
    nlp_service = get_nlp_service()
    
    # Simulate feedback data with potential bias
    # Students with higher engagement/grades might rate higher
    feedback_data = [
        {'student_id': 's1', 'rating': 5, 'text': 'Great!'},
        {'student_id': 's2', 'rating': 4, 'text': 'Good'},
        {'student_id': 's3', 'rating': 2, 'text': 'Not good'},
        {'student_id': 's4', 'rating': 5, 'text': 'Excellent'},
        {'student_id': 's5', 'rating': 3, 'text': 'Average'},
    ]
    
    engagement_data = [
        {'student_id': 's1', 'engagement_score': 85},
        {'student_id': 's2', 'engagement_score': 75},
        {'student_id': 's3', 'engagement_score': 45},
        {'student_id': 's4', 'engagement_score': 90},
        {'student_id': 's5', 'engagement_score': 60},
    ]
    
    grades_data = [
        {'student_id': 's1', 'percentage': 88},
        {'student_id': 's2', 'percentage': 79},
        {'student_id': 's3', 'percentage': 52},
        {'student_id': 's4', 'percentage': 92},
        {'student_id': 's5', 'percentage': 65},
    ]
    
    # Test with bias correction enabled
    if nlp_service.bias_correction_enabled:
        corrected = nlp_service.correct_bias(feedback_data, engagement_data, grades_data)
        
        print("\nBias Correction Results:")
        print(f"  Method: {nlp_service.nlp_config['bias_correction']['method']}")
        print("\n  Original vs Corrected Ratings:")
        
        for i, (original, corrected_item) in enumerate(zip(feedback_data, corrected)):
            original_rating = original['rating']
            corrected_rating = corrected_item.get('rating_corrected', corrected_item['rating'])
            diff = corrected_rating - original_rating
            
            print(f"    Student {original['student_id']}: {original_rating:.2f} → {corrected_rating:.2f} (Δ{diff:+.2f})")
    else:
        print("\n  Bias correction is DISABLED in config.yaml")
        print("  To enable: set nlp.bias_correction.enabled = true")
    
    print(f"\n{'=' * 80}\n")

def test_real_world_scenarios():
    """Test with realistic student feedback scenarios"""
    print("=" * 80)
    print("TEST 6: REAL-WORLD FEEDBACK SCENARIOS")
    print("=" * 80)
    
    nlp_service = get_nlp_service()
    
    scenarios = [
        {
            "name": "Enthusiastic Student",
            "text": "I absolutely loved this lecture! The professor's passion for the subject really shows. The examples were spot-on and helped me understand complex concepts. Can't wait for the next class!"
        },
        {
            "name": "Struggling Student",
            "text": "I'm finding this material really challenging. The professor moves too quickly and I get lost. Would appreciate more practice problems and slower explanations of difficult topics."
        },
        {
            "name": "Technical Issues",
            "text": "The content seems interesting but I couldn't focus because of constant audio glitches and video buffering. Also, the slides were too small to read. Please fix these technical problems."
        },
        {
            "name": "Mixed Feedback",
            "text": "Good explanations and interesting examples. However, the lecture could be more interactive. Maybe add some polls or Q&A sessions to keep students engaged throughout."
        },
        {
            "name": "Constructive Criticism",
            "text": "The theoretical foundation is solid, but we need more practical applications. Real-world case studies would make the content more relatable and easier to remember."
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{scenario['name']}:")
        print(f"  Feedback: {scenario['text'][:100]}...")
        
        # Full analysis
        sentiment = nlp_service.analyze_sentiment(scenario['text'])
        keywords = nlp_service.extract_keywords(scenario['text'], top_n=5)
        themes = nlp_service.detect_themes(scenario['text'])
        
        print(f"  Sentiment: {sentiment['label'].upper()} (compound: {sentiment['compound']:.3f})")
        print(f"  Key Topics: {', '.join(keywords[:5])}")
        print(f"  Themes: {', '.join(themes)}")
    
    print(f"\n{'=' * 80}\n")

def test_performance():
    """Test performance with large batch"""
    print("=" * 80)
    print("TEST 7: PERFORMANCE TEST")
    print("=" * 80)
    
    import time
    nlp_service = get_nlp_service()
    
    # Generate test data
    test_texts = [
        "This is a sample feedback text for testing performance.",
        "Another feedback with different content and sentiment.",
        "Great lecture with excellent explanations and examples.",
    ] * 100  # 300 texts
    
    print(f"\nTesting with {len(test_texts)} feedback texts...")
    
    start_time = time.time()
    
    for text in test_texts:
        _ = nlp_service.analyze_sentiment(text)
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    texts_per_second = len(test_texts) / elapsed
    
    print(f"  Total Time: {elapsed:.2f} seconds")
    print(f"  Processing Rate: {texts_per_second:.1f} texts/second")
    print(f"  Avg Time per Text: {(elapsed/len(test_texts))*1000:.2f} ms")
    
    print(f"\n{'=' * 80}\n")

def run_all_tests():
    """Run all NLP tests"""
    print("\n" + "=" * 80)
    print("SMART LMS - NLP SERVICE COMPREHENSIVE TEST SUITE")
    print("=" * 80 + "\n")
    
    try:
        # Run tests
        sentiment_accuracy = test_sentiment_analysis()
        test_keyword_extraction()
        test_theme_detection()
        test_batch_analysis()
        test_bias_correction()
        test_real_world_scenarios()
        test_performance()
        
        # Summary
        print("=" * 80)
        print("TEST SUITE COMPLETE")
        print("=" * 80)
        print(f"  Overall Status: ✓ ALL TESTS COMPLETED")
        print(f"  Sentiment Accuracy: {sentiment_accuracy:.1f}%")
        print(f"  Model: {get_nlp_service().sentiment_model.upper()}")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\n")

if __name__ == "__main__":
    run_all_tests()
