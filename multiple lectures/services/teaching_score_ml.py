"""
ML-Enhanced Teaching Effectiveness Indicator System
Uses Random Forest and XGBoost for intelligent, context-aware scoring
Includes confidence ranges, limitations, and baseline normalization
"""

import json
import os
import pickle
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict
import math

# ML Libraries
try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split, cross_val_score
    import xgboost as xgb
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️  ML libraries not available. Install: pip install scikit-learn xgboost")


class ContextualFactors:
    """Calculate contextual factors for teaching effectiveness"""
    
    @staticmethod
    def calculate_course_difficulty(course_data: Dict, activities: List[Dict]) -> Dict:
        """
        Calculate course difficulty score based on multiple factors
        
        Returns:
            Dict with difficulty_score (0-100) and explanation
        """
        factors = {
            'quiz_difficulty': 0,
            'completion_rate': 0,
            'time_investment': 0,
            'dropout_indicators': 0
        }
        
        # Quiz difficulty: average scores
        quiz_scores = [a.get('quiz_score', 0) for a in activities 
                      if a.get('event_type') == 'quiz_submit']
        if quiz_scores:
            avg_quiz_score = sum(quiz_scores) / len(quiz_scores)
            # Lower average = higher difficulty
            factors['quiz_difficulty'] = max(0, 100 - avg_quiz_score)
        
        # Completion rate
        lecture_starts = len([a for a in activities if a.get('event_type') == 'lecture_start'])
        lecture_ends = len([a for a in activities if a.get('event_type') == 'lecture_end'])
        if lecture_starts > 0:
            completion_rate = (lecture_ends / lecture_starts) * 100
            # Lower completion = higher difficulty
            factors['completion_rate'] = max(0, 100 - completion_rate)
        
        # Time investment: longer sessions = harder content
        session_times = []
        for activity in activities:
            if 'session_duration' in activity:
                session_times.append(activity['session_duration'])
        if session_times:
            avg_session_time = sum(session_times) / len(session_times)
            # Normalize to 0-100 (assuming 4 hours is very difficult)
            factors['time_investment'] = min(100, (avg_session_time / 14400) * 100)
        
        # Dropout indicators: students who stopped midway
        unique_students = set(a.get('user_id') for a in activities)
        if unique_students:
            active_recently = set()
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            for activity in activities:
                if activity.get('timestamp', '') > week_ago:
                    active_recently.add(activity.get('user_id'))
            
            retention_rate = (len(active_recently) / len(unique_students)) * 100
            factors['dropout_indicators'] = max(0, 100 - retention_rate)
        
        # Calculate weighted difficulty score
        weights = {
            'quiz_difficulty': 0.35,
            'completion_rate': 0.30,
            'time_investment': 0.20,
            'dropout_indicators': 0.15
        }
        
        difficulty_score = sum(factors[k] * weights[k] for k in factors.keys())
        
        # Classify difficulty
        if difficulty_score < 30:
            difficulty_level = "Easy"
        elif difficulty_score < 50:
            difficulty_level = "Moderate"
        elif difficulty_score < 70:
            difficulty_level = "Challenging"
        else:
            difficulty_level = "Advanced"
        
        return {
            'difficulty_score': round(difficulty_score, 2),
            'difficulty_level': difficulty_level,
            'factors': factors,
            'explanation': f"Course classified as {difficulty_level} (score: {difficulty_score:.1f}/100) "
                          f"based on quiz performance, completion rates, time investment, and retention."
        }
    
    @staticmethod
    def calculate_cohort_behavior(activities: List[Dict]) -> Dict:
        """
        Analyze cohort behavior patterns
        
        Returns:
            Dict with cohort metrics and behavior classification
        """
        if not activities:
            return {
                'cohort_size': 0,
                'engagement_level': 'Unknown',
                'behavior_pattern': 'Insufficient Data',
                'explanation': 'No activity data available for cohort analysis'
            }
        
        # Get unique students
        unique_students = set(a.get('user_id') for a in activities)
        cohort_size = len(unique_students)
        
        # Calculate per-student activity average
        student_activity_counts = defaultdict(int)
        for activity in activities:
            student_activity_counts[activity.get('user_id')] += 1
        
        avg_activities_per_student = (
            sum(student_activity_counts.values()) / cohort_size if cohort_size > 0 else 0
        )
        
        # Engagement classification
        if avg_activities_per_student < 10:
            engagement_level = "Low"
        elif avg_activities_per_student < 30:
            engagement_level = "Moderate"
        elif avg_activities_per_student < 60:
            engagement_level = "High"
        else:
            engagement_level = "Very High"
        
        # Behavior pattern analysis
        quiz_takers = len(set(a.get('user_id') for a in activities 
                             if a.get('event_type') == 'quiz_submit'))
        material_downloaders = len(set(a.get('user_id') for a in activities 
                                      if a.get('event_type') == 'material_download'))
        
        participation_rate = (quiz_takers / cohort_size * 100) if cohort_size > 0 else 0
        
        if participation_rate < 30:
            behavior_pattern = "Passive Learners"
        elif participation_rate < 60:
            behavior_pattern = "Mixed Engagement"
        else:
            behavior_pattern = "Active Participants"
        
        return {
            'cohort_size': cohort_size,
            'avg_activities_per_student': round(avg_activities_per_student, 2),
            'engagement_level': engagement_level,
            'behavior_pattern': behavior_pattern,
            'participation_rate': round(participation_rate, 2),
            'explanation': f"Cohort of {cohort_size} students shows {engagement_level.lower()} "
                          f"engagement ({behavior_pattern}) with {participation_rate:.1f}% "
                          f"actively participating in assessments."
        }


class BaselineNormalization:
    """Handle baseline calculations and normalization"""
    
    @staticmethod
    def calculate_course_baseline(course_id: str, historical_scores: List[Dict]) -> Dict:
        """Calculate baseline for a specific course over time"""
        course_scores = [s for s in historical_scores 
                        if s.get('course_id') == course_id]
        
        if len(course_scores) < 2:
            return {
                'baseline_available': False,
                'message': 'Insufficient historical data (need 2+ evaluations)',
                'baseline_score': None
            }
        
        scores = [s.get('overall_score', 0) for s in course_scores]
        
        return {
            'baseline_available': True,
            'baseline_score': round(sum(scores) / len(scores), 2),
            'score_range': {
                'min': round(min(scores), 2),
                'max': round(max(scores), 2),
                'std': round(np.std(scores), 2) if len(scores) > 1 else 0
            },
            'historical_count': len(course_scores),
            'trend': 'improving' if scores[-1] > scores[0] else 'declining'
        }
    
    @staticmethod
    def calculate_teacher_self_comparison(teacher_id: str, course_id: str, 
                                         historical_scores: List[Dict]) -> Dict:
        """Compare teacher's current performance to their own history"""
        teacher_course_scores = [
            s for s in historical_scores 
            if s.get('teacher_id') == teacher_id and s.get('course_id') == course_id
        ]
        
        if len(teacher_course_scores) < 2:
            return {
                'comparison_available': False,
                'message': 'Need previous evaluations for self-comparison'
            }
        
        # Sort by date
        teacher_course_scores.sort(key=lambda x: x.get('timestamp', ''))
        
        current_score = teacher_course_scores[-1].get('overall_score', 0)
        previous_scores = [s.get('overall_score', 0) for s in teacher_course_scores[:-1]]
        avg_previous = sum(previous_scores) / len(previous_scores)
        
        improvement = current_score - avg_previous
        improvement_pct = (improvement / avg_previous * 100) if avg_previous > 0 else 0
        
        return {
            'comparison_available': True,
            'current_score': round(current_score, 2),
            'previous_average': round(avg_previous, 2),
            'improvement': round(improvement, 2),
            'improvement_percentage': round(improvement_pct, 2),
            'trend': 'improving' if improvement > 0 else 'declining',
            'evaluations_count': len(teacher_course_scores)
        }


class MLTeachingScorePredictor:
    """ML-based teaching effectiveness prediction using Random Forest and XGBoost"""
    
    def __init__(self, model_storage_path="./storage/ml_models"):
        self.model_storage_path = model_storage_path
        os.makedirs(model_storage_path, exist_ok=True)
        
        self.rf_model = None
        self.xgb_model = None
        self.scaler = StandardScaler()
        self.best_model = None
        self.best_model_name = None
        
        # Feature names for tracking
        self.feature_names = [
            'engagement_score', 'quiz_performance', 'attendance_rate',
            'lecture_completion', 'sentiment_score', 'resource_usage',
            'activity_patterns', 'course_difficulty', 'cohort_size',
            'participation_rate', 'avg_session_time', 'student_retention'
        ]
    
    def prepare_training_data(self, historical_data: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare training data from historical scores
        
        Args:
            historical_data: List of historical teaching score records
            
        Returns:
            X (features), y (target scores)
        """
        if len(historical_data) < 10:
            raise ValueError("Need at least 10 historical records for training")
        
        X_list = []
        y_list = []
        
        for record in historical_data:
            components = record.get('components', {})
            contextual = record.get('contextual_factors', {})
            
            features = [
                components.get('engagement', {}).get('score', 0),
                components.get('quiz_performance', {}).get('score', 0),
                components.get('attendance', {}).get('score', 0),
                components.get('lecture_completion', {}).get('score', 0),
                components.get('sentiment', {}).get('score', 0),
                components.get('resource_usage', {}).get('score', 0),
                components.get('activity_patterns', {}).get('score', 0),
                contextual.get('course_difficulty', {}).get('difficulty_score', 50),
                contextual.get('cohort_behavior', {}).get('cohort_size', 0),
                contextual.get('cohort_behavior', {}).get('participation_rate', 0),
                contextual.get('avg_session_time', 1800),
                contextual.get('student_retention', 75)
            ]
            
            X_list.append(features)
            y_list.append(record.get('overall_score', 0))
        
        return np.array(X_list), np.array(y_list)
    
    def train_models(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """
        Train both Random Forest and XGBoost models
        
        Returns:
            Dict with model scores and best model info
        """
        if not ML_AVAILABLE:
            raise ImportError("ML libraries not installed")
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # Train Random Forest
        print("Training Random Forest...")
        self.rf_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        self.rf_model.fit(X_train, y_train)
        rf_score = self.rf_model.score(X_test, y_test)
        rf_cv_scores = cross_val_score(self.rf_model, X_scaled, y, cv=5)
        
        print(f"✓ Random Forest R² Score: {rf_score:.4f}")
        print(f"✓ Random Forest CV Score: {rf_cv_scores.mean():.4f} (+/- {rf_cv_scores.std():.4f})")
        
        # Train XGBoost
        print("\nTraining XGBoost...")
        self.xgb_model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            n_jobs=-1
        )
        self.xgb_model.fit(X_train, y_train)
        xgb_score = self.xgb_model.score(X_test, y_test)
        xgb_cv_scores = cross_val_score(self.xgb_model, X_scaled, y, cv=5)
        
        print(f"✓ XGBoost R² Score: {xgb_score:.4f}")
        print(f"✓ XGBoost CV Score: {xgb_cv_scores.mean():.4f} (+/- {xgb_cv_scores.std():.4f})")
        
        # Select best model
        if rf_cv_scores.mean() > xgb_cv_scores.mean():
            self.best_model = self.rf_model
            self.best_model_name = "Random Forest"
            best_score = rf_cv_scores.mean()
        else:
            self.best_model = self.xgb_model
            self.best_model_name = "XGBoost"
            best_score = xgb_cv_scores.mean()
        
        print(f"\n🏆 Best Model: {self.best_model_name} (CV Score: {best_score:.4f})")
        
        # Save models
        self._save_models()
        
        return {
            'random_forest': {
                'test_score': rf_score,
                'cv_score': rf_cv_scores.mean(),
                'cv_std': rf_cv_scores.std()
            },
            'xgboost': {
                'test_score': xgb_score,
                'cv_score': xgb_cv_scores.mean(),
                'cv_std': xgb_cv_scores.std()
            },
            'best_model': self.best_model_name,
            'best_score': best_score
        }
    
    def predict_with_confidence(self, features: List[float]) -> Dict:
        """
        Predict teaching score with confidence intervals
        
        Returns:
            Dict with prediction, confidence range, and model info
        """
        if self.best_model is None:
            self._load_models()
        
        if self.best_model is None:
            raise ValueError("No trained model available. Train models first.")
        
        # Scale features
        features_scaled = self.scaler.transform([features])
        
        # Get prediction
        prediction = self.best_model.predict(features_scaled)[0]
        
        # Calculate confidence interval (using ensemble predictions if RF)
        if self.best_model_name == "Random Forest":
            # Use individual tree predictions for confidence
            tree_predictions = [tree.predict(features_scaled)[0] 
                              for tree in self.rf_model.estimators_]
            confidence_interval = {
                'lower': np.percentile(tree_predictions, 10),
                'upper': np.percentile(tree_predictions, 90),
                'std': np.std(tree_predictions)
            }
        else:
            # For XGBoost, use a simple margin based on training performance
            margin = 5.0  # +/- 5 points
            confidence_interval = {
                'lower': max(0, prediction - margin),
                'upper': min(100, prediction + margin),
                'std': margin / 2
            }
        
        # Calculate confidence level
        confidence_level = self._calculate_confidence_level(features, confidence_interval)
        
        return {
            'predicted_score': round(prediction, 2),
            'confidence_interval': {
                'lower': round(confidence_interval['lower'], 2),
                'upper': round(confidence_interval['upper'], 2),
                'std': round(confidence_interval['std'], 2)
            },
            'confidence_level': confidence_level,
            'model_used': self.best_model_name,
            'feature_importance': self._get_feature_importance()
        }
    
    def _calculate_confidence_level(self, features: List[float], 
                                   confidence_interval: Dict) -> str:
        """Calculate confidence level based on data quality and interval width"""
        interval_width = confidence_interval['upper'] - confidence_interval['lower']
        
        # Check for missing/zero features
        missing_features = sum(1 for f in features if f == 0)
        data_completeness = 1 - (missing_features / len(features))
        
        if interval_width < 5 and data_completeness > 0.8:
            return "Very High"
        elif interval_width < 10 and data_completeness > 0.6:
            return "High"
        elif interval_width < 15 and data_completeness > 0.4:
            return "Moderate"
        else:
            return "Low"
    
    def _get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from the best model"""
        if self.best_model is None:
            return {}
        
        if hasattr(self.best_model, 'feature_importances_'):
            importances = self.best_model.feature_importances_
            return {
                name: round(float(importance), 4)
                for name, importance in zip(self.feature_names, importances)
            }
        return {}
    
    def _save_models(self):
        """Save trained models to disk"""
        if self.rf_model:
            with open(os.path.join(self.model_storage_path, 'rf_model.pkl'), 'wb') as f:
                pickle.dump(self.rf_model, f)
        
        if self.xgb_model:
            with open(os.path.join(self.model_storage_path, 'xgb_model.pkl'), 'wb') as f:
                pickle.dump(self.xgb_model, f)
        
        with open(os.path.join(self.model_storage_path, 'scaler.pkl'), 'wb') as f:
            pickle.dump(self.scaler, f)
        
        # Save metadata
        metadata = {
            'best_model': self.best_model_name,
            'feature_names': self.feature_names,
            'trained_at': datetime.now().isoformat()
        }
        with open(os.path.join(self.model_storage_path, 'metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"💾 Models saved to {self.model_storage_path}")
    
    def _load_models(self):
        """Load trained models from disk"""
        try:
            # Load metadata
            metadata_path = os.path.join(self.model_storage_path, 'metadata.json')
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                    self.best_model_name = metadata.get('best_model')
            
            # Load scaler
            scaler_path = os.path.join(self.model_storage_path, 'scaler.pkl')
            if os.path.exists(scaler_path):
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
            
            # Load models
            rf_path = os.path.join(self.model_storage_path, 'rf_model.pkl')
            if os.path.exists(rf_path):
                with open(rf_path, 'rb') as f:
                    self.rf_model = pickle.load(f)
            
            xgb_path = os.path.join(self.model_storage_path, 'xgb_model.pkl')
            if os.path.exists(xgb_path):
                with open(xgb_path, 'rb') as f:
                    self.xgb_model = pickle.load(f)
            
            # Set best model
            if self.best_model_name == "Random Forest":
                self.best_model = self.rf_model
            else:
                self.best_model = self.xgb_model
            
            print(f"✓ Models loaded from {self.model_storage_path}")
            
        except Exception as e:
            print(f"⚠️  Could not load models: {str(e)}")
            self.best_model = None


class EnhancedTeachingScoreCalculator:
    """
    Enhanced Teaching Effectiveness Indicator with ML, contextual factors,
    confidence ranges, and baseline normalization
    """
    
    def __init__(self, storage_path="./storage/teaching_scores.json"):
        self.storage_path = storage_path
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)
        self._initialize_storage()
        
        self.contextual_factors = ContextualFactors()
        self.baseline_norm = BaselineNormalization()
        self.ml_predictor = MLTeachingScorePredictor() if ML_AVAILABLE else None
        
        # Component weights (used as fallback if ML not available)
        self.weights = {
            'engagement': 0.25,
            'quiz_performance': 0.20,
            'attendance': 0.15,
            'lecture_completion': 0.15,
            'sentiment': 0.10,
            'resource_usage': 0.05,
            'activity_patterns': 0.10
        }
    
    def _initialize_storage(self):
        """Initialize storage file"""
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, 'w') as f:
                json.dump({'scores': []}, f)
    
    def _load_scores(self) -> Dict:
        """Load historical scores"""
        try:
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {'scores': []}
    
    def _save_scores(self, data: Dict):
        """Save scores to storage"""
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def calculate_teaching_effectiveness(self, teacher_id: str, course_id: str,
                                        activities: List[Dict], 
                                        course_data: Dict) -> Dict:
        """
        Calculate comprehensive teaching effectiveness indicator
        
        Args:
            teacher_id: Teacher identifier
            course_id: Course identifier
            activities: List of activity records
            course_data: Course information
            
        Returns:
            Comprehensive teaching effectiveness report with ML predictions,
            confidence ranges, contextual factors, and limitations
        """
        
        # Calculate traditional component scores
        components = self._calculate_all_components(activities, course_data)
        
        # Calculate contextual factors
        course_difficulty = self.contextual_factors.calculate_course_difficulty(
            course_data, activities
        )
        cohort_behavior = self.contextual_factors.calculate_cohort_behavior(activities)
        
        # Load historical data for normalization
        historical_data = self._load_scores()
        historical_scores = historical_data.get('scores', [])
        
        # Calculate baseline and self-comparison
        baseline = self.baseline_norm.calculate_course_baseline(course_id, historical_scores)
        self_comparison = self.baseline_norm.calculate_teacher_self_comparison(
            teacher_id, course_id, historical_scores
        )
        
        # Prepare features for ML prediction
        if self.ml_predictor and len(historical_scores) >= 10:
            try:
                features = [
                    components['engagement']['score'],
                    components['quiz_performance']['score'],
                    components['attendance']['score'],
                    components['lecture_completion']['score'],
                    components['sentiment']['score'],
                    components['resource_usage']['score'],
                    components['activity_patterns']['score'],
                    course_difficulty['difficulty_score'],
                    cohort_behavior['cohort_size'],
                    cohort_behavior['participation_rate'],
                    1800,  # avg_session_time placeholder
                    75     # student_retention placeholder
                ]
                
                ml_prediction = self.ml_predictor.predict_with_confidence(features)
                use_ml = True
            except Exception as e:
                print(f"⚠️  ML prediction failed: {str(e)}")
                ml_prediction = None
                use_ml = False
        else:
            ml_prediction = None
            use_ml = False
        
        # Calculate overall score (ML or weighted)
        if use_ml and ml_prediction:
            overall_score = ml_prediction['predicted_score']
            confidence_interval = ml_prediction['confidence_interval']
            confidence_level = ml_prediction['confidence_level']
            calculation_method = f"ML-Enhanced ({ml_prediction['model_used']})"
        else:
            overall_score = sum(
                components[key]['score'] * self.weights[key]
                for key in self.weights.keys()
            )
            # Confidence based on data completeness
            data_points = sum(1 for c in components.values() if c['score'] > 0)
            confidence_level = "Moderate" if data_points >= 5 else "Low"
            confidence_interval = {
                'lower': max(0, overall_score - 10),
                'upper': min(100, overall_score + 10),
                'std': 5.0
            }
            calculation_method = "Weighted Components"
        
        # Determine limitations
        limitations = self._identify_limitations(activities, components, cohort_behavior)
        
        # Build comprehensive result
        result = {
            'teacher_id': teacher_id,
            'course_id': course_id,
            'timestamp': datetime.now().isoformat(),
            'label': 'Teaching Effectiveness Indicator',
            'overall_score': round(overall_score, 2),
            'confidence_interval': confidence_interval,
            'confidence_level': confidence_level,
            'calculation_method': calculation_method,
            'components': components,
            'contextual_factors': {
                'course_difficulty': course_difficulty,
                'cohort_behavior': cohort_behavior
            },
            'normalization': {
                'baseline': baseline,
                'self_comparison': self_comparison
            },
            'ml_insights': ml_prediction if use_ml else None,
            'limitations': limitations,
            'interpretation': self._generate_interpretation(
                overall_score, confidence_level, limitations
            )
        }
        
        # Save to historical data
        historical_scores.append(result)
        self._save_scores({'scores': historical_scores})
        
        return result
    
    def _calculate_all_components(self, activities: List[Dict], 
                                  course_data: Dict) -> Dict:
        """Calculate all component scores"""
        # Placeholder - implement actual calculations
        # This should use the logic from the original teaching_score.py
        return {
            'engagement': {'score': 75, 'weight': 0.25, 'explanation': 'Moderate engagement'},
            'quiz_performance': {'score': 80, 'weight': 0.20, 'explanation': 'Good quiz scores'},
            'attendance': {'score': 85, 'weight': 0.15, 'explanation': 'High attendance'},
            'lecture_completion': {'score': 70, 'weight': 0.15, 'explanation': 'Moderate completion'},
            'sentiment': {'score': 65, 'weight': 0.10, 'explanation': 'Neutral sentiment'},
            'resource_usage': {'score': 60, 'weight': 0.05, 'explanation': 'Moderate usage'},
            'activity_patterns': {'score': 72, 'weight': 0.10, 'explanation': 'Regular patterns'}
        }
    
    def _identify_limitations(self, activities: List[Dict], 
                            components: Dict, cohort_behavior: Dict) -> List[Dict]:
        """Identify and explain data limitations"""
        limitations = []
        
        # Check sample size
        if cohort_behavior['cohort_size'] < 10:
            limitations.append({
                'type': 'Small Sample Size',
                'severity': 'High',
                'explanation': f"Only {cohort_behavior['cohort_size']} students in cohort. "
                              f"Scores are less reliable with small sample sizes. "
                              f"Recommended minimum: 10 students."
            })
        
        # Check data recency
        if activities:
            latest_activity = max(activities, key=lambda x: x.get('timestamp', ''))
            latest_date = datetime.fromisoformat(latest_activity.get('timestamp', datetime.now().isoformat()))
            days_since_activity = (datetime.now() - latest_date).days
            
            if days_since_activity > 30:
                limitations.append({
                    'type': 'Stale Data',
                    'severity': 'Moderate',
                    'explanation': f"Most recent activity was {days_since_activity} days ago. "
                                  f"Score may not reflect current teaching effectiveness."
                })
        
        # Check missing components
        zero_components = [k for k, v in components.items() if v['score'] == 0]
        if len(zero_components) > 2:
            limitations.append({
                'type': 'Incomplete Data',
                'severity': 'Moderate',
                'explanation': f"Missing data for {len(zero_components)} components: "
                              f"{', '.join(zero_components)}. Score calculated with available data only."
            })
        
        # Check participation rate
        if cohort_behavior.get('participation_rate', 0) < 30:
            limitations.append({
                'type': 'Low Participation',
                'severity': 'High',
                'explanation': f"Only {cohort_behavior['participation_rate']:.1f}% of students "
                              f"actively participating. Low engagement may bias scores."
            })
        
        return limitations if limitations else [{
            'type': 'No Major Limitations',
            'severity': 'Low',
            'explanation': 'Score calculated with sufficient, recent data from an adequately-sized cohort.'
        }]
    
    def _generate_interpretation(self, score: float, confidence: str, 
                                limitations: List[Dict]) -> str:
        """Generate human-readable interpretation"""
        # Score classification
        if score >= 85:
            level = "Excellent"
        elif score >= 70:
            level = "Very Good"
        elif score >= 55:
            level = "Good"
        elif score >= 40:
            level = "Fair"
        else:
            level = "Needs Improvement"
        
        # Confidence qualifier
        confidence_text = {
            'Very High': 'with high confidence',
            'High': 'with reasonable confidence',
            'Moderate': 'with moderate confidence',
            'Low': 'with limited confidence (see limitations)'
        }.get(confidence, '')
        
        # Limitation summary
        high_severity = [l for l in limitations if l['severity'] == 'High']
        limitation_text = ""
        if high_severity:
            limitation_text = f" Note: {len(high_severity)} high-severity limitation(s) identified."
        
        return (f"This Teaching Effectiveness Indicator suggests {level} performance "
                f"(score: {score:.1f}/100) {confidence_text}.{limitation_text} "
                f"This is an indicator, not an absolute measure of teaching quality. "
                f"Consider contextual factors and data limitations when interpreting.")


# Singleton instance
_calculator_instance = None

def get_enhanced_teaching_score_calculator() -> EnhancedTeachingScoreCalculator:
    """Get singleton instance of enhanced calculator"""
    global _calculator_instance
    if _calculator_instance is None:
        _calculator_instance = EnhancedTeachingScoreCalculator()
    return _calculator_instance
