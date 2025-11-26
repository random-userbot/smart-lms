"""
Smart LMS - Advanced Teaching Score Model
Comprehensive evaluation combining ML predictions, student feedback, performance metrics,
and real-time engagement data for accurate teacher assessment
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import json
import logging
from pathlib import Path
import sys
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# Import existing services
sys.path.append(str(Path(__file__).parent))
from evaluation import get_evaluation_service

# Optional ensemble detector import
try:
    from ensemble_engagement import EnsembleEngagementDetector
    ENSEMBLE_AVAILABLE = True
except ImportError:
    EnsembleEngagementDetector = None
    ENSEMBLE_AVAILABLE = False
    logging.warning("EnsembleEngagementDetector not available - using fallback scoring")


class TeachingScoreModel:
    """
    Advanced Teaching Score Model that combines:

    1. Student Engagement (40%) - From ensemble ML model
       - Real-time engagement detection
       - Emotion analysis (boredom, confusion, frustration)
       - Attention patterns

    2. Student Feedback (25%) - Qualitative assessment
       - Rating scores (1-5 scale)
       - Written feedback sentiment
       - Recommendation rates

    3. Student Performance (20%) - Learning outcomes
       - Quiz scores and improvement
       - Assignment completion rates
       - Grade distributions

    4. Teaching Activity (10%) - Engagement and responsiveness
       - Content upload frequency
       - Material updates
       - Response times to queries

    5. Class Engagement (5%) - Overall participation
       - Attendance rates
       - Participation metrics
       - Interaction patterns
    """

    def __init__(self, ensemble_model_path: str = None):
        """Initialize the teaching score model"""
        self.weights = {
            'engagement': 0.40,
            'feedback': 0.25,
            'performance': 0.20,
            'activity': 0.10,
            'class_engagement': 0.05
        }

        # Initialize ensemble detector for real-time engagement (optional)
        if ENSEMBLE_AVAILABLE:
            try:
                self.ensemble_detector = EnsembleEngagementDetector(
                    export_dir=ensemble_model_path,
                    mode="balanced",
                    enable_cache=True
                )
                logging.info("Ensemble detector initialized successfully")
            except Exception as e:
                logging.warning(f"Could not initialize ensemble detector: {e}")
                self.ensemble_detector = None
        else:
            self.ensemble_detector = None
            logging.info("Ensemble detector not available - using simplified scoring")

        # Get existing evaluation service
        self.eval_service = get_evaluation_service()

        # Score ranges and thresholds
        self.score_ranges = {
            'excellent': (90, 100),
            'good': (80, 89),
            'satisfactory': (70, 79),
            'needs_improvement': (60, 69),
            'unsatisfactory': (0, 59)
        }

        self.performance_levels = {
            'A+': (95, 100), 'A': (90, 94), 'A-': (85, 89),
            'B+': (80, 84), 'B': (75, 79), 'B-': (70, 74),
            'C+': (65, 69), 'C': (60, 64), 'C-': (55, 59),
            'D': (50, 54), 'F': (0, 49)
        }

    def calculate_comprehensive_score(self, teacher_id: str, storage, time_period: str = "30d") -> Dict[str, Any]:
        """
        Calculate comprehensive teaching score using all available data

        Args:
            teacher_id: Teacher ID to evaluate
            storage: Storage service instance
            time_period: Time period for analysis ("7d", "30d", "90d", "all")

        Returns:
            Comprehensive evaluation dictionary
        """
        # Get time range
        end_date = datetime.now()
        if time_period == "7d":
            start_date = end_date - timedelta(days=7)
        elif time_period == "30d":
            start_date = end_date - timedelta(days=30)
        elif time_period == "90d":
            start_date = end_date - timedelta(days=90)
        else:  # "all"
            start_date = None

        # Calculate component scores
        engagement_score = self._calculate_engagement_score(teacher_id, storage, start_date, end_date)
        feedback_score = self._calculate_feedback_score(teacher_id, storage, start_date, end_date)
        performance_score = self._calculate_performance_score(teacher_id, storage, start_date, end_date)
        activity_score = self._calculate_activity_score(teacher_id, storage, start_date, end_date)
        class_engagement_score = self._calculate_class_engagement_score(teacher_id, storage, start_date, end_date)

        # Weighted final score
        final_score = (
            self.weights['engagement'] * engagement_score +
            self.weights['feedback'] * feedback_score +
            self.weights['performance'] * performance_score +
            self.weights['activity'] * activity_score +
            self.weights['class_engagement'] * class_engagement_score
        )

        # Determine performance level and grade
        performance_level, grade = self._determine_performance_level(final_score)

        # Create component scores dictionary
        component_scores = {
            'engagement': engagement_score,
            'feedback': feedback_score,
            'performance': performance_score,
            'activity': activity_score,
            'class_engagement': class_engagement_score
        }

        # Generate recommendations
        recommendations = self._generate_recommendations(component_scores, final_score)

        # Get trend analysis
        trend_data = self._calculate_trend_analysis(teacher_id, storage)

        # Try to use ML model prediction if available
        ml_score = self._predict_with_ml_model(component_scores, teacher_id, storage)
        if ml_score is not None:
            # Blend statistical score with ML prediction (70% statistical, 30% ML)
            final_score = 0.7 * final_score + 0.3 * ml_score
            final_score = min(100.0, max(0.0, final_score))

        # Add predictive analytics
        predictive_insights = self._generate_predictive_insights(teacher_id, storage, final_score, component_scores)

        return {
            'teacher_id': teacher_id,
            'final_score': round(final_score, 2),
            'grade': grade,
            'performance_level': performance_level,
            'component_scores': {
                'engagement': round(engagement_score, 2),
                'feedback': round(feedback_score, 2),
                'performance': round(performance_score, 2),
                'activity': round(activity_score, 2),
                'class_engagement': round(class_engagement_score, 2)
            },
            'weights': self.weights,
            'time_period': time_period,
            'calculated_at': datetime.now().isoformat(),
            'recommendations': recommendations,
            'trend_analysis': trend_data,
            'predictive_insights': predictive_insights,
            'detailed_metrics': self._get_detailed_metrics(teacher_id, storage, start_date, end_date),
            'ml_prediction_used': ml_score is not None,
            'ml_score': round(ml_score, 2) if ml_score is not None else None
        }

    def _calculate_engagement_score(self, teacher_id: str, storage, start_date: datetime, end_date: datetime) -> float:
        """Calculate engagement score from ML model predictions and real-time data"""
        try:
            # Get teacher's courses
            courses = storage.get_all_courses(teacher_id=teacher_id)
            if not courses:
                return 50.0  # Neutral score if no courses

            total_engagement = 0
            total_sessions = 0

            for course_id, course in courses.items():
                # Get lectures for this course
                lectures = storage.get_course_lectures(course_id)

                for lecture in lectures:
                    lecture_id = lecture['lecture_id']

                    # Get engagement logs for this lecture
                    engagement_logs = storage.get_engagement_logs(lecture_id=lecture_id)

                    # Filter by time period if specified
                    if start_date:
                        engagement_logs = [log for log in engagement_logs
                                         if datetime.fromisoformat(log['timestamp']) >= start_date]

                    if engagement_logs:
                        # Calculate average engagement for this lecture
                        avg_engagement = np.mean([log['engagement_score'] for log in engagement_logs])
                        total_engagement += avg_engagement
                        total_sessions += 1

                        # Bonus for consistent engagement (low variance)
                        engagement_scores = [log['engagement_score'] for log in engagement_logs]
                        if len(engagement_scores) > 1:
                            variance = np.var(engagement_scores)
                            consistency_bonus = max(0, 10 - variance)  # Max 10 points for consistency
                            total_engagement += consistency_bonus * 0.1  # Scale down

            if total_sessions == 0:
                return 60.0  # Slightly above neutral if no data but courses exist

            # Normalize to 0-100 scale
            avg_engagement = total_engagement / total_sessions
            return min(100.0, max(0.0, avg_engagement))

        except Exception as e:
            logging.warning(f"Error calculating engagement score: {e}")
            return 50.0

    def _calculate_feedback_score(self, teacher_id: str, storage, start_date: datetime, end_date: datetime) -> float:
        """Calculate feedback score from student ratings and reviews"""
        try:
            # Get teacher feedback
            teacher_feedback = storage.get_teacher_feedback(teacher_id)

            # Filter by time period
            if start_date:
                teacher_feedback = [fb for fb in teacher_feedback
                                  if datetime.fromisoformat(fb.get('created_at', '')) >= start_date]

            if not teacher_feedback:
                return 70.0  # Neutral-good score if no feedback

            # Calculate average rating
            ratings = []
            sentiments = []
            recommendations = []

            for fb in teacher_feedback:
                # Rating score (1-5 scale)
                rating = fb.get('ratings', {}).get('overall', 3)
                ratings.append(rating)

                # Sentiment score (-1 to 1, convert to 0-100)
                sentiment = fb.get('nlp_analysis', {}).get('sentiment', {}).get('compound', 0)
                sentiment_score = (sentiment + 1) * 50  # Convert -1,1 to 0,100
                sentiments.append(sentiment_score)

                # Recommendation (binary)
                recommendation = fb.get('metadata', {}).get('would_recommend', False)
                recommendations.append(1 if recommendation else 0)

            # Weighted average: 50% rating, 30% sentiment, 20% recommendation
            avg_rating = np.mean(ratings) * 20  # Convert 1-5 to 0-100
            avg_sentiment = np.mean(sentiments)
            recommendation_rate = np.mean(recommendations) * 100

            feedback_score = (
                0.5 * avg_rating +
                0.3 * avg_sentiment +
                0.2 * recommendation_rate
            )

            return min(100.0, max(0.0, feedback_score))

        except Exception as e:
            logging.warning(f"Error calculating feedback score: {e}")
            return 70.0

    def _calculate_performance_score(self, teacher_id: str, storage, start_date: datetime, end_date: datetime) -> float:
        """Calculate performance score based on student learning outcomes"""
        try:
            # Get teacher's courses
            courses = storage.get_all_courses(teacher_id=teacher_id)
            if not courses:
                return 60.0

            total_quiz_score = 0
            total_assignment_score = 0
            total_completion_rate = 0
            course_count = 0

            for course_id, course in courses.items():
                course_students = course.get('enrolled_students', [])
                if not course_students:
                    continue

                course_quiz_scores = []
                course_assignment_scores = []
                completed_assignments = 0
                total_assignments = 0

                for student_id in course_students:
                    # Get student grades
                    grades = storage.get_student_grades(student_id)

                    # Filter by course and time period
                    course_quizzes = []
                    course_assignments = []

                    for quiz in grades.get('quizzes', []):
                        if quiz.get('course_id') == course_id:
                            if start_date and datetime.fromisoformat(quiz.get('completed_at', '')) >= start_date:
                                course_quizzes.append(quiz['percentage'])
                            elif not start_date:
                                course_quizzes.append(quiz['percentage'])

                    for assignment in grades.get('assignments', []):
                        if assignment.get('course_id') == course_id:
                            if start_date and datetime.fromisoformat(assignment.get('submitted_at', '')) >= start_date:
                                course_assignments.append(assignment['percentage'])
                                completed_assignments += 1
                            elif not start_date:
                                course_assignments.append(assignment['percentage'])
                                completed_assignments += 1

                    # Estimate total assignments (simplified approach)
                    # Since we don't have a direct method, we'll use a default estimate
                    total_assignments += max(1, len(course_quiz_scores) // 2)  # Rough estimate

                    course_quiz_scores.extend(course_quizzes)
                    course_assignment_scores.extend(course_assignments)

                # Calculate course metrics
                if course_quiz_scores:
                    avg_quiz = np.mean(course_quiz_scores)
                    total_quiz_score += avg_quiz

                if course_assignment_scores:
                    avg_assignment = np.mean(course_assignment_scores)
                    total_assignment_score += avg_assignment

                # Completion rate
                if total_assignments > 0:
                    completion = completed_assignments / (len(course_students) * total_assignments)
                    total_completion_rate += completion

                course_count += 1

            if course_count == 0:
                return 60.0

            # Weighted average: 40% quiz, 40% assignment, 20% completion
            avg_quiz_score = total_quiz_score / course_count if course_count > 0 else 0
            avg_assignment_score = total_assignment_score / course_count if course_count > 0 else 0
            avg_completion_rate = (total_completion_rate / course_count) * 100 if course_count > 0 else 0

            performance_score = (
                0.4 * avg_quiz_score +
                0.4 * avg_assignment_score +
                0.2 * avg_completion_rate
            )

            return min(100.0, max(0.0, performance_score))

        except Exception as e:
            logging.warning(f"Error calculating performance score: {e}")
            return 60.0

    def _calculate_activity_score(self, teacher_id: str, storage, start_date: datetime, end_date: datetime) -> float:
        """Calculate activity score based on teaching engagement and responsiveness"""
        try:
            # Get teacher activity logs
            activity_logs = storage.get_teacher_activity(teacher_id, days=30 if start_date else None)

            if not activity_logs:
                return 40.0  # Low score for no activity

            # Filter by time period
            if start_date:
                activity_logs = [log for log in activity_logs
                               if datetime.fromisoformat(log['timestamp']) >= start_date]

            # Count activities by type
            upload_count = sum(1 for log in activity_logs if log['action'] == 'upload_lecture')
            material_count = sum(1 for log in activity_logs if log['action'] == 'upload_material')
            quiz_count = sum(1 for log in activity_logs if log['action'] == 'create_quiz')
            assignment_count = sum(1 for log in activity_logs if log['action'] == 'create_assignment')
            response_count = sum(1 for log in activity_logs if 'response' in log['action'].lower())

            # Calculate frequency scores (per week)
            days_span = 30 if not start_date else (end_date - start_date).days
            weeks = max(1, days_span / 7)

            upload_freq = upload_count / weeks
            material_freq = material_count / weeks
            assessment_freq = (quiz_count + assignment_count) / weeks
            response_freq = response_count / weeks

            # Score components (0-100 scale)
            upload_score = min(100, upload_freq * 20)  # 1 upload/week = 20 points
            material_score = min(100, material_freq * 25)  # 1 material/week = 25 points
            assessment_score = min(100, assessment_freq * 15)  # 1 assessment/week = 15 points
            response_score = min(100, response_freq * 30)  # 1 response/week = 30 points

            # Weighted average
            activity_score = (
                0.3 * upload_score +
                0.25 * material_score +
                0.25 * assessment_score +
                0.2 * response_score
            )

            return activity_score

        except Exception as e:
            logging.warning(f"Error calculating activity score: {e}")
            return 40.0

    def _calculate_class_engagement_score(self, teacher_id: str, storage, start_date: datetime, end_date: datetime) -> float:
        """Calculate class engagement score based on attendance and participation"""
        try:
            # Get teacher's courses
            courses = storage.get_all_courses(teacher_id=teacher_id)
            if not courses:
                return 50.0

            total_attendance = 0
            total_participation = 0
            course_count = 0

            for course_id, course in courses.items():
                course_students = course.get('enrolled_students', [])
                if not course_students:
                    continue

                # Get lectures
                lectures = storage.get_course_lectures(course_id)

                course_attendance = 0
                course_participation = 0
                lecture_count = 0

                for lecture in lectures:
                    lecture_id = lecture['lecture_id']

                    # Get attendance records
                    attendance_records = storage.get_attendance(lecture_id=lecture_id)

                    # Filter by time period
                    if start_date:
                        attendance_records = [a for a in attendance_records
                                            if datetime.fromisoformat(a.get('timestamp', '')) >= start_date]

                    if attendance_records:
                        # Calculate attendance rate for this lecture
                        attendance_rate = np.mean([a['presence_percentage'] for a in attendance_records]) / 100
                        course_attendance += attendance_rate

                        # Get participation from engagement logs (high engagement = participation)
                        engagement_logs = storage.get_engagement_logs(lecture_id=lecture_id)
                        if engagement_logs:
                            avg_participation = np.mean([log['engagement_score'] for log in engagement_logs]) / 100
                            course_participation += avg_participation

                        lecture_count += 1

                if lecture_count > 0:
                    avg_course_attendance = (course_attendance / lecture_count) * 100
                    avg_course_participation = (course_participation / lecture_count) * 100

                    total_attendance += avg_course_attendance
                    total_participation += avg_course_participation
                    course_count += 1

            if course_count == 0:
                return 50.0

            # Weighted average: 60% attendance, 40% participation
            avg_attendance = total_attendance / course_count
            avg_participation = total_participation / course_count

            class_engagement_score = (
                0.6 * avg_attendance +
                0.4 * avg_participation
            )

            return min(100.0, max(0.0, class_engagement_score))

        except Exception as e:
            logging.warning(f"Error calculating class engagement score: {e}")
            return 50.0

    def _predict_with_ml_model(self, component_scores: Dict[str, float], teacher_id: str, storage) -> Optional[float]:
        """Predict score using trained ML model (XGBoost/RandomForest) if available"""
        try:
            # Try to get evaluation service and use ML prediction
            eval_service = get_evaluation_service()

            # Build features in the same format as the evaluation service expects
            features = {
                'teacher_id': teacher_id,
                'num_courses': len(storage.get_all_courses(teacher_id=teacher_id)),
                'avg_engagement_score': component_scores.get('engagement', 0) / 100.0,  # Normalize to 0-1
                'avg_feedback_sentiment': component_scores.get('feedback', 0) / 100.0,
                'avg_quiz_score': component_scores.get('performance', 0) / 100.0,
                'avg_assignment_score': component_scores.get('performance', 0) / 100.0,
                'upload_frequency': component_scores.get('activity', 0) / 100.0 * 10,  # Scale up
                'material_update_count': component_scores.get('activity', 0) / 100.0 * 10,
                'login_frequency': component_scores.get('activity', 0) / 100.0 * 10,
                'response_time': 1.0 / max(component_scores.get('activity', 1), 1),
                'attendance_rate': component_scores.get('class_engagement', 0) / 100.0,
                'feedback_count': 5.0  # Default estimate
            }

            # Try to predict with ML model
            score, shap_values = eval_service.predict_score(features)

            if score is not None:
                logging.info(f"ML prediction successful for teacher {teacher_id}: {score:.2f}")
                return float(score)
            else:
                logging.info(f"No trained ML model available, using statistical scoring")
                return None

        except Exception as e:
            logging.warning(f"ML prediction failed, falling back to statistical scoring: {e}")
            return None

    def _determine_performance_level(self, score: float) -> Tuple[str, str]:
        """Determine performance level and grade from score"""
        for level, (min_score, max_score) in self.performance_levels.items():
            if min_score <= score <= max_score:
                grade = level
                break
        else:
            grade = 'F'

        # Determine performance level
        if score >= 90:
            performance_level = 'Outstanding'
        elif score >= 80:
            performance_level = 'Excellent'
        elif score >= 70:
            performance_level = 'Good'
        elif score >= 60:
            performance_level = 'Satisfactory'
        else:
            performance_level = 'Needs Improvement'

        return performance_level, grade

    def _generate_recommendations(self, component_scores: Dict[str, float], final_score: float) -> List[str]:
        """Generate personalized recommendations based on scores"""
        recommendations = []

        # Check each component
        if component_scores['engagement'] < 70:
            recommendations.append("📊 Focus on improving student engagement during lectures")
            recommendations.append("🎯 Incorporate more interactive elements and real-time feedback")

        if component_scores['feedback'] < 70:
            recommendations.append("💬 Actively seek and respond to student feedback")
            recommendations.append("📝 Request more detailed feedback through surveys")

        if component_scores['performance'] < 70:
            recommendations.append("📚 Review teaching methods to improve student learning outcomes")
            recommendations.append("🎓 Consider additional support materials or tutoring sessions")

        if component_scores['activity'] < 70:
            recommendations.append("⚡ Increase content upload frequency and stay engaged with students")
            recommendations.append("📤 Regularly update course materials and assignments")

        if component_scores['class_engagement'] < 70:
            recommendations.append("👥 Implement strategies to improve attendance and participation")
            recommendations.append("🎪 Create more engaging and interactive class sessions")

        # Overall recommendations
        if final_score >= 90:
            recommendations.append("🌟 Excellent work! Continue maintaining high standards")
        elif final_score >= 80:
            recommendations.append("✅ Good performance! Focus on the identified improvement areas")
        elif final_score >= 70:
            recommendations.append("📈 Satisfactory performance. Consider professional development opportunities")
        else:
            recommendations.append("🔄 Significant improvements needed. Consider mentorship or training programs")

        return recommendations

    def _calculate_trend_analysis(self, teacher_id: str, storage) -> Dict[str, Any]:
        """Calculate trend analysis for teaching performance"""
        try:
            # Get all evaluations and filter for this teacher
            all_evaluations = storage.get_all_evaluations()
            evaluations = [eval_data for eval_data in all_evaluations.values()
                          if eval_data.get('teacher_id') == teacher_id]

            if len(evaluations) < 2:
                return {'trend': 'insufficient_data', 'change': 0, 'description': 'Not enough historical data'}

            # Sort by date
            evaluations.sort(key=lambda x: x.get('evaluated_at', ''))

            # Calculate trend
            scores = [e['score'] for e in evaluations]
            recent_scores = scores[-3:] if len(scores) >= 3 else scores

            # Simple linear trend
            if len(scores) >= 2:
                first_half = scores[:len(scores)//2]
                second_half = scores[len(scores)//2:]

                avg_first = np.mean(first_half)
                avg_second = np.mean(second_half)
                change = avg_second - avg_first

                if change > 5:
                    trend = 'improving'
                    description = 'Performance is trending upward'
                elif change < -5:
                    trend = 'declining'
                    description = 'Performance needs attention'
                else:
                    trend = 'stable'
                    description = 'Performance is stable'
            else:
                trend = 'stable'
                change = 0
                description = 'Recent performance is stable'

            return {
                'trend': trend,
                'change': round(change, 2),
                'description': description,
                'data_points': len(evaluations),
                'recent_average': round(np.mean(recent_scores), 2)
            }

        except Exception as e:
            logging.warning(f"Error calculating trend analysis: {e}")
            return {'trend': 'error', 'change': 0, 'description': 'Could not calculate trend'}

    def _get_detailed_metrics(self, teacher_id: str, storage, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get detailed metrics for advanced analysis"""
        try:
            # Get course-wise breakdown
            courses = storage.get_all_courses(teacher_id=teacher_id)
            course_breakdown = []

            for course_id, course in courses.items():
                course_metrics = {
                    'course_id': course_id,
                    'course_name': course['name'],
                    'enrolled_students': len(course.get('enrolled_students', [])),
                    'lectures_count': len(course.get('lectures', [])),
                    'avg_engagement': 0,
                    'avg_feedback_rating': 0,
                    'completion_rate': 0
                }

                # Calculate course-specific metrics
                lectures = storage.get_course_lectures(course_id)
                if lectures:
                    engagement_scores = []
                    feedback_ratings = []

                    for lecture in lectures:
                        # Engagement
                        logs = storage.get_engagement_logs(lecture_id=lecture['lecture_id'])
                        if logs:
                            engagement_scores.extend([log['engagement_score'] for log in logs])

                        # Feedback
                        feedback = storage.get_feedback(lecture_id=lecture['lecture_id'])
                        if feedback:
                            feedback_ratings.extend([f['rating'] for f in feedback])

                    course_metrics['avg_engagement'] = np.mean(engagement_scores) if engagement_scores else 0
                    course_metrics['avg_feedback_rating'] = np.mean(feedback_ratings) if feedback_ratings else 0

                course_breakdown.append(course_metrics)

            return {
                'course_breakdown': course_breakdown,
                'total_courses': len(courses),
                'total_students': sum(len(c.get('enrolled_students', [])) for c in courses.values()),
                'total_lectures': sum(len(c.get('lectures', [])) for c in courses.values())
            }

        except Exception as e:
            logging.warning(f"Error getting detailed metrics: {e}")
            return {}

    def _generate_predictive_insights(self, teacher_id: str, storage, current_score: float, component_scores: Dict[str, float]) -> Dict[str, Any]:
        """Generate predictive analytics and future performance insights"""
        try:
            # Get historical evaluation data
            historical_evaluations = storage.get_teacher_evaluations(teacher_id, limit=10)

            if len(historical_evaluations) < 3:
                return {
                    'available': False,
                    'message': 'Need at least 3 evaluation periods for predictions',
                    'forecast_score': None,
                    'risk_assessment': 'Unknown',
                    'improvement_trajectory': []
                }

            # Prepare data for prediction
            eval_dates = []
            scores = []
            component_trends = {comp: [] for comp in component_scores.keys()}

            for eval_data in sorted(historical_evaluations, key=lambda x: x.get('evaluated_at', '')):
                eval_dates.append(datetime.fromisoformat(eval_data['evaluated_at']))
                scores.append(eval_data['score'])

                # Track component trends
                eval_components = eval_data.get('features', {}).get('component_scores', {})
                for comp in component_trends.keys():
                    component_trends[comp].append(eval_components.get(comp, 0))

            # Convert dates to days since first evaluation
            base_date = min(eval_dates)
            days_since_start = [(d - base_date).days for d in eval_dates]

            # Fit linear regression for score prediction
            if len(days_since_start) >= 3:
                X = np.array(days_since_start).reshape(-1, 1)
                y = np.array(scores)

                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)

                model = LinearRegression()
                model.fit(X_scaled, y)

                # Predict next 3 months (90 days)
                future_days = max(days_since_start) + 90
                future_X = np.array([[future_days]])
                future_X_scaled = scaler.transform(future_X)
                predicted_score = float(model.predict(future_X_scaled)[0])

                # Clip to valid range
                predicted_score = np.clip(predicted_score, 0, 100)

                # Calculate prediction confidence
                r_squared = model.score(X_scaled, y)
                confidence_level = 'High' if r_squared > 0.7 else 'Medium' if r_squared > 0.4 else 'Low'
            else:
                predicted_score = current_score
                r_squared = 0
                confidence_level = 'Low'

            # Risk assessment
            risk_assessment = self._assess_performance_risk(current_score, predicted_score, component_scores)

            # Improvement trajectory
            improvement_trajectory = self._calculate_improvement_trajectory(
                current_score, predicted_score, component_scores, historical_evaluations
            )

            # Component predictions
            component_predictions = {}
            for comp, values in component_trends.items():
                if len(values) >= 3:
                    try:
                        comp_model = LinearRegression()
                        comp_X = np.array(days_since_start).reshape(-1, 1)
                        comp_model.fit(comp_X, values)

                        future_comp_score = float(comp_model.predict(future_X)[0])
                        future_comp_score = np.clip(future_comp_score, 0, 100)

                        trend_direction = 'improving' if future_comp_score > component_scores[comp] else 'declining' if future_comp_score < component_scores[comp] else 'stable'

                        component_predictions[comp] = {
                            'predicted_score': round(future_comp_score, 1),
                            'trend': trend_direction,
                            'change': round(future_comp_score - component_scores[comp], 1)
                        }
                    except:
                        component_predictions[comp] = {
                            'predicted_score': component_scores[comp],
                            'trend': 'stable',
                            'change': 0
                        }
                else:
                    component_predictions[comp] = {
                        'predicted_score': component_scores[comp],
                        'trend': 'stable',
                        'change': 0
                    }

            return {
                'available': True,
                'forecast_score': round(predicted_score, 1),
                'prediction_confidence': confidence_level,
                'confidence_score': round(r_squared * 100, 1),
                'risk_assessment': risk_assessment,
                'improvement_trajectory': improvement_trajectory,
                'component_predictions': component_predictions,
                'forecast_period': '3 months',
                'data_points_used': len(historical_evaluations)
            }

        except Exception as e:
            logging.warning(f"Error generating predictive insights: {e}")
            return {
                'available': False,
                'message': f'Could not generate predictions: {str(e)}',
                'forecast_score': None,
                'risk_assessment': 'Unknown'
            }

    def _assess_performance_risk(self, current_score: float, predicted_score: float, component_scores: Dict[str, float]) -> str:
        """Assess performance risk based on current and predicted scores"""
        score_change = predicted_score - current_score

        # Risk factors
        risk_factors = []

        # Score declining
        if score_change < -5:
            risk_factors.append('score_declining')
        elif score_change < -2:
            risk_factors.append('score_slightly_declining')

        # Low current score
        if current_score < 60:
            risk_factors.append('low_current_score')
        elif current_score < 75:
            risk_factors.append('moderate_current_score')

        # Component weaknesses
        weak_components = [comp for comp, score in component_scores.items() if score < 60]
        if len(weak_components) > 2:
            risk_factors.append('multiple_weak_components')
        elif len(weak_components) > 0:
            risk_factors.append('some_weak_components')

        # Determine overall risk
        if not risk_factors:
            return 'Low Risk'
        elif 'score_declining' in risk_factors or 'low_current_score' in risk_factors:
            return 'High Risk'
        elif len(risk_factors) >= 2:
            return 'Medium Risk'
        else:
            return 'Low-Moderate Risk'

    def _calculate_improvement_trajectory(self, current_score: float, predicted_score: float,
                                        component_scores: Dict[str, float], historical_data: List[Dict]) -> List[Dict]:
        """Calculate improvement trajectory and milestones"""
        trajectory = []
        score_change = predicted_score - current_score

        # Current status
        trajectory.append({
            'period': 'Current',
            'score': round(current_score, 1),
            'status': 'baseline',
            'description': f'Current performance: {current_score:.1f}/100'
        })

        # Short-term (1 month)
        short_term_score = current_score + (score_change * 0.33)
        short_term_score = np.clip(short_term_score, 0, 100)

        trajectory.append({
            'period': '1 Month',
            'score': round(short_term_score, 1),
            'status': 'predicted',
            'description': f'Projected: {short_term_score:.1f}/100 ({short_term_score - current_score:+.1f})'
        })

        # Medium-term (2 months)
        medium_term_score = current_score + (score_change * 0.67)
        medium_term_score = np.clip(medium_term_score, 0, 100)

        trajectory.append({
            'period': '2 Months',
            'score': round(medium_term_score, 1),
            'status': 'predicted',
            'description': f'Projected: {medium_term_score:.1f}/100 ({medium_term_score - current_score:+.1f})'
        })

        # Long-term (3 months)
        trajectory.append({
            'period': '3 Months',
            'score': round(predicted_score, 1),
            'status': 'predicted',
            'description': f'Projected: {predicted_score:.1f}/100 ({score_change:+.1f})'
        })

        return trajectory


# Singleton instance
_teaching_score_model = None

def get_teaching_score_model() -> TeachingScoreModel:
    """Get teaching score model singleton"""
    global _teaching_score_model
    if _teaching_score_model is None:
        _teaching_score_model = TeachingScoreModel()
    return _teaching_score_model
