"""
Test Smart LMS - Quick Verification Script
Tests key components without running the full Streamlit app
"""

import os
import sys

print("🧪 Smart LMS - System Test\n")
print("=" * 50)

# Test 1: Check Python version
print("\n1️⃣ Checking Python version...")
print(f"   Python {sys.version}")
if sys.version_info >= (3, 8):
    print("   ✅ Python version OK")
else:
    print("   ❌ Python 3.8+ required")

# Test 2: Check required packages
print("\n2️⃣ Checking required packages...")
required_packages = {
    'streamlit': 'Streamlit',
    'cv2': 'OpenCV',
    'numpy': 'NumPy',
    'yaml': 'PyYAML',
    'plotly': 'Plotly'
}

all_packages_ok = True
for package, name in required_packages.items():
    try:
        __import__(package)
        print(f"   ✅ {name}")
    except ImportError:
        print(f"   ❌ {name} - Not installed")
        all_packages_ok = False

# Test 3: Check project structure
print("\n3️⃣ Checking project structure...")
required_dirs = ['app', 'services', 'storage', 'ml']
required_files = ['config.yaml', 'requirements.txt']

for dir_name in required_dirs:
    if os.path.exists(dir_name):
        print(f"   ✅ {dir_name}/ directory")
    else:
        print(f"   ❌ {dir_name}/ directory missing")

for file_name in required_files:
    if os.path.exists(file_name):
        print(f"   ✅ {file_name}")
    else:
        print(f"   ❌ {file_name} missing")

# Test 4: Check storage files
print("\n4️⃣ Checking storage files...")
storage_files = ['users.json', 'courses.json', 'lectures.json']

for file_name in storage_files:
    file_path = os.path.join('storage', file_name)
    if os.path.exists(file_path):
        print(f"   ✅ storage/{file_name}")
    else:
        print(f"   ⚠️  storage/{file_name} - Run scripts/init_storage.py")

# Test 5: Test services
print("\n5️⃣ Testing core services...")

try:
    from services.storage import get_storage
    storage = get_storage()
    print("   ✅ Storage service")
except Exception as e:
    print(f"   ❌ Storage service: {e}")

try:
    from services.auth import get_auth
    auth = get_auth()
    print("   ✅ Authentication service")
except Exception as e:
    print(f"   ❌ Authentication service: {e}")

try:
    from services.pdf_reader import get_pdf_reader
    pdf_reader = get_pdf_reader()
    print("   ✅ PDF reader service")
except Exception as e:
    print(f"   ❌ PDF reader service: {e}")

try:
    from services.comprehensive_engagement import get_engagement_calculator
    calc = get_engagement_calculator()
    print("   ✅ Comprehensive engagement calculator")
except Exception as e:
    print(f"   ❌ Comprehensive engagement calculator: {e}")

try:
    from services.gamification import GamificationService
    gamification = GamificationService("./storage")
    print("   ✅ Gamification service")
except Exception as e:
    print(f"   ❌ Gamification service: {e}")

try:
    from services.recommendations import RecommendationsService
    recommendations = RecommendationsService("./storage")
    print("   ✅ Recommendations service")
except Exception as e:
    print(f"   ❌ Recommendations service: {e}")

# Test 6: Test new features
print("\n6️⃣ Testing new features...")

try:
    # Test gamification
    profile = gamification.get_user_profile("test_user")
    print(f"   ✅ Gamification - User profile created")
except Exception as e:
    print(f"   ❌ Gamification test: {e}")

try:
    # Test recommendations
    learning_profile = recommendations.get_user_learning_profile("test_user")
    print(f"   ✅ Recommendations - Learning profile created")
except Exception as e:
    print(f"   ❌ Recommendations test: {e}")

# Final summary
print("\n" + "=" * 50)
print("\n📋 SUMMARY")
print("-" * 50)

if all_packages_ok:
    print("✅ All required packages installed")
else:
    print("❌ Some packages missing - Run: pip install -r requirements.txt")

if os.path.exists('storage/users.json'):
    print("✅ Storage initialized")
else:
    print("⚠️  Storage not initialized - Run: python scripts/init_storage.py")

print("\n🚀 TO START THE APPLICATION:")
print("   streamlit run app/streamlit_app.py")

print("\n📚 DEFAULT LOGIN CREDENTIALS:")
print("   Admin:    admin / admin123")
print("   Teacher:  dr_ramesh / teacher123")
print("   Student:  demo_student / student123")

print("\n" + "=" * 50)
print("\n✨ Test complete!\n")
