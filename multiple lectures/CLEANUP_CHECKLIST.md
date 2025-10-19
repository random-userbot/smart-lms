# Smart LMS - Cleanup Checklist

**Before starting development, complete these cleanup tasks:**

---

## ✅ Phase 1: Backup & Safety

- [ ] Create backup of entire project folder
- [ ] Verify all CSV data is readable
- [ ] Export current models to safe location
- [ ] Commit current state to Git

```bash
# Backup command
cp -r "c:\Users\revan\Downloads\multiple lectures\multiple lectures" "c:\Users\revan\Downloads\multiple lectures\multiple lectures_backup_$(date +%Y%m%d)"
```

---

## ✅ Phase 2: Archive Legacy Files

Create `/legacy/` folder and move:

- [ ] `app1.py` → `legacy/app1.py`
- [ ] `multiple/` → `legacy/multiple/`
- [ ] `model-trining.py` → `legacy/model-trining.py`
- [ ] `prediction.py` → `legacy/prediction.py`
- [ ] `engagement_model.pkl` → `legacy/engagement_model.pkl`

```bash
mkdir legacy
mv app1.py legacy/
mv multiple legacy/
mv model-trining.py legacy/
mv prediction.py legacy/
mv engagement_model.pkl legacy/
```

---

## ✅ Phase 3: Remove Redundant Files

- [ ] Delete `events.csv` (redundant with events1.csv)
- [ ] Delete `realtime-data.csv` (already refined)
- [ ] Delete `multiple.zip` (345 MB backup - verify first!)
- [ ] Remove `backend/` (empty directory)

```bash
rm events.csv
rm realtime-data.csv
# rm multiple.zip  # Only after verification
rmdir backend
```

---

## ✅ Phase 4: Organize Data Files

Create `/data_archive/` for current CSVs:

- [ ] Move all CSV files to `data_archive/`
- [ ] Keep only essential CSVs in root during migration
- [ ] Document which CSVs map to which JSON files

```bash
mkdir data_archive
cp *.csv data_archive/  # Copy first, then decide what to keep
```

---

## ✅ Phase 5: Clean Python Cache

- [ ] Remove `__pycache__/` directories
- [ ] Remove `.ipynb_checkpoints/`
- [ ] Remove `*.pyc` files

```bash
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
```

---

## ✅ Phase 6: Reorganize Video Files

- [ ] Create `/storage/courses/` structure
- [ ] Move videos to appropriate course folders
- [ ] Update video paths in code

**Target structure:**
```
/storage/
  /courses/
    /computer_vision/
      /lectures/
        Lec_video.mp4
        CV_L2.mp4
    /cryptography/
      /lectures/
        CNS_Lec_1.mp4
        CNS_Lec_2.mp4
    /data_science/
      /lectures/
        Lec_1.mp4
```

---

## ✅ Phase 7: Security Fixes

- [ ] Hash passwords in `student_login.csv`
- [ ] Create `users.json` with bcrypt hashes
- [ ] Remove plaintext password CSV
- [ ] Generate secure secret key

**Script to hash passwords:**
```python
import bcrypt
import csv
import json

# Read plaintext passwords
users = {}
with open('student_login.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        user_id = row['StudentID']
        password = row['Password']
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        users[user_id] = {
            'username': user_id,
            'password_hash': hashed,
            'role': 'student'  # Default role
        }

# Save to JSON
with open('storage/users.json', 'w') as f:
    json.dump(users, f, indent=2)
```

---

## ✅ Phase 8: Create New Project Structure

- [ ] Create `/app/` directory
- [ ] Create `/app/pages/` directory
- [ ] Create `/services/` directory
- [ ] Create `/ml/` directory
- [ ] Create `/ml/models/` directory
- [ ] Create `/storage/` directory

```bash
mkdir -p app/pages
mkdir -p services
mkdir -p ml/models
mkdir -p storage/courses
```

---

## ✅ Phase 9: Documentation

- [ ] Create `README.md` with setup instructions
- [ ] Create `requirements.txt` with all dependencies
- [ ] Create `config.yaml` for configuration
- [ ] Create `run.sh` launch script

---

## ✅ Phase 10: Final Verification

- [ ] All legacy files archived
- [ ] No duplicate code in root
- [ ] Videos organized by course
- [ ] Passwords hashed
- [ ] New structure created
- [ ] Git commit of clean state

---

## Quick Cleanup Script

Save as `cleanup.sh`:

```bash
#!/usr/bin/env bash
set -e

echo "🧹 Starting Smart LMS cleanup..."

# 1. Create directories
echo "📁 Creating directory structure..."
mkdir -p legacy data_archive storage/courses app/pages services ml/models

# 2. Archive legacy files
echo "📦 Archiving legacy files..."
mv app1.py legacy/ 2>/dev/null || true
mv multiple legacy/ 2>/dev/null || true
mv model-trining.py legacy/ 2>/dev/null || true
mv prediction.py legacy/ 2>/dev/null || true
mv engagement_model.pkl legacy/ 2>/dev/null || true

# 3. Remove redundant files
echo "🗑️  Removing redundant files..."
rm -f events.csv
rm -f realtime-data.csv
rmdir backend 2>/dev/null || true

# 4. Clean Python cache
echo "🧼 Cleaning Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# 5. Archive CSV data
echo "📊 Archiving CSV data..."
cp *.csv data_archive/ 2>/dev/null || true

echo "✅ Cleanup complete!"
echo "📋 Next steps:"
echo "   1. Review analysis_report.md"
echo "   2. Run password hashing script"
echo "   3. Reorganize video files"
echo "   4. Begin Streamlit development"
```

---

## Estimated Time: 2-3 hours

**Priority:** HIGH - Must complete before development

**Status:** ⏳ Awaiting user confirmation

---

**Once cleanup is complete, proceed to Smart LMS development!** 🚀
