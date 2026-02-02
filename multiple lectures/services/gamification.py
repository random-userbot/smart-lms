"""
Gamification Service
Handles badges, points, leaderboards, and achievements for student engagement
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path


class GamificationService:
    """Service for managing gamification features"""
    
    # Badge definitions
    BADGES = {
        "early_bird": {
            "name": "Early Bird",
            "description": "Watched a lecture within 1 hour of upload",
            "icon": "🌅",
            "points": 50
        },
        "perfect_score": {
            "name": "Perfect Score",
            "description": "Achieved 100% on a quiz",
            "icon": "💯",
            "points": 100
        },
        "streak_3": {
            "name": "3-Day Streak",
            "description": "Logged in for 3 consecutive days",
            "icon": "🔥",
            "points": 75
        },
        "streak_7": {
            "name": "Week Warrior",
            "description": "Logged in for 7 consecutive days",
            "icon": "⚔️",
            "points": 150
        },
        "streak_30": {
            "name": "Monthly Master",
            "description": "Logged in for 30 consecutive days",
            "icon": "👑",
            "points": 500
        },
        "engagement_master": {
            "name": "Engagement Master",
            "description": "Maintained 90%+ engagement score for 5 lectures",
            "icon": "🎯",
            "points": 200
        },
        "quiz_master": {
            "name": "Quiz Master",
            "description": "Scored 90%+ on 10 quizzes",
            "icon": "🧠",
            "points": 300
        },
        "assignment_ace": {
            "name": "Assignment Ace",
            "description": "Submitted 10 assignments on time",
            "icon": "📝",
            "points": 250
        },
        "helpful_feedback": {
            "name": "Helpful Feedback",
            "description": "Provided feedback on 10 lectures",
            "icon": "💬",
            "points": 100
        },
        "course_complete": {
            "name": "Course Complete",
            "description": "Completed all lectures in a course",
            "icon": "🎓",
            "points": 400
        },
        "fast_learner": {
            "name": "Fast Learner",
            "description": "Completed a course in under 2 weeks",
            "icon": "⚡",
            "points": 300
        },
        "night_owl": {
            "name": "Night Owl",
            "description": "Studied after midnight",
            "icon": "🦉",
            "points": 50
        }
    }
    
    # Points for various activities
    ACTIVITY_POINTS = {
        "lecture_watch": 10,
        "quiz_complete": 20,
        "assignment_submit": 30,
        "feedback_provide": 15,
        "login_daily": 5,
        "high_engagement": 25  # 80%+ engagement
    }
    
    def __init__(self, storage_path: str):
        """Initialize gamification service
        
        Args:
            storage_path: Path to storage directory
        """
        self.storage_path = Path(storage_path)
        self.gamification_file = self.storage_path / "gamification.json"
        self.leaderboard_file = self.storage_path / "leaderboard.json"
        self._ensure_files()
    
    def _ensure_files(self):
        """Ensure gamification files exist"""
        if not self.gamification_file.exists():
            self._save_gamification({})
        if not self.leaderboard_file.exists():
            self._save_leaderboard([])
    
    def _load_gamification(self) -> Dict:
        """Load gamification data"""
        with open(self.gamification_file, 'r') as f:
            return json.load(f)
    
    def _save_gamification(self, data: Dict):
        """Save gamification data"""
        with open(self.gamification_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_leaderboard(self) -> List:
        """Load leaderboard data"""
        with open(self.leaderboard_file, 'r') as f:
            return json.load(f)
    
    def _save_leaderboard(self, data: List):
        """Save leaderboard data"""
        with open(self.leaderboard_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_user_profile(self, user_id: str) -> Dict:
        """Get user's gamification profile
        
        Args:
            user_id: User ID
            
        Returns:
            Dict with user's points, badges, level, etc.
        """
        data = self._load_gamification()
        
        if user_id not in data:
            data[user_id] = {
                "points": 0,
                "level": 1,
                "badges": [],
                "achievements": [],
                "streak_days": 0,
                "last_login": None,
                "activity_history": [],
                "statistics": {
                    "lectures_watched": 0,
                    "quizzes_completed": 0,
                    "assignments_submitted": 0,
                    "perfect_quizzes": 0,
                    "high_engagement_count": 0,
                    "feedback_provided": 0
                }
            }
            self._save_gamification(data)
        
        return data[user_id]
    
    def award_points(self, user_id: str, activity: str, amount: Optional[int] = None) -> Dict:
        """Award points to user for an activity
        
        Args:
            user_id: User ID
            activity: Activity type
            amount: Optional custom points amount
            
        Returns:
            Updated user profile
        """
        data = self._load_gamification()
        profile = self.get_user_profile(user_id)
        
        points = amount if amount is not None else self.ACTIVITY_POINTS.get(activity, 0)
        profile["points"] += points
        
        # Update level (100 points per level)
        profile["level"] = (profile["points"] // 100) + 1
        
        # Record activity
        profile["activity_history"].append({
            "activity": activity,
            "points": points,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last 100 activities
        profile["activity_history"] = profile["activity_history"][-100:]
        
        data[user_id] = profile
        self._save_gamification(data)
        
        # Update leaderboard
        self._update_leaderboard(user_id, profile["points"])
        
        return profile
    
    def award_badge(self, user_id: str, badge_id: str) -> Optional[Dict]:
        """Award a badge to user
        
        Args:
            user_id: User ID
            badge_id: Badge identifier
            
        Returns:
            Badge info if awarded, None if already has badge
        """
        if badge_id not in self.BADGES:
            return None
        
        data = self._load_gamification()
        profile = self.get_user_profile(user_id)
        
        # Check if user already has this badge
        if badge_id in profile["badges"]:
            return None
        
        badge_info = self.BADGES[badge_id].copy()
        badge_info["earned_at"] = datetime.now().isoformat()
        
        profile["badges"].append(badge_id)
        profile["achievements"].append(badge_info)
        profile["points"] += badge_info["points"]
        
        # Update level
        profile["level"] = (profile["points"] // 100) + 1
        
        data[user_id] = profile
        self._save_gamification(data)
        
        # Update leaderboard
        self._update_leaderboard(user_id, profile["points"])
        
        return badge_info
    
    def check_and_award_badges(self, user_id: str, event_type: str, event_data: Dict) -> List[Dict]:
        """Check if user earned any badges from an event
        
        Args:
            user_id: User ID
            event_type: Type of event (quiz_complete, lecture_watch, etc.)
            event_data: Event data
            
        Returns:
            List of newly awarded badges
        """
        new_badges = []
        profile = self.get_user_profile(user_id)
        
        # Check quiz-related badges
        if event_type == "quiz_complete":
            score = event_data.get("score", 0)
            
            if score == 100 and "perfect_score" not in profile["badges"]:
                badge = self.award_badge(user_id, "perfect_score")
                if badge:
                    new_badges.append(badge)
            
            # Update statistics
            profile["statistics"]["quizzes_completed"] += 1
            if score == 100:
                profile["statistics"]["perfect_quizzes"] += 1
            
            # Check Quiz Master badge (10 quizzes with 90%+)
            if score >= 90 and "quiz_master" not in profile["badges"]:
                # Count quizzes with 90%+
                high_score_count = sum(1 for activity in profile["activity_history"] 
                                      if activity.get("activity") == "quiz_complete" 
                                      and activity.get("score", 0) >= 90)
                if high_score_count >= 10:
                    badge = self.award_badge(user_id, "quiz_master")
                    if badge:
                        new_badges.append(badge)
        
        # Check lecture-related badges
        elif event_type == "lecture_watch":
            profile["statistics"]["lectures_watched"] += 1
            
            # Check Early Bird badge
            upload_time = event_data.get("upload_time")
            watch_time = datetime.now()
            if upload_time and "early_bird" not in profile["badges"]:
                upload_dt = datetime.fromisoformat(upload_time)
                if (watch_time - upload_dt) < timedelta(hours=1):
                    badge = self.award_badge(user_id, "early_bird")
                    if badge:
                        new_badges.append(badge)
            
            # Check engagement badges
            engagement_score = event_data.get("engagement_score", 0)
            if engagement_score >= 90:
                profile["statistics"]["high_engagement_count"] += 1
                
                if profile["statistics"]["high_engagement_count"] >= 5 and "engagement_master" not in profile["badges"]:
                    badge = self.award_badge(user_id, "engagement_master")
                    if badge:
                        new_badges.append(badge)
        
        # Check assignment badges
        elif event_type == "assignment_submit":
            profile["statistics"]["assignments_submitted"] += 1
            
            on_time = event_data.get("on_time", False)
            if on_time:
                on_time_count = sum(1 for activity in profile["activity_history"]
                                   if activity.get("activity") == "assignment_submit"
                                   and activity.get("on_time", False))
                
                if on_time_count >= 10 and "assignment_ace" not in profile["badges"]:
                    badge = self.award_badge(user_id, "assignment_ace")
                    if badge:
                        new_badges.append(badge)
        
        # Check feedback badges
        elif event_type == "feedback_provide":
            profile["statistics"]["feedback_provided"] += 1
            
            if profile["statistics"]["feedback_provided"] >= 10 and "helpful_feedback" not in profile["badges"]:
                badge = self.award_badge(user_id, "helpful_feedback")
                if badge:
                    new_badges.append(badge)
        
        # Save updated statistics
        data = self._load_gamification()
        data[user_id] = profile
        self._save_gamification(data)
        
        return new_badges
    
    def update_login_streak(self, user_id: str) -> List[Dict]:
        """Update user's login streak and check for streak badges
        
        Args:
            user_id: User ID
            
        Returns:
            List of newly awarded badges
        """
        new_badges = []
        profile = self.get_user_profile(user_id)
        
        now = datetime.now()
        last_login = profile.get("last_login")
        
        if last_login:
            last_login_dt = datetime.fromisoformat(last_login)
            days_diff = (now - last_login_dt).days
            
            if days_diff == 1:
                # Consecutive day
                profile["streak_days"] += 1
            elif days_diff > 1:
                # Streak broken
                profile["streak_days"] = 1
            # else: same day, no change
        else:
            profile["streak_days"] = 1
        
        profile["last_login"] = now.isoformat()
        
        # Check streak badges
        streak = profile["streak_days"]
        
        if streak >= 3 and "streak_3" not in profile["badges"]:
            badge = self.award_badge(user_id, "streak_3")
            if badge:
                new_badges.append(badge)
        
        if streak >= 7 and "streak_7" not in profile["badges"]:
            badge = self.award_badge(user_id, "streak_7")
            if badge:
                new_badges.append(badge)
        
        if streak >= 30 and "streak_30" not in profile["badges"]:
            badge = self.award_badge(user_id, "streak_30")
            if badge:
                new_badges.append(badge)
        
        # Award daily login points
        self.award_points(user_id, "login_daily")
        
        # Save updated profile
        data = self._load_gamification()
        data[user_id] = profile
        self._save_gamification(data)
        
        return new_badges
    
    def get_leaderboard(self, limit: int = 10, course_id: Optional[str] = None) -> List[Dict]:
        """Get leaderboard rankings
        
        Args:
            limit: Number of top users to return
            course_id: Optional course filter
            
        Returns:
            List of user rankings
        """
        leaderboard = self._load_leaderboard()
        
        # Sort by points descending
        leaderboard.sort(key=lambda x: x["points"], reverse=True)
        
        # Add rank
        for i, entry in enumerate(leaderboard):
            entry["rank"] = i + 1
        
        return leaderboard[:limit]
    
    def _update_leaderboard(self, user_id: str, points: int):
        """Update leaderboard entry for user
        
        Args:
            user_id: User ID
            points: Current points
        """
        leaderboard = self._load_leaderboard()
        
        # Find or create user entry
        entry = None
        for item in leaderboard:
            if item["user_id"] == user_id:
                entry = item
                break
        
        if entry:
            entry["points"] = points
            entry["updated_at"] = datetime.now().isoformat()
        else:
            leaderboard.append({
                "user_id": user_id,
                "points": points,
                "updated_at": datetime.now().isoformat()
            })
        
        self._save_leaderboard(leaderboard)
    
    def get_user_rank(self, user_id: str) -> int:
        """Get user's rank on leaderboard
        
        Args:
            user_id: User ID
            
        Returns:
            User's rank (1-based)
        """
        leaderboard = self.get_leaderboard(limit=1000)
        
        for entry in leaderboard:
            if entry["user_id"] == user_id:
                return entry["rank"]
        
        return len(leaderboard) + 1
    
    def get_badge_progress(self, user_id: str) -> Dict:
        """Get user's progress towards earning badges
        
        Args:
            user_id: User ID
            
        Returns:
            Dict with progress for each badge
        """
        profile = self.get_user_profile(user_id)
        stats = profile["statistics"]
        
        progress = {}
        
        # Quiz Master: 10 quizzes with 90%+
        progress["quiz_master"] = {
            "earned": "quiz_master" in profile["badges"],
            "current": min(stats.get("perfect_quizzes", 0), 10),
            "target": 10,
            "percentage": min(100, stats.get("perfect_quizzes", 0) * 10)
        }
        
        # Assignment Ace: 10 on-time submissions
        on_time_count = sum(1 for activity in profile["activity_history"]
                           if activity.get("activity") == "assignment_submit"
                           and activity.get("on_time", False))
        progress["assignment_ace"] = {
            "earned": "assignment_ace" in profile["badges"],
            "current": min(on_time_count, 10),
            "target": 10,
            "percentage": min(100, on_time_count * 10)
        }
        
        # Engagement Master: 5 lectures with 90%+ engagement
        progress["engagement_master"] = {
            "earned": "engagement_master" in profile["badges"],
            "current": min(stats.get("high_engagement_count", 0), 5),
            "target": 5,
            "percentage": min(100, stats.get("high_engagement_count", 0) * 20)
        }
        
        # Helpful Feedback: 10 feedbacks
        progress["helpful_feedback"] = {
            "earned": "helpful_feedback" in profile["badges"],
            "current": min(stats.get("feedback_provided", 0), 10),
            "target": 10,
            "percentage": min(100, stats.get("feedback_provided", 0) * 10)
        }
        
        # Streak badges
        streak = profile["streak_days"]
        for badge_id, target in [("streak_3", 3), ("streak_7", 7), ("streak_30", 30)]:
            progress[badge_id] = {
                "earned": badge_id in profile["badges"],
                "current": min(streak, target),
                "target": target,
                "percentage": min(100, (streak / target) * 100)
            }
        
        return progress
