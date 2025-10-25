"""
Smart LMS - Behavioral Logging Service
Tracks all user interactions and behaviors during lecture sessions
Logs: login/logout, tab switches, playback speed changes, focus lost, feedback submissions
"""

import os
import csv
import json
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BehavioralLogger:
    """
    Comprehensive behavioral logging system
    Tracks all student interactions for analytics and integrity monitoring
    """
    
    def __init__(self, student_id: str, lecture_id: str = None, course_id: str = None):
        """
        Initialize behavioral logger
        
        Args:
            student_id: Student user ID
            lecture_id: Current lecture ID (optional)
            course_id: Current course ID (optional)
        """
        self.student_id = student_id
        self.lecture_id = lecture_id
        self.course_id = course_id
        
        # Generate session ID
        self.session_id = f"{student_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Directories
        self.activity_logs_dir = "ml_data/activity_logs"
        self.session_logs_dir = "ml_data/session_logs"
        os.makedirs(self.activity_logs_dir, exist_ok=True)
        os.makedirs(self.session_logs_dir, exist_ok=True)
        
        # File paths
        self.behavioral_log_file = os.path.join(
            self.activity_logs_dir, 
            f"behavioral_log_{student_id}_{datetime.utcnow().strftime('%Y%m')}.csv"
        )
        self.session_log_file = os.path.join(
            self.session_logs_dir,
            f"session_{self.session_id}.json"
        )
        
        # Session data
        self.session_data = {
            'session_id': self.session_id,
            'student_id': student_id,
            'lecture_id': lecture_id,
            'course_id': course_id,
            'start_time': datetime.utcnow().isoformat(),
            'end_time': None,
            'events': [],
            'violations': [],
            'total_duration': 0,
            'active_duration': 0,
            'playback_speed_changes': 0,
            'tab_switches': 0,
            'focus_losses': 0,
            'video_pauses': 0,
            'video_seeks': 0,
            'feedbacks_submitted': 0
        }
        
        # Log session start
        self.log_event('session_start', {
            'lecture_id': lecture_id,
            'course_id': course_id
        })
        
        logger.info(f"BehavioralLogger initialized for session {self.session_id}")
    
    def log_event(self, event_type: str, event_data: Dict = None):
        """
        Log a behavioral event
        
        Args:
            event_type: Type of event (e.g., 'login', 'tab_switch', 'playback_speed_change')
            event_data: Additional event data
        """
        timestamp = datetime.utcnow().isoformat()
        
        event = {
            'timestamp': timestamp,
            'session_id': self.session_id,
            'student_id': self.student_id,
            'lecture_id': self.lecture_id,
            'course_id': self.course_id,
            'event_type': event_type,
            'event_data': json.dumps(event_data) if event_data else '{}'
        }
        
        # Add to session events
        self.session_data['events'].append(event)
        
        # Append to CSV
        self._append_to_behavioral_csv(event)
        
        # Update counters
        self._update_counters(event_type, event_data)
        
        logger.debug(f"Logged event: {event_type} | Session: {self.session_id}")
    
    def log_login(self, login_method: str = 'standard'):
        """Log user login"""
        self.log_event('login', {
            'method': login_method,
            'user_agent': 'streamlit_app'
        })
    
    def log_logout(self):
        """Log user logout"""
        self.log_event('logout', {
            'session_duration': self._get_session_duration()
        })
    
    def log_lecture_start(self, lecture_id: str, course_id: str, video_type: str = 'local'):
        """
        Log lecture viewing start
        
        Args:
            lecture_id: Lecture identifier
            course_id: Course identifier
            video_type: 'local' or 'youtube'
        """
        self.lecture_id = lecture_id
        self.course_id = course_id
        
        self.log_event('lecture_start', {
            'lecture_id': lecture_id,
            'course_id': course_id,
            'video_type': video_type
        })
    
    def log_lecture_end(self, completion_percentage: float = 100.0):
        """
        Log lecture viewing end
        
        Args:
            completion_percentage: How much of lecture was watched (0-100)
        """
        self.log_event('lecture_end', {
            'completion_percentage': completion_percentage,
            'duration': self._get_session_duration()
        })
    
    def log_tab_switch(self, away: bool = True):
        """
        Log tab switch or window focus change
        
        Args:
            away: True if switching away from app, False if returning
        """
        self.log_event('tab_switch', {
            'direction': 'away' if away else 'return'
        })
        
        if away:
            self.session_data['tab_switches'] += 1
    
    def log_focus_lost(self):
        """Log when page loses focus"""
        self.log_event('focus_lost', {})
        self.session_data['focus_losses'] += 1
    
    def log_focus_gained(self):
        """Log when page regains focus"""
        self.log_event('focus_gained', {})
    
    def log_playback_speed_change(self, old_speed: float, new_speed: float):
        """
        Log video playback speed change
        
        Args:
            old_speed: Previous playback speed
            new_speed: New playback speed
        """
        self.log_event('playback_speed_change', {
            'old_speed': old_speed,
            'new_speed': new_speed,
            'speed_increase': new_speed > old_speed
        })
        
        self.session_data['playback_speed_changes'] += 1
    
    def log_video_pause(self, video_position: float):
        """
        Log video pause
        
        Args:
            video_position: Current video position in seconds
        """
        self.log_event('video_pause', {
            'position': video_position
        })
        
        self.session_data['video_pauses'] += 1
    
    def log_video_play(self, video_position: float):
        """
        Log video play/resume
        
        Args:
            video_position: Current video position in seconds
        """
        self.log_event('video_play', {
            'position': video_position
        })
    
    def log_video_seek(self, from_position: float, to_position: float):
        """
        Log video seeking (skip forward/backward)
        
        Args:
            from_position: Starting position in seconds
            to_position: Target position in seconds
        """
        self.log_event('video_seek', {
            'from': from_position,
            'to': to_position,
            'skip_amount': to_position - from_position
        })
        
        self.session_data['video_seeks'] += 1
    
    def log_feedback_submission(self, feedback_type: str, rating: int = None):
        """
        Log feedback submission
        
        Args:
            feedback_type: Type of feedback ('lecture', 'quiz', 'course')
            rating: Numerical rating (1-5)
        """
        self.log_event('feedback_submission', {
            'type': feedback_type,
            'rating': rating
        })
        
        self.session_data['feedbacks_submitted'] += 1
    
    def log_quiz_attempt(self, quiz_id: str, score: float = None):
        """
        Log quiz attempt
        
        Args:
            quiz_id: Quiz identifier
            score: Quiz score (0-100)
        """
        self.log_event('quiz_attempt', {
            'quiz_id': quiz_id,
            'score': score
        })
    
    def log_resource_download(self, resource_id: str, resource_type: str):
        """
        Log resource download
        
        Args:
            resource_id: Resource identifier
            resource_type: Type of resource (pdf, video, etc.)
        """
        self.log_event('resource_download', {
            'resource_id': resource_id,
            'type': resource_type
        })
    
    def log_violation(self, violation_type: str, severity: str, details: Dict = None):
        """
        Log integrity violation
        
        Args:
            violation_type: Type of violation ('tab_switch', 'speed_excessive', etc.)
            severity: 'low', 'medium', 'high'
            details: Additional violation details
        """
        violation = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': violation_type,
            'severity': severity,
            'details': details or {}
        }
        
        self.session_data['violations'].append(violation)
        
        self.log_event('violation', {
            'violation_type': violation_type,
            'severity': severity,
            **( details or {})
        })
    
    def _append_to_behavioral_csv(self, event: Dict):
        """Append event to behavioral log CSV"""
        file_exists = os.path.exists(self.behavioral_log_file)
        
        with open(self.behavioral_log_file, 'a', newline='') as f:
            fieldnames = [
                'timestamp', 'session_id', 'student_id', 'lecture_id', 'course_id',
                'event_type', 'event_data'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(event)
    
    def _update_counters(self, event_type: str, event_data: Dict):
        """Update session counters based on event type"""
        # Counter updates are handled by specific log methods
        # This method exists for future extensibility
        return
    
    def _get_session_duration(self) -> float:
        """Get session duration in seconds"""
        start_time = datetime.fromisoformat(self.session_data['start_time'])
        return (datetime.utcnow() - start_time).total_seconds()
    
    def get_session_summary(self) -> Dict:
        """Get comprehensive session summary"""
        duration = self._get_session_duration()
        
        return {
            'session_id': self.session_id,
            'student_id': self.student_id,
            'lecture_id': self.lecture_id,
            'course_id': self.course_id,
            'start_time': self.session_data['start_time'],
            'total_duration': duration,
            'total_events': len(self.session_data['events']),
            'total_violations': len(self.session_data['violations']),
            'tab_switches': self.session_data['tab_switches'],
            'focus_losses': self.session_data['focus_losses'],
            'playback_speed_changes': self.session_data['playback_speed_changes'],
            'video_pauses': self.session_data['video_pauses'],
            'video_seeks': self.session_data['video_seeks'],
            'feedbacks_submitted': self.session_data['feedbacks_submitted'],
            'integrity_score': self._calculate_integrity_score()
        }
    
    def _calculate_integrity_score(self) -> float:
        """
        Calculate student integrity score (0-100)
        Higher score = better integrity
        """
        duration = self._get_session_duration()
        
        if duration < 60:  # Less than 1 minute
            return 100.0
        
        # Base score
        score = 100.0
        
        # Penalties
        score -= self.session_data['tab_switches'] * 2  # -2 per tab switch
        score -= self.session_data['focus_losses'] * 1.5  # -1.5 per focus loss
        score -= self.session_data['playback_speed_changes'] * 1  # -1 per speed change
        score -= len(self.session_data['violations']) * 5  # -5 per violation
        
        # Ensure score is between 0-100
        score = max(0.0, min(100.0, score))
        
        return round(score, 2)
    
    def end_session(self):
        """End session and save final data"""
        self.session_data['end_time'] = datetime.utcnow().isoformat()
        self.session_data['total_duration'] = self._get_session_duration()
        
        # Save session summary
        with open(self.session_log_file, 'w') as f:
            json.dump(self.session_data, f, indent=2)
        
        self.log_event('session_end', {
            'duration': self.session_data['total_duration'],
            'total_events': len(self.session_data['events']),
            'integrity_score': self._calculate_integrity_score()
        })
        
        logger.info(f"Session {self.session_id} ended. Duration: {self.session_data['total_duration']:.1f}s")
    
    def get_violations_summary(self) -> Dict:
        """Get summary of all violations"""
        if not self.session_data['violations']:
            return {
                'total_violations': 0,
                'by_type': {},
                'by_severity': {}
            }
        
        # Count by type
        by_type = {}
        for v in self.session_data['violations']:
            vtype = v['type']
            by_type[vtype] = by_type.get(vtype, 0) + 1
        
        # Count by severity
        by_severity = {}
        for v in self.session_data['violations']:
            severity = v['severity']
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        return {
            'total_violations': len(self.session_data['violations']),
            'by_type': by_type,
            'by_severity': by_severity,
            'integrity_score': self._calculate_integrity_score()
        }


# Singleton instance per session
_behavioral_loggers = {}

def get_behavioral_logger(student_id: str, lecture_id: str = None, 
                          course_id: str = None) -> BehavioralLogger:
    """
    Get or create behavioral logger for student
    
    Args:
        student_id: Student user ID
        lecture_id: Current lecture ID
        course_id: Current course ID
    
    Returns:
        BehavioralLogger instance
    """
    key = f"{student_id}_{lecture_id}"
    
    if key not in _behavioral_loggers:
        _behavioral_loggers[key] = BehavioralLogger(student_id, lecture_id, course_id)
    
    return _behavioral_loggers[key]


def cleanup_logger(student_id: str, lecture_id: str = None):
    """Clean up logger instance"""
    key = f"{student_id}_{lecture_id}"
    
    if key in _behavioral_loggers:
        _behavioral_loggers[key].end_session()
        del _behavioral_loggers[key]


# Export
__all__ = ['BehavioralLogger', 'get_behavioral_logger', 'cleanup_logger']
