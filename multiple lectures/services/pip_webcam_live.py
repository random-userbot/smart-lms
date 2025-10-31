"""
Smart LMS - Picture-in-Picture Webcam Live Service
Real-time webcam capture with OpenFace integration and frame logging
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

from services.openface_processor import get_openface_processor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PiPWebcamLive:
    """
    Picture-in-Picture webcam with real-time OpenFace processing
    Captures frames every second, extracts features, saves to captured_frames
    """
    
    def __init__(self, lecture_id: str, course_id: str, student_id: str):
        """
        Initialize PiP webcam
        
        Args:
            lecture_id: Current lecture ID
            course_id: Current course ID
            student_id: Current student ID
        """
        self.lecture_id = lecture_id
        self.course_id = course_id
        self.student_id = student_id
        
        # Generate session ID
        self.session_id = f"{student_id}_{lecture_id}_{uuid.uuid4().hex[:8]}"
        
        # Initialize OpenFace processor
        self.openface = get_openface_processor()
        self.openface.set_session_id(self.session_id)
        
        # Frame capture settings
        self.capture_interval = 1.0  # seconds
        self.last_capture_time = 0
        self.frame_count = 0
        
        # Directories
        self.captured_frames_dir = "ml_data/captured_frames"
        self.engagement_logs_dir = "ml_data/engagement_logs"
        os.makedirs(self.captured_frames_dir, exist_ok=True)
        os.makedirs(self.engagement_logs_dir, exist_ok=True)
        
        # Session data
        self.session_data = {
            'session_id': self.session_id,
            'student_id': student_id,
            'lecture_id': lecture_id,
            'course_id': course_id,
            'start_time': datetime.utcnow().isoformat(),
            'total_frames': 0,
            'engagement_scores': []
        }
        
        # Thread-safe engagement data
        self.current_engagement = {
            'score': 0.0,
            'status': 'no_face',
            'frame_count': 0
        }
        self.engagement_lock = Lock()
        
        logger.info(f"PiPWebcamLive initialized for session {self.session_id}")
    
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
            
            # Save frame with metadata
            self._save_captured_frame(img, engagement_data)
            
            # Update current engagement
            with self.engagement_lock:
                self.current_engagement['score'] = engagement_data['engagement_score']
                self.current_engagement['status'] = engagement_data['status']
                self.current_engagement['frame_count'] = self.frame_count
            
            # Add to session data
            self.session_data['engagement_scores'].append(engagement_data['engagement_score'])
            self.session_data['total_frames'] = self.frame_count
            
            # Periodically save to CSV
            if self.frame_count % 10 == 0:
                self.openface.save_features_to_csv()
        
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
        
        # Append to engagement log CSV
        self._append_to_engagement_log(log_entry)
        
        logger.debug(f"Saved frame {self.frame_count}: {filename} | Score: {engagement_data['engagement_score']}")
    
    def _append_to_engagement_log(self, log_entry: Dict):
        """Append entry to engagement log CSV"""
        import csv
        
        log_file = os.path.join(self.engagement_logs_dir, f"engagement_log_{self.session_id}.csv")
        
        file_exists = os.path.exists(log_file)
        
        with open(log_file, 'a', newline='') as f:
            fieldnames = [
                'timestamp', 'session_id', 'student_id', 'lecture_id', 'course_id',
                'frame_path', 'engagement_score', 'status', 'face_detected',
                'gaze_angle_x', 'gaze_angle_y', 'head_pose_rx', 'head_pose_ry', 'head_pose_rz'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(log_entry)
    
    def _draw_engagement_overlay(self, frame: np.ndarray, engagement: Dict) -> np.ndarray:
        """
        Draw engagement score and status overlay on frame
        
        Args:
            frame: BGR image
            engagement: Current engagement data
        
        Returns:
            Annotated frame
        """
        h, w = frame.shape[:2]
        overlay = frame.copy()
        
        # Draw semi-transparent background for text
        cv2.rectangle(overlay, (10, h - 80), (w - 10, h - 10), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        
        # Engagement score
        score = engagement['score']
        status = engagement['status']
        
        # Color based on score
        if score >= 75:
            color = (0, 255, 0)  # Green
        elif score >= 50:
            color = (0, 255, 255)  # Yellow
        elif score >= 30:
            color = (0, 165, 255)  # Orange
        else:
            color = (0, 0, 255)  # Red
        
        # Draw engagement score
        score_text = f"Engagement: {score:.1f}/100"
        cv2.putText(frame, score_text, (20, h - 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # Draw status
        status_text = f"Status: {status.replace('_', ' ').title()}"
        cv2.putText(frame, status_text, (20, h - 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Draw frame count
        frame_text = f"Frame: {engagement['frame_count']}"
        cv2.putText(frame, frame_text, (w - 150, h - 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
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
        
        return {
            'session_id': self.session_id,
            'avg_engagement': np.mean(self.session_data['engagement_scores']),
            'min_engagement': np.min(self.session_data['engagement_scores']),
            'max_engagement': np.max(self.session_data['engagement_scores']),
            'total_frames': self.session_data['total_frames'],
            'session_duration': duration,
            'frames_per_minute': self.session_data['total_frames'] / (duration / 60) if duration > 0 else 0
        }
    
    def end_session(self):
        """End session and save final data"""
        # Save remaining features
        self.openface.save_features_to_csv()
        
        # Save session summary
        summary = self.get_session_summary()
        summary_file = os.path.join(self.engagement_logs_dir, f"session_summary_{self.session_id}.json")
        
        import json
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Session {self.session_id} ended. Avg engagement: {summary['avg_engagement']:.2f}")


def render_pip_webcam(lecture_id: str, course_id: str, student_id: str, 
                       on_engagement_update: Optional[Callable] = None) -> PiPWebcamLive:
    """
    Render Picture-in-Picture webcam component
    
    Args:
        lecture_id: Current lecture ID
        course_id: Current course ID
        student_id: Current student ID
        on_engagement_update: Callback for engagement updates
    
    Returns:
        PiPWebcamLive instance
    """
    # Initialize PiP webcam
    if 'pip_webcam' not in st.session_state:
        st.session_state.pip_webcam = PiPWebcamLive(lecture_id, course_id, student_id)
    
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
    Render engagement metrics in sidebar
    
    Args:
        pip_webcam: PiPWebcamLive instance
    """
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Live Engagement")
    
    # Get current engagement
    engagement = pip_webcam.get_current_engagement()
    
    # Display engagement score
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
        label=f"{emoji} Engagement Score",
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
    
    # Progress bar for engagement
    st.sidebar.progress(score / 100)
    
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
