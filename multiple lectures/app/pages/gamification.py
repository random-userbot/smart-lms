"""
Gamification & Recommendations Page
Display badges, leaderboard, and personalized recommendations
"""

import streamlit as st
import sys
import os
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from services.storage import get_storage
from services.gamification import GamificationService
from services.recommendations import RecommendationsService


def show_gamification_page():
    """Display gamification and recommendations page"""
    
    # Check authentication
    if "user" not in st.session_state or not st.session_state.user:
        st.warning("⚠️ Please login to view this page")
        return
    
    user = st.session_state.user
    user_id = user["id"]
    storage = get_storage()
    
    # Initialize services
    storage_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage")
    gamification = GamificationService(storage_path)
    recommendations = RecommendationsService(storage_path)
    
    st.markdown('<h1 class="main-header">🎮 Gamification & Recommendations</h1>', unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🏆 Your Progress", "🥇 Leaderboard", "💡 Recommendations", "📊 Analytics"])
    
    with tab1:
        show_user_progress(user_id, gamification, recommendations)
    
    with tab2:
        show_leaderboard(user_id, gamification, storage)
    
    with tab3:
        show_recommendations(user_id, recommendations, storage)
    
    with tab4:
        show_analytics(user_id, recommendations)


def show_user_progress(user_id: str, gamification: GamificationService, recommendations: RecommendationsService):
    """Show user's badges, points, and progress"""
    
    profile = gamification.get_user_profile(user_id)
    learning_profile = recommendations.get_user_learning_profile(user_id)
    
    # Top stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🏅 Total Points", f"{profile['points']:,}")
    
    with col2:
        st.metric("⭐ Level", profile['level'])
    
    with col3:
        st.metric("🎯 Badges Earned", len(profile['badges']))
    
    with col4:
        rank = gamification.get_user_rank(user_id)
        st.metric("📊 Rank", f"#{rank}")
    
    st.divider()
    
    # Badges Section
    st.subheader("🏆 Your Badges")
    
    if profile['badges']:
        # Display earned badges
        cols = st.columns(4)
        for idx, badge_id in enumerate(profile['badges']):
            badge_info = gamification.BADGES.get(badge_id)
            if badge_info:
                with cols[idx % 4]:
                    st.markdown(f"""
                    <div style="text-align: center; padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                border-radius: 10px; margin: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                        <div style="font-size: 3rem;">{badge_info['icon']}</div>
                        <div style="color: white; font-weight: bold; margin-top: 10px;">{badge_info['name']}</div>
                        <div style="color: #f0f0f0; font-size: 0.9rem;">{badge_info['description']}</div>
                        <div style="color: #ffd700; font-weight: bold; margin-top: 5px;">+{badge_info['points']} pts</div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("🎯 Start earning badges by completing lectures, quizzes, and maintaining high engagement!")
    
    st.divider()
    
    # Badge Progress
    st.subheader("📈 Badge Progress")
    
    progress_data = gamification.get_badge_progress(user_id)
    
    for badge_id, progress in progress_data.items():
        if not progress['earned']:
            badge_info = gamification.BADGES.get(badge_id)
            if badge_info:
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"{badge_info['icon']} **{badge_info['name']}**")
                    st.progress(progress['percentage'] / 100)
                    st.caption(f"{progress['current']}/{progress['target']} - {badge_info['description']}")
                
                with col2:
                    st.metric("Progress", f"{progress['percentage']:.0f}%")
    
    st.divider()
    
    # Login Streak
    st.subheader("🔥 Login Streak")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        streak_days = profile.get('streak_days', 0)
        
        # Visual streak display
        weeks = streak_days // 7
        days = streak_days % 7
        
        st.write(f"**Current Streak: {streak_days} days**")
        
        # Show streak visualization
        streak_visual = "🔥" * min(streak_days, 30)
        st.markdown(f"<div style='font-size: 1.5rem;'>{streak_visual}</div>", unsafe_allow_html=True)
        
        if streak_days >= 30:
            st.success("👑 Amazing! You're a Monthly Master!")
        elif streak_days >= 7:
            st.success("⚔️ Great! You're a Week Warrior!")
        elif streak_days >= 3:
            st.info("🔥 Keep it up! You're on a 3-day streak!")
    
    with col2:
        # Next streak milestone
        if streak_days < 3:
            next_milestone = 3
            milestone_name = "3-Day Streak"
        elif streak_days < 7:
            next_milestone = 7
            milestone_name = "Week Warrior"
        elif streak_days < 30:
            next_milestone = 30
            milestone_name = "Monthly Master"
        else:
            next_milestone = streak_days + 30
            milestone_name = "Extended Streak"
        
        st.metric("Next Milestone", f"{next_milestone - streak_days} days", 
                 delta=milestone_name)
    
    st.divider()
    
    # Recent Activity
    st.subheader("📜 Recent Activity")
    
    recent_activities = profile.get('activity_history', [])[-10:]
    
    if recent_activities:
        for activity in reversed(recent_activities):
            timestamp = datetime.fromisoformat(activity['timestamp'])
            time_str = timestamp.strftime("%b %d, %Y %I:%M %p")
            
            activity_icons = {
                'lecture_watch': '🎥',
                'quiz_complete': '📝',
                'assignment_submit': '📤',
                'feedback_provide': '💬',
                'login_daily': '🔑',
                'high_engagement': '🎯'
            }
            
            icon = activity_icons.get(activity['activity'], '✨')
            
            st.markdown(f"""
            <div style="padding: 10px; border-left: 3px solid #667eea; background: #f8f9fa; margin: 5px 0; border-radius: 5px;">
                {icon} **{activity['activity'].replace('_', ' ').title()}** 
                <span style="float: right; color: #667eea;">+{activity['points']} pts</span>
                <br><span style="font-size: 0.85rem; color: #666;">{time_str}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No recent activity yet. Start learning to see your progress here!")


def show_leaderboard(user_id: str, gamification: GamificationService, storage):
    """Show global leaderboard"""
    
    st.subheader("🥇 Top Learners")
    
    leaderboard = gamification.get_leaderboard(limit=20)
    
    if leaderboard:
        # Get user details
        for entry in leaderboard:
            user_data = storage.get_user_by_id(entry['user_id'])
            if user_data:
                entry['name'] = user_data.get('name', 'Unknown')
                entry['role'] = user_data.get('role', 'student')
        
        # Create columns for top 3
        if len(leaderboard) >= 3:
            st.markdown("### 🏆 Top 3")
            col1, col2, col3 = st.columns(3)
            
            # 1st place
            with col2:  # Center position
                first = leaderboard[0]
                st.markdown(f"""
                <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                            border-radius: 15px; box-shadow: 0 8px 16px rgba(0,0,0,0.2);">
                    <div style="font-size: 4rem;">👑</div>
                    <div style="color: white; font-size: 1.5rem; font-weight: bold;">{first['name']}</div>
                    <div style="color: #fff; font-size: 2rem; font-weight: bold;">{first['points']:,} pts</div>
                    <div style="color: #ffe; font-size: 1.2rem;">Level {gamification.get_user_profile(first['user_id'])['level']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # 2nd place
            with col1:
                second = leaderboard[1]
                st.markdown(f"""
                <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); 
                            border-radius: 15px; box-shadow: 0 6px 12px rgba(0,0,0,0.15);">
                    <div style="font-size: 3rem;">🥈</div>
                    <div style="color: #333; font-size: 1.2rem; font-weight: bold;">{second['name']}</div>
                    <div style="color: #666; font-size: 1.5rem; font-weight: bold;">{second['points']:,} pts</div>
                </div>
                """, unsafe_allow_html=True)
            
            # 3rd place
            with col3:
                third = leaderboard[2]
                st.markdown(f"""
                <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); 
                            border-radius: 15px; box-shadow: 0 6px 12px rgba(0,0,0,0.15);">
                    <div style="font-size: 3rem;">🥉</div>
                    <div style="color: #333; font-size: 1.2rem; font-weight: bold;">{third['name']}</div>
                    <div style="color: #666; font-size: 1.5rem; font-weight: bold;">{third['points']:,} pts</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.divider()
        
        # Full leaderboard table
        st.markdown("### 📊 Full Rankings")
        
        for entry in leaderboard:
            is_current_user = entry['user_id'] == user_id
            bg_color = "#e3f2fd" if is_current_user else "#ffffff"
            border = "3px solid #2196f3" if is_current_user else "1px solid #e0e0e0"
            
            rank_emoji = {1: "🥇", 2: "🥈", 3: "🥉"}.get(entry['rank'], "")
            
            st.markdown(f"""
            <div style="padding: 15px; margin: 5px 0; background: {bg_color}; 
                        border: {border}; border-radius: 10px; display: flex; 
                        align-items: center; justify-content: space-between;">
                <div style="display: flex; align-items: center; gap: 15px;">
                    <div style="font-size: 1.5rem; font-weight: bold; min-width: 40px;">
                        #{entry['rank']} {rank_emoji}
                    </div>
                    <div>
                        <div style="font-weight: bold; font-size: 1.1rem;">
                            {entry['name']} {'👈 You' if is_current_user else ''}
                        </div>
                        <div style="color: #666; font-size: 0.9rem;">
                            Level {gamification.get_user_profile(entry['user_id'])['level']}
                        </div>
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 1.3rem; font-weight: bold; color: #667eea;">
                        {entry['points']:,}
                    </div>
                    <div style="color: #666; font-size: 0.9rem;">points</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Leaderboard is empty. Start earning points to appear here!")


def show_recommendations(user_id: str, recommendations: RecommendationsService, storage):
    """Show personalized recommendations"""
    
    st.subheader("💡 Personalized Recommendations")
    
    # Get learning profile
    learning_profile = recommendations.get_user_learning_profile(user_id)
    
    # Display learning insights
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 Avg Engagement", f"{learning_profile['avg_engagement']:.1f}%",
                 delta=learning_profile['engagement_trend'].title())
    
    with col2:
        st.metric("📝 Avg Quiz Score", f"{learning_profile['avg_quiz_score']:.1f}%",
                 delta=learning_profile['quiz_trend'].title())
    
    with col3:
        st.metric("⚡ Study Pace", learning_profile['study_pace'].title())
    
    st.divider()
    
    # Recommended study schedule
    st.subheader("📅 Your Optimal Study Schedule")
    schedule = recommendations.recommend_study_schedule(user_id)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **Recommended Session Length:** {schedule['recommended_session_length']} minutes  
        **Best Time to Study:** {schedule['recommended_time'].title()}  
        **Sessions Per Week:** {schedule['sessions_per_week']}  
        **Break Frequency:** Every {schedule['break_frequency']} minutes
        """)
    
    with col2:
        if schedule['tips']:
            st.warning("**💡 Personalized Tips:**\n\n" + "\n\n".join(f"• {tip}" for tip in schedule['tips']))
    
    st.divider()
    
    # Content recommendations
    tab1, tab2 = st.tabs(["📚 Recommended Material", "🔄 Review Material"])
    
    with tab1:
        st.subheader("📚 What to Study Next")
        
        # Get user's courses
        courses = storage.get_user_courses(user_id)
        
        if courses:
            selected_course = st.selectbox("Select Course", 
                                          [c['title'] for c in courses],
                                          key="rec_course")
            
            if selected_course:
                course = next(c for c in courses if c['title'] == selected_course)
                next_lectures = recommendations.recommend_next_lecture(user_id, course['id'])
                
                if next_lectures:
                    for rec in next_lectures[:3]:
                        lecture = rec['lecture']
                        reasons = rec['reasons']
                        
                        with st.expander(f"🎥 {lecture.get('title', 'Untitled')}", expanded=True):
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.write(f"**Description:** {lecture.get('description', 'No description')}")
                                st.write(f"**Duration:** {lecture.get('duration_minutes', 0)} minutes")
                                st.write(f"**Difficulty:** {lecture.get('difficulty', 'medium').title()}")
                                
                                if reasons:
                                    st.success("**Why recommended:**\n" + "\n".join(f"• {r}" for r in reasons))
                            
                            with col2:
                                if st.button("▶️ Start", key=f"start_{lecture.get('id')}"):
                                    st.success("Opening lecture...")
                else:
                    st.info("🎉 You've completed all lectures in this course!")
        else:
            st.info("Enroll in a course to get personalized recommendations!")
    
    with tab2:
        st.subheader("🔄 Material to Review")
        
        review_items = recommendations.recommend_review_material(user_id)
        
        if review_items:
            for item in review_items:
                lecture = item['lecture']
                reason = item['reason']
                
                with st.container():
                    st.markdown(f"""
                    <div style="padding: 15px; background: #fff3cd; border-left: 4px solid #ffc107; 
                                border-radius: 5px; margin: 10px 0;">
                        <div style="font-weight: bold; font-size: 1.1rem;">
                            🎥 {lecture.get('title', 'Untitled')}
                        </div>
                        <div style="color: #856404; margin-top: 5px;">
                            ⚠️ {reason}
                        </div>
                        <div style="margin-top: 10px;">
                            Duration: {lecture.get('duration_minutes', 0)} min | 
                            Difficulty: {lecture.get('difficulty', 'medium').title()}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.success("✅ Great job! No review needed at this time.")
    
    st.divider()
    
    # Practice recommendations
    st.subheader("🎯 Recommended Practice")
    
    practice_items = recommendations.recommend_practice(user_id)
    
    if practice_items:
        for item in practice_items[:3]:
            quiz = item['item']
            reason = item['reason']
            
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.write(f"**📝 {quiz.get('title', 'Untitled Quiz')}**")
                st.caption(f"💡 {reason}")
            
            with col2:
                if st.button("Take Quiz", key=f"quiz_{quiz.get('id')}"):
                    st.success("Opening quiz...")
    else:
        st.info("Complete some lectures first to get practice recommendations!")


def show_analytics(user_id: str, recommendations: RecommendationsService):
    """Show learning analytics"""
    
    st.subheader("📊 Your Learning Analytics")
    
    profile = recommendations.get_user_learning_profile(user_id)
    comparison = recommendations.get_peer_comparison(user_id)
    
    # Performance comparison
    col1, col2 = st.columns(2)
    
    with col1:
        # Quiz performance comparison
        fig = go.Figure(data=[
            go.Bar(name='You', x=['Quiz Score'], y=[profile['avg_quiz_score']], 
                  marker_color='#667eea'),
            go.Bar(name='Class Average', x=['Quiz Score'], y=[comparison['class_avg_quiz_score']], 
                  marker_color='#f093fb')
        ])
        fig.update_layout(title="Quiz Performance vs Class", yaxis_title="Score (%)", height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Engagement comparison
        fig = go.Figure(data=[
            go.Bar(name='You', x=['Engagement'], y=[profile['avg_engagement']], 
                  marker_color='#667eea'),
            go.Bar(name='Class Average', x=['Engagement'], y=[comparison['class_avg_engagement']], 
                  marker_color='#f093fb')
        ])
        fig.update_layout(title="Engagement vs Class", yaxis_title="Score (%)", height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # Performance status
    status_colors = {
        'excellent': '🌟',
        'above_average': '👍',
        'average': '📊',
        'needs_improvement': '📈'
    }
    
    status_messages = {
        'excellent': "Excellent! You're in the top 25% of your class!",
        'above_average': "Great job! You're above the class average!",
        'average': "You're doing okay. Keep pushing to improve!",
        'needs_improvement': "There's room for improvement. Check the recommendations!"
    }
    
    status = comparison['status']
    st.info(f"{status_colors[status]} **Performance Status:** {status_messages[status]}")
    
    st.divider()
    
    # Strengths and weaknesses
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💪 Your Strengths")
        if profile['strong_topics']:
            for topic in profile['strong_topics'][:5]:
                st.success(f"✅ {topic['topic']}: {topic['score']:.1f}%")
        else:
            st.info("Complete more quizzes to identify your strengths!")
    
    with col2:
        st.subheader("📚 Areas to Improve")
        if profile['weak_topics']:
            for topic in profile['weak_topics'][:5]:
                st.warning(f"⚠️ {topic['topic']}: {topic['score']:.1f}%")
        else:
            st.success("No weak areas identified yet!")


if __name__ == "__main__":
    show_gamification_page()
