"""
NLP Service Demo - Real-World Usage Example
Demonstrates how to use the enhanced NLP service for lecture feedback analysis
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.nlp import get_nlp_service
from datetime import datetime
from collections import Counter
import json

def demo_single_feedback_analysis():
    """Demo: Analyze a single student feedback"""
    print("\n" + "="*80)
    print("DEMO 1: SINGLE FEEDBACK ANALYSIS")
    print("="*80)
    
    nlp_service = get_nlp_service()
    
    feedback = """
    I really enjoyed this lecture on machine learning! The professor explained
    neural networks very clearly with excellent visualizations. The examples
    from self-driving cars were fascinating. However, the audio quality was
    sometimes poor which made it hard to hear. Overall, great content!
    """
    
    print("\n📝 FEEDBACK TEXT:")
    print(feedback.strip())
    print("\n" + "-"*80)
    
    # Perform comprehensive analysis
    analysis = nlp_service.comprehensive_analysis(feedback)
    
    # Display results
    print("\n📊 ANALYSIS RESULTS:")
    print(f"\n  Quality Score: {analysis['quality_score']:.1f}/100")
    
    # Sentiment with emoji
    sentiment_emoji = {
        'positive': '😊',
        'negative': '😟',
        'neutral': '😐'
    }
    emoji = sentiment_emoji.get(analysis['sentiment']['label'], '😐')
    print(f"  Sentiment: {emoji} {analysis['sentiment']['label'].upper()}")
    print(f"  Confidence: {abs(analysis['sentiment']['compound']):.3f}")
    
    # Emotions
    print(f"\n  🎭 Emotions Detected:")
    for emotion, score in analysis['emotions'].items():
        if score > 0.1:
            bar = "█" * int(score * 20)
            print(f"    {emotion.capitalize():15s} {bar} {score:.3f}")
    
    # Themes
    print(f"\n  🏷️  Themes ({len(analysis['themes'])}):")
    for theme in analysis['themes']:
        print(f"    • {theme.replace('_', ' ').title()}")
    
    # Keywords
    print(f"\n  🔑 Key Topics:")
    print(f"    {', '.join(analysis['keywords'][:8])}")
    
    # Aspect analysis
    print(f"\n  📋 Aspect-Specific Feedback:")
    for aspect, result in analysis['aspect_sentiment'].items():
        if result['mentioned']:
            aspect_emoji = '✅' if result['sentiment'] == 'positive' else '❌' if result['sentiment'] == 'negative' else '➖'
            print(f"    {aspect_emoji} {aspect.capitalize():12s}: {result['sentiment']:8s} ({result['score']:+.2f})")
    
    print("\n" + "="*80)

def demo_batch_analysis():
    """Demo: Analyze multiple feedbacks for a lecture"""
    print("\n" + "="*80)
    print("DEMO 2: BATCH FEEDBACK ANALYSIS (Lecture Review)")
    print("="*80)
    
    nlp_service = get_nlp_service()
    
    # Simulate feedbacks from multiple students
    feedbacks = [
        "Excellent lecture! Very clear and engaging.",
        "I loved the practical examples. Made everything easy to understand.",
        "Great content but the pace was a bit too fast.",
        "Very informative. The professor is knowledgeable.",
        "The audio quality was poor. Hard to follow at times.",
        "Confusing explanations. I didn't understand the key concepts.",
        "Amazing teaching style! Best lecture so far.",
        "Good material but could use more interactive elements.",
        "The slides were well-designed and helpful.",
        "I'm struggling with this topic. Need more practice problems."
    ]
    
    print(f"\n📚 Analyzing {len(feedbacks)} student feedbacks...")
    print("-"*80)
    
    # Analyze each feedback
    analyses = []
    for feedback in feedbacks:
        analysis = nlp_service.comprehensive_analysis(feedback)
        analyses.append(analysis)
    
    # Calculate aggregate metrics
    avg_quality = sum(a['quality_score'] for a in analyses) / len(analyses)
    
    sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
    for analysis in analyses:
        sentiment_counts[analysis['sentiment']['label']] += 1
    
    # Collect all emotions
    emotion_totals = {}
    for analysis in analyses:
        for emotion, score in analysis['emotions'].items():
            if emotion not in emotion_totals:
                emotion_totals[emotion] = []
            emotion_totals[emotion].append(score)
    
    # Average emotions
    avg_emotions = {
        emotion: sum(scores) / len(scores) 
        for emotion, scores in emotion_totals.items()
    }
    
    # Collect all themes
    all_themes = []
    for analysis in analyses:
        all_themes.extend(analysis['themes'])
    theme_counts = Counter(all_themes)
    
    # Display aggregate results
    print("\n📊 AGGREGATE RESULTS:")
    print(f"\n  Average Quality Score: {avg_quality:.1f}/100")
    
    print(f"\n  Sentiment Distribution:")
    total = sum(sentiment_counts.values())
    for sentiment, count in sentiment_counts.items():
        percentage = (count / total) * 100
        bar = "█" * int(percentage / 5)
        emoji = '😊' if sentiment == 'positive' else '😟' if sentiment == 'negative' else '😐'
        print(f"    {emoji} {sentiment.capitalize():8s} {bar} {count:2d} ({percentage:.1f}%)")
    
    print(f"\n  Average Emotions Across All Feedbacks:")
    for emotion, score in sorted(avg_emotions.items(), key=lambda x: -x[1]):
        if score > 0.05:
            bar = "█" * int(score * 30)
            print(f"    {emotion.capitalize():15s} {bar} {score:.3f}")
    
    print(f"\n  Most Common Themes:")
    for theme, count in theme_counts.most_common(5):
        percentage = (count / len(feedbacks)) * 100
        print(f"    • {theme.replace('_', ' ').title():20s} mentioned in {count}/{len(feedbacks)} feedbacks ({percentage:.0f}%)")
    
    # Identify areas needing attention
    print(f"\n  ⚠️  Areas Needing Attention:")
    negative_feedbacks = [a for a in analyses if a['sentiment']['label'] == 'negative']
    if negative_feedbacks:
        neg_themes = []
        for analysis in negative_feedbacks:
            neg_themes.extend(analysis['themes'])
        neg_theme_counts = Counter(neg_themes)
        
        for theme, count in neg_theme_counts.most_common(3):
            print(f"    • {theme.replace('_', ' ').title()}: {count} negative mention(s)")
    else:
        print(f"    None - all feedback is positive or neutral!")
    
    print("\n" + "="*80)

def demo_teacher_dashboard():
    """Demo: Teacher dashboard with actionable insights"""
    print("\n" + "="*80)
    print("DEMO 3: TEACHER DASHBOARD - ACTIONABLE INSIGHTS")
    print("="*80)
    
    nlp_service = get_nlp_service()
    
    # Simulate recent lecture feedbacks
    recent_feedbacks = [
        {
            'text': "The explanation of gradient descent was confusing. I didn't understand the math.",
            'timestamp': '2024-01-15 14:30',
            'student_id': 's1'
        },
        {
            'text': "Too much content in one lecture. Felt rushed and overwhelming.",
            'timestamp': '2024-01-15 14:35',
            'student_id': 's2'
        },
        {
            'text': "Great lecture but audio kept cutting out. Very frustrating!",
            'timestamp': '2024-01-15 14:40',
            'student_id': 's3'
        },
        {
            'text': "I'm confused about backpropagation. Can we have a review session?",
            'timestamp': '2024-01-15 14:45',
            'student_id': 's4'
        }
    ]
    
    print(f"\n📢 Recent Feedback Analysis ({len(recent_feedbacks)} new feedbacks)")
    print("-"*80)
    
    # Analyze each
    insights = []
    for fb in recent_feedbacks:
        analysis = nlp_service.comprehensive_analysis(fb['text'])
        analysis['timestamp'] = fb['timestamp']
        analysis['student_id'] = fb['student_id']
        insights.append(analysis)
    
    # Generate recommendations
    print("\n💡 ACTIONABLE INSIGHTS & RECOMMENDATIONS:")
    
    # Check for confusion
    confused_students = [i for i in insights if i['emotions']['confusion'] > 0.3]
    if confused_students:
        print(f"\n  ⚠️  ALERT: {len(confused_students)}/{len(insights)} students are confused")
        confused_themes = []
        for insight in confused_students:
            confused_themes.extend(insight['themes'])
        
        common_confusion_areas = Counter(confused_themes).most_common(3)
        print(f"     Common issues: {', '.join([t[0] for t in common_confusion_areas])}")
        print(f"     💊 Recommendation: Schedule a review session or post clarification video")
    
    # Check for frustration
    frustrated_students = [i for i in insights if i['emotions']['frustration'] > 0.3]
    if frustrated_students:
        print(f"\n  ⚠️  ALERT: {len(frustrated_students)}/{len(insights)} students are frustrated")
        print(f"     💊 Recommendation: Reach out individually to offer support")
    
    # Check for technical issues
    tech_issues = [i for i in insights if 'technical_issues' in i['themes']]
    if tech_issues:
        print(f"\n  🔧 ALERT: {len(tech_issues)}/{len(insights)} reported technical issues")
        tech_aspects = [i['aspect_sentiment'].get('technical', {}) for i in tech_issues]
        print(f"     💊 Recommendation: Check recording equipment and internet connection")
    
    # Check for pace issues
    pace_issues = [i for i in insights if 'pace' in i['themes']]
    if pace_issues:
        print(f"\n  ⏱️  ALERT: {len(pace_issues)}/{len(insights)} mentioned pace concerns")
        print(f"     💊 Recommendation: Slow down and check for understanding more frequently")
    
    # Positive feedback
    positive = [i for i in insights if i['sentiment']['label'] == 'positive']
    if positive:
        print(f"\n  ✅ POSITIVE: {len(positive)}/{len(insights)} gave positive feedback")
        # Find what they liked
        positive_themes = []
        for insight in positive:
            positive_themes.extend(insight['themes'])
        if positive_themes:
            best_aspects = Counter(positive_themes).most_common(3)
            print(f"     Students appreciate: {', '.join([t[0].replace('_', ' ') for t in best_aspects])}")
            print(f"     💡 Keep doing more of this!")
    
    # Overall quality trend
    avg_quality = sum(i['quality_score'] for i in insights) / len(insights)
    print(f"\n  📈 Current Quality Score: {avg_quality:.1f}/100")
    
    if avg_quality < 50:
        print(f"     ⚠️  Below average - immediate action needed!")
    elif avg_quality < 70:
        print(f"     ⚠️  Room for improvement")
    elif avg_quality < 85:
        print(f"     ✅ Good quality")
    else:
        print(f"     ✅ Excellent quality!")
    
    print("\n" + "="*80)

def demo_emotion_tracking():
    """Demo: Track emotions over the semester"""
    print("\n" + "="*80)
    print("DEMO 4: EMOTION TRACKING OVER TIME")
    print("="*80)
    
    nlp_service = get_nlp_service()
    
    # Simulate feedback from different weeks
    weekly_feedbacks = {
        'Week 1': ["Great start! Excited to learn.", "Clear introduction.", "Looking forward to this course!"],
        'Week 3': ["Getting harder but manageable.", "Need more practice.", "Interesting but challenging."],
        'Week 5': ["Feeling overwhelmed.", "Too much material.", "Confused about recent topics."],
        'Week 7': ["Starting to understand now.", "The review session helped!", "Feeling more confident."],
        'Week 9': ["Really enjoying the advanced topics!", "Everything is clicking now.", "Best course so far!"]
    }
    
    print("\n📅 Emotion Trends Across Semester:")
    print("-"*80)
    
    for week, feedbacks in weekly_feedbacks.items():
        # Analyze all feedbacks for the week
        week_emotions = {'happiness': [], 'frustration': [], 'confusion': [], 'satisfaction': []}
        
        for feedback in feedbacks:
            emotions = nlp_service.detect_emotions(feedback)
            for emotion in week_emotions.keys():
                week_emotions[emotion].append(emotions[emotion])
        
        # Average emotions for the week
        avg_emotions = {e: sum(scores)/len(scores) for e, scores in week_emotions.items()}
        
        # Determine overall mood
        dominant_emotion = max(avg_emotions.items(), key=lambda x: x[1])
        
        print(f"\n  {week}:")
        print(f"    Dominant Emotion: {dominant_emotion[0].capitalize()} ({dominant_emotion[1]:.2f})")
        
        # Show emotion bars
        for emotion, score in sorted(avg_emotions.items(), key=lambda x: -x[1]):
            if score > 0.05:
                bar = "█" * int(score * 20)
                print(f"      {emotion.capitalize():12s} {bar} {score:.3f}")
    
    print("\n  📊 Trend Analysis:")
    print("     Week 1-3: High engagement, students excited and curious")
    print("     Week 5:   Peak confusion and frustration (midterm difficulty)")
    print("     Week 7-9: Recovery and increased satisfaction (concepts clicking)")
    
    print("\n" + "="*80)

def main():
    """Run all demos"""
    print("\n" + "="*80)
    print("SMART LMS - NLP SERVICE DEMONSTRATION")
    print("Advanced Feedback Analysis in Action")
    print("="*80)
    
    try:
        demo_single_feedback_analysis()
        demo_batch_analysis()
        demo_teacher_dashboard()
        demo_emotion_tracking()
        
        print("\n" + "="*80)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY")
        print("="*80)
        print("\nThe NLP service provides:")
        print("  • Real-time sentiment analysis")
        print("  • Emotion detection and tracking")
        print("  • Theme and keyword extraction")
        print("  • Aspect-based sentiment")
        print("  • Actionable insights for teachers")
        print("  • Quality scoring and recommendations")
        print("\nReady for production use! 🚀")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
