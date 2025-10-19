"""
Smart LMS - Progress Tracking Page
Students can view their learning progress and performance trends
"""

import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.auth import get_auth
from services.storage import get_storage
from services.ui_theme import get_theme_manager
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime


def create_progress_chart(progress_data):
    """Create progress visualization"""
    if not progress_data:
        return None
    
    # Create line chart for engagement trend
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=list(range(len(progress_data['engagement_trend']))),
        y=progress_data['engagement_trend'],
        mode='lines+markers',
        name='Engagement',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title='Engagement Trend Over Time',
        xaxis_title='Lecture Number',
        yaxis_title='Engagement Score',
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig


def create_quiz_performance_chart(quiz_scores):
    """Create quiz performance chart"""
    if not quiz_scores:
        return None
    
    df = pd.DataFrame({
        'Quiz': [f"Quiz {i+1}" for i in range(len(quiz_scores))],
        'Score': quiz_scores
    })
    
    fig = px.bar(
        df,
        x='Quiz',
        y='Score',
        title='Quiz Performance',
        color='Score',
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        yaxis_title='Score (%)',
        template='plotly_white'
    )
    
    return fig


def show_course_progress(course_id, course_name):
    """Display progress for a specific course"""
    storage = get_storage()
    user = st.session_state.user
    theme = get_theme_manager()
    
    st.subheader(f"📊 Progress: {course_name}")
    
    # Get progress data
    progress_data = storage.get_progress(user['user_id'], course_id)
    
    if not progress_data:
        st.info("📝 No progress data available yet. Start watching lectures!")
        return
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        completion = progress_data.get('completion_percentage', 0)
        st.metric(
            "Completion",
            f"{completion:.1f}%",
            delta=f"{len(progress_data.get('completed_lectures', []))} lectures"
        )
    
    with col2:
        avg_engagement = sum(progress_data.get('engagement_trend', [0])) / max(len(progress_data.get('engagement_trend', [1])), 1)
        st.metric(
            "Avg Engagement",
            f"{avg_engagement:.1f}/100",
            delta="Good" if avg_engagement >= 70 else "Needs Improvement"
        )
    
    with col3:
        quiz_scores = progress_data.get('quiz_scores', [])
        avg_quiz = sum(quiz_scores) / len(quiz_scores) if quiz_scores else 0
        st.metric(
            "Avg Quiz Score",
            f"{avg_quiz:.1f}%",
            delta="Excellent" if avg_quiz >= 80 else "Keep practicing"
        )
    
    with col4:
        total_lectures = progress_data.get('total_lectures', 0)
        completed = len(progress_data.get('completed_lectures', []))
        st.metric(
            "Lectures",
            f"{completed}/{total_lectures}",
            delta=f"{total_lectures - completed} remaining"
        )
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Engagement trend
        if progress_data.get('engagement_trend'):
            fig = create_progress_chart(progress_data)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Quiz performance
        if progress_data.get('quiz_scores'):
            fig = create_quiz_performance_chart(progress_data['quiz_scores'])
            if fig:
                st.plotly_chart(fig, use_container_width=True)
    
    # Detailed breakdown
    st.markdown("### 📚 Lecture-by-Lecture Breakdown")
    
    completed_lectures = progress_data.get('completed_lectures', [])
    engagement_trend = progress_data.get('engagement_trend', [])
    
    # Get all lectures for this course
    lectures = storage.get_course_lectures(course_id)
    
    for i, lecture in enumerate(lectures):
        lecture_id = lecture['lecture_id']
        is_completed = lecture_id in completed_lectures
        
        with st.expander(
            f"{'✅' if is_completed else '⏳'} {lecture['title']}",
            expanded=not is_completed
        ):
            if is_completed:
                # Show engagement score
                if i < len(engagement_trend):
                    engagement_score = engagement_trend[i]
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.progress(engagement_score / 100)
                        st.caption(f"Engagement: {engagement_score:.1f}/100")
                    
                    with col2:
                        if engagement_score >= 80:
                            st.success("Excellent!")
                        elif engagement_score >= 60:
                            st.info("Good")
                        else:
                            st.warning("Review")
                
                # Show quiz score if available
                quiz_idx = completed_lectures.index(lecture_id)
                if quiz_idx < len(progress_data.get('quiz_scores', [])):
                    quiz_score = progress_data['quiz_scores'][quiz_idx]
                    st.markdown(f"**Quiz Score:** {quiz_score:.1f}%")
            else:
                st.info("Not completed yet")
                if st.button("▶️ Start Lecture", key=f"start_{lecture_id}"):
                    st.session_state.selected_lecture = lecture
                    st.session_state.current_page = 'watch_lecture'
                    st.rerun()
    
    # Recommendations
    st.markdown("---")
    st.markdown("### 💡 Recommendations")
    
    if avg_engagement < 70:
        st.warning("🎯 **Improve Engagement:** Try to minimize distractions and focus on the lecture content.")
    
    if avg_quiz < 70:
        st.warning("📚 **Review Material:** Consider rewatching lectures and reviewing course materials.")
    
    if completion < 50:
        st.info("⏰ **Stay on Track:** You're making progress! Try to complete more lectures this week.")
    
    if avg_engagement >= 80 and avg_quiz >= 80:
        st.success("🌟 **Excellent Performance:** Keep up the great work!")


def show_overall_progress():
    """Display overall progress across all courses"""
    storage = get_storage()
    user = st.session_state.user
    
    st.title("📈 My Learning Progress")
    
    # Get enrolled courses
    all_courses = storage.get_all_courses()
    enrolled_courses = {
        cid: c for cid, c in all_courses.items()
        if user['user_id'] in c.get('enrolled_students', [])
    }
    
    if not enrolled_courses:
        st.info("📝 You are not enrolled in any courses yet.")
        return
    
    # Overall statistics
    st.markdown("### 📊 Overall Statistics")
    
    total_engagement = []
    total_quiz_scores = []
    total_completed = 0
    total_lectures = 0
    
    for course_id in enrolled_courses.keys():
        progress = storage.get_progress(user['user_id'], course_id)
        if progress:
            total_engagement.extend(progress.get('engagement_trend', []))
            total_quiz_scores.extend(progress.get('quiz_scores', []))
            total_completed += len(progress.get('completed_lectures', []))
            total_lectures += progress.get('total_lectures', 0)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Enrolled Courses", len(enrolled_courses))
    
    with col2:
        overall_completion = (total_completed / total_lectures * 100) if total_lectures > 0 else 0
        st.metric("Overall Completion", f"{overall_completion:.1f}%")
    
    with col3:
        avg_engagement = sum(total_engagement) / len(total_engagement) if total_engagement else 0
        st.metric("Avg Engagement", f"{avg_engagement:.1f}/100")
    
    with col4:
        avg_quiz = sum(total_quiz_scores) / len(total_quiz_scores) if total_quiz_scores else 0
        st.metric("Avg Quiz Score", f"{avg_quiz:.1f}%")
    
    st.markdown("---")
    
    # Course-by-course progress
    st.markdown("### 📚 Course Progress")
    
    for course_id, course in enrolled_courses.items():
        with st.expander(f"📖 {course['name']}", expanded=True):
            progress = storage.get_progress(user['user_id'], course_id)
            
            if progress:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    completion = progress.get('completion_percentage', 0)
                    st.metric("Completion", f"{completion:.1f}%")
                
                with col2:
                    eng_trend = progress.get('engagement_trend', [])
                    avg_eng = sum(eng_trend) / len(eng_trend) if eng_trend else 0
                    st.metric("Engagement", f"{avg_eng:.1f}/100")
                
                with col3:
                    quiz_scores = progress.get('quiz_scores', [])
                    avg_q = sum(quiz_scores) / len(quiz_scores) if quiz_scores else 0
                    st.metric("Quiz Avg", f"{avg_q:.1f}%")
                
                if st.button("📊 View Detailed Progress", key=f"view_{course_id}"):
                    st.session_state.selected_course_progress = course_id
                    st.rerun()
            else:
                st.info("No progress data yet. Start watching lectures!")


def main():
    """Main progress page"""
    # Check authentication
    auth = get_auth()
    auth.require_role('student')
    
    # Apply theme
    theme = get_theme_manager()
    theme.apply_theme()
    
    # Check if viewing specific course progress
    if 'selected_course_progress' in st.session_state:
        course_id = st.session_state.selected_course_progress
        storage = get_storage()
        course = storage.get_course(course_id)
        
        if st.button("← Back to Overview"):
            del st.session_state.selected_course_progress
            st.rerun()
        
        if course:
            show_course_progress(course_id, course['name'])
    else:
        show_overall_progress()


if __name__ == "__main__":
    main()
