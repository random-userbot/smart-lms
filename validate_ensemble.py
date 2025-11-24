"""
Ensemble Model Validation Script
Tests ensemble model on existing ML data and captured frames
Compares predictions with baseline engagement scores
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import cv2
from datetime import datetime
import json
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple
import logging

# Add services to path
sys.path.insert(0, str(Path(__file__).parent / "multiple lectures"))

from services.ensemble_engagement import create_ensemble_detector

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EnsembleValidator:
    """Validates ensemble model on existing ML data"""
    
    def __init__(self, ml_data_dir: str = "multiple lectures/ml_data"):
        """
        Initialize validator
        
        Args:
            ml_data_dir: Path to ML data directory
        """
        self.ml_data_dir = Path(ml_data_dir)
        self.csv_logs_dir = self.ml_data_dir / "csv_logs"
        self.engagement_logs_dir = self.ml_data_dir / "engagement_logs"
        self.captured_frames_dir = self.ml_data_dir / "captured_frames"
        
        # Initialize ensemble detector
        logger.info("Initializing ensemble detector...")
        self.detector = create_ensemble_detector(mode="balanced")
        
        # Results storage
        self.validation_results = []
        self.comparison_data = []
    
    def extract_features_from_openface_csv(self, csv_file: Path) -> np.ndarray:
        """
        Extract features from OpenFace CSV for ensemble model
        
        Args:
            csv_file: Path to OpenFace features CSV
        
        Returns:
            Feature array (N, 35) for N frames
        """
        df = pd.read_csv(csv_file)
        
        # Extract relevant features (35 dimensions)
        # Match the feature set used in training
        feature_columns = [
            # Gaze features (2)
            'gaze_angle_x', 'gaze_angle_y',
            # Head pose (6)
            'pose_Tx', 'pose_Ty', 'pose_Tz',
            'pose_Rx', 'pose_Ry', 'pose_Rz',
            # Action Units (17)
            'AU01_r', 'AU02_r', 'AU04_r', 'AU05_r', 'AU06_r', 'AU07_r',
            'AU09_r', 'AU10_r', 'AU12_r', 'AU14_r', 'AU15_r', 'AU17_r',
            'AU20_r', 'AU23_r', 'AU25_r', 'AU26_r', 'AU45_r',
            # Additional features (10)
            'smile_intensity', 'confusion_level', 'drowsiness_level',
            'gaze_0_x', 'gaze_0_y', 'gaze_0_z',
            'gaze_1_x', 'gaze_1_y', 'gaze_1_z',
            'confidence'
        ]
        
        # Check which columns exist
        available_columns = [col for col in feature_columns if col in df.columns]
        
        if len(available_columns) < 20:
            logger.warning(f"Only {len(available_columns)} features available, expected 35+")
        
        # Extract features
        features = df[available_columns].values
        
        # Pad to 35 features if needed
        if features.shape[1] < 35:
            padding = np.zeros((features.shape[0], 35 - features.shape[1]))
            features = np.hstack([features, padding])
        elif features.shape[1] > 35:
            features = features[:, :35]
        
        # Handle NaN values
        features = np.nan_to_num(features, nan=0.0)
        
        return features.astype(np.float32)
    
    def process_openface_features(self, features: np.ndarray, window_size: int = 30) -> List[np.ndarray]:
        """
        Create sliding windows of features for ensemble prediction
        
        Args:
            features: Feature array (N, 35)
            window_size: Window size (default 30 frames = 1 second)
        
        Returns:
            List of feature windows
        """
        windows = []
        
        for i in range(0, len(features) - window_size + 1, window_size):
            window = features[i:i+window_size]
            if len(window) == window_size:
                windows.append(window)
        
        return windows
    
    def extract_features_from_image(self, image_path: Path) -> np.ndarray:
        """
        Extract features from single image using MediaPipe
        (Alternative to OpenFace features)
        
        Args:
            image_path: Path to image file
        
        Returns:
            Feature vector (35,) or None if failed
        """
        try:
            # Load image
            image = cv2.imread(str(image_path))
            if image is None:
                return None
            
            # Import MediaPipe
            import mediapipe as mp
            mp_face_mesh = mp.solutions.face_mesh
            
            # Process with MediaPipe
            with mp_face_mesh.FaceMesh(
                static_image_mode=True,
                max_num_faces=1,
                min_detection_confidence=0.5
            ) as face_mesh:
                
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = face_mesh.process(rgb_image)
                
                if not results.multi_face_landmarks:
                    return None
                
                landmarks = results.multi_face_landmarks[0].landmark
                
                # Extract simplified features (35-dim)
                features = []
                
                # Gaze features (2)
                left_iris = landmarks[468]
                right_iris = landmarks[473]
                features.extend([left_iris.x, right_iris.x])
                
                # Eye openness (2)
                left_eye_top = landmarks[159]
                left_eye_bottom = landmarks[145]
                right_eye_top = landmarks[386]
                right_eye_bottom = landmarks[374]
                features.extend([
                    abs(left_eye_top.y - left_eye_bottom.y),
                    abs(right_eye_top.y - right_eye_bottom.y)
                ])
                
                # Head pose (3)
                nose = landmarks[1]
                chin = landmarks[152]
                left_face = landmarks[234]
                right_face = landmarks[454]
                features.extend([
                    nose.x - chin.x,
                    left_face.x - right_face.x,
                    nose.y - chin.y
                ])
                
                # Mouth features (4)
                upper_lip = landmarks[13]
                lower_lip = landmarks[14]
                left_mouth = landmarks[61]
                right_mouth = landmarks[291]
                features.extend([
                    abs(upper_lip.y - lower_lip.y),
                    abs(left_mouth.x - right_mouth.x),
                    upper_lip.y,
                    lower_lip.y
                ])
                
                # Eyebrow features (4)
                left_eyebrow_inner = landmarks[70]
                left_eyebrow_outer = landmarks[105]
                right_eyebrow_inner = landmarks[300]
                right_eyebrow_outer = landmarks[334]
                features.extend([
                    left_eyebrow_inner.y,
                    left_eyebrow_outer.y,
                    right_eyebrow_inner.y,
                    right_eyebrow_outer.y
                ])
                
                # Pad remaining features
                while len(features) < 35:
                    features.append(0.0)
                
                return np.array(features[:35], dtype=np.float32)
        
        except Exception as e:
            logger.error(f"Failed to extract features from {image_path}: {e}")
            return None
    
    def validate_session(self, session_name: str) -> Dict:
        """
        Validate ensemble model on a single session
        
        Args:
            session_name: Session identifier (e.g., "student_4_lec_2a96290c_3b05caef")
        
        Returns:
            Validation results dictionary
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"Validating session: {session_name}")
        logger.info(f"{'='*70}")
        
        # Load OpenFace features
        csv_file = self.csv_logs_dir / f"openface_features_{session_name}.csv"
        if not csv_file.exists():
            logger.error(f"OpenFace CSV not found: {csv_file}")
            return None
        
        # Load engagement log for comparison
        engagement_file = self.engagement_logs_dir / f"engagement_log_{session_name}.csv"
        if not engagement_file.exists():
            logger.error(f"Engagement log not found: {engagement_file}")
            return None
        
        logger.info("Loading data...")
        openface_df = pd.read_csv(csv_file)
        engagement_df = pd.read_csv(engagement_file)
        
        logger.info(f"  OpenFace features: {len(openface_df)} frames")
        logger.info(f"  Engagement log: {len(engagement_df)} records")
        
        # Extract features
        logger.info("Extracting features from OpenFace data...")
        features = self.extract_features_from_openface_csv(csv_file)
        logger.info(f"  Feature shape: {features.shape}")
        
        # Create windows
        windows = self.process_openface_features(features, window_size=30)
        logger.info(f"  Created {len(windows)} windows")
        
        # Run ensemble predictions
        logger.info("Running ensemble predictions...")
        predictions = []
        
        for i, window in enumerate(windows):
            try:
                result = self.detector.predict(window, return_confidence=True)
                predictions.append(result)
                
                if (i + 1) % 10 == 0:
                    logger.info(f"  Processed {i+1}/{len(windows)} windows")
            except Exception as e:
                logger.error(f"  Prediction failed for window {i}: {e}")
                predictions.append(None)
        
        # Compare with baseline
        logger.info("Comparing with baseline engagement scores...")
        comparison = self.compare_predictions(predictions, engagement_df)
        
        # Calculate metrics
        results = {
            'session_name': session_name,
            'total_windows': len(windows),
            'successful_predictions': sum(1 for p in predictions if p is not None),
            'comparison': comparison,
            'predictions': predictions
        }
        
        self.validation_results.append(results)
        
        return results
    
    def compare_predictions(self, predictions: List[Dict], engagement_df: pd.DataFrame) -> Dict:
        """
        Compare ensemble predictions with baseline engagement scores
        
        Args:
            predictions: List of ensemble predictions
            engagement_df: Baseline engagement dataframe
        
        Returns:
            Comparison metrics
        """
        if not predictions or engagement_df.empty:
            return {}
        
        # Extract ensemble scores
        ensemble_scores = []
        for pred in predictions:
            if pred:
                ensemble_scores.append(pred['engagement_score'] * 100)  # Convert to 0-100
        
        # Get baseline scores (sample at same intervals)
        baseline_scores = []
        for i in range(0, min(len(ensemble_scores), len(engagement_df)), 1):
            if i < len(engagement_df):
                baseline_scores.append(engagement_df.iloc[i]['engagement_score'])
        
        # Ensure same length
        min_len = min(len(ensemble_scores), len(baseline_scores))
        ensemble_scores = ensemble_scores[:min_len]
        baseline_scores = baseline_scores[:min_len]
        
        if not ensemble_scores or not baseline_scores:
            return {}
        
        # Calculate metrics
        ensemble_arr = np.array(ensemble_scores)
        baseline_arr = np.array(baseline_scores)
        
        comparison = {
            'ensemble_mean': float(np.mean(ensemble_arr)),
            'baseline_mean': float(np.mean(baseline_arr)),
            'ensemble_std': float(np.std(ensemble_arr)),
            'baseline_std': float(np.std(baseline_arr)),
            'correlation': float(np.corrcoef(ensemble_arr, baseline_arr)[0, 1]),
            'mae': float(np.mean(np.abs(ensemble_arr - baseline_arr))),
            'rmse': float(np.sqrt(np.mean((ensemble_arr - baseline_arr) ** 2))),
            'improvement': float(np.mean(ensemble_arr) - np.mean(baseline_arr))
        }
        
        # Store for visualization
        self.comparison_data.extend([
            {'type': 'Ensemble', 'score': score} for score in ensemble_scores
        ])
        self.comparison_data.extend([
            {'type': 'Baseline', 'score': score} for score in baseline_scores
        ])
        
        return comparison
    
    def validate_captured_frames(self, max_frames: int = 100) -> Dict:
        """
        Validate ensemble on captured frame images
        
        Args:
            max_frames: Maximum number of frames to process
        
        Returns:
            Validation results
        """
        logger.info(f"\n{'='*70}")
        logger.info("Validating on captured frame images")
        logger.info(f"{'='*70}")
        
        # Get image files
        image_files = list(self.captured_frames_dir.glob("*.jpg"))
        logger.info(f"Found {len(image_files)} image files")
        
        if not image_files:
            logger.error("No image files found")
            return None
        
        # Limit number of frames
        image_files = image_files[:max_frames]
        logger.info(f"Processing {len(image_files)} images...")
        
        # Extract features from images
        frame_features = []
        successful = 0
        
        for i, img_path in enumerate(image_files):
            features = self.extract_features_from_image(img_path)
            if features is not None:
                frame_features.append(features)
                successful += 1
            
            if (i + 1) % 20 == 0:
                logger.info(f"  Processed {i+1}/{len(image_files)} images ({successful} successful)")
        
        logger.info(f"Successfully extracted features from {successful}/{len(image_files)} images")
        
        # Create windows
        if len(frame_features) < 30:
            logger.warning(f"Not enough features ({len(frame_features)}) for a full window (30)")
            return None
        
        features_array = np.array(frame_features)
        windows = self.process_openface_features(features_array, window_size=30)
        logger.info(f"Created {len(windows)} windows")
        
        # Run predictions
        logger.info("Running ensemble predictions...")
        predictions = []
        
        for i, window in enumerate(windows):
            try:
                result = self.detector.predict(window, return_confidence=True)
                predictions.append(result)
            except Exception as e:
                logger.error(f"Prediction failed for window {i}: {e}")
                predictions.append(None)
        
        # Calculate statistics
        engagement_scores = [p['engagement_score'] * 100 for p in predictions if p]
        
        results = {
            'total_images': len(image_files),
            'successful_extractions': successful,
            'total_windows': len(windows),
            'successful_predictions': len(engagement_scores),
            'mean_engagement': float(np.mean(engagement_scores)) if engagement_scores else 0,
            'std_engagement': float(np.std(engagement_scores)) if engagement_scores else 0,
            'predictions': predictions
        }
        
        return results
    
    def generate_report(self, output_file: str = "ensemble_validation_report.json"):
        """Generate validation report"""
        logger.info(f"\n{'='*70}")
        logger.info("Generating Validation Report")
        logger.info(f"{'='*70}")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_sessions': len(self.validation_results),
            'sessions': self.validation_results,
            'summary': self.generate_summary()
        }
        
        # Save report
        output_path = Path(output_file)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"\n✓ Report saved to: {output_path.absolute()}")
        
        return report
    
    def generate_summary(self) -> Dict:
        """Generate summary statistics"""
        if not self.validation_results:
            return {}
        
        # Aggregate comparisons
        all_comparisons = [r['comparison'] for r in self.validation_results if r and 'comparison' in r]
        
        if not all_comparisons:
            return {}
        
        summary = {
            'avg_correlation': np.mean([c['correlation'] for c in all_comparisons if 'correlation' in c]),
            'avg_mae': np.mean([c['mae'] for c in all_comparisons if 'mae' in c]),
            'avg_rmse': np.mean([c['rmse'] for c in all_comparisons if 'rmse' in c]),
            'avg_improvement': np.mean([c['improvement'] for c in all_comparisons if 'improvement' in c]),
            'total_predictions': sum(r['successful_predictions'] for r in self.validation_results)
        }
        
        return summary
    
    def visualize_results(self, output_dir: str = "validation_plots"):
        """Generate visualization plots"""
        logger.info(f"\n{'='*70}")
        logger.info("Generating Visualizations")
        logger.info(f"{'='*70}")
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        if not self.comparison_data:
            logger.warning("No comparison data available for visualization")
            return
        
        # Plot 1: Engagement Score Distribution
        plt.figure(figsize=(12, 6))
        df = pd.DataFrame(self.comparison_data)
        sns.violinplot(data=df, x='type', y='score', palette='Set2')
        plt.title('Engagement Score Distribution: Ensemble vs Baseline')
        plt.ylabel('Engagement Score (%)')
        plt.savefig(output_path / 'engagement_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"  ✓ Saved: engagement_distribution.png")
        
        # Plot 2: Session Comparison
        if self.validation_results:
            plt.figure(figsize=(14, 6))
            session_names = []
            ensemble_means = []
            baseline_means = []
            
            for result in self.validation_results:
                if result and 'comparison' in result:
                    comp = result['comparison']
                    if comp:
                        session_names.append(result['session_name'][-10:])  # Last 10 chars
                        ensemble_means.append(comp.get('ensemble_mean', 0))
                        baseline_means.append(comp.get('baseline_mean', 0))
            
            x = np.arange(len(session_names))
            width = 0.35
            
            plt.bar(x - width/2, ensemble_means, width, label='Ensemble', alpha=0.8)
            plt.bar(x + width/2, baseline_means, width, label='Baseline', alpha=0.8)
            
            plt.xlabel('Session')
            plt.ylabel('Mean Engagement Score (%)')
            plt.title('Mean Engagement Scores by Session')
            plt.xticks(x, session_names, rotation=45, ha='right')
            plt.legend()
            plt.tight_layout()
            plt.savefig(output_path / 'session_comparison.png', dpi=300, bbox_inches='tight')
            plt.close()
            logger.info(f"  ✓ Saved: session_comparison.png")
        
        logger.info(f"\n✓ Visualizations saved to: {output_path.absolute()}")
    
    def print_summary(self):
        """Print validation summary to console"""
        print("\n" + "="*70)
        print("  ENSEMBLE MODEL VALIDATION SUMMARY")
        print("="*70)
        
        if not self.validation_results:
            print("\nNo validation results available")
            return
        
        summary = self.generate_summary()
        
        print(f"\n📊 Overall Statistics:")
        print(f"  • Total Sessions Validated: {len(self.validation_results)}")
        print(f"  • Total Predictions Made: {summary.get('total_predictions', 0)}")
        
        print(f"\n📈 Performance Metrics:")
        print(f"  • Average Correlation: {summary.get('avg_correlation', 0):.3f}")
        print(f"  • Average MAE: {summary.get('avg_mae', 0):.2f}%")
        print(f"  • Average RMSE: {summary.get('avg_rmse', 0):.2f}%")
        print(f"  • Average Improvement: {summary.get('avg_improvement', 0):+.2f}%")
        
        print(f"\n📋 Session Details:")
        for i, result in enumerate(self.validation_results, 1):
            if result and 'comparison' in result:
                comp = result['comparison']
                if comp:
                    print(f"\n  Session {i}: {result['session_name']}")
                    print(f"    ├─ Windows: {result['total_windows']}")
                    print(f"    ├─ Predictions: {result['successful_predictions']}")
                    print(f"    ├─ Ensemble Mean: {comp.get('ensemble_mean', 0):.1f}%")
                    print(f"    ├─ Baseline Mean: {comp.get('baseline_mean', 0):.1f}%")
                    print(f"    ├─ Correlation: {comp.get('correlation', 0):.3f}")
                    print(f"    └─ Improvement: {comp.get('improvement', 0):+.1f}%")
        
        print("\n" + "="*70)


def main():
    """Main validation function"""
    print("\n" + "="*70)
    print("  ENSEMBLE MODEL VALIDATION ON ML DATA")
    print("  Smart LMS - Engagement Detection")
    print("="*70)
    
    try:
        # Initialize validator
        validator = EnsembleValidator()
        
        # Find all sessions
        csv_files = list(validator.csv_logs_dir.glob("openface_features_*.csv"))
        sessions = [f.stem.replace("openface_features_", "") for f in csv_files]
        
        print(f"\nFound {len(sessions)} sessions to validate:")
        for session in sessions:
            print(f"  • {session}")
        
        # Validate each session
        print(f"\n{'='*70}")
        print("Starting Validation...")
        print(f"{'='*70}")
        
        for session in sessions:
            validator.validate_session(session)
        
        # Validate captured frames
        validator.validate_captured_frames(max_frames=60)
        
        # Generate report
        validator.generate_report()
        
        # Generate visualizations
        validator.visualize_results()
        
        # Print summary
        validator.print_summary()
        
        # Cleanup
        validator.detector.shutdown()
        
        print("\n" + "="*70)
        print("  ✓ VALIDATION COMPLETE!")
        print("="*70)
        print("\nResults saved:")
        print("  • ensemble_validation_report.json")
        print("  • validation_plots/engagement_distribution.png")
        print("  • validation_plots/session_comparison.png")
        print("\n" + "="*70)
        
        return 0
    
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
