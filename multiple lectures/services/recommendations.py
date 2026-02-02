"""
Adaptive Recommendations Service
Provides personalized content recommendations based on user behavior and performance
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import numpy as np


class RecommendationsService:
    """Service for generating adaptive recommendations"""
    
    def __init__(self, storage_path: str):
        """Initialize recommendations service
        
        Args:
            storage_path: Path to storage directory
        """
        self.storage_path = Path(storage_path)
        self.recommendations_file = self.storage_path / "recommendations.json"
        self._ensure_files()
    
    def _ensure_files(self):
        """Ensure recommendation files exist"""
        if not self.recommendations_file.exists():
            self._save_recommendations({})
    
    def _load_recommendations(self) -> Dict:
        """Load recommendations data"""
        with open(self.recommendations_file, 'r') as f:
            return json.load(f)
    
    def _save_recommendations(self, data: Dict):
        """Save recommendations data"""
        with open(self.recommendations_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_json(self, filename: str) -> Dict:
        """Load JSON file from storage"""
        filepath = self.storage_path / filename
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
        return {}
    
    def get_user_learning_profile(self, user_id: str) -> Dict:
        """Build user's learning profile from their activity
        
        Args:
            user_id: User ID
            
        Returns:
            Dict with learning patterns, strengths, and weaknesses
        """
        # Load user data
        grades = self._load_json("grades.json")
        engagement_logs = self._load_json("engagement_logs.json")
        progress = self._load_json("progress.json")
        feedback = self._load_json("feedback.json")
        
        profile = {
            "avg_engagement": 0,
            "avg_quiz_score": 0,
            "strong_topics": [],
            "weak_topics": [],
            "preferred_time": "evening",  # morning, afternoon, evening, night
            "study_pace": "moderate",  # slow, moderate, fast
            "engagement_trend": "stable",  # improving, stable, declining
            "quiz_trend": "stable",
            "completed_courses": [],
            "in_progress_courses": [],
            "struggling_courses": [],
            "last_activity": None
        }
        
        # Calculate average engagement
        user_engagement = [log for log in engagement_logs.get("logs", []) 
                          if log.get("user_id") == user_id]
        if user_engagement:
            scores = [log.get("engagement_score", 0) for log in user_engagement[-10:]]
            profile["avg_engagement"] = sum(scores) / len(scores) if scores else 0
            
            # Detect trend
            if len(scores) >= 5:
                first_half = sum(scores[:len(scores)//2]) / (len(scores)//2)
                second_half = sum(scores[len(scores)//2:]) / (len(scores) - len(scores)//2)
                if second_half > first_half + 10:
                    profile["engagement_trend"] = "improving"
                elif second_half < first_half - 10:
                    profile["engagement_trend"] = "declining"
        
        # Calculate quiz performance
        user_grades = grades.get(user_id, {})
        quiz_scores = []
        topic_scores = defaultdict(list)
        
        for item_id, grade_data in user_grades.items():
            if grade_data.get("type") == "quiz":
                score = grade_data.get("score", 0)
                quiz_scores.append(score)
                
                # Track by topic
                topic = grade_data.get("topic", "general")
                topic_scores[topic].append(score)
        
        if quiz_scores:
            profile["avg_quiz_score"] = sum(quiz_scores) / len(quiz_scores)
            
            # Detect quiz trend
            if len(quiz_scores) >= 5:
                first_half = sum(quiz_scores[:len(quiz_scores)//2]) / (len(quiz_scores)//2)
                second_half = sum(quiz_scores[len(quiz_scores)//2:]) / (len(quiz_scores) - len(quiz_scores)//2)
                if second_half > first_half + 10:
                    profile["quiz_trend"] = "improving"
                elif second_half < first_half - 10:
                    profile["quiz_trend"] = "declining"
        
        # Identify strong and weak topics
        for topic, scores in topic_scores.items():
            avg_score = sum(scores) / len(scores)
            if avg_score >= 80:
                profile["strong_topics"].append({"topic": topic, "score": avg_score})
            elif avg_score < 60:
                profile["weak_topics"].append({"topic": topic, "score": avg_score})
        
        # Sort by score
        profile["strong_topics"].sort(key=lambda x: x["score"], reverse=True)
        profile["weak_topics"].sort(key=lambda x: x["score"])
        
        # Analyze study patterns
        if user_engagement:
            hours = [datetime.fromisoformat(log["timestamp"]).hour 
                    for log in user_engagement if "timestamp" in log]
            if hours:
                avg_hour = sum(hours) / len(hours)
                if avg_hour < 12:
                    profile["preferred_time"] = "morning"
                elif avg_hour < 17:
                    profile["preferred_time"] = "afternoon"
                elif avg_hour < 22:
                    profile["preferred_time"] = "evening"
                else:
                    profile["preferred_time"] = "night"
        
        # Analyze progress
        user_progress = progress.get(user_id, {})
        for course_id, course_progress in user_progress.items():
            completion = course_progress.get("completion_percentage", 0)
            avg_score = course_progress.get("average_score", 0)
            
            if completion >= 100:
                profile["completed_courses"].append(course_id)
            elif completion > 0:
                if avg_score < 50:
                    profile["struggling_courses"].append({
                        "course_id": course_id,
                        "completion": completion,
                        "avg_score": avg_score
                    })
                else:
                    profile["in_progress_courses"].append({
                        "course_id": course_id,
                        "completion": completion
                    })
        
        # Study pace
        if user_progress:
            # Calculate average days per course
            completed_days = []
            for course_id in profile["completed_courses"]:
                course_data = user_progress.get(course_id, {})
                if "started_at" in course_data and "completed_at" in course_data:
                    started = datetime.fromisoformat(course_data["started_at"])
                    completed = datetime.fromisoformat(course_data["completed_at"])
                    days = (completed - started).days
                    completed_days.append(days)
            
            if completed_days:
                avg_days = sum(completed_days) / len(completed_days)
                if avg_days < 14:
                    profile["study_pace"] = "fast"
                elif avg_days > 30:
                    profile["study_pace"] = "slow"
        
        # Last activity
        if user_engagement:
            profile["last_activity"] = user_engagement[-1].get("timestamp")
        
        return profile
    
    def recommend_next_lecture(self, user_id: str, course_id: str) -> List[Dict]:
        """Recommend next lectures for user in a course
        
        Args:
            user_id: User ID
            course_id: Course ID
            
        Returns:
            List of recommended lectures with reasons
        """
        profile = self.get_user_learning_profile(user_id)
        lectures = self._load_json("lectures.json")
        progress = self._load_json("progress.json")
        
        user_progress = progress.get(user_id, {}).get(course_id, {})
        completed_lectures = user_progress.get("completed_lectures", [])
        
        recommendations = []
        
        # Get all lectures for course
        course_lectures = [l for l in lectures.get("lectures", []) 
                          if l.get("course_id") == course_id]
        
        for lecture in course_lectures:
            lecture_id = lecture.get("id")
            
            # Skip completed lectures
            if lecture_id in completed_lectures:
                continue
            
            reason = []
            priority = 0
            
            # Check prerequisites
            prerequisites = lecture.get("prerequisites", [])
            if prerequisites and not all(p in completed_lectures for p in prerequisites):
                continue  # Skip if prerequisites not met
            
            # Check if next in sequence
            lecture_order = lecture.get("order", 999)
            if not completed_lectures or lecture_order == len(completed_lectures) + 1:
                reason.append("Next in sequence")
                priority += 10
            
            # Check topic relevance
            lecture_topic = lecture.get("topic", "")
            
            # Recommend if weak topic
            weak_topics = [t["topic"] for t in profile["weak_topics"]]
            if lecture_topic in weak_topics:
                reason.append("Helps strengthen weak area")
                priority += 15
            
            # Recommend if strong topic (to maintain strength)
            strong_topics = [t["topic"] for t in profile["strong_topics"]]
            if lecture_topic in strong_topics:
                reason.append("Build on your strengths")
                priority += 5
            
            # Check difficulty
            difficulty = lecture.get("difficulty", "medium")
            avg_score = profile["avg_quiz_score"]
            
            if avg_score >= 80 and difficulty == "hard":
                reason.append("Challenge yourself")
                priority += 8
            elif 60 <= avg_score < 80 and difficulty == "medium":
                reason.append("Appropriate difficulty")
                priority += 10
            elif avg_score < 60 and difficulty == "easy":
                reason.append("Build confidence")
                priority += 12
            
            # Check duration based on study pace
            duration = lecture.get("duration_minutes", 30)
            if profile["study_pace"] == "fast" and duration <= 30:
                reason.append("Quick lesson")
                priority += 3
            elif profile["study_pace"] == "slow" and duration <= 20:
                reason.append("Short and manageable")
                priority += 5
            
            recommendations.append({
                "lecture": lecture,
                "priority": priority,
                "reasons": reason
            })
        
        # Sort by priority
        recommendations.sort(key=lambda x: x["priority"], reverse=True)
        
        return recommendations[:5]  # Top 5
    
    def recommend_review_material(self, user_id: str) -> List[Dict]:
        """Recommend lectures/topics to review
        
        Args:
            user_id: User ID
            
        Returns:
            List of recommended review materials
        """
        profile = self.get_user_learning_profile(user_id)
        lectures = self._load_json("lectures.json")
        engagement_logs = self._load_json("engagement_logs.json")
        
        recommendations = []
        
        # Recommend weak topics
        for weak_topic in profile["weak_topics"][:3]:  # Top 3 weak topics
            topic = weak_topic["topic"]
            
            # Find lectures on this topic
            topic_lectures = [l for l in lectures.get("lectures", [])
                            if l.get("topic") == topic]
            
            for lecture in topic_lectures[:2]:  # Top 2 per topic
                recommendations.append({
                    "type": "review",
                    "lecture": lecture,
                    "reason": f"Review {topic} (current score: {weak_topic['score']:.1f}%)",
                    "priority": 10 - weak_topic['score'] / 10
                })
        
        # Recommend lectures with low engagement
        user_engagement = [log for log in engagement_logs.get("logs", [])
                          if log.get("user_id") == user_id]
        
        low_engagement_lectures = [log for log in user_engagement
                                  if log.get("engagement_score", 100) < 50]
        
        for log in low_engagement_lectures[-3:]:  # Last 3
            lecture_id = log.get("lecture_id")
            lecture = next((l for l in lectures.get("lectures", [])
                          if l.get("id") == lecture_id), None)
            
            if lecture:
                recommendations.append({
                    "type": "review",
                    "lecture": lecture,
                    "reason": f"Low engagement score ({log.get('engagement_score', 0):.1f}%)",
                    "priority": 8
                })
        
        # Sort by priority
        recommendations.sort(key=lambda x: x["priority"], reverse=True)
        
        return recommendations[:5]
    
    def recommend_practice(self, user_id: str) -> List[Dict]:
        """Recommend quizzes and assignments for practice
        
        Args:
            user_id: User ID
            
        Returns:
            List of recommended practice materials
        """
        profile = self.get_user_learning_profile(user_id)
        quizzes = self._load_json("quizzes.json")
        assignments = self._load_json("assignments.json")
        grades = self._load_json("grades.json")
        
        user_grades = grades.get(user_id, {})
        completed_quizzes = [k for k, v in user_grades.items() if v.get("type") == "quiz"]
        
        recommendations = []
        
        # Recommend quizzes on weak topics
        for weak_topic in profile["weak_topics"][:3]:
            topic = weak_topic["topic"]
            
            topic_quizzes = [q for q in quizzes.get("quizzes", [])
                           if q.get("topic") == topic and q.get("id") not in completed_quizzes]
            
            for quiz in topic_quizzes[:2]:
                recommendations.append({
                    "type": "quiz",
                    "item": quiz,
                    "reason": f"Practice {topic}",
                    "priority": 10
                })
        
        # Recommend retaking low-scored quizzes
        for quiz_id, grade_data in user_grades.items():
            if grade_data.get("type") == "quiz" and grade_data.get("score", 100) < 70:
                quiz = next((q for q in quizzes.get("quizzes", [])
                           if q.get("id") == quiz_id), None)
                
                if quiz:
                    recommendations.append({
                        "type": "retake",
                        "item": quiz,
                        "reason": f"Retake to improve score ({grade_data.get('score')}%)",
                        "priority": 8
                    })
        
        # Sort by priority
        recommendations.sort(key=lambda x: x["priority"], reverse=True)
        
        return recommendations[:5]
    
    def recommend_study_schedule(self, user_id: str) -> Dict:
        """Generate personalized study schedule
        
        Args:
            user_id: User ID
            
        Returns:
            Dict with schedule recommendations
        """
        profile = self.get_user_learning_profile(user_id)
        
        # Base session length on study pace
        session_minutes = {
            "slow": 25,
            "moderate": 40,
            "fast": 60
        }
        
        schedule = {
            "recommended_session_length": session_minutes[profile["study_pace"]],
            "recommended_time": profile["preferred_time"],
            "sessions_per_week": 5 if profile["study_pace"] == "fast" else 3,
            "break_frequency": 25 if profile["study_pace"] == "slow" else 50,  # minutes
            "tips": []
        }
        
        # Add personalized tips
        if profile["engagement_trend"] == "declining":
            schedule["tips"].append("Your engagement has been declining. Try studying at different times or in a new environment.")
        
        if profile["avg_engagement"] < 60:
            schedule["tips"].append("Consider shorter study sessions with more breaks to maintain focus.")
        
        if profile["quiz_trend"] == "declining":
            schedule["tips"].append("Review weak topics before moving to new material.")
        
        if profile["weak_topics"]:
            schedule["tips"].append(f"Focus on: {', '.join([t['topic'] for t in profile['weak_topics'][:2]])}")
        
        if profile["preferred_time"] == "night":
            schedule["tips"].append("You study best at night, but ensure you get adequate sleep.")
        
        return schedule
    
    def get_peer_comparison(self, user_id: str) -> Dict:
        """Compare user's performance with peers
        
        Args:
            user_id: User ID
            
        Returns:
            Dict with comparison metrics
        """
        profile = self.get_user_learning_profile(user_id)
        grades = self._load_json("grades.json")
        engagement_logs = self._load_json("engagement_logs.json")
        
        # Calculate class averages
        all_quiz_scores = []
        all_engagement_scores = []
        
        for uid, user_grades in grades.items():
            for grade_data in user_grades.values():
                if grade_data.get("type") == "quiz":
                    all_quiz_scores.append(grade_data.get("score", 0))
        
        for log in engagement_logs.get("logs", []):
            all_engagement_scores.append(log.get("engagement_score", 0))
        
        comparison = {
            "your_avg_quiz_score": profile["avg_quiz_score"],
            "class_avg_quiz_score": sum(all_quiz_scores) / len(all_quiz_scores) if all_quiz_scores else 0,
            "your_avg_engagement": profile["avg_engagement"],
            "class_avg_engagement": sum(all_engagement_scores) / len(all_engagement_scores) if all_engagement_scores else 0,
            "percentile_quiz": 0,
            "percentile_engagement": 0,
            "status": "average"
        }
        
        # Calculate percentiles
        if all_quiz_scores:
            better_than = sum(1 for s in all_quiz_scores if s < profile["avg_quiz_score"])
            comparison["percentile_quiz"] = (better_than / len(all_quiz_scores)) * 100
        
        if all_engagement_scores:
            better_than = sum(1 for s in all_engagement_scores if s < profile["avg_engagement"])
            comparison["percentile_engagement"] = (better_than / len(all_engagement_scores)) * 100
        
        # Determine status
        avg_percentile = (comparison["percentile_quiz"] + comparison["percentile_engagement"]) / 2
        if avg_percentile >= 75:
            comparison["status"] = "excellent"
        elif avg_percentile >= 50:
            comparison["status"] = "above_average"
        elif avg_percentile >= 25:
            comparison["status"] = "average"
        else:
            comparison["status"] = "needs_improvement"
        
        return comparison
