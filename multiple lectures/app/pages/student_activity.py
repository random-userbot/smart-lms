"""
Student Activity Page
Shows student's own activity tracking and engagement metrics
"""

import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.auth import get_auth
from services.storage import get_storage
from services.activity_tracker import get_activity_tracker
from datetime import datetime, timedelta
import pandas as pd
from io import BytesIO
from collections import defaultdict


def format_timestamp(timestamp_str: str) -> str:
    """Format ISO timestamp to readable format"""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return timestamp_str


def get_event_icon(event_type: str) -> str:
    """Get icon for event type"""
    icons = {
        'login': '🔐',
        'logout': '🚪',
        'lecture_start': '▶️',
        'lecture_end': '⏹️',
        'quiz_start': '📝',
        'quiz_submit': '✅',
        'material_download': '📥',
        'notes_reading': '📖',
        'assignment_interaction': '📋',
        'attendance': '✋',
        'ai_tool_usage': '🤖',
        'tab_switch': '🔄',
        'feedback_given': '💬'
    }
    return icons.get(event_type, '📌')


def show_activity_overview(activities: list):
    """Show overview statistics"""
    st.subheader("📊 Activity Overview")
    
    # Calculate statistics
    total_activities = len(activities)
    
    # Count by event type
    event_counts = defaultdict(int)
    for activity in activities:
        event_counts[activity['event_type']] += 1
    
    # Time-based stats
    if activities:
        activities_sorted = sorted(activities, key=lambda x: x['timestamp'])
        first_activity = format_timestamp(activities_sorted[0]['timestamp'])
        last_activity = format_timestamp(activities_sorted[-1]['timestamp'])
    else:
        first_activity = "N/A"
        last_activity = "N/A"
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Activities", total_activities)
    
    with col2:
        unique_event_types = len(event_counts)
        st.metric("Event Types", unique_event_types)
    
    with col3:
        unique_sessions = len(set(a['session_id'] for a in activities))
        st.metric("Sessions", unique_sessions)
    
    with col4:
        # Count activities in last 7 days
        week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
        recent = [a for a in activities if a['timestamp'] >= week_ago]
        st.metric("Last 7 Days", len(recent))
    
    st.markdown("---")
    
    # Event breakdown
    if event_counts:
        st.markdown("### 📈 Activity Breakdown")
        
        # Create columns for event types
        cols = st.columns(3)
        for idx, (event_type, count) in enumerate(sorted(event_counts.items(), key=lambda x: x[1], reverse=True)):
            with cols[idx % 3]:
                icon = get_event_icon(event_type)
                st.markdown(f"""
                <div style="
                    background: #f0f2f6;
                    border-left: 4px solid #1f77b4;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 5px;
                ">
                    <div style="font-size: 24px;">{icon}</div>
                    <div style="font-weight: bold; margin-top: 5px;">{event_type.replace('_', ' ').title()}</div>
                    <div style="font-size: 20px; color: #1f77b4; font-weight: bold;">{count}</div>
                </div>
                """, unsafe_allow_html=True)


def show_course_specific_activities(activities: list):
    """Show activities grouped by course"""
    st.subheader("📚 Course-Specific Activities")
    
    # Group by course
    course_activities = defaultdict(list)
    for activity in activities:
        course_id = activity.get('event_data', {}).get('course_id')
        if course_id:
            course_activities[course_id].append(activity)
    
    if not course_activities:
        st.info("📭 No course-specific activities recorded yet.")
        return
    
    storage = get_storage()
    
    # Display by course
    for course_id, course_acts in course_activities.items():
        course = storage.get_course(course_id)
        course_name = course['name'] if course else f"Course {course_id}"
        
        with st.expander(f"📚 {course_name} ({len(course_acts)} activities)"):
            # Course-specific statistics
            col1, col2, col3 = st.columns(3)
            
            lecture_starts = len([a for a in course_acts if a['event_type'] == 'lecture_start'])
            quiz_submits = len([a for a in course_acts if a['event_type'] == 'quiz_submit'])
            downloads = len([a for a in course_acts if a['event_type'] == 'material_download'])
            
            with col1:
                st.metric("Lectures Started", lecture_starts)
            with col2:
                st.metric("Quizzes Submitted", quiz_submits)
            with col3:
                st.metric("Materials Downloaded", downloads)
            
            # Recent activities
            st.markdown("**Recent Activities:**")
            recent_acts = sorted(course_acts, key=lambda x: x['timestamp'], reverse=True)[:10]
            
            for act in recent_acts:
                icon = get_event_icon(act['event_type'])
                timestamp = format_timestamp(act['timestamp'])
                event_name = act['event_type'].replace('_', ' ').title()
                st.markdown(f"- {icon} **{event_name}** - {timestamp}")


def show_engagement_metrics(activities: list):
    """Show engagement metrics"""
    st.subheader("💡 Engagement Metrics")
    
    # Calculate engagement metrics
    lecture_activities = [a for a in activities if 'lecture' in a['event_type']]
    quiz_activities = [a for a in activities if 'quiz' in a['event_type']]
    resource_activities = [a for a in activities if a['event_type'] in ['material_download', 'notes_reading']]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            color: white;
        ">
            <h3>🎥 Lecture Engagement</h3>
            <h1>{}</h1>
            <p>lecture interactions</p>
        </div>
        """.format(len(lecture_activities)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            color: white;
        ">
            <h3>📝 Quiz Participation</h3>
            <h1>{}</h1>
            <p>quiz interactions</p>
        </div>
        """.format(len(quiz_activities)), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            color: white;
        ">
            <h3>📚 Resource Usage</h3>
            <h1>{}</h1>
            <p>resource interactions</p>
        </div>
        """.format(len(resource_activities)), unsafe_allow_html=True)


def show_timeline(activities: list):
    """Show activity timeline"""
    st.subheader("📅 Activity Timeline")
    
    # Filter options
    col1, col2 = st.columns([3, 1])
    
    with col1:
        time_filter = st.selectbox(
            "Time Period",
            ['Last 7 Days', 'Last 30 Days', 'All Time'],
            key='timeline_filter'
        )
    
    with col2:
        limit = st.number_input("Show Activities", min_value=10, max_value=100, value=50, step=10)
    
    # Apply time filter
    filtered_activities = activities.copy()
    
    if time_filter != 'All Time':
        cutoff_date = datetime.utcnow()
        if time_filter == 'Last 7 Days':
            cutoff_date -= timedelta(days=7)
        elif time_filter == 'Last 30 Days':
            cutoff_date -= timedelta(days=30)
        
        cutoff_str = cutoff_date.isoformat()
        filtered_activities = [a for a in filtered_activities if a['timestamp'] >= cutoff_str]
    
    # Sort and limit
    filtered_activities.sort(key=lambda x: x['timestamp'], reverse=True)
    filtered_activities = filtered_activities[:limit]
    
    if not filtered_activities:
        st.info("📭 No activities in this time period.")
        return
    
    # Display timeline
    for activity in filtered_activities:
        icon = get_event_icon(activity['event_type'])
        timestamp = format_timestamp(activity['timestamp'])
        event_name = activity['event_type'].replace('_', ' ').title()
        
        with st.expander(f"{icon} {event_name} - {timestamp}"):
            event_data = activity.get('event_data', {})
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Event Details:**")
                st.write(f"- **Type:** {event_name}")
                st.write(f"- **Time:** {timestamp}")
                st.write(f"- **Session:** {activity['session_id'][:8]}...")
            
            with col2:
                st.write("**Additional Information:**")
                for key, value in event_data.items():
                    if key not in ['action']:
                        st.write(f"- **{key.replace('_', ' ').title()}:** {value}")


def main():
    """Main student activity page"""
    # Check authentication
    auth = get_auth()
    user = st.session_state.get('user')
    
    if not user:
        st.error("🚫 Please login to access this page.")
        return
    
    if user['role'] != 'student':
        st.error("🚫 This page is for students only.")
        return
    
    st.title("📊 My Activity Dashboard")
    st.markdown(f"**Welcome, {user['full_name']}!**")
    st.markdown("Track your learning activities, engagement, and progress.")
    st.markdown("---")
    
    # Get student activities
    tracker = get_activity_tracker()
    activities = tracker.get_all_student_activities(user['user_id'])
    
    if not activities:
        st.info("📭 No activities recorded yet. Start engaging with your courses!")
        return
    
    # Export button
    col1, col2 = st.columns([5, 1])
    with col2:
        csv_buffer = BytesIO()
        df = pd.DataFrame(activities)
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        st.download_button(
            label="📥 Export",
            data=csv_buffer,
            file_name=f"my_activities_{user['user_id']}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    # Show tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📚 By Course", "💡 Engagement", "📅 Timeline"])
    
    with tab1:
        show_activity_overview(activities)
    
    with tab2:
        show_course_specific_activities(activities)
    
    with tab3:
        show_engagement_metrics(activities)
    
    with tab4:
        show_timeline(activities)


if __name__ == "__main__":
    main()
