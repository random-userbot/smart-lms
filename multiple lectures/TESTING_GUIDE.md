# 🧪 Smart LMS - Complete Testing Guide

**Last Updated:** October 20, 2025

---

## 📋 Quick Start

### **Step 1: Install Dependencies**

```bash
# Navigate to project directory
cd "c:\Users\revan\Downloads\multiple lectures\multiple lectures"

# Install all dependencies
pip install -r requirements.txt
```

### **Step 2: Initialize Storage**

```bash
# Create storage structure and sample data
python scripts\init_storage.py
```

**What this does:**
- ✅ Creates `storage/` directory structure
- ✅ Creates JSON files (users, courses, lectures, etc.)
- ✅ Hashes passwords with bcrypt
- ✅ Creates sample users (admin, teachers, students)
- ✅ Creates 3 sample courses
- ✅ Creates 5 sample lectures
- ✅ Organizes video files

### **Step 3: Run the Application**

```bash
# Start Streamlit server
streamlit run app\streamlit_app.py
```

**Access:** http://localhost:8501

---

## 👥 Test Accounts

| Role | Username | Password | Purpose |
|------|----------|----------|---------|
| **Admin** | `admin` | `admin123` | System management, view all analytics |
| **Teacher 1** | `dr_ramesh` | `teacher123` | Upload content, view student analytics |
| **Teacher 2** | `dr_priya` | `teacher123` | Alternative teacher account |
| **Student** | `demo_student` | `student123` | Watch lectures, take quizzes |
| **Student (from CSV)** | `11` | `11` | Migrated from old system |

---

## 🧪 Testing Scenarios

### **Scenario 1: Admin Workflow** (5 minutes)

```
1. Login
   - Username: admin
   - Password: admin123

2. View Dashboard
   ✓ See total users count
   ✓ See students count
   ✓ See teachers count
   ✓ See courses count

3. Try Dark Mode
   ✓ Click "🌙 Dark Mode" in sidebar
   ✓ Verify theme changes
   ✓ Click "☀️ Light Mode" to switch back

4. Navigate Pages
   ✓ Click "👥 Manage Users"
   ✓ Click "📚 Manage Courses"
   ✓ Click "📈 Analytics"
   ✓ Click "🌲 Teacher Evaluation"

5. Logout
   ✓ Click "🚪 Logout"
```

---

### **Scenario 2: Teacher Workflow** (10 minutes)

```
1. Login
   - Username: dr_ramesh
   - Password: teacher123

2. View Dashboard
   ✓ See "My Courses" section
   ✓ See enrolled students count
   ✓ See total lectures count

3. Upload Lecture Video
   ✓ Click "📤 Upload Content"
   ✓ Go to "🎥 Upload Lecture" tab
   ✓ Select course: "Computer Vision"
   ✓ Enter title: "Test Lecture"
   ✓ Enter description
   ✓ Upload video file (or skip if no file)
   ✓ Set duration: 60 minutes
   ✓ Click "📤 Upload Lecture"

4. Upload Course Material
   ✓ Go to "📄 Upload Materials" tab
   ✓ Select course
   ✓ Enter material title
   ✓ Upload PDF file (or skip)
   ✓ Click "📤 Upload Material"

5. Create Quiz
   ✓ Go to "📝 Create Quiz" tab
   ✓ Select course and lecture
   ✓ Enter quiz title
   ✓ Set time limit: 30 minutes
   ✓ Add 3-5 questions (MCQ or True/False)
   ✓ Set correct answers
   ✓ Click "✅ Create Quiz"

6. Create Assignment
   ✓ Go to "📋 Create Assignment" tab
   ✓ Select course
   ✓ Enter assignment title and description
   ✓ Set due date
   ✓ Set max score: 100
   ✓ Click "✅ Create Assignment"

7. View Analytics
   ✓ Click "📈 Analytics"
   ✓ View student engagement data

8. Check Attendance
   ✓ Click "📅 Attendance"
   ✓ Select a course
   ✓ View attendance by lecture

9. Logout
```

---

### **Scenario 3: Student Workflow** (15 minutes)

```
1. Login
   - Username: demo_student
   - Password: student123

2. View Dashboard
   ✓ See enrolled courses
   ✓ See average quiz score
   ✓ See average engagement

3. Browse Courses
   ✓ Click "📚 My Courses"
   ✓ View course list
   ✓ Click on a course card

4. Watch Lecture
   ✓ Click "🎥 Lectures"
   ✓ Select a course
   ✓ Click "▶️ Watch Now" on a lecture
   
   Webcam Consent:
   ✓ Read consent dialog
   ✓ Click "✅ I Consent" (or skip with "❌ Continue Without Webcam")
   
   Watch Video:
   ✓ Video plays in main area
   ✓ Webcam placeholder shows (if consented)
   ✓ Engagement score displays
   
   Submit Feedback:
   ✓ Scroll down to feedback section
   ✓ Rate the lecture (1-5 stars)
   ✓ Write feedback text
   ✓ Click "📤 Submit Feedback"

5. Take Quiz
   ✓ Click "📝 Quizzes"
   ✓ Find an available quiz
   ✓ Click "▶️ Start Quiz"
   ✓ Read instructions
   ✓ Click "▶️ Start Quiz" again
   ✓ Answer all questions
   ✓ Click "✅ Submit Quiz"
   ✓ View results (score, percentage, grade)

6. Submit Assignment
   ✓ Click "📋 Assignments"
   ✓ Find an assignment
   ✓ Click "📤 Submit Assignment"
   ✓ Upload a file (PDF, DOCX, etc.)
   ✓ Add comments (optional)
   ✓ Click "📤 Submit Assignment"

7. View Progress
   ✓ Click "📈 My Progress"
   ✓ View overall statistics
   ✓ See engagement trend chart
   ✓ See quiz performance chart
   ✓ Click "📊 View Detailed Progress" for a course
   ✓ View lecture-by-lecture breakdown

8. Check Attendance
   ✓ Click "📅 Attendance" (if available in nav)
   ✓ View attendance records
   ✓ See attendance rate
   ✓ View course-by-course breakdown

9. Try Dark Mode
   ✓ Toggle between light and dark themes
   ✓ Verify all pages look good in both modes

10. Logout
```

---

## 🤖 Training ML Models

### **Model 1: Engagement Classification Model**

**Purpose:** Classify student engagement levels (Engaged, Confused, Distracted, Bored, Not Engaged)

**Train the model:**

```bash
# Train engagement model
python ml\train_engagement_model.py
```

**What happens:**
1. Loads data from `data_archive/` (or generates sample data)
2. Trains RandomForest and XGBoost classifiers
3. Evaluates models on test set
4. Saves models to `ml/models/`
5. Generates confusion matrix plot

**Output files:**
- `ml/models/random_forest_engagement_model.pkl`
- `ml/models/xgboost_engagement_model.pkl`
- `ml/models/label_encoder.pkl`
- `ml/models/confusion_matrix_xgboost.png`

**Expected accuracy:** 85-95% (on balanced data)

---

### **Model 2: Teacher Evaluation Model**

**Purpose:** Predict teacher evaluation scores (0-100) based on multiple features

**Train the model:**

```bash
# Train evaluation model
python ml\train_evaluation_model.py
```

**What happens:**
1. Generates sample teacher data (100 teachers)
2. Trains RandomForest and XGBoost regressors
3. Evaluates models (MSE, MAE, R²)
4. Saves models to `ml/models/`
5. Generates prediction plots and feature importance

**Output files:**
- `ml/models/evaluation_random_forest.pkl`
- `ml/models/evaluation_xgboost.pkl`
- `ml/models/evaluation_features.pkl`
- `ml/models/predictions_xgboost.png`
- `ml/models/feature_importance.png`

**Expected R² score:** 0.90-0.95

---

## 📊 Testing ML Features

### **Test Engagement Tracking**

```bash
1. Login as student
2. Watch a lecture
3. Accept webcam consent
4. Engagement service will:
   - Track face presence
   - Compute gaze score
   - Calculate attention score
   - Monitor head pose
   - Detect blinks
5. After lecture, engagement score is saved
6. View in "My Progress" page
```

**Note:** Real-time webcam tracking requires MediaPipe. For now, engagement scores are simulated.

---

### **Test Teacher Evaluation**

```bash
1. Ensure models are trained (run train_evaluation_model.py)
2. Login as admin
3. Navigate to "🌲 Teacher Evaluation"
4. View teacher scores
5. Click on a teacher to see:
   - Overall score (0-100)
   - Grade (A-F)
   - Feature breakdown
   - SHAP explanations (if available)
```

**Evaluation features:**
- Average engagement score
- Average feedback sentiment
- Average quiz score
- Average assignment score
- Feedback count
- Upload frequency
- Material updates
- Login frequency
- Response time
- Attendance rate

---

## 🔍 Verification Checklist

### **Storage Verification**

```bash
# Check if storage files exist
dir storage

# Should see:
# - users.json
# - courses.json
# - lectures.json
# - engagement_logs.json
# - feedback.json
# - grades.json
# - evaluation.json
# - attendance.json
# - teacher_activity.json
# - progress.json
```

### **Model Verification**

```bash
# Check if models exist
dir ml\models

# Should see:
# - random_forest_engagement_model.pkl
# - xgboost_engagement_model.pkl
# - label_encoder.pkl
# - evaluation_random_forest.pkl
# - evaluation_xgboost.pkl
# - evaluation_features.pkl
```

### **Feature Verification**

**Core Features:**
- [x] Login/Register
- [x] Role-based access
- [x] Course management
- [x] Lecture upload
- [x] Quiz creation
- [x] Assignment creation
- [x] Lecture watching
- [x] Quiz taking
- [x] Assignment submission
- [x] Feedback collection

**AI Features:**
- [x] Engagement tracking (backend)
- [x] Sentiment analysis
- [x] Teacher evaluation
- [x] SHAP explainability

**UI Features:**
- [x] Light/Dark mode toggle
- [x] Modern styling
- [x] Progress tracking
- [x] Attendance tracking
- [x] Interactive charts

---

## 🐛 Common Issues & Solutions

### **Issue 1: Import Errors**

**Error:** `ModuleNotFoundError: No module named 'streamlit'`

**Solution:**
```bash
pip install -r requirements.txt
```

---

### **Issue 2: Storage Not Initialized**

**Error:** `FileNotFoundError: storage/users.json`

**Solution:**
```bash
python scripts\init_storage.py
```

---

### **Issue 3: Port Already in Use**

**Error:** `Address already in use`

**Solution:**
```bash
# Use different port
streamlit run app\streamlit_app.py --server.port 8502
```

---

### **Issue 4: Models Not Found**

**Error:** `FileNotFoundError: ml/models/evaluation_xgboost.pkl`

**Solution:**
```bash
# Train the models
python ml\train_engagement_model.py
python ml\train_evaluation_model.py
```

---

### **Issue 5: Video Files Not Found**

**Error:** `Video file not found`

**Solution:**
- Videos should be in `storage/courses/{course_id}/lectures/`
- Run `scripts\init_storage.py` to organize videos
- Or manually copy videos to the correct location

---

## 📈 Performance Testing

### **Load Testing**

```bash
# Test with multiple users (requires locust or similar)
# For now, test manually with multiple browser tabs

1. Open 3-5 browser tabs
2. Login with different accounts in each
3. Navigate simultaneously
4. Check for:
   - Response time
   - Memory usage
   - No crashes
```

### **Data Volume Testing**

```bash
# Test with large datasets
1. Create 100+ users
2. Create 50+ courses
3. Upload 200+ lectures
4. Generate 1000+ engagement logs
5. Check performance
```

---

## 🎯 Test Coverage

### **Functional Tests**

- [x] Authentication (login, register, logout)
- [x] Authorization (role-based access)
- [x] Course CRUD operations
- [x] Lecture CRUD operations
- [x] Quiz creation and taking
- [x] Assignment submission
- [x] Feedback collection
- [x] Progress tracking
- [x] Attendance tracking

### **ML Tests**

- [x] Engagement model training
- [x] Engagement prediction
- [x] Teacher evaluation training
- [x] Teacher evaluation prediction
- [x] SHAP explanations

### **UI Tests**

- [x] Theme toggle (light/dark)
- [x] Responsive layout
- [x] Navigation
- [x] Form submissions
- [x] File uploads
- [x] Chart rendering

---

## 📊 Expected Results

### **After Initialization:**
- 4 users created (1 admin, 2 teachers, 1 student)
- 3 courses created
- 5 lectures created
- All storage files exist

### **After Training Models:**
- Engagement model accuracy: 85-95%
- Evaluation model R²: 0.90-0.95
- All model files saved

### **After Testing:**
- All features working
- No errors in console
- Data persists across sessions
- Charts display correctly

---

## 🚀 Next Steps After Testing

1. **Add Real Data:**
   - Import actual student data
   - Upload real lecture videos
   - Create actual quizzes

2. **Fine-tune Models:**
   - Retrain with real data
   - Adjust hyperparameters
   - Improve accuracy

3. **Deploy:**
   - Set up production server
   - Configure database (PostgreSQL)
   - Set up SSL/HTTPS
   - Configure backups

4. **Monitor:**
   - Track usage metrics
   - Monitor performance
   - Collect user feedback
   - Fix bugs

---

## 📞 Support

If you encounter issues:

1. **Check logs:** Streamlit shows errors in browser
2. **Verify setup:** Run `python scripts\init_storage.py` again
3. **Check dependencies:** Run `pip install -r requirements.txt`
4. **Review documentation:** See README.md

---

## ✅ Testing Checklist

### **Before Testing:**
- [ ] Dependencies installed
- [ ] Storage initialized
- [ ] Models trained (optional)
- [ ] Videos organized

### **During Testing:**
- [ ] Test all user roles
- [ ] Test all features
- [ ] Test light/dark mode
- [ ] Test on different browsers
- [ ] Check for errors

### **After Testing:**
- [ ] Document bugs found
- [ ] Verify data persistence
- [ ] Check performance
- [ ] Review user experience

---

**Happy Testing!** 🎉

**Estimated Testing Time:** 30-45 minutes for complete workflow
