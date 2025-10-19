import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
import joblib

# Step 1: Load dataset
df = pd.read_csv("balanced_engagement_data.csv")  # make sure this path is correct
print(" Total samples:", len(df))
print(df.head())

# Step 2: Encode EngagementLabel
le = LabelEncoder()
df['EngagementEncoded'] = le.fit_transform(df['EngagementLabel'])

# Step 3: Define feature columns and target
feature_cols = ['PauseCount', 'TabSwitchCount', 'SeekCount', 'Total WatchTime', 'Quiz Score']
X = df[feature_cols]
y = df['EngagementEncoded']

# Step 4: Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.2, random_state=42)
print("\n Distribution of y_test labels:")
print(y_test.value_counts())

# Step 5: Train Random Forest
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)
y_pred_rf = rf_model.predict(X_test)

print("\n Random Forest Evaluation:")
print(" Accuracy:", accuracy_score(y_test, y_pred_rf))
print(" Classification Report:")
print(classification_report(y_test, y_pred_rf, target_names=le.classes_))

# Step 6: Confusion Matrix for Random Forest
cm_rf = confusion_matrix(y_test, y_pred_rf)
disp_rf = ConfusionMatrixDisplay(confusion_matrix=cm_rf, display_labels=le.classes_)
plt.figure(figsize=(8, 6))
disp_rf.plot(cmap=plt.cm.Blues, values_format='d')
plt.title(" Confusion Matrix - Random Forest")
plt.grid(False)
plt.tight_layout()
plt.show()

# Step 7: Train XGBoost
xgb_model = XGBClassifier(n_estimators=100, random_state=42)
xgb_model.fit(X_train, y_train)
y_pred_xgb = xgb_model.predict(X_test)

print("\n XGBoost Evaluation:")
print(" Accuracy:", accuracy_score(y_test, y_pred_xgb))
print(" Classification Report:")
print(classification_report(y_test, y_pred_xgb, target_names=le.classes_))

# Step 8: Confusion Matrix for XGBoost
cm_xgb = confusion_matrix(y_test, y_pred_xgb)
disp_xgb = ConfusionMatrixDisplay(confusion_matrix=cm_xgb, display_labels=le.classes_)
plt.figure(figsize=(8, 6))
disp_xgb.plot(cmap=plt.cm.Greens, values_format='d')
plt.title("📊 Confusion Matrix - XGBoost")
plt.grid(False)
plt.tight_layout()
plt.show()

# Step 9: Save both models
joblib.dump(rf_model, "random_forest_engagement_model.pkl")
joblib.dump(xgb_model, "xgboost_engagement_model.pkl")
print("\n✅ Models saved successfully.")

# For Random Forest
importances_rf = rf_model.feature_importances_
print("featuresRF:",importances_rf)

# For XGBoost
importances_xgb = xgb_model.feature_importances_
print("featuresXGB:",importances_xgb)
