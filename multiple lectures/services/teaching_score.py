"""
Explainable AI Teaching Score Calculator
Computes data-driven teaching scores with explainable factors
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import math


class TeachingScoreCalculator:
    """Calculate teaching scores with explainable AI techniques"""
    
    def __init__(self, storage_path="./storage/teaching_scores.json"):
        """
        Initialize teaching score calculator
        
        Args:
            storage_path: Path to teaching scores storage
        """
        self.storage_path = storage_path
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)
        self._initialize_storage()
        
        # Weight configuration for score components
        self.weights = {
            'engagement': 0.25,           # Student engagement levels
            'quiz_performance': 0.20,     # Quiz scores and completion rates
            'attendance': 0.15,           # Student attendance
            'lecture_completion': 0.15,   # Lecture completion rates
            'sentiment': 0.10,            # NLP sentiment from feedback
            'resource_usage': 0.05,       # Material downloads and usage
            'activity_patterns': 0.10     # Overall activity patterns
        }
    
    def _initialize_storage(self):
        """Initialize storage file"""
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, 'w') as f:
                json.dump({'scores': []}, f)
    
    def _load_scores(self) -> Dict:
        """Load scores from storage"""
        try:
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {'scores': []}
    
    def _save_scores(self, data: Dict):
        """Save scores to storage"""
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def calculate_engagement_score(self, activities: List[Dict], 
                                   course_students: List[str]) -> Tuple[float, Dict]:
        """
        Calculate engagement score from activity data
        
        Returns:
            Tuple of (score, explanation_dict)
        """
        if not course_students:
            return 0.0, {'reason': 'No students enrolled'}
        
        engagement_events = [
            a for a in activities 
            if a['event_type'] in ['lecture_start', 'lecture_end', 'quiz_start', 
                                   'material_download', 'notes_reading']
        ]
        
        # Calculate average engagement per student
        student_engagement = defaultdict(int)
        for activity in engagement_events:
            student_engagement[activity['user_id']] += 1
        
        if not student_engagement:
            return 0.0, {'reason': 'No engagement activities found'}
        
        avg_engagement = sum(student_engagement.values()) / len(course_students)
        
        # Normalize to 0-100 scale (assuming 50+ activities is excellent)
        score = min(100, (avg_engagement / 50) * 100)
        
        explanation = {
            'total_engagement_events': len(engagement_events),
            'active_students': len(student_engagement),
            'total_students': len(course_students),
            'avg_activities_per_student': round(avg_engagement, 2),
            'participation_rate': round(len(student_engagement) / len(course_students) * 100, 2)
        }
        
        return score, explanation
    
    def calculate_quiz_performance_score(self, grades: List[Dict]) -> Tuple[float, Dict]:
        """
        Calculate quiz performance score
        
        Returns:
            Tuple of (score, explanation_dict)
        """
        if not grades:
            return 0.0, {'reason': 'No quiz grades available'}
        
        # Extract quiz scores
        quiz_grades = [g for g in grades if g.get('assessment_type') == 'quiz']
        
        if not quiz_grades:
            return 0.0, {'reason': 'No quiz submissions'}
        
        scores = [g['score'] for g in quiz_grades if 'score' in g]
        
        if not scores:
            return 0.0, {'reason': 'No quiz scores recorded'}
        
        avg_score = sum(scores) / len(scores)
        
        # Calculate pass rate (assuming 60% is passing)
        pass_count = sum(1 for s in scores if s >= 60)
        pass_rate = pass_count / len(scores) * 100
        
        # Score considers both average and pass rate
        score = (avg_score * 0.7) + (pass_rate * 0.3)
        
        explanation = {
            'total_quiz_attempts': len(quiz_grades),
            'average_score': round(avg_score, 2),
            'pass_rate': round(pass_rate, 2),
            'highest_score': round(max(scores), 2),
            'lowest_score': round(min(scores), 2)
        }
        
        return score, explanation
    
    def calculate_attendance_score(self, attendance_records: List[Dict],
                                   course_students: List[str]) -> Tuple[float, Dict]:
        """
        Calculate attendance score
        
        Returns:
            Tuple of (score, explanation_dict)
        """
        if not course_students:
            return 0.0, {'reason': 'No students enrolled'}
        
        if not attendance_records:
            return 0.0, {'reason': 'No attendance records'}
        
        # Calculate attendance rate per student
        student_attendance = defaultdict(lambda: {'present': 0, 'total': 0})
        
        for record in attendance_records:
            student_id = record.get('student_id') or record.get('user_id')
            if student_id in course_students:
                student_attendance[student_id]['total'] += 1
                if record.get('status') == 'present':
                    student_attendance[student_id]['present'] += 1
        
        if not student_attendance:
            return 0.0, {'reason': 'No attendance data for enrolled students'}
        
        # Calculate average attendance rate
        attendance_rates = [
            (data['present'] / data['total']) * 100 
            for data in student_attendance.values() 
            if data['total'] > 0
        ]
        
        avg_attendance = sum(attendance_rates) / len(attendance_rates) if attendance_rates else 0
        
        explanation = {
            'students_with_records': len(student_attendance),
            'average_attendance_rate': round(avg_attendance, 2),
            'total_attendance_records': len(attendance_records)
        }
        
        return avg_attendance, explanation
    
    def calculate_lecture_completion_score(self, activities: List[Dict],
                                          total_lectures: int) -> Tuple[float, Dict]:
        """
        Calculate lecture completion rate score
        
        Returns:
            Tuple of (score, explanation_dict)
        """
        if total_lectures == 0:
            return 0.0, {'reason': 'No lectures available'}
        
        lecture_completions = [
            a for a in activities 
            if a['event_type'] == 'lecture_end'
        ]
        
        if not lecture_completions:
            return 0.0, {'reason': 'No completed lectures'}
        
        # Count unique students who completed lectures
        students_completed = len(set(a['user_id'] for a in lecture_completions))
        
        # Calculate completion rate (lectures completed / total lectures)
        completion_count = len(lecture_completions)
        expected_completions = total_lectures * students_completed
        
        if expected_completions == 0:
            return 0.0, {'reason': 'No expected completions'}
        
        completion_rate = (completion_count / expected_completions) * 100
        score = min(100, completion_rate)  # Cap at 100
        
        explanation = {
            'total_lectures': total_lectures,
            'lecture_completions': completion_count,
            'students_completing_lectures': students_completed,
            'completion_rate': round(completion_rate, 2)
        }
        
        return score, explanation
    
    def calculate_sentiment_score(self, feedback_analysis: Dict) -> Tuple[float, Dict]:
        """
        Calculate sentiment score from NLP analysis
        
        Returns:
            Tuple of (score, explanation_dict)
        """
        if not feedback_analysis:
            return 50.0, {'reason': 'No feedback analysis available', 'note': 'Neutral score'}
        
        # Extract sentiment metrics
        positive_count = feedback_analysis.get('positive', 0)
        negative_count = feedback_analysis.get('negative', 0)
        neutral_count = feedback_analysis.get('neutral', 0)
        
        total = positive_count + negative_count + neutral_count
        
        if total == 0:
            return 50.0, {'reason': 'No feedback entries', 'note': 'Neutral score'}
        
        # Calculate sentiment score
        # Positive: 100, Neutral: 50, Negative: 0
        score = ((positive_count * 100) + (neutral_count * 50)) / total
        
        explanation = {
            'total_feedback': total,
            'positive_count': positive_count,
            'neutral_count': neutral_count,
            'negative_count': negative_count,
            'positive_ratio': round(positive_count / total * 100, 2),
            'negative_ratio': round(negative_count / total * 100, 2)
        }
        
        return score, explanation
    
    def calculate_resource_usage_score(self, activities: List[Dict],
                                      total_materials: int) -> Tuple[float, Dict]:
        """
        Calculate resource usage score
        
        Returns:
            Tuple of (score, explanation_dict)
        """
        if total_materials == 0:
            return 50.0, {'reason': 'No materials available', 'note': 'Neutral score'}
        
        download_events = [
            a for a in activities 
            if a['event_type'] == 'material_download'
        ]
        
        if not download_events:
            return 0.0, {'reason': 'No material downloads'}
        
        # Calculate download rate
        unique_students = len(set(a['user_id'] for a in download_events))
        downloads_per_student = len(download_events) / unique_students if unique_students > 0 else 0
        
        # Normalize (5+ downloads per student is excellent)
        score = min(100, (downloads_per_student / 5) * 100)
        
        explanation = {
            'total_downloads': len(download_events),
            'unique_students_downloading': unique_students,
            'avg_downloads_per_student': round(downloads_per_student, 2),
            'total_materials_available': total_materials
        }
        
        return score, explanation
    
    def calculate_activity_patterns_score(self, activities: List[Dict],
                                         course_duration_days: int) -> Tuple[float, Dict]:
        """
        Calculate activity patterns score (consistency, frequency)
        
        Returns:
            Tuple of (score, explanation_dict)
        """
        if not activities:
            return 0.0, {'reason': 'No activities recorded'}
        
        if course_duration_days <= 0:
            course_duration_days = 30  # Default to 30 days
        
        # Group activities by date
        activity_dates = defaultdict(int)
        for activity in activities:
            timestamp = activity.get('timestamp', '')
            if timestamp:
                date = timestamp.split('T')[0]
                activity_dates[date] += 1
        
        # Calculate active days
        active_days = len(activity_dates)
        activity_frequency = active_days / course_duration_days * 100
        
        # Calculate consistency (standard deviation of daily activities)
        daily_counts = list(activity_dates.values())
        avg_daily = sum(daily_counts) / len(daily_counts) if daily_counts else 0
        variance = sum((x - avg_daily) ** 2 for x in daily_counts) / len(daily_counts) if daily_counts else 0
        std_dev = math.sqrt(variance)
        
        # Lower std_dev means more consistent
        consistency_score = max(0, 100 - (std_dev / avg_daily * 100 if avg_daily > 0 else 100))
        
        # Combine frequency and consistency
        score = (activity_frequency * 0.6) + (consistency_score * 0.4)
        score = min(100, score)
        
        explanation = {
            'total_activities': len(activities),
            'active_days': active_days,
            'course_duration_days': course_duration_days,
            'activity_frequency': round(activity_frequency, 2),
            'avg_activities_per_active_day': round(avg_daily, 2),
            'consistency_score': round(consistency_score, 2)
        }
        
        return score, explanation
    
    def calculate_overall_teaching_score(self, 
                                        activities: List[Dict],
                                        grades: List[Dict],
                                        attendance_records: List[Dict],
                                        feedback_analysis: Dict,
                                        course_students: List[str],
                                        total_lectures: int,
                                        total_materials: int,
                                        course_duration_days: int = 30) -> Dict:
        """
        Calculate overall teaching score with explainable components
        
        Returns:
            Dictionary with overall score and detailed explanations
        """
        # Calculate component scores
        engagement_score, engagement_exp = self.calculate_engagement_score(
            activities, course_students
        )
        
        quiz_score, quiz_exp = self.calculate_quiz_performance_score(grades)
        
        attendance_score, attendance_exp = self.calculate_attendance_score(
            attendance_records, course_students
        )
        
        lecture_comp_score, lecture_exp = self.calculate_lecture_completion_score(
            activities, total_lectures
        )
        
        sentiment_score, sentiment_exp = self.calculate_sentiment_score(
            feedback_analysis
        )
        
        resource_score, resource_exp = self.calculate_resource_usage_score(
            activities, total_materials
        )
        
        activity_score, activity_exp = self.calculate_activity_patterns_score(
            activities, course_duration_days
        )
        
        # Calculate weighted overall score
        overall_score = (
            engagement_score * self.weights['engagement'] +
            quiz_score * self.weights['quiz_performance'] +
            attendance_score * self.weights['attendance'] +
            lecture_comp_score * self.weights['lecture_completion'] +
            sentiment_score * self.weights['sentiment'] +
            resource_score * self.weights['resource_usage'] +
            activity_score * self.weights['activity_patterns']
        )
        
        # Generate grade
        if overall_score >= 90:
            grade = 'A'
        elif overall_score >= 80:
            grade = 'B'
        elif overall_score >= 70:
            grade = 'C'
        elif overall_score >= 60:
            grade = 'D'
        else:
            grade = 'F'
        
        # Compile results
        result = {
            'overall_score': round(overall_score, 2),
            'grade': grade,
            'calculated_at': datetime.utcnow().isoformat(),
            'components': {
                'engagement': {
                    'score': round(engagement_score, 2),
                    'weight': self.weights['engagement'],
                    'contribution': round(engagement_score * self.weights['engagement'], 2),
                    'explanation': engagement_exp
                },
                'quiz_performance': {
                    'score': round(quiz_score, 2),
                    'weight': self.weights['quiz_performance'],
                    'contribution': round(quiz_score * self.weights['quiz_performance'], 2),
                    'explanation': quiz_exp
                },
                'attendance': {
                    'score': round(attendance_score, 2),
                    'weight': self.weights['attendance'],
                    'contribution': round(attendance_score * self.weights['attendance'], 2),
                    'explanation': attendance_exp
                },
                'lecture_completion': {
                    'score': round(lecture_comp_score, 2),
                    'weight': self.weights['lecture_completion'],
                    'contribution': round(lecture_comp_score * self.weights['lecture_completion'], 2),
                    'explanation': lecture_exp
                },
                'sentiment': {
                    'score': round(sentiment_score, 2),
                    'weight': self.weights['sentiment'],
                    'contribution': round(sentiment_score * self.weights['sentiment'], 2),
                    'explanation': sentiment_exp
                },
                'resource_usage': {
                    'score': round(resource_score, 2),
                    'weight': self.weights['resource_usage'],
                    'contribution': round(resource_score * self.weights['resource_usage'], 2),
                    'explanation': resource_exp
                },
                'activity_patterns': {
                    'score': round(activity_score, 2),
                    'weight': self.weights['activity_patterns'],
                    'contribution': round(activity_score * self.weights['activity_patterns'], 2),
                    'explanation': activity_exp
                }
            },
            'weights_used': self.weights
        }
        
        return result
    
    def save_teaching_score(self, teacher_id: str, course_id: str, 
                          score_data: Dict):
        """Save teaching score to storage"""
        data = self._load_scores()
        
        score_record = {
            'score_id': f"{teacher_id}_{course_id}_{int(datetime.utcnow().timestamp())}",
            'teacher_id': teacher_id,
            'course_id': course_id,
            **score_data
        }
        
        data['scores'].append(score_record)
        self._save_scores(data)
    
    def get_teacher_scores(self, teacher_id: str) -> List[Dict]:
        """Get all scores for a teacher"""
        data = self._load_scores()
        return [s for s in data['scores'] if s['teacher_id'] == teacher_id]
    
    def get_course_score(self, course_id: str) -> Optional[Dict]:
        """Get latest score for a course"""
        data = self._load_scores()
        course_scores = [s for s in data['scores'] if s['course_id'] == course_id]
        
        if not course_scores:
            return None
        
        # Return most recent
        course_scores.sort(key=lambda x: x['calculated_at'], reverse=True)
        return course_scores[0]


# Singleton instance
_calculator_instance = None


def get_teaching_score_calculator() -> TeachingScoreCalculator:
    """Get singleton teaching score calculator instance"""
    global _calculator_instance
    if _calculator_instance is None:
        _calculator_instance = TeachingScoreCalculator()
    return _calculator_instance
