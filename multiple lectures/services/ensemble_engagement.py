"""
Smart LMS - Ensemble Engagement Detection
Combines multiple trained models for improved accuracy with real-time performance
CPU and energy efficient implementation with smart caching
"""

import numpy as np
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import threading
import queue
import time
from datetime import datetime, timedelta
import logging

# Configure TensorFlow BEFORE importing it (must be first)
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Reduce TF logging

# Now import TensorFlow
import tensorflow as tf

# Configure threading BEFORE any TF operations
try:
    if hasattr(tf, 'config'):
        tf.config.threading.set_inter_op_parallelism_threads(2)
        tf.config.threading.set_intra_op_parallelism_threads(4)
except (RuntimeError, AttributeError):
    pass  # Already initialized or not available, ignore

# Add export folder to path for custom layers
export_path = Path(__file__).parent.parent.parent / "export"
sys.path.insert(0, str(export_path))

try:
    from model_loader import load_model_with_custom_layers
except ImportError:
    logging.warning("Custom model loader not found. Falling back to default.")
    import keras
    load_model_with_custom_layers = keras.models.load_model


class EnsembleEngagementDetector:
    """
    Efficient ensemble model for engagement detection
    
    Features:
    - Combines 3 best models (Transformer, BiLSTM_FMAE, Fusion)
    - Smart caching to avoid redundant predictions
    - Async prediction for non-blocking operation
    - CPU-optimized with batching
    - Energy-efficient mode
    """
    
    def __init__(
        self,
        export_dir: str = "export",
        mode: str = "balanced",  # "fast", "balanced", "accurate"
        enable_cache: bool = True,
        cache_duration: int = 2  # seconds
    ):
        """
        Initialize ensemble detector
        
        Args:
            export_dir: Path to exported models directory
            mode: Performance mode - "fast" (1 model), "balanced" (2 models), "accurate" (3 models)
            enable_cache: Enable prediction caching
            cache_duration: Cache validity in seconds
        """
        self.export_dir = Path(export_dir)
        self.mode = mode
        self.enable_cache = enable_cache
        self.cache_duration = cache_duration
        
        # Model configurations with weights
        self.model_configs = {
            "fast": [
                ("BiLSTM_Enhanced_FMAE_58.6%", 1.0, 256)  # (name, weight, feature_dim)
            ],
            "balanced": [
                ("Transformer_ViT_59.6%_BEST", 0.6, 768),
                ("BiLSTM_Enhanced_FMAE_58.6%", 0.4, 256)
            ],
            "accurate": [
                ("Transformer_ViT_59.6%_BEST", 0.45, 768),
                ("BiLSTM_Enhanced_FMAE_58.6%", 0.35, 256),
                ("Fusion_Enhanced_57.4%", 0.20, 1059)
            ]
        }
        
        # Engagement dimensions
        self.dimensions = ['Boredom', 'Engagement', 'Confusion', 'Frustration']
        self.levels = ['Very Low', 'Low', 'High', 'Very High']
        
        # Cache for predictions
        self.prediction_cache = {}
        self.cache_lock = threading.Lock()
        
        # Async prediction queue
        self.prediction_queue = queue.Queue(maxsize=10)
        self.result_queue = queue.Queue()
        self.prediction_thread = None
        self.running = False
        
        # Load models
        self.models = self._load_models()
        
        # Set CPU optimization
        self._configure_cpu_optimization()
        
        logging.info(f"Ensemble detector initialized in '{mode}' mode with {len(self.models)} models")
    
    def _configure_cpu_optimization(self):
        """Configure TensorFlow for CPU efficiency"""
        # Threading already configured at module import
        # Just enable memory growth for GPU if available
        physical_devices = tf.config.list_physical_devices('GPU')
        if physical_devices:
            try:
                for device in physical_devices:
                    tf.config.experimental.set_memory_growth(device, True)
            except RuntimeError:
                pass
    
    def _load_models(self) -> List[Tuple[tf.keras.Model, float, int]]:
        """
        Load models based on selected mode
        
        Returns:
            List of (model, weight, feature_dim) tuples
        """
        models = []
        configs = self.model_configs.get(self.mode, self.model_configs["balanced"])
        
        for model_name, weight, feature_dim in configs:
            model_path = self.export_dir / model_name / "best_model.h5"
            
            try:
                logging.info(f"Loading {model_name}...")
                model = load_model_with_custom_layers(str(model_path))
                models.append((model, weight, feature_dim))
                logging.info(f"✓ {model_name} loaded successfully")
            except Exception as e:
                logging.error(f"✗ Failed to load {model_name}: {e}")
                # Adjust weights if model fails to load
                if len(models) > 0:
                    remaining_models = len(configs) - len(models)
                    if remaining_models > 0:
                        # Redistribute weight to loaded models
                        total_weight = sum(m[1] for m in models)
                        models = [(m[0], m[1]/total_weight, m[2]) for m in models]
        
        if not models:
            raise RuntimeError("No models could be loaded!")
        
        return models
    
    def _get_cache_key(self, features: np.ndarray) -> str:
        """Generate cache key from features"""
        # Use hash of features for cache key
        return str(hash(features.tobytes()))
    
    def _check_cache(self, cache_key: str) -> Optional[Dict]:
        """Check if prediction exists in cache"""
        if not self.enable_cache:
            return None
        
        with self.cache_lock:
            if cache_key in self.prediction_cache:
                cached_pred, timestamp = self.prediction_cache[cache_key]
                
                # Check if cache is still valid
                if datetime.now() - timestamp < timedelta(seconds=self.cache_duration):
                    return cached_pred
                else:
                    # Remove expired cache
                    del self.prediction_cache[cache_key]
        
        return None
    
    def _update_cache(self, cache_key: str, prediction: Dict):
        """Update prediction cache"""
        if not self.enable_cache:
            return
        
        with self.cache_lock:
            # Limit cache size to prevent memory issues
            if len(self.prediction_cache) > 100:
                # Remove oldest entries
                oldest_key = min(self.prediction_cache.keys(), 
                               key=lambda k: self.prediction_cache[k][1])
                del self.prediction_cache[oldest_key]
            
            self.prediction_cache[cache_key] = (prediction, datetime.now())
    
    def predict(
        self,
        features: np.ndarray,
        return_confidence: bool = True
    ) -> Dict:
        """
        Predict engagement from features using ensemble
        
        Args:
            features: Input features (shape depends on model)
            return_confidence: Whether to include confidence scores
        
        Returns:
            Dictionary with predictions for each dimension
        """
        # Check cache first
        cache_key = self._get_cache_key(features)
        cached_result = self._check_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Ensemble predictions
        ensemble_predictions = {dim: np.zeros(4) for dim in self.dimensions}
        
        for model, weight, expected_dim in self.models:
            try:
                # Prepare features for this model
                model_features = self._prepare_features(features, expected_dim)
                
                # Predict with this model
                predictions = model.predict(model_features, verbose=0)
                
                # Aggregate predictions (weighted sum)
                for i, dim in enumerate(self.dimensions):
                    if isinstance(predictions, list):
                        pred = predictions[i][0]  # Multi-output model
                    else:
                        pred = predictions[0]  # Single output
                    
                    ensemble_predictions[dim] += pred * weight
                
            except Exception as e:
                logging.warning(f"Model prediction failed: {e}")
                continue
        
        # Create result dictionary
        result = {
            'timestamp': datetime.utcnow().isoformat(),
            'mode': self.mode,
            'predictions': {}
        }
        
        for dim in self.dimensions:
            probs = ensemble_predictions[dim]
            class_id = int(np.argmax(probs))
            confidence = float(probs[class_id])
            level = self.levels[class_id]
            
            result['predictions'][dim] = {
                'level': level,
                'class_id': class_id,
                'level_name': f"{dim}_{level.replace(' ', '_')}",
            }
            
            if return_confidence:
                result['predictions'][dim]['confidence'] = confidence
                result['predictions'][dim]['probabilities'] = probs.tolist()
        
        # Calculate overall engagement score (0-1)
        engagement_class = result['predictions']['Engagement']['class_id']
        result['engagement_score'] = engagement_class / 3.0  # Normalize to 0-1
        
        # Update cache
        self._update_cache(cache_key, result)
        
        return result
    
    def _prepare_features(self, features: np.ndarray, target_dim: int) -> np.ndarray:
        """
        Prepare features for specific model
        
        Args:
            features: Input features
            target_dim: Expected feature dimension for model
        
        Returns:
            Transformed features matching model input shape
        """
        # Get current feature dimension
        current_dim = features.shape[-1] if len(features.shape) > 1 else features.shape[0]
        
        if current_dim == target_dim:
            # Features match, ensure correct shape
            if len(features.shape) == 2:
                return features.reshape(1, features.shape[0], features.shape[1])
            return features
        
        # Feature dimension mismatch - apply transformation
        if len(features.shape) == 3:
            batch, seq_len, feat_dim = features.shape
        else:
            seq_len, feat_dim = features.shape
            batch = 1
        
        if target_dim < feat_dim:
            # Dimensionality reduction (take first N features)
            transformed = features[..., :target_dim]
        else:
            # Dimensionality expansion (zero padding)
            if len(features.shape) == 3:
                pad_width = ((0, 0), (0, 0), (0, target_dim - feat_dim))
            else:
                pad_width = ((0, 0), (0, target_dim - feat_dim))
            transformed = np.pad(features, pad_width, mode='constant')
        
        # Ensure batch dimension
        if len(transformed.shape) == 2:
            transformed = transformed.reshape(1, transformed.shape[0], transformed.shape[1])
        
        return transformed
    
    def predict_async(self, features: np.ndarray) -> str:
        """
        Start async prediction (non-blocking)
        
        Args:
            features: Input features
        
        Returns:
            Prediction ID for retrieving result
        """
        if not self.running:
            self._start_prediction_thread()
        
        pred_id = f"pred_{int(time.time() * 1000)}"
        try:
            self.prediction_queue.put((pred_id, features), block=False)
            return pred_id
        except queue.Full:
            logging.warning("Prediction queue full, processing synchronously")
            result = self.predict(features)
            return pred_id, result
    
    def get_async_result(self, pred_id: str, timeout: float = 1.0) -> Optional[Dict]:
        """
        Get result of async prediction
        
        Args:
            pred_id: Prediction ID from predict_async
            timeout: Maximum wait time in seconds
        
        Returns:
            Prediction result or None if not ready
        """
        try:
            result_id, result = self.result_queue.get(timeout=timeout)
            if result_id == pred_id:
                return result
            else:
                # Put back if not matching
                self.result_queue.put((result_id, result))
                return None
        except queue.Empty:
            return None
    
    def _start_prediction_thread(self):
        """Start background thread for async predictions"""
        if self.prediction_thread is None or not self.prediction_thread.is_alive():
            self.running = True
            self.prediction_thread = threading.Thread(target=self._prediction_worker, daemon=True)
            self.prediction_thread.start()
    
    def _prediction_worker(self):
        """Background worker for processing async predictions"""
        while self.running:
            try:
                pred_id, features = self.prediction_queue.get(timeout=1.0)
                result = self.predict(features)
                self.result_queue.put((pred_id, result))
            except queue.Empty:
                continue
            except Exception as e:
                logging.error(f"Prediction worker error: {e}")
    
    def get_model_info(self) -> Dict:
        """Get information about loaded models"""
        return {
            'mode': self.mode,
            'num_models': len(self.models),
            'models': [
                {
                    'weight': weight,
                    'feature_dim': feat_dim,
                    'parameters': model.count_params()
                }
                for model, weight, feat_dim in self.models
            ],
            'cache_enabled': self.enable_cache,
            'cache_duration': self.cache_duration
        }
    
    def clear_cache(self):
        """Clear prediction cache"""
        with self.cache_lock:
            self.prediction_cache.clear()
        logging.info("Prediction cache cleared")
    
    def shutdown(self):
        """Shutdown ensemble detector and cleanup resources"""
        self.running = False
        if self.prediction_thread:
            self.prediction_thread.join(timeout=2.0)
        self.clear_cache()
        logging.info("Ensemble detector shutdown complete")


# Convenience function for quick usage
def create_ensemble_detector(mode: str = "balanced") -> EnsembleEngagementDetector:
    """
    Create ensemble detector with default settings
    
    Args:
        mode: "fast" (1 model, <50ms), "balanced" (2 models, ~80ms), "accurate" (3 models, ~150ms)
    
    Returns:
        Configured ensemble detector
    """
    return EnsembleEngagementDetector(mode=mode)


if __name__ == "__main__":
    # Test ensemble detector
    logging.basicConfig(level=logging.INFO)
    
    print("Testing Ensemble Engagement Detector")
    print("=" * 50)
    
    # Test all modes
    for mode in ["fast", "balanced", "accurate"]:
        print(f"\nMode: {mode}")
        try:
            detector = create_ensemble_detector(mode=mode)
            info = detector.get_model_info()
            print(f"  Models loaded: {info['num_models']}")
            print(f"  Total parameters: {sum(m['parameters'] for m in info['models']):,}")
            
            # Test prediction with dummy data
            dummy_features = np.random.randn(30, 256).astype(np.float32)
            start_time = time.time()
            result = detector.predict(dummy_features)
            inference_time = (time.time() - start_time) * 1000
            
            print(f"  Inference time: {inference_time:.2f}ms")
            print(f"  Engagement: {result['predictions']['Engagement']['level']}")
            
            detector.shutdown()
        except Exception as e:
            print(f"  Error: {e}")
    
    print("\n" + "=" * 50)
    print("Testing complete!")
