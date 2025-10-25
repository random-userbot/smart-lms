"""
Smart LMS - Storage Service
JSON-based storage with database migration readiness
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import yaml


class StorageService:
    """
    Abstracted storage interface for JSON files.
    Easy to swap with PostgreSQL/MySQL later.
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize storage service with configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.storage_paths = self.config['storage']
        self._ensure_storage_structure()
    
    def _ensure_storage_structure(self):
        """Create storage directories and initialize JSON files if they don't exist"""
        # Create directories
        Path(self.storage_paths['base_path']).mkdir(parents=True, exist_ok=True)
        Path(f"{self.storage_paths['base_path']}/courses").mkdir(parents=True, exist_ok=True)
        Path(f"{self.storage_paths['base_path']}/assignments").mkdir(parents=True, exist_ok=True)
        Path(f"{self.storage_paths['base_path']}/attendance").mkdir(parents=True, exist_ok=True)
        
        # Initialize JSON files with empty structures
        default_structures = {
            'users': {},
            'courses': {},
            'lectures': {},
            'engagement_logs': {},
            'feedback': {},
            'grades': {},
            'evaluation': {},
            'attendance': {},
            'teacher_activity': {},
            'progress': {},
            'enrollment_requests': {}
        }
        
        for key, default_value in default_structures.items():
            file_path = self.storage_paths[key]
            if not os.path.exists(file_path):
                self._write_json(file_path, default_value)
    
    def _read_json(self, file_path: str) -> Dict:
        """Read JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _write_json(self, file_path: str, data: Dict):
        """Write JSON file"""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    # ==================== USER MANAGEMENT ====================
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        users = self._read_json(self.storage_paths['users'])
        return users.get(user_id)
    
    def get_all_users(self, role: Optional[str] = None) -> Dict:
        """Get all users, optionally filtered by role"""
        users = self._read_json(self.storage_paths['users'])
        if role:
            return {uid: u for uid, u in users.items() if u.get('role') == role}
        return users
    
    def create_user(self, user_id: str, username: str, password_hash: str, 
                   role: str, email: Optional[str] = None, **kwargs) -> bool:
        """Create new user"""
        users = self._read_json(self.storage_paths['users'])
        
        if user_id in users:
            return False
        
        users[user_id] = {
            'user_id': user_id,
            'username': username,
            'password_hash': password_hash,
            'role': role,
            'email': email,
            'created_at': datetime.utcnow().isoformat(),
            'last_login': None,
            'is_active': True,
            **kwargs
        }
        
        self._write_json(self.storage_paths['users'], users)
        return True
    
    def update_user(self, user_id: str, updates: Dict) -> bool:
        """Update user information"""
        users = self._read_json(self.storage_paths['users'])
        
        if user_id not in users:
            return False
        
        users[user_id].update(updates)
        users[user_id]['updated_at'] = datetime.utcnow().isoformat()
        
        self._write_json(self.storage_paths['users'], users)
        return True
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user (GDPR compliance)"""
        users = self._read_json(self.storage_paths['users'])
        
        if user_id in users:
            del users[user_id]
            self._write_json(self.storage_paths['users'], users)
            return True
        return False
    
    # ==================== COURSE MANAGEMENT ====================
    
    def get_course(self, course_id: str) -> Optional[Dict]:
        """Get course by ID"""
        courses = self._read_json(self.storage_paths['courses'])
        return courses.get(course_id)
    
    def get_all_courses(self, teacher_id: Optional[str] = None) -> Dict:
        """Get all courses, optionally filtered by teacher"""
        courses = self._read_json(self.storage_paths['courses'])
        if teacher_id:
            return {cid: c for cid, c in courses.items() if c.get('teacher_id') == teacher_id}
        return courses
    
    def create_course(self, course_id: str, name: str, teacher_id: str, 
                     description: str = "", **kwargs) -> bool:
        """Create new course"""
        courses = self._read_json(self.storage_paths['courses'])
        
        if course_id in courses:
            return False
        
        courses[course_id] = {
            'course_id': course_id,
            'name': name,
            'teacher_id': teacher_id,
            'description': description,
            'lectures': [],
            'enrolled_students': [],
            'created_at': datetime.utcnow().isoformat(),
            'is_active': True,
            **kwargs
        }
        
        self._write_json(self.storage_paths['courses'], courses)
        return True
    
    def update_course(self, course_id: str, updates: Dict) -> bool:
        """Update course information"""
        courses = self._read_json(self.storage_paths['courses'])
        
        if course_id not in courses:
            return False
        
        courses[course_id].update(updates)
        courses[course_id]['updated_at'] = datetime.utcnow().isoformat()
        
        self._write_json(self.storage_paths['courses'], courses)
        return True
    
    def enroll_student(self, course_id: str, student_id: str) -> bool:
        """Enroll student in course"""
        courses = self._read_json(self.storage_paths['courses'])
        
        if course_id not in courses:
            return False
        
        if student_id not in courses[course_id]['enrolled_students']:
            courses[course_id]['enrolled_students'].append(student_id)
            self._write_json(self.storage_paths['courses'], courses)
        
        return True
    
    # ==================== LECTURE MANAGEMENT ====================
    
    def get_lecture(self, lecture_id: str) -> Optional[Dict]:
        """Get lecture by ID"""
        lectures = self._read_json(self.storage_paths['lectures'])
        return lectures.get(lecture_id)
    
    def get_course_lectures(self, course_id: str) -> List[Dict]:
        """Get all lectures for a course"""
        lectures = self._read_json(self.storage_paths['lectures'])
        return [l for l in lectures.values() if l.get('course_id') == course_id]
    
    def create_lecture(self, lecture_id: str, title: str, course_id: str,
                      video_path: str, duration: int = 0, **kwargs) -> bool:
        """Create new lecture"""
        lectures = self._read_json(self.storage_paths['lectures'])
        
        if lecture_id in lectures:
            return False
        
        lectures[lecture_id] = {
            'lecture_id': lecture_id,
            'title': title,
            'course_id': course_id,
            'video_path': video_path,
            'duration': duration,
            'materials': [],
            'created_at': datetime.utcnow().isoformat(),
            'is_active': True,
            **kwargs
        }
        
        self._write_json(self.storage_paths['lectures'], lectures)
        
        # Add lecture to course
        courses = self._read_json(self.storage_paths['courses'])
        if course_id in courses:
            if lecture_id not in courses[course_id]['lectures']:
                courses[course_id]['lectures'].append(lecture_id)
                self._write_json(self.storage_paths['courses'], courses)
        
        return True
    
    # ==================== ENGAGEMENT LOGS ====================
    
    def save_engagement_log(self, log_id: str, student_id: str, lecture_id: str,
                           session_start: str, events: List[Dict], 
                           engagement_score: float, **kwargs) -> bool:
        """Save engagement log for a lecture session"""
        logs = self._read_json(self.storage_paths['engagement_logs'])
        
        logs[log_id] = {
            'log_id': log_id,
            'student_id': student_id,
            'lecture_id': lecture_id,
            'session_start': session_start,
            'session_end': datetime.utcnow().isoformat(),
            'events': events,
            'engagement_score': engagement_score,
            'created_at': datetime.utcnow().isoformat(),
            **kwargs
        }
        
        self._write_json(self.storage_paths['engagement_logs'], logs)
        return True
    
    def get_engagement_logs(self, student_id: Optional[str] = None, 
                           lecture_id: Optional[str] = None) -> List[Dict]:
        """Get engagement logs filtered by student or lecture"""
        logs = self._read_json(self.storage_paths['engagement_logs'])
        
        filtered = logs.values()
        if student_id:
            filtered = [l for l in filtered if l.get('student_id') == student_id]
        if lecture_id:
            filtered = [l for l in filtered if l.get('lecture_id') == lecture_id]
        
        return list(filtered)
    
    # ==================== FEEDBACK ====================
    
    def save_feedback(self, feedback_id: str, student_id: str, lecture_id: str,
                     text: str, rating: int, sentiment: Optional[Dict] = None, 
                     **kwargs) -> bool:
        """Save student feedback for a lecture (legacy method)"""
        feedback_data = self._read_json(self.storage_paths['feedback'])
        
        feedback_data[feedback_id] = {
            'feedback_id': feedback_id,
            'student_id': student_id,
            'lecture_id': lecture_id,
            'text': text,
            'rating': rating,
            'sentiment': sentiment or {},
            'created_at': datetime.utcnow().isoformat(),
            **kwargs
        }
        
        self._write_json(self.storage_paths['feedback'], feedback_data)
        return True
    
    def save_detailed_feedback(self, feedback_id: str, student_id: str, lecture_id: str,
                              course_id: str, overall_rating: int, content_quality: int,
                              clarity_rating: int, pace_rating: int, engagement_rating: int,
                              visual_aids_rating: int, composite_score: float,
                              strengths: str, improvements: str, additional_comments: str,
                              difficulty_level: str, would_recommend: bool,
                              had_technical_issues: bool, technical_details: str,
                              sentiment: Dict, keywords: List[str], themes: List[str],
                              combined_text: str, **kwargs) -> bool:
        """Save comprehensive student feedback with NLP analysis"""
        feedback_data = self._read_json(self.storage_paths['feedback'])
        
        feedback_data[feedback_id] = {
            'feedback_id': feedback_id,
            'student_id': student_id,
            'lecture_id': lecture_id,
            'course_id': course_id,
            # Rating categories
            'ratings': {
                'overall': overall_rating,
                'content_quality': content_quality,
                'clarity': clarity_rating,
                'pace': pace_rating,
                'engagement': engagement_rating,
                'visual_aids': visual_aids_rating,
                'composite_score': composite_score
            },
            # Written feedback
            'written_feedback': {
                'strengths': strengths,
                'improvements': improvements,
                'additional_comments': additional_comments,
                'combined_text': combined_text
            },
            # Metadata
            'metadata': {
                'difficulty_level': difficulty_level,
                'would_recommend': would_recommend,
                'had_technical_issues': had_technical_issues,
                'technical_details': technical_details
            },
            # NLP Analysis
            'nlp_analysis': {
                'sentiment': sentiment,
                'keywords': keywords,
                'themes': themes
            },
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            **kwargs
        }
        
        self._write_json(self.storage_paths['feedback'], feedback_data)
        return True
    
    def get_feedback(self, lecture_id: Optional[str] = None, 
                    student_id: Optional[str] = None) -> List[Dict]:
        """Get feedback filtered by lecture or student"""
        feedback_data = self._read_json(self.storage_paths['feedback'])
        
        filtered = feedback_data.values()
        if lecture_id:
            filtered = [f for f in filtered if f.get('lecture_id') == lecture_id]
        if student_id:
            filtered = [f for f in filtered if f.get('student_id') == student_id]
        
        return list(filtered)
    
    def get_teacher_feedback(self, teacher_id: str) -> List[Dict]:
        """Get all feedback for a teacher's lectures"""
        feedback_data = self._read_json(self.storage_paths['feedback'])
        lectures_data = self._read_json(self.storage_paths['lectures'])
        courses_data = self._read_json(self.storage_paths['courses'])
        
        # Get teacher's courses
        teacher_courses = [cid for cid, c in courses_data.items() 
                          if c.get('teacher_id') == teacher_id]
        
        # Get teacher's lectures
        teacher_lectures = [lid for lid, l in lectures_data.items() 
                           if l.get('course_id') in teacher_courses]
        
        # Filter feedback for teacher's lectures
        teacher_feedback = [f for f in feedback_data.values() 
                           if f.get('lecture_id') in teacher_lectures]
        
        return teacher_feedback
    
    def update_teacher_evaluation(self, teacher_id: str, lecture_id: str, 
                                  course_id: str, feedback_id: str,
                                  ratings: Dict, sentiment: Dict) -> bool:
        """Update teacher evaluation metrics"""
        evaluation_data = self._read_json(self.storage_paths['evaluation'])
        
        if teacher_id not in evaluation_data:
            evaluation_data[teacher_id] = {
                'teacher_id': teacher_id,
                'total_feedback_count': 0,
                'average_ratings': {
                    'overall': 0.0,
                    'content_quality': 0.0,
                    'clarity': 0.0,
                    'pace': 0.0,
                    'engagement': 0.0,
                    'visual_aids': 0.0,
                    'composite': 0.0
                },
                'sentiment_distribution': {
                    'positive': 0,
                    'neutral': 0,
                    'negative': 0
                },
                'feedback_by_course': {},
                'feedback_by_lecture': {},
                'last_updated': datetime.utcnow().isoformat()
            }
        
        teacher_eval = evaluation_data[teacher_id]
        
        # Update feedback count
        teacher_eval['total_feedback_count'] += 1
        count = teacher_eval['total_feedback_count']
        
        # Update average ratings (running average)
        for key, value in ratings.items():
            current_avg = teacher_eval['average_ratings'].get(key, 0.0)
            teacher_eval['average_ratings'][key] = ((current_avg * (count - 1)) + value) / count
        
        # Update sentiment distribution
        sentiment_label = sentiment.get('label', 'neutral')
        teacher_eval['sentiment_distribution'][sentiment_label] = \
            teacher_eval['sentiment_distribution'].get(sentiment_label, 0) + 1
        
        # Track by course
        if course_id not in teacher_eval['feedback_by_course']:
            teacher_eval['feedback_by_course'][course_id] = {
                'count': 0,
                'avg_composite': 0.0,
                'feedback_ids': []
            }
        course_eval = teacher_eval['feedback_by_course'][course_id]
        course_eval['count'] += 1
        course_eval['feedback_ids'].append(feedback_id)
        course_eval['avg_composite'] = ((course_eval['avg_composite'] * (course_eval['count'] - 1)) + 
                                        ratings['composite']) / course_eval['count']
        
        # Track by lecture
        if lecture_id not in teacher_eval['feedback_by_lecture']:
            teacher_eval['feedback_by_lecture'][lecture_id] = {
                'count': 0,
                'avg_composite': 0.0,
                'feedback_ids': []
            }
        lecture_eval = teacher_eval['feedback_by_lecture'][lecture_id]
        lecture_eval['count'] += 1
        lecture_eval['feedback_ids'].append(feedback_id)
        lecture_eval['avg_composite'] = ((lecture_eval['avg_composite'] * (lecture_eval['count'] - 1)) + 
                                         ratings['composite']) / lecture_eval['count']
        
        teacher_eval['last_updated'] = datetime.utcnow().isoformat()
        
        self._write_json(self.storage_paths['evaluation'], evaluation_data)
        return True
    
    def get_teacher_evaluation(self, teacher_id: str) -> Optional[Dict]:
        """Get teacher evaluation metrics"""
        evaluation_data = self._read_json(self.storage_paths['evaluation'])
        return evaluation_data.get(teacher_id)

    
    # ==================== GRADES ====================
    
    def save_grade(self, student_id: str, course_id: str, 
                  assessment_type: str, assessment_id: str,
                  score: float, max_score: float, **kwargs) -> bool:
        """Save quiz or assignment grade"""
        grades = self._read_json(self.storage_paths['grades'])
        
        if student_id not in grades:
            grades[student_id] = {'quizzes': [], 'assignments': []}
        
        grade_entry = {
            'course_id': course_id,
            'assessment_id': assessment_id,
            'score': score,
            'max_score': max_score,
            'percentage': (score / max_score * 100) if max_score > 0 else 0,
            'timestamp': datetime.utcnow().isoformat(),
            **kwargs
        }
        
        if assessment_type == 'quiz':
            grades[student_id]['quizzes'].append(grade_entry)
        elif assessment_type == 'assignment':
            grades[student_id]['assignments'].append(grade_entry)
        
        self._write_json(self.storage_paths['grades'], grades)
        return True
    
    def get_student_grades(self, student_id: str) -> Dict:
        """Get all grades for a student"""
        grades = self._read_json(self.storage_paths['grades'])
        return grades.get(student_id, {'quizzes': [], 'assignments': []})
    
    # ==================== TEACHER EVALUATION ====================
    
    def save_evaluation(self, teacher_id: str, score: float, features: Dict,
                       shap_values: Optional[Dict] = None, **kwargs) -> bool:
        """Save teacher evaluation results"""
        evaluations = self._read_json(self.storage_paths['evaluation'])
        
        evaluations[teacher_id] = {
            'teacher_id': teacher_id,
            'score': score,
            'features': features,
            'shap_values': shap_values or {},
            'evaluated_at': datetime.utcnow().isoformat(),
            **kwargs
        }
        
        self._write_json(self.storage_paths['evaluation'], evaluations)
        return True
    
    def get_evaluation(self, teacher_id: str) -> Optional[Dict]:
        """Get teacher evaluation"""
        evaluations = self._read_json(self.storage_paths['evaluation'])
        return evaluations.get(teacher_id)
    
    def get_all_evaluations(self) -> Dict:
        """Get all teacher evaluations"""
        return self._read_json(self.storage_paths['evaluation'])
    
    # ==================== ATTENDANCE ====================
    
    def save_attendance(self, attendance_id: str, student_id: str, lecture_id: str,
                       presence_percentage: float, detection_logs: List[Dict],
                       **kwargs) -> bool:
        """Save attendance record"""
        attendance = self._read_json(self.storage_paths['attendance'])
        
        attendance[attendance_id] = {
            'attendance_id': attendance_id,
            'student_id': student_id,
            'lecture_id': lecture_id,
            'presence_percentage': presence_percentage,
            'status': 'present' if presence_percentage >= 75 else 'absent',
            'detection_logs': detection_logs,
            'recorded_at': datetime.utcnow().isoformat(),
            **kwargs
        }
        
        self._write_json(self.storage_paths['attendance'], attendance)
        return True
    
    def get_attendance(self, student_id: Optional[str] = None,
                      lecture_id: Optional[str] = None) -> List[Dict]:
        """Get attendance records"""
        attendance = self._read_json(self.storage_paths['attendance'])
        
        filtered = attendance.values()
        if student_id:
            filtered = [a for a in filtered if a.get('student_id') == student_id]
        if lecture_id:
            filtered = [a for a in filtered if a.get('lecture_id') == lecture_id]
        
        return list(filtered)
    
    # ==================== TEACHER ACTIVITY ====================
    
    def log_teacher_activity(self, activity_id: str, teacher_id: str,
                            action: str, details: Dict, **kwargs) -> bool:
        """Log teacher activity"""
        activities = self._read_json(self.storage_paths['teacher_activity'])
        
        if teacher_id not in activities:
            activities[teacher_id] = []
        
        activities[teacher_id].append({
            'activity_id': activity_id,
            'action': action,
            'details': details,
            'timestamp': datetime.utcnow().isoformat(),
            **kwargs
        })
        
        self._write_json(self.storage_paths['teacher_activity'], activities)
        return True
    
    def get_teacher_activity(self, teacher_id: str, 
                            days: Optional[int] = None) -> List[Dict]:
        """Get teacher activity logs"""
        activities = self._read_json(self.storage_paths['teacher_activity'])
        teacher_logs = activities.get(teacher_id, [])
        
        if days:
            # Filter by date range (implement if needed)
            pass
        
        return teacher_logs
    
    # ==================== PROGRESS TRACKING ====================
    
    def save_progress(self, student_id: str, course_id: str,
                     completed_lectures: List[str], quiz_scores: List[float],
                     engagement_trend: List[float], **kwargs) -> bool:
        """Save student progress"""
        progress = self._read_json(self.storage_paths['progress'])
        
        if student_id not in progress:
            progress[student_id] = {}
        
        progress[student_id][course_id] = {
            'completed_lectures': completed_lectures,
            'quiz_scores': quiz_scores,
            'engagement_trend': engagement_trend,
            'completion_percentage': len(completed_lectures) / kwargs.get('total_lectures', 1) * 100,
            'updated_at': datetime.utcnow().isoformat(),
            **kwargs
        }
        
        self._write_json(self.storage_paths['progress'], progress)
        return True
    
    def get_progress(self, student_id: str, course_id: Optional[str] = None) -> Dict:
        """Get student progress"""
        progress = self._read_json(self.storage_paths['progress'])
        student_progress = progress.get(student_id, {})
        
        if course_id:
            return student_progress.get(course_id, {})
        return student_progress
    
    # Enrollment Request Methods
    def create_enrollment_request(self, request_id: str, student_id: str, course_id: str, **kwargs) -> bool:
        """Create an enrollment request"""
        requests = self._read_json(self.storage_paths.get('enrollment_requests', './storage/enrollment_requests.json'))
        
        requests[request_id] = {
            'request_id': request_id,
            'student_id': student_id,
            'course_id': course_id,
            'status': 'pending',  # pending, approved, rejected
            'requested_at': datetime.utcnow().isoformat(),
            'processed_at': None,
            'processed_by': None,
            **kwargs
        }
        
        self._write_json(self.storage_paths.get('enrollment_requests', './storage/enrollment_requests.json'), requests)
        return True
    
    def get_enrollment_requests(self, course_id: Optional[str] = None, student_id: Optional[str] = None, 
                                status: Optional[str] = None) -> Dict:
        """Get enrollment requests with optional filters"""
        requests = self._read_json(self.storage_paths.get('enrollment_requests', './storage/enrollment_requests.json'))
        
        filtered_requests = requests
        
        if course_id:
            filtered_requests = {rid: r for rid, r in filtered_requests.items() if r.get('course_id') == course_id}
        
        if student_id:
            filtered_requests = {rid: r for rid, r in filtered_requests.items() if r.get('student_id') == student_id}
        
        if status:
            filtered_requests = {rid: r for rid, r in filtered_requests.items() if r.get('status') == status}
        
        return filtered_requests
    
    def update_enrollment_request(self, request_id: str, status: str, processed_by: str) -> bool:
        """Update enrollment request status"""
        requests = self._read_json(self.storage_paths.get('enrollment_requests', './storage/enrollment_requests.json'))
        
        if request_id not in requests:
            return False
        
        requests[request_id]['status'] = status
        requests[request_id]['processed_at'] = datetime.utcnow().isoformat()
        requests[request_id]['processed_by'] = processed_by
        
        # If approved, add student to course
        if status == 'approved':
            course_id = requests[request_id]['course_id']
            student_id = requests[request_id]['student_id']
            
            courses = self._read_json(self.storage_paths['courses'])
            if course_id in courses:
                enrolled_students = courses[course_id].get('enrolled_students', [])
                if student_id not in enrolled_students:
                    enrolled_students.append(student_id)
                    courses[course_id]['enrolled_students'] = enrolled_students
                    courses[course_id]['updated_at'] = datetime.utcnow().isoformat()
                    self._write_json(self.storage_paths['courses'], courses)
        
        self._write_json(self.storage_paths.get('enrollment_requests', './storage/enrollment_requests.json'), requests)
        return True


# Singleton instance
_storage_instance = None

def get_storage() -> StorageService:
    """Get storage service singleton"""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = StorageService()
    return _storage_instance
