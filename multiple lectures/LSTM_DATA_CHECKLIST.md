# LSTM Training Data Checklist - Smart LMS to DAiSEE Integration

## 📋 Overview
This document outlines what data you have in Smart LMS, what features to check for DAiSEE LSTM training, and how to ensure compatibility between both datasets.

---

## 🗂️ Your Smart LMS Data Structure

### 1. **CSV Logs Location**
```
ml_data/
├── activity_logs/              # Behavioral events (clicks, navigation)
├── csv_logs/                   # OpenFace features (17 AUs + gaze + pose)
├── engagement_logs/            # Frame-level engagement scores
├── reading_logs/               # PDF reading time tracking
├── session_logs/               # Session start/end times
└── captured_frames/            # JPEG images with timestamps
```

### 2. **Available CSV Files** (Your Current Data)
- `activity_logs/behavioral_log_student_4_202510.csv` - 3.5 KB
- `csv_logs/openface_features_student_4_lec_2a96290c_3b05caef.csv` - 18 KB
- `engagement_logs/engagement_log_student_4_lec_2a96290c_3b05caef.csv` - 14.8 KB
- **Captured frames**: 67 JPEG images with timestamps (38-61 KB each)

---

## 📊 CSV File Formats & Features

### **File 1: OpenFace Features CSV** (`csv_logs/`)
**Location**: `ml_data/csv_logs/openface_features_student_4_lec_2a96290c_3b05caef.csv`

#### Columns (42 total):
```
timestamp, frame, session_id, lecture_id, course_id, face_detected, confidence, 
status, engagement_score, 

GAZE (6):
gaze_0_x, gaze_0_y, gaze_0_z, gaze_1_x, gaze_1_y, gaze_1_z, 
gaze_angle_x, gaze_angle_y,

HEAD POSE (6):
pose_Tx, pose_Ty, pose_Tz, pose_Rx, pose_Ry, pose_Rz,

ACTION UNITS (17):
AU01_r, AU02_r, AU04_r, AU05_r, AU06_r, AU07_r, AU09_r, AU10_r, AU12_r, 
AU14_r, AU15_r, AU17_r, AU20_r, AU23_r, AU25_r, AU26_r, AU45_r,

DERIVED METRICS (3):
smile_intensity, confusion_level, drowsiness_level
```

#### **✅ CRITICAL FOR LSTM: Use these 22 features**
```python
LSTM_FEATURES = [
    # 17 Action Units
    'AU01_r', 'AU02_r', 'AU04_r', 'AU05_r', 'AU06_r', 'AU07_r', 
    'AU09_r', 'AU10_r', 'AU12_r', 'AU14_r', 'AU15_r', 'AU17_r', 
    'AU20_r', 'AU23_r', 'AU25_r', 'AU26_r', 'AU45_r',
    
    # 2 Gaze angles
    'gaze_angle_x', 'gaze_angle_y',
    
    # 3 Head pose rotations
    'pose_Rx', 'pose_Ry', 'pose_Rz'
]
```

#### Sample Data Row:
```csv
2025-10-24T09:38:13.710855,1,student_4_lec_2a96290c_3b05caef,lec_2a96290c,cv101,
1,0.95,partially_engaged,31.59,
-0.0056,0.0002,-0.0037,-0.0046,-0.0011,-0.0035,-125.6,7.02,
117.63,106.43,3109.8,-168.27,-16.31,-1.34,
3.83,3.15,1.17,1.38,3.54,3.62,2.36,3.73,1.97,1.38,3.03,4.67,1.64,1.88,3.12,3.34,5.0,
2.75,2.72,7.24
```

---

### **File 2: Engagement Log CSV** (`engagement_logs/`)
**Location**: `ml_data/engagement_logs/engagement_log_student_4_lec_2a96290c_3b05caef.csv`

#### Columns (14 total):
```
timestamp, session_id, student_id, lecture_id, course_id, frame_path,
engagement_score, status, face_detected,
gaze_angle_x, gaze_angle_y, 
head_pose_rx, head_pose_ry, head_pose_rz
```

#### Purpose:
- **Links frames to images**: `frame_path` column points to captured JPEG
- **Ground truth labels**: `status` = engaged, partially_engaged, disengaged, not_detected
- **Simplified features**: Only gaze + head pose (no AUs)

#### Sample Data Row:
```csv
2025-10-24T09:38:13.710855,student_4_lec_2a96290c_3b05caef,student_4,lec_2a96290c,cv101,
ml_data/captured_frames\student_4_lec_2a96290c_3b05caef_20251024_093813_723405.jpg,
31.59,partially_engaged,1,-125.6,7.02,-168.27,-16.31,-1.34
```

---

### **File 3: Behavioral Log CSV** (`activity_logs/`)
**Location**: `ml_data/activity_logs/behavioral_log_student_4_202510.csv`

#### Columns (7 total):
```
timestamp, session_id, student_id, lecture_id, course_id, 
event_type, event_data
```

#### Event Types:
- `session_start`, `session_end`
- `lecture_start`, `lecture_pause`, `lecture_resume`, `lecture_end`
- `quiz_start`, `quiz_submit`
- `assignment_start`, `assignment_submit`
- `material_download`, `material_upload`
- `mouse_click`, `mouse_move`, `keyboard_press`

#### Purpose:
- Context for engagement (e.g., student paused video → low engagement expected)
- Clickstream analysis
- Not directly used in LSTM (but useful for interpretability)

---

### **File 4: Captured Frames** (`captured_frames/`)
**Location**: `ml_data/captured_frames/`

#### Naming Convention:
```
{student_id}_lec_{lecture_id}_{session_id}_{timestamp}.jpg

Example:
student_4_lec_2a96290c_3b05caef_20251024_093813_723405.jpg
         └─ student_id
              └─ lecture_id
                    └─ session_id
                             └─ timestamp (YYYYMMDD_HHMMSS_microseconds)
```

#### Key Info:
- **67 frames** captured from one session (~1 minute of video)
- ~1 frame per second (not consistent FPS)
- Image size: 38-61 KB (JPEG compressed)
- **Use this timestamp to sync with CSV data**

---

## 🔍 What to Check for DAiSEE Dataset

### **1. OpenFace Feature Extraction on DAiSEE Videos**

When you run OpenFace on DAiSEE dataset, **ensure your output CSV has these exact 22 columns**:

```python
# Your DAiSEE OpenFace CSV should have:
required_columns = [
    'AU01_r', 'AU02_r', 'AU04_r', 'AU05_r', 'AU06_r', 'AU07_r',
    'AU09_r', 'AU10_r', 'AU12_r', 'AU14_r', 'AU15_r', 'AU17_r',
    'AU20_r', 'AU23_r', 'AU25_r', 'AU26_r', 'AU45_r',
    'gaze_angle_x', 'gaze_angle_y',
    'pose_Rx', 'pose_Ry', 'pose_Rz'
]
```

#### OpenFace Command for DAiSEE:
```bash
# Extract same features as Smart LMS
FeatureExtraction -f video.mp4 -aus -gaze -pose -of output.csv
```

#### OpenFace Output Columns to Use:
- **Action Units**: `AU01_r` to `AU45_r` (use intensity `_r`, not presence `_c`)
- **Gaze**: `gaze_angle_x`, `gaze_angle_y` (in radians)
- **Head Pose**: `pose_Rx`, `pose_Ry`, `pose_Rz` (pitch, yaw, roll in degrees)

---

### **2. Timestamp & Frame Alignment**

#### Smart LMS Timestamps:
```python
# Format: ISO 8601
"2025-10-24T09:38:13.710855"
```

#### DAiSEE Timestamps:
- DAiSEE videos are ~10 seconds each
- OpenFace outputs frame numbers (frame 1, 2, 3...)
- **Convert to seconds**: `time_sec = frame_number / fps`

#### Alignment Strategy:
```python
# For LSTM sequences (30 frames = 1 second)
# Smart LMS: Variable FPS (~1 fps)
# DAiSEE: 30 fps → Use 30 consecutive frames

# Ensure temporal consistency:
df = df.sort_values('frame')  # Sort by frame number
sequences = create_sequences(df, seq_length=30)  # 30 frames/seq
```

---

### **3. Feature Value Ranges**

#### Expected Ranges (from Smart LMS data):

| Feature Type | Column | Min | Max | Unit |
|-------------|--------|-----|-----|------|
| **Action Units** | AU01_r - AU45_r | 0.0 | 5.0 | Intensity (0-5) |
| **Gaze Angle X** | gaze_angle_x | -180 | +180 | Degrees |
| **Gaze Angle Y** | gaze_angle_y | -90 | +90 | Degrees |
| **Head Pose Rx** | pose_Rx | -180 | +180 | Pitch (degrees) |
| **Head Pose Ry** | pose_Ry | -180 | +180 | Yaw (degrees) |
| **Head Pose Rz** | pose_Rz | -180 | +180 | Roll (degrees) |

#### ⚠️ Check for Outliers:
```python
# In your DAiSEE feature extraction, verify:
assert (df[au_columns] >= 0).all().all(), "AUs should be >= 0"
assert (df[au_columns] <= 5).all().all(), "AUs should be <= 5"
assert (df['gaze_angle_x'].between(-180, 180)).all(), "Gaze X out of range"
assert (df['gaze_angle_y'].between(-90, 90)).all(), "Gaze Y out of range"
```

---

## 🧪 LSTM Data Preparation Checklist

### **Step 1: Feature Extraction** ✅
- [ ] Run OpenFace on all DAiSEE videos
- [ ] Extract 17 AUs (intensity: `_r` suffix)
- [ ] Extract gaze angles (gaze_angle_x, gaze_angle_y)
- [ ] Extract head pose (pose_Rx, pose_Ry, pose_Rz)
- [ ] Save as CSV with frame numbers

### **Step 2: Data Validation** ✅
- [ ] Check for missing values (face not detected)
- [ ] Verify AU ranges: 0-5
- [ ] Verify gaze ranges: -180 to +180 (x), -90 to +90 (y)
- [ ] Verify pose ranges: -180 to +180 degrees
- [ ] Count total frames per video (~300 frames for 10-sec @ 30fps)

### **Step 3: Sequence Creation** ✅
- [ ] Create sliding windows: 30 frames per sequence
- [ ] Stride: 15 frames (50% overlap) for data augmentation
- [ ] Handle short videos (<30 frames): pad or skip
- [ ] Shape: (num_sequences, 30, 22)

### **Step 4: Normalization** ✅
- [ ] Use StandardScaler on all 22 features
- [ ] Fit scaler on training set ONLY
- [ ] Transform train, validation, test separately
- [ ] Save scaler as `lstm_scaler.pkl`

### **Step 5: Label Mapping** ✅
- [ ] DAiSEE labels: Boredom, Engagement, Confusion, Frustration (4 classes)
- [ ] Convert to integers: 0, 1, 2, 3
- [ ] One-hot encode for categorical_crossentropy loss
- [ ] Verify class distribution (check for imbalance)

### **Step 6: Train/Val/Test Split** ✅
- [ ] 70% train, 15% validation, 15% test
- [ ] Stratify by class to maintain distribution
- [ ] Ensure no video appears in multiple splits
- [ ] Save split indices for reproducibility

---

## 🔗 Integration with Smart LMS Data

### **Use Case 1: Fine-Tuning Trained Model**
After training on DAiSEE, you can fine-tune using Smart LMS data:

```python
# Load DAiSEE-trained model
model = keras.models.load_model('daisee_lstm_model.h5')

# Load Smart LMS data
df_smart_lms = pd.read_csv('ml_data/csv_logs/openface_features_*.csv')

# Extract same 22 features
X_smart_lms = df_smart_lms[LSTM_FEATURES].values

# Create sequences
X_sequences = create_sequences(X_smart_lms, seq_length=30)

# Fine-tune (freeze early layers, unfreeze last LSTM layer)
model.layers[0].trainable = False  # Freeze first LSTM
model.layers[1].trainable = True   # Unfreeze second LSTM

# Train with lower learning rate
model.compile(optimizer=Adam(lr=0.0001), loss='categorical_crossentropy')
model.fit(X_sequences, y_smart_lms, epochs=5)
```

### **Use Case 2: Validation with Real Students**
```python
# Use Smart LMS engagement_logs as ground truth
df_engagement = pd.read_csv('ml_data/engagement_logs/engagement_log_*.csv')

# Map status to DAiSEE classes:
status_mapping = {
    'disengaged': 0,      # Boredom
    'partially_engaged': 2,  # Confusion
    'engaged': 1,         # Engagement
}

# Compare LSTM predictions with engagement_score
predictions = model.predict(X_smart_lms_sequences)
ground_truth = df_engagement['status'].map(status_mapping)

accuracy = (predictions.argmax(axis=1) == ground_truth).mean()
print(f"Real-world validation accuracy: {accuracy:.2%}")
```

---

## 📸 Frame Image Usage

### **Current Captured Frames** (67 images)
- **Purpose**: Visual reference for debugging
- **Not used in LSTM training** (we use extracted features, not raw images)
- **Useful for**:
  - Verifying OpenFace detection quality
  - Visualizing engagement states
  - Error analysis (why did model misclassify?)

### **DAiSEE Video Frames**
- **Extract frames**: Use OpenCV to save frames as JPEG
- **Only if needed**: For CNN-LSTM hybrid models (visual + AU features)
- **For pure LSTM**: Frames not required, use OpenFace CSV only

---

## 🚀 LSTM Training Workflow

### **Your Next Steps:**

#### 1. **Setup DAiSEE Training Workspace**
```powershell
# Create new folder
mkdir daisee-lstm-training
cd daisee-lstm-training

# Subfolder structure
mkdir data\raw data\processed data\features
mkdir models\trained scripts notebooks
```

#### 2. **Run OpenFace Feature Extraction**
```python
# scripts/01_extract_openface_features.py
import subprocess
import os

daisee_videos = 'data/raw/DAiSEE/Videos/'
output_dir = 'data/processed/openface_output/'

for video in os.listdir(daisee_videos):
    video_path = os.path.join(daisee_videos, video)
    output_csv = os.path.join(output_dir, video.replace('.avi', '.csv'))
    
    cmd = [
        'FeatureExtraction',
        '-f', video_path,
        '-aus',      # Extract Action Units
        '-gaze',     # Extract gaze
        '-pose',     # Extract head pose
        '-of', output_csv
    ]
    
    subprocess.run(cmd, check=True)
    print(f"✅ Processed: {video}")
```

#### 3. **Prepare LSTM Data**
```python
# scripts/02_prepare_lstm_data.py
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import pickle

# Load all OpenFace CSVs
all_features = []
for csv_file in os.listdir('data/processed/openface_output/'):
    df = pd.read_csv(csv_file)
    
    # Extract 22 features
    features = df[LSTM_FEATURES].values
    label = get_label_from_filename(csv_file)  # From DAiSEE annotations
    
    # Create sequences (30 frames)
    sequences = create_sequences(features, seq_length=30, stride=15)
    labels = [label] * len(sequences)
    
    all_features.extend(sequences)
    all_labels.extend(labels)

# Convert to numpy arrays
X = np.array(all_features)  # Shape: (num_sequences, 30, 22)
y = np.array(all_labels)    # Shape: (num_sequences,)

# Normalize
scaler = StandardScaler()
X_reshaped = X.reshape(-1, 22)  # Flatten for scaling
X_scaled = scaler.fit_transform(X_reshaped)
X_scaled = X_scaled.reshape(-1, 30, 22)  # Reshape back

# Save
np.save('data/features/X_train.npy', X_scaled)
np.save('data/features/y_train.npy', y)
pickle.dump(scaler, open('models/trained/lstm_scaler.pkl', 'wb'))
```

#### 4. **Train LSTM Model**
```python
# scripts/03_train_lstm.py
from tensorflow import keras
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

# Load data
X_train = np.load('data/features/X_train.npy')
y_train = np.load('data/features/y_train.npy')

# One-hot encode labels
y_train_encoded = keras.utils.to_categorical(y_train, num_classes=4)

# Build LSTM model
model = keras.Sequential([
    LSTM(128, return_sequences=True, input_shape=(30, 22)),
    Dropout(0.3),
    LSTM(64),
    Dropout(0.3),
    Dense(32, activation='relu'),
    Dense(4, activation='softmax')  # 4 classes
])

model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# Train
callbacks = [
    EarlyStopping(patience=10, restore_best_weights=True),
    ModelCheckpoint('models/trained/engagement_lstm.h5', save_best_only=True)
]

history = model.fit(
    X_train, y_train_encoded,
    validation_split=0.2,
    epochs=100,
    batch_size=32,
    callbacks=callbacks
)

print("✅ Training complete!")
```

#### 5. **Copy Trained Model to Smart LMS**
```powershell
# After training completes
Copy-Item "daisee-lstm-training\models\trained\engagement_lstm.h5" `
          "smart-lms\ml\models\"

Copy-Item "daisee-lstm-training\models\trained\lstm_scaler.pkl" `
          "smart-lms\ml\models\"
```

#### 6. **Integrate into Smart LMS**
Add to `services/engagement.py`:
```python
def load_lstm_model(self):
    """Load trained LSTM model"""
    import pickle
    self.lstm_model = keras.models.load_model('ml/models/engagement_lstm.h5')
    with open('ml/models/lstm_scaler.pkl', 'rb') as f:
        self.lstm_scaler = pickle.load(f)
    self.feature_buffer = []  # Store 30 frames

def predict_engagement_lstm(self, frame_features):
    """Predict engagement using LSTM"""
    # Add current frame to buffer
    self.feature_buffer.append(frame_features)
    
    # Keep only last 30 frames
    if len(self.feature_buffer) > 30:
        self.feature_buffer.pop(0)
    
    # Need 30 frames for prediction
    if len(self.feature_buffer) < 30:
        return None
    
    # Prepare input
    X = np.array(self.feature_buffer).reshape(1, 30, 22)
    X_scaled = self.lstm_scaler.transform(X.reshape(-1, 22)).reshape(1, 30, 22)
    
    # Predict
    predictions = self.lstm_model.predict(X_scaled, verbose=0)[0]
    
    return {
        'boredom': float(predictions[0]),
        'engagement': float(predictions[1]),
        'confusion': float(predictions[2]),
        'frustration': float(predictions[3])
    }
```

---

## ✅ Final Checklist

### **Before Training:**
- [ ] Downloaded DAiSEE dataset (Videos + Labels)
- [ ] Installed OpenFace 2.2.0
- [ ] Verified OpenFace extracts 17 AUs + gaze + pose
- [ ] Created `daisee-lstm-training/` workspace

### **During Training:**
- [ ] Extracted features from all DAiSEE videos
- [ ] Created 30-frame sequences
- [ ] Normalized features with StandardScaler
- [ ] Trained LSTM model (>75% accuracy target)
- [ ] Saved model and scaler

### **After Training:**
- [ ] Copied `engagement_lstm.h5` to `smart-lms/ml/models/`
- [ ] Copied `lstm_scaler.pkl` to `smart-lms/ml/models/`
- [ ] Added `load_lstm_model()` to `services/engagement.py`
- [ ] Added `predict_engagement_lstm()` to `services/engagement.py`
- [ ] Tested with Smart LMS captured frames
- [ ] Validated accuracy on real student sessions

---

## 📚 References

### **Smart LMS Feature Extraction Code:**
- `services/engagement.py` - Current MediaPipe tracking
- `services/openface_tracker.py` - OpenFace integration (if exists)
- `ml_data/csv_logs/` - Your current OpenFace outputs

### **DAiSEE Dataset:**
- Paper: "DAiSEE: Towards User Engagement Recognition in the Wild"
- Labels: 4 classes (Boredom, Engagement, Confusion, Frustration)
- Videos: ~9000 clips, 10 seconds each, 30 fps

### **OpenFace Documentation:**
- GitHub: https://github.com/TadasBaltrusaitis/OpenFace
- AU list: https://github.com/TadasBaltrusaitis/OpenFace/wiki/Action-Units

---

## 🎯 Key Takeaways

1. **Use OpenFace CSV from Smart LMS as your reference format**
   - 17 AUs + 2 gaze angles + 3 head pose = 22 features

2. **Your Smart LMS data has 67 frames with complete feature extraction**
   - Use this to validate your DAiSEE feature extraction matches

3. **Timestamps are critical for synchronization**
   - Smart LMS: ISO 8601 format
   - DAiSEE: Frame numbers (convert to seconds)

4. **Captured frames are for debugging, not training**
   - LSTM uses numerical features, not images

5. **After training on DAiSEE, you can fine-tune with Smart LMS data**
   - Use engagement_logs as ground truth labels

---

**Next Action**: Open DAiSEE workspace and give Copilot the prompt to generate the 4 training scripts! 🚀
