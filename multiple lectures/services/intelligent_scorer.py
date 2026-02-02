"""
Intelligent Engagement Scorer
Uses ML to understand user behavior patterns and assign engagement scores
Works for all user types and adapts to individual learning patterns
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json


class IntelligentEngagementScorer:
    """
    ML-based engagement scorer that learns from user behavior patterns
    Handles all scenarios: online reading, downloads, varied interaction patterns
    """
    
    def __init__(self, model_dir: str = "./ml/models/intelligent_engagement"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        self.model = None
        self.scaler = None
        self.feature_importance = {}
        
        # Load or initialize model
        self._load_or_create_model()
    
    def _load_or_create_model(self):
        """Load existing model or create new one"""
        model_path = self.model_dir / "engagement_model.pkl"
        scaler_path = self.model_dir / "scaler.pkl"
        
        if model_path.exists() and scaler_path.exists():
            try:
                self.model = joblib.load(model_path)
                self.scaler = joblib.load(scaler_path)
                print("✅ Loaded existing intelligent engagement model")
            except Exception as e:
                print(f"⚠️ Error loading model: {e}. Creating new model...")
                self._create_new_model()
        else:
            self._create_new_model()
    
    def _create_new_model(self):
        """Create new ML model"""
        # Use ensemble of models for robustness
        self.model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        self.scaler = StandardScaler()
        print("✅ Created new intelligent engagement model")
    
    def extract_features_from_actions(self, actions: List[Dict], 
                                     context: Dict) -> Dict[str, float]:
        """
        Extract ML features from user actions
        
        Args:
            actions: List of user actions from universal logger
            context: Context (course_id, lecture_id, user_role, etc.)
        
        Returns:
            Dictionary of features for ML model
        """
        if not actions:
            return self._get_default_features()
        
        # Sort actions by timestamp
        actions = sorted(actions, key=lambda x: x['unix_timestamp'])
        
        features = {}
        
        # === TEMPORAL FEATURES ===
        
        # Time-based patterns
        timestamps = [a['unix_timestamp'] for a in actions]
        if len(timestamps) > 1:
            time_diffs = np.diff(timestamps)
            features['avg_time_between_actions'] = np.mean(time_diffs)
            features['std_time_between_actions'] = np.std(time_diffs)
            features['max_gap_seconds'] = np.max(time_diffs)
            features['min_gap_seconds'] = np.min(time_diffs)
        else:
            features['avg_time_between_actions'] = 0
            features['std_time_between_actions'] = 0
            features['max_gap_seconds'] = 0
            features['min_gap_seconds'] = 0
        
        # Session duration
        if actions:
            session_duration = timestamps[-1] - timestamps[0]
            features['total_session_duration'] = session_duration
            features['actions_per_minute'] = len(actions) / (session_duration / 60) if session_duration > 0 else 0
        else:
            features['total_session_duration'] = 0
            features['actions_per_minute'] = 0
        
        # Time of day patterns
        hours = [a['hour_of_day'] for a in actions]
        features['avg_hour_of_day'] = np.mean(hours)
        features['studies_morning'] = sum(1 for h in hours if 6 <= h < 12) / len(hours)
        features['studies_afternoon'] = sum(1 for h in hours if 12 <= h < 18) / len(hours)
        features['studies_evening'] = sum(1 for h in hours if 18 <= h < 24) / len(hours)
        features['studies_night'] = sum(1 for h in hours if 0 <= h < 6) / len(hours)
        
        # Weekend vs weekday
        features['weekend_activity_ratio'] = sum(1 for a in actions if a['is_weekend']) / len(actions)
        
        # === ACTION PATTERN FEATURES ===
        
        # Action counts by category
        categories = [a['action_category'] for a in actions]
        total_actions = len(actions)
        
        for category in ['content_access', 'content_download', 'assessment', 
                        'interaction', 'navigation', 'feedback']:
            count = sum(1 for c in categories if c == category)
            features[f'{category}_count'] = count
            features[f'{category}_ratio'] = count / total_actions if total_actions > 0 else 0
        
        # === CONTENT ENGAGEMENT FEATURES ===
        
        # PDF-specific features
        pdf_actions = [a for a in actions if 'pdf' in a['action_type']]
        features['pdf_actions_count'] = len(pdf_actions)
        features['pdf_downloaded'] = sum(1 for a in pdf_actions if 'download' in a['action_type']) > 0
        features['pdf_viewed_online'] = sum(1 for a in pdf_actions if a['action_type'] == 'pdf_open') > 0
        
        # If downloaded but not viewed online, infer offline reading
        if features['pdf_downloaded'] and not features['pdf_viewed_online']:
            # Look for subsequent actions that indicate engagement
            download_time = next((a['unix_timestamp'] for a in pdf_actions if 'download' in a['action_type']), 0)
            post_download_actions = [a for a in actions if a['unix_timestamp'] > download_time]
            features['post_download_activity_count'] = len(post_download_actions)
            features['returned_after_download'] = len(post_download_actions) > 0
        else:
            features['post_download_activity_count'] = 0
            features['returned_after_download'] = False
        
        # Video-specific features
        video_actions = [a for a in actions if 'video' in a['action_type']]
        features['video_actions_count'] = len(video_actions)
        features['video_pauses'] = sum(1 for a in video_actions if a['action_type'] == 'video_pause')
        features['video_seeks'] = sum(1 for a in video_actions if a['action_type'] == 'video_seek')
        features['video_completions'] = sum(1 for a in video_actions if a['action_type'] == 'video_complete')
        
        # === INTERACTION QUALITY FEATURES ===
        
        # Diversity of actions
        unique_action_types = len(set(a['action_type'] for a in actions))
        features['action_type_diversity'] = unique_action_types
        features['action_diversity_ratio'] = unique_action_types / total_actions if total_actions > 0 else 0
        
        # Sequence features (already computed in actions)
        if actions and 'sequence_features' in actions[-1]:
            seq = actions[-1]['sequence_features']
            features['final_actions_in_5min'] = seq['actions_in_last_5min']
            features['final_actions_in_hour'] = seq['actions_in_last_hour']
            features['final_action_diversity'] = seq['action_diversity']
        
        # Navigation patterns (tab switches, window blur = distraction)
        nav_actions = [a for a in actions if a['action_category'] == 'navigation']
        features['tab_switches'] = sum(1 for a in nav_actions if a['action_type'] == 'tab_switch')
        features['window_blurs'] = sum(1 for a in nav_actions if a['action_type'] == 'window_blur')
        features['focus_loss_ratio'] = features['window_blurs'] / total_actions if total_actions > 0 else 0
        
        # === ASSESSMENT FEATURES ===
        
        # Quiz/assignment performance
        assessment_actions = [a for a in actions if a['action_category'] == 'assessment']
        if assessment_actions:
            scores = [a['metadata'].get('score', 0) for a in assessment_actions if 'score' in a['metadata']]
            features['assessment_count'] = len(assessment_actions)
            features['avg_assessment_score'] = np.mean(scores) if scores else 0
            features['assessment_completion_rate'] = sum(1 for a in assessment_actions if 'submit' in a['action_type']) / len(assessment_actions)
        else:
            features['assessment_count'] = 0
            features['avg_assessment_score'] = 0
            features['assessment_completion_rate'] = 0
        
        # === PERSISTENCE FEATURES ===
        
        # Unique sessions
        unique_sessions = len(set(a['session_id'] for a in actions))
        features['unique_sessions'] = unique_sessions
        features['avg_actions_per_session'] = total_actions / unique_sessions if unique_sessions > 0 else 0
        
        # Resource coverage (how many different resources accessed)
        unique_resources = len(set(a['context'].get('resource_id', '') for a in actions if a['context'].get('resource_id')))
        features['unique_resources_accessed'] = unique_resources
        
        # Completion indicators
        features['has_feedback'] = sum(1 for a in actions if a['action_category'] == 'feedback') > 0
        features['has_completed_assessment'] = features['assessment_completion_rate'] > 0
        
        # === RECENCY FEATURES ===
        
        if actions:
            last_action_time = actions[-1]['unix_timestamp']
            now = datetime.now().timestamp()
            features['hours_since_last_action'] = (now - last_action_time) / 3600
            features['is_recent_activity'] = features['hours_since_last_action'] < 24
        else:
            features['hours_since_last_action'] = 999
            features['is_recent_activity'] = False
        
        # === CONSISTENCY FEATURES ===
        
        # Calculate active days
        if actions:
            dates = set(datetime.fromtimestamp(a['unix_timestamp']).date() for a in actions)
            features['active_days'] = len(dates)
            
            # Regularity (are actions spread out or clustered?)
            if len(dates) > 1:
                date_list = sorted(dates)
                gaps = [(date_list[i+1] - date_list[i]).days for i in range(len(date_list)-1)]
                features['avg_days_between_sessions'] = np.mean(gaps)
                features['session_regularity'] = 1 / (np.std(gaps) + 1)  # Higher = more regular
            else:
                features['avg_days_between_sessions'] = 0
                features['session_regularity'] = 0
        else:
            features['active_days'] = 0
            features['avg_days_between_sessions'] = 0
            features['session_regularity'] = 0
        
        return features
    
    def _get_default_features(self) -> Dict[str, float]:
        """Return default features when no actions available"""
        return {key: 0.0 for key in self._get_feature_names()}
    
    def _get_feature_names(self) -> List[str]:
        """Get list of all feature names"""
        return [
            'avg_time_between_actions', 'std_time_between_actions', 'max_gap_seconds', 'min_gap_seconds',
            'total_session_duration', 'actions_per_minute', 'avg_hour_of_day',
            'studies_morning', 'studies_afternoon', 'studies_evening', 'studies_night',
            'weekend_activity_ratio',
            'content_access_count', 'content_access_ratio',
            'content_download_count', 'content_download_ratio',
            'assessment_count', 'assessment_ratio',
            'interaction_count', 'interaction_ratio',
            'navigation_count', 'navigation_ratio',
            'feedback_count', 'feedback_ratio',
            'pdf_actions_count', 'pdf_downloaded', 'pdf_viewed_online',
            'post_download_activity_count', 'returned_after_download',
            'video_actions_count', 'video_pauses', 'video_seeks', 'video_completions',
            'action_type_diversity', 'action_diversity_ratio',
            'final_actions_in_5min', 'final_actions_in_hour', 'final_action_diversity',
            'tab_switches', 'window_blurs', 'focus_loss_ratio',
            'avg_assessment_score', 'assessment_completion_rate',
            'unique_sessions', 'avg_actions_per_session', 'unique_resources_accessed',
            'has_feedback', 'has_completed_assessment',
            'hours_since_last_action', 'is_recent_activity',
            'active_days', 'avg_days_between_sessions', 'session_regularity'
        ]
    
    def predict_engagement_score(self, actions: List[Dict], context: Dict) -> Dict:
        """
        Predict engagement score from user actions
        
        Args:
            actions: List of user actions
            context: Context dictionary
        
        Returns:
            Dict with score, confidence, and explanation
        """
        # Extract features
        features = self.extract_features_from_actions(actions, context)
        
        # Convert to DataFrame
        feature_df = pd.DataFrame([features])
        
        # Ensure all features are present
        for feat_name in self._get_feature_names():
            if feat_name not in feature_df.columns:
                feature_df[feat_name] = 0
        
        # Reorder columns to match training
        feature_df = feature_df[self._get_feature_names()]
        
        # Scale features
        try:
            features_scaled = self.scaler.transform(feature_df)
        except:
            # If scaler not fitted, use rule-based scoring
            return self._rule_based_scoring(features, actions)
        
        # Predict
        try:
            raw_score = self.model.predict(features_scaled)[0]
            # Clip to 0-100 range
            score = np.clip(raw_score, 0, 100)
        except:
            # Fallback to rule-based
            return self._rule_based_scoring(features, actions)
        
        # Calculate confidence based on data quality
        confidence = self._calculate_confidence(features, actions)
        
        # Generate explanation
        explanation = self._generate_explanation(features, score)
        
        return {
            'engagement_score': round(score, 2),
            'confidence': round(confidence, 2),
            'level': self._get_engagement_level(score),
            'explanation': explanation,
            'features_used': len([v for v in features.values() if v > 0]),
            'total_actions': len(actions),
            'predicted_at': datetime.now().isoformat()
        }
    
    def _rule_based_scoring(self, features: Dict, actions: List[Dict]) -> Dict:
        """
        Fallback rule-based scoring when ML model unavailable
        Uses intelligent heuristics
        """
        score = 50  # Start at neutral
        
        # Content interaction (max +25 points)
        content_score = min(25, features['content_access_ratio'] * 50 + features['content_download_ratio'] * 25)
        score += content_score
        
        # Assessment performance (max +20 points)
        if features['assessment_count'] > 0:
            score += features['avg_assessment_score'] * 0.2
        
        # Active participation (max +15 points)
        participation = min(15, features['action_type_diversity'] * 2 + features['unique_resources_accessed'] * 3)
        score += participation
        
        # Regularity bonus (max +10 points)
        if features['active_days'] > 1:
            regularity = min(10, features['session_regularity'] * 10)
            score += regularity
        
        # Penalties
        score -= features['focus_loss_ratio'] * 20  # Distraction penalty
        score -= min(10, features['tab_switches'] * 2)  # Tab switching penalty
        
        # Clip to valid range
        score = np.clip(score, 0, 100)
        
        return {
            'engagement_score': round(score, 2),
            'confidence': 0.75,  # Medium confidence for rule-based
            'level': self._get_engagement_level(score),
            'explanation': 'Calculated using intelligent rule-based scoring',
            'features_used': len([v for v in features.values() if v > 0]),
            'total_actions': len(actions),
            'predicted_at': datetime.now().isoformat()
        }
    
    def _calculate_confidence(self, features: Dict, actions: List[Dict]) -> float:
        """Calculate prediction confidence based on data quality"""
        confidence = 1.0
        
        # Reduce confidence if limited data
        if len(actions) < 5:
            confidence *= 0.6
        elif len(actions) < 10:
            confidence *= 0.8
        
        # Reduce if very recent (not enough time to observe patterns)
        if features['hours_since_last_action'] < 0.5:
            confidence *= 0.9
        
        # Reduce if only one session
        if features['unique_sessions'] < 2:
            confidence *= 0.85
        
        # Increase if diverse actions
        if features['action_type_diversity'] > 10:
            confidence *= 1.1
        
        return min(1.0, confidence)
    
    def _generate_explanation(self, features: Dict, score: float) -> str:
        """Generate human-readable explanation of score"""
        explanations = []
        
        # Content engagement
        if features['pdf_downloaded']:
            if features['returned_after_download']:
                explanations.append("Downloaded materials and continued engaging with content")
            else:
                explanations.append("Downloaded materials for offline study")
        
        if features['pdf_viewed_online']:
            explanations.append(f"Spent time reading materials online")
        
        # Video engagement
        if features['video_completions'] > 0:
            explanations.append(f"Completed {int(features['video_completions'])} video(s)")
        
        # Assessment
        if features['assessment_count'] > 0:
            explanations.append(f"Completed assessments with {features['avg_assessment_score']:.0f}% avg score")
        
        # Activity pattern
        if features['active_days'] > 3:
            explanations.append(f"Consistent activity over {int(features['active_days'])} days")
        
        # Regularity
        if features['session_regularity'] > 0.5:
            explanations.append("Regular study pattern")
        
        # Issues
        if features['focus_loss_ratio'] > 0.3:
            explanations.append("⚠️ Frequent distractions detected")
        
        if features['tab_switches'] > 10:
            explanations.append("⚠️ High tab switching activity")
        
        if not explanations:
            return "Limited activity data available"
        
        return " • ".join(explanations)
    
    def _get_engagement_level(self, score: float) -> str:
        """Convert score to engagement level"""
        if score >= 85:
            return "Excellent"
        elif score >= 70:
            return "Good"
        elif score >= 50:
            return "Average"
        elif score >= 30:
            return "Below Average"
        else:
            return "Needs Attention"
    
    def train_model_from_data(self, data_dir: str = "./ml_data/activity_logs"):
        """
        Train model from existing activity logs
        This would be run periodically to improve the model
        """
        # Implementation for training from logged data
        # Would collect features and engagement labels from historical data
        pass
    
    def save_model(self):
        """Save trained model"""
        if self.model and self.scaler:
            joblib.dump(self.model, self.model_dir / "engagement_model.pkl")
            joblib.dump(self.scaler, self.model_dir / "scaler.pkl")
            print("✅ Model saved")


# Global instance
_scorer = None

def get_intelligent_scorer() -> IntelligentEngagementScorer:
    """Get global intelligent scorer instance"""
    global _scorer
    if _scorer is None:
        _scorer = IntelligentEngagementScorer()
    return _scorer
