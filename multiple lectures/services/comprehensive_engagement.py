"""
Comprehensive Engagement Score Calculator
Combines all user actions: video watching, PDF reading, quiz attempts, assignment submissions
"""

import os
import csv
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import json


class ComprehensiveEngagementCalculator:
    """Calculate final engagement score from all user activities"""
    
    def __init__(self, storage_dir: str = "./storage", ml_data_dir: str = "./ml_data"):
        self.storage_dir = storage_dir
        self.ml_data_dir = ml_data_dir
    
    def get_video_engagement(self, student_id: str, lecture_id: str) -> Dict:
        """Get video watching engagement from engagement logs"""
        engagement_file = os.path.join(self.storage_dir, "engagement_logs.json")
        
        if not os.path.exists(engagement_file):
            return {'avg_score': 0, 'total_time': 0, 'sessions': 0}
        
        try:
            with open(engagement_file, 'r') as f:
                data = json.load(f)
            
            logs = data.get('logs', [])
            student_logs = [
                log for log in logs 
                if log.get('user_id') == student_id and log.get('lecture_id') == lecture_id
            ]
            
            if not student_logs:
                return {'avg_score': 0, 'total_time': 0, 'sessions': 0}
            
            total_score = sum(log.get('engagement_score', 0) for log in student_logs)
            avg_score = total_score / len(student_logs)
            
            # Calculate total watch time
            total_time = 0
            for log in student_logs:
                if 'watch_time_seconds' in log:
                    total_time += log['watch_time_seconds']
            
            return {
                'avg_score': avg_score,
                'total_time': total_time,
                'sessions': len(student_logs)
            }
        except Exception as e:
            print(f"Error reading video engagement: {e}")
            return {'avg_score': 0, 'total_time': 0, 'sessions': 0}
    
    def get_pdf_reading_time(self, student_id: str, lecture_id: str) -> Dict:
        """Get PDF reading time from reading logs"""
        reading_logs_dir = os.path.join(self.ml_data_dir, "reading_logs")
        
        if not os.path.exists(reading_logs_dir):
            return {'total_time': 0, 'num_materials': 0, 'sessions': 0}
        
        # Find all reading log files for this student
        total_seconds = 0
        materials_read = set()
        total_sessions = 0
        
        for log_file in os.listdir(reading_logs_dir):
            if log_file.startswith(f"pdf_reading_log_{student_id}"):
                log_path = os.path.join(reading_logs_dir, log_file)
                
                try:
                    with open(log_path, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            if row.get('lecture_id') == lecture_id:
                                total_seconds += int(row.get('reading_duration_seconds', 0))
                                materials_read.add(row.get('material_id'))
                                total_sessions += 1
                except Exception as e:
                    print(f"Error reading PDF log {log_file}: {e}")
        
        return {
            'total_time': total_seconds,
            'num_materials': len(materials_read),
            'sessions': total_sessions
        }
    
    def get_quiz_performance(self, student_id: str, lecture_id: str) -> Dict:
        """Get quiz performance for this lecture"""
        grades_file = os.path.join(self.storage_dir, "grades.json")
        
        if not os.path.exists(grades_file):
            return {'avg_score': 0, 'completed': 0, 'attempts': 0}
        
        try:
            with open(grades_file, 'r') as f:
                grades_data = json.load(f)
            
            student_grades = grades_data.get(student_id, {})
            quiz_scores = []
            attempts = 0
            
            for item_id, grade_info in student_grades.items():
                if (grade_info.get('type') == 'quiz' and 
                    grade_info.get('lecture_id') == lecture_id):
                    quiz_scores.append(grade_info.get('score', 0))
                    attempts += 1
            
            return {
                'avg_score': sum(quiz_scores) / len(quiz_scores) if quiz_scores else 0,
                'completed': len(quiz_scores),
                'attempts': attempts
            }
        except Exception as e:
            print(f"Error reading quiz performance: {e}")
            return {'avg_score': 0, 'completed': 0, 'attempts': 0}
    
    def get_assignment_completion(self, student_id: str, lecture_id: str) -> Dict:
        """Get assignment completion status"""
        assignments_file = os.path.join(self.storage_dir, "assignments.json")
        
        if not os.path.exists(assignments_file):
            return {'submitted': 0, 'on_time': 0, 'total': 0}
        
        try:
            with open(assignments_file, 'r') as f:
                assignments_data = json.load(f)
            
            assignments = assignments_data.get('assignments', [])
            lecture_assignments = [
                a for a in assignments 
                if a.get('lecture_id') == lecture_id
            ]
            
            submitted = 0
            on_time = 0
            
            for assignment in lecture_assignments:
                submissions = assignment.get('submissions', [])
                student_submission = next(
                    (s for s in submissions if s.get('student_id') == student_id),
                    None
                )
                
                if student_submission:
                    submitted += 1
                    if student_submission.get('on_time', False):
                        on_time += 1
            
            return {
                'submitted': submitted,
                'on_time': on_time,
                'total': len(lecture_assignments)
            }
        except Exception as e:
            print(f"Error reading assignment completion: {e}")
            return {'submitted': 0, 'on_time': 0, 'total': 0}
    
    def get_behavioral_data(self, student_id: str, lecture_id: str) -> Dict:
        """Get behavioral tracking data (mouse clicks, scrolls, etc.)"""
        behavioral_logs_dir = os.path.join(self.ml_data_dir, "behavioral_logs")
        
        if not os.path.exists(behavioral_logs_dir):
            return {
                'active_time': 0,
                'interactions': 0,
                'tab_switches': 0,
                'focus_lost_count': 0
            }
        
        # Find behavioral log for this student and lecture
        log_pattern = f"behavioral_log_{student_id}_{lecture_id}_*.csv"
        
        active_seconds = 0
        total_interactions = 0
        tab_switches = 0
        focus_lost = 0
        
        for log_file in Path(behavioral_logs_dir).glob(log_pattern):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        event_type = row.get('event_type', '')
                        
                        if event_type in ['mouse_click', 'scroll', 'keypress']:
                            total_interactions += 1
                        elif event_type == 'tab_switch':
                            tab_switches += 1
                        elif event_type == 'focus_lost':
                            focus_lost += 1
                        
                        # Calculate active time (time between interactions)
                        if 'duration_seconds' in row:
                            active_seconds += float(row.get('duration_seconds', 0))
            except Exception as e:
                print(f"Error reading behavioral log {log_file}: {e}")
        
        return {
            'active_time': active_seconds,
            'interactions': total_interactions,
            'tab_switches': tab_switches,
            'focus_lost_count': focus_lost
        }
    
    def calculate_comprehensive_score(self, student_id: str, lecture_id: str) -> Dict:
        """
        Calculate comprehensive engagement score from all activities
        
        Args:
            student_id: Student's user ID
            lecture_id: Lecture identifier
        
        Returns:
            Dict with detailed breakdown and final score
        """
        # Gather all data
        video_data = self.get_video_engagement(student_id, lecture_id)
        pdf_data = self.get_pdf_reading_time(student_id, lecture_id)
        quiz_data = self.get_quiz_performance(student_id, lecture_id)
        assignment_data = self.get_assignment_completion(student_id, lecture_id)
        behavioral_data = self.get_behavioral_data(student_id, lecture_id)
        
        # Calculate component scores (0-100 scale)
        
        # 1. Video Engagement (40% weight)
        video_score = video_data['avg_score']  # Already 0-100
        
        # 2. PDF Reading Score (20% weight)
        # Score based on time spent and materials read
        pdf_minutes = pdf_data['total_time'] / 60
        pdf_score = min(100, (pdf_minutes / 30) * 100)  # 30 min = 100%
        if pdf_data['num_materials'] > 0:
            pdf_score = pdf_score * 0.7 + (pdf_data['num_materials'] * 20)  # Bonus for multiple materials
        pdf_score = min(100, pdf_score)
        
        # 3. Quiz Performance (20% weight)
        quiz_score = quiz_data['avg_score']  # Already 0-100
        
        # 4. Assignment Completion (10% weight)
        if assignment_data['total'] > 0:
            assignment_score = (assignment_data['submitted'] / assignment_data['total']) * 100
            # Bonus for on-time submission
            if assignment_data['on_time'] > 0:
                on_time_bonus = (assignment_data['on_time'] / assignment_data['total']) * 20
                assignment_score = min(100, assignment_score + on_time_bonus)
        else:
            assignment_score = 100  # No penalty if no assignments
        
        # 5. Active Participation (10% weight)
        # Based on interactions and focus
        if behavioral_data['interactions'] > 0:
            participation_score = min(100, (behavioral_data['interactions'] / 50) * 100)
            # Penalty for excessive tab switching
            if behavioral_data['tab_switches'] > 5:
                penalty = min(50, (behavioral_data['tab_switches'] - 5) * 5)
                participation_score = max(0, participation_score - penalty)
        else:
            participation_score = 50  # Neutral score if no data
        
        # Calculate weighted final score
        final_score = (
            video_score * 0.40 +
            pdf_score * 0.20 +
            quiz_score * 0.20 +
            assignment_score * 0.10 +
            participation_score * 0.10
        )
        
        # Round to 2 decimal places
        final_score = round(final_score, 2)
        
        # Determine engagement level
        if final_score >= 80:
            level = "Excellent"
            emoji = "🌟"
        elif final_score >= 60:
            level = "Good"
            emoji = "👍"
        elif final_score >= 40:
            level = "Average"
            emoji = "📊"
        else:
            level = "Needs Improvement"
            emoji = "📈"
        
        return {
            'final_score': final_score,
            'level': level,
            'emoji': emoji,
            'breakdown': {
                'video_engagement': {
                    'score': round(video_score, 2),
                    'weight': '40%',
                    'avg_engagement': video_data['avg_score'],
                    'watch_time_minutes': round(video_data['total_time'] / 60, 1),
                    'sessions': video_data['sessions']
                },
                'pdf_reading': {
                    'score': round(pdf_score, 2),
                    'weight': '20%',
                    'reading_time_minutes': round(pdf_data['total_time'] / 60, 1),
                    'materials_read': pdf_data['num_materials'],
                    'sessions': pdf_data['sessions']
                },
                'quiz_performance': {
                    'score': round(quiz_score, 2),
                    'weight': '20%',
                    'avg_quiz_score': quiz_data['avg_score'],
                    'completed': quiz_data['completed'],
                    'attempts': quiz_data['attempts']
                },
                'assignment_completion': {
                    'score': round(assignment_score, 2),
                    'weight': '10%',
                    'submitted': assignment_data['submitted'],
                    'on_time': assignment_data['on_time'],
                    'total': assignment_data['total']
                },
                'active_participation': {
                    'score': round(participation_score, 2),
                    'weight': '10%',
                    'interactions': behavioral_data['interactions'],
                    'tab_switches': behavioral_data['tab_switches'],
                    'focus_lost': behavioral_data['focus_lost_count']
                }
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def get_student_overall_engagement(self, student_id: str, course_id: Optional[str] = None) -> Dict:
        """Get overall engagement across all lectures or specific course"""
        # This would aggregate scores across all lectures
        # Implementation depends on your data structure
        pass


# Global instance
_calculator = None

def get_engagement_calculator() -> ComprehensiveEngagementCalculator:
    """Get global engagement calculator instance"""
    global _calculator
    if _calculator is None:
        _calculator = ComprehensiveEngagementCalculator()
    return _calculator
