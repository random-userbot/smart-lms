import pandas as pd
import random

# Engagement categories
labels = ["Engaged", "Confused", "Distracted", "Bored", "Not Engaged"]
samples_per_class = 200  # 200 samples * 5 classes = 1000 rows

data = []

for label in labels:
    for i in range(samples_per_class):
        student_id = f"S{i+1}_{label[:2].upper()}"
        if label == "Engaged":
            watch_time = random.uniform(35, 60)
            pause_count = random.randint(0, 2)
            tab_switch_count = random.randint(0, 2)
            quiz_score = random.randint(7, 10)
        elif label == "Confused":
            watch_time = random.uniform(20, 30)
            pause_count = random.randint(4, 8)
            tab_switch_count = random.randint(3, 6)
            quiz_score = random.randint(3, 6)
        elif label == "Distracted":
            watch_time = random.uniform(10, 25)
            pause_count = random.randint(1, 4)
            tab_switch_count = random.randint(6, 10)
            quiz_score = random.randint(4, 6)
        elif label == "Bored":
            watch_time = random.uniform(5, 20)
            pause_count = random.randint(0, 3)
            tab_switch_count = random.randint(4, 8)
            quiz_score = random.randint(0, 4)
        else:  # Not Engaged
            watch_time = random.uniform(1, 10)
            pause_count = random.randint(0, 2)
            tab_switch_count = random.randint(6, 10)
            quiz_score = random.randint(0, 3)

        data.append({
            "StudentID": student_id,
            "PauseCount": pause_count,
            "TabSwitchCount": tab_switch_count,
            "Total WatchTime": round(watch_time, 2),
            "Quiz Score": quiz_score,
            "EngagementLabel": label
        })

df = pd.DataFrame(data)
df.to_csv("balanced_engagement_data.csv", index=False)
print("✅ Balanced dataset with 1000 samples saved to 'balanced_engagement_data.csv'")
