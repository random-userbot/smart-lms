#!/usr/bin/env python3
"""
Single Image Engagement Analysis with Explainable AI
Analyzes a single image and provides detailed engagement predictions with explanations
"""

import sys
import argparse
import numpy as np
import cv2
from pathlib import Path
import json
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent / "multiple lectures"))

from services.ensemble_engagement import create_ensemble_detector
import mediapipe as mp


class ImageEngagementAnalyzer:
    """
    Comprehensive image engagement analyzer with explainable AI
    """
    
    def __init__(self, mode: str = 'balanced'):
        """Initialize analyzer with ensemble detector"""
        print("🚀 Initializing Ensemble Engagement Analyzer...")
        print(f"   Mode: {mode}")
        
        self.detector = create_ensemble_detector(mode=mode)
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )
        
        print("✓ Analyzer ready!\n")
    
    def extract_facial_features(self, image_path: str) -> Optional[np.ndarray]:
        """
        Extract 35-dimensional facial features from image using MediaPipe
        
        Returns:
            numpy array of shape (35,) or None if face not detected
        """
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        # Convert to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Process with MediaPipe
        results = self.face_mesh.process(image_rgb)
        
        if not results.multi_face_landmarks:
            return None
        
        # Get first face
        face_landmarks = results.multi_face_landmarks[0]
        
        # Extract key landmark indices (same as training)
        key_indices = [
            # Eyes (8 points)
            33, 133, 362, 263,  # Eye corners
            159, 145, 386, 374,  # Upper/lower eye
            
            # Eyebrows (6 points)
            70, 63, 105, 66, 107, 336,
            
            # Nose (4 points)
            1, 4, 5, 6,
            
            # Mouth (8 points)
            61, 291, 0, 17, 91, 146, 321, 375,
            
            # Face contour (9 points)
            10, 338, 297, 332, 284, 251, 389, 356, 454
        ]
        
        # Extract coordinates
        features = []
        h, w = image.shape[:2]
        
        for idx in key_indices:
            landmark = face_landmarks.landmark[idx]
            features.extend([landmark.x, landmark.y, landmark.z])
        
        # Normalize features
        features = np.array(features, dtype=np.float32)
        features = (features - features.mean()) / (features.std() + 1e-8)
        
        return features
    
    def analyze_attention_patterns(self, features: np.ndarray) -> Dict[str, float]:
        """
        Analyze which facial features contribute most to engagement
        
        Returns:
            Dictionary with attention scores for different facial regions
        """
        # Features are grouped by facial region
        eye_features = features[0:24]  # 8 points × 3 coords
        eyebrow_features = features[24:42]  # 6 points × 3 coords
        nose_features = features[42:54]  # 4 points × 3 coords
        mouth_features = features[54:78]  # 8 points × 3 coords
        face_contour = features[78:105]  # 9 points × 3 coords
        
        # Calculate attention scores based on feature variance
        attention = {
            'eyes': float(np.std(eye_features) * 100),
            'eyebrows': float(np.std(eyebrow_features) * 100),
            'nose': float(np.std(nose_features) * 100),
            'mouth': float(np.std(mouth_features) * 100),
            'face_shape': float(np.std(face_contour) * 100)
        }
        
        # Normalize to percentages
        total = sum(attention.values())
        if total > 0:
            attention = {k: (v/total) * 100 for k, v in attention.items()}
        
        return attention
    
    def explain_prediction(self, prediction: Dict, attention: Dict[str, float]) -> Dict[str, any]:
        """
        Generate explainable AI insights for the prediction
        
        Returns:
            Dictionary with explanations and insights
        """
        engagement_score = prediction['engagement_score']
        predictions = prediction['predictions']
        
        # Determine engagement level
        if engagement_score >= 75:
            engagement_level = "Very High"
            emoji = "🎯"
            color = "green"
        elif engagement_score >= 50:
            engagement_level = "High"
            emoji = "✅"
            color = "lightgreen"
        elif engagement_score >= 25:
            engagement_level = "Moderate"
            emoji = "⚠️"
            color = "orange"
        else:
            engagement_level = "Low"
            emoji = "❌"
            color = "red"
        
        # Analyze emotional states
        emotional_states = {}
        for emotion, data in predictions.items():
            emotional_states[emotion] = {
                'level': data['level'],
                'confidence': round(data['confidence'] * 100, 1)
            }
        
        # Find dominant features
        dominant_feature = max(attention.items(), key=lambda x: x[1])
        
        # Generate insights
        insights = []
        
        # Engagement insights
        if engagement_score >= 75:
            insights.append(f"Student shows very high engagement ({engagement_score:.1f}%)")
            insights.append("Strong positive emotional indicators detected")
        elif engagement_score >= 50:
            insights.append(f"Student shows good engagement ({engagement_score:.1f}%)")
            insights.append("Generally positive learning state")
        elif engagement_score >= 25:
            insights.append(f"Student shows moderate engagement ({engagement_score:.1f}%)")
            insights.append("Some signs of distraction or confusion")
        else:
            insights.append(f"Student shows low engagement ({engagement_score:.1f}%)")
            insights.append("Strong indicators of disengagement detected")
        
        # Boredom analysis
        boredom = predictions['Boredom']
        if boredom['level'] in ['High', 'Very High']:
            insights.append(f"⚠️ High boredom detected ({boredom['confidence']*100:.1f}% confidence)")
            insights.append("Recommendation: Introduce interactive elements or change pace")
        elif boredom['level'] == 'Very Low':
            insights.append(f"✓ Low boredom indicates sustained interest")
        
        # Confusion analysis
        confusion = predictions['Confusion']
        if confusion['level'] in ['High', 'Very High']:
            insights.append(f"⚠️ Confusion detected ({confusion['confidence']*100:.1f}% confidence)")
            insights.append("Recommendation: Clarify current topic or provide examples")
        
        # Frustration analysis
        frustration = predictions['Frustration']
        if frustration['level'] in ['High', 'Very High']:
            insights.append(f"⚠️ Frustration detected ({frustration['confidence']*100:.1f}% confidence)")
            insights.append("Recommendation: Offer assistance or break down complex concepts")
        
        # Feature importance
        insights.append(f"\nMost informative facial region: {dominant_feature[0]} ({dominant_feature[1]:.1f}%)")
        
        return {
            'engagement_level': engagement_level,
            'engagement_score': engagement_score,
            'emoji': emoji,
            'color': color,
            'emotional_states': emotional_states,
            'insights': insights,
            'dominant_feature': dominant_feature[0],
            'feature_importance': attention
        }
    
    def visualize_analysis(self, 
                          image_path: str, 
                          prediction: Dict, 
                          explanation: Dict,
                          output_path: str = None):
        """
        Create comprehensive visualization of the analysis
        """
        # Read original image
        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Create figure with subplots
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # 1. Original image with engagement score
        ax1 = fig.add_subplot(gs[0:2, 0])
        ax1.imshow(image_rgb)
        ax1.set_title(f"{explanation['emoji']} Engagement: {explanation['engagement_level']}\n"
                     f"Score: {explanation['engagement_score']:.1f}%",
                     fontsize=14, fontweight='bold', 
                     color=explanation['color'])
        ax1.axis('off')
        
        # 2. Emotional states radar chart
        ax2 = fig.add_subplot(gs[0, 1:], projection='polar')
        emotions = list(prediction['predictions'].keys())
        confidences = [prediction['predictions'][e]['confidence'] * 100 
                      for e in emotions]
        
        angles = np.linspace(0, 2 * np.pi, len(emotions), endpoint=False)
        confidences = confidences + confidences[:1]
        angles = np.concatenate((angles, [angles[0]]))
        
        ax2.plot(angles, confidences, 'o-', linewidth=2, color='steelblue')
        ax2.fill(angles, confidences, alpha=0.25, color='steelblue')
        ax2.set_xticks(angles[:-1])
        ax2.set_xticklabels(emotions, fontsize=10)
        ax2.set_ylim(0, 100)
        ax2.set_title('Emotional State Confidence', fontsize=12, fontweight='bold', pad=20)
        ax2.grid(True)
        
        # 3. Feature importance bar chart
        ax3 = fig.add_subplot(gs[1, 1:])
        features = list(explanation['feature_importance'].keys())
        importance = list(explanation['feature_importance'].values())
        
        colors_map = plt.cm.viridis(np.linspace(0, 1, len(features)))
        bars = ax3.barh(features, importance, color=colors_map)
        ax3.set_xlabel('Contribution (%)', fontsize=10)
        ax3.set_title('Facial Feature Importance', fontsize=12, fontweight='bold')
        ax3.set_xlim(0, max(importance) * 1.1)
        
        # Add value labels
        for i, (feat, val) in enumerate(zip(features, importance)):
            ax3.text(val + 0.5, i, f'{val:.1f}%', va='center', fontsize=9)
        
        # 4. Emotion level breakdown
        ax4 = fig.add_subplot(gs[2, 0])
        emotion_data = []
        for emotion, data in prediction['predictions'].items():
            probs = data['probabilities']
            emotion_data.append(probs)
        
        emotion_data = np.array(emotion_data)
        levels = ['Very Low', 'Low', 'High', 'Very High']
        
        x = np.arange(len(emotions))
        width = 0.2
        
        for i, level in enumerate(levels):
            offset = (i - 1.5) * width
            ax4.bar(x + offset, emotion_data[:, i] * 100, width, 
                   label=level, alpha=0.8)
        
        ax4.set_xlabel('Emotion', fontsize=10)
        ax4.set_ylabel('Probability (%)', fontsize=10)
        ax4.set_title('Detailed Emotion Levels', fontsize=12, fontweight='bold')
        ax4.set_xticks(x)
        ax4.set_xticklabels(emotions, rotation=45, ha='right')
        ax4.legend(loc='upper right', fontsize=8)
        ax4.grid(axis='y', alpha=0.3)
        
        # 5. Insights text box
        ax5 = fig.add_subplot(gs[2, 1:])
        ax5.axis('off')
        
        insights_text = "🔍 AI INSIGHTS & RECOMMENDATIONS\n" + "="*60 + "\n\n"
        insights_text += "\n".join([f"• {insight}" for insight in explanation['insights']])
        
        ax5.text(0.05, 0.95, insights_text, 
                transform=ax5.transAxes,
                fontsize=9,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3),
                family='monospace')
        
        plt.suptitle(f'Engagement Analysis Report - {Path(image_path).name}',
                    fontsize=16, fontweight='bold', y=0.98)
        
        # Save or show
        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            print(f"✓ Visualization saved: {output_path}")
        else:
            plt.tight_layout()
            plt.show()
        
        plt.close()
    
    def analyze_image(self, 
                     image_path: str, 
                     visualize: bool = True,
                     save_report: bool = True) -> Dict:
        """
        Complete analysis pipeline for a single image
        
        Args:
            image_path: Path to image file
            visualize: Generate visualization
            save_report: Save JSON report
            
        Returns:
            Complete analysis results
        """
        print(f"\n{'='*70}")
        print(f"  ANALYZING IMAGE: {Path(image_path).name}")
        print(f"{'='*70}\n")
        
        # Step 1: Extract features
        print("Step 1: Extracting facial features...")
        features = self.extract_facial_features(image_path)
        
        if features is None:
            print("❌ No face detected in the image!")
            print("   Please ensure:")
            print("   • Face is clearly visible")
            print("   • Good lighting conditions")
            print("   • Face is front-facing")
            return None
        
        print(f"✓ Extracted {len(features)} facial features")
        
        # Step 2: Create sequence (repeat for 30 frames as required by model)
        print("\nStep 2: Preparing features for ensemble model...")
        feature_sequence = np.tile(features, (30, 1))  # Shape: (30, 35)
        
        # Step 3: Get ensemble prediction
        print("Step 3: Running ensemble prediction...")
        prediction = self.detector.predict(feature_sequence)
        print(f"✓ Engagement Score: {prediction['engagement_score']:.1f}%")
        
        # Step 4: Analyze attention patterns
        print("\nStep 4: Analyzing facial feature importance...")
        attention = self.analyze_attention_patterns(features)
        
        print("\nFeature Importance:")
        for feature, importance in sorted(attention.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {feature:15s}: {importance:5.1f}%")
        
        # Step 5: Generate explanations
        print("\nStep 5: Generating AI explanations...")
        explanation = self.explain_prediction(prediction, attention)
        
        # Step 6: Display results
        print(f"\n{'='*70}")
        print(f"  {explanation['emoji']} ANALYSIS RESULTS")
        print(f"{'='*70}\n")
        
        print(f"Engagement Level: {explanation['engagement_level']}")
        print(f"Engagement Score: {explanation['engagement_score']:.1f}%\n")
        
        print("Emotional States:")
        for emotion, data in explanation['emotional_states'].items():
            print(f"  • {emotion:12s}: {data['level']:10s} ({data['confidence']:5.1f}% confidence)")
        
        print(f"\n{'='*70}")
        print("AI INSIGHTS & RECOMMENDATIONS")
        print(f"{'='*70}\n")
        for insight in explanation['insights']:
            print(f"{insight}")
        
        # Compile complete report
        report = {
            'timestamp': datetime.now().isoformat(),
            'image_path': str(image_path),
            'prediction': {
                'engagement_score': float(prediction['engagement_score']),
                'mode': prediction['mode'],
                'emotions': {
                    emotion: {
                        'level': data['level'],
                        'confidence': float(data['confidence']),
                        'probabilities': [float(p) for p in data['probabilities']]
                    }
                    for emotion, data in prediction['predictions'].items()
                }
            },
            'feature_analysis': {
                'feature_importance': {k: float(v) for k, v in attention.items()},
                'dominant_feature': explanation['dominant_feature']
            },
            'explanation': {
                'engagement_level': explanation['engagement_level'],
                'insights': explanation['insights']
            }
        }
        
        # Step 7: Save report
        if save_report:
            report_path = Path(image_path).parent / f"analysis_{Path(image_path).stem}.json"
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n✓ Detailed report saved: {report_path}")
        
        # Step 8: Create visualization
        if visualize:
            print("\nGenerating visualization...")
            viz_path = Path(image_path).parent / f"analysis_{Path(image_path).stem}.png"
            self.visualize_analysis(image_path, prediction, explanation, str(viz_path))
        
        print(f"\n{'='*70}")
        print("  ✓ ANALYSIS COMPLETE!")
        print(f"{'='*70}\n")
        
        return report
    
    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, 'detector'):
            self.detector.shutdown()
        if hasattr(self, 'face_mesh'):
            self.face_mesh.close()


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description='Analyze student engagement from a single image',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze an image with default settings
  python analyze_image.py photo.jpg
  
  # Use fast mode without visualization
  python analyze_image.py photo.jpg --mode fast --no-viz
  
  # Analyze without saving report
  python analyze_image.py photo.jpg --no-report
  
Modes:
  fast      - Quick analysis (~66ms, Transformer only)
  balanced  - Balanced accuracy/speed (~126ms, 2 models) [DEFAULT]
  accurate  - Maximum accuracy (~173ms, all 3 models)
        """
    )
    
    parser.add_argument('image', type=str,
                       help='Path to the image file')
    parser.add_argument('--mode', type=str, default='balanced',
                       choices=['fast', 'balanced', 'accurate'],
                       help='Prediction mode (default: balanced)')
    parser.add_argument('--no-viz', action='store_true',
                       help='Skip visualization generation')
    parser.add_argument('--no-report', action='store_true',
                       help='Skip JSON report generation')
    
    args = parser.parse_args()
    
    # Validate image path
    if not Path(args.image).exists():
        print(f"❌ Error: Image not found: {args.image}")
        sys.exit(1)
    
    # Create analyzer
    analyzer = ImageEngagementAnalyzer(mode=args.mode)
    
    try:
        # Analyze image
        result = analyzer.analyze_image(
            args.image,
            visualize=not args.no_viz,
            save_report=not args.no_report
        )
        
        if result is None:
            sys.exit(1)
            
    finally:
        analyzer.cleanup()


if __name__ == '__main__':
    main()
