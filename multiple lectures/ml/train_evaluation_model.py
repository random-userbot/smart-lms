"""
Train Teacher Evaluation Model
Uses engagement, feedback, and performance data to evaluate teachers
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import matplotlib.pyplot as plt
import seaborn as sns


def generate_sample_teacher_data(n_teachers=50):
    """Generate sample teacher evaluation data"""
    np.random.seed(42)
    
    data = []
    
    for i in range(n_teachers):
        # Generate correlated features
        base_quality = np.random.uniform(0.3, 1.0)
        
        # Features
        avg_engagement = base_quality * 100 + np.random.normal(0, 10)
        avg_engagement = np.clip(avg_engagement, 0, 100)
        
        avg_feedback_sentiment = base_quality + np.random.normal(0, 0.1)
        avg_feedback_sentiment = np.clip(avg_feedback_sentiment, 0, 1)
        
        avg_quiz_score = base_quality + np.random.normal(0, 0.1)
        avg_quiz_score = np.clip(avg_quiz_score, 0, 1)
        
        avg_assignment_score = base_quality + np.random.normal(0, 0.1)
        avg_assignment_score = np.clip(avg_assignment_score, 0, 1)
        
        feedback_count = base_quality * 2 + np.random.normal(0, 0.2)
        feedback_count = np.clip(feedback_count, 0, 3)
        
        upload_frequency = base_quality * 0.5 + np.random.normal(0, 0.1)
        upload_frequency = np.clip(upload_frequency, 0, 1)
        
        material_update_count = base_quality * 0.3 + np.random.normal(0, 0.05)
        material_update_count = np.clip(material_update_count, 0, 0.5)
        
        login_frequency = base_quality * 0.8 + np.random.normal(0, 0.1)
        login_frequency = np.clip(login_frequency, 0, 1)
        
        response_time = (1 - base_quality) * 0.5 + np.random.normal(0, 0.05)
        response_time = np.clip(response_time, 0, 1)
        
        attendance_rate = base_quality + np.random.normal(0, 0.05)
        attendance_rate = np.clip(attendance_rate, 0, 1)
        
        # Target score (0-100)
        score = (
            0.25 * avg_engagement +
            0.20 * avg_feedback_sentiment * 100 +
            0.15 * avg_quiz_score * 100 +
            0.15 * avg_assignment_score * 100 +
            0.10 * upload_frequency * 100 +
            0.10 * attendance_rate * 100 +
            0.05 * feedback_count * 33.33
        )
        score = np.clip(score, 0, 100)
        
        data.append({
            'teacher_id': f'teacher_{i+1}',
            'avg_engagement_score': avg_engagement,
            'avg_feedback_sentiment': avg_feedback_sentiment,
            'avg_quiz_score': avg_quiz_score,
            'avg_assignment_score': avg_assignment_score,
            'feedback_count': feedback_count,
            'upload_frequency': upload_frequency,
            'material_update_count': material_update_count,
            'login_frequency': login_frequency,
            'response_time': response_time,
            'attendance_rate': attendance_rate,
            'score': score
        })
    
    return pd.DataFrame(data)


def train_evaluation_models(df):
    """Train teacher evaluation models"""
    
    # Features
    feature_columns = [
        'avg_engagement_score',
        'avg_feedback_sentiment',
        'avg_quiz_score',
        'avg_assignment_score',
        'feedback_count',
        'upload_frequency',
        'material_update_count',
        'login_frequency',
        'response_time',
        'attendance_rate'
    ]
    
    X = df[feature_columns]
    y = df['score']
    
    print(f"\n📊 Dataset Info:")
    print(f"   - Total teachers: {len(df)}")
    print(f"   - Features: {len(feature_columns)}")
    print(f"   - Score range: {y.min():.2f} - {y.max():.2f}")
    print(f"   - Mean score: {y.mean():.2f}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"\n📊 Train/Test Split:")
    print(f"   - Training samples: {len(X_train)}")
    print(f"   - Test samples: {len(X_test)}")
    
    # Train RandomForest
    print("\n🌲 Training RandomForest Regressor...")
    rf_model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    rf_model.fit(X_train, y_train)
    
    # Evaluate RandomForest
    y_pred_rf = rf_model.predict(X_test)
    rf_mse = mean_squared_error(y_test, y_pred_rf)
    rf_mae = mean_absolute_error(y_test, y_pred_rf)
    rf_r2 = r2_score(y_test, y_pred_rf)
    
    print(f"\n✅ RandomForest Results:")
    print(f"   - MSE: {rf_mse:.4f}")
    print(f"   - MAE: {rf_mae:.4f}")
    print(f"   - R² Score: {rf_r2:.4f}")
    
    # Train XGBoost
    print("\n🚀 Training XGBoost Regressor...")
    xgb_model = XGBRegressor(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        n_jobs=-1
    )
    xgb_model.fit(X_train, y_train)
    
    # Evaluate XGBoost
    y_pred_xgb = xgb_model.predict(X_test)
    xgb_mse = mean_squared_error(y_test, y_pred_xgb)
    xgb_mae = mean_absolute_error(y_test, y_pred_xgb)
    xgb_r2 = r2_score(y_test, y_pred_xgb)
    
    print(f"\n✅ XGBoost Results:")
    print(f"   - MSE: {xgb_mse:.4f}")
    print(f"   - MAE: {xgb_mae:.4f}")
    print(f"   - R² Score: {xgb_r2:.4f}")
    
    # Feature importance
    print("\n📊 Feature Importance (XGBoost):")
    feature_importance = sorted(
        zip(feature_columns, xgb_model.feature_importances_),
        key=lambda x: x[1],
        reverse=True
    )
    for feature, importance in feature_importance:
        print(f"   - {feature}: {importance:.4f}")
    
    # Save models
    os.makedirs('ml/models', exist_ok=True)
    
    joblib.dump(rf_model, 'ml/models/evaluation_random_forest.pkl')
    joblib.dump(xgb_model, 'ml/models/evaluation_xgboost.pkl')
    
    # Save feature names
    joblib.dump(feature_columns, 'ml/models/evaluation_features.pkl')
    
    print(f"\n💾 Models saved:")
    print(f"   - ml/models/evaluation_random_forest.pkl")
    print(f"   - ml/models/evaluation_xgboost.pkl")
    print(f"   - ml/models/evaluation_features.pkl")
    
    # Plot predictions vs actual
    plot_predictions(y_test, y_pred_xgb, "XGBoost")
    plot_feature_importance(feature_columns, xgb_model.feature_importances_)
    
    return rf_model, xgb_model


def plot_predictions(y_true, y_pred, model_name):
    """Plot predictions vs actual values"""
    plt.figure(figsize=(10, 6))
    plt.scatter(y_true, y_pred, alpha=0.6)
    plt.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'r--', lw=2)
    plt.xlabel('Actual Score')
    plt.ylabel('Predicted Score')
    plt.title(f'Predictions vs Actual - {model_name}')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    plt.savefig(f'ml/models/predictions_{model_name.lower()}.png')
    print(f"   - Predictions plot saved: ml/models/predictions_{model_name.lower()}.png")
    plt.close()


def plot_feature_importance(features, importances):
    """Plot feature importance"""
    plt.figure(figsize=(10, 6))
    indices = np.argsort(importances)[::-1]
    
    plt.bar(range(len(importances)), importances[indices])
    plt.xticks(range(len(importances)), [features[i] for i in indices], rotation=45, ha='right')
    plt.xlabel('Features')
    plt.ylabel('Importance')
    plt.title('Feature Importance')
    plt.tight_layout()
    
    plt.savefig('ml/models/feature_importance.png')
    print(f"   - Feature importance plot saved: ml/models/feature_importance.png")
    plt.close()


def main():
    """Main training function"""
    print("=" * 60)
    print("🎓 Smart LMS - Teacher Evaluation Model Training")
    print("=" * 60)
    print()
    
    # Generate sample data
    print("📊 Generating sample teacher data...")
    df = generate_sample_teacher_data(n_teachers=100)
    
    print(f"✅ Generated {len(df)} teacher samples")
    print()
    
    # Train models
    rf_model, xgb_model = train_evaluation_models(df)
    
    print()
    print("=" * 60)
    print("✅ Training Complete!")
    print("=" * 60)
    print()
    print("📋 Next steps:")
    print("   1. Models are saved in ml/models/")
    print("   2. Use them in the evaluation service")
    print("   3. Test with real teacher data")
    print()
    print("💡 Tip: The evaluation service will automatically load these models")
    print()


if __name__ == "__main__":
    main()
