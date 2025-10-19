# 🧹 Smart LMS - Cleanup Instructions

## Files to Keep ✅

### Application Files (Keep)
```
✅ app/streamlit_app.py
✅ app/pages/upload.py
✅ app/pages/lectures.py
✅ app/pages/quizzes.py
✅ app/pages/assignments.py
```

### Services (Keep)
```
✅ services/storage.py
✅ services/auth.py
✅ services/engagement.py
✅ services/nlp.py
✅ services/evaluation.py
```

### Scripts (Keep)
```
✅ scripts/init_storage.py
```

### Configuration (Keep)
```
✅ config.yaml
✅ requirements.txt
✅ run.bat
✅ run.sh
```

### Documentation (Keep)
```
✅ README.md
✅ QUICKSTART.md
✅ IMPLEMENTATION_STATUS.md
✅ COMPLETION_SUMMARY.md
✅ analysis_report.md
✅ ARCHITECTURE_COMPARISON.md
✅ TRANSFORMATION_ROADMAP.md
✅ CLEANUP_CHECKLIST.md
✅ ANALYSIS_SUMMARY.md
```

### Storage (Keep - will be auto-created)
```
✅ storage/ (directory)
```

---

## Files to Archive 📦

### Legacy Flask Files (Move to legacy/)
```
📦 app.py
📦 app1.py
📦 balance.py
📦 label-engage.py
📦 model-trining.py
📦 prediction.py
📦 refine-data.py
📦 train-accu.py
```

### Legacy Directories (Move to legacy/)
```
📦 templates/
📦 static/
📦 multiple/
```

### Data Files (Move to data_archive/)
```
📦 *.csv (all CSV files)
📦 *.pkl (all PKL model files)
```

---

## Files to Delete 🗑️

### Redundant Files
```
🗑️ events.csv (small, redundant)
🗑️ realtime-data.csv (already refined)
🗑️ multiple.zip (345 MB backup)
```

### IDE/Cache Files
```
🗑️ __pycache__/ (all directories)
🗑️ .ipynb_checkpoints/ (all directories)
🗑️ *.pyc (all files)
🗑️ .idea/ (PyCharm)
🗑️ .vscode/ (VS Code)
🗑️ .git/ (already removed)
```

### Empty Directories
```
🗑️ backend/ (empty)
🗑️ .venv/ (if empty)
```

---

## Manual Cleanup Steps

### Step 1: Create Directories
```powershell
mkdir legacy, data_archive, storage\courses, storage\assignments -Force
```

### Step 2: Archive Legacy Files
```powershell
# Archive Python files
Move-Item app.py, app1.py, balance.py, label-engage.py, model-trining.py, prediction.py, refine-data.py, train-accu.py legacy\ -ErrorAction SilentlyContinue

# Archive directories
Move-Item templates, static, multiple legacy\ -ErrorAction SilentlyContinue
```

### Step 3: Archive Data Files
```powershell
# Archive CSV and PKL files
Move-Item *.csv data_archive\ -ErrorAction SilentlyContinue
Move-Item *.pkl data_archive\ -ErrorAction SilentlyContinue
```

### Step 4: Delete Redundant Files
```powershell
# Remove large zip
Remove-Item multiple.zip -Force -ErrorAction SilentlyContinue

# Remove empty directories
Remove-Item backend -Force -ErrorAction SilentlyContinue
```

### Step 5: Clean Python Cache
```powershell
# Remove __pycache__
Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force

# Remove .pyc files
Get-ChildItem -Recurse -File -Filter "*.pyc" | Remove-Item -Force
```

### Step 6: Clean IDE Files
```powershell
Remove-Item .idea, .vscode -Recurse -Force -ErrorAction SilentlyContinue
```

---

## Quick Cleanup (Copy-Paste)

```powershell
# Create directories
mkdir legacy, data_archive, storage\courses, storage\assignments -Force

# Archive legacy files
Move-Item app.py, app1.py, balance.py, label-engage.py, model-trining.py, prediction.py, refine-data.py, train-accu.py legacy\ -ErrorAction SilentlyContinue
Move-Item templates, static, multiple legacy\ -ErrorAction SilentlyContinue

# Archive data
Move-Item *.csv, *.pkl data_archive\ -ErrorAction SilentlyContinue

# Remove redundant
Remove-Item multiple.zip, backend -Recurse -Force -ErrorAction SilentlyContinue

# Clean cache
Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -Recurse -File -Filter "*.pyc" | Remove-Item -Force
Remove-Item .idea, .vscode -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "✅ Cleanup Complete!" -ForegroundColor Green
```

---

## Final Structure

After cleanup, your project should look like:

```
/smart-lms/
├── app/
│   ├── streamlit_app.py
│   └── pages/
│       ├── upload.py
│       ├── lectures.py
│       ├── quizzes.py
│       └── assignments.py
├── services/
│   ├── storage.py
│   ├── auth.py
│   ├── engagement.py
│   ├── nlp.py
│   └── evaluation.py
├── scripts/
│   └── init_storage.py
├── storage/              (auto-created)
├── ml/models/            (auto-created)
├── legacy/               (archived files)
├── data_archive/         (archived data)
├── config.yaml
├── requirements.txt
├── run.bat
├── run.sh
├── README.md
└── [other docs]
```

---

## Verification

After cleanup, verify:

1. ✅ All app/ files exist
2. ✅ All services/ files exist
3. ✅ config.yaml exists
4. ✅ requirements.txt exists
5. ✅ Legacy files in legacy/
6. ✅ Data files in data_archive/
7. ✅ No __pycache__ directories
8. ✅ No .idea or .vscode

---

## Next Steps

After cleanup:

```bash
# 1. Initialize storage
python scripts\init_storage.py

# 2. Run the app
streamlit run app\streamlit_app.py
```

---

**Total Space Saved:** ~350+ MB (multiple.zip + cache files)
