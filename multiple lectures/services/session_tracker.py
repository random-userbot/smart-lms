"""
Smart LMS - Global Session Activity Tracker
Comprehensive tracking from login to logout with detailed activity summaries
"""

import os
import json
import csv
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GlobalSessionTracker:
    """
    Tracks complete user session from login to logout
    Aggregates all activities: lectures, quizzes, materials, assignments, etc.
    """
    
    def __init__(self, student_id: str):
        """
        Initialize global session tracker
        
        Args:
            student_id: Student user ID
        """
        self.student_id = student_id
        self.session_start = datetime.utcnow()
        self.session_id = f"{student_id}_{self.session_start.strftime('%Y%m%d_%H%M%S')}"
        
        # Session data structure
        self.session_data = {
            'session_id': self.session_id,
            'student_id': student_id,
            'login_time': self.session_start.isoformat(),
            'logout_time': None,
            'total_duration': 0,
            
            # Activity counters
            'lectures_watched': [],
            'quizzes_taken': [],
            'assignments_submitted': [],
            'materials_read': [],
            'resources_downloaded': [],
            'feedback_submitted': [],
            
            # Time tracking (seconds)
            'time_on_lectures': 0,
            'time_on_quizzes': 0,
            'time_on_materials': 0,
            'time_on_assignments': 0,
            'time_idle': 0,
            
            # Engagement metrics
            'avg_lecture_engagement': 0,
            'avg_quiz_score': 0,
            'total_violations': 0,
            'overall_integrity_score': 100,
            
            # Page visits
            'pages_visited': [],
            'current_activity': None,
            'activity_start_time': None
        }
        
        # Directories
        self.session_logs_dir = "ml_data/session_logs"
        self.global_activity_dir = "ml_data/activity_logs"
        os.makedirs(self.session_logs_dir, exist_ok=True)
        os.makedirs(self.global_activity_dir, exist_ok=True)
        
        # File paths
        self.session_file = os.path.join(
            self.session_logs_dir,
            f"global_session_{self.session_id}.json"
        )
        
        self.activity_summary_file = os.path.join(
            self.global_activity_dir,
            f"activity_summary_{student_id}_{self.session_start.strftime('%Y%m')}.csv"
        )
        
        logger.info(f"GlobalSessionTracker initialized for {student_id}")
    
    def start_activity(self, activity_type: str, activity_id: str, metadata: Dict = None):
        """
        Start tracking a new activity
        
        Args:
            activity_type: 'lecture', 'quiz', 'material', 'assignment'
            activity_id: Unique identifier for activity
            metadata: Additional context (course_id, title, etc.)
        """
        # End previous activity if any
        if self.session_data['current_activity']:
            self._end_current_activity()
        
        self.session_data['current_activity'] = {
            'type': activity_type,
            'id': activity_id,
            'metadata': metadata or {},
            'start_time': datetime.utcnow().isoformat()
        }
        self.session_data['activity_start_time'] = datetime.utcnow()
        
        logger.debug(f"Started activity: {activity_type} - {activity_id}")
    
    def _end_current_activity(self):
        """End current activity and record duration"""
        if not self.session_data['current_activity']:
            return
        
        activity = self.session_data['current_activity']
        duration = (datetime.utcnow() - self.session_data['activity_start_time']).total_seconds()
        
        activity['end_time'] = datetime.utcnow().isoformat()
        activity['duration'] = duration
        
        # Update time tracking
        activity_type = activity['type']
        if activity_type == 'lecture':
            self.session_data['time_on_lectures'] += duration
        elif activity_type == 'quiz':
            self.session_data['time_on_quizzes'] += duration
        elif activity_type == 'material':
            self.session_data['time_on_materials'] += duration
        elif activity_type == 'assignment':
            self.session_data['time_on_assignments'] += duration
        
        # Clear current activity
        self.session_data['current_activity'] = None
        self.session_data['activity_start_time'] = None
    
    def log_lecture_watched(self, lecture_id: str, course_id: str, duration: float, 
                             engagement_score: float, completion_pct: float):
        """
        Log lecture watching activity
        
        Args:
            lecture_id: Lecture identifier
            course_id: Course identifier
            duration: Watch duration in seconds
            engagement_score: Average engagement score (0-100)
            completion_pct: Percentage completed (0-100)
        """
        lecture_data = {
            'lecture_id': lecture_id,
            'course_id': course_id,
            'duration': duration,
            'engagement_score': engagement_score,
            'completion_pct': completion_pct,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.session_data['lectures_watched'].append(lecture_data)
        self.session_data['time_on_lectures'] += duration
        
        # Update average engagement
        all_scores = [l['engagement_score'] for l in self.session_data['lectures_watched']]
        self.session_data['avg_lecture_engagement'] = sum(all_scores) / len(all_scores)
    
    def log_quiz_taken(self, quiz_id: str, lecture_id: str, score: float, 
                        duration: float, violations: int = 0):
        """
        Log quiz taking activity
        
        Args:
            quiz_id: Quiz identifier
            lecture_id: Associated lecture ID
            score: Quiz score (0-100)
            duration: Time taken in seconds
            violations: Number of integrity violations during quiz
        """
        quiz_data = {
            'quiz_id': quiz_id,
            'lecture_id': lecture_id,
            'score': score,
            'duration': duration,
            'violations': violations,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.session_data['quizzes_taken'].append(quiz_data)
        self.session_data['time_on_quizzes'] += duration
        self.session_data['total_violations'] += violations
        
        # Update average quiz score
        all_scores = [q['score'] for q in self.session_data['quizzes_taken']]
        self.session_data['avg_quiz_score'] = sum(all_scores) / len(all_scores) if all_scores else 0
    
    def log_material_read(self, material_id: str, lecture_id: str, title: str,
                          time_spent: float, pages_viewed: int = 1):
        """
        Log material reading activity
        
        Args:
            material_id: Material identifier
            lecture_id: Associated lecture ID
            title: Material title
            time_spent: Time spent reading in seconds
            pages_viewed: Number of pages/sections viewed
        """
        material_data = {
            'material_id': material_id,
            'lecture_id': lecture_id,
            'title': title,
            'time_spent': time_spent,
            'pages_viewed': pages_viewed,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.session_data['materials_read'].append(material_data)
        self.session_data['time_on_materials'] += time_spent
    
    def log_assignment_submitted(self, assignment_id: str, course_id: str,
                                   time_spent: float, status: str = 'submitted'):
        """
        Log assignment submission
        
        Args:
            assignment_id: Assignment identifier
            course_id: Course identifier
            time_spent: Time spent on assignment in seconds
            status: 'draft', 'submitted', 'late'
        """
        assignment_data = {
            'assignment_id': assignment_id,
            'course_id': course_id,
            'time_spent': time_spent,
            'status': status,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.session_data['assignments_submitted'].append(assignment_data)
        self.session_data['time_on_assignments'] += time_spent
    
    def log_resource_downloaded(self, resource_id: str, resource_type: str):
        """Log resource download"""
        self.session_data['resources_downloaded'].append({
            'resource_id': resource_id,
            'type': resource_type,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def log_feedback_submitted(self, feedback_type: str, target_id: str, rating: int):
        """Log feedback submission"""
        self.session_data['feedback_submitted'].append({
            'type': feedback_type,
            'target_id': target_id,
            'rating': rating,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def log_page_visit(self, page_name: str):
        """Log page navigation"""
        self.session_data['pages_visited'].append({
            'page': page_name,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def update_violations(self, violation_count: int):
        """Update total violations"""
        self.session_data['total_violations'] += violation_count
        
        # Recalculate integrity score
        self.session_data['overall_integrity_score'] = max(
            0, 
            100 - (self.session_data['total_violations'] * 3)
        )
    
    def end_session(self):
        """End session and save comprehensive summary"""
        # End any ongoing activity
        if self.session_data['current_activity']:
            self._end_current_activity()
        
        # Set logout time
        self.session_data['logout_time'] = datetime.utcnow().isoformat()
        
        # Calculate total duration
        logout_time = datetime.utcnow()
        total_duration = (logout_time - self.session_start).total_seconds()
        self.session_data['total_duration'] = total_duration
        
        # Calculate idle time
        active_time = (
            self.session_data['time_on_lectures'] +
            self.session_data['time_on_quizzes'] +
            self.session_data['time_on_materials'] +
            self.session_data['time_on_assignments']
        )
        self.session_data['time_idle'] = max(0, total_duration - active_time)
        
        # Save detailed session JSON
        with open(self.session_file, 'w') as f:
            json.dump(self.session_data, f, indent=2)
        
        # Append to activity summary CSV
        self._append_to_activity_summary()
        
        logger.info(f"Session {self.session_id} ended. Total duration: {total_duration:.1f}s")
    
    def _append_to_activity_summary(self):
        """Append session summary to monthly CSV"""
        file_exists = os.path.exists(self.activity_summary_file)
        
        summary = {
            'session_id': self.session_id,
            'student_id': self.student_id,
            'date': self.session_start.strftime('%Y-%m-%d'),
            'login_time': self.session_data['login_time'],
            'logout_time': self.session_data['logout_time'],
            'total_duration_min': round(self.session_data['total_duration'] / 60, 2),
            
            # Activity counts
            'lectures_watched': len(self.session_data['lectures_watched']),
            'quizzes_taken': len(self.session_data['quizzes_taken']),
            'materials_read': len(self.session_data['materials_read']),
            'assignments_submitted': len(self.session_data['assignments_submitted']),
            'resources_downloaded': len(self.session_data['resources_downloaded']),
            'feedback_submitted': len(self.session_data['feedback_submitted']),
            
            # Time distribution (minutes)
            'time_on_lectures_min': round(self.session_data['time_on_lectures'] / 60, 2),
            'time_on_quizzes_min': round(self.session_data['time_on_quizzes'] / 60, 2),
            'time_on_materials_min': round(self.session_data['time_on_materials'] / 60, 2),
            'time_on_assignments_min': round(self.session_data['time_on_assignments'] / 60, 2),
            'time_idle_min': round(self.session_data['time_idle'] / 60, 2),
            
            # Performance metrics
            'avg_lecture_engagement': round(self.session_data['avg_lecture_engagement'], 2),
            'avg_quiz_score': round(self.session_data['avg_quiz_score'], 2),
            'total_violations': self.session_data['total_violations'],
            'overall_integrity_score': round(self.session_data['overall_integrity_score'], 2)
        }
        
        with open(self.activity_summary_file, 'a', newline='') as f:
            fieldnames = list(summary.keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(summary)
    
    def get_current_summary(self) -> Dict:
        """Get current session summary (before ending)"""
        current_duration = (datetime.utcnow() - self.session_start).total_seconds()
        
        return {
            'session_id': self.session_id,
            'duration_minutes': round(current_duration / 60, 2),
            'lectures_watched': len(self.session_data['lectures_watched']),
            'quizzes_taken': len(self.session_data['quizzes_taken']),
            'materials_read': len(self.session_data['materials_read']),
            'assignments_submitted': len(self.session_data['assignments_submitted']),
            'avg_engagement': round(self.session_data['avg_lecture_engagement'], 2),
            'avg_quiz_score': round(self.session_data['avg_quiz_score'], 2),
            'integrity_score': round(self.session_data['overall_integrity_score'], 2)
        }


# Global session tracker instance
_global_session_tracker = None

def get_global_session_tracker(student_id: str) -> GlobalSessionTracker:
    """Get or create global session tracker"""
    global _global_session_tracker
    
    if _global_session_tracker is None or _global_session_tracker.student_id != student_id:
        _global_session_tracker = GlobalSessionTracker(student_id)
    
    return _global_session_tracker

def cleanup_global_session():
    """Cleanup global session tracker"""
    global _global_session_tracker
    
    if _global_session_tracker:
        _global_session_tracker.end_session()
        _global_session_tracker = None


# Export
__all__ = ['GlobalSessionTracker', 'get_global_session_tracker', 'cleanup_global_session']
