# System Architecture Diagram

## 📊 Complete Engagement Tracking System

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           STUDENT LOGIN                                  │
│                                 ↓                                        │
│                   Initialize Global Session Tracker                      │
│                                 ↓                                        │
│                     Check Calibration Status                             │
└─────────────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
            [Needs Calibration]         [Already Calibrated]
                    │                           │
                    ↓                           ↓
        ┌───────────────────────┐    ┌──────────────────────┐
        │  30s Calibration      │    │  Load Baseline       │
        │  - Record gaze        │    │  Thresholds          │
        │  - Record head pose   │    │                      │
        │  - Record blinks      │    │                      │
        │  - Record AUs         │    │                      │
        └───────────┬───────────┘    └──────────┬───────────┘
                    │                           │
                    └──────────────┬────────────┘
                                   ↓
                    ┌────────────────────────────┐
                    │  Ready for Activities      │
                    └────────────┬───────────────┘
                                 │
                 ┌───────────────┼───────────────┬────────────────┐
                 │               │               │                │
                 ↓               ↓               ↓                ↓
         ┌──────────────┐ ┌──────────────┐ ┌──────────┐ ┌──────────────┐
         │   LECTURE    │ │     QUIZ     │ │ MATERIAL │ │ ASSIGNMENT   │
         └──────┬───────┘ └──────┬───────┘ └────┬─────┘ └──────┬───────┘
                │                │              │              │
                └────────────────┴──────────────┴──────────────┘
                                 ↓
                    ┌────────────────────────────┐
                    │   ENGAGEMENT TRACKING      │
                    └────────────┬───────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
        ↓                        ↓                        ↓
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│ FACIAL        │      │ BEHAVIORAL    │      │ INTERACTION   │
│ FEATURES      │      │ SIGNALS       │      │ TRACKING      │
│               │      │               │      │               │
│ - Webcam      │      │ - Keyboard    │      │ - Video       │
│ - 17 AUs      │      │ - Mouse       │      │   controls    │
│ - Gaze        │      │ - Scroll      │      │ - Quiz        │
│ - Head pose   │      │ - Focus       │      │   answers     │
│ - Blinks      │      │ - Tab switch  │      │ - Notes       │
└───────┬───────┘      └───────┬───────┘      └───────┬───────┘
        │                      │                      │
        ↓                      ↓                      ↓
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│OpenFace       │      │Behavioral     │      │Event          │
│Processor      │      │Logger         │      │Trackers       │
└───────┬───────┘      └───────┬───────┘      └───────┬───────┘
        │                      │                      │
        └──────────────────────┼──────────────────────┘
                               ↓
                ┌──────────────────────────────┐
                │  Engagement Calibrator       │
                │  (Apply Personalized         │
                │   Thresholds)                │
                └──────────────┬───────────────┘
                               ↓
                ┌──────────────────────────────┐
                │  Multimodal Engagement       │
                │  Scorer                      │
                │                              │
                │  Weights:                    │
                │  - Facial: 50%               │
                │  - Behavioral: 25%           │
                │  - Interaction: 15%          │
                │  - Temporal: 10%             │
                └──────────────┬───────────────┘
                               ↓
                ┌──────────────────────────────┐
                │  ENGAGEMENT SCORE (0-100)    │
                │  + Confidence Level          │
                │  + Breakdown by Modality     │
                └──────────────┬───────────────┘
                               ↓
                ┌──────────────────────────────┐
                │  Anti-Cheating Monitor       │
                │  - Check violations          │
                │  - Issue warnings            │
                │  - Log incidents             │
                └──────────────┬───────────────┘
                               ↓
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ↓                      ↓                      ↓
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│ CSV LOGS      │      │ JSON SESSIONS │      │ FRAME CAPTURE │
│               │      │               │      │               │
│ - OpenFace    │      │ - Session     │      │ - Timestamp   │
│   features    │      │   summary     │      │   images      │
│ - Engagement  │      │ - Quiz        │      │               │
│   log         │      │   details     │      │               │
│ - Behavioral  │      │ - Activity    │      │               │
│   events      │      │   timeline    │      │               │
│ - Violations  │      │               │      │               │
└───────────────┘      └───────────────┘      └───────────────┘
        │                      │                      │
        └──────────────────────┼──────────────────────┘
                               ↓
                ┌──────────────────────────────┐
                │  Global Session Tracker      │
                │  - Aggregate all activities  │
                │  - Calculate totals          │
                │  - Compute integrity score   │
                └──────────────┬───────────────┘
                               ↓
                    ┌──────────────────────┐
                    │  STUDENT LOGOUT      │
                    │  - End session       │
                    │  - Save summary      │
                    │  - Generate report   │
                    └──────────────────────┘
```

---

## 🔄 Activity-Specific Flows

### LECTURE FLOW
```
Start Lecture
    ↓
├─→ PiP Webcam Starts (bottom-right)
│   ├─→ Capture frame every 1 second
│   ├─→ Extract OpenFace features
│   ├─→ Apply personalized thresholds
│   └─→ Compute engagement score
│
├─→ Video Player Monitoring
│   ├─→ Track play/pause
│   ├─→ Monitor playback speed (max 1.25x)
│   └─→ Log seek events
│
├─→ Behavioral Tracking
│   ├─→ Tab switches
│   ├─→ Focus changes
│   ├─→ Keyboard activity
│   └─→ Mouse activity
│
└─→ Anti-Cheating Checks
    ├─→ Speed violations → Reset to 1.0x
    ├─→ Tab switches > 3 → Warning
    └─→ Engagement < 30 → Alert
    ↓
On Lecture Complete/Exit
    ↓
GlobalSessionTracker.log_lecture_watched()
    - Duration, avg engagement, violations
```

### QUIZ FLOW
```
Start Quiz
    ↓
├─→ Quiz Monitor Initializes
│   ├─→ PiP webcam enabled
│   ├─→ Violation tracking active
│   └─→ Time tracking per question
│
├─→ Per Question:
│   ├─→ Start time recorded
│   ├─→ Monitor for violations
│   │   ├─→ Tab switch (+5 penalty)
│   │   ├─→ Focus loss (+2 penalty)
│   │   ├─→ Copy/paste (+10 penalty)
│   │   ├─→ Low engagement (+3 penalty)
│   │   └─→ Multiple faces (+15 penalty)
│   ├─→ Record answer + time
│   └─→ Update engagement
│
└─→ On Quiz Submit
    ├─→ Calculate score
    ├─→ Calculate integrity (100 - penalties)
    ├─→ Flag if integrity < 50
    ├─→ Save detailed log
    └─→ GlobalSessionTracker.log_quiz_taken()
```

### MATERIAL READING FLOW
```
Open Material
    ↓
├─→ Material Reader Initializes
│   ├─→ Load content (PDF/Text/Markdown)
│   ├─→ Start JavaScript tracking
│   └─→ Display in viewport
│
├─→ While Reading:
│   ├─→ Update time every 1 second
│   ├─→ Track scroll depth (0-100%)
│   ├─→ Count interactions (clicks, scrolls)
│   └─→ Check completion (95% scroll)
│
└─→ On Close/Finish
    ├─→ Get reading stats
    ├─→ Display summary
    └─→ GlobalSessionTracker.log_material_read()
```

---

## 📦 Data Storage Structure

```
ml_data/
│
├── calibration/
│   └── {student_id}_baseline.json
│       {
│         "student_id": "...",
│         "calibration_date": "...",
│         "baseline": {
│           "gaze_angle_threshold": 22.5,
│           "head_pitch_range": [-12, 18],
│           "head_yaw_range": [-18, 22],
│           "blink_rate_range": [12, 28],
│           "au_baseline": {...}
│         }
│       }
│
├── engagement_logs/
│   └── engagement_log_{session_id}.csv
│       timestamp, face_detected, engagement_score, gaze_score, 
│       head_pose_score, attention_score, status, violations
│
├── csv_logs/
│   └── openface_features_{session_id}.csv
│       timestamp, frame_number, face_detected, detection_confidence,
│       AU01_r, AU02_r, ..., AU45_r,
│       gaze_0_x, gaze_0_y, gaze_0_z, gaze_1_x, gaze_1_y, gaze_1_z,
│       gaze_angle_x, gaze_angle_y, gaze_angle,
│       head_pitch, head_yaw, head_roll,
│       head_translation_x, head_translation_y, head_translation_z
│
├── session_logs/
│   ├── session_{session_id}.json (per lecture/activity)
│   └── global_session_{session_id}.json (complete session)
│       {
│         "session_id": "...",
│         "student_id": "...",
│         "login_time": "...",
│         "logout_time": "...",
│         "total_duration_min": 125.5,
│         "activities": [
│           {
│             "type": "lecture",
│             "lecture_id": "...",
│             "start_time": "...",
│             "duration_min": 45,
│             "engagement_score": 78.5,
│             "violations": {...}
│           },
│           ...
│         ],
│         "summary": {
│           "lectures_watched": 2,
│           "quizzes_taken": 1,
│           "materials_read": 3,
│           "avg_engagement": 75.2,
│           "total_violations": 5,
│           "integrity_score": 85
│         }
│       }
│
├── activity_logs/
│   ├── behavioral_log_{student_id}_{month}.csv
│   │   timestamp, event_type, details, session_id, lecture_id
│   │
│   └── activity_summary_{student_id}_{month}.csv
│       session_id, date, login_time, logout_time, total_duration_min,
│       lectures_watched, quizzes_taken, materials_read, 
│       time_on_lectures_min, time_on_quizzes_min, time_on_materials_min,
│       avg_lecture_engagement, avg_quiz_score, total_violations,
│       overall_integrity_score
│
├── quiz_logs/
│   ├── quiz_session_{session_id}.json
│   │   {
│   │     "quiz_id": "...",
│   │     "student_id": "...",
│   │     "start_time": "...",
│   │     "end_time": "...",
│   │     "duration_seconds": 180,
│   │     "questions": [
│   │       {
│   │         "question_id": "q1",
│   │         "answer": "B",
│   │         "time_spent_seconds": 45,
│   │         "timestamp": "..."
│   │       },
│   │       ...
│   │     ],
│   │     "violations": {
│   │       "tab_switches": 2,
│   │       "focus_losses": 3,
│   │       "copy_paste_attempts": 0,
│   │       "low_engagement_events": 1,
│   │       "multiple_faces_detected": 0
│   │     },
│   │     "score": 85.0,
│   │     "integrity_score": 78,
│   │     "flagged_for_review": false
│   │   }
│   │
│   └── quiz_violations_{student_id}_{month}.csv
│       timestamp, quiz_id, violation_type, details, penalty
│
└── captured_frames/
    └── {session_id}_{timestamp}.jpg
        + metadata.json (engagement_score, face_detected, etc.)
```

---

## 🎯 Engagement Score Calculation

### Step 1: Facial Features (Base Score)
```
┌─────────────────────────────────────┐
│  OpenFace Feature Extraction        │
│  Input: Webcam frame                │
│  Output: 50+ features               │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Apply Personalized Calibration     │
│  - Adjust gaze threshold            │
│  - Adjust head pose ranges          │
│  - Adjust blink rate expectations   │
│  - Adjust AU baselines              │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Compute Sub-Scores:                │
│  - Gaze Score (0-1)                 │
│  - Head Pose Score (0-1)            │
│  - Attention AUs Score (0-1)        │
│  - Blink Rate Score (0-1)           │
│  - Expression Score (0-1)           │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Weighted Combination:              │
│  facial_score = (                   │
│    gaze × 0.30 +                    │
│    head_pose × 0.25 +               │
│    attention × 0.25 +               │
│    blink × 0.10 +                   │
│    expression × 0.10                │
│  ) × 100                            │
└─────────────┬───────────────────────┘
              ↓
        Facial Score (0-100)
```

### Step 2: Behavioral Signals
```
┌─────────────────────────────────────┐
│  Track Activities (last 60s):      │
│  - Keystrokes per minute            │
│  - Mouse events per minute          │
│  - Scroll events per minute         │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Normalize to 0-1 scale:            │
│  - Keyboard: activity / 60          │
│  - Mouse: activity / 100            │
│  - Scroll: activity / 20            │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Weighted Combination:              │
│  behavioral_score = (               │
│    keyboard × 0.40 +                │
│    mouse × 0.35 +                   │
│    scroll × 0.25                    │
│  ) × 100                            │
└─────────────┬───────────────────────┘
              ↓
        Behavioral Score (0-100)
```

### Step 3: Interaction Tracking
```
┌─────────────────────────────────────┐
│  Track Interactions (last 2min):   │
│  - Quiz answers                     │
│  - Notes taken                      │
│  - Video seeks                      │
│  - Pause/play events                │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Score Based on Type:               │
│  - Quiz answer: +0.4 per answer     │
│  - Note taken: +0.3 per note        │
│  - Appropriate seeks: +0.2          │
└─────────────┬───────────────────────┘
              ↓
        Interaction Score (0-100)
```

### Step 4: Temporal Consistency
```
┌─────────────────────────────────────┐
│  Engagement History (last 10 frames)│
│  Calculate mean and variance        │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Consistency Bonus:                 │
│  - Low variance = more consistent   │
│  - Apply to mean score              │
└─────────────┬───────────────────────┘
              ↓
        Temporal Score (0-100)
```

### Step 5: Final Combination
```
┌─────────────────────────────────────┐
│  Activity-Specific Weights:         │
│                                     │
│  LECTURE:                           │
│    final = facial×0.50 +            │
│            behavioral×0.25 +        │
│            interaction×0.15 +       │
│            temporal×0.10            │
│                                     │
│  QUIZ:                              │
│    final = facial×0.35 +            │
│            behavioral×0.15 +        │
│            interaction×0.40 +       │
│            temporal×0.10            │
│                                     │
│  READING:                           │
│    final = facial×0.30 +            │
│            behavioral×0.45 +        │
│            interaction×0.15 +       │
│            temporal×0.10            │
└─────────────┬───────────────────────┘
              ↓
    Final Engagement Score (0-100)
    + Confidence Level (0-100)
    + Breakdown by Modality
```

---

## 🔐 Integrity Score Calculation

```
Start with Base Score: 100
    ↓
For each violation type:
    ↓
    Tab Switch: -5 points each
    Focus Loss: -2 points each
    Copy/Paste: -10 points each
    Low Engagement Event: -3 points each
    Multiple Faces: -15 points each
    Playback Speed Violation: -5 points each
    ↓
integrity_score = max(0, 100 - total_penalties)
    ↓
if integrity_score < 50:
    flag_for_review = True
    ↓
if integrity_score < 20:
    auto_fail = True
```

---

**Complete system architecture ready!** 🏗️
