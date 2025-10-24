"""
Smart LMS - Resources Page
Download and manage course resources, materials, and files
"""

import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.storage import get_storage
from pathlib import Path
import mimetypes


def get_file_size(file_path):
    """Get file size in human-readable format"""
    try:
        size = os.path.getsize(file_path)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    except:
        return "Unknown"


def get_file_icon(filename):
    """Get appropriate icon for file type"""
    ext = Path(filename).suffix.lower()
    icons = {
        '.pdf': '📄',
        '.pptx': '📊',
        '.ppt': '📊',
        '.docx': '📝',
        '.doc': '📝',
        '.txt': '📃',
        '.zip': '🗜️',
        '.rar': '🗜️',
        '.mp4': '🎥',
        '.avi': '🎥',
        '.mov': '🎥',
        '.jpg': '🖼️',
        '.jpeg': '🖼️',
        '.png': '🖼️',
        '.py': '🐍',
        '.java': '☕',
        '.cpp': '⚙️',
        '.c': '⚙️'
    }
    return icons.get(ext, '📁')


def show_resources_by_course():
    """Display resources organized by course"""
    storage = get_storage()
    user = st.session_state.user
    
    # Get user's courses
    if user['role'] == 'admin':
        courses = storage.get_all_courses()
        st.subheader("📚 All Course Resources")
    elif user['role'] == 'teacher':
        courses = storage.get_all_courses(teacher_id=user['user_id'])
        st.subheader("📚 My Course Resources")
    else:  # student
        all_courses = storage.get_all_courses()
        courses = {
            cid: c for cid, c in all_courses.items()
            if user['user_id'] in c.get('enrolled_students', [])
        }
        st.subheader("📚 My Enrolled Course Resources")
    
    if not courses:
        st.info("No courses available. You need to be enrolled in courses to access resources.")
        return
    
    # Search and filter
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search = st.text_input("🔍 Search resources", placeholder="Search by course name, lecture, or material...")
    
    with col2:
        filter_type = st.selectbox("Filter", ["All", "Videos", "Documents", "Other"])
    
    # Display courses and their resources
    for course_id, course in courses.items():
        lectures = storage.get_course_lectures(course_id)
        
        if not lectures:
            continue
        
        # Count resources
        total_videos = len(lectures)
        total_materials = sum(len(lec.get('materials', [])) for lec in lectures)
        
        with st.expander(f"📖 {course['name']} ({total_videos} videos, {total_materials} materials)", expanded=False):
            # Display course info
            col1, col2 = st.columns([3, 1])
            
            with col1:
                teacher = storage.get_user(course.get('teacher_id', ''))
                teacher_name = teacher.get('full_name', 'Unknown') if teacher else 'Unknown'
                st.write(f"**Teacher:** {teacher_name}")
                st.write(f"**Department:** {course.get('department', 'N/A')}")
            
            with col2:
                if user['role'] in ['admin', 'teacher']:
                    if st.button(f"📤 Upload to {course['name'][:20]}...", key=f"upload_{course_id}", use_container_width=True):
                        st.session_state.selected_course = course_id
                        st.session_state.current_page = 'upload'
                        st.rerun()
            
            st.markdown("---")
            
            # Display lectures and their materials
            for lecture in lectures:
                # Apply search filter
                if search and search.lower() not in lecture.get('title', '').lower():
                    continue
                
                # Apply type filter
                materials = lecture.get('materials', [])
                if filter_type == "Videos":
                    # Show only if video exists
                    if not lecture.get('video_path'):
                        continue
                elif filter_type == "Documents":
                    # Show only if has document materials
                    if not materials:
                        continue
                elif filter_type == "Other":
                    # Show only if has non-video, non-document materials
                    pass
                
                st.markdown(f"### 🎥 {lecture.get('title', 'Untitled Lecture')}")
                st.write(f"*{lecture.get('description', 'No description')}*")
                
                # Video download
                video_path = lecture.get('video_path', '')
                if video_path and os.path.exists(video_path):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        file_size = get_file_size(video_path)
                        st.write(f"🎥 **Video:** {Path(video_path).name} ({file_size})")
                    
                    with col2:
                        duration = lecture.get('duration', 0)
                        st.write(f"⏱️ {duration // 60}min {duration % 60}s")
                    
                    with col3:
                        # Download button
                        try:
                            with open(video_path, 'rb') as f:
                                st.download_button(
                                    label="⬇️ Download",
                                    data=f,
                                    file_name=Path(video_path).name,
                                    mime='video/mp4',
                                    key=f"download_video_{lecture.get('lecture_id', 'unknown')}",
                                    use_container_width=True
                                )
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                
                # Display materials
                if materials:
                    st.markdown("**📄 Course Materials:**")
                    
                    for idx, material in enumerate(materials):
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        with col1:
                            icon = get_file_icon(material.get('file_name', ''))
                            material_path = material.get('file_path', '')
                            file_size = get_file_size(material_path) if os.path.exists(material_path) else "N/A"
                            
                            st.write(f"{icon} **{material.get('title', 'Untitled')}**")
                            st.write(f"   Type: {material.get('type', 'Unknown')} | Size: {file_size}")
                        
                        with col2:
                            uploaded_at = material.get('uploaded_at', 'Unknown')
                            st.write(f"📅 {uploaded_at[:10] if uploaded_at != 'Unknown' else 'Unknown'}")
                        
                        with col3:
                            # Download button
                            if os.path.exists(material_path):
                                try:
                                    with open(material_path, 'rb') as f:
                                        file_bytes = f.read()
                                        
                                        # Determine MIME type
                                        mime_type, _ = mimetypes.guess_type(material_path)
                                        if not mime_type:
                                            mime_type = 'application/octet-stream'
                                        
                                        st.download_button(
                                            label="⬇️ Download",
                                            data=file_bytes,
                                            file_name=material.get('file_name', 'download'),
                                            mime=mime_type,
                                            key=f"download_mat_{lecture.get('lecture_id', 'unknown')}_{idx}",
                                            use_container_width=True
                                        )
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                            else:
                                st.warning("File not found")
                
                st.markdown("---")


def show_all_resources_table():
    """Display all resources in a table format"""
    storage = get_storage()
    user = st.session_state.user
    
    st.subheader("📊 All Resources Table View")
    
    # Collect all resources
    resources = []
    
    # Get user's courses
    if user['role'] == 'admin':
        courses = storage.get_all_courses()
    elif user['role'] == 'teacher':
        courses = storage.get_all_courses(teacher_id=user['user_id'])
    else:
        all_courses = storage.get_all_courses()
        courses = {
            cid: c for cid, c in all_courses.items()
            if user['user_id'] in c.get('enrolled_students', [])
        }
    
    for course_id, course in courses.items():
        lectures = storage.get_course_lectures(course_id)
        
        for lecture in lectures:
            # Add video
            video_path = lecture.get('video_path', '')
            if video_path:
                resources.append({
                    'Course': course['name'],
                    'Lecture': lecture.get('title', 'Untitled'),
                    'Type': 'Video',
                    'Name': Path(video_path).name,
                    'Size': get_file_size(video_path) if os.path.exists(video_path) else 'N/A',
                    'Path': video_path
                })
            
            # Add materials
            for material in lecture.get('materials', []):
                material_path = material.get('file_path', '')
                resources.append({
                    'Course': course['name'],
                    'Lecture': lecture.get('title', 'Untitled'),
                    'Type': material.get('type', 'Unknown'),
                    'Name': material.get('title', 'Untitled'),
                    'Size': get_file_size(material_path) if os.path.exists(material_path) else 'N/A',
                    'Path': material_path
                })
    
    if resources:
        import pandas as pd
        df = pd.DataFrame(resources)
        
        # Display statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📁 Total Resources", len(resources))
        
        with col2:
            videos = len([r for r in resources if r['Type'] == 'Video'])
            st.metric("🎥 Videos", videos)
        
        with col3:
            documents = len([r for r in resources if r['Type'] in ['Lecture Notes', 'Slides', 'Reference Material']])
            st.metric("📄 Documents", documents)
        
        with col4:
            total_size = sum(
                os.path.getsize(r['Path']) 
                for r in resources 
                if os.path.exists(r['Path'])
            )
            total_size_mb = total_size / (1024 * 1024)
            st.metric("💾 Total Size", f"{total_size_mb:.1f} MB")
        
        st.markdown("---")
        
        # Display table
        st.dataframe(
            df[['Course', 'Lecture', 'Type', 'Name', 'Size']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No resources available yet.")


def show_recent_uploads():
    """Display recently uploaded resources"""
    storage = get_storage()
    user = st.session_state.user
    
    st.subheader("📅 Recent Uploads")
    
    # Get user's courses
    if user['role'] == 'admin':
        courses = storage.get_all_courses()
    elif user['role'] == 'teacher':
        courses = storage.get_all_courses(teacher_id=user['user_id'])
    else:
        all_courses = storage.get_all_courses()
        courses = {
            cid: c for cid, c in all_courses.items()
            if user['user_id'] in c.get('enrolled_students', [])
        }
    
    # Collect recent uploads (last 10)
    recent_items = []
    
    for course_id, course in courses.items():
        lectures = storage.get_course_lectures(course_id)
        
        for lecture in lectures:
            recent_items.append({
                'course': course['name'],
                'title': lecture.get('title', 'Untitled'),
                'type': 'Lecture Video',
                'uploaded_at': lecture.get('created_at', ''),
                'uploaded_by': lecture.get('uploaded_by', 'Unknown')
            })
            
            for material in lecture.get('materials', []):
                recent_items.append({
                    'course': course['name'],
                    'title': material.get('title', 'Untitled'),
                    'type': material.get('type', 'Material'),
                    'uploaded_at': material.get('uploaded_at', ''),
                    'uploaded_by': material.get('uploaded_by', 'Unknown')
                })
    
    # Sort by upload date
    recent_items.sort(key=lambda x: x['uploaded_at'], reverse=True)
    recent_items = recent_items[:10]  # Get last 10
    
    if recent_items:
        for item in recent_items:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                icon = '🎥' if item['type'] == 'Lecture Video' else '📄'
                st.write(f"{icon} **{item['title']}**")
                st.write(f"   Course: {item['course']}")
            
            with col2:
                st.write(f"**Type:** {item['type']}")
            
            with col3:
                uploaded_at = item['uploaded_at']
                st.write(f"📅 {uploaded_at[:10] if uploaded_at else 'Unknown'}")
    else:
        st.info("No recent uploads found.")


def main():
    """Main resources page"""
    st.title("📚 Resources & Downloads")
    
    # Check if user is logged in
    if 'user' not in st.session_state:
        st.error("🚫 Please login to access resources.")
        return
    
    # Navigation tabs
    tab1, tab2, tab3 = st.tabs(["📚 By Course", "📊 All Resources", "📅 Recent"])
    
    with tab1:
        show_resources_by_course()
    
    with tab2:
        show_all_resources_table()
    
    with tab3:
        show_recent_uploads()


if __name__ == "__main__":
    main()
