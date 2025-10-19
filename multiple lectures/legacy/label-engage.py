import pandas as pd

# Load the refined dataset
df = pd.read_csv("student_wise_summary.csv")  # Change this if your file has a different name

# ---- Rule-Based Function to Classify Engagement ----
def classify_engagement(row):
    watch_time = row.get('Total WatchTime', 0)
    tab_switches = row.get('TabSwitchCount', 0)
    pauses = row.get('PauseCount', 0)
    quiz_score = row.get('Quiz Score', 0)
    seek_count = row.get('SeekCount', 0)

    if watch_time >= 25 or tab_switches <= 3 and pauses <= 1 and quiz_score >4:
        return "Engaged"
    elif watch_time >= 20 or tab_switches>=3 and pauses > 5 and quiz_score <= 5:
        return "Confused"
    elif tab_switches > 3 and seek_count>3 and quiz_score >=3:
        return "Distracted"
    elif tab_switches>3  or  seek_count >= 4:
        return "Bored"
    elif tab_switches > 5 :
        return "Not Engaged"

    else:
        return "Not Engaged"

# ---- Apply Rule-Based Labeling ----
df['EngagementLabel'] = df.apply(classify_engagement, axis=1)

# ---- Save Updated Table ----
df.to_csv("labelled_data.csv", index=False)

# ---- Print Preview ----
print("Engagement labels added and saved to 'labelled_data.csv'\n")
print(df[['StudentID', 'Total WatchTime', 'PauseCount', 'TabSwitchCount', 'Quiz Score', 'EngagementLabel']].head())

# ---- Print Distribution ----

print("\n📊 Engagement Label Counts:")
label_counts = df['EngagementLabel'].value_counts()
print(label_counts)


# ---- Convert Counts to Percentages ----
total_students = len(df)
label_percentages = (label_counts / total_students) * 100

print("\n📊 Engagement Label Percentages:")
print(label_percentages.round(2).astype(str) + " %")