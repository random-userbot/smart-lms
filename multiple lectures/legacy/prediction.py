import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib

# Step 1: Load labelled dataset
df = pd.read_csv("labelled_data.csv")

# Step 2: Select features and label
features = ['Total WatchTime', 'PauseCount', 'TabSwitchCount', 'Quiz Score']
X = df[features]
y = df['EngagementLabel']

# Step 3: Encode class labels
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# Step 4: Split into train/test sets
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# Step 5: Train the model (Random Forest)
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Step 6: Predict on test set
y_pred = clf.predict(X_test)

# Step 7: Evaluation
print("✅ Model Evaluation on Test Data:\n")
print(classification_report(y_test, y_pred, target_names=le.classes_))
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))

# Step 8: Save the model and label encoder
joblib.dump(clf, "engagement_model.pkl")
joblib.dump(le, "label_encoder.pkl")

print("\n✅ Model and label encoder saved as 'engagement_model.pkl' and 'label_encoder.pkl'")
