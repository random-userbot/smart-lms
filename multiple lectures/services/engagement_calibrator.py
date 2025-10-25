"""
Engagement Calibration Service
Establishes personalized baseline metrics for each student to improve engagement score accuracy
"""

import json
import os
from datetime import datetime
from pathlib import Path
import numpy as np
from typing import Dict, List, Optional
import streamlit as st


class EngagementCalibrator:
    """
    Calibrates engagement detection for individual students by recording their baseline metrics
    during a known engaging activity (watching a short calibration video)
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._load_config()
        self.calibration_dir = Path(self.config.get('ml_data', {}).get('calibration', './ml_data/calibration'))
        self.calibration_dir.mkdir(parents=True, exist_ok=True)
        
        # Calibration settings
        self.calibration_duration = 30  # 30 seconds
        self.min_frames_required = 25   # Need at least 25 valid frames
        
        # Default thresholds (used if no calibration)
        self.default_thresholds = {
            'gaze_angle_threshold': 25.0,
            'head_pitch_range': (-15, 15),
            'head_yaw_range': (-20, 20),
            'blink_rate_range': (10, 30),  # blinks per minute
            'attention_au_threshold': 0.3
        }
    
    def _load_config(self) -> Dict:
        """Load configuration from config.yaml"""
        config_path = Path('./config.yaml')
        if config_path.exists():
            import yaml
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    def needs_calibration(self, student_id: str) -> bool:
        """Check if student needs calibration"""
        calibration_file = self.calibration_dir / f"{student_id}_baseline.json"
        
        if not calibration_file.exists():
            return True
        
        # Check if calibration is recent (within 30 days)
        with open(calibration_file, 'r') as f:
            data = json.load(f)
            calibration_date = datetime.fromisoformat(data['calibration_date'])
            days_since_calibration = (datetime.now() - calibration_date).days
            
            # Recalibrate if older than 30 days
            return days_since_calibration > 30
    
    def start_calibration(self, student_id: str) -> Dict:
        """Initialize calibration session"""
        session_id = f"calib_{student_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        calibration_state = {
            'session_id': session_id,
            'student_id': student_id,
            'start_time': datetime.now().isoformat(),
            'frames_collected': 0,
            'gaze_angles': [],
            'head_pitch': [],
            'head_yaw': [],
            'head_roll': [],
            'blink_times': [],
            'au_values': {},
            'status': 'in_progress'
        }
        
        return calibration_state
    
    def record_calibration_frame(self, calibration_state: Dict, openface_features: Dict) -> Dict:
        """Record features from a calibration frame"""
        
        # Only record if face detected with high confidence
        if not openface_features.get('face_detected', False):
            return calibration_state
        
        if openface_features.get('detection_confidence', 0) < 0.8:
            return calibration_state
        
        # Record gaze angle
        gaze_angle = openface_features.get('gaze_angle', 0)
        if 0 <= gaze_angle <= 90:  # Valid range
            calibration_state['gaze_angles'].append(gaze_angle)
        
        # Record head pose
        calibration_state['head_pitch'].append(openface_features.get('head_pitch', 0))
        calibration_state['head_yaw'].append(openface_features.get('head_yaw', 0))
        calibration_state['head_roll'].append(openface_features.get('head_roll', 0))
        
        # Record blinks (AU45)
        au45 = openface_features.get('AU45_r', 0)
        if au45 > 3.0:  # Blink detected
            current_time = datetime.now()
            calibration_state['blink_times'].append(current_time.isoformat())
        
        # Record AU baselines
        for au_name in ['AU01_r', 'AU02_r', 'AU04_r', 'AU05_r', 'AU06_r', 
                       'AU07_r', 'AU09_r', 'AU10_r', 'AU12_r', 'AU14_r',
                       'AU15_r', 'AU17_r', 'AU20_r', 'AU23_r', 'AU25_r',
                       'AU26_r', 'AU45_r']:
            if au_name not in calibration_state['au_values']:
                calibration_state['au_values'][au_name] = []
            
            au_value = openface_features.get(au_name, 0)
            calibration_state['au_values'][au_name].append(au_value)
        
        calibration_state['frames_collected'] += 1
        
        return calibration_state
    
    def complete_calibration(self, calibration_state: Dict) -> Dict:
        """Complete calibration and save baseline"""
        
        if calibration_state['frames_collected'] < self.min_frames_required:
            return {
                'success': False,
                'message': f"Insufficient data. Collected {calibration_state['frames_collected']} frames, need {self.min_frames_required}",
                'student_id': calibration_state['student_id']
            }
        
        # Calculate baseline metrics
        baseline = self._calculate_baseline_metrics(calibration_state)
        
        # Save to file
        student_id = calibration_state['student_id']
        calibration_file = self.calibration_dir / f"{student_id}_baseline.json"
        
        baseline_data = {
            'student_id': student_id,
            'calibration_date': datetime.now().isoformat(),
            'frames_used': calibration_state['frames_collected'],
            'baseline': baseline
        }
        
        with open(calibration_file, 'w') as f:
            json.dump(baseline_data, f, indent=2)
        
        return {
            'success': True,
            'message': 'Calibration completed successfully',
            'student_id': student_id,
            'baseline': baseline
        }
    
    def _calculate_baseline_metrics(self, calibration_state: Dict) -> Dict:
        """Calculate baseline metrics from calibration data"""
        
        baseline = {}
        
        # Gaze baseline
        if calibration_state['gaze_angles']:
            gaze_angles = np.array(calibration_state['gaze_angles'])
            baseline['gaze_angle_mean'] = float(np.mean(gaze_angles))
            baseline['gaze_angle_std'] = float(np.std(gaze_angles))
            baseline['gaze_angle_threshold'] = float(baseline['gaze_angle_mean'] + 1.5 * baseline['gaze_angle_std'])
        else:
            baseline['gaze_angle_threshold'] = self.default_thresholds['gaze_angle_threshold']
        
        # Head pose baseline
        if calibration_state['head_pitch']:
            pitch = np.array(calibration_state['head_pitch'])
            baseline['head_pitch_mean'] = float(np.mean(pitch))
            baseline['head_pitch_std'] = float(np.std(pitch))
            baseline['head_pitch_range'] = (
                float(baseline['head_pitch_mean'] - 2 * baseline['head_pitch_std']),
                float(baseline['head_pitch_mean'] + 2 * baseline['head_pitch_std'])
            )
        else:
            baseline['head_pitch_range'] = self.default_thresholds['head_pitch_range']
        
        if calibration_state['head_yaw']:
            yaw = np.array(calibration_state['head_yaw'])
            baseline['head_yaw_mean'] = float(np.mean(yaw))
            baseline['head_yaw_std'] = float(np.std(yaw))
            baseline['head_yaw_range'] = (
                float(baseline['head_yaw_mean'] - 2 * baseline['head_yaw_std']),
                float(baseline['head_yaw_mean'] + 2 * baseline['head_yaw_std'])
            )
        else:
            baseline['head_yaw_range'] = self.default_thresholds['head_yaw_range']
        
        # Blink rate baseline
        if len(calibration_state['blink_times']) >= 2:
            blink_times = [datetime.fromisoformat(t) for t in calibration_state['blink_times']]
            duration_minutes = (blink_times[-1] - blink_times[0]).total_seconds() / 60.0
            blink_rate = len(blink_times) / duration_minutes if duration_minutes > 0 else 0
            baseline['blink_rate_mean'] = float(blink_rate)
            baseline['blink_rate_range'] = (
                max(5, blink_rate * 0.5),
                min(40, blink_rate * 1.5)
            )
        else:
            baseline['blink_rate_range'] = self.default_thresholds['blink_rate_range']
        
        # AU baselines (neutral expressions during engaged viewing)
        baseline['au_baseline'] = {}
        for au_name, values in calibration_state['au_values'].items():
            if values:
                baseline['au_baseline'][au_name] = {
                    'mean': float(np.mean(values)),
                    'std': float(np.std(values)),
                    'p75': float(np.percentile(values, 75))  # 75th percentile for threshold
                }
        
        return baseline
    
    def get_baseline(self, student_id: str) -> Dict:
        """Get baseline metrics for a student"""
        calibration_file = self.calibration_dir / f"{student_id}_baseline.json"
        
        if not calibration_file.exists():
            return {'calibrated': False, 'thresholds': self.default_thresholds}
        
        with open(calibration_file, 'r') as f:
            data = json.load(f)
            return {
                'calibrated': True,
                'thresholds': data['baseline'],
                'calibration_date': data['calibration_date']
            }
    
    def apply_personalized_thresholds(self, student_id: str, openface_features: Dict) -> Dict:
        """
        Apply personalized thresholds to compute more accurate engagement score
        Returns adjusted scores
        """
        
        baseline_data = self.get_baseline(student_id)
        
        if not baseline_data['calibrated']:
            # Use default calculation
            return openface_features
        
        baseline = baseline_data['thresholds']
        adjusted = openface_features.copy()
        
        # Adjust gaze score
        gaze_angle = openface_features.get('gaze_angle', 0)
        gaze_threshold = baseline.get('gaze_angle_threshold', 25.0)
        
        if gaze_angle < gaze_threshold:
            adjusted['gaze_score'] = 1.0
        else:
            adjusted['gaze_score'] = max(0, 1 - (gaze_angle - gaze_threshold) / 30.0)
        
        # Adjust head pose score
        pitch = openface_features.get('head_pitch', 0)
        yaw = openface_features.get('head_yaw', 0)
        
        pitch_range = baseline.get('head_pitch_range', (-15, 15))
        yaw_range = baseline.get('head_yaw_range', (-20, 20))
        
        pitch_in_range = pitch_range[0] <= pitch <= pitch_range[1]
        yaw_in_range = yaw_range[0] <= yaw <= yaw_range[1]
        
        if pitch_in_range and yaw_in_range:
            adjusted['head_pose_score'] = 1.0
        elif pitch_in_range or yaw_in_range:
            adjusted['head_pose_score'] = 0.6
        else:
            adjusted['head_pose_score'] = 0.3
        
        # Adjust blink rate score
        # (Would need to track recent blink history in session)
        
        # Adjust AU scores based on deviation from baseline
        au_baseline = baseline.get('au_baseline', {})
        for au_name in ['AU01_r', 'AU02_r', 'AU04_r', 'AU05_r']:
            if au_name in au_baseline:
                au_value = openface_features.get(au_name, 0)
                au_mean = au_baseline[au_name]['mean']
                au_std = au_baseline[au_name]['std']
                
                # Score based on deviation from personal baseline
                deviation = abs(au_value - au_mean) / (au_std + 0.1)
                
                # Attention AUs: higher deviation = more engaged
                if au_name in ['AU01_r', 'AU02_r', 'AU05_r']:
                    adjusted[f'{au_name}_normalized'] = min(1.0, deviation / 2.0)
                # Confusion AUs: lower deviation = more engaged
                else:
                    adjusted[f'{au_name}_normalized'] = max(0, 1 - deviation / 2.0)
        
        return adjusted
    
    def render_calibration_ui(self, student_id: str):
        """Render calibration UI in Streamlit"""
        
        st.markdown("### 🎯 Engagement Calibration")
        st.markdown("""
        To improve accuracy, we need to calibrate the system to your unique characteristics.
        
        **Instructions:**
        1. Watch the calibration video for 30 seconds
        2. Look at the video naturally (as you normally would)
        3. Don't move excessively or make exaggerated expressions
        4. The system will record your baseline metrics
        
        This only needs to be done once (or monthly for best accuracy).
        """)
        
        # Initialize calibration state
        if 'calibration_state' not in st.session_state:
            st.session_state.calibration_state = None
        
        # Start button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Start Calibration", type="primary", use_container_width=True):
                st.session_state.calibration_state = self.start_calibration(student_id)
                st.rerun()
        
        # Show calibration video and progress
        if st.session_state.calibration_state and st.session_state.calibration_state['status'] == 'in_progress':
            
            # Progress bar
            progress = st.session_state.calibration_state['frames_collected'] / self.min_frames_required
            st.progress(min(1.0, progress))
            
            st.markdown(f"""
            **Frames Collected:** {st.session_state.calibration_state['frames_collected']} / {self.min_frames_required}
            
            Please watch the video below and look at it naturally.
            """)
            
            # Calibration video (engaging educational content)
            st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")  # Replace with actual calibration video
            
            # Note: In actual implementation, this would integrate with pip_webcam_live
            # to capture frames during video playback
            
            st.info("💡 **Tip:** The calibration records your natural viewing patterns to personalize accuracy.")


def integrate_with_openface_processor():
    """
    Example integration with OpenFaceProcessor
    
    In services/openface_processor.py:
    
    from services.engagement_calibrator import EngagementCalibrator
    
    class OpenFaceProcessor:
        def __init__(self, ...):
            ...
            self.calibrator = EngagementCalibrator()
        
        def compute_engagement_score(self, features, student_id):
            # Apply personalized thresholds
            adjusted_features = self.calibrator.apply_personalized_thresholds(
                student_id, 
                features
            )
            
            # Use adjusted scores
            engagement_score = (
                adjusted_features['gaze_score'] * 0.30 + ...
            )
            
            return engagement_score
    """
    # Integration example provided in docstring above
    # See get_personalized_features() method for the actual implementation


if __name__ == "__main__":
    # Test calibration
    calibrator = EngagementCalibrator()
    
    print("Engagement Calibration System Initialized")
    print(f"Calibration directory: {calibrator.calibration_dir}")
    print(f"Calibration duration: {calibrator.calibration_duration} seconds")
    print(f"Minimum frames required: {calibrator.min_frames_required}")
