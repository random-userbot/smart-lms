"""
ML Model Training Script for Teaching Effectiveness Indicators
Trains Random Forest and XGBoost models on historical data
"""

import sys
import os
import json
from datetime import datetime
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.teaching_score_ml import MLTeachingScorePredictor, ML_AVAILABLE


def generate_synthetic_training_data(n_samples=100):
    """
    Generate synthetic training data for initial model training
    In production, this should use real historical data
    """
    print(f"📊 Generating {n_samples} synthetic training samples...")
    
    np.random.seed(42)
    data = []
    
    for i in range(n_samples):
        # Generate realistic component scores with correlations
        engagement = np.random.beta(5, 2) * 100  # Slightly positive skew
        quiz_perf = engagement * 0.7 + np.random.normal(0, 10)  # Correlated with engagement
        attendance = engagement * 0.6 + np.random.normal(0, 15)
        lecture_comp = engagement * 0.65 + np.random.normal(0, 12)
        sentiment = engagement * 0.5 + np.random.normal(0, 15)
        resource_usage = engagement * 0.4 + np.random.normal(0, 20)
        activity_patterns = engagement * 0.55 + np.random.normal(0, 15)
        
        # Contextual factors
        course_difficulty = np.random.uniform(20, 80)
        cohort_size = int(np.random.uniform(10, 50))
        participation_rate = np.clip(engagement * 0.8 + np.random.normal(0, 10), 0, 100)
        avg_session_time = np.random.uniform(900, 3600)
        student_retention = np.clip(engagement * 0.7 + np.random.normal(0, 15), 0, 100)
        
        # Clip all scores to 0-100
        engagement = np.clip(engagement, 0, 100)
        quiz_perf = np.clip(quiz_perf, 0, 100)
        attendance = np.clip(attendance, 0, 100)
        lecture_comp = np.clip(lecture_comp, 0, 100)
        sentiment = np.clip(sentiment, 0, 100)
        resource_usage = np.clip(resource_usage, 0, 100)
        activity_patterns = np.clip(activity_patterns, 0, 100)
        
        # Calculate overall score (weighted average with noise)
        weights = [0.25, 0.20, 0.15, 0.15, 0.10, 0.05, 0.10]
        overall_score = (
            engagement * weights[0] +
            quiz_perf * weights[1] +
            attendance * weights[2] +
            lecture_comp * weights[3] +
            sentiment * weights[4] +
            resource_usage * weights[5] +
            activity_patterns * weights[6]
        )
        
        # Adjust for contextual factors
        difficulty_factor = (50 - course_difficulty) / 100 * 5  # Harder courses get slight boost
        cohort_factor = min(cohort_size / 30, 1) * 2  # Larger cohorts more reliable
        overall_score += difficulty_factor + cohort_factor
        overall_score = np.clip(overall_score, 0, 100)
        
        record = {
            'teacher_id': f'teacher_{i % 10}',
            'course_id': f'course_{i % 20}',
            'timestamp': datetime.now().isoformat(),
            'overall_score': overall_score,
            'components': {
                'engagement': {'score': engagement},
                'quiz_performance': {'score': quiz_perf},
                'attendance': {'score': attendance},
                'lecture_completion': {'score': lecture_comp},
                'sentiment': {'score': sentiment},
                'resource_usage': {'score': resource_usage},
                'activity_patterns': {'score': activity_patterns}
            },
            'contextual_factors': {
                'course_difficulty': {'difficulty_score': course_difficulty},
                'cohort_behavior': {
                    'cohort_size': cohort_size,
                    'participation_rate': participation_rate
                },
                'avg_session_time': avg_session_time,
                'student_retention': student_retention
            }
        }
        
        data.append(record)
    
    print("✓ Synthetic data generated")
    return data


def train_models_from_storage(storage_path="./storage/teaching_scores.json"):
    """Train models using data from storage"""
    
    print("\n" + "="*60)
    print("🤖 ML MODEL TRAINING - Teaching Effectiveness Indicators")
    print("="*60 + "\n")
    
    if not ML_AVAILABLE:
        print("❌ ML libraries not installed!")
        print("📦 Install with: pip install scikit-learn xgboost")
        return False
    
    # Load historical data
    if os.path.exists(storage_path):
        with open(storage_path, 'r') as f:
            data = json.load(f)
            historical_scores = data.get('scores', [])
    else:
        historical_scores = []
    
    print(f"📚 Found {len(historical_scores)} historical records")
    
    # Check if enough data
    if len(historical_scores) < 10:
        print(f"⚠️  Insufficient historical data ({len(historical_scores)} records)")
        print(f"📊 Generating synthetic training data for demonstration...")
        
        synthetic_data = generate_synthetic_training_data(100)
        
        # Save synthetic data
        print(f"💾 Saving synthetic data to {storage_path}")
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)
        with open(storage_path, 'w') as f:
            json.dump({'scores': synthetic_data}, f, indent=2)
        
        historical_scores = synthetic_data
    
    # Initialize predictor
    print("\n🔧 Initializing ML Predictor...")
    predictor = MLTeachingScorePredictor()
    
    # Prepare training data
    print("📋 Preparing training data...")
    try:
        X, y = predictor.prepare_training_data(historical_scores)
        print(f"✓ Prepared {len(X)} training samples with {len(predictor.feature_names)} features")
    except ValueError as e:
        print(f"❌ Error preparing data: {str(e)}")
        return False
    
    # Train models
    print("\n🎓 Training machine learning models...\n")
    try:
        results = predictor.train_models(X, y)
        
        print("\n" + "="*60)
        print("📊 TRAINING RESULTS")
        print("="*60)
        
        print("\n🌲 Random Forest:")
        print(f"   Test R² Score:  {results['random_forest']['test_score']:.4f}")
        print(f"   CV Score:       {results['random_forest']['cv_score']:.4f} (+/- {results['random_forest']['cv_std']:.4f})")
        
        print("\n⚡ XGBoost:")
        print(f"   Test R² Score:  {results['xgboost']['test_score']:.4f}")
        print(f"   CV Score:       {results['xgboost']['cv_score']:.4f} (+/- {results['xgboost']['cv_std']:.4f})")
        
        print(f"\n🏆 Best Model: {results['best_model']}")
        print(f"   Best Score: {results['best_score']:.4f}")
        
        print("\n" + "="*60)
        print("✅ TRAINING COMPLETE")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Training failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_prediction():
    """Test the trained models with a sample prediction"""
    
    print("\n" + "="*60)
    print("🧪 TESTING PREDICTIONS")
    print("="*60 + "\n")
    
    predictor = MLTeachingScorePredictor()
    
    # Load models
    try:
        predictor._load_models()
    except:
        print("⚠️  No trained models found. Run training first.")
        return
    
    if predictor.best_model is None:
        print("❌ No model available for prediction")
        return
    
    # Sample features
    print("📝 Sample Teacher Profile:")
    print("   Engagement: 75/100")
    print("   Quiz Performance: 80/100")
    print("   Attendance: 85/100")
    print("   Lecture Completion: 70/100")
    print("   Sentiment: 65/100")
    print("   Resource Usage: 60/100")
    print("   Activity Patterns: 72/100")
    print("   Course Difficulty: 55/100")
    print("   Cohort Size: 25 students")
    print("   Participation Rate: 70%")
    
    features = [75, 80, 85, 70, 65, 60, 72, 55, 25, 70, 1800, 75]
    
    # Predict
    print("\n🔮 Generating prediction...")
    result = predictor.predict_with_confidence(features)
    
    print(f"\n✅ PREDICTION RESULTS:")
    print(f"   Predicted Score: {result['predicted_score']:.1f}/100")
    print(f"   Confidence Range: {result['confidence_interval']['lower']:.1f} - {result['confidence_interval']['upper']:.1f}")
    print(f"   Confidence Level: {result['confidence_level']}")
    print(f"   Model Used: {result['model_used']}")
    
    if result.get('feature_importance'):
        print(f"\n📊 Top Feature Importance:")
        sorted_features = sorted(
            result['feature_importance'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        for feature, importance in sorted_features:
            print(f"   {feature}: {importance:.2%}")
    
    print("\n" + "="*60 + "\n")


def main():
    """Main training script"""
    
    print("\n🚀 Starting ML Training Pipeline\n")
    
    # Train models
    success = train_models_from_storage()
    
    if success:
        # Test predictions
        test_prediction()
        
        print("✅ All done! Models are ready for use.")
        print("\n📝 Next steps:")
        print("   1. Models are saved in ./storage/ml_models/")
        print("   2. The system will automatically use the best model")
        print("   3. As you collect real data, retrain for better accuracy")
        print("\n💡 To retrain with new data, run this script again")
    else:
        print("\n❌ Training failed. Check errors above.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
