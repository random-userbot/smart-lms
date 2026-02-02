"""
Smart LMS - Intelligent Engagement Analytics Page
Display ML-based engagement scores with explanations and insights
"""

import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.auth import get_auth
from services.storage import get_storage
from services.universal_logger import get_activity_logger
from services.intelligent_scorer import get_intelligent_scorer
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


def show_engagement_analytics():
    """Main analytics page"""
    st.title("📊 Intelligent Engagement Analytics")
    st.markdown("ML-powered insights into learning engagement and patterns")
    st.markdown("---")
    
    user = st.session_state.user
    storage = get_storage()
    logger = get_activity_logger()
    scorer = get_intelligent_scorer()
    
    # Role-specific views
    if user['role'] == 'student':
        show_student_analytics(user, storage, logger, scorer)
    elif user['role'] == 'teacher':
        show_teacher_analytics(user, storage, logger, scorer)
    elif user['role'] == 'admin':
        show_admin_analytics(storage, logger, scorer)
    else:
        st.error("Invalid role")


def show_student_analytics(user, storage, logger, scorer):
    """Show analytics for student"""
    student_id = user['user_id']
    
    # Get student's courses
    enrolled_courses = storage.get_student_courses(student_id)
    
    if not enrolled_courses:
        st.info("📚 Enroll in courses to see your engagement analytics!")
        return
    
    # Course selector
    course_options = {course_id: course['name'] for course_id, course in enrolled_courses.items()}
    selected_course = st.selectbox("📖 Select Course", options=list(course_options.keys()), 
                                   format_func=lambda x: course_options[x])
    
    # Get lectures for selected course
    lectures = storage.get_course_lectures(selected_course)
    
    if not lectures:
        st.info("No lectures available for this course yet.")
        return
    
    # Overall course engagement
    st.markdown("## 🎯 Overall Course Engagement")
    
    # Get all actions for this course
    all_actions = logger._get_recent_actions(student_id, limit=5000)
    course_actions = [a for a in all_actions if a['context'].get('course_id') == selected_course]
    
    if not course_actions:
        st.warning("⏳ No activity recorded yet. Start engaging with the course to see your analytics!")
        return
    
    # Calculate overall engagement
    result = scorer.predict_engagement_score(
        course_actions,
        {'course_id': selected_course, 'user_role': 'student'}
    )
    
    # Display overall score
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        score_color = "🟢" if result['engagement_score'] >= 80 else "🟡" if result['engagement_score'] >= 60 else "🔴"
        st.metric("Engagement Score", f"{score_color} {result['engagement_score']}/100")
    
    with col2:
        st.metric("Level", result['level'])
    
    with col3:
        st.metric("Confidence", f"{result['confidence']*100:.0f}%")
    
    with col4:
        st.metric("Total Actions", result['total_actions'])
    
    # Explanation
    st.info(f"💡 **Insight:** {result['explanation']}")
    
    # Feature breakdown
    with st.expander("🔍 Detailed Feature Analysis", expanded=False):
        features = scorer.extract_features_from_actions(course_actions, {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ⏱️ Temporal Patterns")
            st.write(f"📅 Active days: **{int(features['active_days'])}**")
            st.write(f"🔄 Unique sessions: **{int(features['unique_sessions'])}**")
            st.write(f"⏳ Avg time between actions: **{features['avg_time_between_actions']:.0f}s**")
            st.write(f"📊 Actions per minute: **{features['actions_per_minute']:.2f}**")
            
            st.markdown("### 📚 Content Engagement")
            st.write(f"📄 PDF downloads: **{int(features['pdf_downloads'])}**")
            st.write(f"👀 PDF viewed online: **{'Yes' if features['pdf_viewed_online'] else 'No'}**")
            st.write(f"🎥 Video completions: **{int(features['video_completions'])}**")
            st.write(f"📖 Content accessed: **{int(features['content_accessed'])}**")
        
        with col2:
            st.markdown("### 💎 Quality Metrics")
            st.write(f"🎯 Action diversity: **{int(features['action_type_diversity'])} types**")
            st.write(f"🔀 Tab switches: **{int(features['tab_switches'])}**")
            st.write(f"👁️ Focus loss ratio: **{features['focus_loss_ratio']:.1%}**")
            
            st.markdown("### 📝 Assessment Performance")
            st.write(f"✅ Assessments completed: **{int(features['assessments_completed'])}**")
            if features['assessments_completed'] > 0:
                st.write(f"📊 Avg score: **{features['avg_assessment_score']:.1f}%**")
                st.write(f"🏆 High scores: **{int(features['high_assessment_scores'])}**")
    
    st.markdown("---")
    
    # Lecture-by-lecture breakdown
    st.markdown("## 📖 Lecture-Level Engagement")
    
    for lecture in lectures:
        lecture_id = lecture['lecture_id']
        lecture_actions = [a for a in course_actions if a['context'].get('lecture_id') == lecture_id]
        
        if not lecture_actions:
            continue
        
        lecture_result = scorer.predict_engagement_score(
            lecture_actions,
            {'course_id': selected_course, 'lecture_id': lecture_id, 'user_role': 'student'}
        )
        
        with st.expander(f"🎥 {lecture['title']} - Score: {lecture_result['engagement_score']}/100"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Score", f"{lecture_result['engagement_score']}/100")
            with col2:
                st.metric("Level", lecture_result['level'])
            with col3:
                st.metric("Actions", lecture_result['total_actions'])
            
            st.write(f"💡 {lecture_result['explanation']}")
            
            # Action timeline
            if len(lecture_actions) > 1:
                action_df = pd.DataFrame([
                    {
                        'Time': datetime.fromisoformat(a['timestamp']),
                        'Action': a['action_type'].replace('_', ' ').title(),
                        'Category': a['action_category']
                    }
                    for a in lecture_actions[-20:]  # Last 20 actions
                ])
                
                st.markdown("**Recent Activity:**")
                st.dataframe(action_df, use_container_width=True, hide_index=True)


def show_teacher_analytics(user, storage, logger, scorer):
    """Show analytics for teacher - monitor all students"""
    st.markdown("## 👥 Student Engagement Monitoring")
    
    teacher_id = user['user_id']
    
    # Get teacher's courses
    teacher_courses = storage.get_all_courses(teacher_id)
    
    if not teacher_courses:
        st.info("📚 Create courses to monitor student engagement!")
        return
    
    # Course selector
    course_options = {course['course_id']: course['name'] for course in teacher_courses.values()}
    selected_course = st.selectbox("📖 Select Course", options=list(course_options.keys()),
                                   format_func=lambda x: course_options[x])
    
    # Get enrolled students
    course = storage.get_course(selected_course)
    student_ids = course.get('enrolled_students', []) if course else []
    
    if not student_ids:
        st.info("No students enrolled yet.")
        return
    
    st.markdown(f"### 📊 Engagement Overview ({len(student_ids)} students)")
    
    # Calculate engagement for all students
    student_scores = []
    
    for student_id in student_ids:
        # Get student object from storage
        student = storage.get_user(student_id)
        if not student:
            continue
            
        student_actions = logger._get_recent_actions(student_id, limit=2000)
        course_actions = [a for a in student_actions 
                         if a['context'].get('course_id') == selected_course]
        
        if course_actions:
            result = scorer.predict_engagement_score(
                course_actions,
                {'course_id': selected_course, 'user_role': 'student'}
            )
            
            student_scores.append({
                'Student': student.get('full_name', 'Unknown'),
                'Student ID': student_id,
                'Score': result['engagement_score'],
                'Level': result['level'],
                'Actions': result['total_actions'],
                'Confidence': f"{result['confidence']*100:.0f}%"
            })
    
    if not student_scores:
        st.warning("No student activity recorded yet.")
        return
    
    # Create dataframe
    df = pd.DataFrame(student_scores)
    df = df.sort_values('Score', ascending=False)
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_score = df['Score'].mean()
        st.metric("Average Score", f"{avg_score:.1f}/100")
    
    with col2:
        high_engagement = len(df[df['Score'] >= 80])
        st.metric("High Engagement", f"{high_engagement} students")
    
    with col3:
        low_engagement = len(df[df['Score'] < 50])
        st.metric("⚠️ At Risk", f"{low_engagement} students")
    
    with col4:
        total_actions = df['Actions'].sum()
        st.metric("Total Activity", f"{total_actions:,} actions")
    
    st.markdown("---")
    
    # Student table with color coding
    def color_score(row):
        score = row['Score']
        if score >= 80:
            return ['background-color: #d4edda'] * len(row)
        elif score >= 60:
            return ['background-color: #fff3cd'] * len(row)
        elif score >= 40:
            return ['background-color: #ffe5d9'] * len(row)
        else:
            return ['background-color: #f8d7da'] * len(row)
    
    styled_df = df.style.apply(color_score, axis=1)
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
    
    # At-risk students
    if low_engagement > 0:
        st.markdown("### ⚠️ Students Requiring Attention")
        at_risk_df = df[df['Score'] < 50]
        st.dataframe(at_risk_df, use_container_width=True, hide_index=True)
        
        st.warning(f"💡 **Recommendation:** Reach out to these {len(at_risk_df)} student(s) to provide support and encourage participation.")
    
    # Engagement distribution chart
    st.markdown("### 📈 Engagement Distribution")
    
    fig = px.histogram(df, x='Score', nbins=10, 
                       title='Student Engagement Score Distribution',
                       labels={'Score': 'Engagement Score', 'count': 'Number of Students'},
                       color_discrete_sequence=['#1f77b4'])
    st.plotly_chart(fig, use_container_width=True)


def show_admin_analytics(storage, logger, scorer):
    """Show system-wide analytics for admin"""
    st.markdown("## 🌐 System-Wide Analytics")
    
    # Time range selector
    time_range = st.selectbox("📅 Time Range", 
                             options=['Last 24 Hours', 'Last 7 Days', 'Last 30 Days', 'All Time'])
    
    # Get time filter
    now = datetime.now()
    if time_range == 'Last 24 Hours':
        since = now - timedelta(days=1)
    elif time_range == 'Last 7 Days':
        since = now - timedelta(days=7)
    elif time_range == 'Last 30 Days':
        since = now - timedelta(days=30)
    else:
        since = None
    
    # Get all users
    all_users = storage.get_all_users()
    students = [u for u in all_users if u.get('role') == 'student']
    teachers = [u for u in all_users if u.get('role') == 'teacher']
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Students", len(students))
    
    with col2:
        st.metric("Total Teachers", len(teachers))
    
    with col3:
        # Count active users
        active_count = 0
        for student in students:
            actions = logger._get_recent_actions(student['user_id'], limit=10)
            if actions and since:
                recent = [a for a in actions if datetime.fromisoformat(a['timestamp']) > since]
                if recent:
                    active_count += 1
            elif actions and not since:
                active_count += 1
        
        st.metric("Active Students", active_count)
    
    with col4:
        # Calculate total actions
        total_actions = 0
        for student in students[:50]:  # Sample for performance
            actions = logger._get_recent_actions(student['user_id'], limit=100)
            if since:
                actions = [a for a in actions if datetime.fromisoformat(a['timestamp']) > since]
            total_actions += len(actions)
        
        st.metric("Total Actions", f"{total_actions:,}")
    
    st.markdown("---")
    
    # Platform engagement overview
    st.markdown("### 📊 Platform Engagement Overview")
    
    engagement_data = []
    
    for student in students[:100]:  # Limit for performance
        actions = logger._get_recent_actions(student['user_id'], limit=500)
        if since:
            actions = [a for a in actions if datetime.fromisoformat(a['timestamp']) > since]
        
        if actions:
            result = scorer.predict_engagement_score(actions, {'user_role': 'student'})
            engagement_data.append({
                'Student': student.get('full_name', 'Unknown'),
                'Score': result['engagement_score'],
                'Level': result['level'],
                'Actions': len(actions)
            })
    
    if engagement_data:
        df = pd.DataFrame(engagement_data)
        
        # Distribution chart
        fig = px.histogram(df, x='Score', nbins=15,
                          title='Platform-Wide Engagement Distribution',
                          labels={'Score': 'Engagement Score', 'count': 'Students'},
                          color_discrete_sequence=['#1f77b4'])
        st.plotly_chart(fig, use_container_width=True)
        
        # Level breakdown
        level_counts = df['Level'].value_counts()
        fig2 = px.pie(values=level_counts.values, names=level_counts.index,
                     title='Engagement Levels',
                     color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No engagement data available for the selected time range.")


# Main router
def main():
    """Main entry point"""
    auth = get_auth()
    
    if not auth.is_authenticated():
        st.warning("Please log in to view analytics.")
        return
    
    show_engagement_analytics()


if __name__ == "__main__":
    main()
