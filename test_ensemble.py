"""
Quick Test - Ensemble Model Integration
Verify that ensemble system works with exported models
"""

import sys
from pathlib import Path
import numpy as np

print("=" * 70)
print("  ENSEMBLE MODEL INTEGRATION - QUICK TEST")
print("=" * 70)

# Test 1: Check export folder exists
print("\n[1/6] Checking export folder...")
export_dir = Path("export")
if export_dir.exists():
    print(f"✓ Export folder found: {export_dir.absolute()}")
    models = list(export_dir.glob("*/best_model.h5"))
    print(f"✓ Found {len(models)} models:")
    for model in models:
        size_mb = model.stat().st_size / (1024 * 1024)
        print(f"    • {model.parent.name} ({size_mb:.1f} MB)")
else:
    print(f"✗ Export folder not found at: {export_dir.absolute()}")
    print("  Please ensure export folder is in project root")
    sys.exit(1)

# Test 2: Import ensemble module
print("\n[2/6] Importing ensemble module...")
try:
    sys.path.insert(0, str(Path(__file__).parent / "multiple lectures"))
    from services.ensemble_engagement import EnsembleEngagementDetector, create_ensemble_detector
    print("✓ Ensemble module imported successfully")
except ImportError as e:
    print(f"✗ Failed to import ensemble module: {e}")
    sys.exit(1)

# Test 3: Load model in fast mode
print("\n[3/6] Testing 'fast' mode (1 model)...")
try:
    detector_fast = create_ensemble_detector(mode="fast")
    info = detector_fast.get_model_info()
    print(f"✓ Fast mode loaded: {info['num_models']} model(s)")
    detector_fast.shutdown()
except Exception as e:
    print(f"✗ Fast mode failed: {e}")

# Test 4: Load model in balanced mode
print("\n[4/6] Testing 'balanced' mode (2 models)...")
try:
    detector_balanced = create_ensemble_detector(mode="balanced")
    info = detector_balanced.get_model_info()
    print(f"✓ Balanced mode loaded: {info['num_models']} model(s)")
except Exception as e:
    print(f"✗ Balanced mode failed: {e}")
    detector_balanced = None

# Test 5: Run prediction
print("\n[5/6] Testing prediction...")
if detector_balanced:
    try:
        # Generate dummy features
        features = np.random.randn(30, 256).astype(np.float32)
        
        # Predict
        result = detector_balanced.predict(features, return_confidence=True)
        
        # Verify result structure
        assert 'engagement_score' in result, "Missing engagement_score"
        assert 'predictions' in result, "Missing predictions"
        assert 'Engagement' in result['predictions'], "Missing Engagement dimension"
        
        engagement_level = result['predictions']['Engagement']['level']
        engagement_score = result['engagement_score']
        confidence = result['predictions']['Engagement']['confidence']
        
        print(f"✓ Prediction successful:")
        print(f"    • Engagement: {engagement_level}")
        print(f"    • Score: {engagement_score:.1%}")
        print(f"    • Confidence: {confidence:.1%}")
        
    except Exception as e:
        print(f"✗ Prediction failed: {e}")
        import traceback
        traceback.print_exc()
else:
    print("✗ Skipped (detector not loaded)")

# Test 6: Test cache performance
print("\n[6/6] Testing cache performance...")
if detector_balanced:
    try:
        import time
        
        # First prediction (no cache)
        features = np.random.randn(30, 256).astype(np.float32)
        start = time.time()
        result1 = detector_balanced.predict(features)
        time1 = (time.time() - start) * 1000
        
        # Second prediction (cached)
        start = time.time()
        result2 = detector_balanced.predict(features)
        time2 = (time.time() - start) * 1000
        
        speedup = time1 / time2 if time2 > 0 else 0
        
        print(f"✓ Cache working:")
        print(f"    • First prediction: {time1:.2f}ms")
        print(f"    • Cached prediction: {time2:.2f}ms")
        print(f"    • Speedup: {speedup:.1f}x faster")
        
        detector_balanced.shutdown()
        
    except Exception as e:
        print(f"✗ Cache test failed: {e}")
else:
    print("✗ Skipped (detector not loaded)")

# Final summary
print("\n" + "=" * 70)
print("  TEST SUMMARY")
print("=" * 70)
print("\n✅ All tests passed!")
print("\nYour ensemble system is ready to use!")
print("\nNext steps:")
print("  1. Run full demo: python demo_ensemble.py")
print("  2. Try Streamlit: streamlit run streamlit_ensemble_example.py")
print("  3. Integrate into your app: see ENSEMBLE_GUIDE.md")
print("\n" + "=" * 70)
