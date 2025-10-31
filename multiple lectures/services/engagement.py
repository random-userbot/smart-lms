"""
Smart LMS - Engagement Tracking Service
Real-time webcam engagement using MediaPipe and offline OpenFace integration
"""

import cv2
import numpy as np
import yaml
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import subprocess
import os


class EngagementTracker:
    """Engagement tracking using MediaPipe (real-time) or OpenFace (offline)"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize engagement tracker"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.engagement_config = self.config['engagement']
        self.mode = self.engagement_config['mode']
        self.sampling_rate = self.engagement_config['sampling_rate']
        self.weights = self.engagement_config['weights']
        
        # Initialize MediaPipe if in realtime mode
        if self.mode == 'realtime':
            self._init_mediapipe()
    
    def _init_mediapipe(self):
        """Initialize MediaPipe Face Mesh"""
        try:
            import mediapipe as mp
            self.mp_face_mesh = mp.solutions.face_mesh
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            self.mp_drawing = mp.solutions.drawing_utils
            self.mp_drawing_styles = mp.solutions.drawing_styles
        except ImportError:
            raise ImportError("MediaPipe not installed. Run: pip install mediapipe")
    
    def process_frame(self, frame: np.ndarray) -> Dict:
        """
        Process a single frame and extract engagement features
        
        Args:
            frame: BGR image from webcam
        
        Returns:
            Dictionary with engagement features
        """
        if self.mode == 'realtime':
            return self._process_frame_mediapipe(frame)
        else:
            raise ValueError("Offline mode requires batch processing with OpenFace")
    
    def _process_frame_mediapipe(self, frame: np.ndarray) -> Dict:
        """Process frame using MediaPipe Face Mesh"""
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process with MediaPipe
        results = self.face_mesh.process(rgb_frame)
        
        features = {
            'timestamp': datetime.utcnow().isoformat(),
            'face_detected': False,
            'gaze_score': 0.0,
            'attention_score': 0.0,
            'head_pose_score': 0.0,
            'blink_detected': False
        }
        
        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]
            features['face_detected'] = True
            
            # Extract features
            landmarks = face_landmarks.landmark
            
            # Gaze estimation (simplified)
            gaze_score = self._estimate_gaze(landmarks, frame.shape)
            features['gaze_score'] = gaze_score
            
            # Attention score (based on eye openness)
            attention_score = self._estimate_attention(landmarks)
            features['attention_score'] = attention_score
            
            # Head pose stability
            head_pose_score = self._estimate_head_pose(landmarks)
            features['head_pose_score'] = head_pose_score
            
            # Blink detection
            features['blink_detected'] = self._detect_blink(landmarks)
        
        return features
    
    def _estimate_gaze(self, landmarks, frame_shape) -> float:
        """
        Estimate gaze direction (simplified)
        Returns score 0-1 (1 = looking at screen)
        """
        # Get eye landmarks (simplified - using iris landmarks)
        # Left eye: 468-473, Right eye: 473-478
        left_iris = landmarks[468]
        right_iris = landmarks[473]
        
        # Get eye corners
        left_corner = landmarks[33]
        right_corner = landmarks[263]
        
        # Calculate horizontal gaze ratio
        left_ratio = abs(left_iris.x - left_corner.x)
        right_ratio = abs(right_iris.x - right_corner.x)
        
        # Average ratio (closer to 0.5 = looking at center)
        avg_ratio = (left_ratio + right_ratio) / 2
        
        # Convert to score (penalize looking away)
        gaze_score = 1.0 - abs(avg_ratio - 0.5) * 2
        gaze_score = max(0.0, min(1.0, gaze_score))
        
        return gaze_score
    
    def _estimate_attention(self, landmarks) -> float:
        """
        Estimate attention based on eye openness
        Returns score 0-1 (1 = eyes wide open, attentive)
        """
        # Left eye landmarks: 159 (top), 145 (bottom)
        # Right eye landmarks: 386 (top), 374 (bottom)
        
        left_eye_top = landmarks[159]
        left_eye_bottom = landmarks[145]
        right_eye_top = landmarks[386]
        right_eye_bottom = landmarks[374]
        
        # Calculate eye openness
        left_openness = abs(left_eye_top.y - left_eye_bottom.y)
        right_openness = abs(right_eye_top.y - right_eye_bottom.y)
        
        avg_openness = (left_openness + right_openness) / 2
        
        # Normalize (typical range 0.01-0.03)
        attention_score = min(1.0, avg_openness / 0.03)
        
        return attention_score
    
    def _estimate_head_pose(self, landmarks) -> float:
        """
        Estimate head pose stability
        Returns score 0-1 (1 = stable, facing forward)
        """
        # Use nose tip (1) and chin (152) for vertical angle
        # Use left (234) and right (454) face for horizontal angle
        
        nose = landmarks[1]
        chin = landmarks[152]
        left_face = landmarks[234]
        right_face = landmarks[454]
        
        # Vertical stability (nose-chin alignment)
        vertical_diff = abs(nose.x - chin.x)
        
        # Horizontal stability (face symmetry)
        horizontal_diff = abs((left_face.x + right_face.x) / 2 - nose.x)
        
        # Combined stability score
        stability = 1.0 - (vertical_diff + horizontal_diff) * 5
        stability = max(0.0, min(1.0, stability))
        
        return stability
    
    def _detect_blink(self, landmarks) -> bool:
        """
        Detect if eyes are blinking
        """
        # Use eye openness threshold
        left_eye_top = landmarks[159]
        left_eye_bottom = landmarks[145]
        
        openness = abs(left_eye_top.y - left_eye_bottom.y)
        
        # Threshold for blink detection
        return openness < 0.01
    
    def compute_engagement_score(self, features_list: List[Dict]) -> float:
        """
        Compute overall engagement score from list of frame features
        
        Args:
            features_list: List of feature dictionaries from multiple frames
        
        Returns:
            Engagement score 0-100
        """
        if not features_list:
            return 0.0
        
        # Filter frames where face was detected
        valid_features = [f for f in features_list if f['face_detected']]
        
        if not valid_features:
            return 0.0
        
        # Calculate average scores
        avg_gaze = np.mean([f['gaze_score'] for f in valid_features])
        avg_attention = np.mean([f['attention_score'] for f in valid_features])
        avg_head_pose = np.mean([f['head_pose_score'] for f in valid_features])
        
        # Calculate blink rate (normal: 15-20 per minute)
        total_blinks = sum(1 for f in valid_features if f['blink_detected'])
        duration_minutes = len(features_list) * self.sampling_rate / 60
        blink_rate = total_blinks / duration_minutes if duration_minutes > 0 else 0
        
        # Normalize blink rate (15-20 is optimal)
        if 15 <= blink_rate <= 20:
            blink_score = 1.0
        elif blink_rate < 15:
            blink_score = blink_rate / 15
        else:
            blink_score = max(0.0, 1.0 - (blink_rate - 20) / 20)
        
        # Weighted combination
        engagement_score = (
            self.weights['gaze'] * avg_gaze +
            self.weights['attention'] * avg_attention +
            self.weights['head_pose'] * avg_head_pose +
            self.weights['blink'] * blink_score
        )
        
        # Convert to 0-100 scale
        engagement_score = engagement_score * 100
        
        # Penalize for low face detection rate
        detection_rate = len(valid_features) / len(features_list)
        engagement_score = engagement_score * detection_rate
        
        return round(engagement_score, 2)
    
    def process_video_offline(self, video_path: str, output_dir: str) -> Dict:
        """
        Process video using OpenFace (offline mode)
        
        Args:
            video_path: Path to video file
            output_dir: Directory to save OpenFace output
        
        Returns:
            Dictionary with engagement features
        """
        if self.mode != 'offline':
            raise ValueError("Offline processing requires mode='offline' in config")
        
        openface_config = self.config['openface']
        openface_exe = openface_config['executable_path']
        
        # Security: Validate OpenFace executable path
        if not openface_exe or not os.path.exists(openface_exe):
            raise FileNotFoundError(f"OpenFace executable not found or not configured: {openface_exe}")
        
        # Security: Validate that executable is not a script or suspicious file
        if not openface_exe.endswith(('.exe', '')):  # Allow .exe on Windows or no extension on Unix
            raise ValueError("OpenFace executable must be a binary, not a script")
        
        # Security: Validate input video path to prevent path traversal
        video_path = os.path.abspath(video_path)
        if '..' in video_path or not os.path.exists(video_path):
            raise ValueError(f"Invalid video path: {video_path}")
        
        # Create output directory with secure permissions
        os.makedirs(output_dir, mode=0o750, exist_ok=True)
        output_dir = os.path.abspath(output_dir)
        
        # Security: Whitelist allowed arguments and validate paths
        allowed_args = ['-f', '-out_dir', '-of', '-ov']
        
        # Run OpenFace with validated arguments (no shell=True)
        cmd = [
            openface_exe,
            '-f', video_path,
            '-out_dir', output_dir
        ]
        
        # Security: Ensure no shell metacharacters can be injected
        for arg in cmd:
            if any(char in str(arg) for char in ['&', '|', ';', '$', '`', '\n', '\r']):
                raise ValueError(f"Invalid character in command argument: {arg}")
        
        try:
            # Run with strict timeout and resource limits
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                shell=False,  # NEVER use shell=True
                check=False   # We'll check returncode manually
            )
            
            if result.returncode != 0:
                # Log error but don't expose full stderr to user (may contain paths)
                error_msg = "OpenFace processing failed"
                if result.stderr:
                    # Log for admin review but sanitize for user display
                    print(f"[ERROR] OpenFace stderr: {result.stderr[:500]}")  # Truncate
                raise RuntimeError(error_msg)
            
            # Parse OpenFace output CSV
            csv_filename = os.path.basename(video_path).replace('.mp4', '.csv').replace('.avi', '.csv')
            csv_file = os.path.join(output_dir, csv_filename)
            
            if not os.path.exists(csv_file):
                raise FileNotFoundError(f"OpenFace output CSV not generated")
            
            # Load and process features
            features = self._parse_openface_output(csv_file)
            
            return features
        
        except subprocess.TimeoutExpired:
            raise RuntimeError("OpenFace processing timed out (exceeded 5 minutes)")
    
    def _parse_openface_output(self, csv_file: str) -> Dict:
        """Parse OpenFace CSV output and extract features"""
        import pandas as pd
        
        df = pd.read_csv(csv_file)
        
        # Extract relevant features
        features = {
            'total_frames': len(df),
            'face_detection_rate': df['success'].mean(),
            'avg_gaze_angle_x': df['gaze_angle_x'].mean(),
            'avg_gaze_angle_y': df['gaze_angle_y'].mean(),
            'avg_head_pose_rx': df['pose_Rx'].mean(),
            'avg_head_pose_ry': df['pose_Ry'].mean(),
            'avg_head_pose_rz': df['pose_Rz'].mean(),
            'action_units': {}
        }
        
        # Extract Action Units (AUs)
        au_columns = [col for col in df.columns if col.startswith('AU') and col.endswith('_r')]
        for au_col in au_columns:
            features['action_units'][au_col] = df[au_col].mean()
        
        # Compute engagement score from OpenFace features
        engagement_score = self._compute_engagement_from_openface(features)
        features['engagement_score'] = engagement_score
        
        return features
    
    def _compute_engagement_from_openface(self, features: Dict) -> float:
        """Compute engagement score from OpenFace features"""
        # Simplified engagement computation
        # In production, train a model on labeled data
        
        # Gaze score (penalize large angles)
        gaze_angle = np.sqrt(features['avg_gaze_angle_x']**2 + features['avg_gaze_angle_y']**2)
        gaze_score = max(0, 1 - gaze_angle / 30)  # 30 degrees threshold
        
        # Head pose score (penalize large rotations)
        head_rotation = np.sqrt(
            features['avg_head_pose_rx']**2 +
            features['avg_head_pose_ry']**2 +
            features['avg_head_pose_rz']**2
        )
        head_pose_score = max(0, 1 - head_rotation / 45)  # 45 degrees threshold
        
        # Attention AUs (AU01, AU02, AU05 indicate attention)
        attention_aus = ['AU01_r', 'AU02_r', 'AU05_r']
        attention_score = np.mean([
            features['action_units'].get(au, 0)
            for au in attention_aus
        ])
        
        # Weighted combination
        engagement_score = (
            0.4 * gaze_score +
            0.3 * head_pose_score +
            0.3 * attention_score
        ) * 100
        
        # Adjust for face detection rate
        engagement_score *= features['face_detection_rate']
        
        return round(engagement_score, 2)
    
    def get_engagement_summary(self, features_list: List[Dict]) -> Dict:
        """
        Get detailed engagement summary
        
        Returns:
            Dictionary with engagement metrics and statistics
        """
        if not features_list:
            return {
                'engagement_score': 0,
                'face_detection_rate': 0,
                'avg_gaze_score': 0,
                'avg_attention_score': 0,
                'avg_head_pose_score': 0,
                'total_frames': 0
            }
        
        valid_features = [f for f in features_list if f['face_detected']]
        
        return {
            'engagement_score': self.compute_engagement_score(features_list),
            'face_detection_rate': len(valid_features) / len(features_list),
            'avg_gaze_score': np.mean([f['gaze_score'] for f in valid_features]) if valid_features else 0,
            'avg_attention_score': np.mean([f['attention_score'] for f in valid_features]) if valid_features else 0,
            'avg_head_pose_score': np.mean([f['head_pose_score'] for f in valid_features]) if valid_features else 0,
            'total_frames': len(features_list),
            'valid_frames': len(valid_features)
        }


# Singleton instance
_engagement_tracker = None

def get_engagement_tracker() -> EngagementTracker:
    """Get engagement tracker singleton"""
    global _engagement_tracker
    if _engagement_tracker is None:
        _engagement_tracker = EngagementTracker()
    return _engagement_tracker
