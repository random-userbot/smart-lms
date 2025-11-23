"""
Test Advanced NLP Features
Tests emotion detection, aspect-based sentiment, and comprehensive analysis
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.nlp import get_nlp_service
import json

def test_emotion_detection():
    """Test emotion detection"""
    print("=" * 80)
    print("TEST: EMOTION DETECTION")
    print("=" * 80)
    
    nlp_service = get_nlp_service()
    
    test_cases = [
        {
            "text": "I absolutely love this course! The professor is amazing and I'm so happy!",
            "expected_dominant": "happiness"
        },
        {
            "text": "I'm so frustrated. I can't understand anything and I'm stuck on every problem.",
            "expected_dominant": "frustration"
        },
        {
            "text": "I'm really confused about this topic. The explanation was unclear.",
            "expected_dominant": "confusion"
        },
        {
            "text": "This is terrible! The worst lecture I've ever attended. Completely awful!",
            "expected_dominant": "anger"
        },
        {
            "text": "I'm satisfied with the course content. It was helpful and useful.",
            "expected_dominant": "satisfaction"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        text = test_case["text"]
        expected = test_case["expected_dominant"]
        
        emotions = nlp_service.detect_emotions(text)
        dominant = max(emotions.items(), key=lambda x: x[1])[0] if any(emotions.values()) else 'neutral'
        
        status = "✓ PASS" if dominant == expected else "✗ FAIL"
        
        print(f"\nTest {i}: {status}")
        print(f"  Text: {text[:70]}...")
        print(f"  Expected: {expected} | Got: {dominant}")
        print(f"  Emotion Scores:")
        for emotion, score in emotions.items():
            if score > 0:
                print(f"    {emotion}: {score:.3f}")
    
    print(f"\n{'=' * 80}\n")

def test_aspect_sentiment():
    """Test aspect-based sentiment analysis"""
    print("=" * 80)
    print("TEST: ASPECT-BASED SENTIMENT ANALYSIS")
    print("=" * 80)
    
    nlp_service = get_nlp_service()
    
    test_texts = [
        "The content was excellent but the audio quality was terrible.",
        "Great teaching style and clear delivery. Very engaging professor!",
        "The material is too difficult and the technical setup keeps failing.",
        "Interesting topic with good examples. The slides were well designed.",
        "Poor presentation, confusing explanations, but the content itself is useful."
    ]
    
    for i, text in enumerate(test_texts, 1):
        aspects = nlp_service.analyze_aspect_sentiment(text)
        
        print(f"\nTest {i}:")
        print(f"  Text: {text}")
        print(f"  Aspect Analysis:")
        
        for aspect, result in aspects.items():
            if result['mentioned']:
                emoji = "😊" if result['sentiment'] == 'positive' else "😟" if result['sentiment'] == 'negative' else "😐"
                print(f"    {aspect}: {emoji} {result['sentiment']} (score: {result['score']:.2f})")
    
    print(f"\n{'=' * 80}\n")

def test_comprehensive_analysis():
    """Test comprehensive feedback analysis"""
    print("=" * 80)
    print("TEST: COMPREHENSIVE ANALYSIS")
    print("=" * 80)
    
    nlp_service = get_nlp_service()
    
    feedback_samples = [
        """This was an outstanding lecture! The professor explained complex concepts
        with crystal clarity using real-world examples. The interactive elements kept
        me engaged throughout. I especially loved the practical demonstrations and
        the Q&A session at the end. Perfect pacing and excellent visual aids!""",
        
        """I'm really struggling with this material. The pace is way too fast and
        I can't keep up. The explanations are confusing and I don't understand most
        of the concepts. Plus, there were constant audio glitches that made it even
        harder to follow. I feel frustrated and lost.""",
        
        """Mixed feelings about this lecture. The content quality is good and the
        topic is interesting. However, the technical issues (poor video quality,
        lag, audio cutting out) really disrupted the learning experience. The
        professor's teaching style is engaging when I can actually hear them.""",
        
        """Decent lecture overall. The material was well-organized and the examples
        were relevant. Could use more interactive elements to keep students engaged.
        The difficulty level was appropriate for the course. Slides could be improved
        with better graphics."""
    ]
    
    for i, text in enumerate(feedback_samples, 1):
        print(f"\n{'=' * 40}")
        print(f"FEEDBACK #{i}")
        print(f"{'=' * 40}")
        
        analysis = nlp_service.comprehensive_analysis(text)
        
        # Display results in a formatted way
        print(f"\n📊 OVERALL METRICS:")
        print(f"  Quality Score: {analysis['quality_score']:.1f}/100")
        print(f"  Sentiment: {analysis['sentiment']['label'].upper()} (compound: {analysis['sentiment']['compound']:.3f})")
        print(f"  Dominant Emotion: {analysis['dominant_emotion']}")
        print(f"  Word Count: {analysis['word_count']}")
        
        print(f"\n😊 EMOTIONS:")
        for emotion, score in analysis['emotions'].items():
            if score > 0.1:
                bar = "█" * int(score * 10)
                print(f"  {emotion.capitalize():15s} {bar} {score:.3f}")
        
        print(f"\n🏷️  THEMES ({len(analysis['themes'])}):")
        if analysis['themes']:
            print(f"  {', '.join(analysis['themes'])}")
        else:
            print(f"  None detected")
        
        print(f"\n🔑 TOP KEYWORDS:")
        print(f"  {', '.join(analysis['keywords'][:8])}")
        
        print(f"\n📋 ASPECT SENTIMENT:")
        for aspect, result in analysis['aspect_sentiment'].items():
            if result['mentioned']:
                emoji = "✅" if result['sentiment'] == 'positive' else "❌" if result['sentiment'] == 'negative' else "➖"
                print(f"  {emoji} {aspect.capitalize():12s}: {result['sentiment']} ({result['score']:+.2f})")
    
    print(f"\n{'=' * 80}\n")

def test_mixed_sentiment():
    """Test improved mixed sentiment handling"""
    print("=" * 80)
    print("TEST: MIXED SENTIMENT HANDLING")
    print("=" * 80)
    
    nlp_service = get_nlp_service()
    
    test_cases = [
        {
            "text": "Great content but terrible audio quality.",
            "expected": "positive"  # Positive aspect is more important
        },
        {
            "text": "The professor is amazing and explains well, but the technical issues were frustrating.",
            "expected": "positive"
        },
        {
            "text": "Interesting topic, however the delivery was poor and confusing.",
            "expected": "negative"
        },
        {
            "text": "Good examples but way too difficult for beginners.",
            "expected": "negative"
        }
    ]
    
    correct = 0
    for i, test_case in enumerate(test_cases, 1):
        text = test_case["text"]
        expected = test_case["expected"]
        
        sentiment = nlp_service.analyze_sentiment(text)
        result = sentiment['label']
        
        status = "✓ PASS" if result == expected else "✗ FAIL"
        if result == expected:
            correct += 1
        
        is_mixed = sentiment.get('is_mixed', False)
        
        print(f"\nTest {i}: {status}")
        print(f"  Text: {text}")
        print(f"  Expected: {expected} | Got: {result}")
        print(f"  Mixed Sentiment: {is_mixed}")
        print(f"  Scores: pos={sentiment['positive']:.3f}, neg={sentiment['negative']:.3f}, compound={sentiment['compound']:.3f}")
    
    accuracy = (correct / len(test_cases)) * 100
    print(f"\n  Accuracy: {correct}/{len(test_cases)} ({accuracy:.1f}%)")
    print(f"\n{'=' * 80}\n")

def test_quality_score():
    """Test quality score calculation"""
    print("=" * 80)
    print("TEST: QUALITY SCORE CALCULATION")
    print("=" * 80)
    
    nlp_service = get_nlp_service()
    
    test_feedbacks = [
        ("Excellent lecture! Clear, engaging, and well-organized.", "Expected: High (85-100)"),
        ("The content was confusing and the technical issues made it worse.", "Expected: Low (0-40)"),
        ("Decent lecture with some good points and some areas for improvement.", "Expected: Medium (50-70)"),
        ("Amazing professor but terrible audio quality throughout.", "Expected: Medium-High (60-80)"),
        ("I'm so frustrated and confused by this difficult material.", "Expected: Low (20-45)")
    ]
    
    for text, expected_range in test_feedbacks:
        analysis = nlp_service.comprehensive_analysis(text)
        quality = analysis['quality_score']
        
        print(f"\n  Text: {text}")
        print(f"  Quality Score: {quality:.1f}/100")
        print(f"  {expected_range}")
        print(f"  Sentiment: {analysis['sentiment']['label']} ({analysis['sentiment']['compound']:+.3f})")
        print(f"  Dominant Emotion: {analysis['dominant_emotion']}")
    
    print(f"\n{'=' * 80}\n")

def run_advanced_tests():
    """Run all advanced NLP tests"""
    print("\n" + "=" * 80)
    print("SMART LMS - ADVANCED NLP FEATURES TEST SUITE")
    print("=" * 80 + "\n")
    
    try:
        test_emotion_detection()
        test_aspect_sentiment()
        test_mixed_sentiment()
        test_quality_score()
        test_comprehensive_analysis()
        
        print("=" * 80)
        print("✓ ALL ADVANCED TESTS COMPLETED SUCCESSFULLY")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_advanced_tests()
