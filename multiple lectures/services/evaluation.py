"""
Smart LMS - Teacher Evaluation Service
XGBoost/RandomForest model with SHAP explainability
"""

import yaml
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import joblib
import os


class TeacherEvaluationService:
    """Teacher evaluation using ML models with explainability"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize evaluation service"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.eval_config = self.config['evaluation']
        self.model_type = self.eval_config['model']
        self.features = self.eval_config['features']
        self.shap_enabled = self.eval_config['shap']['enabled']
        
        self.model = None
        self.feature_names = None
        
        # Try to load existing model
        self._load_model()
    
    def _load_model(self):
        """Load pre-trained model if exists"""
        model_path = f"./ml/models/evaluation_{self.model_type}.pkl"
        
        if os.path.exists(model_path):
            try:
                self.model = joblib.load(model_path)
                print(f"✅ Loaded evaluation model: {model_path}")
            except Exception as e:
                print(f"⚠️ Failed to load model: {e}")
    
    def build_features(self, teacher_id: str, storage) -> Optional[Dict]:
        """
        Build feature vector for a teacher
        
        Args:
            teacher_id: Teacher ID
            storage: Storage service instance
        
        Returns:
            Dictionary with features or None if insufficient data
        """
        # Get teacher's courses
        courses = storage.get_all_courses(teacher_id=teacher_id)
        
        if not courses:
            return None
        
        # Initialize feature dict
        features = {
            'teacher_id': teacher_id,
            'num_courses': len(courses)
        }
        
        # Aggregate data across all courses
        all_engagement_scores = []
        all_feedback = []
        all_quiz_scores = []
        all_assignment_scores = []
        total_students = 0
        
        for course_id, course in courses.items():
            # Get enrolled students
            students = course.get('enrolled_students', [])
            total_students += len(students)
            
            # Get lectures
            lectures = storage.get_course_lectures(course_id)
            
            for lecture in lectures:
                lecture_id = lecture['lecture_id']
                
                # Get engagement logs
                engagement_logs = storage.get_engagement_logs(lecture_id=lecture_id)
                all_engagement_scores.extend([log['engagement_score'] for log in engagement_logs])
                
                # Get feedback
                feedback = storage.get_feedback(lecture_id=lecture_id)
                all_feedback.extend(feedback)
            
            # Get grades for students in this course
            for student_id in students:
                grades = storage.get_student_grades(student_id)
                
                # Filter by course
                course_quizzes = [q for q in grades.get('quizzes', []) if q.get('course_id') == course_id]
                course_assignments = [a for a in grades.get('assignments', []) if a.get('course_id') == course_id]
                
                all_quiz_scores.extend([q['percentage'] for q in course_quizzes])
                all_assignment_scores.extend([a['percentage'] for a in course_assignments])
        
        # Feature 1: Average engagement score
        features['avg_engagement_score'] = np.mean(all_engagement_scores) if all_engagement_scores else 0
        
        # Feature 2: Average feedback sentiment
        if all_feedback:
            avg_rating = np.mean([f['rating'] for f in all_feedback])
            features['avg_feedback_sentiment'] = avg_rating / 5.0  # Normalize to 0-1
        else:
            features['avg_feedback_sentiment'] = 0.5  # Neutral
        
        # Feature 3: Average quiz score
        features['avg_quiz_score'] = np.mean(all_quiz_scores) / 100 if all_quiz_scores else 0
        
        # Feature 4: Average assignment score
        features['avg_assignment_score'] = np.mean(all_assignment_scores) / 100 if all_assignment_scores else 0
        
        # Feature 5: Feedback count (normalized by students)
        features['feedback_count'] = len(all_feedback) / max(total_students, 1)
        
        # Feature 6-10: Teacher activity metrics
        teacher_activity = storage.get_teacher_activity(teacher_id, days=30)
        
        # Count activities by type
        upload_count = sum(1 for a in teacher_activity if a['action'] == 'upload_lecture')
        material_count = sum(1 for a in teacher_activity if a['action'] == 'upload_material')
        quiz_count = sum(1 for a in teacher_activity if a['action'] == 'create_quiz')
        assignment_count = sum(1 for a in teacher_activity if a['action'] == 'create_assignment')
        login_count = len(teacher_activity)  # Total activities as proxy for logins
        
        features['upload_frequency'] = upload_count / 30  # Per day
        features['material_update_count'] = material_count / 30
        features['login_frequency'] = login_count / 30
        
        # Feature 11: Response time (simplified - based on activity frequency)
        features['response_time'] = 1.0 / max(login_count, 1)  # Inverse of activity
        
        # Feature 12: Attendance rate (from attendance tracking)
        attendance_records = []
        for course_id in courses.keys():
            lectures = storage.get_course_lectures(course_id)
            for lecture in lectures:
                lecture_attendance = storage.get_attendance(lecture_id=lecture['lecture_id'])
                attendance_records.extend(lecture_attendance)
        
        if attendance_records:
            features['attendance_rate'] = np.mean([a['presence_percentage'] for a in attendance_records]) / 100
        else:
            features['attendance_rate'] = 0.75  # Default
        
        return features
    
    def train_model(self, training_data: pd.DataFrame, target_column: str = 'score'):
        """
        Train evaluation model
        
        Args:
            training_data: DataFrame with features and target scores
            target_column: Name of target column
        """
        # Separate features and target
        feature_columns = [col for col in training_data.columns if col not in ['teacher_id', target_column]]
        X = training_data[feature_columns]
        y = training_data[target_column]
        
        self.feature_names = feature_columns
        
        # Train model
        if self.model_type == 'xgboost':
            from xgboost import XGBRegressor
            self.model = XGBRegressor(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
        elif self.model_type == 'random_forest':
            from sklearn.ensemble import RandomForestRegressor
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
        
        self.model.fit(X, y)
        
        # Save model
        model_path = f"./ml/models/evaluation_{self.model_type}.pkl"
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        joblib.dump(self.model, model_path)
        
        print(f"✅ Model trained and saved: {model_path}")
    
    def predict_score(self, features: Dict) -> Tuple[float, Optional[Dict]]:
        """
        Predict teacher evaluation score
        
        Args:
            features: Feature dictionary
        
        Returns:
            Tuple of (score, shap_values_dict)
        """
        if self.model is None:
            # No model trained, use simple weighted average
            return self._predict_simple(features), None
        
        # Prepare feature vector
        feature_vector = [features.get(f, 0) for f in self.feature_names]
        X = np.array(feature_vector).reshape(1, -1)
        
        # Predict
        score = self.model.predict(X)[0]
        
        # Clip to 0-100 range
        score = np.clip(score, 0, 100)
        
        # Compute SHAP values if enabled
        shap_values = None
        if self.shap_enabled:
            shap_values = self._compute_shap_values(X)
        
        return float(score), shap_values
    
    def _predict_simple(self, features: Dict) -> float:
        """Simple weighted average prediction when no model is trained"""
        # Weighted combination of features
        score = (
            0.25 * features.get('avg_engagement_score', 0) +
            0.20 * features.get('avg_feedback_sentiment', 0.5) * 100 +
            0.15 * features.get('avg_quiz_score', 0) * 100 +
            0.15 * features.get('avg_assignment_score', 0) * 100 +
            0.10 * features.get('upload_frequency', 0) * 100 +
            0.10 * features.get('attendance_rate', 0.75) * 100 +
            0.05 * features.get('feedback_count', 0) * 100
        )
        
        return np.clip(score, 0, 100)
    
    def _compute_shap_values(self, X: np.ndarray) -> Dict:
        """
        Compute SHAP values for explainability
        
        Args:
            X: Feature vector (1 x n_features)
        
        Returns:
            Dictionary with SHAP values and feature importances
        """
        try:
            import shap
            
            # Create explainer
            if self.model_type == 'xgboost':
                explainer = shap.TreeExplainer(self.model)
            elif self.model_type == 'random_forest':
                explainer = shap.TreeExplainer(self.model)
            else:
                return None
            
            # Compute SHAP values
            shap_values = explainer.shap_values(X)
            
            # Get base value (expected value)
            base_value = explainer.expected_value
            
            # Create feature importance dict
            feature_importance = {}
            for i, feature_name in enumerate(self.feature_names):
                feature_importance[feature_name] = float(shap_values[0][i])
            
            # Sort by absolute importance
            sorted_features = sorted(
                feature_importance.items(),
                key=lambda x: abs(x[1]),
                reverse=True
            )
            
            return {
                'base_value': float(base_value),
                'feature_importance': feature_importance,
                'top_features': sorted_features[:self.eval_config['shap']['max_display']]
            }
        
        except ImportError:
            print("⚠️ SHAP not installed. Run: pip install shap")
            return None
        except Exception as e:
            print(f"⚠️ SHAP computation failed: {e}")
            return None
    
    def evaluate_teacher(self, teacher_id: str, storage) -> Dict:
        """
        Complete teacher evaluation
        
        Args:
            teacher_id: Teacher ID
            storage: Storage service instance
        
        Returns:
            Dictionary with evaluation results
        """
        # Build features
        features = self.build_features(teacher_id, storage)
        
        if features is None:
            return {
                'teacher_id': teacher_id,
                'score': 0,
                'status': 'insufficient_data',
                'message': 'Not enough data to evaluate this teacher'
            }
        
        # Predict score
        score, shap_values = self.predict_score(features)
        
        # Determine grade
        if score >= 90:
            grade = 'A'
            performance = 'Excellent'
        elif score >= 80:
            grade = 'B'
            performance = 'Good'
        elif score >= 70:
            grade = 'C'
            performance = 'Satisfactory'
        elif score >= 60:
            grade = 'D'
            performance = 'Needs Improvement'
        else:
            grade = 'F'
            performance = 'Unsatisfactory'
        
        return {
            'teacher_id': teacher_id,
            'score': round(score, 2),
            'grade': grade,
            'performance': performance,
            'features': features,
            'shap_values': shap_values,
            'evaluated_at': datetime.utcnow().isoformat(),
            'status': 'success'
        }
    
    def evaluate_all_teachers(self, storage) -> Dict[str, Dict]:
        """
        Evaluate all teachers in the system
        
        Args:
            storage: Storage service instance
        
        Returns:
            Dictionary mapping teacher_id to evaluation results
        """
        # Get all teachers
        teachers = storage.get_all_users(role='teacher')
        
        evaluations = {}
        for teacher_id in teachers.keys():
            evaluation = self.evaluate_teacher(teacher_id, storage)
            evaluations[teacher_id] = evaluation
            
            # Save evaluation
            if evaluation['status'] == 'success':
                storage.save_evaluation(
                    teacher_id=teacher_id,
                    score=evaluation['score'],
                    features=evaluation['features'],
                    shap_values=evaluation.get('shap_values'),
                    grade=evaluation['grade'],
                    performance=evaluation['performance']
                )
        
        return evaluations
    
    def get_feature_importance(self) -> Optional[Dict]:
        """Get feature importance from trained model"""
        if self.model is None:
            return None
        
        if hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
            
            feature_importance = {}
            for i, feature_name in enumerate(self.feature_names):
                feature_importance[feature_name] = float(importances[i])
            
            # Sort by importance
            sorted_features = sorted(
                feature_importance.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            return {
                'feature_importance': feature_importance,
                'top_features': sorted_features
            }
        
        return None


# Singleton instance
_evaluation_service = None

def get_evaluation_service() -> TeacherEvaluationService:
    """Get evaluation service singleton"""
    global _evaluation_service
    if _evaluation_service is None:
        _evaluation_service = TeacherEvaluationService()
    return _evaluation_service
