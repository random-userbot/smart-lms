"""
Smart LMS - Upload Page
Teachers can upload lectures, materials, quizzes, and assignments
"""

import streamlit as st
import sys
import os
import re
import mimetypes
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.auth import get_auth
from services.storage import get_storage
from services.behavioral_logger import BehavioralLogger
from datetime import datetime
import uuid
import shutil
from pathlib import Path


# Security constants
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB
ALLOWED_VIDEO_TYPES = ['video/mp4', 'video/avi', 'video/quicktime', 'video/x-matroska']
ALLOWED_MATERIAL_TYPES = [
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain',
    'application/zip'
]


def sanitize_filename(filename: str) -> str:
    """
    Sanitize uploaded filename to prevent path traversal and other attacks
    
    Args:
        filename: Original filename from upload
    
    Returns:
        Sanitized filename safe for filesystem
    """
    # Remove path components
    filename = os.path.basename(filename)
    
    # Remove any non-alphanumeric characters except .-_
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    
    # Prevent hidden files
    if filename.startswith('.'):
        filename = '_' + filename[1:]
    
    # Limit length
    name, ext = os.path.splitext(filename)
    if len(name) > 100:
        name = name[:100]
    
    return name + ext


def validate_file_upload(uploaded_file, allowed_types: list, max_size: int = MAX_FILE_SIZE) -> tuple:
    """
    Validate uploaded file for security
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        allowed_types: List of allowed MIME types
        max_size: Maximum file size in bytes
    
    Returns:
        (is_valid: bool, error_message: str or None)
    """
    # Check file size
    if uploaded_file.size > max_size:
        return False, f"File too large. Maximum size: {max_size // (1024*1024)} MB"
    
    # Check MIME type
    file_type = uploaded_file.type
    if file_type not in allowed_types:
        return False, f"Invalid file type: {file_type}. Allowed: {', '.join(allowed_types)}"
    
    # Additional extension validation
    filename = uploaded_file.name
    ext = os.path.splitext(filename)[1].lower()
    
    # Map extensions to expected MIME types
    valid_extensions = {
        '.mp4': 'video/mp4',
        '.avi': 'video/avi',
        '.mov': 'video/quicktime',
        '.mkv': 'video/x-matroska',
        '.pdf': 'application/pdf',
        '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.txt': 'text/plain',
        '.zip': 'application/zip'
    }
    
    if ext not in valid_extensions:
        return False, f"Invalid file extension: {ext}"
    
    return True, None


def save_uploaded_file(uploaded_file, destination_path):
    """Save uploaded file to destination with security checks"""
    try:
        # Ensure destination directory exists with secure permissions
        dest_dir = os.path.dirname(destination_path)
        os.makedirs(dest_dir, mode=0o750, exist_ok=True)
        
        # Validate destination path (prevent path traversal)
        destination_path = os.path.abspath(destination_path)
        if '..' in destination_path:
            raise ValueError("Invalid destination path")
        
        # Write file
        with open(destination_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Set restrictive permissions
        os.chmod(destination_path, 0o640)
        
        return True
    except Exception as e:
        st.error(f"Error saving file: {str(e)}")
        return False


def show_upload_lecture():
    """Upload lecture video or YouTube link"""
    st.subheader("🎥 Upload Lecture")
    
    storage = get_storage()
    user = st.session_state.user
    
    # Get teacher's courses
    courses = storage.get_all_courses(teacher_id=user['user_id'])
    
    if not courses:
        st.warning("⚠️ You don't have any courses yet. Contact admin to create courses.")
        return
    
    # Toggle between file upload and YouTube link
    upload_type = st.radio(
        "Lecture Source",
        ["📹 YouTube Link", "📁 Upload Video File"],
        horizontal=True
    )
    
    with st.form("upload_lecture_form"):
        # Course selection
        course_options = {cid: c['name'] for cid, c in courses.items()}
        selected_course = st.selectbox(
            "Select Course",
            options=list(course_options.keys()),
            format_func=lambda x: course_options[x]
        )
        
        # Lecture details
        lecture_title = st.text_input("Lecture Title", placeholder="e.g., Introduction to Machine Learning")
        lecture_description = st.text_area("Description", placeholder="Brief description of the lecture content")
        
        # Conditional input based on upload type
        video_file = None
        youtube_url = None
        
        if upload_type == "📹 YouTube Link":
            youtube_url = st.text_input(
                "YouTube URL",
                placeholder="https://www.youtube.com/watch?v=...",
                help="Paste the full YouTube video URL"
            )
            
            # Show preview if URL is valid
            if youtube_url and ('youtube.com' in youtube_url or 'youtu.be' in youtube_url):
                st.video(youtube_url)
        else:
            # Video upload
            video_file = st.file_uploader(
                "Upload Video File",
                type=['mp4', 'avi', 'mov', 'mkv'],
                help="Supported formats: MP4, AVI, MOV, MKV"
            )
        
        # Duration
        duration_minutes = st.number_input("Duration (minutes)", min_value=1, value=60)
        
        submit = st.form_submit_button("📤 Upload Lecture", type="primary")
        
        if submit:
            if not lecture_title:
                st.error("❌ Please enter a lecture title")
                return
            
            if upload_type == "📹 YouTube Link":
                if not youtube_url:
                    st.error("❌ Please enter a YouTube URL")
                    return
                
                if not ('youtube.com' in youtube_url or 'youtu.be' in youtube_url):
                    st.error("❌ Please enter a valid YouTube URL")
                    return
                
                # Generate lecture ID
                lecture_id = f"lec_{uuid.uuid4().hex[:8]}"
                
                with st.spinner("Creating lecture..."):
                    # Create lecture record with YouTube URL
                    success = storage.create_lecture(
                        lecture_id=lecture_id,
                        title=lecture_title,
                        course_id=selected_course,
                        video_path=youtube_url,  # Store YouTube URL as video_path
                        duration=duration_minutes * 60,
                        description=lecture_description,
                        uploaded_by=user['user_id'],
                        video_type='youtube'  # Flag as YouTube video
                    )
                    
                    if success:
                        # Log teacher activity to JSON
                        storage.log_teacher_activity(
                            activity_id=str(uuid.uuid4()),
                            teacher_id=user['user_id'],
                            action='upload_lecture',
                            details={
                                'lecture_id': lecture_id,
                                'course_id': selected_course,
                                'title': lecture_title,
                                'type': 'youtube'
                            }
                        )
                        
                        # Log to CSV for audit trail
                        csv_logger = BehavioralLogger(student_id=user['user_id'])
                        csv_logger.log_lecture_upload(
                            lecture_id=lecture_id,
                            course_id=selected_course,
                            lecture_type='youtube',
                            video_url=youtube_url
                        )
                        
                        st.success(f"✅ Lecture '{lecture_title}' created successfully!")
                        st.balloons()
                    else:
                        st.error("❌ Failed to create lecture record")
            
            else:  # File upload
                if not video_file:
                    st.error("❌ Please upload a video file")
                    return
                
                # Validate file upload
                is_valid, error_msg = validate_file_upload(video_file, ALLOWED_VIDEO_TYPES)
                if not is_valid:
                    st.error(f"❌ {error_msg}")
                    return
                
                # Generate lecture ID
                lecture_id = f"lec_{uuid.uuid4().hex[:8]}"
                
                # Sanitize filename
                safe_filename = sanitize_filename(video_file.name)
                video_path = f"./storage/courses/{selected_course}/lectures/{lecture_id}_{safe_filename}"
                
                with st.spinner("Uploading video... This may take a moment."):
                    if save_uploaded_file(video_file, video_path):
                        # Create lecture record
                        success = storage.create_lecture(
                            lecture_id=lecture_id,
                            title=lecture_title,
                            course_id=selected_course,
                            video_path=video_path,
                            duration=duration_minutes * 60,
                            description=lecture_description,
                            uploaded_by=user['user_id'],
                            video_type='file'
                        )
                        
                        if success:
                            # Log teacher activity to JSON
                            storage.log_teacher_activity(
                                activity_id=str(uuid.uuid4()),
                                teacher_id=user['user_id'],
                                action='upload_lecture',
                                details={
                                    'lecture_id': lecture_id,
                                    'course_id': selected_course,
                                    'title': lecture_title,
                                    'type': 'file'
                                }
                            )
                            
                            # Log to CSV for audit trail
                            csv_logger = BehavioralLogger(student_id=user['user_id'])
                            csv_logger.log_lecture_upload(
                                lecture_id=lecture_id,
                                course_id=selected_course,
                                lecture_type='file',
                                video_url=video_path,
                                file_size=video_file.size
                            )
                            
                            st.success(f"✅ Lecture '{lecture_title}' uploaded successfully!")
                            st.balloons()
                        else:
                            st.error("❌ Failed to create lecture record")
                    else:
                        st.error("❌ Failed to upload video file")


def show_upload_material():
    """Upload course materials (PDFs, documents)"""
    st.subheader("📄 Upload Course Materials")
    
    storage = get_storage()
    user = st.session_state.user
    
    # Get teacher's courses
    courses = storage.get_all_courses(teacher_id=user['user_id'])
    
    if not courses:
        st.warning("⚠️ You don't have any courses yet. Contact admin to create courses.")
        return
    
    with st.form("upload_material_form"):
        # Course selection
        course_options = {cid: c['name'] for cid, c in courses.items()}
        selected_course = st.selectbox(
            "Select Course",
            options=list(course_options.keys()),
            format_func=lambda x: course_options[x]
        )
        
        # Material details
        material_title = st.text_input("Material Title", placeholder="e.g., Lecture Notes - Week 1")
        material_type = st.selectbox("Material Type", ["Lecture Notes", "Slides", "Reference Material", "Other"])
        
        # File upload
        material_file = st.file_uploader(
            "Upload File",
            type=['pdf', 'pptx', 'docx', 'txt', 'zip'],
            help="Supported formats: PDF, PPTX, DOCX, TXT, ZIP"
        )
        
        # Optional: Link to specific lecture
        lectures = storage.get_course_lectures(selected_course)
        lecture_options = {l['lecture_id']: l['title'] for l in lectures}
        lecture_options['none'] = "Not linked to specific lecture"
        
        linked_lecture = st.selectbox(
            "Link to Lecture (Optional)",
            options=list(lecture_options.keys()),
            format_func=lambda x: lecture_options[x],
            index=len(lecture_options) - 1
        )
        
        submit = st.form_submit_button("📤 Upload Material")
        
        if submit:
            if not material_title:
                st.error("❌ Please enter a material title")
                return
            
            if not material_file:
                st.error("❌ Please upload a file")
                return
            
            # Validate file upload
            is_valid, error_msg = validate_file_upload(material_file, ALLOWED_MATERIAL_TYPES)
            if not is_valid:
                st.error(f"❌ {error_msg}")
                return
            
            # Generate material ID and sanitize filename
            material_id = f"mat_{uuid.uuid4().hex[:8]}"
            safe_filename = sanitize_filename(material_file.name)
            material_path = f"./storage/courses/{selected_course}/materials/{material_id}_{safe_filename}"
            
            with st.spinner("Uploading material..."):
                if save_uploaded_file(material_file, material_path):
                    # Update course or lecture with material
                    material_info = {
                        'material_id': material_id,
                        'title': material_title,
                        'type': material_type,
                        'file_path': material_path,
                        'file_name': material_file.name,
                        'uploaded_at': datetime.utcnow().isoformat(),
                        'uploaded_by': user['user_id']
                    }
                    
                    if linked_lecture != 'none':
                        # Add to lecture
                        lecture = storage.get_lecture(linked_lecture)
                        if lecture:
                            materials = lecture.get('materials', [])
                            materials.append(material_info)
                            # Persist materials to the lecture record
                            storage.update_lecture(linked_lecture, {'materials': materials})
                    
                    # Log teacher activity to JSON
                    storage.log_teacher_activity(
                        activity_id=str(uuid.uuid4()),
                        teacher_id=user['user_id'],
                        action='upload_material',
                        details={
                            'material_id': material_id,
                            'course_id': selected_course,
                            'title': material_title,
                            'type': material_type
                        }
                    )
                    
                    # Log to CSV for audit trail
                    csv_logger = BehavioralLogger(student_id=user['user_id'])
                    csv_logger.log_material_upload(
                        material_id=material_id,
                        material_type=material_type,
                        course_id=selected_course,
                        lecture_id=linked_lecture if linked_lecture != 'none' else None,
                        file_name=material_file.name,
                        file_size=material_file.size
                    )
                    
                    st.success(f"✅ Material '{material_title}' uploaded successfully!")
                else:
                    st.error("❌ Failed to upload material file")


def show_create_quiz():
    """Create quiz for a lecture"""
    st.subheader("📝 Create Quiz")
    
    storage = get_storage()
    user = st.session_state.user
    
    # Get teacher's courses
    courses = storage.get_all_courses(teacher_id=user['user_id'])
    
    if not courses:
        st.warning("⚠️ You don't have any courses yet. Contact admin to create courses.")
        return
    
    with st.form("create_quiz_form"):
        # Course selection
        course_options = {cid: c['name'] for cid, c in courses.items()}
        selected_course = st.selectbox(
            "Select Course",
            options=list(course_options.keys()),
            format_func=lambda x: course_options[x]
        )
        
        # Lecture selection
        lectures = storage.get_course_lectures(selected_course)
        if not lectures:
            st.warning("⚠️ No lectures available in this course. Upload a lecture first.")
            st.form_submit_button("Create Quiz", disabled=True)
            return
        
        lecture_options = {l['lecture_id']: l['title'] for l in lectures}
        selected_lecture = st.selectbox(
            "Select Lecture",
            options=list(lecture_options.keys()),
            format_func=lambda x: lecture_options[x]
        )
        
        # Quiz details
        quiz_title = st.text_input("Quiz Title", placeholder="e.g., Week 1 Quiz")
        time_limit = st.number_input("Time Limit (minutes)", min_value=5, value=30)
        
        st.markdown("---")
        st.markdown("### Questions")
        
        # Number of questions
        num_questions = st.number_input("Number of Questions", min_value=1, max_value=20, value=5)
        
        questions = []
        for i in range(num_questions):
            st.markdown(f"**Question {i+1}**")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                question_text = st.text_area(
                    f"Question",
                    key=f"q_{i}",
                    placeholder="Enter your question here"
                )
            with col2:
                question_type = st.selectbox(
                    "Type",
                    ["Multiple Choice", "True/False"],
                    key=f"type_{i}"
                )
            
            if question_type == "Multiple Choice":
                option_a = st.text_input(f"Option A", key=f"opt_a_{i}")
                option_b = st.text_input(f"Option B", key=f"opt_b_{i}")
                option_c = st.text_input(f"Option C", key=f"opt_c_{i}")
                option_d = st.text_input(f"Option D", key=f"opt_d_{i}")
                correct_answer = st.selectbox(
                    "Correct Answer",
                    ["A", "B", "C", "D"],
                    key=f"ans_{i}"
                )
                
                questions.append({
                    'question': question_text,
                    'type': 'mcq',
                    'options': {
                        'A': option_a,
                        'B': option_b,
                        'C': option_c,
                        'D': option_d
                    },
                    'correct_answer': correct_answer
                })
            else:  # True/False
                correct_answer = st.radio(
                    "Correct Answer",
                    ["True", "False"],
                    key=f"ans_{i}"
                )
                
                questions.append({
                    'question': question_text,
                    'type': 'true_false',
                    'correct_answer': correct_answer
                })
            
            st.markdown("---")
        
        submit = st.form_submit_button("✅ Create Quiz")
        
        if submit:
            if not quiz_title:
                st.error("❌ Please enter a quiz title")
                return
            
            # Validate questions
            valid = True
            for i, q in enumerate(questions):
                if not q['question']:
                    st.error(f"❌ Question {i+1} is empty")
                    valid = False
                if q['type'] == 'mcq':
                    if not all(q['options'].values()):
                        st.error(f"❌ Question {i+1} has empty options")
                        valid = False
            
            if not valid:
                return
            
            # Create quiz
            quiz_id = f"quiz_{uuid.uuid4().hex[:8]}"
            
            # Store quiz in lecture metadata
            lecture = storage.get_lecture(selected_lecture)
            if lecture:
                quizzes = lecture.get('quizzes', [])
                quizzes.append({
                    'quiz_id': quiz_id,
                    'title': quiz_title,
                    'time_limit': time_limit,
                    'questions': questions,
                    'created_at': datetime.utcnow().isoformat(),
                    'created_by': user['user_id']
                })
                
                # Update lecture (need to implement update_lecture in storage)
                lectures_data = storage._read_json(storage.storage_paths['lectures'])
                lectures_data[selected_lecture]['quizzes'] = quizzes
                storage._write_json(storage.storage_paths['lectures'], lectures_data)
                
                # Log teacher activity
                storage.log_teacher_activity(
                    activity_id=str(uuid.uuid4()),
                    teacher_id=user['user_id'],
                    action='create_quiz',
                    details={
                        'quiz_id': quiz_id,
                        'lecture_id': selected_lecture,
                        'course_id': selected_course,
                        'title': quiz_title,
                        'num_questions': len(questions)
                    }
                )
                
                st.success(f"✅ Quiz '{quiz_title}' created successfully!")
                st.balloons()


def show_create_assignment():
    """Create assignment for a course"""
    st.subheader("📋 Create Assignment")
    
    storage = get_storage()
    user = st.session_state.user
    
    # Get teacher's courses
    courses = storage.get_all_courses(teacher_id=user['user_id'])
    
    if not courses:
        st.warning("⚠️ You don't have any courses yet. Contact admin to create courses.")
        return
    
    with st.form("create_assignment_form"):
        # Course selection
        course_options = {cid: c['name'] for cid, c in courses.items()}
        selected_course = st.selectbox(
            "Select Course",
            options=list(course_options.keys()),
            format_func=lambda x: course_options[x]
        )
        
        # Assignment details
        assignment_title = st.text_input("Assignment Title", placeholder="e.g., Project 1: Image Classification")
        assignment_description = st.text_area(
            "Description",
            placeholder="Detailed instructions for the assignment",
            height=150
        )
        
        col1, col2 = st.columns(2)
        with col1:
            due_date = st.date_input("Due Date")
        with col2:
            max_score = st.number_input("Maximum Score", min_value=1, value=100)
        
        # Optional: Upload reference files
        reference_files = st.file_uploader(
            "Upload Reference Files (Optional)",
            type=['pdf', 'zip', 'docx'],
            accept_multiple_files=True,
            help="Upload any reference materials or templates"
        )
        
        submit = st.form_submit_button("✅ Create Assignment")
        
        if submit:
            if not assignment_title:
                st.error("❌ Please enter an assignment title")
                return
            
            if not assignment_description:
                st.error("❌ Please enter assignment description")
                return
            
            # Create assignment
            assignment_id = f"assign_{uuid.uuid4().hex[:8]}"
            
            # Save reference files if any
            reference_paths = []
            if reference_files:
                for ref_file in reference_files:
                    ref_path = f"./storage/courses/{selected_course}/assignments/{assignment_id}_{ref_file.name}"
                    if save_uploaded_file(ref_file, ref_path):
                        reference_paths.append({
                            'file_name': ref_file.name,
                            'file_path': ref_path
                        })
            
            # Store assignment in course metadata
            course = storage.get_course(selected_course)
            if course:
                assignments = course.get('assignments', [])
                assignments.append({
                    'assignment_id': assignment_id,
                    'title': assignment_title,
                    'description': assignment_description,
                    'due_date': due_date.isoformat(),
                    'max_score': max_score,
                    'reference_files': reference_paths,
                    'created_at': datetime.utcnow().isoformat(),
                    'created_by': user['user_id']
                })
                
                storage.update_course(selected_course, {'assignments': assignments})
                
                # Log teacher activity
                storage.log_teacher_activity(
                    activity_id=str(uuid.uuid4()),
                    teacher_id=user['user_id'],
                    action='create_assignment',
                    details={
                        'assignment_id': assignment_id,
                        'course_id': selected_course,
                        'title': assignment_title,
                        'max_score': max_score
                    }
                )
                
                st.success(f"✅ Assignment '{assignment_title}' created successfully!")
                st.balloons()


def main():
    """Main upload page"""
    # Check authentication
    auth = get_auth()
    auth.require_role('teacher')
    
    st.title("📤 Upload Content")
    st.markdown("Upload lectures, materials, create quizzes and assignments")
    
    # Create tabs for different upload types
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎥 Upload Lecture",
        "📄 Upload Materials",
        "📝 Create Quiz",
        "📋 Create Assignment"
    ])
    
    with tab1:
        show_upload_lecture()
    
    with tab2:
        show_upload_material()
    
    with tab3:
        show_create_quiz()
    
    with tab4:
        show_create_assignment()


if __name__ == "__main__":
    main()
