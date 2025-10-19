"""
Smart LMS - Attendance Tracking Page
View and manage attendance records
"""

import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.auth import get_auth
from services.storage import get_storage
from services.ui_theme import get_theme_manager
import plotly.express as px
import pandas as pd
from datetime import datetime


def create_attendance_heatmap(attendance_data):
    """Create attendance heatmap"""
    if not attendance_data:
        return None
    
    # Prepare data for heatmap
    df = pd.DataFrame(attendance_data)
    
    if df.empty:
        return None
    
    # Create pivot table
    pivot = df.pivot_table(
        values='presence_percentage',
        index='student_id',
        columns='lecture_id',
        aggfunc='mean'
    )
    
    fig = px.imshow(
        pivot,
        labels=dict(x="Lecture", y="Student", color="Attendance %"),
        color_continuous_scale='RdYlGn',
        title='Attendance Heatmap'
    )
    
    return fig


def show_student_attendance():
    """Show attendance for student"""
    storage = get_storage()
    user = st.session_state.user
    theme = get_theme_manager()
    
    st.title("📅 My Attendance")
    
    # Get student's attendance records
    attendance_records = storage.get_attendance(student_id=user['user_id'])
    
    if not attendance_records:
        st.info("📝 No attendance records yet. Attend lectures to see your attendance.")
        return
    
    # Overall statistics
    total_records = len(attendance_records)
    present_count = sum(1 for r in attendance_records if r['status'] == 'present')
    avg_presence = sum(r['presence_percentage'] for r in attendance_records) / total_records
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Lectures", total_records)
    
    with col2:
        attendance_rate = (present_count / total_records * 100) if total_records > 0 else 0
        st.metric("Attendance Rate", f"{attendance_rate:.1f}%")
    
    with col3:
        st.metric("Avg Presence", f"{avg_presence:.1f}%")
    
    st.markdown("---")
    
    # Attendance by course
    st.markdown("### 📚 Attendance by Course")
    
    # Group by course
    course_attendance = {}
    for record in attendance_records:
        lecture = storage.get_lecture(record['lecture_id'])
        if lecture:
            course_id = lecture['course_id']
            if course_id not in course_attendance:
                course_attendance[course_id] = []
            course_attendance[course_id].append(record)
    
    for course_id, records in course_attendance.items():
        course = storage.get_course(course_id)
        if course:
            with st.expander(f"📖 {course['name']}", expanded=True):
                present = sum(1 for r in records if r['status'] == 'present')
                total = len(records)
                rate = (present / total * 100) if total > 0 else 0
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.progress(rate / 100)
                    st.caption(f"Attendance: {rate:.1f}% ({present}/{total} lectures)")
                
                with col2:
                    if rate >= 75:
                        st.success("✅ Good")
                    elif rate >= 50:
                        st.warning("⚠️ Fair")
                    else:
                        st.error("❌ Poor")
    
    # Detailed records
    st.markdown("---")
    st.markdown("### 📋 Detailed Records")
    
    # Create dataframe
    records_data = []
    for record in attendance_records:
        lecture = storage.get_lecture(record['lecture_id'])
        if lecture:
            course = storage.get_course(lecture['course_id'])
            records_data.append({
                'Date': record['recorded_at'][:10],
                'Course': course['name'] if course else 'Unknown',
                'Lecture': lecture['title'],
                'Presence': f"{record['presence_percentage']:.1f}%",
                'Status': record['status'].capitalize()
            })
    
    if records_data:
        df = pd.DataFrame(records_data)
        st.dataframe(df, use_container_width=True)


def show_teacher_attendance():
    """Show attendance overview for teacher"""
    storage = get_storage()
    user = st.session_state.user
    
    st.title("📅 Student Attendance")
    
    # Get teacher's courses
    courses = storage.get_all_courses(teacher_id=user['user_id'])
    
    if not courses:
        st.info("📝 No courses assigned yet.")
        return
    
    # Course selection
    course_options = {cid: c['name'] for cid, c in courses.items()}
    selected_course = st.selectbox(
        "Select Course",
        options=list(course_options.keys()),
        format_func=lambda x: course_options[x]
    )
    
    course = courses[selected_course]
    st.markdown(f"### 📖 {course['name']}")
    
    # Get lectures for this course
    lectures = storage.get_course_lectures(selected_course)
    
    if not lectures:
        st.info("📝 No lectures available yet.")
        return
    
    # Get attendance for all students in this course
    all_attendance = []
    for lecture in lectures:
        lecture_attendance = storage.get_attendance(lecture_id=lecture['lecture_id'])
        all_attendance.extend(lecture_attendance)
    
    if not all_attendance:
        st.info("📝 No attendance records yet.")
        return
    
    # Statistics
    enrolled_students = course.get('enrolled_students', [])
    total_students = len(enrolled_students)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Enrolled Students", total_students)
    
    with col2:
        present_count = sum(1 for r in all_attendance if r['status'] == 'present')
        total_records = len(all_attendance)
        avg_attendance = (present_count / total_records * 100) if total_records > 0 else 0
        st.metric("Avg Attendance", f"{avg_attendance:.1f}%")
    
    with col3:
        st.metric("Total Lectures", len(lectures))
    
    st.markdown("---")
    
    # Attendance by lecture
    st.markdown("### 📊 Attendance by Lecture")
    
    for lecture in lectures:
        lecture_attendance = storage.get_attendance(lecture_id=lecture['lecture_id'])
        
        with st.expander(f"🎥 {lecture['title']}", expanded=False):
            if lecture_attendance:
                present = sum(1 for r in lecture_attendance if r['status'] == 'present')
                total = len(lecture_attendance)
                rate = (present / total * 100) if total > 0 else 0
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.progress(rate / 100)
                    st.caption(f"Attendance: {rate:.1f}% ({present}/{total} students)")
                
                with col2:
                    if rate >= 75:
                        st.success("✅ Good")
                    elif rate >= 50:
                        st.warning("⚠️ Fair")
                    else:
                        st.error("❌ Poor")
                
                # Student list
                st.markdown("**Students:**")
                for record in lecture_attendance:
                    student = storage.get_user(record['student_id'])
                    if student:
                        status_icon = "✅" if record['status'] == 'present' else "❌"
                        st.markdown(f"{status_icon} {student['full_name']} - {record['presence_percentage']:.1f}%")
            else:
                st.info("No attendance records yet")


def main():
    """Main attendance page"""
    # Check authentication
    auth = get_auth()
    
    # Apply theme
    theme = get_theme_manager()
    theme.apply_theme()
    
    # Check role
    user = st.session_state.user
    role = user['role']
    
    if role == 'student':
        show_student_attendance()
    elif role == 'teacher':
        show_teacher_attendance()
    elif role == 'admin':
        st.title("📅 Attendance Management")
        st.info("Admin attendance overview coming soon!")
    else:
        st.error("Access denied")


if __name__ == "__main__":
    main()
