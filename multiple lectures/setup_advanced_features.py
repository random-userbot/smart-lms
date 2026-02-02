"""
Setup Script for Advanced Features
Installs required dependencies and verifies configuration
"""

import subprocess
import sys
import os


def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing required dependencies...")
    
    packages = [
        "groq",      # AI chatbot (Grok via Groq API)
        "plotly",    # Interactive charts
        "pandas"     # Data manipulation
    ]
    
    for package in packages:
        print(f"   Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"   ✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to install {package}: {e}")
            return False
    
    return True


def check_config_file():
    """Check if config.yaml exists and has required settings"""
    print("\n📝 Checking configuration...")
    
    config_path = "config.yaml"
    
    if not os.path.exists(config_path):
        print(f"   ⚠️ Warning: {config_path} not found")
        print(f"   💡 Copy config.example.yaml to config.yaml and update settings")
        return False
    
    # Check for required storage paths
    with open(config_path, 'r') as f:
        content = f.read()
        
        required_settings = [
            "activity_tracking",
            "session_tracking",
            "teaching_scores"
        ]
        
        missing = []
        for setting in required_settings:
            if setting not in content:
                missing.append(setting)
        
        if missing:
            print(f"   ⚠️ Missing storage paths in config.yaml:")
            for item in missing:
                print(f"      - {item}")
            print(f"\n   💡 Add these paths to the storage section:")
            print(f"""
storage:
  activity_tracking: "./storage/activity_tracking.json"
  session_tracking: "./storage/session_tracking.json"
  teaching_scores: "./storage/teaching_scores.json"
  student_analytics: "./storage/student_analytics.json"
            """)
            return False
    
    print("   ✅ Config file looks good")
    return True


def check_api_keys():
    """Check if API keys are configured"""
    print("\n🔑 Checking API keys...")
    
    groq_key = os.getenv('GROQ_API_KEY')
    
    if groq_key:
        print(f"   ✅ GROQ_API_KEY found in environment")
        return True
    
    # Check config.yaml
    config_path = "config.yaml"
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            content = f.read()
            if 'groq:' in content and 'gsk_' in content:
                print(f"   ✅ GROQ_API_KEY found in config.yaml")
                return True
    
    print(f"   ⚠️ GROQ_API_KEY not found")
    print(f"\n   💡 To enable AI Chatbot:")
    print(f"   1. Get free API key: https://console.groq.com/keys")
    print(f"   2. Add to config.yaml:")
    print(f"      api_keys:")
    print(f"        groq: 'gsk_your_key_here'")
    print(f"   3. Or set environment variable:")
    print(f"      export GROQ_API_KEY='gsk_your_key_here'")
    
    return False


def create_storage_directories():
    """Create required storage directories"""
    print("\n📁 Creating storage directories...")
    
    directories = [
        "./storage",
        "./ml_data/activity_logs"
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"   ✅ {directory}")
        except Exception as e:
            print(f"   ❌ Failed to create {directory}: {e}")
            return False
    
    return True


def verify_files():
    """Verify that all required files are present"""
    print("\n📄 Verifying files...")
    
    required_files = [
        "services/activity_tracker.py",
        "services/teaching_score.py",
        "services/ai_explainer_bot.py",
        "app/pages/tracking.py",
        "app/pages/student_activity.py",
        "app/pages/analytics_dashboard.py"
    ]
    
    missing = []
    for file in required_files:
        if not os.path.exists(file):
            missing.append(file)
            print(f"   ❌ Missing: {file}")
        else:
            print(f"   ✅ {file}")
    
    if missing:
        print(f"\n   ⚠️ {len(missing)} file(s) missing")
        return False
    
    return True


def main():
    """Main setup function"""
    print("=" * 60)
    print("🚀 Smart LMS - Advanced Features Setup")
    print("=" * 60)
    
    # Check Python version
    print(f"\n🐍 Python version: {sys.version}")
    
    if sys.version_info < (3, 8):
        print("   ❌ Python 3.8 or higher required")
        return False
    
    print("   ✅ Python version OK")
    
    # Run setup steps
    steps = [
        ("Install Dependencies", install_dependencies),
        ("Create Storage Directories", create_storage_directories),
        ("Verify Files", verify_files),
        ("Check Configuration", check_config_file),
        ("Check API Keys", check_api_keys)
    ]
    
    results = []
    for step_name, step_func in steps:
        try:
            result = step_func()
            results.append((step_name, result))
        except Exception as e:
            print(f"\n   ❌ Error in {step_name}: {e}")
            results.append((step_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Setup Summary")
    print("=" * 60)
    
    for step_name, result in results:
        status = "✅" if result else "⚠️"
        print(f"{status} {step_name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n" + "=" * 60)
        print("🎉 Setup Complete!")
        print("=" * 60)
        print("\n✅ All checks passed!")
        print("\n🚀 You can now run the application:")
        print("   streamlit run app/streamlit_app.py")
        print("\n📚 Documentation:")
        print("   - ADVANCED_FEATURES_GUIDE.md")
        print("   - QUICK_START_ADVANCED_FEATURES.md")
        print("   - IMPLEMENTATION_SUMMARY.md")
    else:
        print("\n" + "=" * 60)
        print("⚠️ Setup Incomplete")
        print("=" * 60)
        print("\nSome checks failed. Please review the messages above.")
        print("The application may still work, but some features may be unavailable.")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
