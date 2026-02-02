"""
Universal Activity Logger
Tracks ALL user actions across the platform for intelligent engagement analysis
"""

import json
import csv
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import hashlib


class UniversalActivityLogger:
    """
    Comprehensive activity logger that tracks every user action
    For intelligent ML-based engagement scoring
    """
    
    def __init__(self, storage_dir: str = "./ml_data/activity_logs"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Action categories for classification
        self.ACTION_CATEGORIES = {
            'content_access': ['video_start', 'video_pause', 'video_resume', 'video_seek', 
                              'pdf_open', 'pdf_scroll', 'pdf_zoom', 'pdf_page_turn',
                              'material_view', 'lecture_enter', 'lecture_exit'],
            'content_download': ['pdf_download', 'material_download', 'video_download',
                                'resource_download'],
            'assessment': ['quiz_start', 'quiz_submit', 'quiz_review', 'assignment_start',
                          'assignment_submit', 'assignment_revise'],
            'interaction': ['mouse_click', 'mouse_move', 'scroll', 'keypress', 
                          'button_click', 'link_click', 'form_submit'],
            'navigation': ['page_view', 'page_leave', 'tab_switch', 'window_blur',
                          'window_focus', 'back_button', 'forward_button'],
            'feedback': ['feedback_submit', 'rating_given', 'comment_added',
                        'like_clicked', 'flag_raised'],
            'collaboration': ['message_sent', 'discussion_post', 'reply_added',
                            'file_shared', 'group_joined'],
            'system': ['login', 'logout', 'session_start', 'session_end',
                      'error_occurred', 'timeout'],
            'creation': ['upload_start', 'upload_complete', 'content_create',
                        'quiz_create', 'assignment_create', 'announcement_post']
        }
    
    def log_action(self, user_id: str, user_role: str, action_type: str, 
                   context: Dict[str, Any], metadata: Optional[Dict] = None):
        """
        Log any user action with full context
        
        Args:
            user_id: User identifier
            user_role: Role (student, teacher, admin)
            action_type: Type of action (e.g., 'pdf_open', 'quiz_submit')
            context: Action context (course_id, lecture_id, resource_id, etc.)
            metadata: Additional metadata (duration, score, file_size, etc.)
        """
        timestamp = datetime.now()
        
        # Create action record
        action = {
            'timestamp': timestamp.isoformat(),
            'unix_timestamp': int(timestamp.timestamp()),
            'user_id': user_id,
            'user_role': user_role,
            'action_type': action_type,
            'action_category': self._get_action_category(action_type),
            'session_id': self._get_or_create_session_id(user_id),
            'context': context,
            'metadata': metadata or {},
            'day_of_week': timestamp.strftime('%A'),
            'hour_of_day': timestamp.hour,
            'is_weekend': timestamp.weekday() >= 5
        }
        
        # Calculate action sequence features
        action['sequence_features'] = self._calculate_sequence_features(user_id, action_type)
        
        # Save to multiple formats for different use cases
        self._save_to_json(user_id, action)
        self._save_to_csv(user_id, action)
        self._update_session_summary(user_id, action)
        
        return action
    
    def _get_action_category(self, action_type: str) -> str:
        """Classify action into category"""
        for category, actions in self.ACTION_CATEGORIES.items():
            if action_type in actions:
                return category
        return 'other'
    
    def _get_or_create_session_id(self, user_id: str) -> str:
        """Get or create session ID for user"""
        session_file = self.storage_dir / f"session_{user_id}.json"
        
        now = datetime.now()
        
        if session_file.exists():
            with open(session_file, 'r') as f:
                session_data = json.load(f)
                last_activity = datetime.fromisoformat(session_data['last_activity'])
                
                # If last activity was within 30 minutes, same session
                if (now - last_activity).total_seconds() < 1800:
                    session_data['last_activity'] = now.isoformat()
                    session_data['action_count'] += 1
                    with open(session_file, 'w') as f:
                        json.dump(session_data, f)
                    return session_data['session_id']
        
        # Create new session
        session_id = hashlib.md5(f"{user_id}_{now.isoformat()}".encode()).hexdigest()[:12]
        session_data = {
            'session_id': session_id,
            'start_time': now.isoformat(),
            'last_activity': now.isoformat(),
            'action_count': 1
        }
        
        with open(session_file, 'w') as f:
            json.dump(session_data, f)
        
        return session_id
    
    def _calculate_sequence_features(self, user_id: str, current_action: str) -> Dict:
        """Calculate features based on action sequences"""
        recent_actions = self._get_recent_actions(user_id, limit=10)
        
        if not recent_actions:
            return {
                'actions_in_last_5min': 0,
                'actions_in_last_hour': 0,
                'time_since_last_action': 0,
                'action_diversity': 0,
                'repeated_action_count': 0
            }
        
        now = datetime.now()
        
        # Count actions in time windows
        actions_5min = sum(1 for a in recent_actions 
                          if (now - datetime.fromisoformat(a['timestamp'])).total_seconds() < 300)
        actions_1hour = sum(1 for a in recent_actions 
                           if (now - datetime.fromisoformat(a['timestamp'])).total_seconds() < 3600)
        
        # Time since last action
        last_action_time = datetime.fromisoformat(recent_actions[0]['timestamp'])
        time_since_last = (now - last_action_time).total_seconds()
        
        # Action diversity (unique action types in recent history)
        unique_actions = len(set(a['action_type'] for a in recent_actions))
        
        # Repeated action count
        repeated_count = sum(1 for a in recent_actions if a['action_type'] == current_action)
        
        return {
            'actions_in_last_5min': actions_5min,
            'actions_in_last_hour': actions_1hour,
            'time_since_last_action': time_since_last,
            'action_diversity': unique_actions,
            'repeated_action_count': repeated_count
        }
    
    def _get_recent_actions(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get recent actions for a user"""
        json_file = self.storage_dir / f"actions_{user_id}.json"
        
        if not json_file.exists():
            return []
        
        try:
            with open(json_file, 'r') as f:
                actions = json.load(f)
                return actions[-limit:] if actions else []
        except:
            return []
    
    def _save_to_json(self, user_id: str, action: Dict):
        """Save action to JSON file (for quick access)"""
        json_file = self.storage_dir / f"actions_{user_id}.json"
        
        actions = []
        if json_file.exists():
            with open(json_file, 'r') as f:
                try:
                    actions = json.load(f)
                except:
                    actions = []
        
        actions.append(action)
        
        # Keep only last 1000 actions in JSON (for performance)
        if len(actions) > 1000:
            actions = actions[-1000:]
        
        with open(json_file, 'w') as f:
            json.dump(actions, f, indent=2)
    
    def _save_to_csv(self, user_id: str, action: Dict):
        """Save action to CSV file (for ML training)"""
        year_month = datetime.now().strftime("%Y%m")
        csv_file = self.storage_dir / f"actions_{user_id}_{year_month}.csv"
        
        file_exists = csv_file.exists()
        
        # Flatten nested dictionaries for CSV
        flat_action = {
            'timestamp': action['timestamp'],
            'unix_timestamp': action['unix_timestamp'],
            'user_id': action['user_id'],
            'user_role': action['user_role'],
            'action_type': action['action_type'],
            'action_category': action['action_category'],
            'session_id': action['session_id'],
            'day_of_week': action['day_of_week'],
            'hour_of_day': action['hour_of_day'],
            'is_weekend': action['is_weekend'],
            
            # Context fields
            'course_id': action['context'].get('course_id', ''),
            'lecture_id': action['context'].get('lecture_id', ''),
            'resource_id': action['context'].get('resource_id', ''),
            'target_id': action['context'].get('target_id', ''),
            
            # Metadata fields
            'duration_seconds': action['metadata'].get('duration_seconds', 0),
            'file_size_bytes': action['metadata'].get('file_size_bytes', 0),
            'score': action['metadata'].get('score', 0),
            'success': action['metadata'].get('success', True),
            
            # Sequence features
            'actions_in_last_5min': action['sequence_features']['actions_in_last_5min'],
            'actions_in_last_hour': action['sequence_features']['actions_in_last_hour'],
            'time_since_last_action': action['sequence_features']['time_since_last_action'],
            'action_diversity': action['sequence_features']['action_diversity'],
            'repeated_action_count': action['sequence_features']['repeated_action_count']
        }
        
        with open(csv_file, 'a', newline='', encoding='utf-8') as f:
            fieldnames = list(flat_action.keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(flat_action)
    
    def _update_session_summary(self, user_id: str, action: Dict):
        """Update session summary statistics"""
        summary_file = self.storage_dir / f"session_summary_{user_id}.json"
        
        session_id = action['session_id']
        
        summaries = {}
        if summary_file.exists():
            with open(summary_file, 'r') as f:
                try:
                    summaries = json.load(f)
                except:
                    summaries = {}
        
        if session_id not in summaries:
            summaries[session_id] = {
                'session_id': session_id,
                'start_time': action['timestamp'],
                'end_time': action['timestamp'],
                'total_actions': 0,
                'action_categories': {},
                'resources_accessed': set(),
                'duration_seconds': 0
            }
        
        session = summaries[session_id]
        session['end_time'] = action['timestamp']
        session['total_actions'] += 1
        
        # Count by category
        category = action['action_category']
        session['action_categories'][category] = session['action_categories'].get(category, 0) + 1
        
        # Track resources
        if isinstance(session['resources_accessed'], set):
            session['resources_accessed'] = list(session['resources_accessed'])
        
        if 'resource_id' in action['context']:
            if action['context']['resource_id'] not in session['resources_accessed']:
                session['resources_accessed'].append(action['context']['resource_id'])
        
        # Calculate duration
        start = datetime.fromisoformat(session['start_time'])
        end = datetime.fromisoformat(session['end_time'])
        session['duration_seconds'] = (end - start).total_seconds()
        
        with open(summary_file, 'w') as f:
            json.dump(summaries, f, indent=2)
    
    def get_user_activity_summary(self, user_id: str, days: int = 7) -> Dict:
        """Get activity summary for a user"""
        recent_actions = self._get_recent_actions(user_id, limit=1000)
        
        cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)
        recent_actions = [a for a in recent_actions if a['unix_timestamp'] >= cutoff_time]
        
        if not recent_actions:
            return {
                'total_actions': 0,
                'unique_sessions': 0,
                'categories': {},
                'most_active_hour': None,
                'avg_actions_per_session': 0
            }
        
        categories = {}
        sessions = set()
        hours = {}
        
        for action in recent_actions:
            categories[action['action_category']] = categories.get(action['action_category'], 0) + 1
            sessions.add(action['session_id'])
            hours[action['hour_of_day']] = hours.get(action['hour_of_day'], 0) + 1
        
        most_active_hour = max(hours.items(), key=lambda x: x[1])[0] if hours else None
        
        return {
            'total_actions': len(recent_actions),
            'unique_sessions': len(sessions),
            'categories': categories,
            'most_active_hour': most_active_hour,
            'avg_actions_per_session': len(recent_actions) / len(sessions) if sessions else 0,
            'days_analyzed': days
        }


# Global instance
_logger = None

def get_activity_logger() -> UniversalActivityLogger:
    """Get global activity logger instance"""
    global _logger
    if _logger is None:
        _logger = UniversalActivityLogger()
    return _logger


# Convenience functions for common actions
def log_video_action(user_id: str, action: str, course_id: str, lecture_id: str, 
                     video_time: float = 0, duration: float = 0):
    """Log video-related action"""
    logger = get_activity_logger()
    return logger.log_action(
        user_id=user_id,
        user_role='student',
        action_type=action,
        context={'course_id': course_id, 'lecture_id': lecture_id},
        metadata={'video_time_seconds': video_time, 'duration_seconds': duration}
    )


def log_pdf_action(user_id: str, action: str, course_id: str, lecture_id: str,
                   material_id: str, page: int = 0, duration: float = 0):
    """Log PDF-related action"""
    logger = get_activity_logger()
    return logger.log_action(
        user_id=user_id,
        user_role='student',
        action_type=action,
        context={'course_id': course_id, 'lecture_id': lecture_id, 'resource_id': material_id},
        metadata={'page_number': page, 'duration_seconds': duration}
    )


def log_download(user_id: str, resource_type: str, course_id: str, lecture_id: str,
                 resource_id: str, file_size: int = 0):
    """Log download action"""
    logger = get_activity_logger()
    return logger.log_action(
        user_id=user_id,
        user_role='student',
        action_type=f'{resource_type}_download',
        context={'course_id': course_id, 'lecture_id': lecture_id, 'resource_id': resource_id},
        metadata={'file_size_bytes': file_size, 'downloaded': True}
    )


def log_assessment(user_id: str, action: str, course_id: str, lecture_id: str,
                   assessment_id: str, score: float = 0, duration: float = 0):
    """Log quiz/assignment action"""
    logger = get_activity_logger()
    return logger.log_action(
        user_id=user_id,
        user_role='student',
        action_type=action,
        context={'course_id': course_id, 'lecture_id': lecture_id, 'target_id': assessment_id},
        metadata={'score': score, 'duration_seconds': duration}
    )
