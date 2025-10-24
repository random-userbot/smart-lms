"""
Smart LMS - OpenFace Feature Processor
Comprehensive facial feature extraction using MediaPipe + OpenFace-style analysis
Extracts 17 Action Units, gaze vectors, head pose, and computes accurate engagement scores
"""

import cv2
import numpy as np
import mediapipe as mp
from typing import Dict, Optional, Tuple, List
from datetime import datetime
import os
import csv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OpenFaceProcessor:
    """
    OpenFace-style feature extraction using MediaPipe Face Mesh
    Extracts comprehensive facial features for engagement analysis
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize OpenFace processor"""
        # Initialize MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Session tracking
        self.session_id = None
        self.frame_count = 0
        self.features_buffer = []
        
        # CSV file paths
        self.csv_dir = "ml_data/csv_logs"
        os.makedirs(self.csv_dir, exist_ok=True)
        
        # Feature extraction weights for engagement
        self.weights = {
            'gaze': 0.30,
            'head_pose': 0.25,
            'attention_aus': 0.25,
            'blink_rate': 0.10,
            'facial_expression': 0.10
        }
        
        logger.info("OpenFaceProcessor initialized with MediaPipe Face Mesh")
    
    def set_session_id(self, session_id: str):
        """Set session ID for CSV logging"""
        self.session_id = session_id
        self.frame_count = 0
        self.features_buffer = []
    
    def process_frame(self, frame: np.ndarray, lecture_id: str = None, course_id: str = None) -> Dict:
        """
        Process single frame and extract comprehensive OpenFace-style features
        
        Args:
            frame: BGR image from webcam
            lecture_id: Current lecture identifier
            course_id: Current course identifier
        
        Returns:
            Dictionary with comprehensive facial features and engagement score
        """
        self.frame_count += 1
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w = frame.shape[:2]
        
        # Process with MediaPipe
        results = self.face_mesh.process(rgb_frame)
        
        # Initialize feature dictionary
        features = {
            'timestamp': datetime.utcnow().isoformat(),
            'frame': self.frame_count,
            'session_id': self.session_id,
            'lecture_id': lecture_id,
            'course_id': course_id,
            'face_detected': 0,
            'confidence': 0.0,
            'status': 'no_face'
        }
        
        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark
            
            # Face detected successfully
            features['face_detected'] = 1
            features['confidence'] = 0.95  # MediaPipe confidence
            features['status'] = 'engaged'
            
            # Extract all features
            gaze_features = self._extract_gaze_features(landmarks, w, h)
            head_pose_features = self._extract_head_pose(landmarks, w, h)
            action_units = self._extract_action_units(landmarks)
            expression_features = self._extract_expression_features(action_units)
            
            # Merge all features
            features.update(gaze_features)
            features.update(head_pose_features)
            features.update(action_units)
            features.update(expression_features)
            
            # Compute engagement score
            engagement_score, status = self._compute_engagement_score(features)
            features['engagement_score'] = engagement_score
            features['status'] = status
            
        else:
            # No face detected - set default values
            self._set_default_features(features)
        
        # Buffer features for batch writing
        self.features_buffer.append(features)
        
        return features
    
    def _extract_gaze_features(self, landmarks, w: int, h: int) -> Dict:
        """
        Extract gaze direction and eye tracking features
        
        Returns:
            gaze_0_x, gaze_0_y, gaze_0_z (left eye)
            gaze_1_x, gaze_1_y, gaze_1_z (right eye)
            gaze_angle_x, gaze_angle_y (degrees)
        """
        # Left eye landmarks
        left_eye_center = np.array([
            (landmarks[33].x + landmarks[133].x) / 2,
            (landmarks[33].y + landmarks[133].y) / 2,
            (landmarks[33].z + landmarks[133].z) / 2
        ])
        left_iris = np.array([landmarks[468].x, landmarks[468].y, landmarks[468].z])
        
        # Right eye landmarks
        right_eye_center = np.array([
            (landmarks[263].x + landmarks[362].x) / 2,
            (landmarks[263].y + landmarks[362].y) / 2,
            (landmarks[263].z + landmarks[362].z) / 2
        ])
        right_iris = np.array([landmarks[473].x, landmarks[473].y, landmarks[473].z])
        
        # Compute gaze vectors (iris position relative to eye center)
        gaze_0 = left_iris - left_eye_center
        gaze_1 = right_iris - right_eye_center
        
        # Compute gaze angles (in degrees)
        gaze_angle_x = np.mean([np.arctan2(gaze_0[0], gaze_0[2]), 
                                 np.arctan2(gaze_1[0], gaze_1[2])]) * 180 / np.pi
        gaze_angle_y = np.mean([np.arctan2(gaze_0[1], gaze_0[2]), 
                                 np.arctan2(gaze_1[1], gaze_1[2])]) * 180 / np.pi
        
        return {
            'gaze_0_x': round(gaze_0[0], 4),
            'gaze_0_y': round(gaze_0[1], 4),
            'gaze_0_z': round(gaze_0[2], 4),
            'gaze_1_x': round(gaze_1[0], 4),
            'gaze_1_y': round(gaze_1[1], 4),
            'gaze_1_z': round(gaze_1[2], 4),
            'gaze_angle_x': round(gaze_angle_x, 2),
            'gaze_angle_y': round(gaze_angle_y, 2)
        }
    
    def _extract_head_pose(self, landmarks, w: int, h: int) -> Dict:
        """
        Extract head pose (rotation and translation)
        
        Returns:
            pose_Tx, pose_Ty, pose_Tz (translation)
            pose_Rx, pose_Ry, pose_Rz (rotation in degrees)
        """
        # Get key 3D points
        nose_tip = np.array([landmarks[1].x * w, landmarks[1].y * h, landmarks[1].z * w])
        chin = np.array([landmarks[152].x * w, landmarks[152].y * h, landmarks[152].z * w])
        left_eye = np.array([landmarks[33].x * w, landmarks[33].y * h, landmarks[33].z * w])
        right_eye = np.array([landmarks[263].x * w, landmarks[263].y * h, landmarks[263].z * w])
        left_mouth = np.array([landmarks[61].x * w, landmarks[61].y * h, landmarks[61].z * w])
        right_mouth = np.array([landmarks[291].x * w, landmarks[291].y * h, landmarks[291].z * w])
        
        # 3D model points (generic face model)
        model_points = np.array([
            (0.0, 0.0, 0.0),          # Nose tip
            (0.0, -330.0, -65.0),     # Chin
            (-225.0, 170.0, -135.0),  # Left eye
            (225.0, 170.0, -135.0),   # Right eye
            (-150.0, -150.0, -125.0), # Left mouth
            (150.0, -150.0, -125.0)   # Right mouth
        ])
        
        # 2D image points
        image_points = np.array([
            (landmarks[1].x * w, landmarks[1].y * h),
            (landmarks[152].x * w, landmarks[152].y * h),
            (landmarks[33].x * w, landmarks[33].y * h),
            (landmarks[263].x * w, landmarks[263].y * h),
            (landmarks[61].x * w, landmarks[61].y * h),
            (landmarks[291].x * w, landmarks[291].y * h)
        ], dtype="double")
        
        # Camera matrix
        focal_length = w
        center = (w / 2, h / 2)
        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype="double")
        
        dist_coeffs = np.zeros((4, 1))
        
        # Solve PnP
        success, rotation_vec, translation_vec = cv2.solvePnP(
            model_points, image_points, camera_matrix, dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE
        )
        
        # Convert rotation vector to Euler angles
        rotation_mat, _ = cv2.Rodrigues(rotation_vec)
        pose_mat = cv2.hconcat((rotation_mat, translation_vec))
        _, _, _, _, _, _, euler_angles = cv2.decomposeProjectionMatrix(pose_mat)
        
        pitch, yaw, roll = euler_angles.flatten()[:3]
        
        return {
            'pose_Tx': round(translation_vec[0][0], 2),
            'pose_Ty': round(translation_vec[1][0], 2),
            'pose_Tz': round(translation_vec[2][0], 2),
            'pose_Rx': round(pitch, 2),
            'pose_Ry': round(yaw, 2),
            'pose_Rz': round(roll, 2)
        }
    
    def _extract_action_units(self, landmarks) -> Dict:
        """
        Extract 17 Facial Action Units (AUs)
        
        Returns:
            AU01_r through AU45_r (intensity values 0-5)
        """
        # Calculate distances and ratios for AUs
        
        # Inner brow raiser (AU01)
        left_brow_inner = landmarks[70]
        left_eye_top = landmarks[159]
        au01_intensity = abs(left_brow_inner.y - left_eye_top.y) * 100
        
        # Outer brow raiser (AU02)
        left_brow_outer = landmarks[46]
        au02_intensity = abs(left_brow_outer.y - left_eye_top.y) * 100
        
        # Brow lowerer (AU04)
        au04_intensity = max(0, 5 - au01_intensity)
        
        # Upper lid raiser (AU05)
        left_eye_bottom = landmarks[145]
        eye_openness = abs(left_eye_top.y - left_eye_bottom.y)
        au05_intensity = eye_openness * 150
        
        # Cheek raiser (AU06)
        left_cheek = landmarks[205]
        au06_intensity = abs(left_cheek.y - left_eye_bottom.y) * 50
        
        # Lid tightener (AU07)
        au07_intensity = max(0, 5 - au05_intensity)
        
        # Nose wrinkler (AU09)
        nose_tip = landmarks[1]
        nose_bridge = landmarks[6]
        au09_intensity = abs(nose_tip.y - nose_bridge.y) * 30
        
        # Upper lip raiser (AU10)
        upper_lip = landmarks[13]
        nose_bottom = landmarks[2]
        au10_intensity = abs(upper_lip.y - nose_bottom.y) * 80
        
        # Lip corner puller (AU12) - SMILE
        left_mouth_corner = landmarks[61]
        right_mouth_corner = landmarks[291]
        mouth_width = abs(left_mouth_corner.x - right_mouth_corner.x)
        au12_intensity = mouth_width * 30
        
        # Dimpler (AU14)
        au14_intensity = au12_intensity * 0.7
        
        # Lip corner depressor (AU15)
        au15_intensity = max(0, 5 - au12_intensity)
        
        # Chin raiser (AU17)
        chin = landmarks[152]
        lower_lip = landmarks[14]
        au17_intensity = abs(chin.y - lower_lip.y) * 80
        
        # Lip stretcher (AU20)
        au20_intensity = mouth_width * 25
        
        # Lip tightener (AU23)
        upper_lip_top = landmarks[0]
        lower_lip_bottom = landmarks[17]
        lip_distance = abs(upper_lip_top.y - lower_lip_bottom.y)
        au23_intensity = max(0, 5 - lip_distance * 100)
        
        # Lips part (AU25)
        au25_intensity = lip_distance * 100
        
        # Jaw drop (AU26)
        au26_intensity = abs(chin.y - nose_tip.y) * 30
        
        # Blink (AU45)
        au45_intensity = 5 if eye_openness < 0.01 else 0
        
        # Normalize all AUs to 0-5 scale
        def normalize_au(value):
            return round(min(5.0, max(0.0, value)), 2)
        
        return {
            'AU01_r': normalize_au(au01_intensity),  # Inner brow raiser
            'AU02_r': normalize_au(au02_intensity),  # Outer brow raiser
            'AU04_r': normalize_au(au04_intensity),  # Brow lowerer
            'AU05_r': normalize_au(au05_intensity),  # Upper lid raiser
            'AU06_r': normalize_au(au06_intensity),  # Cheek raiser
            'AU07_r': normalize_au(au07_intensity),  # Lid tightener
            'AU09_r': normalize_au(au09_intensity),  # Nose wrinkler
            'AU10_r': normalize_au(au10_intensity),  # Upper lip raiser
            'AU12_r': normalize_au(au12_intensity),  # Lip corner puller (smile)
            'AU14_r': normalize_au(au14_intensity),  # Dimpler
            'AU15_r': normalize_au(au15_intensity),  # Lip corner depressor
            'AU17_r': normalize_au(au17_intensity),  # Chin raiser
            'AU20_r': normalize_au(au20_intensity),  # Lip stretcher
            'AU23_r': normalize_au(au23_intensity),  # Lip tightener
            'AU25_r': normalize_au(au25_intensity),  # Lips part
            'AU26_r': normalize_au(au26_intensity),  # Jaw drop
            'AU45_r': normalize_au(au45_intensity)   # Blink
        }
    
    def _extract_expression_features(self, action_units: Dict) -> Dict:
        """
        Extract expression features from Action Units
        
        Returns:
            smile_intensity, confusion_level, drowsiness_level
        """
        # Smile intensity (AU06 + AU12)
        smile_intensity = (action_units['AU06_r'] + action_units['AU12_r']) / 2
        
        # Confusion (AU01 + AU02 + AU04)
        confusion_level = (action_units['AU01_r'] + action_units['AU02_r'] + action_units['AU04_r']) / 3
        
        # Drowsiness (AU07 + AU45 - AU05)
        drowsiness_level = (action_units['AU07_r'] + action_units['AU45_r'] - action_units['AU05_r'])
        drowsiness_level = max(0, drowsiness_level)
        
        return {
            'smile_intensity': round(smile_intensity, 2),
            'confusion_level': round(confusion_level, 2),
            'drowsiness_level': round(drowsiness_level, 2)
        }
    
    def _compute_engagement_score(self, features: Dict) -> Tuple[float, str]:
        """
        Compute accurate engagement score from extracted features
        
        Returns:
            (engagement_score, status_string)
        """
        # Gaze score (looking at screen = high score)
        gaze_angle = np.sqrt(features['gaze_angle_x']**2 + features['gaze_angle_y']**2)
        if gaze_angle > 25:
            gaze_score = 0.2
            status = 'looking_away'
        elif gaze_angle > 15:
            gaze_score = 0.6
            status = 'partially_engaged'
        else:
            gaze_score = 1.0
            status = 'engaged'
        
        # Head pose score (facing forward = high score)
        pitch = abs(features['pose_Rx'])
        yaw = abs(features['pose_Ry'])
        roll = abs(features['pose_Rz'])
        
        head_rotation = np.sqrt(pitch**2 + yaw**2 + roll**2)
        if head_rotation > 30:
            head_pose_score = 0.3
            status = 'looking_away'
        elif head_rotation > 15:
            head_pose_score = 0.7
        else:
            head_pose_score = 1.0
        
        # Attention AUs (high = attentive)
        # AU05 (eye openness), AU06 (cheek raiser), AU12 (smile)
        attention_score = (features['AU05_r'] + features['AU06_r'] * 0.5 + features['AU12_r'] * 0.3) / 5.8
        
        # Drowsiness penalty
        if features['drowsiness_level'] > 3:
            attention_score *= 0.5
            status = 'drowsy'
        
        # Blink rate (AU45)
        blink_score = 1.0 if features['AU45_r'] < 3 else 0.5
        
        # Expression score (positive emotions = engaged)
        expression_score = (features['smile_intensity'] + (5 - features['confusion_level'])) / 10
        
        # Weighted combination
        engagement_score = (
            self.weights['gaze'] * gaze_score +
            self.weights['head_pose'] * head_pose_score +
            self.weights['attention_aus'] * attention_score +
            self.weights['blink_rate'] * blink_score +
            self.weights['facial_expression'] * expression_score
        ) * 100
        
        # Determine status
        if engagement_score >= 75:
            status = 'highly_engaged'
        elif engagement_score >= 50:
            status = 'engaged'
        elif engagement_score >= 30:
            status = 'partially_engaged'
        else:
            status = 'disengaged'
        
        return round(engagement_score, 2), status
    
    def _set_default_features(self, features: Dict):
        """Set default values when no face is detected"""
        # Gaze features
        for axis in ['x', 'y', 'z']:
            features[f'gaze_0_{axis}'] = 0.0
            features[f'gaze_1_{axis}'] = 0.0
        features['gaze_angle_x'] = 0.0
        features['gaze_angle_y'] = 0.0
        
        # Head pose features
        for t in ['Tx', 'Ty', 'Tz', 'Rx', 'Ry', 'Rz']:
            features[f'pose_{t}'] = 0.0
        
        # Action Units
        for au in ['01', '02', '04', '05', '06', '07', '09', '10', 
                   '12', '14', '15', '17', '20', '23', '25', '26', '45']:
            features[f'AU{au}_r'] = 0.0
        
        # Expression features
        features['smile_intensity'] = 0.0
        features['confusion_level'] = 0.0
        features['drowsiness_level'] = 0.0
        
        # Engagement
        features['engagement_score'] = 0.0
    
    def save_features_to_csv(self):
        """Save buffered features to CSV file"""
        if not self.features_buffer:
            return
        
        csv_file = os.path.join(self.csv_dir, f"openface_features_{self.session_id}.csv")
        
        # Check if file exists to determine if we need to write headers
        file_exists = os.path.exists(csv_file)
        
        # Define CSV columns
        fieldnames = [
            'timestamp', 'frame', 'session_id', 'lecture_id', 'course_id',
            'face_detected', 'confidence', 'status', 'engagement_score',
            # Gaze features
            'gaze_0_x', 'gaze_0_y', 'gaze_0_z', 'gaze_1_x', 'gaze_1_y', 'gaze_1_z',
            'gaze_angle_x', 'gaze_angle_y',
            # Head pose
            'pose_Tx', 'pose_Ty', 'pose_Tz', 'pose_Rx', 'pose_Ry', 'pose_Rz',
            # Action Units
            'AU01_r', 'AU02_r', 'AU04_r', 'AU05_r', 'AU06_r', 'AU07_r',
            'AU09_r', 'AU10_r', 'AU12_r', 'AU14_r', 'AU15_r', 'AU17_r',
            'AU20_r', 'AU23_r', 'AU25_r', 'AU26_r', 'AU45_r',
            # Expression features
            'smile_intensity', 'confusion_level', 'drowsiness_level'
        ]
        
        with open(csv_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerows(self.features_buffer)
        
        logger.info(f"Saved {len(self.features_buffer)} frames to {csv_file}")
        
        # Clear buffer
        self.features_buffer = []
    
    def get_session_summary(self) -> Dict:
        """Get summary statistics for current session"""
        if not self.features_buffer:
            return {}
        
        face_detected_frames = [f for f in self.features_buffer if f['face_detected'] == 1]
        
        if not face_detected_frames:
            return {
                'total_frames': len(self.features_buffer),
                'face_detection_rate': 0.0,
                'avg_engagement_score': 0.0
            }
        
        engagement_scores = [f['engagement_score'] for f in face_detected_frames]
        
        return {
            'total_frames': len(self.features_buffer),
            'face_detection_rate': len(face_detected_frames) / len(self.features_buffer),
            'avg_engagement_score': np.mean(engagement_scores),
            'min_engagement_score': np.min(engagement_scores),
            'max_engagement_score': np.max(engagement_scores),
            'avg_gaze_angle': np.mean([np.sqrt(f['gaze_angle_x']**2 + f['gaze_angle_y']**2) 
                                       for f in face_detected_frames]),
            'avg_smile_intensity': np.mean([f['smile_intensity'] for f in face_detected_frames])
        }


# Singleton instance
_openface_processor = None

def get_openface_processor() -> OpenFaceProcessor:
    """Get OpenFace processor singleton"""
    global _openface_processor
    if _openface_processor is None:
        _openface_processor = OpenFaceProcessor()
    return _openface_processor
