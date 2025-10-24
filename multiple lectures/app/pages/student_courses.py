"""
Smart LMS - Student Courses Page
Display all courses in card format with enrollment status
"""

import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.storage import get_storage
from services.auth import get_auth
import uuid
from datetime import datetime


def render_course_card(course_id, course, is_enrolled, has_pending_request):
    """Render a single course card"""
    
    storage = get_storage()
    
    # Get teacher info
    teacher = storage.get_user(course.get('teacher_id'))
    teacher_name = teacher.get('full_name', 'Unknown') if teacher else 'Unknown'
    
    # Get course statistics
    num_lectures = len(course.get('lectures', []))
    num_students = len(course.get('enrolled_students', []))
    
    # Card styling
    if is_enrolled:
        border_color = "#28a745"  # Green
        status_icon = "✅"
        status_text = "Enrolled"
    elif has_pending_request:
        border_color = "#ffc107"  # Yellow
        status_icon = "⏳"
        status_text = "Pending Approval"
    else:
        border_color = "#6c757d"  # Gray
        status_icon = "📚"
        status_text = "Not Enrolled"
    
    # Create card HTML
    card_html = f"""
    <div style="
        border: 2px solid {border_color};
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    ">
        <div style="display: flex; justify-content: space-between; align-items: start;">
            <div style="flex: 1;">
                <h3 style="margin: 0 0 10px 0; color: #2c3e50;">
                    {status_icon} {course.get('name', 'Untitled Course')}
                </h3>
                <p style="margin: 5px 0; color: #7f8c8d; font-size: 14px;">
                    <strong>Code:</strong> {course.get('code', 'N/A')} | 
                    <strong>Teacher:</strong> {teacher_name}
                </p>
                <p style="margin: 5px 0; color: #7f8c8d; font-size: 14px;">
                    <strong>Department:</strong> {course.get('department', 'N/A')} | 
                    <strong>Credits:</strong> {course.get('credits', 0)}
                </p>
                <p style="margin: 10px 0; color: #34495e; font-size: 14px;">
                    {course.get('description', 'No description available.')}
                </p>
                <p style="margin: 5px 0; color: #95a5a6; font-size: 13px;">
                    📹 {num_lectures} Lectures | 👥 {num_students} Students
                </p>
            </div>
            <div style="
                background-color: {border_color};
                color: white;
                padding: 8px 15px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: bold;
                white-space: nowrap;
            ">
                {status_text}
            </div>
        </div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col3:
        if is_enrolled:
            if st.button("🎓 Continue Learning", key=f"continue_{course_id}", 
                        type="primary", use_container_width=True):
                st.session_state.selected_course = course_id
                st.session_state.page = "lectures"
                st.rerun()
        elif has_pending_request:
            st.button("⏳ Request Pending", key=f"pending_{course_id}", 
                     disabled=True, use_container_width=True)
        else:
            if st.button("📝 Apply for Course", key=f"apply_{course_id}", 
                        use_container_width=True):
                # Create enrollment request
                request_id = f"req_{uuid.uuid4().hex[:8]}"
                student_id = st.session_state.user['user_id']
                
                storage.create_enrollment_request(
                    request_id=request_id,
                    student_id=student_id,
                    course_id=course_id,
                    student_name=st.session_state.user.get('full_name', 'Unknown'),
                    course_name=course.get('name', 'Unknown')
                )
                
                st.success(f"✅ Application submitted for {course.get('name')}!")
                st.balloons()
                st.rerun()


def main():
    """Main student courses page"""
    
    # Check authentication
    auth = get_auth()
    if not auth.is_authenticated():
        st.warning("⚠️ Please login to view courses")
        st.stop()
    
    user = st.session_state.user
    
    if user['role'] != 'student':
        st.error("❌ This page is only for students")
        st.stop()
    
    st.title("📚 Course Catalog")
    
    storage = get_storage()
    
    # Get all public courses
    all_courses = storage.get_all_courses()
    public_courses = {cid: c for cid, c in all_courses.items() if c.get('is_public', True)}
    
    # Get student's enrolled courses
    student_id = user['user_id']
    enrolled_course_ids = [
        cid for cid, c in public_courses.items() 
        if student_id in c.get('enrolled_students', [])
    ]
    
    # Get student's pending requests
    pending_requests = storage.get_enrollment_requests(student_id=student_id, status='pending')
    pending_course_ids = [r['course_id'] for r in pending_requests.values()]
    
    # Tabs for filtering
    tab1, tab2, tab3 = st.tabs(["📖 All Courses", "✅ My Courses", "⏳ Pending Requests"])
    
    with tab1:
        st.subheader("All Available Courses")
        
        # Search bar
        search_query = st.text_input("🔍 Search courses", placeholder="Search by name, code, or department...")
        
        # Filter courses
        filtered_courses = public_courses
        if search_query:
            filtered_courses = {
                cid: c for cid, c in public_courses.items()
                if search_query.lower() in c.get('name', '').lower()
                or search_query.lower() in c.get('code', '').lower()
                or search_query.lower() in c.get('department', '').lower()
                or search_query.lower() in c.get('description', '').lower()
            }
        
        if filtered_courses:
            st.markdown(f"**Showing {len(filtered_courses)} courses**")
            
            for course_id, course in filtered_courses.items():
                is_enrolled = course_id in enrolled_course_ids
                has_pending = course_id in pending_course_ids
                render_course_card(course_id, course, is_enrolled, has_pending)
        else:
            st.info("No courses found matching your search.")
    
    with tab2:
        st.subheader("My Enrolled Courses")
        
        if enrolled_course_ids:
            for course_id in enrolled_course_ids:
                course = public_courses[course_id]
                render_course_card(course_id, course, True, False)
        else:
            st.info("📚 You haven't enrolled in any courses yet. Browse the 'All Courses' tab to apply!")
    
    with tab3:
        st.subheader("Pending Enrollment Requests")
        
        if pending_requests:
            for request_id, request in pending_requests.items():
                course_id = request['course_id']
                if course_id in public_courses:
                    course = public_courses[course_id]
                    
                    st.markdown(f"""
                    **Course:** {course.get('name', 'Unknown')}  
                    **Requested:** {request.get('requested_at', 'Unknown')[:10]}  
                    **Status:** ⏳ Waiting for teacher approval
                    """)
                    st.divider()
        else:
            st.info("You have no pending enrollment requests.")
    
    # Statistics summary
    st.sidebar.markdown("### 📊 My Statistics")
    st.sidebar.metric("Enrolled Courses", len(enrolled_course_ids))
    st.sidebar.metric("Pending Requests", len(pending_requests))
    st.sidebar.metric("Available Courses", len(public_courses))


if __name__ == "__main__":
    main()
