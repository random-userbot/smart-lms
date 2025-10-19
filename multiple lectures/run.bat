@echo off
echo 🚀 Starting Smart LMS...
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo 📦 Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt --quiet

REM Initialize storage if needed
if not exist "storage\users.json" (
    echo 🗄️  Initializing storage...
    python scripts\init_storage.py
)

REM Run Streamlit app
echo ✅ Launching Smart LMS...
echo.
streamlit run app\streamlit_app.py
