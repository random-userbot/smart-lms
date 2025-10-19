"""
Train Engagement Classification Model
Uses student engagement data to classify engagement levels
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import joblib
import matplotlib.pyplot as plt
import seaborn as sns


def load_engagement_data():
    """Load engagement data from storage"""
    # Try to load from data_archive
    data_files = [
        'data_archive/balanced_engagement_data.csv',
        'data_archive/student_wise_summary.csv',
        'data_archive/labelled_data.csv'
    ]
    
    for file_path in data_files:
        if os.path.exists(file_path):
            print(f"✅ Loading data from: {file_path}")
            return pd.read_csv(file_path)
    
    print("⚠️ No training data found. Generating sample data...")
    return generate_sample_data()


def generate_sample_data(n_samples=1000):
    """Generate sample engagement data for training"""
    np.random.seed(42)
    
    labels = ["Engaged", "Confused", "Distracted", "Bored", "Not Engaged"]
    samples_per_class = n_samples // len(labels)
    
    data = []
    
    for label in labels:
        for i in range(samples_per_class):
            if label == "Engaged":
                watch_time = np.random.uniform(35, 60)
                pause_count = np.random.randint(0, 2)
                tab_switch_count = np.random.randint(0, 2)
                seek_count = np.random.randint(0, 2)
                quiz_score = np.random.randint(7, 10)
            elif label == "Confused":
                watch_time = np.random.uniform(20, 30)
                pause_count = np.random.randint(4, 8)
                tab_switch_count = np.random.randint(3, 6)
                seek_count = np.random.randint(3, 6)
                quiz_score = np.random.randint(3, 6)
            elif label == "Distracted":
                watch_time = np.random.uniform(10, 25)
                pause_count = np.random.randint(1, 4)
                tab_switch_count = np.random.randint(6, 10)
                seek_count = np.random.randint(4, 8)
                quiz_score = np.random.randint(4, 6)
            elif label == "Bored":
                watch_time = np.random.uniform(5, 20)
                pause_count = np.random.randint(0, 3)
                tab_switch_count = np.random.randint(4, 8)
                seek_count = np.random.randint(5, 10)
                quiz_score = np.random.randint(0, 4)
            else:  # Not Engaged
                watch_time = np.random.uniform(1, 10)
                pause_count = np.random.randint(0, 2)
                tab_switch_count = np.random.randint(6, 10)
                seek_count = np.random.randint(6, 12)
                quiz_score = np.random.randint(0, 3)
            
            data.append({
                "Total WatchTime": round(watch_time, 2),
                "PauseCount": pause_count,
                "TabSwitchCount": tab_switch_count,
                "SeekCount": seek_count,
                "Quiz Score": quiz_score,
                "EngagementLabel": label
            })
    
    return pd.DataFrame(data)


def train_models(df):
    """Train both RandomForest and XGBoost models"""
    
    # Prepare features and labels
    feature_columns = ['Total WatchTime', 'PauseCount', 'TabSwitchCount', 'SeekCount', 'Quiz Score']
    
    # Check which columns exist
    available_features = [col for col in feature_columns if col in df.columns]
    
    if not available_features:
        print("❌ No feature columns found in data!")
        return None, None, None
    
    print(f"📊 Using features: {available_features}")
    
    X = df[available_features]
    
    # Get label column
    label_col = None
    for col in ['EngagementLabel', 'Label', 'EngagementLevel']:
        if col in df.columns:
            label_col = col
            break
    
    if label_col is None:
        print("❌ No label column found!")
        return None, None, None
    
    y = df[label_col]
    
    # Encode labels
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    print(f"\n📊 Dataset Info:")
    print(f"   - Total samples: {len(df)}")
    print(f"   - Features: {len(available_features)}")
    print(f"   - Classes: {len(le.classes_)}")
    print(f"   - Class distribution:\n{y.value_counts()}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    print(f"\n📊 Train/Test Split:")
    print(f"   - Training samples: {len(X_train)}")
    print(f"   - Test samples: {len(X_test)}")
    
    # Train RandomForest
    print("\n🌲 Training RandomForest...")
    rf_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    rf_model.fit(X_train, y_train)
    
    # Evaluate RandomForest
    y_pred_rf = rf_model.predict(X_test)
    rf_accuracy = accuracy_score(y_test, y_pred_rf)
    
    print(f"\n✅ RandomForest Results:")
    print(f"   - Accuracy: {rf_accuracy:.4f}")
    print(f"\n   Classification Report:")
    print(classification_report(y_test, y_pred_rf, target_names=le.classes_))
    
    # Train XGBoost
    print("\n🚀 Training XGBoost...")
    xgb_model = XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        n_jobs=-1
    )
    xgb_model.fit(X_train, y_train)
    
    # Evaluate XGBoost
    y_pred_xgb = xgb_model.predict(X_test)
    xgb_accuracy = accuracy_score(y_test, y_pred_xgb)
    
    print(f"\n✅ XGBoost Results:")
    print(f"   - Accuracy: {xgb_accuracy:.4f}")
    print(f"\n   Classification Report:")
    print(classification_report(y_test, y_pred_xgb, target_names=le.classes_))
    
    # Feature importance
    print("\n📊 Feature Importance (RandomForest):")
    for feature, importance in zip(available_features, rf_model.feature_importances_):
        print(f"   - {feature}: {importance:.4f}")
    
    # Save models
    os.makedirs('ml/models', exist_ok=True)
    
    joblib.dump(rf_model, 'ml/models/random_forest_engagement_model.pkl')
    joblib.dump(xgb_model, 'ml/models/xgboost_engagement_model.pkl')
    joblib.dump(le, 'ml/models/label_encoder.pkl')
    
    print(f"\n💾 Models saved:")
    print(f"   - ml/models/random_forest_engagement_model.pkl")
    print(f"   - ml/models/xgboost_engagement_model.pkl")
    print(f"   - ml/models/label_encoder.pkl")
    
    # Plot confusion matrix
    plot_confusion_matrix(y_test, y_pred_xgb, le.classes_, "XGBoost")
    
    return rf_model, xgb_model, le


def plot_confusion_matrix(y_true, y_pred, classes, model_name):
    """Plot confusion matrix"""
    cm = confusion_matrix(y_true, y_pred)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=classes, yticklabels=classes)
    plt.title(f'Confusion Matrix - {model_name}')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    
    # Save plot
    plt.savefig(f'ml/models/confusion_matrix_{model_name.lower()}.png')
    print(f"   - Confusion matrix saved: ml/models/confusion_matrix_{model_name.lower()}.png")
    plt.close()


def main():
    """Main training function"""
    print("=" * 60)
    print("🤖 Smart LMS - Engagement Model Training")
    print("=" * 60)
    print()
    
    # Load data
    df = load_engagement_data()
    
    if df is None or df.empty:
        print("❌ No data available for training!")
        return
    
    print(f"✅ Loaded {len(df)} samples")
    print()
    
    # Train models
    rf_model, xgb_model, le = train_models(df)
    
    if rf_model is None:
        print("❌ Training failed!")
        return
    
    print()
    print("=" * 60)
    print("✅ Training Complete!")
    print("=" * 60)
    print()
    print("📋 Next steps:")
    print("   1. Models are saved in ml/models/")
    print("   2. Use them in the Smart LMS application")
    print("   3. Test predictions with new data")
    print()


if __name__ == "__main__":
    main()
