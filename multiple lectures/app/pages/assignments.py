"""
Smart LMS - Assignments Page
Students can view and submit assignments
"""

import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.auth import get_auth
from services.storage import get_storage
from datetime import datetime
import uuid


def save_uploaded_file(uploaded_file, destination_path):
    """Save uploaded file to destination"""
    try:
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        with open(destination_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return True
    except Exception as e:
        st.error(f"Error saving file: {str(e)}")
        return False


def show_assignment_submission(assignment, course_id):
    """Display assignment submission form"""
    st.title(f"📋 {assignment['title']}")
    
    st.markdown("### Assignment Details")
    st.markdown(assignment['description'])
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Due Date", assignment['due_date'])
    with col2:
        st.metric("Maximum Score", assignment['max_score'])
    
    # Reference files
    if assignment.get('reference_files'):
        st.markdown("### 📎 Reference Files")
        for ref_file in assignment['reference_files']:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"📄 {ref_file['file_name']}")
            with col2:
                if st.button("📥 Download", key=f"ref_{ref_file['file_name']}"):
                    st.info("Download functionality will be implemented")
    
    st.markdown("---")
    
    # Check if already submitted
    storage = get_storage()
    user = st.session_state.user
    grades = storage.get_student_grades(user['user_id'])
    
    existing_submission = None
    for assignment_grade in grades.get('assignments', []):
        if assignment_grade['assessment_id'] == assignment['assignment_id']:
            existing_submission = assignment_grade
            break
    
    if existing_submission:
        st.success("✅ Assignment Already Submitted")
        st.markdown(f"**Submitted on:** {existing_submission['timestamp']}")
        if existing_submission.get('score') is not None:
            st.markdown(f"**Score:** {existing_submission['score']}/{existing_submission['max_score']} ({existing_submission['percentage']:.1f}%)")
        else:
            st.info("⏳ Grading pending")
        
        st.markdown("---")
        st.markdown("### Resubmit Assignment")
    
    # Submission form
    st.markdown("### 📤 Submit Your Work")
    
    with st.form("assignment_submission_form"):
        # File upload
        submitted_file = st.file_uploader(
            "Upload your assignment",
            type=['pdf', 'zip', 'docx', 'pptx'],
            help="Supported formats: PDF, ZIP, DOCX, PPTX"
        )
        
        # Comments
        comments = st.text_area(
            "Comments (Optional)",
            placeholder="Any additional notes or comments for the teacher",
            height=100
        )
        
        submit = st.form_submit_button("📤 Submit Assignment")
        
        if submit:
            if not submitted_file:
                st.error("❌ Please upload your assignment file")
                return
            
            # Save submission
            submission_id = f"sub_{uuid.uuid4().hex[:8]}"
            file_path = f"./storage/assignments/{course_id}/{user['user_id']}_{assignment['assignment_id']}_{submitted_file.name}"
            
            with st.spinner("Uploading assignment..."):
                if save_uploaded_file(submitted_file, file_path):
                    # Save grade record (score will be added by teacher later)
                    storage.save_grade(
                        student_id=user['user_id'],
                        course_id=course_id,
                        assessment_type='assignment',
                        assessment_id=assignment['assignment_id'],
                        score=0,  # Pending grading
                        max_score=assignment['max_score'],
                        submission_file=file_path,
                        comments=comments,
                        graded=False
                    )
                    
                    st.success("✅ Assignment submitted successfully!")
                    st.balloons()
                    
                    if st.button("🏠 Back to Assignments"):
                        st.session_state.current_page = 'assignments'
                        if 'selected_assignment' in st.session_state:
                            del st.session_state.selected_assignment
                        st.rerun()
                else:
                    st.error("❌ Failed to upload assignment file")


def show_available_assignments():
    """Display list of available assignments"""
    st.title("📋 My Assignments")
    
    storage = get_storage()
    user = st.session_state.user
    
    # Get enrolled courses
    all_courses = storage.get_all_courses()
    enrolled_courses = {
        cid: c for cid, c in all_courses.items()
        if user['user_id'] in c.get('enrolled_students', [])
    }
    
    if not enrolled_courses:
        st.info("📝 You are not enrolled in any courses yet.")
        return
    
    # Get student's grades
    grades = storage.get_student_grades(user['user_id'])
    submitted_assignments = {g['assessment_id']: g for g in grades.get('assignments', [])}
    
    # Display assignments by course
    for course_id, course in enrolled_courses.items():
        st.subheader(f"📚 {course['name']}")
        
        assignments = course.get('assignments', [])
        
        if not assignments:
            st.info("📝 No assignments available for this course yet.")
        else:
            for assignment in assignments:
                assignment_id = assignment['assignment_id']
                is_submitted = assignment_id in submitted_assignments
                
                # Check if overdue
                due_date = datetime.fromisoformat(assignment['due_date'])
                is_overdue = datetime.now().date() > due_date.date()
                
                status_icon = "✅" if is_submitted else ("⏰" if is_overdue else "📋")
                
                with st.expander(
                    f"{status_icon} {assignment['title']}",
                    expanded=not is_submitted and not is_overdue
                ):
                    st.markdown(f"**Due Date:** {assignment['due_date']}")
                    st.markdown(f"**Maximum Score:** {assignment['max_score']}")
                    
                    if is_overdue and not is_submitted:
                        st.error("⏰ This assignment is overdue!")
                    
                    if is_submitted:
                        submission = submitted_assignments[assignment_id]
                        st.success(f"✅ Submitted on {submission['timestamp']}")
                        
                        if submission.get('graded', False):
                            st.markdown(f"**Score:** {submission['score']}/{submission['max_score']} ({submission['percentage']:.1f}%)")
                            if submission.get('teacher_feedback'):
                                st.markdown("**Teacher Feedback:**")
                                st.info(submission['teacher_feedback'])
                        else:
                            st.info("⏳ Grading pending")
                        
                        if st.button("📝 Resubmit", key=f"resubmit_{assignment_id}"):
                            st.session_state.selected_assignment = assignment
                            st.session_state.selected_course_id = course_id
                            st.session_state.current_page = 'submit_assignment'
                            st.rerun()
                    else:
                        if st.button("📤 Submit Assignment", key=f"submit_{assignment_id}", use_container_width=True):
                            st.session_state.selected_assignment = assignment
                            st.session_state.selected_course_id = course_id
                            st.session_state.current_page = 'submit_assignment'
                            st.rerun()
        
        st.markdown("---")


def main():
    """Main assignments page"""
    # Check authentication
    auth = get_auth()
    auth.require_role('student')
    
    # Check if submitting an assignment
    if st.session_state.get('current_page') == 'submit_assignment' and 'selected_assignment' in st.session_state:
        assignment = st.session_state.selected_assignment
        course_id = st.session_state.selected_course_id
        
        # Back button
        if st.button("← Back to Assignments"):
            st.session_state.current_page = 'assignments'
            if 'selected_assignment' in st.session_state:
                del st.session_state.selected_assignment
            st.rerun()
        
        show_assignment_submission(assignment, course_id)
    else:
        # Show available assignments
        show_available_assignments()


if __name__ == "__main__":
    main()
