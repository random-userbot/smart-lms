# 🚀 Developer Quick Reference Card

## Import Statements

```python
# Core Services
from services.openface_processor import OpenFaceProcessor
from services.pip_webcam_live import render_pip_webcam
from services.behavioral_logger import BehavioralLogger
from services.anti_cheating import AntiCheatingMonitor

# New Services
from services.session_tracker import GlobalSessionTracker
from services.material_reader import MaterialReader, render_material_viewer
from services.quiz_monitor import QuizMonitor, render_quiz_with_monitoring
from services.engagement_calibrator import EngagementCalibrator
from services.multimodal_engagement import MultimodalEngagementScorer
```

---

## Initialization (on Login)

```python
# In app/streamlit_app.py after successful login:

# Global session tracker
st.session_state.global_tracker = GlobalSessionTracker(
    student_id=st.session_state.user_id,
    student_name=st.session_state.username
)
st.session_state.global_tracker.start_session()

# Calibration
st.session_state.calibrator = EngagementCalibrator()

# Multimodal scorer
st.session_state.multimodal_scorer = MultimodalEngagementScorer()
```

---

## Calibration Check

```python
# In app/pages/lectures.py at the top:

if st.session_state.calibrator.needs_calibration(st.session_state.user_id):
    st.warning("⚠️ Calibration Required")
    if st.button("Start Calibration"):
        st.session_state.show_calibration = True
        st.rerun()

if st.session_state.get('show_calibration', False):
    st.session_state.calibrator.render_calibration_ui(st.session_state.user_id)
    st.stop()
```

---

## Enhanced Engagement Scoring

```python
# Replace basic engagement computation with:

# Step 1: Get OpenFace features
openface_features = openface_processor.process_frame(frame)

# Step 2: Apply personalized thresholds
adjusted_features = st.session_state.calibrator.apply_personalized_thresholds(
    st.session_state.user_id,
    openface_features
)

# Step 3: Compute facial score
facial_score = openface_processor.compute_engagement_score(adjusted_features)

# Step 4: Combine with behavioral signals
result = st.session_state.multimodal_scorer.compute_multimodal_engagement(
    facial_score,
    current_activity='lecture'  # or 'quiz', 'reading', 'assignment'
)

final_score = result['engagement_score']
confidence = result['confidence']
breakdown = result['breakdown']
```

---

## Behavioral Event Tracking

```python
# Feed events to multimodal scorer:

# Keyboard
st.session_state.multimodal_scorer.update_keyboard_activity(
    datetime.now(), keystrokes=1
)

# Mouse
st.session_state.multimodal_scorer.update_mouse_activity(
    datetime.now(), 'click'  # or 'move', 'scroll'
)

# Scroll
st.session_state.multimodal_scorer.update_scroll_activity(
    datetime.now(), scroll_delta=1
)

# Video interaction
st.session_state.multimodal_scorer.update_interaction(
    datetime.now(),
    'video_play',  # or 'video_pause', 'video_seek', 'quiz_answer', 'note_taken'
    metadata={'event': 'play'}
)
```

---

## Log Lecture Completion

```python
# When lecture ends or student navigates away:

st.session_state.global_tracker.log_lecture_watched(
    lecture_id="lec_123",
    course_id="course_456",
    duration_minutes=45.5,
    engagement_score=78.5,
    completion_percentage=95.0,
    violations={
        'tab_switches': 2,
        'playback_speed_violations': 1,
        'low_engagement_periods': 3
    }
)
```

---

## Material Reading with Tracking

```python
# In materials page or lecture materials section:

reading_stats = render_material_viewer(
    material_path="./storage/courses/course_123/lecture_456/material.pdf",
    material_title="Introduction to Python",
    material_id="mat_789",
    lecture_id="lec_123",
    student_id=st.session_state.user_id
)

# When finished:
if st.button("Finish Reading"):
    st.session_state.global_tracker.log_material_read(
        material_id="mat_789",
        lecture_id="lec_123",
        title="Introduction to Python",
        time_spent_minutes=reading_stats['time_spent'] / 60,
        pages_viewed=reading_stats.get('pages_viewed', 1),
        completion_percentage=reading_stats['scroll_depth']
    )
```

---

## Quiz with Monitoring

```python
# Option 1: Complete UI with monitoring
quiz_result = render_quiz_with_monitoring(
    quiz_id="quiz_123",
    quiz_title="Python Basics Quiz",
    questions=[
        {
            'id': 'q1',
            'question': 'What is Python?',
            'options': ['Language', 'Snake', 'Both'],
            'correct': 'Language'
        },
        # ... more questions
    ],
    lecture_id="lec_123",
    student_id=st.session_state.user_id
)

if quiz_result:
    st.success(f"Score: {quiz_result['score']:.1f}%")
    st.info(f"Integrity: {quiz_result['integrity_score']:.1f}/100")
    
    # Log to global tracker
    st.session_state.global_tracker.log_quiz_taken(
        quiz_id="quiz_123",
        lecture_id="lec_123",
        score=quiz_result['score'],
        duration_minutes=quiz_result['duration'] / 60,
        violations=quiz_result['violations'],
        integrity_score=quiz_result['integrity_score']
    )
```

---

## Session Cleanup (on Logout)

```python
# In app/streamlit_app.py logout function:

if 'global_tracker' in st.session_state:
    session_summary = st.session_state.global_tracker.end_session()
    st.success("Session saved!")
    
    # Clean up
    del st.session_state.global_tracker
    del st.session_state.calibrator
    del st.session_state.multimodal_scorer
```

---

## Common Patterns

### Display Engagement Breakdown
```python
st.sidebar.metric("Engagement", f"{result['engagement_score']:.1f}",
                  delta=f"Confidence: {result['confidence']:.0f}%")

with st.sidebar.expander("📊 Breakdown"):
    for modality, score in result['breakdown'].items():
        st.metric(modality.capitalize(), f"{score:.1f}")
```

### Check Calibration Status
```python
baseline_data = calibrator.get_baseline(student_id)

if baseline_data['calibrated']:
    st.info(f"✅ Calibrated on {baseline_data['calibration_date']}")
else:
    st.warning("⚠️ Not calibrated (using default thresholds)")
```

---

## File Paths Reference

```python
# From config.yaml
calibration_file = f"./ml_data/calibration/{student_id}_baseline.json"
openface_csv = f"./ml_data/csv_logs/openface_features_{session_id}.csv"
engagement_csv = f"./ml_data/engagement_logs/engagement_log_{session_id}.csv"
behavioral_csv = f"./ml_data/activity_logs/behavioral_log_{student_id}_{month}.csv"
session_json = f"./ml_data/session_logs/global_session_{session_id}.json"
activity_csv = f"./ml_data/activity_logs/activity_summary_{student_id}_{month}.csv"
quiz_json = f"./ml_data/quiz_logs/quiz_session_{session_id}.json"
quiz_violations_csv = f"./ml_data/quiz_logs/quiz_violations_{student_id}_{month}.csv"
frame_jpg = f"./ml_data/captured_frames/{session_id}_{timestamp}.jpg"
```

---

## Quick Commands

```powershell
# Create all directories
New-Item -ItemType Directory -Force -Path ml_data\calibration,ml_data\engagement_logs,ml_data\csv_logs,ml_data\session_logs,ml_data\activity_logs,ml_data\quiz_logs,ml_data\captured_frames

# Check if files being created
Get-ChildItem ml_data\calibration\
Get-ChildItem ml_data\session_logs\

# Count total sessions
(Get-ChildItem ml_data\session_logs\).Count
```

---

**Print this for quick reference during development!** 📋

---

## ⚡ Quick Start (3 Commands)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Initialize storage
python scripts\init_storage.py

# 3. Run app
streamlit run app\streamlit_app.py
```

**Access:** http://localhost:8501

---

## 🔑 Login Credentials

| Username | Password | Role |
|----------|----------|------|
| `admin` | `admin123` | Admin |
| `dr_ramesh` | `teacher123` | Teacher |
| `demo_student` | `student123` | Student |

---

## 🤖 Train Models

```bash
# Train engagement model
python ml\train_engagement_model.py

# Train evaluation model
python ml\train_evaluation_model.py
```

---

## 🎨 Features

### **UI:**
- 🌙 Dark Mode Toggle (sidebar)
- 🎴 Modern Card Layouts
- 📊 Interactive Charts
- 💫 Smooth Animations

### **For Students:**
- 🎥 Watch Lectures
- 📝 Take Quizzes
- 📋 Submit Assignments
- 📈 View Progress
- 📅 Check Attendance

### **For Teachers:**
- 📤 Upload Content
- 📝 Create Quizzes
- 📋 Create Assignments
- 📊 View Analytics
- 📅 Track Attendance

### **For Admins:**
- 👥 Manage Users
- 📚 Manage Courses
- 🌲 Teacher Evaluation
- 📊 System Analytics

---

## 📁 Project Structure

```
app/                    - Streamlit application
  streamlit_app.py      - Main entry point
  pages/                - Page modules
services/               - Backend services
  storage.py            - JSON storage
  auth.py               - Authentication
  engagement.py         - Engagement tracking
  nlp.py                - Sentiment analysis
  evaluation.py         - Teacher evaluation
  ui_theme.py           - Theme management
ml/                     - ML models
  train_*.py            - Training scripts
  models/               - Saved models
storage/                - JSON data files
scripts/                - Utility scripts
  init_storage.py       - Initialize storage
```

---

## 🐛 Troubleshooting

**App won't start?**
```bash
pip install -r requirements.txt
```

**No data?**
```bash
python scripts\init_storage.py
```

**Port in use?**
```bash
streamlit run app\streamlit_app.py --server.port 8502
```

**Models missing?**
```bash
python ml\train_engagement_model.py
python ml\train_evaluation_model.py
```

---

## 📊 File Locations

**Storage:** `./storage/*.json`  
**Models:** `./ml/models/*.pkl`  
**Videos:** `./storage/courses/*/lectures/*.mp4`  
**Logs:** Streamlit console

---

## ✅ Quick Test

1. Run `python scripts\init_storage.py`
2. Run `streamlit run app\streamlit_app.py`
3. Login as `demo_student` / `student123`
4. Click "🎥 Lectures"
5. Watch a lecture
6. Take a quiz
7. View progress

---

## 🎯 Key Commands

```bash
# Install
pip install -r requirements.txt

# Initialize
python scripts\init_storage.py

# Run
streamlit run app\streamlit_app.py

# Train Models
python ml\train_engagement_model.py
python ml\train_evaluation_model.py

# Stop App
Ctrl + C
```

---

## 📚 Documentation

- `README.md` - Complete guide
- `TESTING_GUIDE.md` - Testing instructions
- `IMPLEMENTATION_STATUS.md` - Feature status
- `NEW_FEATURES_ADDED.md` - Latest features

---

## 🎨 Theme Toggle

**Location:** Sidebar  
**Button:** 🌙 Dark Mode / ☀️ Light Mode  
**Shortcut:** Click to toggle instantly

---

## 💡 Tips

1. **Dark Mode** - Great for night studying
2. **Progress Page** - Track your learning
3. **Attendance** - Monitor presence
4. **Analytics** - View detailed stats
5. **Feedback** - Help improve courses

---

**Need Help?** Check `TESTING_GUIDE.md` for detailed instructions!
