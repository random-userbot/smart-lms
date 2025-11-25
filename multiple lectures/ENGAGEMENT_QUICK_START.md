# Smart LMS - Real-Time Engagement Tracking Quick Start

## 🚀 Quick Start Guide

### 1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 2. **Run the Application**
```bash
cd "c:\Users\revan\Downloads\multiple lectures\multiple lectures"
streamlit run app\streamlit_app.py
```

### 3. **Login as Student**
- Username: `demo_student`
- Password: `student123`

### 4. **Watch a Lecture with Tracking**

1. Navigate to **🎥 My Lectures**
2. Select a course
3. Click **▶️ Watch Now** on any lecture

---

## 📹 What Happens Automatically

### ✅ No Consent Dialog
- Webcam starts immediately (no interruption)

### ✅ PiP Webcam (Bottom-Right)
- Small 320x240 window appears
- Shows live webcam feed
- Displays real-time engagement score
- Overlays status (engaged, looking_away, etc.)

### ✅ Frame Capture (Every 1 Second)
- Image saved to `ml_data/captured_frames/`
- Metadata includes engagement score, status, lecture ID, etc.

### ✅ OpenFace Feature Extraction
- **17 Action Units** (AU01-AU45): Facial expressions
- **Gaze Vectors**: Eye movement tracking
- **Head Pose**: 6DOF rotation and translation
- **Engagement Score**: 0-100 calculated from features
- All saved to CSV: `ml_data/csv_logs/openface_features_*.csv`

### ✅ Behavioral Logging
- Every interaction tracked:
  - Tab switches
  - Video pause/play
  - Playback speed changes
  - Focus lost/gained
  - Resource downloads
  - Feedback submissions
- Saved to CSV: `ml_data/activity_logs/behavioral_log_*.csv`

### ✅ Anti-Cheating Monitoring
- **Tab Switch Detection**: Warning after 3 switches
- **Speed Enforcement**: Max 1.25x playback speed
- **Focus Monitoring**: Alerts on repeated focus losses
- **Violation Logging**: All violations saved to CSV
- **Popup Warnings**: Immediate feedback to student

---

## 🎯 Features at a Glance

| Feature | Status | Location |
|---------|--------|----------|
| YouTube Video Support | ✅ | `app/pages/lectures.py` |
| PiP Webcam | ✅ | Bottom-right corner |
| OpenFace Features (17 AUs) | ✅ | `ml_data/csv_logs/` |
| Gaze Tracking | ✅ | Part of OpenFace |
| Head Pose | ✅ | Part of OpenFace |
| Frame Capture (1/sec) | ✅ | `ml_data/captured_frames/` |
| Engagement Logging | ✅ | `ml_data/engagement_logs/` |
| Behavioral Logging | ✅ | `ml_data/activity_logs/` |
| Tab Switch Detection | ✅ | JavaScript + logging |
| Speed Enforcement (<1.25x) | ✅ | YouTube API + alerts |
| Violation Warnings | ✅ | Popup messages |
| Integrity Score | ✅ | Calculated per session |
| Session Summary | ✅ | JSON in session_logs |

---

## 📊 Real-Time Sidebar Displays

### Live Engagement (Right Sidebar)
```
📊 Live Engagement
━━━━━━━━━━━━━━━━━━━━
🟢 Engagement Score
87.5/100
Highly Engaged

📸 Frames: 145
⏱️ Duration: 12.3m

[Progress bar: ████████░░ 87%]

✅ Great focus!
```

### Integrity Monitor (Right Sidebar)
```
🛡️ Integrity Monitor
━━━━━━━━━━━━━━━━━━━━
🟢 Integrity Score
95/100
Excellent

✅ No violations

[Progress bar: █████████░ 95%]
```

---

## 🎥 YouTube Video Integration

### Add YouTube Link to Lecture

**As Admin/Teacher:**
1. Navigate to **Courses** page
2. Edit a course
3. Add/Edit lecture
4. Set `youtube_url` field to any of these formats:
   - `https://www.youtube.com/watch?v=VIDEO_ID`
   - `https://youtu.be/VIDEO_ID`
   - `VIDEO_ID` (11-character ID)

**Example:**
```
YouTube URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

### Playback Speed Monitoring
- JavaScript monitors speed changes every 1 second
- If speed > 1.25x:
  - Alert popup: "🚫 Playback Speed Too High!"
  - Speed auto-reset to 1.0x
  - Violation logged

---

## 🗂️ Data Files Generated

### Per Lecture Session:

1. **OpenFace Features CSV** (50+ columns)
   ```
   ml_data/csv_logs/openface_features_{session_id}.csv
   ```
   - timestamp, frame, session_id, lecture_id, course_id
   - face_detected, confidence, status, engagement_score
   - gaze_0_x, gaze_0_y, gaze_0_z, gaze_1_x, gaze_1_y, gaze_1_z
   - gaze_angle_x, gaze_angle_y
   - pose_Tx, pose_Ty, pose_Tz, pose_Rx, pose_Ry, pose_Rz
   - AU01_r through AU45_r (17 Action Units)
   - smile_intensity, confusion_level, drowsiness_level

2. **Engagement Log CSV**
   ```
   ml_data/engagement_logs/engagement_log_{session_id}.csv
   ```
   - timestamp, session_id, student_id, lecture_id
   - frame_path (link to captured image)
   - engagement_score, status, face_detected
   - gaze_angle_x, gaze_angle_y
   - head_pose_rx, head_pose_ry, head_pose_rz

3. **Behavioral Log CSV** (monthly)
   ```
   ml_data/activity_logs/behavioral_log_{student_id}_{YYYYMM}.csv
   ```
   - timestamp, session_id, student_id, lecture_id
   - event_type (login, tab_switch, speed_change, etc.)
   - event_data (JSON with details)

4. **Violations CSV** (monthly)
   ```
   ml_data/session_logs/violations_{student_id}_{YYYYMM}.csv
   ```
   - timestamp, student_id, lecture_id
   - violation_type (tab_switch, excessive_speed, etc.)
   - severity (low, medium, high)
   - details (JSON)

5. **Session Summary JSON**
   ```
   ml_data/session_logs/session_{session_id}.json
   ```
   - Complete session statistics
   - Total events, violations, integrity score
   - Engagement summary

6. **Captured Frame Images**
   ```
   ml_data/captured_frames/{session_id}_{timestamp}.jpg
   ```
   - One image per second
   - 60 images/minute × lecture duration

---

## 🔍 Checking Data Collection

### Quick Verification:

```bash
# Check OpenFace features
dir ml_data\csv_logs\openface_features_*.csv

# Check engagement logs
dir ml_data\engagement_logs\engagement_log_*.csv

# Check behavioral logs
dir ml_data\activity_logs\behavioral_log_*.csv

# Check captured frames
dir ml_data\captured_frames\*.jpg

# Check session summaries
dir ml_data\session_logs\session_*.json
```

### Example Session Data Size:

**60-minute lecture:**
- OpenFace CSV: ~3600 rows × 50 columns ≈ 2-3 MB
- Engagement CSV: ~3600 rows ≈ 500 KB
- Behavioral CSV: ~50 events ≈ 10 KB
- Captured Frames: ~3600 JPG images ≈ 200-400 MB
- Session JSON: ~50 KB

**Total per session: ~400-600 MB**

---

## ⚠️ Anti-Cheating Violations & Warnings

### Violation Types:

| Violation | Severity | Penalty | Warning Message |
|-----------|----------|---------|-----------------|
| Tab Switch | Medium | -2 points | ⚠️ Tab Switch Detected! Please stay focused. |
| Excessive Speed (>1.25x) | High | -5 points | 🚫 Playback Speed Too High! |
| Focus Lost | Low | -1.5 points | 👀 Focus Lost! Please return attention. |
| Low Engagement (<30) | Medium | -5 points | 😴 Low Engagement Detected! |

### Integrity Score:
```
Base: 100 points
Final Score: 100 - (violations × penalties)
Range: 0-100

90-100: 🟢 Excellent
75-89:  🟡 Good
60-74:  🟠 Fair
0-59:   🔴 Poor
```

---

## 🧪 Testing Scenarios

### Test 1: Normal Lecture Watching
1. Watch lecture for 2-3 minutes
2. Stay focused on screen
3. Check engagement score (should be 70-90)
4. Verify frame capture (should have ~120-180 images)

### Test 2: Tab Switch
1. Start watching lecture
2. Switch to another tab/window
3. **Expected:** Warning popup appears
4. Switch back
5. Check violations CSV (should show tab_switch entry)

### Test 3: Speed Violation
1. Watch YouTube lecture
2. Try changing speed to 1.5x or 2x
3. **Expected:** Alert + auto-reset to 1.0x
4. Check violations CSV (should show excessive_speed entry)

### Test 4: Low Engagement
1. Look away from screen for 30+ seconds
2. **Expected:** Engagement score drops
3. If score < 30, low_engagement violation logged

### Test 5: Data Verification
```bash
# After 5-minute test session:
- OpenFace CSV: ~300 rows
- Engagement CSV: ~300 rows
- Captured Frames: ~300 images
- Behavioral CSV: 10-20 events
- Session JSON: complete summary
```

---

## 📈 Using Data for Analytics

### LSTM Model Training:
```python
import pandas as pd

# Load OpenFace features
df = pd.read_csv('ml_data/csv_logs/openface_features_session123.csv')

# Time-series features
X = df[['engagement_score', 'gaze_angle_x', 'gaze_angle_y', 
        'pose_Rx', 'pose_Ry', 'AU05_r', 'AU12_r']].values

# Build LSTM model
# Predict dropout risk, engagement trends, etc.
```

### Explainable AI (SHAP):
```python
import shap

# Explain engagement score drivers
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X)

# Identify: Which AUs drive engagement?
```

### Teacher Analytics Dashboard:
```python
# Load all sessions for a lecture
sessions = load_all_sessions(lecture_id)

# Calculate metrics:
- Average class engagement
- Students at risk (low integrity score)
- Confusion hotspots (high confusion_level AU)
- Attention drops (time-series analysis)
```

---

## 🎓 Summary

### You Now Have:

✅ **Real-time engagement tracking** with accurate scoring (0-100)
✅ **Comprehensive OpenFace features** (17 AUs + gaze + pose)
✅ **Frame capture** every 1 second with metadata
✅ **Behavioral logging** for all user interactions
✅ **Anti-cheating monitoring** with popup warnings
✅ **YouTube video support** with speed enforcement
✅ **5 types of CSV logs** for future ML models
✅ **Integrity scoring** for teacher analytics
✅ **Session summaries** in JSON format

### All Data is Ready For:

- 📊 LSTM time-series modeling
- 🧠 Explainable AI (SHAP, LIME)
- 💬 NLP sentiment analysis
- 📈 Teacher dashboards
- 🚨 At-risk student detection
- 🎯 Personalized recommendations

---

## 🚀 Start Collecting Data Now!

```bash
streamlit run app\streamlit_app.py
```

Login → Watch Lectures → Data Automatically Collected! 🎉

---

**Everything is production-ready and fully integrated!**
