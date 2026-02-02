# Intelligent Engagement Tracking System

## Overview

The Smart LMS now features an **intelligent engagement scoring system** that uses machine learning to understand user behavior patterns and assign engagement scores based on **ALL user actions**, not just specific events.

## Key Features

### ✨ Universal Activity Tracking
- **Logs EVERYTHING**: Every click, scroll, page view, download, upload
- **Context-Aware**: Captures full context (course, lecture, resource, timing)
- **Sequential Analysis**: Understands action patterns and sequences
- **Multi-Format Storage**: JSON (quick access) + CSV (ML training)

### 🤖 Intelligent ML-Based Scoring
- **Pattern Recognition**: Learns from behavior, not fixed rules
- **Adaptive**: Understands different learning styles
- **Offline-Aware**: Detects downloads and infers offline engagement
- **Quality Focus**: Measures interaction quality, not just quantity

### 🎯 Handles All Scenarios

#### Scenario 1: Student Downloads PDF
```
Student downloads PDF → Goes offline → Returns → Takes quiz (85%)
System Inference: "Downloaded for offline study, good performance"
Engagement Score: 86/100 ✅
```

#### Scenario 2: Student Reads Online
```
Student reads 10 pages → Interactive zooms → Watches video → Quiz (92%)
System Detection: "Rich online engagement with diverse actions"
Engagement Score: 99/100 ⭐
```

#### Scenario 3: Distracted Student
```
Student opens PDF → Tab switches (2x) → Quick skim → Poor quiz (45%)
System Detection: "Multiple distractions, superficial engagement"
Engagement Score: Lower (reflects quality)
```

#### Scenario 4: Teacher Activity
```
Teacher uploads content → Creates quiz → Monitors analytics
System Tracking: "Active teaching presence and content creation"
Activity Score: Measured independently
```

## Architecture

### Components

1. **Universal Activity Logger** (`services/universal_logger.py`)
   - Logs all user actions
   - Calculates sequence features
   - Maintains session tracking
   - Multi-format persistence

2. **Intelligent Scorer** (`services/intelligent_scorer.py`)
   - 50+ behavioral features
   - ML model (GradientBoosting)
   - Rule-based fallback
   - Confidence scoring

3. **Feature Extractor**
   - Temporal patterns (timing, regularity)
   - Action diversity and sequences
   - Content engagement (PDF, video, assessment)
   - Quality metrics (distractions, focus)
   - Persistence indicators

## Features Extracted

### Temporal Features
- `avg_time_between_actions`: Average gap between actions
- `session_duration`: Total time in session
- `actions_per_minute`: Activity rate
- `studies_morning/afternoon/evening/night`: Time preferences
- `weekend_activity_ratio`: Weekend vs weekday patterns

### Content Engagement
- `pdf_downloaded`: Whether PDF was downloaded
- `pdf_viewed_online`: Whether read in browser
- `returned_after_download`: Came back after downloading
- `post_download_activity_count`: Actions after download
- `video_completions`: Videos watched fully
- `video_pauses/seeks`: Interaction quality

### Interaction Quality
- `action_type_diversity`: Variety of actions
- `unique_resources_accessed`: Coverage breadth
- `tab_switches`: Distraction count
- `focus_loss_ratio`: Attention metric
- `window_blurs`: Tab/window switching

### Assessment Performance
- `avg_assessment_score`: Quiz/assignment scores
- `assessment_completion_rate`: Completion ratio
- `assessment_count`: Number attempted

### Persistence Indicators
- `unique_sessions`: Number of study sessions
- `active_days`: Days with activity
- `session_regularity`: Consistency metric
- `has_completed_assessment`: Goal completion

## Data Storage

### Locations
```
ml_data/
├── activity_logs/
│   ├── actions_student_001.json          # Quick access
│   ├── actions_student_001_202601.csv    # ML training
│   ├── session_summary_student_001.json  # Aggregated stats
│   └── session_student_001.json          # Current session
```

### File Formats

**JSON (Quick Access)**
```json
{
  "timestamp": "2026-01-30T14:23:45",
  "user_id": "student_001",
  "action_type": "pdf_download",
  "action_category": "content_download",
  "context": {
    "course_id": "CS101",
    "lecture_id": "lecture_001",
    "resource_id": "pdf_intro"
  },
  "metadata": {
    "file_size_bytes": 5242880
  },
  "sequence_features": {
    "actions_in_last_5min": 3,
    "time_since_last_action": 45
  }
}
```

**CSV (ML Training)**
```csv
timestamp,user_id,action_type,action_category,course_id,lecture_id,resource_id,duration_seconds,...
2026-01-30T14:23:45,student_001,pdf_download,content_download,CS101,lecture_001,pdf_intro,0,...
```

## Integration with Streamlit

### Quick Start

```python
from services.universal_logger import get_activity_logger, log_pdf_action, log_download
from services.intelligent_scorer import get_intelligent_scorer

# 1. Log any action
logger = get_activity_logger()
logger.log_action(
    user_id=st.session_state.user['id'],
    user_role='student',
    action_type='pdf_open',
    context={'course_id': 'CS101', 'lecture_id': 'lec1'},
    metadata={'page': 1}
)

# 2. Use convenience functions
log_pdf_action(user_id, 'pdf_page_turn', course_id, lecture_id, material_id, page=5, duration=120)
log_download(user_id, 'pdf', course_id, lecture_id, material_id, file_size=5242880)

# 3. Calculate engagement score
scorer = get_intelligent_scorer()
actions = logger._get_recent_actions(user_id, limit=1000)
result = scorer.predict_engagement_score(actions, context)

print(f"Score: {result['engagement_score']}/100")
print(f"Level: {result['level']}")
print(f"Confidence: {result['confidence']}")
print(f"Explanation: {result['explanation']}")
```

### Integration Points

**In Lectures Page:**
```python
# When student views lecture
logger.log_action(user_id, 'student', 'lecture_enter', ...)

# When student downloads PDF
log_download(user_id, 'pdf', course_id, lecture_id, material_id, file_size)

# When student opens PDF reader
log_pdf_action(user_id, 'pdf_open', course_id, lecture_id, material_id)

# When student turns page
log_pdf_action(user_id, 'pdf_page_turn', course_id, lecture_id, material_id, page=n)
```

**In Quiz Page:**
```python
# Quiz start
log_assessment(user_id, 'quiz_start', course_id, lecture_id, quiz_id)

# Quiz submit
log_assessment(user_id, 'quiz_submit', course_id, lecture_id, quiz_id, score=85, duration=360)
```

**In Analytics Dashboard:**
```python
# Get comprehensive engagement
actions = logger._get_recent_actions(user_id)
result = scorer.predict_engagement_score(actions, context)

st.metric("Engagement Score", f"{result['engagement_score']}/100")
st.info(result['explanation'])
```

## How It Works

### 1. Action Logging
Every user action is captured with:
- Full timestamp and context
- Sequential features (what came before)
- Session tracking (same session or new)
- Category classification

### 2. Feature Extraction
50+ features are extracted including:
- Temporal patterns
- Action diversity
- Content interaction quality
- Assessment performance
- Persistence metrics

### 3. Intelligent Scoring
ML model analyzes patterns to assign score:
- **Online reading**: High score for active interaction
- **Downloaded PDF**: Infers offline engagement from:
  - Download action
  - Return after reasonable time
  - Good assessment performance
  - Subsequent engagement
- **Distracted behavior**: Detects via:
  - Tab switching
  - Short interaction times
  - Poor assessment scores
  - Large time gaps

### 4. Explainable Results
Every score includes:
- Numerical score (0-100)
- Engagement level (Excellent/Good/Average/etc.)
- Confidence (0-1, based on data quality)
- Human-readable explanation
- Feature importance

## Demo Results

From `demo_intelligent_engagement.py`:

| Scenario | Actions | Score | Level |
|----------|---------|-------|-------|
| Offline Reader (Downloaded) | 6 | 86/100 | Excellent |
| Online Reader (Active) | 20 | 99/100 | Excellent |
| Distracted Student | 10 | Lower | Reflects quality |
| Teacher Activity | 5 | 60/100 | Average |

## Benefits

### For Students
- ✅ Fair scoring regardless of online/offline
- ✅ Recognizes different learning styles
- ✅ Downloads don't penalize engagement
- ✅ Quality over quantity

### For Teachers
- ✅ Accurate engagement insights
- ✅ Identifies truly struggling students
- ✅ Detects superficial vs deep engagement
- ✅ Tracks teaching activity

### For System
- ✅ Comprehensive data collection
- ✅ ML model improves over time
- ✅ Explainable AI (not black box)
- ✅ Privacy-conscious (no video/audio required)

## Model Training

The ML model can be retrained with accumulated data:

```python
from services.intelligent_scorer import get_intelligent_scorer

scorer = get_intelligent_scorer()
scorer.train_model_from_data("./ml_data/activity_logs")
scorer.save_model()
```

Training data comes from:
- Historical action logs (CSV files)
- Assessment scores (ground truth)
- Teacher feedback
- Student self-reports

## Privacy & Ethics

- ✅ No video/audio recording required
- ✅ Only behavioral actions logged (clicks, time, navigation)
- ✅ Data aggregated and anonymized for training
- ✅ Students can view their own data
- ✅ Transparent scoring with explanations
- ✅ GDPR compliant (data export/deletion)

## Next Steps

1. **Integration**: Add logger calls throughout Streamlit app
2. **Dashboard**: Create engagement visualization page
3. **Training**: Collect data and retrain ML model periodically
4. **Alerts**: Notify teachers of at-risk students
5. **Recommendations**: Use scores for adaptive learning

## Testing

Run the demonstration:
```bash
python demo_intelligent_engagement.py
```

Check logged data:
```bash
ls ml_data/activity_logs/
```

View session summaries:
```bash
cat ml_data/activity_logs/session_summary_student_001.json
```

---

**This is true intelligent engagement tracking - understanding behavior patterns, not just counting actions!** 🎓✨
