# 🚀 Smart LMS - Quick Reference Card

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
