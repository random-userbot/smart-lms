"""
Smart LMS - Unified Course Management
Consolidated page for: Course Management, Content Upload, Resources, Quiz Creation
Teachers can manage all course-related activities from one place
"""

import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.auth import get_auth
from services.storage import get_storage
from services.activity_tracker import get_activity_tracker
from datetime import datetime
import shutil
from pathlib import Path

UPLOAD_FOLDER = 'uploaded_files'
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB


def render_course_card(course_id: str, course: dict, on_select_callback):
    """Render course card for selection"""
    enrolled_count = len(course.get('enrolled_students', []))
    
    gradients = [
        "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
        "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
        "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
        "linear-gradient(135deg, #fa709a 0%, #fee140 100%)",
    ]
    gradient = gradients[hash(course_id) % len(gradients)]
    
    st.markdown(f"""
    <div style="
        background: {gradient};
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        transition: transform 0.2s;
        cursor: pointer;
    ">
        <h3 style="color: white; margin: 0 0 12px 0;">📚 {course.get('name', 'Untitled Course')}</h3>
        <p style="color: #f5f5f5; margin: 8px 0; font-size: 15px;">
            {course.get('description', 'No description')[:120]}...
        </p>
        <div style="display: flex; justify-content: space-between; margin-top: 18px;">
            <span style="color: white; font-weight: bold;">👥 {enrolled_count} Students</span>
            <span style="color: white; font-size: 13px;">ID: {course_id}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("📝 Manage", key=f"manage_{course_id}", use_container_width=True):
            on_select_callback(course_id, 'manage')
    with col2:
        if st.button("📤 Upload", key=f"upload_{course_id}", use_container_width=True):
            on_select_callback(course_id, 'upload')
    with col3:
        if st.button("📊 Quiz", key=f"quiz_{course_id}", use_container_width=True):
            on_select_callback(course_id, 'quiz')
    with col4:
        if st.button("👥 Students", key=f"students_{course_id}", use_container_width=True):
            on_select_callback(course_id, 'students')


def show_course_overview_tab(user, storage):
    """Overview of all courses with quick actions"""
    st.markdown("## 📚 My Courses")
    
    # Get teacher's courses
    all_courses = storage.get_all_courses()
    teacher_courses = {cid: c for cid, c in all_courses.items() 
                      if c.get('teacher_id') == user['user_id']}
    
    if not teacher_courses:
        st.info("📚 You haven't created any courses yet. Create your first course below!")
        
        with st.expander("➕ Create New Course", expanded=True):
            show_create_course_form(user, storage)
        return
    
    # Course statistics
    col1, col2, col3, col4 = st.columns(4)
    
    total_students = sum(len(c.get('enrolled_students', [])) for c in teacher_courses.values())
    total_lectures = sum(len(c.get('lectures', [])) for c in teacher_courses.values())
    
    with col1:
        st.metric("Total Courses", len(teacher_courses))
    with col2:
        st.metric("Total Students", total_students)
    with col3:
        st.metric("Total Lectures", total_lectures)
    with col4:
        avg_students = total_students / len(teacher_courses) if teacher_courses else 0
        st.metric("Avg Students/Course", f"{avg_students:.1f}")
    
    st.markdown("---")
    
    # Create new course button
    if st.button("➕ Create New Course", type="primary", use_container_width=True):
        st.session_state.show_create_course = True
        st.rerun()
    
    if st.session_state.get('show_create_course'):
        with st.expander("Create New Course", expanded=True):
            show_create_course_form(user, storage)
            if st.button("Cancel", key="cancel_create"):
                st.session_state.show_create_course = False
                st.rerun()
    
    st.markdown("---")
    st.markdown("### 📋 Your Courses")
    
    # Display courses as cards
    def handle_course_action(course_id, action):
        st.session_state.selected_course_manage = course_id
        st.session_state.course_action = action
        st.rerun()
    
    cols = st.columns(2)
    for idx, (course_id, course) in enumerate(teacher_courses.items()):
        with cols[idx % 2]:
            render_course_card(course_id, course, handle_course_action)


def show_create_course_form(user, storage):
    """Form to create a new course"""
    st.markdown("### ➕ Create New Course")
    
    with st.form("create_course_form"):
        course_name = st.text_input("Course Name *", placeholder="e.g., Introduction to Python Programming")
        course_code = st.text_input("Course Code", placeholder="e.g., CS101")
        description = st.text_area("Course Description *", placeholder="Brief description of the course", height=100)
        
        col1, col2 = st.columns(2)
        with col1:
            category = st.text_input("Category", placeholder="e.g., Programming")
        with col2:
            difficulty = st.selectbox("Difficulty Level", ["Beginner", "Intermediate", "Advanced"])
        
        submit = st.form_submit_button("Create Course", type="primary", use_container_width=True)
        
        if submit:
            if not course_name or not description:
                st.error("❌ Course name and description are required!")
                return
            
            # Create course
            course_id = storage.create_course(
                teacher_id=user['user_id'],
                name=course_name,
                description=description,
                course_code=course_code,
                category=category,
                difficulty=difficulty
            )
            
            if course_id:
                st.success(f"✅ Course '{course_name}' created successfully!")
                
                # Track activity
                tracker = get_activity_tracker()
                tracker.track_activity(
                    user_id=user['user_id'],
                    action_type='course_created',
                    details={'course_id': course_id, 'course_name': course_name}
                )
                
                st.session_state.show_create_course = False
                st.rerun()
            else:
                st.error("❌ Failed to create course. Please try again.")


def show_manage_lectures_tab(user, storage):
    """Manage lectures, materials, and resources for a course"""
    st.markdown("## 📚 Manage Course Content")
    
    # Get teacher's courses
    all_courses = storage.get_all_courses()
    teacher_courses = {cid: c for cid, c in all_courses.items() 
                      if c.get('teacher_id') == user['user_id']}
    
    if not teacher_courses:
        st.info("Create a course first to manage content.")
        return
    
    # Course selection
    selected_course = st.session_state.get('selected_course_content')
    
    if not selected_course:
        st.markdown("### 📚 Select a Course")
        
        def select_course(course_id, action):
            st.session_state.selected_course_content = course_id
            st.rerun()
        
        cols = st.columns(2)
        for idx, (course_id, course) in enumerate(teacher_courses.items()):
            with cols[idx % 2]:
                render_course_card(course_id, course, select_course)
        return
    
    # Selected course management
    course = teacher_courses.get(selected_course)
    if not course:
        st.error("Course not found")
        if st.button("← Back"):
            st.session_state.selected_course_content = None
            st.rerun()
        return
    
    # Back button
    if st.button("← Back to Courses"):
        st.session_state.selected_course_content = None
        st.rerun()
    
    st.markdown(f"### 📚 {course.get('name')}")
    st.markdown("---")
    
    # Sub-tabs for different content types
    content_tabs = st.tabs(["📹 Lectures", "📄 Materials", "📋 Assignments"])
    
    with content_tabs[0]:
        show_lecture_management(user, storage, selected_course, course)
    
    with content_tabs[1]:
        show_material_management(user, storage, selected_course, course)
    
    with content_tabs[2]:
        show_assignment_management(user, storage, selected_course, course)


def show_lecture_management(user, storage, course_id, course):
    """Manage lectures for a course"""
    st.markdown("#### 📹 Lecture Management")
    
    # Upload new lecture button
    if st.button("➕ Upload New Lecture", type="primary"):
        st.session_state.show_upload_lecture = True
    
    if st.session_state.get('show_upload_lecture'):
        with st.expander("Upload Lecture", expanded=True):
            show_upload_lecture_form(user, storage, course_id)
            if st.button("Cancel Upload", key="cancel_lecture"):
                st.session_state.show_upload_lecture = False
                st.rerun()
    
    # Display existing lectures
    lectures = course.get('lectures', [])
    
    if not lectures:
        st.info("No lectures uploaded yet.")
        return
    
    st.markdown(f"**{len(lectures)} Lectures**")
    
    for lecture in lectures:
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"**{lecture.get('title', 'Untitled')}**")
                st.caption(f"Duration: {lecture.get('duration', 'Unknown')} | Uploaded: {lecture.get('created_at', '')[:10]}")
            
            with col2:
                if st.button("✏️ Edit", key=f"edit_lec_{lecture.get('lecture_id')}"):
                    st.session_state.edit_lecture = lecture.get('lecture_id')
                    st.rerun()
            
            with col3:
                if st.button("🗑️ Delete", key=f"del_lec_{lecture.get('lecture_id')}"):
                    if storage.delete_lecture(course_id, lecture.get('lecture_id')):
                        st.success("Lecture deleted")
                        st.rerun()
            
            st.markdown("---")


def show_upload_lecture_form(user, storage, course_id):
    """Form to upload a new lecture"""
    st.markdown("### Upload Lecture")
    
    with st.form("upload_lecture_form"):
        title = st.text_input("Lecture Title *", placeholder="e.g., Introduction to Variables")
        description = st.text_area("Description", placeholder="Brief description of the lecture")
        
        video_file = st.file_uploader("Upload Video *", type=['mp4', 'avi', 'mov', 'mkv'])
        transcript_file = st.file_uploader("Upload Transcript (Optional)", type=['txt', 'pdf'])
        
        col1, col2 = st.columns(2)
        with col1:
            duration = st.text_input("Duration (e.g., 45min)", placeholder="45min")
        with col2:
            order = st.number_input("Lecture Order", min_value=1, value=1)
        
        submit = st.form_submit_button("Upload Lecture", type="primary")
        
        if submit:
            if not title or not video_file:
                st.error("Title and video file are required!")
                return
            
            with st.spinner("Uploading lecture..."):
                # Create uploads directory
                upload_dir = Path(UPLOAD_FOLDER) / 'lectures' / course_id
                upload_dir.mkdir(parents=True, exist_ok=True)
                
                # Save video file
                video_path = upload_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{video_file.name}"
                with open(video_path, 'wb') as f:
                    f.write(video_file.getbuffer())
                
                # Save transcript if provided
                transcript_path = None
                if transcript_file:
                    transcript_path = upload_dir / f"transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{transcript_file.name}"
                    with open(transcript_path, 'wb') as f:
                        f.write(transcript_file.getbuffer())
                
                # Create lecture in storage
                lecture_id = storage.add_lecture(
                    course_id=course_id,
                    title=title,
                    description=description,
                    video_path=str(video_path),
                    transcript_path=str(transcript_path) if transcript_path else None,
                    duration=duration,
                    order=order
                )
                
                if lecture_id:
                    st.success("✅ Lecture uploaded successfully!")
                    
                    # Track activity
                    tracker = get_activity_tracker()
                    tracker.track_activity(
                        user_id=user['user_id'],
                        action_type='lecture_uploaded',
                        details={'course_id': course_id, 'lecture_id': lecture_id, 'title': title}
                    )
                    
                    st.session_state.show_upload_lecture = False
                    st.rerun()
                else:
                    st.error("Failed to create lecture")


def show_material_management(user, storage, course_id, course):
    """Manage course materials"""
    st.markdown("#### 📄 Course Materials")
    
    if st.button("➕ Upload Material", type="primary"):
        st.session_state.show_upload_material = True
    
    if st.session_state.get('show_upload_material'):
        with st.expander("Upload Material", expanded=True):
            show_upload_material_form(user, storage, course_id)
            if st.button("Cancel Material", key="cancel_material"):
                st.session_state.show_upload_material = False
                st.rerun()
    
    # Display materials
    materials = course.get('materials', [])
    
    if not materials:
        st.info("No materials uploaded yet.")
        return
    
    st.markdown(f"**{len(materials)} Materials**")
    
    for material in materials:
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"📄 **{material.get('title', 'Untitled')}**")
                st.caption(f"Type: {material.get('type', 'Unknown')} | Uploaded: {material.get('created_at', '')[:10]}")
            
            with col2:
                # Download button
                if st.button("⬇️ Download", key=f"dl_mat_{material.get('material_id')}"):
                    file_path = material.get('file_path')
                    if file_path and os.path.exists(file_path):
                        with open(file_path, 'rb') as f:
                            st.download_button(
                                "Download File",
                                data=f.read(),
                                file_name=os.path.basename(file_path),
                                key=f"dl_btn_{material.get('material_id')}"
                            )
            
            with col3:
                if st.button("🗑️ Delete", key=f"del_mat_{material.get('material_id')}"):
                    if storage.delete_material(course_id, material.get('material_id')):
                        st.success("Material deleted")
                        st.rerun()
            
            st.markdown("---")


def show_upload_material_form(user, storage, course_id):
    """Form to upload material"""
    with st.form("upload_material_form"):
        title = st.text_input("Material Title *")
        description = st.text_area("Description")
        material_type = st.selectbox("Type", ["PDF", "Document", "Slides", "Notes", "Other"])
        file = st.file_uploader("Upload File *", type=['pdf', 'docx', 'pptx', 'txt'])
        
        submit = st.form_submit_button("Upload Material")
        
        if submit:
            if not title or not file:
                st.error("Title and file are required!")
                return
            
            with st.spinner("Uploading..."):
                upload_dir = Path(UPLOAD_FOLDER) / 'materials' / course_id
                upload_dir.mkdir(parents=True, exist_ok=True)
                
                file_path = upload_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.name}"
                with open(file_path, 'wb') as f:
                    f.write(file.getbuffer())
                
                material_id = storage.add_material(
                    course_id=course_id,
                    title=title,
                    description=description,
                    material_type=material_type,
                    file_path=str(file_path)
                )
                
                if material_id:
                    st.success("✅ Material uploaded successfully!")
                    st.session_state.show_upload_material = False
                    st.rerun()


def show_assignment_management(user, storage, course_id, course):
    """Manage assignments"""
    st.markdown("#### 📋 Assignments")
    
    if st.button("➕ Create Assignment", type="primary"):
        st.session_state.show_create_assignment = True
    
    if st.session_state.get('show_create_assignment'):
        with st.expander("Create Assignment", expanded=True):
            show_create_assignment_form(user, storage, course_id)
            if st.button("Cancel Assignment", key="cancel_assign"):
                st.session_state.show_create_assignment = False
                st.rerun()
    
    assignments = course.get('assignments', [])
    
    if not assignments:
        st.info("No assignments created yet.")
        return
    
    st.markdown(f"**{len(assignments)} Assignments**")
    
    for assignment in assignments:
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"📋 **{assignment.get('title', 'Untitled')}**")
                due_date = assignment.get('due_date', 'No deadline')
                st.caption(f"Due: {due_date} | Points: {assignment.get('max_points', 100)}")
            
            with col2:
                if st.button("🗑️ Delete", key=f"del_assign_{assignment.get('assignment_id')}"):
                    if storage.delete_assignment(course_id, assignment.get('assignment_id')):
                        st.success("Assignment deleted")
                        st.rerun()
            
            st.markdown("---")


def show_create_assignment_form(user, storage, course_id):
    """Form to create assignment"""
    with st.form("create_assignment_form"):
        title = st.text_input("Assignment Title *")
        description = st.text_area("Description *")
        due_date = st.date_input("Due Date")
        max_points = st.number_input("Maximum Points", min_value=1, value=100)
        
        submit = st.form_submit_button("Create Assignment")
        
        if submit:
            if not title or not description:
                st.error("Title and description are required!")
                return
            
            assignment_id = storage.create_assignment(
                course_id=course_id,
                title=title,
                description=description,
                due_date=str(due_date),
                max_points=max_points
            )
            
            if assignment_id:
                st.success("✅ Assignment created successfully!")
                st.session_state.show_create_assignment = False
                st.rerun()


def show_course_management():
    """Main unified course management page"""
    st.title("📚 Course Management Hub")
    st.markdown("Manage your courses, upload content, create quizzes, and monitor students")
    st.markdown("---")
    
    auth = get_auth()
    if not auth.is_authenticated():
        st.warning("Please log in to manage courses.")
        return
    
    user = st.session_state.user
    storage = get_storage()
    
    if user['role'] != 'teacher':
        st.error("🚫 Access denied. This page is for teachers only.")
        return
    
    # Main tabs
    tabs = st.tabs(["📚 My Courses", "📤 Upload Content", "👥 Manage Students"])
    
    with tabs[0]:
        show_course_overview_tab(user, storage)
    
    with tabs[1]:
        show_manage_lectures_tab(user, storage)
    
    with tabs[2]:
        st.markdown("## 👥 Manage Students")
        st.info("Student management features coming soon. For now, approve enrollment requests from the Enrollment Requests page.")
