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
import re
import html


def get_file_size(file_path):
    """Get human-readable file size"""
    try:
        size = os.path.getsize(file_path)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    except (OSError, IOError):
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


def render_lecture_resource_card(lecture, course):
    """Render a lecture resource card with Streamlit native components"""
    video_path = lecture.get('video_path', '')
    youtube_url = lecture.get('youtube_url', '')
    materials = lecture.get('materials', [])
    video_type = lecture.get('video_type', 'file')
    
    is_youtube = video_type == 'youtube' or youtube_url or \
                 ('youtube.com' in video_path or 'youtu.be' in video_path)
    
    video_icon = "🎬" if is_youtube else "🎥"
    
    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### {video_icon} {lecture.get('title', 'Untitled Lecture')}")
        with col2:
            st.caption(f"📚 {course['name'][:20]}...")
        
        desc = lecture.get('description', 'No description available')
        desc_clean = re.sub(r'<[^>]+>', '', html.unescape(desc))
        st.caption(desc_clean[:100] + '...' if len(desc_clean) > 100 else desc_clean)
        
        col1, col2 = st.columns(2)
        with col1:
            if video_path or youtube_url:
                st.metric("Video Type", "YouTube" if is_youtube else "Video File")
        with col2:
            st.metric("Materials", len(materials))
        
        st.markdown("---")
    
    # Display materials
    if materials:
        with st.expander(f"📄 View Materials ({len(materials)})"):
            for i, material in enumerate(materials):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    icon = get_file_icon(material.get('file_name', ''))
                    st.markdown(f"{icon} **{material.get('title', 'Untitled Material')}**")
                    st.caption(material.get('type', 'File'))
                
                with col2:
                    file_path = material.get('file_path', '')
                    if file_path and os.path.exists(file_path):
                        file_size = get_file_size(file_path)
                        st.caption(f"📦 {file_size}")
                
                with col3:
                    if st.button("📥 Download", key=f"download_{lecture.get('lecture_id')}_{i}"):
                        st.info("📥 Download functionality will be implemented")


def show_resources_by_course():
    """Display resources organized by course with card-based UI"""
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
        st.subheader("📚 My Course Resources")
    
    if not courses:
        st.info("📝 No courses available. You need to be enrolled in courses to access resources.")
        return
    
    # Calculate statistics
    total_lectures = 0
    total_materials = 0
    total_courses = len(courses)
    
    for course_id, course in courses.items():
        lectures = storage.get_course_lectures(course_id)
        total_lectures += len(lectures)
        for lecture in lectures:
            total_materials += len(lecture.get('materials', []))
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("� Courses", total_courses)
    with col2:
        st.metric("🎥 Lectures", total_lectures)
    with col3:
        st.metric("📄 Materials", total_materials)
    with col4:
        st.metric("📦 Total Items", total_lectures + total_materials)
    
    st.markdown("---")
    
    # Search and filter
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search = st.text_input("🔍 Search resources", placeholder="Search by lecture, course, or material...", key="resource_search")
    
    with col2:
        filter_type = st.selectbox("Type", ["All", "With Materials", "Videos Only"], key="resource_type_filter")
    
    with col3:
        course_filter = st.selectbox("Course", ["All Courses"] + [c['name'] for c in courses.values()], key="course_filter")
    
    st.markdown("---")
    
    # Display courses and their resources
    resources_found = False
    
    for course_id, course in courses.items():
        # Apply course filter
        if course_filter != "All Courses" and course['name'] != course_filter:
            continue
        
        lectures = storage.get_course_lectures(course_id)
        
        if not lectures:
            continue
        
        # Filter lectures
        filtered_lectures = []
        
        for lecture in lectures:
            # Apply search filter
            if search:
                search_lower = search.lower()
                if search_lower not in lecture.get('title', '').lower() and \
                   search_lower not in lecture.get('description', '').lower() and \
                   search_lower not in course['name'].lower():
                    continue
            
            # Apply type filter
            materials = lecture.get('materials', [])
            video_path = lecture.get('video_path', '')
            
            if filter_type == "With Materials" and not materials:
                continue
            if filter_type == "Videos Only" and not video_path:
                continue
            
            filtered_lectures.append(lecture)
        
        if filtered_lectures:
            resources_found = True
            
            # Course header
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"### 📖 {course['name']}")
                teacher = storage.get_user(course.get('teacher_id', ''))
                teacher_name = teacher.get('full_name', 'Unknown') if teacher else 'Unknown'
                st.caption(f"👨‍🏫 {teacher_name} • {course.get('department', 'N/A')}")
            
            with col2:
                if user['role'] in ['admin', 'teacher']:
                    if st.button(f"📤 Upload", key=f"upload_{course_id}", use_container_width=True):
                        st.session_state.selected_course = course_id
                        st.session_state.current_page = 'upload'
                        st.rerun()
            
            # Display lecture cards
            for lecture in filtered_lectures:
                render_lecture_resource_card(lecture, course)
            
            st.markdown("---")
    
    if not resources_found:
        st.info("🔍 No resources match your search criteria.")


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
