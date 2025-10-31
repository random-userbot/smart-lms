# Integration Guide: New Features

## 🎯 Overview

This guide covers the integration of new engagement accuracy improvements and session tracking features:

1. **Engagement Calibration** - Personalized baselines
2. **Multimodal Engagement Scoring** - Facial + behavioral signals
3. **Global Session Tracking** - Login to logout activity logs
4. **Quiz Monitoring** - Webcam + integrity tracking during quizzes
5. **Material Reading Tracking** - In-app reading with time tracking

---

## 📋 Quick Integration Checklist

### Phase 1: Core Services (Already Created ✅)
- [x] `services/openface_processor.py` - Facial feature extraction
- [x] `services/pip_webcam_live.py` - PiP webcam
- [x] `services/behavioral_logger.py` - Event logging
- [x] `services/anti_cheating.py` - Violation detection
- [x] `services/session_tracker.py` - Global session tracking
- [x] `services/material_reader.py` - Material viewing
- [x] `services/quiz_monitor.py` - Quiz monitoring
- [x] `services/engagement_calibrator.py` - Personalized calibration
- [x] `services/multimodal_engagement.py` - Multi-modal scoring

### Phase 2: App Integration (To Do 🔄)
- [ ] Update `app/streamlit_app.py` - Main app initialization
- [ ] Update `app/pages/lectures.py` - Integrate calibration + multimodal
- [ ] Create/Update `app/pages/materials.py` - Material reading page
- [ ] Update quiz display logic - Integrate quiz monitoring
- [ ] Test complete flow

---

## 🚀 Step-by-Step Integration

### 1. Main App Initialization (app/streamlit_app.py)

```python
# Add to imports
from services.session_tracker import GlobalSessionTracker
from services.engagement_calibrator import EngagementCalibrator
from services.multimodal_engagement import MultimodalEngagementScorer

# Initialize in session_state (after login)
def initialize_session():
    if 'global_tracker' not in st.session_state:
        st.session_state.global_tracker = GlobalSessionTracker(
            student_id=st.session_state.user_id,
            student_name=st.session_state.username
        )
        st.session_state.global_tracker.start_session()
    
    if 'calibrator' not in st.session_state:
        st.session_state.calibrator = EngagementCalibrator()
    
    if 'multimodal_scorer' not in st.session_state:
        st.session_state.multimodal_scorer = MultimodalEngagementScorer()

# Add to login success callback
def on_login_success():
    # ... existing login code ...
    initialize_session()

# Add to logout callback
def on_logout():
    if 'global_tracker' in st.session_state:
        st.session_state.global_tracker.end_session()
    # ... existing logout code ...
```

### 2. Lectures Page with Calibration (app/pages/lectures.py)

**Add at the beginning of the page:**

```python
from services.engagement_calibrator import EngagementCalibrator
from services.multimodal_engagement import MultimodalEngagementScorer

# Check if calibration needed
if 'calibrator' in st.session_state:
    calibrator = st.session_state.calibrator
    
    if calibrator.needs_calibration(st.session_state.user_id):
        st.warning("⚠️ Calibration Required for Better Accuracy")
        with st.expander("📌 Why Calibration?", expanded=True):
            st.markdown("""
            To improve engagement tracking accuracy, we need to understand your unique patterns:
            - Your natural gaze direction when focused
            - Your typical head position
            - Your normal blink rate
            
            **This takes just 30 seconds and improves accuracy by ~10-15%!**
            """)
            
            if st.button("Start Calibration Now", type="primary"):
                st.session_state.show_calibration = True
                st.rerun()

# Show calibration UI if requested
if st.session_state.get('show_calibration', False):
    calibrator.render_calibration_ui(st.session_state.user_id)
    
    # After calibration completes, hide UI
    if st.button("Continue to Lectures"):
        st.session_state.show_calibration = False
        st.rerun()
    
    st.stop()  # Don't show lectures during calibration
```

**Update engagement score calculation:**

```python
# In the webcam callback or engagement computation
def compute_enhanced_engagement(openface_features):
    # Apply personalized thresholds
    if 'calibrator' in st.session_state:
        adjusted_features = st.session_state.calibrator.apply_personalized_thresholds(
            st.session_state.user_id,
            openface_features
        )
    else:
        adjusted_features = openface_features
    
    # Compute facial engagement score (from OpenFaceProcessor)
    facial_score = openface_processor.compute_engagement_score(adjusted_features)
    
    # Apply multimodal enhancement
    if 'multimodal_scorer' in st.session_state:
        result = st.session_state.multimodal_scorer.compute_multimodal_engagement(
            facial_score,
            current_activity='lecture'
        )
        final_score = result['engagement_score']
        confidence = result['confidence']
        
        # Display breakdown
        with st.sidebar:
            st.metric("Engagement Score", f"{final_score:.1f}", 
                     delta=f"Confidence: {confidence:.0f}%")
            
            with st.expander("📊 Score Breakdown"):
                for modality, score in result['breakdown'].items():
                    st.metric(modality.capitalize(), f"{score:.1f}")
    else:
        final_score = facial_score
    
    return final_score
```

**Log lecture completion to global tracker:**

```python
# When lecture ends or student navigates away
def on_lecture_complete(lecture_id, watch_duration, avg_engagement, completion_pct):
    if 'global_tracker' in st.session_state:
        st.session_state.global_tracker.log_lecture_watched(
            lecture_id=lecture_id,
            course_id=current_course_id,
            duration_minutes=watch_duration / 60,
            engagement_score=avg_engagement,
            completion_percentage=completion_pct,
            violations={
                'tab_switches': tab_switch_count,
                'playback_speed_violations': speed_violation_count,
                'low_engagement_periods': low_engagement_count
            }
        )
```

### 3. Material Reading Page (app/pages/materials.py or integrate into lectures.py)

```python
import streamlit as st
from services.material_reader import MaterialReader, render_material_viewer

st.title("📚 Course Materials")

# Select material
materials = load_materials_for_lecture(selected_lecture_id)

if materials:
    selected_material = st.selectbox(
        "Select Material",
        materials,
        format_func=lambda m: m['title']
    )
    
    if selected_material:
        # Render material viewer with tracking
        reading_stats = render_material_viewer(
            material_path=selected_material['file_path'],
            material_title=selected_material['title'],
            material_id=selected_material['id'],
            lecture_id=selected_lecture_id,
            student_id=st.session_state.user_id
        )
        
        # Display reading stats
        if reading_stats:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Time Spent", f"{reading_stats['time_spent']:.1f}s")
            with col2:
                st.metric("Scroll Progress", f"{reading_stats['scroll_depth']:.0f}%")
            with col3:
                status = "✅ Complete" if reading_stats['completed'] else "🔄 In Progress"
                st.metric("Status", status)
        
        # Log to global tracker when material is closed
        if st.button("Finish Reading"):
            if 'global_tracker' in st.session_state:
                st.session_state.global_tracker.log_material_read(
                    material_id=selected_material['id'],
                    lecture_id=selected_lecture_id,
                    title=selected_material['title'],
                    time_spent_minutes=reading_stats['time_spent'] / 60,
                    pages_viewed=reading_stats.get('pages_viewed', 1),
                    completion_percentage=reading_stats['scroll_depth']
                )
            st.success("Material reading logged!")
            st.rerun()
else:
    st.info("No materials available for this lecture.")
```

### 4. Quiz Monitoring Integration

**Update quiz display function:**

```python
from services.quiz_monitor import QuizMonitor, render_quiz_with_monitoring

def display_quiz(quiz_id, questions):
    """Display quiz with monitoring"""
    
    # Option 1: Use complete monitoring UI
    quiz_result = render_quiz_with_monitoring(
        quiz_id=quiz_id,
        quiz_title=quiz_data['title'],
        questions=questions,
        lecture_id=lecture_id,
        student_id=st.session_state.user_id
    )
    
    if quiz_result:
        st.success(f"Quiz submitted! Score: {quiz_result['score']:.1f}%")
        st.info(f"Integrity Score: {quiz_result['integrity_score']:.1f}/100")
        
        # Log to global tracker
        if 'global_tracker' in st.session_state:
            st.session_state.global_tracker.log_quiz_taken(
                quiz_id=quiz_id,
                lecture_id=lecture_id,
                score=quiz_result['score'],
                duration_minutes=quiz_result['duration'] / 60,
                violations=quiz_result['violations'],
                integrity_score=quiz_result['integrity_score']
            )
    
    # Option 2: Custom quiz UI with monitoring
    # ... your custom quiz UI ...
    # Just integrate QuizMonitor for tracking
```

### 5. Behavioral Event Tracking

**Update behavioral logger to feed multimodal scorer:**

In `services/behavioral_logger.py`:

```python
from services.multimodal_engagement import MultimodalEngagementScorer

class BehavioralLogger:
    def __init__(self, ...):
        # ... existing init ...
        self.multimodal_scorer = MultimodalEngagementScorer()
    
    def log_keystroke(self, ...):
        # ... existing code ...
        # Feed to multimodal scorer
        self.multimodal_scorer.update_keyboard_activity(
            datetime.now(),
            keystrokes=1
        )
    
    def log_mouse_click(self, ...):
        # ... existing code ...
        self.multimodal_scorer.update_mouse_activity(
            datetime.now(),
            'click'
        )
    
    def log_scroll(self, ...):
        # ... existing code ...
        self.multimodal_scorer.update_scroll_activity(
            datetime.now(),
            scroll_delta=1
        )
    
    def log_video_interaction(self, event_type, ...):
        # ... existing code ...
        self.multimodal_scorer.update_interaction(
            datetime.now(),
            f'video_{event_type}',
            metadata={'event': event_type}
        )
```

---

## 🧪 Testing Instructions

### Test 1: Calibration Flow
1. Login as a new student
2. Navigate to lectures page
3. See calibration prompt
4. Complete 30-second calibration
5. Verify baseline saved: `ml_data/calibration/{student_id}_baseline.json`

### Test 2: Multimodal Engagement
1. Watch a lecture with webcam enabled
2. Type some notes (keyboard activity)
3. Move mouse and click
4. Observe engagement score breakdown in sidebar
5. Verify facial + behavioral scores are combined

### Test 3: Global Session Tracking
1. Login
2. Watch a lecture (full or partial)
3. Take a quiz
4. Read a material
5. Logout
6. Check session file: `ml_data/session_logs/global_session_{session_id}.json`
7. Check activity summary: `ml_data/activity_logs/activity_summary_{student_id}_{month}.csv`

### Test 4: Quiz Monitoring
1. Start a quiz
2. See webcam PiP appear
3. Switch tabs → see violation logged
4. Answer questions
5. Submit quiz
6. Check integrity score
7. Verify quiz log: `ml_data/quiz_logs/quiz_session_{session_id}.json`

### Test 5: Material Reading
1. Select a material (PDF or text)
2. Read for 30 seconds
3. Scroll through content
4. Finish reading
5. Verify time tracked in global session
6. Check reading stats in material viewer

---

## 📊 Data Validation

After testing, verify these files exist and contain correct data:

```
ml_data/
├── calibration/
│   └── {student_id}_baseline.json          ✓ Personalized thresholds
├── engagement_logs/
│   └── engagement_log_{session_id}.csv     ✓ Frame-by-frame scores
├── session_logs/
│   └── global_session_{session_id}.json    ✓ Complete session data
├── activity_logs/
│   ├── activity_summary_{student_id}_{month}.csv  ✓ Monthly aggregates
│   └── behavioral_log_{student_id}_{month}.csv    ✓ All events
├── quiz_logs/
│   ├── quiz_session_{session_id}.json      ✓ Quiz details
│   └── quiz_violations_{student_id}_{month}.csv   ✓ Violations
└── captured_frames/
    └── {session_id}_{timestamp}.jpg        ✓ Webcam frames
```

---

## 🐛 Troubleshooting

### Issue: Calibration not triggering
**Solution:** Check `st.session_state.calibrator` exists and `needs_calibration()` returns True

### Issue: Multimodal score same as facial score
**Solution:** Ensure behavioral events are being logged (keyboard, mouse, etc.)

### Issue: Session not saving on logout
**Solution:** Verify `global_tracker.end_session()` is called in logout handler

### Issue: Quiz webcam not showing
**Solution:** Check `config.yaml` → `quiz_monitoring.webcam_required: true`

### Issue: Material reading time not tracking
**Solution:** Verify JavaScript tracking code is rendered in material viewer

---

## 📈 Performance Optimization

1. **Frame Processing:**
   - Current: ~1 FPS (1 frame per second)
   - Sufficient for engagement tracking
   - If experiencing lag, reduce to 0.5 FPS

2. **CSV Writing:**
   - Buffer writes every 10 seconds instead of per-frame
   - Use batch writes to improve performance

3. **Session Storage:**
   - Sessions saved on logout (not during)
   - Monthly CSVs for efficient querying

4. **Calibration:**
   - Only required once per 30 days
   - Minimal overhead after initial setup

---

## 🎯 Next Steps

### Immediate (This Week):
1. Integrate calibration prompt in lectures page
2. Add multimodal scorer to engagement computation
3. Test global session tracking flow
4. Verify all CSV/JSON files generating correctly

### Short-term (Next Week):
5. Create materials reading page with tracking
6. Integrate quiz monitoring into existing quiz flow
7. Add session summary dashboard for students
8. Teacher dashboard for viewing student sessions

### Long-term (Next Month):
9. Implement LSTM temporal model (see ENGAGEMENT_ACCURACY_IMPROVEMENTS.md)
10. Add A/B testing framework
11. Collect teacher annotations for ground truth
12. Train ML model on labeled engagement data

---

## 📚 Related Documentation

- [ENGAGEMENT_ACCURACY_IMPROVEMENTS.md](./ENGAGEMENT_ACCURACY_IMPROVEMENTS.md) - Detailed accuracy improvement strategies
- [REALTIME_ENGAGEMENT_COMPLETE.md](./REALTIME_ENGAGEMENT_COMPLETE.md) - Original engagement system docs
- [ENGAGEMENT_QUICK_START.md](./ENGAGEMENT_QUICK_START.md) - Quick setup guide
- [config.yaml](./config.yaml) - Complete configuration reference

---

## ✅ Integration Status

| Feature | Status | File | Next Step |
|---------|--------|------|-----------|
| Calibration Service | ✅ Created | `services/engagement_calibrator.py` | Integrate into lectures page |
| Multimodal Scoring | ✅ Created | `services/multimodal_engagement.py` | Connect to behavioral logger |
| Session Tracker | ✅ Created | `services/session_tracker.py` | Add to login/logout flow |
| Quiz Monitor | ✅ Created | `services/quiz_monitor.py` | Replace existing quiz UI |
| Material Reader | ✅ Created | `services/material_reader.py` | Create materials page |
| Config Updated | ✅ Done | `config.yaml` | - |
| Main App Integration | 🔄 Pending | `app/streamlit_app.py` | Initialize trackers |
| Lectures Integration | 🔄 Pending | `app/pages/lectures.py` | Add calibration + multimodal |
| Materials Page | ❌ To Create | `app/pages/materials.py` | Build page |
| Quiz Integration | 🔄 Pending | Quiz display logic | Use `render_quiz_with_monitoring()` |
| Testing | ❌ Pending | - | Run all 5 test scenarios |

---

**Ready to integrate! Start with Phase 2 tasks above.** 🚀
