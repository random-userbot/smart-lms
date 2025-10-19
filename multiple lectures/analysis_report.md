# Smart LMS - Codebase Analysis Report

**Analysis Date:** October 20, 2025  
**Analyst:** Cascade AI  
**Project Location:** `c:\Users\revan\Downloads\multiple lectures\multiple lectures`

---

## Executive Summary

This is a **Flask-based Learning Management System (LMS)** with basic engagement tracking and ML-based student engagement prediction. The project has foundational features but requires significant refactoring and extension to meet the Smart LMS requirements (Streamlit, webcam engagement, NLP feedback analysis, teacher evaluation, etc.).

---

## 1. Current Project Structure

### 1.1 Application Entrypoints

| File | Type | Purpose | Status |
|------|------|---------|--------|
| `app.py` | **Primary Flask App** | Main LMS with login, lecture tracking, quiz, assignment submission | ✅ Active |
| `app1.py` | Flask App | Simpler version of app.py, appears to be an earlier iteration | ⚠️ Duplicate/Legacy |
| `multiple/app_updated_clickstream.py` | Flask App | Another variant in subdirectory | ⚠️ Duplicate/Legacy |

**Recommendation:** `app.py` is the most complete version. Remove `app1.py` and consolidate `multiple/` folder contents.

---

### 1.2 Machine Learning Scripts

| File | Purpose | Model Output | Status |
|------|---------|--------------|--------|
| `train-accu.py` | Trains RandomForest & XGBoost on engagement data | `random_forest_engagement_model.pkl`, `xgboost_engagement_model.pkl` | ✅ Working |
| `model-trining.py` | Rule-based labeling + RandomForest training | `engagement_model.pkl`, `label_encoder.pkl` | ⚠️ Typo in filename, older version |
| `prediction.py` | Loads labeled data and trains RandomForest | `engagement_model.pkl`, `label_encoder.pkl` | ⚠️ Duplicate functionality |
| `balance.py` | Generates synthetic balanced engagement dataset | `balanced_engagement_data.csv` | ✅ Useful for testing |
| `label-engage.py` | Rule-based engagement labeling | `labelled_data.csv` | ✅ Working |
| `refine-data.py` | Cleans and refines event logs | `refined_realtime_data.csv` | ✅ Working |

**Recommendation:** Keep `train-accu.py` (most advanced), `balance.py`, `label-engage.py`, and `refine-data.py`. Archive or delete duplicates.

---

### 1.3 Frontend Templates (Flask/Jinja2)

| File | Purpose | Features |
|------|---------|----------|
| `templates/login.html` | User login page | Basic form |
| `templates/register.html` | User registration | Basic form |
| `templates/index_clickstream.html` | Main student dashboard | Subject selection, video player, event logging (JS) |
| `templates/index.html` | Simpler dashboard | Legacy version |
| `templates/quiz.html` | Quiz submission form | Basic |
| `templates/assignment.html` | Assignment submission | Basic |

**Recommendation:** `index_clickstream.html` is the most advanced. Migrate its features to Streamlit.

---

### 1.4 Data Storage (CSV Files)

| File | Purpose | Size | Keep? |
|------|---------|------|-------|
| `student_login.csv` | User credentials (plaintext passwords ⚠️) | 245 bytes | ✅ Migrate to JSON with hashed passwords |
| `events1.csv` | Detailed event logs (378 KB) | 378 KB | ✅ Keep as historical data |
| `events.csv` | Smaller event log | 46 bytes | ❌ Redundant |
| `clickstream_logs.csv` | Clickstream data | 5 KB | ✅ Keep |
| `assignment_status.csv` | Assignment submissions | 55 bytes | ✅ Keep |
| `student_wise_summary.csv` | Aggregated student metrics | 8.7 KB | ✅ Keep for ML training |
| `labelled_data.csv` | Engagement-labeled data | 9.5 KB | ✅ Keep for ML |
| `balanced_engagement_data.csv` | Synthetic balanced dataset | 29.7 KB | ✅ Keep for testing |
| `realtime-data.csv` | Raw event data | 427 KB | ⚠️ Archive after refinement |
| `refined_realtime_data.csv` | Cleaned event data | 504 KB | ✅ Keep |
| `refined_student_metrics.csv` | Cleaned metrics | 645 bytes | ✅ Keep |
| `refined_clickstream.csv` | Cleaned clickstream | 814 bytes | ✅ Keep |
| `cleaned_labelled_data.csv` | Cleaned labels | 2.7 KB | ✅ Keep |
| `balanced_labelled_data.csv` | Balanced labels | 11.8 KB | ✅ Keep |

**Recommendation:** Consolidate CSVs into structured JSON files for the new Streamlit app. Archive raw/unrefined CSVs.

---

### 1.5 Trained Models

| File | Model Type | Size | Purpose |
|------|------------|------|---------|
| `random_forest_engagement_model.pkl` | RandomForest | 961 KB | Engagement prediction |
| `xgboost_engagement_model.pkl` | XGBoost | 488 KB | Engagement prediction |
| `engagement_model.pkl` | RandomForest | 73.6 KB | Older engagement model |
| `label_encoder.pkl` | LabelEncoder | 495 bytes | Encodes engagement labels |

**Recommendation:** Keep `random_forest_engagement_model.pkl` and `xgboost_engagement_model.pkl` (latest). Archive older `engagement_model.pkl`.

---

### 1.6 Static Assets

| Directory | Contents | Purpose |
|-----------|----------|---------|
| `static/videos/` | 5 lecture videos (CNS, CV, Data Science) | Total ~353 MB | ✅ Keep, organize by course |

**Recommendation:** Restructure to `/storage/courses/{course_id}/lectures/` format.

---

### 1.7 Dependencies (requirements.txt)

**Current dependencies:**
```
blinker==1.9.0
click==8.2.1
colorama==0.4.6
Flask==3.1.1
itsdangerous==2.2.0
Jinja2==3.1.6
MarkupSafe==3.0.2
Werkzeug==3.1.3
```

**Missing for Smart LMS:**
- Streamlit
- streamlit-webrtc (webcam)
- mediapipe (face tracking)
- transformers (NLP)
- shap (explainability)
- bcrypt (password hashing)
- plotly (charts)
- opencv-python
- pandas, scikit-learn, xgboost (already used but not listed)

**Recommendation:** Create comprehensive `requirements.txt` with all Smart LMS dependencies.

---

### 1.8 Virtual Environment & Git

| Item | Status | Notes |
|------|--------|-------|
| `.venv/` | ✅ Exists (empty) | Virtual environment folder |
| `.git/` | ✅ Exists (empty) | Git repository initialized |
| `.idea/` | ✅ Exists (empty) | PyCharm/IntelliJ project files |
| `backend/` | ⚠️ Empty directory | Unused |

**Recommendation:** Remove empty `backend/` directory. Keep `.venv/` and `.git/`.

---

### 1.9 Unnecessary/Legacy Files

**Files to Archive or Delete:**

1. **Duplicate Apps:**
   - `app1.py` (superseded by `app.py`)
   - `multiple/app_updated_clickstream.py` (consolidate into main app)

2. **Duplicate/Old Models:**
   - `engagement_model.pkl` (older version)
   - `model-trining.py` (typo, superseded by `train-accu.py`)
   - `prediction.py` (redundant with `train-accu.py`)

3. **Raw/Unrefined Data:**
   - `realtime-data.csv` (427 KB, already refined)
   - `events.csv` (46 bytes, redundant with `events1.csv`)

4. **Large Archive:**
   - `multiple.zip` (345 MB) - appears to be a backup, can be deleted after verification

5. **Empty Directories:**
   - `backend/`

6. **IDE/Cache Files:**
   - `__pycache__/` (if exists)
   - `.ipynb_checkpoints/` (if exists)

---

## 2. Current Features Analysis

### 2.1 Implemented Features ✅

1. **User Authentication:**
   - Login/Register with CSV-based storage
   - Session management
   - ⚠️ **Security Issue:** Passwords stored in plaintext

2. **Lecture Delivery:**
   - Video player with multiple subjects (CV, CNS, Data Science)
   - Event logging (play, pause, seek, tab switch)
   - JavaScript-based clickstream tracking

3. **Assessments:**
   - Quiz submission (score + duration tracking)
   - Assignment submission (with document links)

4. **Engagement Tracking:**
   - Event logs: play, pause, seek, tab switches, watch time
   - Rule-based engagement labeling (Engaged, Confused, Distracted, Bored, Not Engaged)

5. **Machine Learning:**
   - RandomForest and XGBoost models for engagement prediction
   - Feature engineering from clickstream data
   - Model persistence with joblib

### 2.2 Missing Features (Required for Smart LMS) ❌

1. **Role-Based Access Control:**
   - No Admin/Teacher/Student roles
   - No teacher dashboard or analytics

2. **Webcam Engagement:**
   - No real-time face tracking
   - No MediaPipe/OpenFace integration
   - No visual engagement scoring

3. **NLP & Feedback:**
   - No textual feedback collection
   - No sentiment analysis
   - No bias correction

4. **Teacher Evaluation:**
   - No teacher activity tracking
   - No evaluation model combining engagement + feedback + grades
   - No SHAP explainability

5. **Analytics Dashboard:**
   - No visualizations (charts, heatmaps)
   - No downloadable reports

6. **File Upload Management:**
   - No teacher upload interface for lectures/materials
   - No structured file storage system

7. **Privacy & Consent:**
   - No consent management
   - No data deletion features

---

## 3. Code Quality Assessment

### 3.1 Strengths ✅

- Clean Flask routing structure
- Good separation of event logging logic
- Functional ML pipeline (data → labeling → training → prediction)
- JavaScript event tracking is comprehensive

### 3.2 Weaknesses ⚠️

- **Security:** Plaintext passwords, hardcoded secret keys
- **Code Duplication:** Multiple app files with similar functionality
- **No Modularity:** All logic in single files, no service layer
- **No Tests:** No unit tests or validation scripts
- **Inconsistent Naming:** `model-trining.py` (typo), mixed naming conventions
- **No Documentation:** No README or inline comments
- **No Configuration:** Hardcoded paths and parameters

---

## 4. Migration Path to Smart LMS

### 4.1 Data Migration Strategy

**CSV → JSON Conversion:**

| Current CSV | New JSON File | Structure |
|-------------|---------------|-----------|
| `student_login.csv` | `users.json` | `{user_id: {username, password_hash, role, email, ...}}` |
| `events1.csv` | `engagement_logs.json` | `{log_id: {student_id, lecture_id, events: [...], score}}` |
| `assignment_status.csv` | `grades.json` | `{student_id: {assignments: [...], quizzes: [...]}}` |
| N/A (new) | `courses.json` | `{course_id: {name, teacher_id, lectures: [...]}}` |
| N/A (new) | `lectures.json` | `{lecture_id: {title, video_path, duration, ...}}` |
| N/A (new) | `feedback.json` | `{feedback_id: {student_id, lecture_id, text, rating, sentiment}}` |
| N/A (new) | `evaluation.json` | `{teacher_id: {score, features, shap_values, ...}}` |

**File Storage Restructure:**

```
/storage/
  /courses/
    /course_1/
      /lectures/
        lecture_1.mp4
        lecture_2.mp4
      /materials/
        notes.pdf
        slides.pdf
  /assignments/
    /course_1/
      student_1_assignment.pdf
  users.json
  courses.json
  lectures.json
  engagement_logs.json
  feedback.json
  grades.json
  evaluation.json
```

### 4.2 Code Refactoring Plan

**New Project Structure:**

```
/lms-root/
  /app/
    streamlit_app.py          # Main Streamlit entry
    /pages/
      student.py              # Student dashboard
      teacher.py              # Teacher dashboard
      admin.py                # Admin dashboard
      upload.py               # Upload interface
      analytics.py            # Analytics & reports
  /services/
    storage.py                # JSON file I/O (abstracted for DB migration)
    auth.py                   # bcrypt password hashing + role checks
    engagement.py             # MediaPipe/OpenFace + scoring
    nlp.py                    # Sentiment analysis + bias correction
    evaluation.py             # Teacher evaluation model
    logs.py                   # Event logging
  /ml/
    train_engagement.py       # Train engagement model
    train_evaluation.py       # Train teacher evaluation model
    /models/
      engagement_model.pth
      evaluation_model.pkl
  /storage/                   # As described above
  /legacy/                    # Archive old Flask app
    app.py
    templates/
    ...
  requirements.txt
  config.yaml
  run.sh
  cleanup.sh
  README.md
```

---

## 5. Recommended Cleanup Steps

### 5.1 Pre-Development Cleanup

**Step 1: Archive Legacy Code**
```bash
mkdir legacy
mv app1.py legacy/
mv multiple/ legacy/
mv model-trining.py legacy/
mv prediction.py legacy/
mv engagement_model.pkl legacy/
```

**Step 2: Remove Redundant Data**
```bash
rm events.csv
rm realtime-data.csv
rm multiple.zip  # After verification
rmdir backend
```

**Step 3: Organize Current Data**
```bash
mkdir data_archive
mv *.csv data_archive/  # Keep for reference
mv *.pkl data_archive/  # Keep models
```

**Step 4: Clean Python Cache**
```bash
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

### 5.2 Create Cleanup Script

Create `cleanup.sh`:
```bash
#!/usr/bin/env bash
echo "🧹 Cleaning up Smart LMS project..."

# Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete

# Remove empty directories
find . -type d -empty -delete

echo "✅ Cleanup complete!"
```

---

## 6. Risk Assessment

### 6.1 High Priority Risks ⚠️

1. **Security Vulnerability:** Plaintext passwords in `student_login.csv`
   - **Impact:** High
   - **Mitigation:** Immediate migration to bcrypt hashing

2. **No Backup Strategy:** Single copy of data in CSVs
   - **Impact:** High
   - **Mitigation:** Implement versioned backups before migration

3. **Large Video Files:** 353 MB in repo
   - **Impact:** Medium
   - **Mitigation:** Move to external storage or CDN

### 6.2 Medium Priority Risks

1. **Code Duplication:** Multiple app versions may cause confusion
2. **No Tests:** Refactoring without tests is risky
3. **Hardcoded Secrets:** `app.secret_key = 'your_secret_key'`

---

## 7. Estimated Effort

| Task | Estimated Time | Priority |
|------|----------------|----------|
| Cleanup & archive legacy code | 1 hour | High |
| Create new project structure | 2 hours | High |
| Migrate CSV → JSON | 3 hours | High |
| Implement Streamlit auth + routing | 4 hours | High |
| Build student/teacher/admin pages | 8 hours | High |
| Integrate MediaPipe webcam tracking | 6 hours | High |
| Implement NLP feedback analysis | 4 hours | Medium |
| Build teacher evaluation model | 5 hours | Medium |
| Create analytics dashboard | 6 hours | Medium |
| Add SHAP explainability | 3 hours | Medium |
| Testing & documentation | 4 hours | High |
| **Total** | **~46 hours** | |

---

## 8. Recommendations Summary

### 8.1 Immediate Actions (Before Coding)

1. ✅ **Archive legacy files** to `/legacy/` folder
2. ✅ **Remove duplicates** (app1.py, old models, redundant CSVs)
3. ✅ **Create cleanup.sh** script
4. ✅ **Backup current data** before any migration
5. ✅ **Hash existing passwords** in student_login.csv

### 8.2 Development Priorities

1. **Phase 1:** Core Streamlit app + role-based auth + file storage
2. **Phase 2:** Webcam engagement tracking (MediaPipe)
3. **Phase 3:** NLP feedback + bias correction
4. **Phase 4:** Teacher evaluation model + SHAP
5. **Phase 5:** Analytics dashboard + reports

### 8.3 Long-Term Considerations

- Plan database migration (Postgres) after JSON MVP is stable
- Implement CI/CD pipeline for testing
- Add comprehensive logging and monitoring
- Consider containerization (Docker) for deployment

---

## 9. Files Inventory

### Keep & Migrate ✅
- `app.py` (reference for features)
- `train-accu.py` (ML training)
- `balance.py` (test data generation)
- `label-engage.py` (engagement labeling)
- `refine-data.py` (data cleaning)
- `templates/index_clickstream.html` (event tracking logic)
- All refined CSV files (for historical data)
- Latest ML models (RF & XGBoost)
- Video files (reorganize)

### Archive 📦
- `app1.py`
- `multiple/` folder
- `model-trining.py`
- `prediction.py`
- `engagement_model.pkl` (old)
- Raw/unrefined CSVs

### Delete 🗑️
- `events.csv` (redundant)
- `multiple.zip` (after verification)
- `backend/` (empty)
- `__pycache__/` (if exists)

---

## 10. Next Steps

**Awaiting User Confirmation:**

1. ✅ Review this analysis report
2. ✅ Confirm cleanup actions
3. ✅ Approve project structure
4. ✅ Begin implementation

**Once approved, I will:**

1. Execute cleanup script
2. Create new project structure
3. Implement Streamlit app skeleton
4. Migrate data to JSON format
5. Build core features iteratively

---

## Appendix: Current Tech Stack

**Backend:**
- Flask 3.1.1
- Python (version not specified in requirements)

**Frontend:**
- Jinja2 templates
- Vanilla JavaScript (event tracking)
- Basic CSS

**ML/Data:**
- pandas
- scikit-learn (RandomForest)
- xgboost
- joblib (model persistence)

**Storage:**
- CSV files (plaintext)

**Missing (Required for Smart LMS):**
- Streamlit
- MediaPipe / OpenFace
- Transformers (NLP)
- SHAP (explainability)
- bcrypt (security)
- Plotly (visualization)

---

**End of Analysis Report**

*Generated by Cascade AI - Ready for Smart LMS transformation* 🚀
