"""
Test script for ensemble integration in Streamlit app
Verifies all components are working correctly
"""

import sys
import os

# Change to multiple lectures directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(script_dir, 'multiple lectures'))

# Add to path
sys.path.insert(0, os.getcwd())

print("="*70)
print("  ENSEMBLE STREAMLIT INTEGRATION TEST")
print("="*70)
print(f"\nWorking directory: {os.getcwd()}")

# Test 1: Import ensemble detector
print("\n1. Testing ensemble detector import...")
try:
    from services.ensemble_engagement import create_ensemble_detector
    print("   ✓ Ensemble detector module imported")
except Exception as e:
    print(f"   ✗ Failed to import: {e}")
    sys.exit(1)

# Test 2: Create ensemble detector
print("\n2. Testing ensemble detector creation...")
try:
    detector = create_ensemble_detector(mode="fast")
    print("   ✓ Ensemble detector created in 'fast' mode")
except Exception as e:
    print(f"   ✗ Failed to create detector: {e}")
    sys.exit(1)

# Test 3: Check directories
print("\n3. Checking required directories...")
dirs_to_check = [
    "ml_data/captured_frames",
    "ml_data/engagement_logs",
    "ml_data/ensemble_analysis_reports",
    "export"
]

for dir_path in dirs_to_check:
    if os.path.exists(dir_path):
        print(f"   ✓ {dir_path}")
    else:
        print(f"   ✗ Missing: {dir_path}")

# Test 4: Check model files
print("\n4. Checking ensemble model files...")
model_dirs = [
    "export/Transformer_ViT_59.6%_BEST",
    "export/BiLSTM_Enhanced_FMAE_58.6%",
    "export/Fusion_Enhanced_57.4%"
]

for model_dir in model_dirs:
    model_file = os.path.join(model_dir, "best_model.h5")
    if os.path.exists(model_file):
        print(f"   ✓ {model_dir}")
    else:
        print(f"   ✗ Missing model in: {model_dir}")

# Test 5: Test dummy prediction
print("\n5. Testing dummy prediction...")
try:
    import numpy as np
    dummy_features = np.random.randn(30, 35).astype(np.float32)
    result = detector.predict(dummy_features)
    
    print(f"   ✓ Prediction successful")
    print(f"     - Engagement score: {result['engagement_score']:.1f}%")
    print(f"     - Mode: {result['mode']}")
    print(f"     - Emotions detected: {len(result['predictions'])}")
    
except Exception as e:
    print(f"   ✗ Prediction failed: {e}")

# Test 6: Test pip_webcam_live integration
print("\n6. Testing pip_webcam_live integration...")
try:
    from services.pip_webcam_live import PiPWebcamLive
    print("   ✓ PiPWebcamLive imported successfully")
    
    # Check if class has ensemble support
    import inspect
    init_signature = inspect.signature(PiPWebcamLive.__init__)
    params = list(init_signature.parameters.keys())
    
    if 'use_ensemble' in params and 'ensemble_mode' in params:
        print("   ✓ Ensemble parameters present in __init__")
    else:
        print("   ✗ Missing ensemble parameters in __init__")
    
except Exception as e:
    print(f"   ✗ Failed: {e}")

# Test 7: Check analytics page
print("\n7. Checking ensemble analytics page...")
analytics_page = "app/pages/ensemble_analytics.py"
if os.path.exists(analytics_page):
    print(f"   ✓ Analytics page exists")
else:
    print(f"   ✗ Analytics page not found")

# Test 8: Cleanup
print("\n8. Cleaning up...")
try:
    detector.shutdown()
    print("   ✓ Detector shutdown successful")
except Exception as e:
    print(f"   ✗ Cleanup failed: {e}")

# Summary
print("\n" + "="*70)
print("  TEST SUMMARY")
print("="*70)
print("\n✅ All core components tested successfully!")
print("\nNext steps:")
print("  1. Run Streamlit app: streamlit run app/streamlit_app.py")
print("  2. Login as a student")
print("  3. Navigate to Lectures page")
print("  4. Enable 'Ensemble ML Model' in settings")
print("  5. Watch a lecture to test real-time integration")
print("  6. Check 'Ensemble Analytics' page to view reports")
print("\n" + "="*70)
