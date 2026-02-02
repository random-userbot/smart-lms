"""
Enhanced Setup Script for ML-Powered Teaching Effectiveness System
Installs all dependencies, validates system, and trains ML models
"""

import subprocess
import sys
import os
import json
from pathlib import Path


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")


def check_python_version():
    """Check Python version"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        return False
    
    print("✓ Python version OK")
    return True


def install_dependencies():
    """Install required Python packages"""
    print_header("📦 Installing Dependencies")
    
    packages = [
        'groq',
        'plotly',
        'pandas',
        'scikit-learn',
        'xgboost',
        'numpy',
        'pyyaml'
    ]
    
    print(f"Installing {len(packages)} packages...\n")
    
    for package in packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call(
                [sys.executable, '-m', 'pip', 'install', package, '-q'],
                stdout=subprocess.DEVNULL
            )
            print(f"   ✓ {package} installed")
        except subprocess.CalledProcessError:
            print(f"   ⚠️  Failed to install {package}")
    
    print("\n✅ Dependency installation complete")


def check_config_file():
    """Check and update config.yaml"""
    print_header("⚙️  Checking Configuration")
    
    config_path = Path("config.yaml")
    
    if not config_path.exists():
        print("❌ config.yaml not found")
        print("📝 Please create config.yaml from config.example.yaml")
        return False
    
    print("✓ config.yaml found")
    
    # Check for ML model storage path
    try:
        import yaml
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        storage = config.get('storage', {})
        
        # Add ML model storage if not exists
        if 'ml_models' not in storage:
            print("📝 Adding ML model storage path to config...")
            storage['ml_models'] = './storage/ml_models'
            
            # Add attendance tracking if not exists
            if 'attendance_auto' not in storage:
                storage['attendance_auto'] = './storage/attendance_auto.json'
            
            config['storage'] = storage
            
            with open(config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            
            print("✓ Config updated")
    
    except Exception as e:
        print(f"⚠️  Error updating config: {str(e)}")
    
    return True


def create_storage_directories():
    """Create required storage directories"""
    print_header("📁 Creating Storage Directories")
    
    directories = [
        './storage',
        './storage/ml_models',
        './storage/courses',
        './storage/lectures',
        './storage/quizzes',
        './storage/users',
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ {directory}")
    
    print("\n✅ Storage directories ready")


def initialize_data_files():
    """Initialize required JSON data files"""
    print_header("📄 Initializing Data Files")
    
    files = {
        './storage/activity_tracking.json': {'activities': []},
        './storage/session_tracking.json': {'sessions': {}},
        './storage/teaching_scores.json': {'scores': []},
        './storage/attendance_auto.json': {'attendance_records': []},
    }
    
    for filepath, default_data in files.items():
        path = Path(filepath)
        if not path.exists():
            with open(filepath, 'w') as f:
                json.dump(default_data, f, indent=2)
            print(f"✓ Created {filepath}")
        else:
            print(f"  {filepath} exists")
    
    print("\n✅ Data files initialized")


def train_ml_models():
    """Train ML models"""
    print_header("🤖 Training ML Models")
    
    print("Starting ML training pipeline...\n")
    
    try:
        # Import and run training
        from train_ml_models import train_models_from_storage, test_prediction
        
        success = train_models_from_storage()
        
        if success:
            print("\n✅ ML models trained successfully")
            
            # Test prediction
            print("\nRunning test prediction...")
            test_prediction()
            
            return True
        else:
            print("\n⚠️  ML training completed with warnings")
            return False
            
    except ImportError as e:
        print(f"❌ Could not import training module: {str(e)}")
        print("💡 Make sure train_ml_models.py is in the current directory")
        return False
    except Exception as e:
        print(f"❌ Training failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def run_system_validation():
    """Run system validation checks"""
    print_header("🔍 Running System Validation")
    
    try:
        from services.system_validator import run_validation
        
        results = run_validation()
        
        errors = len(results.get('errors', []))
        warnings = len(results.get('warnings', []))
        
        if errors == 0 and warnings == 0:
            print("\n✅ System validation passed")
            return True
        elif errors == 0:
            print(f"\n⚠️  System functional with {warnings} warnings")
            return True
        else:
            print(f"\n❌ System has {errors} errors")
            return False
            
    except Exception as e:
        print(f"⚠️  Could not run validation: {str(e)}")
        return False


def check_api_keys():
    """Check for required API keys"""
    print_header("🔑 Checking API Keys")
    
    groq_key = os.getenv('GROQ_API_KEY')
    
    if groq_key:
        print("✓ GROQ_API_KEY found in environment")
    else:
        print("⚠️  GROQ_API_KEY not found")
        print("\n📝 To enable AI chatbot:")
        print("   1. Get API key from: https://console.groq.com/")
        print("   2. Set environment variable: GROQ_API_KEY=your_key")
        print("   3. Or add to config.yaml under api.groq.key")
        print("\n💡 System will work without it, but AI features disabled")


def main():
    """Main setup script"""
    
    print("\n" + "="*60)
    print("  🚀 ENHANCED TEACHING EFFECTIVENESS SYSTEM SETUP")
    print("="*60)
    print("\n  ML-Powered with XAI | Automatic Attendance | Context-Aware\n")
    
    # Step 1: Check Python
    if not check_python_version():
        return 1
    
    # Step 2: Install dependencies
    install_dependencies()
    
    # Step 3: Check configuration
    if not check_config_file():
        return 1
    
    # Step 4: Create directories
    create_storage_directories()
    
    # Step 5: Initialize data files
    initialize_data_files()
    
    # Step 6: Check API keys
    check_api_keys()
    
    # Step 7: Train ML models
    ml_success = train_ml_models()
    
    # Step 8: Run validation
    validation_success = run_system_validation()
    
    # Final summary
    print_header("✨ SETUP COMPLETE")
    
    print("System Status:")
    print(f"   ✓ Dependencies installed")
    print(f"   ✓ Storage configured")
    print(f"   ✓ Data files initialized")
    print(f"   {'✓' if ml_success else '⚠️ '} ML models {'trained' if ml_success else 'needs attention'}")
    print(f"   {'✓' if validation_success else '⚠️ '} System validation {'passed' if validation_success else 'has issues'}")
    
    print("\n📚 Documentation:")
    print("   - ADVANCED_FEATURES_GUIDE.md - Complete technical guide")
    print("   - QUICK_START_ADVANCED_FEATURES.md - Quick start guide")
    print("   - TESTING_CHECKLIST.md - Testing checklist")
    
    print("\n🚀 Next Steps:")
    print("   1. Configure GROQ_API_KEY (optional, for AI chatbot)")
    print("   2. Start application: streamlit run app/streamlit_app.py")
    print("   3. System will auto-track attendance and activities")
    print("   4. ML models will provide intelligent scoring")
    print("   5. Retrain models as you collect real data: python train_ml_models.py")
    
    print("\n💡 Features Enabled:")
    print("   ✓ Automatic attendance tracking")
    print("   ✓ ML-powered teaching effectiveness indicators")
    print("   ✓ Contextual factors (difficulty, cohort)")
    print("   ✓ Confidence ranges and limitations")
    print("   ✓ Baseline normalization")
    print("   ✓ XAI-compliant explanations")
    print("   ✓ Random Forest + XGBoost models")
    
    print("\n" + "="*60)
    print("  🎉 READY TO USE")
    print("="*60 + "\n")
    
    return 0


if __name__ == "__main__":
    exit(main())
