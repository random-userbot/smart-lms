"""Quick test to verify ensemble models load"""
import sys
sys.path.insert(0, '.')

from services.ensemble_engagement import create_ensemble_detector

print("🔄 Loading ensemble models...")
print("-" * 50)

try:
    detector = create_ensemble_detector('fast')
    info = detector.get_model_info()
    
    print("✅ Models loaded successfully!")
    print(f"   Mode: {info['mode']}")
    print(f"   Number of models: {info['num_models']}")
    print(f"   Cache enabled: {info['cache_enabled']}")
    
    print("\n📊 Model Details:")
    for i, model_info in enumerate(info['models'], 1):
        print(f"   Model {i}:")
        print(f"     - Weight: {model_info['weight']}")
        print(f"     - Feature dim: {model_info['feature_dim']}")
        print(f"     - Parameters: {model_info['parameters']:,}")
    
    print("\n🎉 Ensemble system ready!")
    detector.shutdown()
    
except Exception as e:
    print(f"❌ Error loading models: {e}")
    import traceback
    traceback.print_exc()
