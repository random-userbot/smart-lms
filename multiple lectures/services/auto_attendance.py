"""
Automatic Attendance Tracking System
Tracks lecture attendance automatically based on lecture viewing behavior
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading


class AutomaticAttendanceTracker:
    """Automatically track student attendance based on lecture viewing"""
    
    def __init__(self, storage_path="./storage/attendance_auto.json"):
        """
        Initialize automatic attendance tracker
        
        Args:
            storage_path: Path to attendance storage file
        """
        self.storage_path = storage_path
        self.lock = threading.Lock()
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)
        self._initialize_storage()
        
        # Attendance criteria
        self.min_watch_percentage = 70  # Must watch 70% to mark attended
        self.min_watch_duration = 300   # Must watch at least 5 minutes
    
    def _initialize_storage(self):
        """Initialize storage file"""
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, 'w') as f:
                json.dump({'attendance_records': []}, f)
    
    def _load_attendance(self) -> Dict:
        """Load attendance records"""
        with self.lock:
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                return {'attendance_records': []}
    
    def _save_attendance(self, data: Dict):
        """Save attendance records"""
        with self.lock:
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
    
    def track_lecture_view(self, user_id: str, course_id: str, lecture_id: str,
                          watch_duration: int, lecture_duration: int,
                          session_id: str) -> Dict:
        """
        Track lecture viewing and determine attendance
        
        Args:
            user_id: Student ID
            course_id: Course ID
            lecture_id: Lecture ID
            watch_duration: Time watched in seconds
            lecture_duration: Total lecture duration in seconds
            session_id: Session ID
            
        Returns:
            Attendance record with status
        """
        # Calculate watch percentage
        watch_percentage = (watch_duration / lecture_duration * 100) if lecture_duration > 0 else 0
        
        # Determine attendance status
        attended = (
            watch_percentage >= self.min_watch_percentage and 
            watch_duration >= self.min_watch_duration
        )
        
        # Create attendance record
        attendance_record = {
            'user_id': user_id,
            'course_id': course_id,
            'lecture_id': lecture_id,
            'timestamp': datetime.now().isoformat(),
            'watch_duration': watch_duration,
            'lecture_duration': lecture_duration,
            'watch_percentage': round(watch_percentage, 2),
            'attended': attended,
            'attendance_status': 'Present' if attended else 'Absent',
            'session_id': session_id,
            'criteria': {
                'min_watch_percentage': self.min_watch_percentage,
                'min_watch_duration': self.min_watch_duration
            }
        }
        
        # Save to storage
        data = self._load_attendance()
        
        # Check if already exists (update instead of duplicate)
        existing_idx = None
        for idx, record in enumerate(data['attendance_records']):
            if (record['user_id'] == user_id and 
                record['lecture_id'] == lecture_id and
                record['session_id'] == session_id):
                existing_idx = idx
                break
        
        if existing_idx is not None:
            # Update existing record
            data['attendance_records'][existing_idx] = attendance_record
        else:
            # Add new record
            data['attendance_records'].append(attendance_record)
        
        self._save_attendance(data)
        
        return attendance_record
    
    def get_student_attendance(self, user_id: str, course_id: Optional[str] = None) -> Dict:
        """
        Get attendance summary for a student
        
        Args:
            user_id: Student ID
            course_id: Optional course ID to filter
            
        Returns:
            Attendance summary with statistics
        """
        data = self._load_attendance()
        records = data['attendance_records']
        
        # Filter by user and optionally course
        user_records = [r for r in records if r['user_id'] == user_id]
        if course_id:
            user_records = [r for r in user_records if r['course_id'] == course_id]
        
        if not user_records:
            return {
                'user_id': user_id,
                'course_id': course_id,
                'total_lectures': 0,
                'attended': 0,
                'absent': 0,
                'attendance_rate': 0,
                'average_watch_percentage': 0,
                'records': []
            }
        
        attended = len([r for r in user_records if r['attended']])
        absent = len(user_records) - attended
        attendance_rate = (attended / len(user_records) * 100) if user_records else 0
        avg_watch_pct = sum(r['watch_percentage'] for r in user_records) / len(user_records)
        
        return {
            'user_id': user_id,
            'course_id': course_id,
            'total_lectures': len(user_records),
            'attended': attended,
            'absent': absent,
            'attendance_rate': round(attendance_rate, 2),
            'average_watch_percentage': round(avg_watch_pct, 2),
            'records': sorted(user_records, key=lambda x: x['timestamp'], reverse=True)
        }
    
    def get_course_attendance(self, course_id: str) -> Dict:
        """
        Get attendance summary for entire course
        
        Args:
            course_id: Course ID
            
        Returns:
            Course-wide attendance statistics
        """
        data = self._load_attendance()
        records = [r for r in data['attendance_records'] if r['course_id'] == course_id]
        
        if not records:
            return {
                'course_id': course_id,
                'total_students': 0,
                'total_lectures_tracked': 0,
                'overall_attendance_rate': 0,
                'student_summaries': []
            }
        
        # Get unique students
        students = set(r['user_id'] for r in records)
        
        # Calculate per-student statistics
        student_summaries = []
        for student_id in students:
            student_data = self.get_student_attendance(student_id, course_id)
            student_summaries.append(student_data)
        
        # Calculate overall statistics
        total_possible = sum(s['total_lectures'] for s in student_summaries)
        total_attended = sum(s['attended'] for s in student_summaries)
        overall_rate = (total_attended / total_possible * 100) if total_possible > 0 else 0
        
        return {
            'course_id': course_id,
            'total_students': len(students),
            'total_lectures_tracked': len(set(r['lecture_id'] for r in records)),
            'overall_attendance_rate': round(overall_rate, 2),
            'total_possible_attendance': total_possible,
            'total_attended': total_attended,
            'student_summaries': sorted(
                student_summaries, 
                key=lambda x: x['attendance_rate'], 
                reverse=True
            )
        }
    
    def get_lecture_attendance(self, lecture_id: str) -> Dict:
        """
        Get attendance for a specific lecture
        
        Args:
            lecture_id: Lecture ID
            
        Returns:
            Lecture attendance details
        """
        data = self._load_attendance()
        records = [r for r in data['attendance_records'] if r['lecture_id'] == lecture_id]
        
        if not records:
            return {
                'lecture_id': lecture_id,
                'total_views': 0,
                'attended': 0,
                'absent': 0,
                'attendance_rate': 0,
                'records': []
            }
        
        attended = len([r for r in records if r['attended']])
        absent = len(records) - attended
        attendance_rate = (attended / len(records) * 100) if records else 0
        
        return {
            'lecture_id': lecture_id,
            'total_views': len(records),
            'attended': attended,
            'absent': absent,
            'attendance_rate': round(attendance_rate, 2),
            'average_watch_percentage': round(
                sum(r['watch_percentage'] for r in records) / len(records), 2
            ),
            'records': sorted(records, key=lambda x: x['timestamp'], reverse=True)
        }
    
    def generate_attendance_report(self, course_id: str, 
                                  start_date: Optional[str] = None,
                                  end_date: Optional[str] = None) -> Dict:
        """
        Generate comprehensive attendance report
        
        Args:
            course_id: Course ID
            start_date: Optional start date (ISO format)
            end_date: Optional end date (ISO format)
            
        Returns:
            Detailed attendance report
        """
        data = self._load_attendance()
        records = [r for r in data['attendance_records'] if r['course_id'] == course_id]
        
        # Apply date filters
        if start_date:
            records = [r for r in records if r['timestamp'] >= start_date]
        if end_date:
            records = [r for r in records if r['timestamp'] <= end_date]
        
        if not records:
            return {
                'course_id': course_id,
                'period': {'start': start_date, 'end': end_date},
                'message': 'No attendance data for specified period'
            }
        
        # Get unique lectures and students
        lectures = sorted(set(r['lecture_id'] for r in records))
        students = sorted(set(r['user_id'] for r in records))
        
        # Build attendance matrix
        attendance_matrix = []
        for student_id in students:
            student_row = {
                'student_id': student_id,
                'lectures': {}
            }
            
            for lecture_id in lectures:
                lecture_records = [r for r in records 
                                 if r['user_id'] == student_id and r['lecture_id'] == lecture_id]
                if lecture_records:
                    # Take most recent record
                    latest = max(lecture_records, key=lambda x: x['timestamp'])
                    student_row['lectures'][lecture_id] = {
                        'attended': latest['attended'],
                        'watch_percentage': latest['watch_percentage']
                    }
                else:
                    student_row['lectures'][lecture_id] = {
                        'attended': False,
                        'watch_percentage': 0
                    }
            
            # Calculate student attendance rate
            attended_count = sum(1 for l in student_row['lectures'].values() if l['attended'])
            student_row['attendance_rate'] = round(
                (attended_count / len(lectures) * 100) if lectures else 0, 2
            )
            
            attendance_matrix.append(student_row)
        
        # Calculate lecture-wise attendance
        lecture_stats = []
        for lecture_id in lectures:
            lecture_data = self.get_lecture_attendance(lecture_id)
            lecture_stats.append({
                'lecture_id': lecture_id,
                'attendance_rate': lecture_data['attendance_rate'],
                'attended': lecture_data['attended'],
                'total': lecture_data['total_views']
            })
        
        return {
            'course_id': course_id,
            'period': {
                'start': start_date or 'Beginning',
                'end': end_date or 'Present'
            },
            'summary': {
                'total_students': len(students),
                'total_lectures': len(lectures),
                'overall_attendance_rate': round(
                    sum(s['attendance_rate'] for s in attendance_matrix) / len(students)
                    if students else 0, 2
                )
            },
            'attendance_matrix': attendance_matrix,
            'lecture_statistics': lecture_stats,
            'generated_at': datetime.now().isoformat()
        }


# Singleton instance
_attendance_tracker_instance = None

def get_auto_attendance_tracker() -> AutomaticAttendanceTracker:
    """Get singleton instance of automatic attendance tracker"""
    global _attendance_tracker_instance
    if _attendance_tracker_instance is None:
        _attendance_tracker_instance = AutomaticAttendanceTracker()
    return _attendance_tracker_instance


# Integration helper for activity tracker
def integrate_with_activity_tracker():
    """
    Integration function to automatically track attendance when lectures are viewed
    This should be called from the lecture viewing page
    """
    def on_lecture_end(user_id: str, course_id: str, lecture_id: str,
                       watch_duration: int, lecture_duration: int, session_id: str):
        """
        Callback for when a lecture viewing session ends
        Automatically records attendance
        """
        tracker = get_auto_attendance_tracker()
        record = tracker.track_lecture_view(
            user_id=user_id,
            course_id=course_id,
            lecture_id=lecture_id,
            watch_duration=watch_duration,
            lecture_duration=lecture_duration,
            session_id=session_id
        )
        
        # Also track in activity tracker
        try:
            from services.activity_tracker import get_activity_tracker
            activity_tracker = get_activity_tracker()
            activity_tracker.track_attendance(
                user_id=user_id,
                course_id=course_id,
                lecture_id=lecture_id,
                status='present' if record['attended'] else 'absent',
                session_id=session_id,
                details={
                    'watch_duration': watch_duration,
                    'watch_percentage': record['watch_percentage'],
                    'automatic': True
                }
            )
        except Exception as e:
            print(f"⚠️  Could not track in activity tracker: {str(e)}")
        
        return record
    
    return on_lecture_end
