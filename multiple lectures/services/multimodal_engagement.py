"""
Multimodal Engagement Scorer
Combines facial features with behavioral signals for improved accuracy
"""

import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import deque


class MultimodalEngagementScorer:
    """
    Combines multiple modalities for engagement detection:
    1. Facial features (OpenFace AUs, gaze, head pose)
    2. Behavioral signals (keyboard, mouse, scrolling)
    3. Video interaction (play/pause, seek, speed)
    4. Content interaction (quiz answers, notes)
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        # Weights for different modalities
        self.weights = {
            'facial': 0.50,          # 50%: Facial engagement
            'behavioral': 0.25,      # 25%: Behavioral signals
            'interaction': 0.15,     # 15%: Content interaction
            'temporal': 0.10         # 10%: Temporal consistency
        }
        
        # Activity tracking windows
        self.keyboard_window = deque(maxlen=60)    # Last 60 seconds
        self.mouse_window = deque(maxlen=60)       # Last 60 seconds
        self.scroll_window = deque(maxlen=30)      # Last 30 seconds
        self.interaction_window = deque(maxlen=120) # Last 2 minutes
        
        # Temporal smoothing
        self.engagement_history = deque(maxlen=10)  # Last 10 scores
        
        # Normalization parameters
        self.norm_params = {
            'keystrokes_per_min': 60,   # Active note-taking
            'mouse_events_per_min': 100, # Active interaction
            'scroll_events_per_min': 20, # Reading materials
            'video_controls_per_min': 5  # Normal interaction
        }
    
    def update_keyboard_activity(self, timestamp: datetime, keystrokes: int = 1):
        """Record keyboard activity"""
        self.keyboard_window.append({
            'timestamp': timestamp,
            'keystrokes': keystrokes
        })
    
    def update_mouse_activity(self, timestamp: datetime, event_type: str):
        """Record mouse activity (click, move, scroll)"""
        self.mouse_window.append({
            'timestamp': timestamp,
            'event_type': event_type
        })
    
    def update_scroll_activity(self, timestamp: datetime, scroll_delta: int):
        """Record scroll activity"""
        self.scroll_window.append({
            'timestamp': timestamp,
            'scroll_delta': scroll_delta
        })
    
    def update_interaction(self, timestamp: datetime, interaction_type: str, metadata: Dict = None):
        """
        Record content interaction
        Types: video_play, video_pause, video_seek, quiz_answer, note_taken
        """
        self.interaction_window.append({
            'timestamp': timestamp,
            'type': interaction_type,
            'metadata': metadata or {}
        })
    
    def compute_behavioral_score(self) -> float:
        """
        Compute engagement score from behavioral signals
        High activity = high engagement
        """
        now = datetime.now()
        
        # Calculate activities per minute
        keyboard_rate = self._calculate_rate(self.keyboard_window, now, window_seconds=60)
        mouse_rate = self._calculate_rate(self.mouse_window, now, window_seconds=60)
        scroll_rate = self._calculate_rate(self.scroll_window, now, window_seconds=30)
        
        # Normalize to 0-1 scale
        keyboard_score = min(1.0, keyboard_rate / self.norm_params['keystrokes_per_min'])
        mouse_score = min(1.0, mouse_rate / self.norm_params['mouse_events_per_min'])
        scroll_score = min(1.0, scroll_rate / self.norm_params['scroll_events_per_min'])
        
        # Weight different activities
        behavioral_score = (
            keyboard_score * 0.40 +   # Note-taking is highly indicative
            mouse_score * 0.35 +      # Active interaction
            scroll_score * 0.25       # Reading/reviewing
        )
        
        return behavioral_score
    
    def compute_interaction_score(self) -> float:
        """
        Compute engagement score from content interactions
        Appropriate interactions = high engagement
        """
        now = datetime.now()
        recent_interactions = [
            i for i in self.interaction_window
            if (now - i['timestamp']).total_seconds() <= 120  # Last 2 minutes
        ]
        
        if not recent_interactions:
            return 0.5  # Neutral score if no interactions
        
        # Analyze interaction patterns
        interaction_types = {}
        for interaction in recent_interactions:
            itype = interaction['type']
            interaction_types[itype] = interaction_types.get(itype, 0) + 1
        
        # Positive interactions
        positive_score = 0.0
        if 'quiz_answer' in interaction_types:
            positive_score += 0.4 * min(1.0, interaction_types['quiz_answer'] / 5)
        if 'note_taken' in interaction_types:
            positive_score += 0.3 * min(1.0, interaction_types['note_taken'] / 3)
        if 'video_seek' in interaction_types:
            # Seeking = reviewing (positive if not excessive)
            seek_rate = interaction_types['video_seek'] / 2.0
            if seek_rate < 5:  # Less than 5 seeks per 2 min
                positive_score += 0.2 * min(1.0, seek_rate / 3)
        
        # Neutral interactions
        neutral_score = 0.0
        if 'video_play' in interaction_types or 'video_pause' in interaction_types:
            # Some pausing is okay
            pause_rate = interaction_types.get('video_pause', 0) / 2.0
            if pause_rate < 3:  # Less than 3 pauses per 2 min
                neutral_score += 0.1
        
        interaction_score = min(1.0, positive_score + neutral_score)
        
        return interaction_score
    
    def compute_temporal_score(self, facial_score: float) -> float:
        """
        Compute temporal consistency score
        Smooth engagement = more reliable than spiky engagement
        """
        self.engagement_history.append(facial_score)
        
        if len(self.engagement_history) < 3:
            return facial_score  # Not enough history
        
        # Calculate variance in recent scores
        scores = np.array(self.engagement_history)
        mean_score = np.mean(scores)
        std_score = np.std(scores)
        
        # Lower variance = more consistent = higher confidence
        consistency = max(0, 1 - (std_score / 0.3))  # Penalize high variance
        
        # Weighted combination: favor consistent high engagement
        temporal_score = mean_score * (0.7 + 0.3 * consistency)
        
        return temporal_score
    
    def compute_multimodal_engagement(self, facial_engagement: float, 
                                     current_activity: str = 'lecture') -> Dict:
        """
        Main function: Compute multimodal engagement score
        
        Args:
            facial_engagement: Score from OpenFaceProcessor (0-100)
            current_activity: 'lecture', 'quiz', 'reading', 'assignment'
        
        Returns:
            Dictionary with scores and breakdown
        """
        
        # Normalize facial score to 0-1
        facial_score = facial_engagement / 100.0
        
        # Compute other modality scores
        behavioral_score = self.compute_behavioral_score()
        interaction_score = self.compute_interaction_score()
        temporal_score = self.compute_temporal_score(facial_score)
        
        # Adjust weights based on activity type
        adjusted_weights = self._adjust_weights_for_activity(current_activity)
        
        # Combine scores
        final_score = (
            facial_score * adjusted_weights['facial'] +
            behavioral_score * adjusted_weights['behavioral'] +
            interaction_score * adjusted_weights['interaction'] +
            temporal_score * adjusted_weights['temporal']
        )
        
        # Scale to 0-100
        final_score = final_score * 100
        
        # Confidence level based on data availability
        confidence = self._calculate_confidence()
        
        return {
            'engagement_score': round(final_score, 2),
            'confidence': round(confidence, 2),
            'breakdown': {
                'facial': round(facial_score * 100, 2),
                'behavioral': round(behavioral_score * 100, 2),
                'interaction': round(interaction_score * 100, 2),
                'temporal': round(temporal_score * 100, 2)
            },
            'weights': adjusted_weights,
            'activity_type': current_activity
        }
    
    def _adjust_weights_for_activity(self, activity: str) -> Dict[str, float]:
        """
        Adjust modality weights based on activity type
        Different activities have different engagement signals
        """
        if activity == 'lecture':
            # Lecture: facial > behavioral > interaction
            return {
                'facial': 0.50,
                'behavioral': 0.25,
                'interaction': 0.15,
                'temporal': 0.10
            }
        
        elif activity == 'quiz':
            # Quiz: interaction > facial > behavioral
            return {
                'facial': 0.35,
                'behavioral': 0.15,
                'interaction': 0.40,
                'temporal': 0.10
            }
        
        elif activity == 'reading':
            # Reading: behavioral > facial > interaction
            return {
                'facial': 0.30,
                'behavioral': 0.45,
                'interaction': 0.15,
                'temporal': 0.10
            }
        
        elif activity == 'assignment':
            # Assignment: behavioral > interaction > facial
            return {
                'facial': 0.25,
                'behavioral': 0.45,
                'interaction': 0.20,
                'temporal': 0.10
            }
        
        else:
            # Default weights
            return self.weights
    
    def _calculate_rate(self, activity_window: deque, current_time: datetime, 
                       window_seconds: int) -> float:
        """Calculate activity rate (events per minute)"""
        cutoff_time = current_time - timedelta(seconds=window_seconds)
        
        recent_activities = [
            a for a in activity_window
            if a['timestamp'] >= cutoff_time
        ]
        
        if not recent_activities:
            return 0.0
        
        # Count events
        event_count = sum(a.get('keystrokes', 1) for a in recent_activities)
        
        # Calculate rate per minute
        rate_per_minute = (event_count / window_seconds) * 60
        
        return rate_per_minute
    
    def _calculate_confidence(self) -> float:
        """
        Calculate confidence in the engagement score
        Higher confidence when more data available
        """
        confidence_factors = []
        
        # Factor 1: Facial data availability (from engagement history)
        if len(self.engagement_history) >= 5:
            confidence_factors.append(1.0)
        else:
            confidence_factors.append(len(self.engagement_history) / 5.0)
        
        # Factor 2: Behavioral data availability
        behavioral_data_points = len(self.keyboard_window) + len(self.mouse_window)
        confidence_factors.append(min(1.0, behavioral_data_points / 30))
        
        # Factor 3: Interaction data availability
        confidence_factors.append(min(1.0, len(self.interaction_window) / 10))
        
        # Average confidence
        confidence = np.mean(confidence_factors) * 100
        
        return confidence
    
    def get_engagement_status(self, score: float) -> Dict:
        """
        Get engagement status and recommendations
        """
        if score >= 80:
            status = "Highly Engaged"
            color = "green"
            icon = "🟢"
            message = "Excellent focus! Keep up the great work."
        elif score >= 60:
            status = "Engaged"
            color = "lightgreen"
            icon = "🟡"
            message = "Good engagement. Stay focused."
        elif score >= 40:
            status = "Moderately Engaged"
            color = "yellow"
            icon = "🟠"
            message = "Try to focus more. Take notes to stay engaged."
        elif score >= 20:
            status = "Low Engagement"
            color = "orange"
            icon = "🔴"
            message = "Attention dropping. Consider taking a short break."
        else:
            status = "Disengaged"
            color = "red"
            icon = "⚠️"
            message = "Very low engagement. Take a break and return refreshed."
        
        return {
            'status': status,
            'color': color,
            'icon': icon,
            'message': message,
            'score': score
        }
    
    def reset(self):
        """Reset all tracking windows"""
        self.keyboard_window.clear()
        self.mouse_window.clear()
        self.scroll_window.clear()
        self.interaction_window.clear()
        self.engagement_history.clear()


def integrate_with_behavioral_logger():
    """
    Example integration with BehavioralLogger
    
    In services/behavioral_logger.py:
    
    from services.multimodal_engagement import MultimodalEngagementScorer
    
    class BehavioralLogger:
        def __init__(self, ...):
            ...
            self.multimodal_scorer = MultimodalEngagementScorer()
        
        def log_keystroke(self):
            timestamp = datetime.now()
            self.multimodal_scorer.update_keyboard_activity(timestamp)
        
        def log_mouse_click(self):
            timestamp = datetime.now()
            self.multimodal_scorer.update_mouse_activity(timestamp, 'click')
        
        def log_video_pause(self):
            timestamp = datetime.now()
            self.multimodal_scorer.update_interaction(timestamp, 'video_pause')
        
        def compute_enhanced_engagement(self, facial_score):
            result = self.multimodal_scorer.compute_multimodal_engagement(
                facial_score, 
                current_activity='lecture'
            )
            return result['engagement_score']
    """
    # Integration example provided in docstring above
    # Implement when integrating with existing EngagementTracker


if __name__ == "__main__":
    # Test multimodal scoring
    scorer = MultimodalEngagementScorer()
    
    # Simulate activity
    now = datetime.now()
    
    # Keyboard activity (note-taking)
    for i in range(5):
        scorer.update_keyboard_activity(now, keystrokes=10)
    
    # Mouse activity
    for i in range(3):
        scorer.update_mouse_activity(now, 'click')
    
    # Content interaction
    scorer.update_interaction(now, 'quiz_answer', {'question_id': 1})
    
    # Compute engagement (with 70% facial score)
    result = scorer.compute_multimodal_engagement(70.0, 'lecture')
    
    print("Multimodal Engagement Score:")
    print(f"Overall: {result['engagement_score']:.2f}")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"\nBreakdown:")
    for modality, score in result['breakdown'].items():
        print(f"  {modality.capitalize()}: {score:.2f}")
    
    status = scorer.get_engagement_status(result['engagement_score'])
    print(f"\nStatus: {status['icon']} {status['status']}")
    print(f"Message: {status['message']}")
