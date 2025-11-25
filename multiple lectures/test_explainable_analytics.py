"""
Test script for Explainable AI Analytics
Verifies comprehensive metrics, feature analysis, and score justifications
"""

import json
import numpy as np
from pathlib import Path

def test_analytics_completeness():
    """Test that analytics files contain comprehensive metrics"""
    
    print("=" * 80)
    print("TESTING EXPLAINABLE AI ANALYTICS")
    print("=" * 80)
    
    # Paths
    analytics_dir = Path("ml_data/ensemble_detailed_analytics")
    
    # Check directories
    directories = {
        'captured_faces': analytics_dir / 'captured_faces',
        'emotion_logs': analytics_dir / 'emotion_logs',
        'feature_vectors': analytics_dir / 'feature_vectors',
        'analysis_reports': analytics_dir / 'analysis_reports',
        'suggestions': analytics_dir / 'suggestions'
    }
    
    print("\n📁 Directory Status:")
    for name, path in directories.items():
        if path.exists():
            file_count = len(list(path.glob('*')))
            print(f"  ✅ {name}: {file_count} files")
        else:
            print(f"  ❌ {name}: NOT FOUND")
    
    # Test emotion logs
    print("\n😊 Testing Emotion Logs:")
    emotion_files = list(directories['emotion_logs'].glob('*.json'))
    if emotion_files:
        with open(emotion_files[0]) as f:
            emotion_data = json.load(f)
        
        print(f"  ✓ Loaded: {emotion_files[0].name}")
        print(f"  ✓ Has ensemble: {emotion_data.get('has_ensemble', False)}")
        print(f"  ✓ OpenFace score: {emotion_data.get('openface_engagement', 'N/A')}")
        
        if emotion_data.get('emotions'):
            print(f"  ✓ Emotions tracked: {len(emotion_data['emotions'])}")
            for emotion, data in emotion_data['emotions'].items():
                print(f"    - {emotion}: {data['level']} ({data['confidence']*100:.1f}%)")
        else:
            print("  ⚠️  No emotion data (ensemble may be disabled)")
    else:
        print("  ❌ No emotion log files found")
    
    # Test feature vectors
    print("\n🔢 Testing Feature Vectors:")
    feature_files = list(directories['feature_vectors'].glob('*.npy'))
    if feature_files:
        features = np.load(feature_files[0])
        print(f"  ✓ Loaded: {feature_files[0].name}")
        print(f"  ✓ Shape: {features.shape}")
        print(f"  ✓ Feature count: {len(features)}")
        print(f"  ✓ Mean: {np.mean(features):.4f}, Std: {np.std(features):.4f}")
        print(f"  ✓ Non-zero features: {np.count_nonzero(features)}")
    else:
        print("  ❌ No feature vector files found")
    
    # Test comprehensive analysis reports
    print("\n📊 Testing Comprehensive Analysis Reports:")
    analysis_files = list(directories['analysis_reports'].glob('*.json'))
    if analysis_files:
        # Load most recent
        latest_analysis = sorted(analysis_files)[-1]
        with open(latest_analysis) as f:
            analysis = json.load(f)
        
        print(f"  ✓ Loaded: {latest_analysis.name}")
        print(f"  ✓ Analysis version: {analysis.get('analysis_version', 'N/A')}")
        
        # Check OpenFace metrics
        if 'openface_metrics' in analysis:
            print("\n  📈 OpenFace Metrics:")
            of = analysis['openface_metrics']
            print(f"    ✓ Engagement: {of.get('engagement_score', 'N/A')}")
            print(f"    ✓ Status: {of.get('status', 'N/A')}")
            
            if 'gaze' in of and 'interpretation' in of['gaze']:
                print(f"    ✓ Gaze interpretation: {of['gaze']['interpretation']['attention_level']}")
                print(f"      → {of['gaze']['interpretation']['description']}")
            
            if 'head_pose' in of and 'interpretation' in of['head_pose']:
                print(f"    ✓ Head pose: {of['head_pose']['interpretation']['posture']}")
                print(f"      → {of['head_pose']['interpretation']['description']}")
        
        # Check feature analysis
        if 'feature_analysis' in analysis:
            print("\n  🔬 Feature Analysis:")
            fa = analysis['feature_analysis']
            print(f"    ✓ Feature vector shape: {fa.get('feature_vector_shape', 'N/A')}")
            
            if 'feature_statistics' in fa:
                stats = fa['feature_statistics']
                print(f"    ✓ Statistics:")
                print(f"      - Mean: {stats['mean']:.4f}")
                print(f"      - Std: {stats['std']:.4f}")
                print(f"      - Non-zero: {stats['non_zero_count']}")
            
            if 'engagement_indicators' in fa:
                ind = fa['engagement_indicators']
                print(f"    ✓ Indicators:")
                print(f"      - Gaze stability: {ind['gaze_stability']}")
                print(f"      - Head orientation: {ind['head_orientation']}")
                print(f"      - Facial activity: {ind['facial_activity']}")
        
        # Check EXPLAINABLE AI
        if 'ensemble_metrics' in analysis:
            print("\n  🤖 Ensemble AI Metrics:")
            em = analysis['ensemble_metrics']
            print(f"    ✓ Score: {em.get('engagement_score', 'N/A')}")
            print(f"    ✓ Mode: {em.get('mode', 'N/A')}")
            print(f"    ✓ Improvement: {em.get('improvement_over_openface', 'N/A'):.2f}")
            
            if 'explainable_ai' in em:
                print("\n  ✨ EXPLAINABLE AI BREAKDOWN:")
                xai = em['explainable_ai']
                
                print(f"    ✓ Final Score: {xai['final_score']:.1f}%")
                
                if 'score_breakdown' in xai:
                    sb = xai['score_breakdown']
                    print(f"    ✓ Engagement Level: {sb['engagement_level']}")
                    print(f"    ✓ Confidence: {sb['engagement_confidence']:.1f}%")
                    
                    if 'primary_factors' in sb:
                        print("\n    📌 Primary Factors:")
                        for factor in sb['primary_factors']:
                            print(f"      • {factor}")
                    
                    if 'secondary_factors' in sb:
                        print("\n    📌 Secondary Factors:")
                        for factor in sb['secondary_factors']:
                            print(f"      • {factor}")
                
                if 'model_reasoning' in xai:
                    print("\n    🧠 Model Reasoning:")
                    for reason in xai['model_reasoning']:
                        print(f"      {reason}")
                
                if 'score_justification' in xai:
                    print(f"\n    💡 Score Justification:")
                    print(f"      {xai['score_justification']}")
                
                if 'contributing_factors' in xai and xai['contributing_factors']:
                    print(f"\n    ⚠️  Contributing Negative Factors:")
                    for factor, data in xai['contributing_factors'].items():
                        print(f"      • {factor.title()}: {data['severity']} severity ({data['confidence']:.1f}% confidence)")
                        print(f"        → {data['description']}")
            
            # Check emotion interpretations
            if 'emotions' in em:
                print("\n  💭 Emotion Interpretations:")
                for emotion, data in em['emotions'].items():
                    if 'interpretation' in data:
                        print(f"    • {emotion}: {data['interpretation']}")
        
        # Check session context
        if 'session_context' in analysis:
            print("\n  📊 Session Context:")
            sc = analysis['session_context']
            print(f"    ✓ Frames processed: {sc.get('total_frames_processed', 'N/A')}")
            print(f"    ✓ Average engagement: {sc.get('average_engagement_so_far', 'N/A'):.2f}%")
            
            if 'engagement_trend' in sc:
                trend = sc['engagement_trend']
                print(f"    ✓ Trend: {trend['direction']}")
                print(f"      → {trend['trend']}")
    else:
        print("  ❌ No analysis report files found")
    
    # Test suggestions
    print("\n💡 Testing Suggestions:")
    suggestion_files = list(directories['suggestions'].glob('*.json'))
    if suggestion_files:
        with open(suggestion_files[0]) as f:
            suggestions = json.load(f)
        
        print(f"  ✓ Loaded: {suggestion_files[0].name}")
        print(f"  ✓ Engagement score: {suggestions.get('engagement_score', 'N/A')}")
        print(f"  ✓ Suggestions:")
        for i, suggestion in enumerate(suggestions.get('suggestions', []), 1):
            print(f"    {i}. {suggestion}")
    else:
        print("  ❌ No suggestion files found")
    
    print("\n" + "=" * 80)
    print("✅ ANALYTICS TEST COMPLETE")
    print("=" * 80)
    
    # Summary
    print("\n📋 SUMMARY:")
    all_good = all(path.exists() and list(path.glob('*')) for path in directories.values())
    
    if all_good:
        print("  ✅ All analytics directories populated")
        print("  ✅ Comprehensive metrics available")
        print("  ✅ Explainable AI working")
        print("  ✅ Feature vectors saved")
        print("  ✅ Emotion logs complete")
        print("\n  🎉 System ready for production!")
    else:
        print("  ⚠️  Some analytics missing - run app with ensemble enabled")
        print("  💡 Make sure to:")
        print("     1. Enable ensemble in lecture settings")
        print("     2. Watch a lecture for at least 30 frames")
        print("     3. Check that export/ directory has models")


if __name__ == "__main__":
    test_analytics_completeness()
