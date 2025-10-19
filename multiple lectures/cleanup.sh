#!/usr/bin/env bash
set -e

echo "🧹 Starting Smart LMS cleanup..."

# 1. Create new directory structure
echo "📁 Creating directory structure..."
mkdir -p legacy
mkdir -p data_archive
mkdir -p app/pages
mkdir -p services
mkdir -p ml/models
mkdir -p storage/courses
mkdir -p storage/assignments
mkdir -p storage/attendance

# 2. Archive legacy files
echo "📦 Archiving legacy files..."
if [ -f "app1.py" ]; then mv app1.py legacy/; fi
if [ -d "multiple" ]; then mv multiple legacy/; fi
if [ -f "model-trining.py" ]; then mv model-trining.py legacy/; fi
if [ -f "prediction.py" ]; then mv prediction.py legacy/; fi
if [ -f "engagement_model.pkl" ]; then mv engagement_model.pkl legacy/; fi

# 3. Archive Flask app and templates (keep for reference)
echo "📦 Archiving Flask app..."
if [ -f "app.py" ]; then cp app.py legacy/; fi
if [ -d "templates" ]; then cp -r templates legacy/; fi
if [ -d "static" ]; then cp -r static legacy/; fi

# 4. Remove redundant files
echo "🗑️  Removing redundant files..."
if [ -f "events.csv" ]; then rm events.csv; fi
if [ -f "realtime-data.csv" ]; then rm realtime-data.csv; fi
if [ -d "backend" ]; then rmdir backend 2>/dev/null || true; fi

# 5. Archive CSV data
echo "📊 Archiving CSV data..."
cp *.csv data_archive/ 2>/dev/null || true
cp *.pkl data_archive/ 2>/dev/null || true

# 6. Clean Python cache
echo "🧼 Cleaning Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# 7. Organize videos
echo "🎥 Organizing video files..."
if [ -d "static/videos" ]; then
    mkdir -p storage/courses/computer_vision/lectures
    mkdir -p storage/courses/cryptography/lectures
    mkdir -p storage/courses/data_science/lectures
    
    # Copy videos to organized structure
    if [ -f "static/videos/Lec_video.mp4" ]; then cp static/videos/Lec_video.mp4 storage/courses/computer_vision/lectures/; fi
    if [ -f "static/videos/CV_L2.mp4" ]; then cp static/videos/CV_L2.mp4 storage/courses/computer_vision/lectures/; fi
    if [ -f "static/videos/CNS_Lec_1.mp4" ]; then cp static/videos/CNS_Lec_1.mp4 storage/courses/cryptography/lectures/; fi
    if [ -f "static/videos/CNS_Lec_2.mp4" ]; then cp static/videos/CNS_Lec_2.mp4 storage/courses/cryptography/lectures/; fi
    if [ -f "static/videos/Lec_1.mp4" ]; then cp static/videos/Lec_1.mp4 storage/courses/data_science/lectures/; fi
fi

echo "✅ Cleanup complete!"
echo ""
echo "📋 Summary:"
echo "   - Legacy files moved to: ./legacy/"
echo "   - CSV data archived to: ./data_archive/"
echo "   - New structure created: ./app/, ./services/, ./ml/, ./storage/"
echo "   - Videos organized in: ./storage/courses/"
echo ""
echo "🚀 Ready for Smart LMS development!"
