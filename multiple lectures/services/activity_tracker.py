"""
Comprehensive Activity Tracking Service
Tracks all user actions with timestamps, session IDs, and persistent storage
Supports live dashboard and CSV export capabilities
"""

import json
import os
import csv
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import threading


class ActivityTracker:
    """Comprehensive activity tracking for all user actions"""
    
    def __init__(self, storage_path="./storage/activity_tracking.json", 
                 session_storage_path="./storage/session_tracking.json"):
        """
        Initialize activity tracker
        
        Args:
            storage_path: Path to activity tracking JSON file
            session_storage_path: Path to session tracking JSON file
        """
        self.storage_path = storage_path
        self.session_storage_path = session_storage_path
        self.lock = threading.Lock()
        
        # Ensure storage directory exists
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)
        os.makedirs(os.path.dirname(session_storage_path), exist_ok=True)
        
        # Initialize storage files
        self._initialize_storage()
    
    def _initialize_storage(self):
        """Initialize storage files if they don't exist"""
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, 'w') as f:
                json.dump({'activities': []}, f)
        
        if not os.path.exists(self.session_storage_path):
            with open(self.session_storage_path, 'w') as f:
                json.dump({'sessions': {}}, f)
    
    def _load_activities(self) -> Dict:
        """Load activities from storage"""
        try:
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {'activities': []}
    
    def _save_activities(self, data: Dict):
        """Save activities to storage"""
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_sessions(self) -> Dict:
        """Load sessions from storage"""
        try:
            with open(self.session_storage_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {'sessions': {}}
    
    def _save_sessions(self, data: Dict):
        """Save sessions to storage"""
        with open(self.session_storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def track_event(self, user_id: str, event_type: str, event_data: Dict[str, Any],
                   session_id: Optional[str] = None, role: str = "student") -> str:
        """
        Track a user event
        
        Args:
            user_id: User ID
            event_type: Type of event (login, logout, lecture_start, quiz_submit, etc.)
            event_data: Additional event data
            session_id: Session ID (generated if not provided)
            role: User role (student, teacher, admin)
        
        Returns:
            Activity ID
        """
        with self.lock:
            activity_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat()
            
            if not session_id:
                session_id = self._get_or_create_session(user_id, role)
            
            activity = {
                'activity_id': activity_id,
                'user_id': user_id,
                'role': role,
                'event_type': event_type,
                'event_data': event_data,
                'session_id': session_id,
                'timestamp': timestamp
            }
            
            # Load and save activities
            data = self._load_activities()
            data['activities'].append(activity)
            self._save_activities(data)
            
            return activity_id
    
    def _get_or_create_session(self, user_id: str, role: str) -> str:
        """Get existing session or create new one"""
        sessions_data = self._load_sessions()
        
        # Check for active session
        for session_id, session in sessions_data['sessions'].items():
            if session['user_id'] == user_id and not session.get('ended'):
                return session_id
        
        # Create new session
        session_id = str(uuid.uuid4())
        sessions_data['sessions'][session_id] = {
            'session_id': session_id,
            'user_id': user_id,
            'role': role,
            'started_at': datetime.utcnow().isoformat(),
            'ended': False,
            'ended_at': None
        }
        self._save_sessions(sessions_data)
        
        return session_id
    
    def end_session(self, session_id: str):
        """End a user session"""
        with self.lock:
            sessions_data = self._load_sessions()
            
            if session_id in sessions_data['sessions']:
                sessions_data['sessions'][session_id]['ended'] = True
                sessions_data['sessions'][session_id]['ended_at'] = datetime.utcnow().isoformat()
                self._save_sessions(sessions_data)
    
    def get_user_activities(self, user_id: str, 
                           event_type: Optional[str] = None,
                           start_date: Optional[str] = None,
                           end_date: Optional[str] = None,
                           limit: Optional[int] = None) -> List[Dict]:
        """
        Get activities for a specific user
        
        Args:
            user_id: User ID
            event_type: Filter by event type (optional)
            start_date: Filter by start date (ISO format)
            end_date: Filter by end date (ISO format)
            limit: Maximum number of results
        
        Returns:
            List of activities
        """
        data = self._load_activities()
        activities = data['activities']
        
        # Filter by user
        filtered = [a for a in activities if a['user_id'] == user_id]
        
        # Filter by event type
        if event_type:
            filtered = [a for a in filtered if a['event_type'] == event_type]
        
        # Filter by date range
        if start_date:
            filtered = [a for a in filtered if a['timestamp'] >= start_date]
        if end_date:
            filtered = [a for a in filtered if a['timestamp'] <= end_date]
        
        # Sort by timestamp (descending)
        filtered.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Apply limit
        if limit:
            filtered = filtered[:limit]
        
        return filtered
    
    def get_course_activities(self, course_id: str, 
                             teacher_id: Optional[str] = None) -> List[Dict]:
        """
        Get all activities for a specific course
        
        Args:
            course_id: Course ID
            teacher_id: Filter by teacher (optional)
        
        Returns:
            List of activities
        """
        data = self._load_activities()
        activities = data['activities']
        
        # Filter by course
        filtered = [a for a in activities 
                   if a['event_data'].get('course_id') == course_id]
        
        # Filter by teacher
        if teacher_id:
            filtered = [a for a in filtered if a['user_id'] == teacher_id]
        
        # Sort by timestamp (descending)
        filtered.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return filtered
    
    def get_student_activities_in_course(self, course_id: str, 
                                        student_id: str) -> List[Dict]:
        """Get activities for a specific student in a specific course"""
        data = self._load_activities()
        activities = data['activities']
        
        filtered = [a for a in activities 
                   if a['user_id'] == student_id and 
                   a['event_data'].get('course_id') == course_id]
        
        filtered.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return filtered
    
    def get_all_student_activities(self, student_id: str) -> List[Dict]:
        """Get all activities for a student"""
        return self.get_user_activities(student_id)
    
    def get_session_details(self, session_id: str) -> Optional[Dict]:
        """Get details for a specific session"""
        sessions_data = self._load_sessions()
        return sessions_data['sessions'].get(session_id)
    
    def get_user_sessions(self, user_id: str) -> List[Dict]:
        """Get all sessions for a user"""
        sessions_data = self._load_sessions()
        user_sessions = [s for s in sessions_data['sessions'].values() 
                        if s['user_id'] == user_id]
        user_sessions.sort(key=lambda x: x['started_at'], reverse=True)
        return user_sessions
    
    def export_to_csv(self, filepath: str, user_id: Optional[str] = None,
                     course_id: Optional[str] = None):
        """
        Export activities to CSV
        
        Args:
            filepath: Output CSV file path
            user_id: Filter by user (optional)
            course_id: Filter by course (optional)
        """
        data = self._load_activities()
        activities = data['activities']
        
        # Apply filters
        if user_id:
            activities = [a for a in activities if a['user_id'] == user_id]
        if course_id:
            activities = [a for a in activities 
                         if a['event_data'].get('course_id') == course_id]
        
        # Write to CSV
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            if activities:
                fieldnames = ['activity_id', 'user_id', 'role', 'event_type', 
                             'session_id', 'timestamp', 'event_data']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for activity in activities:
                    row = activity.copy()
                    row['event_data'] = json.dumps(row['event_data'])
                    writer.writerow(row)
    
    def get_statistics(self, user_id: Optional[str] = None, 
                      course_id: Optional[str] = None) -> Dict:
        """
        Get activity statistics
        
        Args:
            user_id: Filter by user (optional)
            course_id: Filter by course (optional)
        
        Returns:
            Dictionary with statistics
        """
        data = self._load_activities()
        activities = data['activities']
        
        # Apply filters
        if user_id:
            activities = [a for a in activities if a['user_id'] == user_id]
        if course_id:
            activities = [a for a in activities 
                         if a['event_data'].get('course_id') == course_id]
        
        # Calculate statistics
        event_counts = {}
        for activity in activities:
            event_type = activity['event_type']
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        return {
            'total_activities': len(activities),
            'event_counts': event_counts,
            'unique_users': len(set(a['user_id'] for a in activities)),
            'unique_sessions': len(set(a['session_id'] for a in activities))
        }


# Singleton instance
_tracker_instance = None


def get_activity_tracker() -> ActivityTracker:
    """Get singleton activity tracker instance"""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = ActivityTracker()
    return _tracker_instance


# Convenience tracking functions

def track_login(user_id: str, role: str, session_id: Optional[str] = None):
    """Track user login"""
    tracker = get_activity_tracker()
    return tracker.track_event(
        user_id=user_id,
        event_type='login',
        event_data={'action': 'user_logged_in'},
        session_id=session_id,
        role=role
    )


def track_logout(user_id: str, role: str, session_id: str):
    """Track user logout"""
    tracker = get_activity_tracker()
    tracker.end_session(session_id)
    return tracker.track_event(
        user_id=user_id,
        event_type='logout',
        event_data={'action': 'user_logged_out'},
        session_id=session_id,
        role=role
    )


def track_lecture_start(user_id: str, lecture_id: str, course_id: str, 
                       lecture_title: str, session_id: Optional[str] = None):
    """Track lecture start"""
    tracker = get_activity_tracker()
    return tracker.track_event(
        user_id=user_id,
        event_type='lecture_start',
        event_data={
            'lecture_id': lecture_id,
            'course_id': course_id,
            'lecture_title': lecture_title,
            'action': 'started_lecture'
        },
        session_id=session_id,
        role='student'
    )


def track_lecture_end(user_id: str, lecture_id: str, course_id: str,
                     duration_seconds: int, session_id: Optional[str] = None):
    """Track lecture end"""
    tracker = get_activity_tracker()
    return tracker.track_event(
        user_id=user_id,
        event_type='lecture_end',
        event_data={
            'lecture_id': lecture_id,
            'course_id': course_id,
            'duration_seconds': duration_seconds,
            'action': 'completed_lecture'
        },
        session_id=session_id,
        role='student'
    )


def track_quiz_start(user_id: str, quiz_id: str, lecture_id: str, 
                    course_id: str, session_id: Optional[str] = None):
    """Track quiz start"""
    tracker = get_activity_tracker()
    return tracker.track_event(
        user_id=user_id,
        event_type='quiz_start',
        event_data={
            'quiz_id': quiz_id,
            'lecture_id': lecture_id,
            'course_id': course_id,
            'action': 'started_quiz'
        },
        session_id=session_id,
        role='student'
    )


def track_quiz_submit(user_id: str, quiz_id: str, lecture_id: str,
                     course_id: str, score: float, duration_seconds: int,
                     session_id: Optional[str] = None):
    """Track quiz submission"""
    tracker = get_activity_tracker()
    return tracker.track_event(
        user_id=user_id,
        event_type='quiz_submit',
        event_data={
            'quiz_id': quiz_id,
            'lecture_id': lecture_id,
            'course_id': course_id,
            'score': score,
            'duration_seconds': duration_seconds,
            'action': 'submitted_quiz'
        },
        session_id=session_id,
        role='student'
    )


def track_material_download(user_id: str, material_id: str, course_id: str,
                           material_name: str, session_id: Optional[str] = None):
    """Track material download"""
    tracker = get_activity_tracker()
    return tracker.track_event(
        user_id=user_id,
        event_type='material_download',
        event_data={
            'material_id': material_id,
            'course_id': course_id,
            'material_name': material_name,
            'action': 'downloaded_material'
        },
        session_id=session_id,
        role='student'
    )


def track_notes_reading(user_id: str, lecture_id: str, course_id: str,
                       duration_seconds: int, session_id: Optional[str] = None):
    """Track time spent reading notes"""
    tracker = get_activity_tracker()
    return tracker.track_event(
        user_id=user_id,
        event_type='notes_reading',
        event_data={
            'lecture_id': lecture_id,
            'course_id': course_id,
            'duration_seconds': duration_seconds,
            'action': 'read_notes'
        },
        session_id=session_id,
        role='student'
    )


def track_assignment_interaction(user_id: str, assignment_id: str, 
                                course_id: str, interaction_type: str,
                                session_id: Optional[str] = None):
    """Track assignment interaction (view, submit, download)"""
    tracker = get_activity_tracker()
    return tracker.track_event(
        user_id=user_id,
        event_type='assignment_interaction',
        event_data={
            'assignment_id': assignment_id,
            'course_id': course_id,
            'interaction_type': interaction_type,
            'action': f'assignment_{interaction_type}'
        },
        session_id=session_id,
        role='student'
    )


def track_attendance(user_id: str, course_id: str, lecture_id: str,
                    status: str, session_id: Optional[str] = None):
    """Track attendance"""
    tracker = get_activity_tracker()
    return tracker.track_event(
        user_id=user_id,
        event_type='attendance',
        event_data={
            'course_id': course_id,
            'lecture_id': lecture_id,
            'status': status,
            'action': 'marked_attendance'
        },
        session_id=session_id,
        role='student'
    )


def track_ai_tool_usage(user_id: str, tool_name: str, duration_seconds: int,
                       course_id: Optional[str] = None, 
                       session_id: Optional[str] = None):
    """Track AI tool usage"""
    tracker = get_activity_tracker()
    return tracker.track_event(
        user_id=user_id,
        event_type='ai_tool_usage',
        event_data={
            'tool_name': tool_name,
            'duration_seconds': duration_seconds,
            'course_id': course_id,
            'action': 'used_ai_tool'
        },
        session_id=session_id,
        role='student'
    )


def track_tab_switch(user_id: str, from_tab: str, to_tab: str,
                    session_id: Optional[str] = None):
    """Track tab switch"""
    tracker = get_activity_tracker()
    return tracker.track_event(
        user_id=user_id,
        event_type='tab_switch',
        event_data={
            'from_tab': from_tab,
            'to_tab': to_tab,
            'action': 'switched_tab'
        },
        session_id=session_id,
        role='student'
    )


def track_feedback_given(user_id: str, course_id: str, lecture_id: Optional[str] = None,
                        session_id: Optional[str] = None):
    """Track feedback given (anonymized - content not stored)"""
    tracker = get_activity_tracker()
    event_data = {
        'course_id': course_id,
        'action': 'gave_feedback',
        'note': 'Feedback content is anonymized'
    }
    if lecture_id:
        event_data['lecture_id'] = lecture_id
    
    return tracker.track_event(
        user_id=user_id,
        event_type='feedback_given',
        event_data=event_data,
        session_id=session_id,
        role='student'
    )


def track_teacher_action(user_id: str, action_type: str, action_data: Dict,
                        session_id: Optional[str] = None):
    """Track teacher actions (course updates, quiz generation, content uploads)"""
    tracker = get_activity_tracker()
    return tracker.track_event(
        user_id=user_id,
        event_type='teacher_action',
        event_data={
            'action_type': action_type,
            **action_data
        },
        session_id=session_id,
        role='teacher'
    )
