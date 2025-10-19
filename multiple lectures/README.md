# 🎓 Smart LMS - AI-Powered Learning Management System

An intelligent Learning Management System with real-time engagement tracking, NLP-based feedback analysis, and AI-powered teacher evaluation.

## ✨ Features

### 🔐 Core Features
- **Role-Based Access Control**: Admin, Teacher, and Student roles with secure authentication (bcrypt)
- **Course Management**: Upload lectures, PDFs, quizzes, and assignments
- **Video Lecture Player**: Integrated video player with event tracking
- **Quiz & Assignments**: Auto-graded quizzes with instant feedback
- **Engagement Tracking**: Real-time webcam-based engagement monitoring using MediaPipe/OpenFace
- **Attendance System**: Automated attendance based on face detection
- **NLP Feedback Analysis**: Sentiment analysis and bias correction using DistilBERT/VADER
- **Teacher Evaluation**: XGBoost/RandomForest model with SHAP explainability
- **Analytics Dashboard**: Comprehensive visualizations with Plotly
- **Progress Tracking**: Student performance monitoring over time
- **Teacher Activity Logs**: Track uploads, logins, and material updates
- **Ethical AI Dashboard**: Transparency, data control, and GDPR compliance

### 🎯 Optional Features (Extensible)
- Adaptive Recommendations
- Gamification (badges, leaderboards)
- Predictive Analytics
- Mobile Companion App

---

## 🏗️ Architecture

```
/smart-lms/
├── app/
│   ├── streamlit_app.py          # Main entry point
│   └── pages/
│       ├── student.py             # Student dashboard
│       ├── teacher.py             # Teacher dashboard
│       ├── admin.py               # Admin dashboard
│       ├── upload.py              # File upload interface
│       └── analytics.py           # Analytics & reports
├── services/
│   ├── storage.py                 # JSON storage (DB-ready)
│   ├── auth.py                    # Authentication & authorization
│   ├── engagement.py              # MediaPipe/OpenFace integration
│   ├── nlp.py                     # Sentiment analysis & bias correction
│   ├── evaluation.py              # Teacher evaluation model
│   └── logs.py                    # Event logging
├── ml/
│   ├── train_engagement.py        # Train engagement model
│   ├── train_evaluation.py        # Train teacher evaluation model
│   └── models/
│       ├── engagement_model.pkl
│       └── evaluation_model.pkl
├── storage/
│   ├── users.json                 # User accounts
│   ├── courses.json               # Course metadata
│   ├── lectures.json              # Lecture metadata
│   ├── engagement_logs.json       # Engagement data
│   ├── feedback.json              # Student feedback
│   ├── grades.json                # Quiz/assignment scores
│   ├── evaluation.json            # Teacher evaluation results
│   ├── attendance.json            # Attendance records
│   ├── teacher_activity.json      # Teacher activity logs
│   ├── progress.json              # Student progress tracking
│   └── courses/
│       └── {course_id}/
│           ├── lectures/*.mp4
│           └── materials/*.pdf
├── scripts/
│   └── init_storage.py            # Initialize storage with sample data
├── config.yaml                    # Configuration file
├── requirements.txt               # Python dependencies
├── run.bat / run.sh               # Launch scripts
└── README.md                      # This file
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- (Optional) OpenFace for offline engagement tracking

### Installation

#### Windows
```bash
# Clone or download the repository
cd "path\to\smart-lms"

# Run the application (auto-installs dependencies)
run.bat
```

#### Linux/Mac
```bash
# Clone or download the repository
cd path/to/smart-lms

# Make run script executable
chmod +x run.sh

# Run the application
./run.sh
```

#### Manual Installation
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize storage
python scripts/init_storage.py

# Run application
streamlit run app/streamlit_app.py
```

---

## 🔑 Default Credentials

After initialization, use these credentials to log in:

| Role | Username | Password |
|------|----------|----------|
| **Admin** | `admin` | `admin123` |
| **Teacher** | `dr_ramesh` | `teacher123` |
| **Teacher** | `dr_priya` | `teacher123` |
| **Student** | `demo_student` | `student123` |

⚠️ **Change these passwords in production!**

---

## 📖 User Guide

### For Students

1. **Login** with your student credentials
2. **Browse Courses** from your dashboard
3. **Watch Lectures** with webcam engagement tracking (consent required)
4. **Take Quizzes** and submit assignments
5. **Provide Feedback** after each lecture
6. **Track Progress** and view your engagement scores

### For Teachers

1. **Login** with your teacher credentials
2. **Manage Courses** and view enrolled students
3. **Upload Content** (lectures, PDFs, quizzes, assignments)
4. **View Analytics** for student engagement and performance
5. **Monitor Feedback** and sentiment analysis
6. **Track Your Evaluation** score and SHAP explanations

### For Admins

1. **Login** with admin credentials
2. **Manage Users** (create, edit, delete accounts)
3. **Manage Courses** and assign teachers
4. **View System Analytics** across all courses
5. **Teacher Evaluation** dashboard with SHAP explainability
6. **Ethical AI Dashboard** for transparency and data control

---

## 🎥 Engagement Tracking

### Real-Time Mode (MediaPipe)
- Lightweight, browser-based face tracking
- Extracts gaze direction, attention, head pose
- Computes engagement score (0-100) in real-time
- Privacy-first: only derived features stored

### Offline Mode (OpenFace)
- High-quality Action Unit (AU) extraction
- Precise gaze and head pose estimation
- Batch processing after lecture
- Requires OpenFace installation

**Configuration:** Edit `config.yaml` to switch modes:
```yaml
engagement:
  mode: "realtime"  # or "offline"
```

---

## 💬 NLP Feedback Analysis

### Sentiment Analysis
- **VADER**: Fast, rule-based sentiment analysis
- **DistilBERT**: Deep learning-based sentiment (more accurate)

### Bias Correction
- Controls for course difficulty and expected grades
- Residual-based or covariate adjustment
- Ensures fair teacher evaluation

**Configuration:** Edit `config.yaml`:
```yaml
nlp:
  sentiment_model: "vader"  # or "distilbert"
  bias_correction:
    enabled: true
    method: "residual"
```

---

## 🌲 Teacher Evaluation

### Features Used
- Average engagement score
- Average feedback sentiment
- Average quiz/assignment scores
- Upload frequency
- Login frequency
- Material update count
- Response time
- Attendance rate

### Models
- **XGBoost**: Gradient boosting (default)
- **RandomForest**: Ensemble learning

### Explainability
- SHAP values for feature importance
- Force plots and bar charts
- Downloadable reports (CSV, PDF)

**Configuration:** Edit `config.yaml`:
```yaml
evaluation:
  model: "xgboost"  # or "random_forest"
  shap:
    enabled: true
```

---

## 📊 Analytics Dashboard

### Available Charts
- Engagement time-series
- Sentiment distribution
- Quiz performance
- Attendance heatmap
- Teacher evaluation comparison
- Progress tracking

### Export Formats
- CSV (raw data)
- PDF (formatted reports)

---

## 🔒 Privacy & Security

### Security Features
- bcrypt password hashing (12 rounds)
- Session-based authentication
- Role-based access control
- Secure file storage

### Privacy Features
- Explicit webcam consent required
- Only derived features stored (not raw video)
- Data deletion on request (GDPR compliant)
- Anonymization after 180 days
- Transparent data collection policy

### Ethical AI Dashboard
- Shows what data is collected
- Model accuracy and confidence intervals
- Data deletion request button
- Privacy policy and terms of service

---

## ⚙️ Configuration

Edit `config.yaml` to customize:

```yaml
# Engagement tracking
engagement:
  mode: "realtime"  # or "offline"
  sampling_rate: 0.5  # seconds

# NLP
nlp:
  sentiment_model: "vader"  # or "distilbert"
  bias_correction:
    enabled: true

# Teacher evaluation
evaluation:
  model: "xgboost"  # or "random_forest"
  retrain_interval: 7  # days

# Privacy
privacy:
  require_consent: true
  store_raw_video: false
  data_retention_days: 365

# UI
ui:
  theme: "light"  # or "dark", "auto"
  layout: "wide"
```

---

## 🗄️ Database Migration

Currently using JSON files for storage. To migrate to PostgreSQL:

1. **Enable database in config.yaml:**
```yaml
database:
  enabled: true
  type: "postgresql"
  host: "localhost"
  port: 5432
  name: "smart_lms"
```

2. **Run migration script** (to be implemented):
```bash
python scripts/migrate_to_db.py
```

The `storage.py` interface is designed for easy migration - just swap the implementation!

---

## 🧪 Testing

### Run Unit Tests
```bash
pytest tests/
```

### Test Storage Interface
```bash
python tests/test_storage.py
```

### End-to-End Test
```bash
python tests/test_e2e.py
```

---

## 📦 Dependencies

### Core
- streamlit 1.29.0
- streamlit-webrtc 0.47.1
- bcrypt 4.1.2

### ML & AI
- scikit-learn 1.3.2
- xgboost 2.0.3
- transformers 4.36.2
- torch 2.1.2
- shap 0.44.0

### Computer Vision
- opencv-python 4.8.1.78
- mediapipe 0.10.9

### NLP
- vaderSentiment 3.3.2
- keybert 0.8.3
- sentence-transformers 2.2.2

### Visualization
- plotly 5.18.0
- matplotlib 3.8.2
- seaborn 0.13.0

See `requirements.txt` for complete list.

---

## 🐛 Troubleshooting

### Issue: "Module not found" error
**Solution:** Ensure virtual environment is activated and dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: Webcam not working
**Solution:** 
1. Grant browser camera permissions
2. Check `config.yaml` engagement settings
3. Try switching to offline mode

### Issue: Storage files not found
**Solution:** Run initialization script:
```bash
python scripts/init_storage.py
```

### Issue: Port already in use
**Solution:** Specify different port:
```bash
streamlit run app/streamlit_app.py --server.port 8502
```

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 📧 Contact

For questions or support:
- Email: support@smartlms.edu
- GitHub Issues: [Create an issue](https://github.com/yourusername/smart-lms/issues)

---

## 🎯 Roadmap

### Phase 1: Foundation ✅
- [x] Role-based authentication
- [x] JSON storage system
- [x] Basic dashboards

### Phase 2: Core Features (In Progress)
- [ ] File upload interface
- [ ] Quiz system
- [ ] Assignment submission

### Phase 3: Engagement Tracking
- [ ] MediaPipe integration
- [ ] OpenFace offline mode
- [ ] Engagement scoring algorithm

### Phase 4: NLP & Feedback
- [ ] Sentiment analysis
- [ ] Bias correction
- [ ] Feedback dashboard

### Phase 5: Teacher Evaluation
- [ ] Feature engineering
- [ ] XGBoost/RandomForest training
- [ ] SHAP explainability

### Phase 6: Optional Features
- [ ] Attendance tracking
- [ ] Progress tracking
- [ ] Teacher activity logs
- [ ] Ethical AI dashboard
- [ ] Adaptive recommendations
- [ ] Gamification
- [ ] Predictive analytics

---

## 🌟 Acknowledgments

- **MediaPipe** for real-time face tracking
- **OpenFace** for offline AU extraction
- **Hugging Face** for NLP models
- **SHAP** for model explainability
- **Streamlit** for the amazing framework

---

**Built with ❤️ for better education**

🎓 Smart LMS - Empowering educators and learners with AI
