import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib

# Load your refined data
df = pd.read_csv("student_wise_summary.csv")

# Step 1: Rule-based labeling for EngagementLevel
def assign_engagement(row):
    if row['TotalTimeMinutes'] >= 40 and row['TabSwitchCount'] <= 1 and row['PauseCount'] <= 2 and row['SeekCount'] <= 1:
        return 'Engaged'
    elif row['PauseCount'] > 3 and row['SeekCount'] > 2:
        return 'Confused'
    elif row['TabSwitchCount'] > 3 and row['TotalTimeMinutes'] < 25:
        return 'Distracted'
    elif row['PauseCount'] >= 3 and row['TotalTimeMinutes'] < 20:
        return 'Bored'
    else:
        return 'Not Engaged'

df['EngagementLevel'] = df.apply(assign_engagement, axis=1)

# Step 2: Encode the labels
le = LabelEncoder()
df['Label'] = le.fit_transform(df['EngagementLevel'])

# Step 3: Feature selection
features = ['PauseCount', 'TabSwitchCount', 'PlayCount', 'SeekCount', 'Total WatchTime']
X = df[features]
y = df['Label']

# Step 4: Split the dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 5: Train the Random Forest model
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Step 6: Evaluate the model
y_pred = clf.predict(X_test)
print("\n✅ Classification Report:\n")
print(classification_report(y_test, y_pred, target_names=le.classes_))
print("Accuracy:", accuracy_score(y_test, y_pred))

# Step 7: Save the model and label encoder
joblib.dump(clf, "engagement_model.pkl")
joblib.dump(le, "label_encoder.pkl")
print("✅ Model saved as 'engagement_model.pkl'")
