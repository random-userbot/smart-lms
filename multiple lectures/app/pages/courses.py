"""
Smart LMS - Course Management Page
For admin and teachers to manage courses and resources
"""

import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.storage import get_storage
from datetime import datetime
import uuid


def show_course_statistics():
    """Display course statistics"""
    storage = get_storage()
    user = st.session_state.user
    
    if user['role'] == 'admin':
        courses = storage.get_all_courses()
        title = "📊 All Courses Statistics"
    else:
        courses = storage.get_all_courses(teacher_id=user['user_id'])
        title = "📊 My Courses Statistics"
    
    st.subheader(title)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📚 Total Courses", len(courses))
    
    with col2:
        total_students = sum(len(c.get('enrolled_students', [])) for c in courses.values())
        st.metric("👥 Total Students", total_students)
    
    with col3:
        total_lectures = sum(len(c.get('lectures', [])) for c in courses.values())
        st.metric("🎥 Total Lectures", total_lectures)
    
    with col4:
        active_courses = sum(1 for c in courses.values() if c.get('is_active', True))
        st.metric("✅ Active Courses", active_courses)


def show_course_list():
    """Display and manage course list"""
    storage = get_storage()
    user = st.session_state.user
    
    st.subheader("📚 Course Management")
    
    # Filter and search options
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        if user['role'] == 'admin':
            # Admin can filter by teacher
            all_teachers = storage.get_all_users(role='teacher')
            teacher_options = {"all": "All Teachers"}
            teacher_options.update({tid: t.get('full_name', t['username']) for tid, t in all_teachers.items()})
            
            teacher_filter = st.selectbox("Filter by Teacher", options=list(teacher_options.keys()),
                                        format_func=lambda x: teacher_options[x])
        else:
            teacher_filter = user['user_id']
    
    with col2:
        search_query = st.text_input("🔍 Search courses", placeholder="Search by name...")
    
    with col3:
        st.write("")  # Spacing
        st.write("")
        if st.button("➕ Create Course", type="primary", use_container_width=True):
            st.session_state.show_create_course = True
            st.rerun()
    
    # Get courses based on filter
    if user['role'] == 'admin' and teacher_filter == 'all':
        courses = storage.get_all_courses()
    elif user['role'] == 'admin':
        courses = storage.get_all_courses(teacher_id=teacher_filter)
    else:
        courses = storage.get_all_courses(teacher_id=user['user_id'])
    
    # Apply search filter
    if search_query:
        courses = {
            cid: c for cid, c in courses.items()
            if search_query.lower() in c.get('name', '').lower()
            or search_query.lower() in c.get('description', '').lower()
        }
    
    # Display courses
    if courses:
        st.markdown(f"**Showing {len(courses)} courses**")
        
        for course_id, course in courses.items():
            with st.expander(f"📖 {course['name']} ({course_id})"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Course ID:** {course_id}")
                    st.write(f"**Description:** {course.get('description', 'No description')}")
                    
                    # Get teacher info
                    teacher = storage.get_user(course.get('teacher_id', ''))
                    teacher_name = teacher.get('full_name', teacher['username']) if teacher else 'Unknown'
                    st.write(f"**Teacher:** {teacher_name}")
                    
                    st.write(f"**Enrolled Students:** {len(course.get('enrolled_students', []))}")
                    st.write(f"**Lectures:** {len(course.get('lectures', []))}")
                    st.write(f"**Status:** {'✅ Active' if course.get('is_active', True) else '❌ Inactive'}")
                    st.write(f"**Created:** {course.get('created_at', 'N/A')[:10]}")
                
                with col2:
                    st.write("")  # Spacing
                    
                    if st.button("✏️ Edit", key=f"edit_{course_id}", use_container_width=True):
                        st.session_state.edit_course_id = course_id
                        st.session_state.show_edit_course = True
                        st.rerun()
                    
                    if st.button("👥 Manage Students", key=f"students_{course_id}", use_container_width=True):
                        st.session_state.manage_course_id = course_id
                        st.session_state.show_manage_students = True
                        st.rerun()
                    
                    if st.button("📄 View Materials", key=f"materials_{course_id}", use_container_width=True):
                        st.session_state.view_materials_course = course_id
                        st.session_state.show_materials = True
                        st.rerun()
                    
                    if course.get('is_active', True):
                        if st.button("🔒 Archive", key=f"archive_{course_id}", use_container_width=True):
                            storage.update_course(course_id, {'is_active': False})
                            st.success(f"Course archived")
                            st.rerun()
                    else:
                        if st.button("✅ Activate", key=f"activate_{course_id}", use_container_width=True):
                            storage.update_course(course_id, {'is_active': True})
                            st.success(f"Course activated")
                            st.rerun()
    else:
        st.info("No courses found. Create your first course to get started!")


def show_create_course_form():
    """Form to create new course"""
    st.subheader("➕ Create New Course")
    
    storage = get_storage()
    user = st.session_state.user
    
    with st.form("create_course_form"):
        # Course details
        course_name = st.text_input("Course Name*", placeholder="e.g., Introduction to Machine Learning")
        course_code = st.text_input("Course Code", placeholder="e.g., CS301")
        description = st.text_area("Description*", placeholder="Brief description of the course")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Teacher selection (admin only)
            if user['role'] == 'admin':
                teachers = storage.get_all_users(role='teacher')
                teacher_options = {tid: t.get('full_name', t['username']) for tid, t in teachers.items()}
                
                if teacher_options:
                    teacher_id = st.selectbox("Assign Teacher*", 
                                            options=list(teacher_options.keys()),
                                            format_func=lambda x: teacher_options[x])
                else:
                    st.error("No teachers available. Please create teacher accounts first.")
                    teacher_id = None
            else:
                teacher_id = user['user_id']
                teacher = storage.get_user(teacher_id)
                st.text_input("Teacher", value=teacher.get('full_name', teacher['username']), disabled=True)
            
            semester = st.selectbox("Semester", ["Spring", "Fall", "Summer"])
            year = st.number_input("Year", min_value=2020, max_value=2030, value=datetime.now().year)
        
        with col2:
            department = st.text_input("Department", placeholder="e.g., Computer Science")
            credits = st.number_input("Credits", min_value=1, max_value=10, value=3)
            max_students = st.number_input("Max Students", min_value=10, max_value=500, value=100)
        
        # Additional settings
        st.markdown("#### Course Settings")
        col1, col2 = st.columns(2)
        
        with col1:
            is_active = st.checkbox("Active Course", value=True)
            allow_self_enroll = st.checkbox("Allow Self-Enrollment", value=False)
        
        with col2:
            requires_approval = st.checkbox("Enrollment Requires Approval", value=False)
            is_public = st.checkbox("Public Course (visible to all)", value=True)
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("✅ Create Course", type="primary", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if cancel:
            st.session_state.show_create_course = False
            st.rerun()
        
        if submit:
            # Validation
            if not course_name or not description:
                st.error("❌ Please fill all required fields marked with *")
                return
            
            if user['role'] == 'admin' and not teacher_id:
                st.error("❌ Please assign a teacher to the course")
                return
            
            # Generate course ID
            course_id = course_code.lower().replace(' ', '_') if course_code else f"course_{uuid.uuid4().hex[:8]}"
            
            # Create course
            success = storage.create_course(
                course_id=course_id,
                name=course_name,
                teacher_id=teacher_id,
                description=description,
                code=course_code,
                department=department,
                credits=credits,
                semester=semester,
                year=year,
                max_students=max_students,
                is_active=is_active,
                allow_self_enroll=allow_self_enroll,
                requires_approval=requires_approval,
                is_public=is_public,
                enrolled_students=[],
                lectures=[]
            )
            
            if success:
                st.success(f"✅ Course '{course_name}' created successfully!")
                st.balloons()
                st.session_state.show_create_course = False
                st.rerun()
            else:
                st.error("❌ Failed to create course. Course ID may already exist.")


def show_edit_course_form():
    """Form to edit existing course"""
    st.subheader("✏️ Edit Course")
    
    storage = get_storage()
    user = st.session_state.user
    course_id = st.session_state.edit_course_id
    course = storage.get_course(course_id)
    
    if not course:
        st.error("Course not found")
        return
    
    with st.form("edit_course_form"):
        # Course details
        course_name = st.text_input("Course Name", value=course.get('name', ''))
        course_code = st.text_input("Course Code", value=course.get('code', ''))
        description = st.text_area("Description", value=course.get('description', ''))
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Teacher selection (admin only)
            if user['role'] == 'admin':
                teachers = storage.get_all_users(role='teacher')
                teacher_options = {tid: t.get('full_name', t['username']) for tid, t in teachers.items()}
                
                current_teacher_idx = list(teacher_options.keys()).index(course['teacher_id']) if course['teacher_id'] in teacher_options else 0
                teacher_id = st.selectbox("Teacher", 
                                        options=list(teacher_options.keys()),
                                        format_func=lambda x: teacher_options[x],
                                        index=current_teacher_idx)
            else:
                teacher_id = course['teacher_id']
            
            semester = st.selectbox("Semester", ["Spring", "Fall", "Summer"], 
                                  index=["Spring", "Fall", "Summer"].index(course.get('semester', 'Spring')))
            year = st.number_input("Year", min_value=2020, max_value=2030, value=course.get('year', datetime.now().year))
        
        with col2:
            department = st.text_input("Department", value=course.get('department', ''))
            credits = st.number_input("Credits", min_value=1, max_value=10, value=course.get('credits', 3))
            max_students = st.number_input("Max Students", min_value=10, max_value=500, value=course.get('max_students', 100))
        
        # Additional settings
        st.markdown("#### Course Settings")
        col1, col2 = st.columns(2)
        
        with col1:
            is_active = st.checkbox("Active Course", value=course.get('is_active', True))
            allow_self_enroll = st.checkbox("Allow Self-Enrollment", value=course.get('allow_self_enroll', False))
        
        with col2:
            requires_approval = st.checkbox("Enrollment Requires Approval", value=course.get('requires_approval', False))
            is_public = st.checkbox("Public Course", value=course.get('is_public', True))
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if cancel:
            st.session_state.show_edit_course = False
            st.rerun()
        
        if submit:
            # Update course
            updates = {
                'name': course_name,
                'code': course_code,
                'description': description,
                'teacher_id': teacher_id,
                'department': department,
                'credits': credits,
                'semester': semester,
                'year': year,
                'max_students': max_students,
                'is_active': is_active,
                'allow_self_enroll': allow_self_enroll,
                'requires_approval': requires_approval,
                'is_public': is_public
            }
            
            success = storage.update_course(course_id, updates)
            
            if success:
                st.success(f"✅ Course updated successfully!")
                st.session_state.show_edit_course = False
                st.rerun()
            else:
                st.error("❌ Failed to update course")


def show_manage_students_form():
    """Form to manage course enrollments"""
    st.subheader("👥 Manage Course Students")
    
    storage = get_storage()
    course_id = st.session_state.manage_course_id
    course = storage.get_course(course_id)
    
    if not course:
        st.error("Course not found")
        return
    
    st.write(f"**Course:** {course['name']}")
    st.write(f"**Current Enrollments:** {len(course.get('enrolled_students', []))} / {course.get('max_students', 100)}")
    
    # Tabs for enrolled and available students
    tab1, tab2 = st.tabs(["Enrolled Students", "Add Students"])
    
    with tab1:
        enrolled_ids = course.get('enrolled_students', [])
        
        if enrolled_ids:
            st.markdown(f"**{len(enrolled_ids)} students enrolled**")
            
            for student_id in enrolled_ids:
                student = storage.get_user(student_id)
                if student:
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        st.write(f"🎓 {student.get('full_name', student['username'])} ({student.get('enrollment_number', 'N/A')})")
                    
                    with col2:
                        if st.button("❌ Remove", key=f"remove_{student_id}"):
                            enrolled_ids.remove(student_id)
                            storage.update_course(course_id, {'enrolled_students': enrolled_ids})
                            st.success(f"Removed {student['username']}")
                            st.rerun()
        else:
            st.info("No students enrolled yet")
    
    with tab2:
        # Get all students not enrolled in this course
        all_students = storage.get_all_users(role='student')
        enrolled_ids = course.get('enrolled_students', [])
        available_students = {sid: s for sid, s in all_students.items() if sid not in enrolled_ids}
        
        if available_students:
            search = st.text_input("🔍 Search students", placeholder="Search by name or enrollment number")
            
            # Filter students
            if search:
                available_students = {
                    sid: s for sid, s in available_students.items()
                    if search.lower() in s.get('full_name', '').lower()
                    or search.lower() in s.get('username', '').lower()
                    or search.lower() in s.get('enrollment_number', '').lower()
                }
            
            if available_students:
                for student_id, student in available_students.items():
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        st.write(f"🎓 {student.get('full_name', student['username'])} ({student.get('enrollment_number', 'N/A')})")
                    
                    with col2:
                        if st.button("➕ Add", key=f"add_{student_id}"):
                            enrolled_ids.append(student_id)
                            storage.update_course(course_id, {'enrolled_students': enrolled_ids})
                            st.success(f"Added {student['username']}")
                            st.rerun()
            else:
                st.info("No students found matching your search")
        else:
            st.success("All students are enrolled in this course!")
    
    if st.button("✅ Done", type="primary", use_container_width=True):
        st.session_state.show_manage_students = False
        st.rerun()


def show_course_materials():
    """Display course materials and resources"""
    st.subheader("📄 Course Materials & Resources")
    
    storage = get_storage()
    course_id = st.session_state.view_materials_course
    course = storage.get_course(course_id)
    
    if not course:
        st.error("Course not found")
        return
    
    st.write(f"**Course:** {course['name']}")
    
    # Get course lectures
    lectures = storage.get_course_lectures(course_id)
    
    if lectures:
        st.markdown(f"**📚 {len(lectures)} Lectures Available**")
        
        for lecture in lectures:
            with st.expander(f"🎥 {lecture.get('title', 'Untitled')}"):
                st.write(f"**Lecture ID:** {lecture.get('lecture_id', 'N/A')}")
                st.write(f"**Description:** {lecture.get('description', 'No description')}")
                st.write(f"**Duration:** {lecture.get('duration', 0) // 60} minutes")
                st.write(f"**Video Path:** {lecture.get('video_path', 'N/A')}")
                st.write(f"**Uploaded:** {lecture.get('created_at', 'N/A')[:10]}")
                
                # Show associated materials
                materials = lecture.get('materials', [])
                if materials:
                    st.markdown("**Associated Materials:**")
                    for material in materials:
                        st.write(f"- 📄 {material.get('title', 'Untitled')} ({material.get('type', 'Unknown')})")
    else:
        st.info("No lectures uploaded yet for this course")
    
    if st.button("✅ Close", type="primary", use_container_width=True):
        st.session_state.show_materials = False
        st.rerun()


def main():
    """Main course management page"""
    st.title("📚 Course Management")
    
    # Check if user is admin or teacher
    if 'user' not in st.session_state or st.session_state.user['role'] not in ['admin', 'teacher']:
        st.error("🚫 Access Denied. Admin or Teacher privileges required.")
        return
    
    # Show statistics
    show_course_statistics()
    
    st.markdown("---")
    
    # Check for active forms
    if st.session_state.get('show_create_course', False):
        show_create_course_form()
    elif st.session_state.get('show_edit_course', False):
        show_edit_course_form()
    elif st.session_state.get('show_manage_students', False):
        show_manage_students_form()
    elif st.session_state.get('show_materials', False):
        show_course_materials()
    else:
        show_course_list()


if __name__ == "__main__":
    main()
