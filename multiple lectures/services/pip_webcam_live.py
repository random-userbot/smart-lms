"""
Smart LMS - Picture-in-Picture Webcam Live Service
Real-time webcam capture with OpenFace integration, ensemble ML, and frame logging
"""

import cv2
import numpy as np
import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import av
from typing import Dict, Optional, Callable
from datetime import datetime
import os
import uuid
import logging
from threading import Thread, Lock
import time
import json

from services.openface_processor import get_openface_processor

# Configure logging FIRST
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import ensemble detector
try:
    from services.ensemble_engagement import create_ensemble_detector
    ENSEMBLE_AVAILABLE = True
    logger.info("✅ Ensemble detector imported successfully")
except ImportError as e:
    ENSEMBLE_AVAILABLE = False
    logger.error(f"❌ Failed to import ensemble detector: {e}")
except Exception as e:
    ENSEMBLE_AVAILABLE = False
    logger.error(f"❌ Unexpected error importing ensemble detector: {e}")


class PiPWebcamLive:
    """
    Picture-in-Picture webcam with real-time OpenFace processing and ensemble ML
    Captures frames every second, extracts features, saves to captured_frames
    Uses ensemble model for improved engagement predictions with explainable AI
    """
    
    def __init__(self, lecture_id: str, course_id: str, student_id: str, use_ensemble: bool = True, ensemble_mode: str = "fast"):
        """
        Initialize PiP webcam
        
        Args:
            lecture_id: Current lecture ID
            course_id: Current course ID
            student_id: Current student ID
            use_ensemble: Enable ensemble ML model for predictions
            ensemble_mode: "fast" (66ms), "balanced" (126ms), "accurate" (173ms)
        """
        self.lecture_id = lecture_id
        self.course_id = course_id
        self.student_id = student_id
        
        # Generate session ID
        self.session_id = f"{student_id}_{lecture_id}_{uuid.uuid4().hex[:8]}"
        
        # Initialize OpenFace processor
        self.openface = get_openface_processor()
        self.openface.set_session_id(self.session_id)
        
        # Initialize ensemble detector
        self.use_ensemble = use_ensemble and ENSEMBLE_AVAILABLE
        self.ensemble_detector = None
        self.feature_buffer = []  # Buffer for 30-frame sequences
        self.ensemble_predictions = []
        
        logger.info(f"=== ENSEMBLE INITIALIZATION ===")
        logger.info(f"use_ensemble parameter: {use_ensemble}")
        logger.info(f"ENSEMBLE_AVAILABLE: {ENSEMBLE_AVAILABLE}")
        logger.info(f"self.use_ensemble: {self.use_ensemble}")
        
        if self.use_ensemble:
            try:
                logger.info(f"Creating ensemble detector in '{ensemble_mode}' mode...")
                self.ensemble_detector = create_ensemble_detector(mode=ensemble_mode)
                logger.info(f"✅ Ensemble detector initialized successfully in '{ensemble_mode}' mode")
            except Exception as e:
                logger.error(f"❌ Failed to initialize ensemble detector: {e}")
                import traceback
                traceback.print_exc()
                self.use_ensemble = False
        else:
            logger.warning(f"⚠️ Ensemble detector NOT initialized (use_ensemble={use_ensemble}, ENSEMBLE_AVAILABLE={ENSEMBLE_AVAILABLE})")
        
        # Frame capture settings
        self.capture_interval = 1.0  # seconds
        self.last_capture_time = 0
        self.frame_count = 0
        
        # Directories
        self.captured_frames_dir = "ml_data/captured_frames"
        self.engagement_logs_dir = "ml_data/engagement_logs"
        self.analysis_reports_dir = "ml_data/ensemble_analysis_reports"
        
        # Detailed analytics directories
        self.detailed_analytics_base = "ml_data/ensemble_detailed_analytics"
        self.detailed_faces_dir = f"{self.detailed_analytics_base}/captured_faces"
        self.detailed_emotions_dir = f"{self.detailed_analytics_base}/emotion_logs"
        self.detailed_features_dir = f"{self.detailed_analytics_base}/feature_vectors"
        self.detailed_analysis_dir = f"{self.detailed_analytics_base}/analysis_reports"
        self.detailed_suggestions_dir = f"{self.detailed_analytics_base}/suggestions"
        
        # Create all directories
        for dir_path in [self.captured_frames_dir, self.engagement_logs_dir, self.analysis_reports_dir,
                         self.detailed_faces_dir, self.detailed_emotions_dir, self.detailed_features_dir,
                         self.detailed_analysis_dir, self.detailed_suggestions_dir]:
            os.makedirs(dir_path, exist_ok=True)
        
        # Session data
        self.session_data = {
            'session_id': self.session_id,
            'student_id': student_id,
            'lecture_id': lecture_id,
            'course_id': course_id,
            'start_time': datetime.utcnow().isoformat(),
            'total_frames': 0,
            'engagement_scores': [],
            'ensemble_scores': [],
            'use_ensemble': self.use_ensemble,
            'ensemble_mode': ensemble_mode if self.use_ensemble else None
        }
        
        # Thread-safe engagement data
        self.current_engagement = {
            'score': 0.0,
            'ensemble_score': 0.0,
            'status': 'no_face',
            'frame_count': 0,
            'emotions': {}
        }
        self.engagement_lock = Lock()
        
        logger.info(f"PiPWebcamLive initialized for session {self.session_id} | Ensemble: {self.use_ensemble}")
    
    def video_frame_callback(self, frame: av.VideoFrame) -> av.VideoFrame:
        """
        Process each video frame from webcam
        
        Args:
            frame: Video frame from streamlit-webrtc
        
        Returns:
            Processed frame with annotations
        """
        # Convert to numpy array
        img = frame.to_ndarray(format="bgr24")
        
        # Get current time
        current_time = time.time()
        
        # Capture frame every second
        if current_time - self.last_capture_time >= self.capture_interval:
            self.last_capture_time = current_time
            self.frame_count += 1
            
            # Process with OpenFace
            engagement_data = self.openface.process_frame(
                img, 
                lecture_id=self.lecture_id, 
                course_id=self.course_id
            )
            
            # Add features to buffer for ensemble prediction
            if self.use_ensemble and engagement_data['face_detected']:
                # Extract 35-dimensional features from OpenFace data
                features = self._extract_features_for_ensemble(engagement_data)
                if features is not None:
                    self.feature_buffer.append(features)
                    
                    # Keep buffer at 30 frames max
                    if len(self.feature_buffer) > 30:
                        self.feature_buffer.pop(0)
                    
                    logger.debug(f"Feature buffer size: {len(self.feature_buffer)}/30")
                    
                    # Run ensemble prediction when we have enough frames (>= 30)
                    if len(self.feature_buffer) >= 30:
                        logger.info(f"🚀 Running ensemble prediction (buffer size: {len(self.feature_buffer)})")
                        ensemble_result = self._run_ensemble_prediction()
                        engagement_data['ensemble_result'] = ensemble_result
                        logger.info(f"✅ Ensemble prediction complete: {ensemble_result['engagement_score']:.2f}")
                        
                        # Save detailed analytics when ensemble prediction is available
                        self._save_detailed_analytics(img, engagement_data, features, ensemble_result)
                    else:
                        logger.debug(f"Waiting for buffer to fill: {len(self.feature_buffer)}/30")
                else:
                    logger.warning("⚠️ Feature extraction failed")
                    # Save without ensemble if features extraction failed
                    if self.frame_count % 5 == 0:  # Save every 5th frame
                        self._save_detailed_analytics(img, engagement_data, None, None)
            else:
                if not self.use_ensemble:
                    logger.debug("Ensemble disabled")
                if not engagement_data['face_detected']:
                    logger.debug("No face detected")
                # Save without ensemble if not using ensemble or no face
                if self.frame_count % 5 == 0:  # Save every 5th frame
                    self._save_detailed_analytics(img, engagement_data, None, None)
            
            # Save frame with metadata
            self._save_captured_frame(img, engagement_data)
            
            # Update current engagement
            with self.engagement_lock:
                self.current_engagement['score'] = engagement_data['engagement_score']
                self.current_engagement['status'] = engagement_data['status']
                self.current_engagement['frame_count'] = self.frame_count
                
                # Add ensemble data if available
                if 'ensemble_result' in engagement_data:
                    self.current_engagement['ensemble_score'] = engagement_data['ensemble_result']['engagement_score']
                    self.current_engagement['emotions'] = engagement_data['ensemble_result']['predictions']
            
            # Add to session data
            self.session_data['engagement_scores'].append(engagement_data['engagement_score'])
            if 'ensemble_result' in engagement_data:
                self.session_data['ensemble_scores'].append(engagement_data['ensemble_result']['engagement_score'])
            self.session_data['total_frames'] = self.frame_count
            
            # Periodically save to CSV and generate reports
            if self.frame_count % 10 == 0:
                self.openface.save_features_to_csv()
                if self.use_ensemble and len(self.ensemble_predictions) > 0:
                    self._save_ensemble_analysis_report()
        
        # Draw engagement overlay on frame
        annotated_frame = self._draw_engagement_overlay(img, self.current_engagement)
        
        return av.VideoFrame.from_ndarray(annotated_frame, format="bgr24")
    
    def _save_captured_frame(self, frame: np.ndarray, engagement_data: Dict):
        """
        Save captured frame with metadata
        
        Args:
            frame: BGR image
            engagement_data: OpenFace features and engagement score
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{self.session_id}_{timestamp}.jpg"
        filepath = os.path.join(self.captured_frames_dir, filename)
        
        # Save frame
        cv2.imwrite(filepath, frame)
        
        # Save metadata to engagement logs
        log_entry = {
            'timestamp': engagement_data['timestamp'],
            'session_id': self.session_id,
            'student_id': self.student_id,
            'lecture_id': self.lecture_id,
            'course_id': self.course_id,
            'frame_path': filepath,
            'engagement_score': engagement_data['engagement_score'],
            'status': engagement_data['status'],
            'face_detected': engagement_data['face_detected'],
            'gaze_angle_x': engagement_data.get('gaze_angle_x', 0),
            'gaze_angle_y': engagement_data.get('gaze_angle_y', 0),
            'head_pose_rx': engagement_data.get('pose_Rx', 0),
            'head_pose_ry': engagement_data.get('pose_Ry', 0),
            'head_pose_rz': engagement_data.get('pose_Rz', 0)
        }
        
        # Add ensemble data if available
        if 'ensemble_result' in engagement_data:
            log_entry['ensemble_score'] = engagement_data['ensemble_result']['engagement_score']
            for emotion, data in engagement_data['ensemble_result']['predictions'].items():
                log_entry[f'{emotion.lower()}_level'] = data['level']
                log_entry[f'{emotion.lower()}_confidence'] = data['confidence']
        
        # Append to engagement log CSV
        self._append_to_engagement_log(log_entry)
        
        logger.debug(f"Saved frame {self.frame_count}: {filename} | Score: {engagement_data['engagement_score']}")
    
    def _extract_features_for_ensemble(self, engagement_data: Dict) -> Optional[np.ndarray]:
        """
        Extract 35-dimensional feature vector from OpenFace data for ensemble model
        
        Args:
            engagement_data: Dictionary with OpenFace features
            
        Returns:
            35-dimensional numpy array or None
        """
        try:
            # Extract key features from OpenFace (matches training format)
            features = []
            
            # Gaze features (2)
            features.extend([
                engagement_data.get('gaze_angle_x', 0),
                engagement_data.get('gaze_angle_y', 0)
            ])
            
            # Head pose features (6)
            features.extend([
                engagement_data.get('pose_Tx', 0),
                engagement_data.get('pose_Ty', 0),
                engagement_data.get('pose_Tz', 0),
                engagement_data.get('pose_Rx', 0),
                engagement_data.get('pose_Ry', 0),
                engagement_data.get('pose_Rz', 0)
            ])
            
            # Action units (27 key AUs)
            au_names = [
                'AU01_r', 'AU02_r', 'AU04_r', 'AU05_r', 'AU06_r', 'AU07_r', 'AU09_r', 
                'AU10_r', 'AU12_r', 'AU14_r', 'AU15_r', 'AU17_r', 'AU20_r', 'AU23_r',
                'AU25_r', 'AU26_r', 'AU45_r',
                'AU01_c', 'AU02_c', 'AU04_c', 'AU05_c', 'AU06_c', 'AU07_c', 'AU09_c',
                'AU12_c', 'AU14_c', 'AU15_c'
            ]
            
            for au in au_names:
                features.append(engagement_data.get(au, 0))
            
            # Convert to numpy array and normalize
            features = np.array(features, dtype=np.float32)
            
            # Basic normalization
            if len(features) == 35:
                features = (features - features.mean()) / (features.std() + 1e-8)
                return features
            else:
                logger.warning(f"Feature vector has {len(features)} dimensions, expected 35")
                return None
                
        except Exception as e:
            logger.error(f"Failed to extract features for ensemble: {e}")
            return None
    
    def _run_ensemble_prediction(self) -> Dict:
        """
        Run ensemble prediction on buffered features
        
        Returns:
            Dictionary with ensemble prediction results
        """
        try:
            # Convert buffer to numpy array (30, 35)
            feature_sequence = np.array(self.feature_buffer)
            
            # Run ensemble prediction
            prediction = self.ensemble_detector.predict(feature_sequence)
            
            # Store prediction
            self.ensemble_predictions.append({
                'timestamp': datetime.utcnow().isoformat(),
                'frame_number': self.frame_count,
                'prediction': prediction
            })
            
            logger.info(f"Ensemble prediction: {prediction['engagement_score']:.1f}% | Mode: {prediction['mode']}")
            
            return prediction
            
        except Exception as e:
            logger.error(f"Ensemble prediction failed: {e}")
            return {
                'engagement_score': 0.0,
                'mode': 'error',
                'predictions': {}
            }
    
    def _save_ensemble_analysis_report(self):
        """Save comprehensive ensemble analysis report"""
        try:
            report = {
                'session_id': self.session_id,
                'student_id': self.student_id,
                'lecture_id': self.lecture_id,
                'course_id': self.course_id,
                'timestamp': datetime.utcnow().isoformat(),
                'total_frames': self.frame_count,
                'ensemble_predictions': len(self.ensemble_predictions),
                'predictions': self.ensemble_predictions[-10:],  # Last 10 predictions
                'statistics': self._calculate_ensemble_statistics()
            }
            
            # Save report
            report_file = os.path.join(
                self.analysis_reports_dir, 
                f"ensemble_analysis_{self.session_id}.json"
            )
            
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"Saved ensemble analysis report: {report_file}")
            
        except Exception as e:
            logger.error(f"Failed to save ensemble report: {e}")
    
    def _calculate_ensemble_statistics(self) -> Dict:
        """Calculate statistics from ensemble predictions"""
        if not self.ensemble_predictions:
            return {}
        
        scores = [p['prediction']['engagement_score'] for p in self.ensemble_predictions]
        
        # Emotion aggregation
        emotion_stats = {}
        for emotion in ['Boredom', 'Engagement', 'Confusion', 'Frustration']:
            levels = []
            confidences = []
            for p in self.ensemble_predictions:
                if emotion in p['prediction']['predictions']:
                    levels.append(p['prediction']['predictions'][emotion]['level'])
                    confidences.append(p['prediction']['predictions'][emotion]['confidence'])
            
            if confidences:
                emotion_stats[emotion] = {
                    'avg_confidence': float(np.mean(confidences)),
                    'most_common_level': max(set(levels), key=levels.count) if levels else 'Unknown'
                }
        
        return {
            'avg_engagement': float(np.mean(scores)),
            'min_engagement': float(np.min(scores)),
            'max_engagement': float(np.max(scores)),
            'std_engagement': float(np.std(scores)),
            'emotion_analysis': emotion_stats
        }
    
    def _save_detailed_analytics(self, frame: np.ndarray, engagement_data: Dict, 
                                  features: np.ndarray, ensemble_result: Optional[Dict]):
        """
        Save comprehensive detailed analytics for ensemble predictions
        
        Args:
            frame: Captured frame image
            engagement_data: OpenFace engagement data
            features: 35-dimensional feature vector
            ensemble_result: Ensemble prediction result
        """
        timestamp = datetime.utcnow()
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S_%f")
        
        # 1. Save high-quality captured face
        face_filename = f"{self.session_id}_frame_{self.frame_count}_{timestamp_str}.jpg"
        face_path = os.path.join(self.detailed_faces_dir, face_filename)
        cv2.imwrite(face_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
        
        # 2. ALWAYS save feature vector (extract if not provided)
        if features is None and engagement_data.get('face_detected'):
            features = self._extract_features_for_ensemble(engagement_data)
        
        if features is not None:
            feature_filename = f"{self.session_id}_features_{self.frame_count}_{timestamp_str}.npy"
            feature_path = os.path.join(self.detailed_features_dir, feature_filename)
            np.save(feature_path, features)
        
        # 3. ALWAYS save emotion log (with or without ensemble)
        emotion_data = {
            'timestamp': timestamp.isoformat(),
            'session_id': self.session_id,
            'frame_number': self.frame_count,
            'has_ensemble': ensemble_result is not None,
            'openface_engagement': engagement_data['engagement_score'],
            'emotions': {}
        }
        
        if ensemble_result:
            emotion_data['ensemble_engagement'] = ensemble_result['engagement_score']
            emotion_data['mode'] = ensemble_result['mode']
            
            for emotion, data in ensemble_result['predictions'].items():
                emotion_data['emotions'][emotion] = {
                    'level': data['level'],
                    'class_id': data['class_id'],
                    'confidence': float(data['confidence']),
                    'probabilities': {
                        'Very Low': float(data['probabilities'][0]),
                        'Low': float(data['probabilities'][1]),
                        'High': float(data['probabilities'][2]),
                        'Very High': float(data['probabilities'][3])
                    }
                }
        
        emotion_filename = f"{self.session_id}_emotions_{self.frame_count}_{timestamp_str}.json"
        emotion_path = os.path.join(self.detailed_emotions_dir, emotion_filename)
        with open(emotion_path, 'w') as f:
            json.dump(emotion_data, f, indent=2)
        
        # 4. Generate and save COMPREHENSIVE analysis report with explainable AI
        analysis = self._generate_comprehensive_analysis(engagement_data, ensemble_result, features)
        analysis_filename = f"{self.session_id}_analysis_{self.frame_count}_{timestamp_str}.json"
        analysis_path = os.path.join(self.detailed_analysis_dir, analysis_filename)
        with open(analysis_path, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        # 5. Generate and save suggestions
        suggestions = self._generate_suggestions(ensemble_result if ensemble_result else {'predictions': {}, 'engagement_score': engagement_data['engagement_score']})
        if suggestions:
            suggestions_data = {
                'timestamp': timestamp.isoformat(),
                'frame_number': self.frame_count,
                'engagement_score': ensemble_result['engagement_score'] if ensemble_result else engagement_data['engagement_score'],
                'suggestions': suggestions
            }
            suggestions_filename = f"{self.session_id}_suggestions_{self.frame_count}_{timestamp_str}.json"
            suggestions_path = os.path.join(self.detailed_suggestions_dir, suggestions_filename)
            with open(suggestions_path, 'w') as f:
                json.dump(suggestions_data, f, indent=2)
        
        logger.debug(f"Saved detailed analytics for frame {self.frame_count}")
    
    def _generate_comprehensive_analysis(self, engagement_data: Dict, ensemble_result: Optional[Dict],
                                          features: Optional[np.ndarray]) -> Dict:
        """
        Generate COMPREHENSIVE frame analysis with explainable AI and detailed metrics
        
        Args:
            engagement_data: OpenFace engagement data
            ensemble_result: Ensemble prediction result
            features: 35-dimensional feature vector
            
        Returns:
            Comprehensive analysis dictionary with explainable AI
        """
        analysis = {
            'timestamp': datetime.utcnow().isoformat(),
            'frame_number': self.frame_count,
            'session_id': self.session_id,
            'analysis_version': '2.0_explainable_ai',
            'openface_metrics': {
                'engagement_score': engagement_data['engagement_score'],
                'status': engagement_data['status'],
                'face_detected': engagement_data['face_detected'],
                'confidence': engagement_data.get('confidence', 1.0),
                'gaze': {
                    'angle_x': engagement_data.get('gaze_angle_x', 0),
                    'angle_y': engagement_data.get('gaze_angle_y', 0),
                    'interpretation': self._interpret_gaze(
                        engagement_data.get('gaze_angle_x', 0),
                        engagement_data.get('gaze_angle_y', 0)
                    )
                },
                'head_pose': {
                    'rotation_x': engagement_data.get('pose_Rx', 0),
                    'rotation_y': engagement_data.get('pose_Ry', 0),
                    'rotation_z': engagement_data.get('pose_Rz', 0),
                    'interpretation': self._interpret_head_pose(
                        engagement_data.get('pose_Rx', 0),
                        engagement_data.get('pose_Ry', 0),
                        engagement_data.get('pose_Rz', 0)
                    )
                }
            }
        }
        
        # Add comprehensive feature breakdown
        if features is not None:
            analysis['feature_analysis'] = self._analyze_features(features, engagement_data)
        
        # Add ensemble metrics with EXPLAINABLE AI
        if ensemble_result:
            ensemble_score = ensemble_result['engagement_score']
            openface_score = engagement_data['engagement_score']
            
            analysis['ensemble_metrics'] = {
                'engagement_score': ensemble_score,
                'mode': ensemble_result['mode'],
                'improvement_over_openface': ensemble_score - openface_score,
                'improvement_percentage': ((ensemble_score - openface_score) / openface_score * 100) if openface_score > 0 else 0,
                'emotions': {},
                'explainable_ai': self._explain_ensemble_score(ensemble_result, engagement_data, features)
            }
            
            for emotion, data in ensemble_result['predictions'].items():
                analysis['ensemble_metrics']['emotions'][emotion] = {
                    'level': data['level'],
                    'class_id': data['class_id'],
                    'confidence': float(data['confidence']),
                    'all_probabilities': {
                        'Very Low': float(data['probabilities'][0]),
                        'Low': float(data['probabilities'][1]),
                        'High': float(data['probabilities'][2]),
                        'Very High': float(data['probabilities'][3])
                    },
                    'interpretation': self._interpret_emotion(emotion, data)
                }
        
        # Add statistical context
        analysis['session_context'] = {
            'total_frames_processed': self.frame_count,
            'average_engagement_so_far': float(np.mean(self.session_data['engagement_scores'])) if self.session_data['engagement_scores'] else 0,
            'engagement_trend': self._calculate_engagement_trend()
        }
        
        return analysis
    
    def _generate_suggestions(self, ensemble_result: Optional[Dict]) -> list:
        """
        Generate actionable suggestions based on ensemble predictions
        
        Args:
            ensemble_result: Ensemble prediction result
            
        Returns:
            List of suggestion strings
        """
        if not ensemble_result:
            return []
        
        suggestions = []
        engagement_score = ensemble_result['engagement_score']
        predictions = ensemble_result['predictions']
        
        # Engagement level suggestions
        if engagement_score >= 75:
            suggestions.append("✅ Excellent engagement! Keep up the great focus.")
        elif engagement_score >= 50:
            suggestions.append("👍 Good engagement level. Stay focused on the content.")
        elif engagement_score >= 25:
            suggestions.append("⚠️ Moderate engagement. Try to minimize distractions.")
        else:
            suggestions.append("❌ Low engagement detected. Consider taking a short break or changing environment.")
        
        # Boredom suggestions
        boredom = predictions.get('Boredom', {})
        if boredom.get('level') in ['High', 'Very High']:
            confidence = boredom.get('confidence', 0) * 100
            suggestions.append(f"😴 High boredom detected ({confidence:.0f}% confidence)")
            suggestions.append("💡 Suggestion: Try interactive elements, take notes, or switch to a different learning method")
        
        # Confusion suggestions
        confusion = predictions.get('Confusion', {})
        if confusion.get('level') in ['High', 'Very High']:
            confidence = confusion.get('confidence', 0) * 100
            suggestions.append(f"😕 Confusion detected ({confidence:.0f}% confidence)")
            suggestions.append("💡 Suggestion: Pause and review the material, or seek clarification on difficult concepts")
        
        # Frustration suggestions
        frustration = predictions.get('Frustration', {})
        if frustration.get('level') in ['High', 'Very High']:
            confidence = frustration.get('confidence', 0) * 100
            suggestions.append(f"😤 Frustration detected ({confidence:.0f}% confidence)")
            suggestions.append("💡 Suggestion: Take a break, try a different approach, or reach out for help")
        
        # Positive reinforcement
        engagement_emotion = predictions.get('Engagement', {})
        if engagement_emotion.get('level') in ['High', 'Very High']:
            suggestions.append("🎯 High cognitive engagement detected - you're learning effectively!")
        
        return suggestions
    
    def _interpret_gaze(self, angle_x: float, angle_y: float) -> Dict:
        """Interpret gaze angles for explainability"""
        interpretation = {
            'direction': 'center',
            'attention_level': 'focused',
            'description': ''
        }
        
        # Horizontal gaze (X-axis)
        if abs(angle_x) < 0.2:
            h_dir = 'center'
        elif angle_x > 0:
            h_dir = 'right'
        else:
            h_dir = 'left'
        
        # Vertical gaze (Y-axis)
        if abs(angle_y) < 0.2:
            v_dir = 'center'
        elif angle_y > 0:
            v_dir = 'down'
        else:
            v_dir = 'up'
        
        interpretation['direction'] = f"{v_dir}_{h_dir}"
        
        # Determine attention level based on gaze dispersion
        gaze_magnitude = np.sqrt(angle_x**2 + angle_y**2)
        if gaze_magnitude < 0.3:
            interpretation['attention_level'] = 'highly_focused'
            interpretation['description'] = 'Direct eye gaze - strong attention to screen'
        elif gaze_magnitude < 0.6:
            interpretation['attention_level'] = 'moderately_focused'
            interpretation['description'] = 'Slightly averted gaze - partial attention'
        else:
            interpretation['attention_level'] = 'distracted'
            interpretation['description'] = 'Gaze away from screen - likely distracted'
        
        return interpretation
    
    def _interpret_head_pose(self, rx: float, ry: float, rz: float) -> Dict:
        """Interpret head pose for explainability"""
        interpretation = {
            'posture': 'neutral',
            'engagement_indicator': 'positive',
            'description': ''
        }
        
        # Analyze head orientation
        if abs(ry) < 15:  # Facing forward
            if abs(rx) < 10:  # Level head
                interpretation['posture'] = 'attentive'
                interpretation['description'] = 'Upright posture, facing screen directly'
            elif rx > 10:  # Head tilted down
                interpretation['posture'] = 'reading_focused'
                interpretation['description'] = 'Head tilted down - reading or taking notes'
            else:  # Head tilted up
                interpretation['posture'] = 'relaxed'
                interpretation['description'] = 'Head tilted up - relaxed posture'
        elif abs(ry) > 30:  # Head turned significantly
            interpretation['posture'] = 'distracted'
            interpretation['engagement_indicator'] = 'negative'
            interpretation['description'] = 'Head turned away - attention elsewhere'
        else:  # Moderate turn
            interpretation['posture'] = 'partially_engaged'
            interpretation['engagement_indicator'] = 'neutral'
            interpretation['description'] = 'Head slightly turned - divided attention'
        
        # Factor in head roll (rz)
        if abs(rz) > 15:
            interpretation['description'] += ' | Head tilted sideways - possible fatigue or discomfort'
        
        return interpretation
    
    def _extract_action_units(self, engagement_data: Dict) -> Dict:
        """Extract and interpret facial action units"""
        aus = {}
        
        # Extract all AU_ prefixed features
        for key, value in engagement_data.items():
            if key.startswith('AU'):
                au_name = key
                au_value = value
                
                # Interpret common AUs
                interpretation = ''
                if 'AU01' in au_name:
                    interpretation = 'Inner brow raise - confusion/surprise'
                elif 'AU02' in au_name:
                    interpretation = 'Outer brow raise - interest/surprise'
                elif 'AU04' in au_name:
                    interpretation = 'Brow lower - concentration/confusion'
                elif 'AU05' in au_name:
                    interpretation = 'Upper lid raise - surprise/attention'
                elif 'AU06' in au_name:
                    interpretation = 'Cheek raise - positive emotion'
                elif 'AU07' in au_name:
                    interpretation = 'Lid tighten - focus/concentration'
                elif 'AU09' in au_name:
                    interpretation = 'Nose wrinkle - disgust/confusion'
                elif 'AU10' in au_name:
                    interpretation = 'Upper lip raise - disgust/dislike'
                elif 'AU12' in au_name:
                    interpretation = 'Lip corner pull - smile/positive'
                elif 'AU14' in au_name:
                    interpretation = 'Dimpler - smile'
                elif 'AU15' in au_name:
                    interpretation = 'Lip corner depress - sadness/frustration'
                elif 'AU17' in au_name:
                    interpretation = 'Chin raise - dislike/doubt'
                elif 'AU20' in au_name:
                    interpretation = 'Lip stretch - stress/tension'
                elif 'AU23' in au_name:
                    interpretation = 'Lip tighten - stress/concentration'
                elif 'AU25' in au_name:
                    interpretation = 'Lips part - surprise/confusion'
                elif 'AU26' in au_name:
                    interpretation = 'Jaw drop - surprise/shock'
                elif 'AU45' in au_name:
                    interpretation = 'Blink - normal/stress indicator'
                
                aus[au_name] = {
                    'value': float(au_value) if au_value is not None else 0.0,
                    'active': float(au_value) > 0.5 if au_value is not None else False,
                    'interpretation': interpretation
                }
        
        return aus
    
    def _analyze_features(self, features: np.ndarray, engagement_data: Dict) -> Dict:
        """Comprehensive feature analysis with interpretations"""
        # Features: [gaze_x, gaze_y, pose_rx, pose_ry, pose_rz, pose_tx, pose_ty, pose_tz, ...AUs]
        
        analysis = {
            'feature_vector_shape': features.shape,
            'feature_statistics': {
                'mean': float(np.mean(features)),
                'std': float(np.std(features)),
                'min': float(np.min(features)),
                'max': float(np.max(features)),
                'non_zero_count': int(np.count_nonzero(features))
            },
            'feature_breakdown': {
                'gaze_features': {
                    'gaze_x': float(features[0]),
                    'gaze_y': float(features[1]),
                    'magnitude': float(np.sqrt(features[0]**2 + features[1]**2)),
                    'interpretation': 'Low magnitude = focused, High = distracted'
                },
                'head_pose_rotation': {
                    'pitch_rx': float(features[2]),
                    'yaw_ry': float(features[3]),
                    'roll_rz': float(features[4]),
                    'interpretation': 'Near zero = facing screen, Large values = turned away'
                },
                'head_pose_translation': {
                    'tx': float(features[5]) if len(features) > 5 else 0,
                    'ty': float(features[6]) if len(features) > 6 else 0,
                    'tz': float(features[7]) if len(features) > 7 else 0,
                    'interpretation': 'Distance and position relative to camera'
                },
                'action_units': {
                    'count': len(features) - 8,
                    'active_aus': int(np.sum(features[8:] > 0.5)) if len(features) > 8 else 0,
                    'mean_activation': float(np.mean(features[8:])) if len(features) > 8 else 0,
                    'interpretation': 'Facial expressions indicating emotional state'
                }
            },
            'engagement_indicators': {
                'gaze_stability': 'good' if np.sqrt(features[0]**2 + features[1]**2) < 0.5 else 'poor',
                'head_orientation': 'good' if abs(features[3]) < 20 else 'needs_attention',
                'facial_activity': 'active' if (len(features) > 8 and np.mean(features[8:]) > 0.3) else 'neutral'
            }
        }
        
        return analysis
    
    def _explain_ensemble_score(self, ensemble_result: Dict, engagement_data: Dict, 
                                 features: Optional[np.ndarray]) -> Dict:
        """
        EXPLAINABLE AI: Break down why ensemble assigned this score
        """
        predictions = ensemble_result['predictions']
        score = ensemble_result['engagement_score']
        
        explanation = {
            'final_score': score * 100,  # Convert to percentage
            'score_breakdown': {
                'engagement_level': predictions['Engagement']['level'],
                'engagement_confidence': float(predictions['Engagement']['confidence'] * 100),
                'primary_factors': [],
                'secondary_factors': []
            },
            'contributing_factors': {},
            'score_justification': '',
            'model_reasoning': []
        }
        
        # Analyze engagement dimension (primary factor)
        eng_class = predictions['Engagement']['class_id']
        eng_conf = predictions['Engagement']['confidence']
        
        if eng_class >= 2:  # High or Very High
            explanation['score_breakdown']['primary_factors'].append(
                f"High engagement level detected ({predictions['Engagement']['level']}) with {eng_conf*100:.0f}% confidence"
            )
            explanation['model_reasoning'].append(
                "✅ Positive engagement indicators from temporal patterns in facial features"
            )
        else:
            explanation['score_breakdown']['primary_factors'].append(
                f"Low engagement level detected ({predictions['Engagement']['level']}) with {eng_conf*100:.0f}% confidence"
            )
            explanation['model_reasoning'].append(
                "⚠️ Limited engagement indicators from facial feature analysis"
            )
        
        # Analyze boredom (negative factor)
        boredom_class = predictions['Boredom']['class_id']
        boredom_conf = predictions['Boredom']['confidence']
        if boredom_class >= 2:
            explanation['contributing_factors']['boredom'] = {
                'impact': 'negative',
                'severity': 'high' if boredom_class == 3 else 'moderate',
                'confidence': float(boredom_conf * 100),
                'description': f"Model detected {predictions['Boredom']['level'].lower()} boredom patterns"
            }
            explanation['model_reasoning'].append(
                f"❌ Boredom indicators: {predictions['Boredom']['level']} ({boredom_conf*100:.0f}% confidence)"
            )
        
        # Analyze confusion (negative factor)
        confusion_class = predictions['Confusion']['class_id']
        confusion_conf = predictions['Confusion']['confidence']
        if confusion_class >= 2:
            explanation['contributing_factors']['confusion'] = {
                'impact': 'negative',
                'severity': 'high' if confusion_class == 3 else 'moderate',
                'confidence': float(confusion_conf * 100),
                'description': f"Model detected {predictions['Confusion']['level'].lower()} confusion patterns"
            }
            explanation['model_reasoning'].append(
                f"❌ Confusion indicators: {predictions['Confusion']['level']} ({confusion_conf*100:.0f}% confidence)"
            )
        
        # Analyze frustration (negative factor)
        frustration_class = predictions['Frustration']['class_id']
        frustration_conf = predictions['Frustration']['confidence']
        if frustration_class >= 2:
            explanation['contributing_factors']['frustration'] = {
                'impact': 'negative',
                'severity': 'high' if frustration_class == 3 else 'moderate',
                'confidence': float(frustration_conf * 100),
                'description': f"Model detected {predictions['Frustration']['level'].lower()} frustration patterns"
            }
            explanation['model_reasoning'].append(
                f"❌ Frustration indicators: {predictions['Frustration']['level']} ({frustration_conf*100:.0f}% confidence)"
            )
        
        # Add OpenFace comparison
        openface_score = engagement_data['engagement_score']
        score_diff = (score * 100) - openface_score
        
        explanation['score_breakdown']['secondary_factors'].append(
            f"OpenFace baseline: {openface_score:.1f}%"
        )
        explanation['score_breakdown']['secondary_factors'].append(
            f"Ensemble improvement: {score_diff:+.1f}%"
        )
        
        if score_diff > 10:
            explanation['model_reasoning'].append(
                "✨ Ensemble models detected subtle engagement cues missed by traditional analysis"
            )
        elif score_diff < -10:
            explanation['model_reasoning'].append(
                "⚠️ Ensemble models identified negative patterns (boredom/confusion) affecting engagement"
            )
        
        # Feature-based justification
        if features is not None:
            gaze_mag = np.sqrt(features[0]**2 + features[1]**2)
            head_yaw = abs(features[3]) if len(features) > 3 else 0
            
            if gaze_mag < 0.3 and head_yaw < 15:
                explanation['score_breakdown']['secondary_factors'].append(
                    "Strong visual attention: Direct gaze and forward head pose"
                )
            elif gaze_mag > 0.6 or head_yaw > 30:
                explanation['score_breakdown']['secondary_factors'].append(
                    "Weak visual attention: Averted gaze or head turned away"
                )
            
            # AU analysis for emotional state
            if len(features) > 8:
                au_activity = np.mean(features[8:])
                if au_activity > 0.4:
                    explanation['score_breakdown']['secondary_factors'].append(
                        f"High facial expressiveness (AU activity: {au_activity:.2f}) - indicates cognitive processing"
                    )
        
        # Generate final justification
        if score > 0.75:
            explanation['score_justification'] = (
                f"Excellent engagement ({score*100:.0f}%) justified by: "
                f"Strong engagement signals, minimal distraction indicators, "
                f"and consistent attention patterns across temporal window."
            )
        elif score > 0.50:
            explanation['score_justification'] = (
                f"Good engagement ({score*100:.0f}%) justified by: "
                f"Moderate engagement indicators with some mixed signals. "
                f"Overall positive attention but with room for improvement."
            )
        elif score > 0.25:
            explanation['score_justification'] = (
                f"Low engagement ({score*100:.0f}%) justified by: "
                f"Limited engagement signals, presence of distraction/confusion indicators. "
                f"Attention quality needs improvement."
            )
        else:
            explanation['score_justification'] = (
                f"Very low engagement ({score*100:.0f}%) justified by: "
                f"Strong disengagement patterns, high boredom/confusion signals, "
                f"and inconsistent attention indicators."
            )
        
        return explanation
    
    def _interpret_emotion(self, emotion: str, data: Dict) -> str:
        """Interpret emotion prediction for human understanding"""
        level = data['level']
        confidence = data['confidence'] * 100
        class_id = data['class_id']
        
        interpretations = {
            'Boredom': {
                0: f"Student shows alertness and interest (confidence: {confidence:.0f}%)",
                1: f"Minimal boredom detected (confidence: {confidence:.0f}%)",
                2: f"Moderate boredom - content may be too easy or slow (confidence: {confidence:.0f}%)",
                3: f"High boredom - student disengaged from material (confidence: {confidence:.0f}%)"
            },
            'Engagement': {
                0: f"Very low cognitive engagement detected (confidence: {confidence:.0f}%)",
                1: f"Limited engagement with material (confidence: {confidence:.0f}%)",
                2: f"Good engagement - actively processing content (confidence: {confidence:.0f}%)",
                3: f"Excellent engagement - deep focus and learning (confidence: {confidence:.0f}%)"
            },
            'Confusion': {
                0: f"Clear understanding of content (confidence: {confidence:.0f}%)",
                1: f"Minor confusion points (confidence: {confidence:.0f}%)",
                2: f"Moderate confusion - may need clarification (confidence: {confidence:.0f}%)",
                3: f"High confusion - intervention recommended (confidence: {confidence:.0f}%)"
            },
            'Frustration': {
                0: f"Calm and patient learning state (confidence: {confidence:.0f}%)",
                1: f"Minor frustration detected (confidence: {confidence:.0f}%)",
                2: f"Moderate frustration - difficulty with content (confidence: {confidence:.0f}%)",
                3: f"High frustration - at risk of disengagement (confidence: {confidence:.0f}%)"
            }
        }
        
        return interpretations.get(emotion, {}).get(class_id, f"{level} {emotion.lower()} detected")
    
    def _calculate_engagement_trend(self) -> Dict:
        """Calculate engagement trend over session"""
        scores = self.session_data['engagement_scores']
        
        if len(scores) < 2:
            return {'trend': 'insufficient_data', 'direction': 'neutral', 'change': 0}
        
        # Calculate moving average
        recent_window = min(10, len(scores))
        recent_avg = np.mean(scores[-recent_window:])
        earlier_avg = np.mean(scores[:max(1, len(scores)//2)])
        
        change = recent_avg - earlier_avg
        
        if abs(change) < 5:
            direction = 'stable'
            trend = 'Engagement levels stable throughout session'
        elif change > 0:
            direction = 'improving'
            trend = f'Engagement improving (+{change:.1f}% from session start)'
        else:
            direction = 'declining'
            trend = f'Engagement declining ({change:.1f}% from session start)'
        
        return {
            'trend': trend,
            'direction': direction,
            'change': float(change),
            'recent_average': float(recent_avg),
            'session_average': float(np.mean(scores))
        }
    
    def _append_to_engagement_log(self, log_entry: Dict):
        """Append entry to engagement log CSV"""
        import csv
        
        log_file = os.path.join(self.engagement_logs_dir, f"engagement_log_{self.session_id}.csv")
        
        file_exists = os.path.exists(log_file)
        
        with open(log_file, 'a', newline='') as f:
            fieldnames = [
                'timestamp', 'session_id', 'student_id', 'lecture_id', 'course_id',
                'frame_path', 'engagement_score', 'status', 'face_detected',
                'gaze_angle_x', 'gaze_angle_y', 'head_pose_rx', 'head_pose_ry', 'head_pose_rz',
                # Ensemble fields
                'ensemble_score', 'boredom_level', 'boredom_confidence',
                'engagement_level', 'engagement_confidence',
                'confusion_level', 'confusion_confidence',
                'frustration_level', 'frustration_confidence'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(log_entry)
    
    def _draw_engagement_overlay(self, frame: np.ndarray, engagement: Dict) -> np.ndarray:
        """
        Draw engagement score and status overlay on frame with prominent ensemble display
        
        Args:
            frame: BGR image
            engagement: Current engagement data
        
        Returns:
            Annotated frame
        """
        h, w = frame.shape[:2]
        overlay = frame.copy()
        
        # Determine overlay height - larger for more info
        has_ensemble = engagement.get('ensemble_score', 0) > 0
        overlay_height = 140 if has_ensemble else 80
        
        # Draw semi-transparent background for text
        cv2.rectangle(overlay, (10, h - overlay_height), (w - 10, h - 10), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Get scores
        openface_score = engagement['score']
        ensemble_score = engagement.get('ensemble_score', 0)
        status = engagement['status']
        
        # Color helper function
        def get_color(score):
            if score >= 75:
                return (0, 255, 0)  # Green
            elif score >= 50:
                return (0, 255, 255)  # Yellow
            elif score >= 30:
                return (0, 165, 255)  # Orange
            else:
                return (0, 0, 255)  # Red
        
        y_offset = h - overlay_height + 25
        
        if has_ensemble:
            # PROMINENT ENSEMBLE SCORE (bigger and first)
            ensemble_color = get_color(ensemble_score)
            ensemble_text = f"AI Ensemble: {ensemble_score:.1f}%"
            cv2.putText(frame, ensemble_text, (20, y_offset), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, ensemble_color, 2)
            
            # Improvement indicator
            improvement = ensemble_score - openface_score
            if improvement != 0:
                improvement_text = f"({improvement:+.1f}%)"
                improvement_color = (0, 255, 0) if improvement > 0 else (0, 165, 255)
                cv2.putText(frame, improvement_text, (230, y_offset), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, improvement_color, 1)
            
            y_offset += 30
            
            # OpenFace score (secondary)
            openface_color = get_color(openface_score)
            openface_text = f"OpenFace: {openface_score:.1f}%"
            cv2.putText(frame, openface_text, (20, y_offset), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, openface_color, 1)
            
            y_offset += 30
            
            # Show top emotion if available
            if engagement.get('emotions'):
                # Find dominant emotion
                dominant_emotion = None
                max_confidence = 0
                for emotion, data in engagement['emotions'].items():
                    if data['confidence'] > max_confidence and data['level'] in ['High', 'Very High']:
                        max_confidence = data['confidence']
                        dominant_emotion = (emotion, data)
                
                if dominant_emotion:
                    emotion_emoji = {
                        'Boredom': '😴',
                        'Engagement': '🎯',
                        'Confusion': '😕',
                        'Frustration': '😤'
                    }
                    emotion_name, emotion_data = dominant_emotion
                    emoji = emotion_emoji.get(emotion_name, '•')
                    emotion_text = f"{emoji} {emotion_name}: {emotion_data['level']}"
                    cv2.putText(frame, emotion_text, (20, y_offset), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    y_offset += 25
        else:
            # Only OpenFace available
            openface_color = get_color(openface_score)
            openface_text = f"Engagement: {openface_score:.1f}/100"
            cv2.putText(frame, openface_text, (20, y_offset), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, openface_color, 2)
            y_offset += 35
        
        # Draw status (bottom line)
        status_text = f"Status: {status.replace('_', ' ').title()}"
        cv2.putText(frame, status_text, (20, h - 15), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Draw frame count (bottom right)
        frame_text = f"Frame: {engagement['frame_count']}"
        cv2.putText(frame, frame_text, (w - 130, h - 15), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        
        return frame
    
    def get_current_engagement(self) -> Dict:
        """Get current engagement data (thread-safe)"""
        with self.engagement_lock:
            return self.current_engagement.copy()
    
    def get_session_summary(self) -> Dict:
        """Get session summary statistics"""
        if not self.session_data['engagement_scores']:
            return {
                'avg_engagement': 0.0,
                'total_frames': 0,
                'session_duration': 0
            }
        
        start_time = datetime.fromisoformat(self.session_data['start_time'])
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        summary = {
            'session_id': self.session_id,
            'avg_engagement': np.mean(self.session_data['engagement_scores']),
            'min_engagement': np.min(self.session_data['engagement_scores']),
            'max_engagement': np.max(self.session_data['engagement_scores']),
            'total_frames': self.session_data['total_frames'],
            'session_duration': duration,
            'frames_per_minute': self.session_data['total_frames'] / (duration / 60) if duration > 0 else 0
        }
        
        # Add ensemble statistics if available
        if self.session_data['ensemble_scores']:
            summary['avg_ensemble_engagement'] = np.mean(self.session_data['ensemble_scores'])
            summary['min_ensemble_engagement'] = np.min(self.session_data['ensemble_scores'])
            summary['max_ensemble_engagement'] = np.max(self.session_data['ensemble_scores'])
            summary['ensemble_predictions'] = len(self.ensemble_predictions)
        
        return summary
    
    def end_session(self):
        """End session and save final data"""
        # Save remaining features
        self.openface.save_features_to_csv()
        
        # Save final ensemble analysis report
        if self.use_ensemble and len(self.ensemble_predictions) > 0:
            self._save_ensemble_analysis_report()
        
        # Save session summary
        summary = self.get_session_summary()
        summary_file = os.path.join(self.engagement_logs_dir, f"session_summary_{self.session_id}.json")
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Session {self.session_id} ended. Avg engagement: {summary['avg_engagement']:.2f}")
        
        # Cleanup ensemble detector
        if self.ensemble_detector:
            self.ensemble_detector.shutdown()


def render_pip_webcam(lecture_id: str, course_id: str, student_id: str, 
                       on_engagement_update: Optional[Callable] = None,
                       use_ensemble: bool = True,
                       ensemble_mode: str = "fast") -> PiPWebcamLive:
    """
    Render Picture-in-Picture webcam component with ensemble ML
    
    Args:
        lecture_id: Current lecture ID
        course_id: Current course ID
        student_id: Current student ID
        on_engagement_update: Callback for engagement updates
        use_ensemble: Enable ensemble ML model (default: True)
        ensemble_mode: "fast" (66ms), "balanced" (126ms), "accurate" (173ms)
    
    Returns:
        PiPWebcamLive instance
    """
    # Initialize PiP webcam with ensemble support
    if 'pip_webcam' not in st.session_state:
        st.session_state.pip_webcam = PiPWebcamLive(
            lecture_id, course_id, student_id,
            use_ensemble=use_ensemble,
            ensemble_mode=ensemble_mode
        )
    
    pip_webcam = st.session_state.pip_webcam
    
    # Custom CSS for PiP positioning
    st.markdown("""
    <style>
    /* PiP Container */
    .pip-container {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 320px;
        height: 240px;
        z-index: 9999;
        border: 3px solid #1f77b4;
        border-radius: 12px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.3);
        overflow: hidden;
        background: #000;
    }
    
    /* Make PiP draggable effect */
    .pip-container:hover {
        box-shadow: 0 12px 24px rgba(0,0,0,0.4);
        border-color: #4CAF50;
    }
    
    /* Ensure video fits in container */
    .pip-container video {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    
    /* Hide Streamlit WebRTC controls */
    .stStreamlit video {
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # RTC Configuration for webcam
    rtc_configuration = RTCConfiguration(
        {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
    )
    
    # Create PiP webcam streamer
    webrtc_ctx = webrtc_streamer(
        key=f"pip_webcam_{lecture_id}",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=rtc_configuration,
        video_frame_callback=pip_webcam.video_frame_callback,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )
    
    return pip_webcam


def render_engagement_sidebar(pip_webcam: PiPWebcamLive):
    """
    Render engagement metrics in sidebar with ensemble ML insights
    
    Args:
        pip_webcam: PiPWebcamLive instance
    """
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Live Engagement")
    
    # Get current engagement
    engagement = pip_webcam.get_current_engagement()
    
    # Display ensemble score if available
    if engagement.get('ensemble_score', 0) > 0:
        ensemble_score = engagement['ensemble_score']
        
        if ensemble_score >= 75:
            emoji = "🟢"
        elif ensemble_score >= 50:
            emoji = "🟡"
        elif ensemble_score >= 30:
            emoji = "🟠"
        else:
            emoji = "🔴"
        
        st.sidebar.metric(
            label=f"{emoji} Ensemble AI Score",
            value=f"{ensemble_score:.1f}/100",
            delta=f"+{ensemble_score - engagement['score']:.1f}% vs OpenFace"
        )
        
        # Show emotional states
        if engagement.get('emotions'):
            st.sidebar.markdown("**🎭 Emotional States:**")
            for emotion, data in engagement['emotions'].items():
                level = data['level']
                confidence = data['confidence'] * 100
                
                # Emoji for each emotion
                emotion_emoji = {
                    'Boredom': '😴',
                    'Engagement': '🎯',
                    'Confusion': '😕',
                    'Frustration': '😤'
                }
                
                st.sidebar.text(f"{emotion_emoji.get(emotion, '•')} {emotion}: {level} ({confidence:.0f}%)")
    
    # Display OpenFace score
    score = engagement['score']
    
    if score >= 75:
        delta_color = "normal"
        emoji = "🟢"
    elif score >= 50:
        delta_color = "normal"
        emoji = "🟡"
    elif score >= 30:
        delta_color = "inverse"
        emoji = "🟠"
    else:
        delta_color = "inverse"
        emoji = "🔴"
    
    st.sidebar.metric(
        label=f"{emoji} OpenFace Score",
        value=f"{score:.1f}/100",
        delta=engagement['status'].replace('_', ' ').title()
    )
    
    # Display session stats
    summary = pip_webcam.get_session_summary()
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("📸 Frames", summary['total_frames'])
    with col2:
        duration_min = summary['session_duration'] / 60
        st.metric("⏱️ Duration", f"{duration_min:.1f}m")
    
    # Show ensemble prediction count if available
    if summary.get('ensemble_predictions', 0) > 0:
        st.sidebar.metric("🤖 AI Predictions", summary['ensemble_predictions'])
    
    # Progress bar for engagement
    progress_score = engagement.get('ensemble_score', score)
    st.sidebar.progress(progress_score / 100)
    
    # Status message
    status = engagement['status']
    if status == 'highly_engaged':
        st.sidebar.success("✅ Great focus!")
    elif status == 'engaged':
        st.sidebar.info("👍 Good attention")
    elif status == 'partially_engaged':
        st.sidebar.warning("⚠️ Try to focus")
    elif status == 'looking_away':
        st.sidebar.warning("👀 Please look at screen")
    elif status == 'drowsy':
        st.sidebar.error("😴 Take a break?")
    else:
        st.sidebar.error("❌ No face detected")


# Export functions
__all__ = ['PiPWebcamLive', 'render_pip_webcam', 'render_engagement_sidebar']
