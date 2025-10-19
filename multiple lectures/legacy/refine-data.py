import pandas as pd

# Step 1: Load the CSV without header
df = pd.read_csv("realtime-data.csv", header=None, on_bad_lines='skip', encoding='cp1252')

# Step 2: Rename all 6 columns correctly
df.columns = ['StudentID', 'EventType', 'Timestamp', 'AdditionalInfo', 'AssignmentStatus', 'QuizTime']

# Step 3: Convert Timestamp column to datetime format
df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')

# Step 4: Extract 'Subject' and 'Lecture' from AdditionalInfo
df['Subject'] = df['AdditionalInfo'].str.extract(r"Subject: ([^,]+)")
df['Lecture'] = df['AdditionalInfo'].str.extract(r"Lecture: ([^,]+)")

# Step 5: Drop rows where timestamp is invalid
df = df.dropna(subset=['Timestamp'])

# Optional: Clean up empty strings and NaNs in AssignmentStatus/QuizTime
df['AssignmentStatus'] = df['AssignmentStatus'].fillna('Not Attempted')
df['QuizTime'] = pd.to_numeric(df['QuizTime'], errors='coerce').fillna(0)

# Step 6: Save the refined dataset
df.to_csv("refined_realtime_data.csv", index=False)

# Step 7: Print column names and a sample of the data
print("✅ Refined data saved to 'refined_realtime_data.csv'")
print("Columns:", df.columns.tolist())
print(df.head())
