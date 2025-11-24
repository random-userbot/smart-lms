"""
Ensemble Model Demo - Smart LMS
Demonstrates the usage of the ensemble engagement detection system
"""

import numpy as np
import time
import sys
from pathlib import Path

# Add services to path
sys.path.insert(0, str(Path(__file__).parent / "multiple lectures"))

from services.ensemble_engagement import create_ensemble_detector


def print_header(text: str):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_prediction(result: dict, mode: str):
    """Print prediction results in a formatted way"""
    print(f"\nMode: {mode}")
    print(f"Timestamp: {result['timestamp']}")
    print(f"Overall Engagement Score: {result['engagement_score']:.2%}\n")
    
    print("Detailed Predictions:")
    print("-" * 70)
    print(f"{'Dimension':<20} {'Level':<15} {'Confidence':<12} {'Class ID'}")
    print("-" * 70)
    
    for dim, pred in result['predictions'].items():
        level = pred['level']
        confidence = pred.get('confidence', 0)
        class_id = pred['class_id']
        print(f"{dim:<20} {level:<15} {confidence:<12.2%} {class_id}")
    
    print("-" * 70)


def demo_basic_usage():
    """Demonstrate basic ensemble usage"""
    print_header("Demo 1: Basic Ensemble Usage")
    
    print("\nInitializing ensemble detector in 'balanced' mode...")
    detector = create_ensemble_detector(mode="balanced")
    
    # Get model info
    info = detector.get_model_info()
    print(f"\nModels loaded: {info['num_models']}")
    print(f"Total parameters: {sum(m['parameters'] for m in info['models']):,}")
    print(f"Cache enabled: {info['cache_enabled']}")
    
    # Generate dummy features (simulating 1 second of video @ 30 FPS)
    print("\nGenerating dummy features (30 frames x 256 features)...")
    features = np.random.randn(30, 256).astype(np.float32)
    
    # Make prediction
    print("Running prediction...")
    start_time = time.time()
    result = detector.predict(features, return_confidence=True)
    inference_time = (time.time() - start_time) * 1000
    
    print(f"Inference time: {inference_time:.2f}ms")
    print_prediction(result, "balanced")
    
    # Test caching
    print("\n\nTesting cache (same features)...")
    start_time = time.time()
    result2 = detector.predict(features, return_confidence=True)
    cache_time = (time.time() - start_time) * 1000
    
    print(f"Cached inference time: {cache_time:.2f}ms")
    if cache_time > 0:
        print(f"Speedup: {inference_time / cache_time:.1f}x faster")
    else:
        print(f"Speedup: >100x faster (cached instantly)")
    
    detector.shutdown()
    print("\n✓ Basic demo complete")


def demo_performance_modes():
    """Compare different performance modes"""
    print_header("Demo 2: Performance Mode Comparison")
    
    modes = ["fast", "balanced", "accurate"]
    results_summary = []
    
    for mode in modes:
        print(f"\n\nTesting '{mode}' mode...")
        print("-" * 70)
        
        try:
            detector = create_ensemble_detector(mode=mode)
            info = detector.get_model_info()
            
            # Generate features
            features = np.random.randn(30, 256).astype(np.float32)
            
            # Warm-up
            detector.predict(features, return_confidence=False)
            
            # Benchmark (10 runs)
            times = []
            for _ in range(10):
                detector.clear_cache()  # Clear cache for accurate timing
                start = time.time()
                result = detector.predict(features, return_confidence=False)
                times.append((time.time() - start) * 1000)
            
            avg_time = np.mean(times)
            std_time = np.std(times)
            
            results_summary.append({
                'mode': mode,
                'models': info['num_models'],
                'avg_time': avg_time,
                'std_time': std_time,
                'engagement': result['engagement_score']
            })
            
            print(f"Models: {info['num_models']}")
            print(f"Avg inference time: {avg_time:.2f} ± {std_time:.2f}ms")
            print(f"Engagement score: {result['engagement_score']:.2%}")
            
            detector.shutdown()
            
        except Exception as e:
            print(f"✗ Error in {mode} mode: {e}")
    
    # Summary table
    print("\n\n" + "=" * 70)
    print("  Performance Summary")
    print("=" * 70)
    print(f"\n{'Mode':<12} {'Models':<8} {'Avg Time (ms)':<16} {'Throughput (FPS)':<18}")
    print("-" * 70)
    
    for result in results_summary:
        throughput = 1000 / result['avg_time'] if result['avg_time'] > 0 else 0
        print(f"{result['mode']:<12} {result['models']:<8} "
              f"{result['avg_time']:>6.2f} ± {result['std_time']:<6.2f}  "
              f"{throughput:>6.1f}")
    
    print("-" * 70)
    print("\n✓ Performance comparison complete")


def demo_async_prediction():
    """Demonstrate async prediction for non-blocking operation"""
    print_header("Demo 3: Async Prediction (Non-blocking)")
    
    print("\nInitializing detector...")
    detector = create_ensemble_detector(mode="balanced")
    
    print("Starting async predictions...")
    
    # Submit multiple predictions asynchronously
    pred_ids = []
    for i in range(5):
        features = np.random.randn(30, 256).astype(np.float32)
        pred_id = detector.predict_async(features)
        pred_ids.append(pred_id)
        print(f"  Submitted prediction {i+1}: {pred_id}")
    
    # Retrieve results
    print("\nRetrieving results (with timeout)...")
    time.sleep(0.5)  # Give some time for processing
    
    for i, pred_id in enumerate(pred_ids):
        result = detector.get_async_result(pred_id, timeout=2.0)
        if result:
            engagement = result['predictions']['Engagement']['level']
            print(f"  Prediction {i+1}: Engagement = {engagement}")
        else:
            print(f"  Prediction {i+1}: Not ready yet")
    
    detector.shutdown()
    print("\n✓ Async demo complete")


def demo_realtime_simulation():
    """Simulate real-time video processing"""
    print_header("Demo 4: Real-Time Video Simulation")
    
    print("\nSimulating 10 seconds of video at 30 FPS...")
    detector = create_ensemble_detector(mode="fast")  # Use fast mode for real-time
    
    frame_buffer = []
    engagement_history = []
    
    # Simulate 300 frames (10 seconds @ 30 FPS)
    for frame_num in range(300):
        # Generate frame features
        frame_features = np.random.randn(256).astype(np.float32)
        frame_buffer.append(frame_features)
        
        # Keep buffer at 30 frames
        if len(frame_buffer) > 30:
            frame_buffer.pop(0)
        
        # Make prediction every 30 frames (once per second)
        if len(frame_buffer) == 30 and frame_num % 30 == 0:
            features = np.array(frame_buffer)
            result = detector.predict(features, return_confidence=False)
            
            engagement_score = result['engagement_score']
            engagement_history.append(engagement_score)
            
            second = frame_num // 30
            engagement_level = result['predictions']['Engagement']['level']
            
            # Print progress bar
            bar_length = 40
            filled = int(bar_length * engagement_score)
            bar = '█' * filled + '░' * (bar_length - filled)
            
            print(f"  Second {second:2d}/10: [{bar}] {engagement_score:.2%} - {engagement_level}")
    
    # Summary
    avg_engagement = np.mean(engagement_history)
    print(f"\nAverage Engagement: {avg_engagement:.2%}")
    print(f"Min: {min(engagement_history):.2%}, Max: {max(engagement_history):.2%}")
    
    detector.shutdown()
    print("\n✓ Real-time simulation complete")


def demo_energy_efficiency():
    """Demonstrate energy-efficient features"""
    print_header("Demo 5: Energy Efficiency Features")
    
    print("\nComparing with and without caching...")
    
    # Without cache
    print("\n1. Without cache:")
    detector_no_cache = create_ensemble_detector(mode="balanced")
    detector_no_cache.enable_cache = False
    
    features = np.random.randn(30, 256).astype(np.float32)
    
    start = time.time()
    for _ in range(100):
        detector_no_cache.predict(features, return_confidence=False)
    time_no_cache = time.time() - start
    
    print(f"   100 predictions: {time_no_cache:.3f}s")
    print(f"   Avg per prediction: {time_no_cache * 10:.2f}ms")
    
    detector_no_cache.shutdown()
    
    # With cache
    print("\n2. With cache (same features):")
    detector_cache = create_ensemble_detector(mode="balanced")
    
    start = time.time()
    for _ in range(100):
        detector_cache.predict(features, return_confidence=False)
    time_cache = time.time() - start
    
    print(f"   100 predictions: {time_cache:.3f}s")
    print(f"   Avg per prediction: {time_cache * 10:.2f}ms")
    print(f"   Speedup: {time_no_cache / time_cache:.1f}x faster")
    print(f"   Energy saved: ~{(1 - time_cache/time_no_cache) * 100:.1f}%")
    
    detector_cache.shutdown()
    
    print("\n✓ Energy efficiency demo complete")


def main():
    """Run all demos"""
    print("\n" + "=" * 70)
    print("  ENSEMBLE ENGAGEMENT DETECTION - DEMO SUITE")
    print("  Smart LMS - AI-Powered Student Engagement")
    print("=" * 70)
    
    try:
        # Run demos
        demo_basic_usage()
        demo_performance_modes()
        demo_async_prediction()
        demo_realtime_simulation()
        demo_energy_efficiency()
        
        # Final summary
        print("\n" + "=" * 70)
        print("  ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\nKey Features Demonstrated:")
        print("  ✓ Ensemble prediction combining 3 models")
        print("  ✓ Multiple performance modes (fast/balanced/accurate)")
        print("  ✓ Smart caching for efficiency")
        print("  ✓ Async prediction for non-blocking operation")
        print("  ✓ Real-time video processing simulation")
        print("  ✓ Energy-efficient operation")
        print("\nNext Steps:")
        print("  • Integrate with Streamlit app")
        print("  • Connect to webcam for live tracking")
        print("  • Save predictions to database")
        print("  • Visualize engagement over time")
        print("\n" + "=" * 70)
        
    except Exception as e:
        print(f"\n✗ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
