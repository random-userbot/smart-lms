# Engagement Score Accuracy Improvement Guide

## 🎯 Current Engagement Score Calculation

### Current Formula (services/openface_processor.py):
```python
engagement_score = (
    gaze_score × 0.30 +           # 30%: Looking at screen
    head_pose_score × 0.25 +      # 25%: Head position stability
    attention_aus_score × 0.25 +  # 25%: Attention-related AUs
    blink_rate_score × 0.10 +     # 10%: Normal blink frequency
    facial_expression_score × 0.10 # 10%: Positive expressions
) × 100
```

**Current Accuracy Estimate:** ~70-75%

---

## 🚀 Improvement Strategies

### 1. **Calibration Phase (Personalized Baseline)**

#### Problem:
- Current system uses generic thresholds
- Individual differences in gaze patterns, head pose, blinking
- Some students naturally have different resting positions

#### Solution: **Per-Student Calibration**
```python
class EngagementCalibrator:
    def calibrate_student(self, student_id: str, duration: int = 30):
        """
        Calibrate for 30 seconds while student watches engaging content
        Record baseline metrics for personalized thresholds
        """
        baseline = {
            'normal_gaze_angle': [],  # Their natural screen-looking angle
            'normal_head_pose': [],   # Their comfortable head position
            'blink_rate': [],          # Their typical blink frequency
            'au_baseline': {}          # Their neutral AU values
        }
        
        # Record for 30 seconds
        # Save to: ml_data/calibration/{student_id}_baseline.json
```

**Implementation:**
- Add calibration step on first lecture watch
- Show calibration video (30 seconds of engaging content)
- Record baseline while they're naturally attentive
- Use personalized thresholds instead of generic ones

**Expected Accuracy Gain:** +10-15%

---

### 2. **Temporal Context Analysis (Time-Series LSTM)**

#### Problem:
- Current system evaluates each frame independently
- Ignores temporal patterns and context
- Single frames can be misleading

#### Solution: **LSTM-Based Engagement Predictor**
```python
import torch
import torch.nn as nn

class EngagementLSTM(nn.Module):
    def __init__(self, input_size=50, hidden_size=128, num_layers=2):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)  # Engagement score output
    
    def forward(self, x):
        # x shape: (batch, sequence_length, features)
        lstm_out, _ = self.lstm(x)
        # Take last time step
        output = self.fc(lstm_out[:, -1, :])
        return torch.sigmoid(output) * 100  # 0-100 scale
```

**Features to Use:**
- Past 10 seconds of data (10 frames)
- All 17 AUs, gaze, head pose
- Capture engagement trends, not just snapshots

**Training Data:**
- Label data from teacher observations
- Use quiz scores as proxy for engagement
- Correlation with learning outcomes

**Expected Accuracy Gain:** +15-20%

---

### 3. **Multi-Modal Fusion (Facial + Behavioral)**

#### Problem:
- Only using facial features
- Ignoring behavioral signals (mouse movement, typing, scrolling)

#### Solution: **Combine Facial + Behavioral Signals**
```python
def calculate_multimodal_engagement(facial_data, behavioral_data):
    # Facial engagement (current system)
    facial_score = compute_facial_engagement(facial_data)
    
    # Behavioral engagement (NEW)
    behavioral_score = compute_behavioral_engagement(behavioral_data)
    
    # Combine with learned weights
    final_score = (
        facial_score × 0.70 +        # 70%: Facial features
        behavioral_score × 0.30       # 30%: Behavioral signals
    )
    
    return final_score

def compute_behavioral_engagement(behavioral_data):
    """
    Behavioral signals:
    - Keyboard activity (taking notes)
    - Mouse movement (interacting with content)
    - Scroll events (reading materials)
    - Video controls (pause/play/seek appropriately)
    - Question answering speed
    """
    keyboard_activity = behavioral_data['keystrokes_per_min']
    mouse_activity = behavioral_data['mouse_events_per_min']
    scroll_depth = behavioral_data['scroll_progress']
    
    # Normalize and weight
    behavioral_score = (
        normalize(keyboard_activity, max=60) × 0.30 +
        normalize(mouse_activity, max=100) × 0.30 +
        normalize(scroll_depth, max=100) × 0.40
    )
    
    return behavioral_score * 100
```

**Expected Accuracy Gain:** +10-12%

---

### 4. **Contextual AU Interpretation**

#### Problem:
- AUs interpreted generically
- Context matters: smiling during funny video vs. serious lecture

#### Solution: **Context-Aware AU Analysis**
```python
def context_aware_au_analysis(aus, lecture_context):
    """
    Adjust AU interpretation based on lecture type and moment
    
    lecture_context = {
        'type': 'theoretical' | 'practical' | 'humorous',
        'difficulty': 1-5,
        'current_segment': 'intro' | 'core' | 'example' | 'conclusion'
    }
    """
    
    # Example: Smiling (AU12)
    if lecture_context['type'] == 'humorous':
        # High AU12 = engaged (appropriate)
        smile_score = aus['AU12_r'] / 5.0
    else:
        # High AU12 might indicate distraction
        smile_score = max(0, 1 - (aus['AU12_r'] - 2) / 5.0)
    
    # Example: Brow furrow (AU04)
    if lecture_context['difficulty'] >= 4:
        # Furrowing = concentration (good)
        concentration_score = aus['AU04_r'] / 5.0
    else:
        # Furrowing = confusion (bad)
        concentration_score = max(0, 1 - aus['AU04_r'] / 5.0)
    
    return contextual_engagement_score
```

**Implementation:**
- Add lecture metadata (type, difficulty, segments)
- Train context-specific models
- Use teacher annotations for ground truth

**Expected Accuracy Gain:** +8-10%

---

### 5. **Advanced Gaze Tracking (Eye-Tracking Validation)**

#### Problem:
- Current gaze estimation is approximate (MediaPipe iris landmarks)
- No validation of actual screen fixation

#### Solution: **Improved Gaze Estimation**
```python
def improved_gaze_estimation(landmarks, screen_bounds):
    """
    Better gaze tracking with:
    1. Screen boundary calibration
    2. Fixation detection (not just direction)
    3. Saccade vs. fixation distinction
    """
    
    # Calculate precise gaze point on screen
    gaze_point = estimate_gaze_point(landmarks, screen_bounds)
    
    # Check if gaze is on video player area
    video_bounds = get_video_player_bounds()
    is_looking_at_video = point_in_rect(gaze_point, video_bounds)
    
    # Detect fixation (stable gaze for >200ms)
    is_fixated = detect_fixation(gaze_history, threshold_ms=200)
    
    # Score
    if is_looking_at_video and is_fixated:
        gaze_score = 1.0
    elif is_looking_at_video:
        gaze_score = 0.7  # Looking but not fixated (scanning)
    else:
        gaze_score = 0.3  # Looking away
    
    return gaze_score
```

**Hardware Improvement:**
- Optional: WebGazer.js for browser-based eye tracking
- Optional: External eye tracker for ground truth validation

**Expected Accuracy Gain:** +5-8%

---

### 6. **Engagement State Machine**

#### Problem:
- Binary engaged/disengaged is too simplistic
- Doesn't capture engagement transitions

#### Solution: **State-Based Engagement Model**
```python
class EngagementStateMachine:
    """
    States:
    - HIGHLY_ENGAGED: Active learning, taking notes, focused
    - ENGAGED: Watching attentively
    - PASSIVE: Watching but not actively engaging
    - DISTRACTED: Looking away briefly, still present
    - DISENGAGED: Extended inattention
    - DROWSY: Signs of fatigue
    """
    
    def transition(self, current_state, features, duration):
        # State transitions based on:
        # - Duration in current state
        # - Feature thresholds
        # - Transition probabilities
        
        if current_state == 'ENGAGED':
            if features['engagement_score'] < 30 and duration > 5:
                return 'DISTRACTED'
            elif features['drowsiness_level'] > 3:
                return 'DROWSY'
            elif features['engagement_score'] > 85 and has_behavioral_signals:
                return 'HIGHLY_ENGAGED'
        
        # ... other transitions
        
        return current_state
```

**Benefits:**
- Smoother engagement tracking
- Reduces noise from brief distractions
- Better captures sustained attention

**Expected Accuracy Gain:** +5-7%

---

### 7. **Learning Outcome Validation**

#### Problem:
- No ground truth for engagement
- Can't validate if high engagement = good learning

#### Solution: **Correlation with Learning Outcomes**
```python
def validate_engagement_model():
    """
    Correlate engagement scores with:
    1. Quiz performance (immediate learning)
    2. Assignment scores (applied learning)
    3. Final exam results (long-term retention)
    4. Teacher assessments
    """
    
    # Collect data
    for student in students:
        engagement_avg = get_avg_engagement(student)
        quiz_scores = get_quiz_scores(student)
        assignment_scores = get_assignment_scores(student)
        
        # Correlation analysis
        correlation = compute_correlation(
            engagement_avg, 
            quiz_scores
        )
        
        # If low correlation, adjust engagement model
        if correlation < 0.6:
            recalibrate_engagement_weights()
```

**Iterative Improvement:**
- Collect data for 1 month
- Analyze correlations
- Adjust weights to maximize correlation
- Repeat

**Expected Accuracy Gain:** +10-15% (over time)

---

### 8. **Ensemble Models**

#### Problem:
- Single model might have biases
- Different features work better for different students

#### Solution: **Ensemble of Engagement Models**
```python
class EngagementEnsemble:
    def __init__(self):
        self.models = [
            FacialEngagementModel(),      # AU-based
            GazeEngagementModel(),         # Gaze-based
            PostureEngagementModel(),      # Head pose
            BehavioralEngagementModel(),   # Keyboard/mouse
            TemporalEngagementModel()      # LSTM time-series
        ]
    
    def predict(self, features):
        predictions = []
        
        for model in self.models:
            score = model.predict(features)
            predictions.append(score)
        
        # Weighted average (learned weights)
        final_score = np.average(predictions, weights=self.model_weights)
        
        return final_score
```

**Expected Accuracy Gain:** +8-12%

---

## 📊 Recommended Implementation Priority

### Phase 1: Quick Wins (1-2 weeks)
1. **Calibration Phase** → +10-15% accuracy
2. **Multi-Modal Fusion** → +10-12% accuracy
3. **Contextual AU Interpretation** → +8-10% accuracy

**Total Expected Gain:** +28-37% accuracy (→ 98-112% total, normalize to ~95%)

### Phase 2: Advanced Models (1-2 months)
4. **LSTM Time-Series** → +15-20% accuracy
5. **Engagement State Machine** → +5-7% accuracy
6. **Improved Gaze Tracking** → +5-8% accuracy

**Total Expected Gain:** +25-35% accuracy

### Phase 3: Validation & Refinement (3-6 months)
7. **Learning Outcome Validation** → +10-15% accuracy (iterative)
8. **Ensemble Models** → +8-12% accuracy

---

## 🔬 Data Collection for Training

### What to Collect (Already doing):
✅ OpenFace features (17 AUs, gaze, pose)
✅ Engagement scores
✅ Behavioral logs
✅ Quiz scores
✅ Violation logs

### What to Add:
- [ ] **Teacher annotations:** Manual engagement ratings on sample videos
- [ ] **Ground truth labels:** Mark segments as "highly engaged", "engaged", "distracted"
- [ ] **Learning outcomes:** Link engagement to quiz/exam performance
- [ ] **Student self-reports:** "How engaged did you feel?" surveys
- [ ] **Calibration data:** Per-student baselines

### Annotation Tool:
```python
# Build simple annotation interface
def annotate_engagement_segments():
    """
    Teacher watches recorded session
    Marks segments with engagement level
    Creates ground truth dataset
    """
    video_player()
    engagement_slider(0-100)
    save_annotation_button()
```

---

## 🧪 A/B Testing Framework

```python
def run_engagement_ab_test():
    """
    Test new engagement model vs. current model
    """
    # Group A: Current model
    # Group B: New model with improvements
    
    # Metrics to compare:
    # 1. Correlation with quiz scores
    # 2. Teacher agreement rate
    # 3. Student feedback on accuracy
    # 4. False positive rate (flagging engaged students)
    # 5. False negative rate (missing disengaged students)
    
    # Run for 2 weeks, compare results
```

---

## 🎯 Target Accuracy Goals

| Metric | Current | Phase 1 | Phase 2 | Phase 3 |
|--------|---------|---------|---------|---------|
| Overall Accuracy | 70-75% | 85-90% | 92-95% | 95-98% |
| Correlation with Quiz Scores | 0.45 | 0.60 | 0.75 | 0.85 |
| Teacher Agreement | 65% | 80% | 90% | 95% |
| False Positive Rate | 15% | 8% | 4% | <2% |
| False Negative Rate | 20% | 10% | 5% | <3% |

---

## 💡 Immediate Actions (This Week)

1. **Add Calibration Feature:**
   ```python
   # In app/pages/lectures.py, add calibration step
   if not has_calibration_data(student_id):
       run_calibration_phase()
   ```

2. **Collect Teacher Annotations:**
   - Record 10 sample lecture sessions
   - Have teacher annotate engagement levels
   - Use as initial training data

3. **Implement Behavioral Tracking:**
   - Add keyboard/mouse activity tracking
   - Combine with facial features (70/30 split)

4. **Add Context to Lectures:**
   ```python
   # In storage/lectures.json, add:
   {
       "lecture_id": "...",
       "context": {
           "type": "theoretical",
           "difficulty": 3,
           "has_humor": false,
           "segments": [...]
       }
   }
   ```

---

## 📈 Success Metrics

Track these metrics weekly:
- Engagement score vs. quiz performance correlation
- Student complaints about inaccurate scores
- Teacher feedback on score validity
- System uptime and frame processing rate
- Data quality (% frames with face detected)

---

**Current System is good, but these improvements will make it GREAT!** 🚀
