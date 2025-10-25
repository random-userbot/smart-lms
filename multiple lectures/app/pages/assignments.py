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
from services.session_tracker import SessionTracker
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
                    
                    # Log assignment submission to CSV for audit trail
                    session_tracker = SessionTracker(user['user_id'])
                    session_tracker.log_assignment_submitted(
                        assignment_id=assignment['assignment_id'],
                        course_id=course_id,
                        file_path=file_path,
                        file_size=submitted_file.size,
                        comments=comments
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


def render_assignment_card(assignment, course_id, is_submitted, submission=None):
    """Render an assignment card with visual styling"""
    # Parse due date
    due_date = datetime.fromisoformat(assignment['due_date'])
    is_overdue = datetime.now().date() > due_date.date() and not is_submitted
    days_until_due = (due_date.date() - datetime.now().date()).days
    
    # Determine status and color
    if is_submitted:
        if submission and submission.get('graded', False):
            percentage = submission['percentage']
            if percentage >= 80:
                status_color = "#28a745"  # Green
                status_text = f"✅ {percentage:.0f}%"
            elif percentage >= 60:
                status_color = "#ffc107"  # Yellow
                status_text = f"✅ {percentage:.0f}%"
            else:
                status_color = "#fd7e14"  # Orange
                status_text = f"✅ {percentage:.0f}%"
        else:
            status_color = "#17a2b8"  # Cyan
            status_text = "⏳ Grading"
    elif is_overdue:
        status_color = "#dc3545"  # Red
        status_text = "⏰ Overdue"
    elif days_until_due <= 3:
        status_color = "#ffc107"  # Yellow
        status_text = f"⚠️ Due Soon"
    else:
        status_color = "#007bff"  # Blue
        status_text = "📋 Pending"
    
    # Format due date
    due_date_str = due_date.strftime("%b %d, %Y")
    
    card_html = f"""
    <div style="
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    ">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
            <h3 style="color: white; margin: 0; font-size: 1.3em;">
                📋 {assignment['title']}
            </h3>
            <span style="
                background: {status_color};
                color: white;
                padding: 5px 12px;
                border-radius: 20px;
                font-size: 0.85em;
                font-weight: bold;
            ">{status_text}</span>
        </div>
        
        <p style="color: rgba(255,255,255,0.95); margin: 10px 0; font-size: 0.95em;">
            {assignment.get('description', 'No description available')}
        </p>
        
        <div style="display: flex; gap: 20px; margin-top: 15px; flex-wrap: wrap;">
            <div style="color: white;">
                <span style="font-size: 1.2em;">📅</span>
                <span style="margin-left: 5px;">Due: {due_date_str}</span>
            </div>
            <div style="color: white;">
                <span style="font-size: 1.2em;">🎯</span>
                <span style="margin-left: 5px;">Max Score: {assignment['max_score']}</span>
            </div>
            {f'''<div style="color: white;">
                <span style="font-size: 1.2em;">{"⏰" if days_until_due < 0 else "⏳"}</span>
                <span style="margin-left: 5px;">{abs(days_until_due)} day{"s" if abs(days_until_due) != 1 else ""} {"overdue" if days_until_due < 0 else "left"}</span>
            </div>''' if not is_submitted else ''}
            {f'''<div style="color: white;">
                <span style="font-size: 1.2em;">📊</span>
                <span style="margin-left: 5px;">Score: {submission['score']}/{submission['max_score']}</span>
            </div>''' if submission and submission.get('graded') else ''}
        </div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)
    
    # Show reference files
    if assignment.get('reference_files'):
        with st.expander("📎 Reference Files"):
            for ref_file in assignment['reference_files']:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"📄 {ref_file['file_name']}")
                with col2:
                    if st.button("📥 Download", key=f"ref_{assignment['assignment_id']}_{ref_file['file_name']}"):
                        st.info("Download functionality will be implemented")
    
    # Show teacher feedback if graded
    if submission and submission.get('graded') and submission.get('teacher_feedback'):
        with st.expander("💬 Teacher Feedback"):
            st.info(submission['teacher_feedback'])
    
    # Action buttons
    if is_submitted:
        col1, col2 = st.columns(2)
        with col1:
            if submission and submission.get('graded'):
                st.success(f"✅ Submitted on {submission['timestamp']}")
            else:
                st.info(f"⏳ Submitted on {submission['timestamp']}")
        with col2:
            if st.button("📝 Resubmit", key=f"resubmit_{assignment['assignment_id']}", use_container_width=True):
                st.session_state.selected_assignment = assignment
                st.session_state.selected_course_id = course_id
                st.session_state.current_page = 'submit_assignment'
                st.rerun()
    else:
        if st.button("📤 Submit Assignment", key=f"submit_{assignment['assignment_id']}", type="primary" if not is_overdue else "secondary", use_container_width=True):
            st.session_state.selected_assignment = assignment
            st.session_state.selected_course_id = course_id
            st.session_state.current_page = 'submit_assignment'
            st.rerun()


def show_available_assignments():
    """Display list of available assignments with card-based UI"""
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
    
    # Calculate statistics
    total_assignments = 0
    submitted_count = 0
    graded_count = 0
    overdue_count = 0
    total_score = 0
    
    for course_id, course in enrolled_courses.items():
        for assignment in course.get('assignments', []):
            total_assignments += 1
            assignment_id = assignment['assignment_id']
            
            if assignment_id in submitted_assignments:
                submitted_count += 1
                submission = submitted_assignments[assignment_id]
                if submission.get('graded'):
                    graded_count += 1
                    total_score += submission['percentage']
            else:
                due_date = datetime.fromisoformat(assignment['due_date'])
                if datetime.now().date() > due_date.date():
                    overdue_count += 1
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📋 Total", total_assignments)
    with col2:
        st.metric("✅ Submitted", submitted_count)
    with col3:
        st.metric("⏰ Overdue", overdue_count)
    with col4:
        avg_score = total_score / graded_count if graded_count > 0 else 0
        st.metric("📊 Avg Score", f"{avg_score:.0f}%")
    
    st.markdown("---")
    
    # Search and filter
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("� Search assignments", placeholder="Search by title or description...", key="assignment_search")
    with col2:
        filter_option = st.selectbox("Filter", ["All", "Submitted", "Pending", "Overdue"], key="assignment_filter")
    
    st.markdown("---")
    
    # Display assignments by course
    for course_id, course in enrolled_courses.items():
        assignments = course.get('assignments', [])
        
        course_assignments = []
        for assignment in assignments:
            assignment_id = assignment['assignment_id']
            is_submitted = assignment_id in submitted_assignments
            submission = submitted_assignments.get(assignment_id)
            
            # Check if overdue
            due_date = datetime.fromisoformat(assignment['due_date'])
            is_overdue = datetime.now().date() > due_date.date() and not is_submitted
            
            # Apply filters
            if filter_option == "Submitted" and not is_submitted:
                continue
            if filter_option == "Pending" and is_submitted:
                continue
            if filter_option == "Overdue" and not is_overdue:
                continue
            
            # Apply search
            if search_query:
                if search_query.lower() not in assignment['title'].lower() and \
                   search_query.lower() not in assignment.get('description', '').lower():
                    continue
            
            course_assignments.append((assignment, is_submitted, submission))
        
        if course_assignments:
            st.subheader(f"📚 {course['name']}")
            
            for assignment, is_submitted, submission in course_assignments:
                render_assignment_card(assignment, course_id, is_submitted, submission)
            
            st.markdown("---")
    
    if total_assignments == 0:
        st.info("📋 No assignments available yet. Check back later!")


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
