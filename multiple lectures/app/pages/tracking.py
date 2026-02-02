"""
Activity Tracking Page - For Teachers and Admins
Card-based UI for viewing student activities, course tracking, and analytics
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
        'feedback_given': '💬',
        'teacher_action': '👨‍🏫'
    }
    return icons.get(event_type, '📌')


def render_course_card(course_id: str, course: dict):
    """Render clickable course card"""
    enrolled_count = len(course.get('enrolled_students', []))
    
    with st.container():
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            cursor: pointer;
            transition: transform 0.2s;
        ">
            <h3 style="color: white; margin: 0 0 10px 0;">📚 {course.get('name', 'Untitled Course')}</h3>
            <p style="color: #f0f0f0; margin: 5px 0; font-size: 14px;">
                {course.get('description', 'No description')[:100]}...
            </p>
            <div style="display: flex; justify-content: space-between; margin-top: 15px;">
                <span style="color: white; font-weight: bold;">👥 {enrolled_count} Students</span>
                <span style="color: white;">Course ID: {course_id}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(f"View Students", key=f"course_btn_{course_id}", type="primary", use_container_width=True):
            st.session_state.tracking_selected_course = course_id
            st.rerun()


def render_student_row(student_id: str, student_name: str, recent_activity_count: int):
    """Render clickable student row in table"""
    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
    
    with col1:
        st.markdown(f"**{student_name}**")
    
    with col2:
        st.markdown(f"ID: `{student_id}`")
    
    with col3:
        st.markdown(f"📊 {recent_activity_count} activities (7d)")
    
    with col4:
        if st.button("View", key=f"student_btn_{student_id}", type="secondary"):
            st.session_state.tracking_selected_student = student_id
            st.rerun()


def show_activity_log(activities: list, show_filters: bool = True):
    """Show chronological activity log with filters"""
    if not activities:
        st.info("📭 No activities recorded yet.")
        return
    
    # Filters
    if show_filters:
        col1, col2, col3 = st.columns([2, 2, 2])
        
        with col1:
            event_types = list(set(a['event_type'] for a in activities))
            selected_event = st.selectbox(
                "Filter by Event Type",
                ['All'] + event_types,
                key='event_filter'
            )
        
        with col2:
            date_filter = st.selectbox(
                "Time Period",
                ['All Time', 'Last 24 Hours', 'Last 7 Days', 'Last 30 Days'],
                key='date_filter'
            )
        
        with col3:
            sort_order = st.selectbox(
                "Sort Order",
                ['Newest First', 'Oldest First'],
                key='sort_filter'
            )
        
        # Apply filters
        filtered_activities = activities.copy()
        
        if selected_event != 'All':
            filtered_activities = [a for a in filtered_activities if a['event_type'] == selected_event]
        
        if date_filter != 'All Time':
            cutoff_date = datetime.utcnow()
            if date_filter == 'Last 24 Hours':
                cutoff_date -= timedelta(days=1)
            elif date_filter == 'Last 7 Days':
                cutoff_date -= timedelta(days=7)
            elif date_filter == 'Last 30 Days':
                cutoff_date -= timedelta(days=30)
            
            cutoff_str = cutoff_date.isoformat()
            filtered_activities = [a for a in filtered_activities if a['timestamp'] >= cutoff_str]
        
        # Sort
        reverse = (sort_order == 'Newest First')
        filtered_activities.sort(key=lambda x: x['timestamp'], reverse=reverse)
        
        st.markdown("---")
    else:
        filtered_activities = activities
        filtered_activities.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Activities", len(filtered_activities))
    
    with col2:
        unique_events = len(set(a['event_type'] for a in filtered_activities))
        st.metric("Event Types", unique_events)
    
    with col3:
        unique_sessions = len(set(a['session_id'] for a in filtered_activities))
        st.metric("Sessions", unique_sessions)
    
    with col4:
        if filtered_activities:
            latest = format_timestamp(filtered_activities[0]['timestamp'])
            st.metric("Latest Activity", latest.split()[1])
    
    st.markdown("---")
    
    # Display activities
    st.subheader("📋 Activity Timeline")
    
    for activity in filtered_activities[:100]:  # Limit to 100 for performance
        event_icon = get_event_icon(activity['event_type'])
        timestamp = format_timestamp(activity['timestamp'])
        
        with st.expander(f"{event_icon} {activity['event_type'].replace('_', ' ').title()} - {timestamp}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Event Details:**")
                st.write(f"- **Event Type:** {activity['event_type']}")
                st.write(f"- **User ID:** {activity['user_id']}")
                st.write(f"- **Role:** {activity['role']}")
                st.write(f"- **Session ID:** {activity['session_id'][:8]}...")
            
            with col2:
                st.write("**Event Data:**")
                event_data = activity.get('event_data', {})
                for key, value in event_data.items():
                    st.write(f"- **{key.replace('_', ' ').title()}:** {value}")
    
    if len(filtered_activities) > 100:
        st.info(f"📊 Showing first 100 of {len(filtered_activities)} activities. Use filters to narrow down.")


def show_student_tracking_view():
    """Show detailed student activity tracking"""
    student_id = st.session_state.tracking_selected_student
    course_id = st.session_state.tracking_selected_course
    
    # Get student info
    storage = get_storage()
    all_users = storage.get_all_users()
    student = all_users.get(student_id)
    
    if not student:
        st.error("Student not found")
        return
    
    # Back button
    if st.button("← Back to Students"):
        del st.session_state.tracking_selected_student
        st.rerun()
    
    st.title(f"👤 Student Activity: {student['full_name']}")
    st.markdown(f"**Student ID:** `{student_id}`  |  **Email:** {student.get('email', 'N/A')}")
    st.markdown("---")
    
    # Get activities
    tracker = get_activity_tracker()
    activities = tracker.get_student_activities_in_course(course_id, student_id)
    
    if not activities:
        st.info("📭 No activities recorded for this student in this course.")
        return
    
    # Export button
    col1, col2 = st.columns([5, 1])
    with col2:
        csv_buffer = BytesIO()
        df = pd.DataFrame(activities)
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        st.download_button(
            label="📥 Export CSV",
            data=csv_buffer,
            file_name=f"student_{student_id}_activities.csv",
            mime="text/csv"
        )
    
    # Show activity log
    show_activity_log(activities)


def show_students_list():
    """Show list of students in selected course"""
    course_id = st.session_state.tracking_selected_course
    
    storage = get_storage()
    course = storage.get_course(course_id)
    
    if not course:
        st.error("Course not found")
        return
    
    # Back button
    if st.button("← Back to Courses"):
        del st.session_state.tracking_selected_course
        st.rerun()
    
    st.title(f"📚 {course['name']}")
    st.markdown(f"*Course ID: {course_id}*")
    st.markdown("---")
    
    # Get enrolled students
    enrolled_students = course.get('enrolled_students', [])
    
    if not enrolled_students:
        st.info("👥 No students enrolled in this course yet.")
        return
    
    # Get all users
    all_users = storage.get_all_users()
    tracker = get_activity_tracker()
    
    # Show student count
    st.markdown(f"### 👥 Enrolled Students ({len(enrolled_students)})")
    st.markdown("Click on a student to view their activity tracking.")
    st.markdown("---")
    
    # Get recent activity counts
    student_activities = {}
    for student_id in enrolled_students:
        activities = tracker.get_student_activities_in_course(course_id, student_id)
        # Count activities in last 7 days
        week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
        recent = [a for a in activities if a['timestamp'] >= week_ago]
        student_activities[student_id] = len(recent)
    
    # Render student table (clickable rows)
    for student_id in enrolled_students:
        student = all_users.get(student_id)
        if student:
            student_name = student.get('full_name', 'Unknown')
            recent_count = student_activities.get(student_id, 0)
            
            render_student_row(student_id, student_name, recent_count)
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)


def show_courses_grid():
    """Show grid of course cards for teacher"""
    user = st.session_state.user
    storage = get_storage()
    
    # Get teacher's courses
    if user['role'] == 'admin':
        courses = storage.get_all_courses()
    else:
        courses = storage.get_all_courses(teacher_id=user['user_id'])
    
    if not courses:
        st.info("📚 No courses found. Create a course first.")
        return
    
    st.markdown("### 📚 Your Courses")
    st.markdown("Click on a course to view enrolled students and their activities.")
    st.markdown("---")
    
    # Render course cards in grid
    cols_per_row = 2
    course_items = list(courses.items())
    
    for i in range(0, len(course_items), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            if i + j < len(course_items):
                course_id, course = course_items[i + j]
                with col:
                    render_course_card(course_id, course)


def main():
    """Main tracking page"""
    # Check authentication and authorization
    auth = get_auth()
    user = st.session_state.get('user')
    
    if not user:
        st.error("🚫 Please login to access this page.")
        return
    
    if user['role'] not in ['teacher', 'admin']:
        st.error("🚫 Access Denied. This page is for teachers and administrators only.")
        return
    
    st.title("📊 Activity Tracking Dashboard")
    st.markdown("Monitor student activities, engagement, and course analytics in real-time.")
    st.markdown("---")
    
    # Check navigation state
    if 'tracking_selected_student' in st.session_state:
        # Show student detail view
        show_student_tracking_view()
    elif 'tracking_selected_course' in st.session_state:
        # Show students list
        show_students_list()
    else:
        # Show courses grid
        show_courses_grid()


if __name__ == "__main__":
    main()
