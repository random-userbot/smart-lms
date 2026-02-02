"""
Smart LMS - YouTube Playlist Viewer (Student)
Students can watch YouTube playlist videos and access materials
"""

import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.auth import get_auth
from services.storage import get_storage
from services.youtube_service import get_youtube_service
from services.universal_logger import log_video_action
from datetime import datetime


def main():
    """Main entry point for playlist viewer"""
    auth = get_auth()
    
    if not auth.is_authenticated():
        st.warning("⚠️ Please log in to view playlists")
        return
    
    user = st.session_state.user
    
    if user['role'] != 'student':
        st.error("❌ This page is for students only")
        return
    
    show_playlists_page(user)


def show_playlists_page(user):
    """Display playlists page for students"""
    st.title("📺 YouTube Playlists")
    st.markdown("Watch course videos and access study materials")
    st.markdown("---")
    
    storage = get_storage()
    youtube_service = get_youtube_service()
    student_id = user['user_id']
    
    # Get enrolled courses
    all_courses = storage.get_all_courses()
    enrolled_courses = {cid: c for cid, c in all_courses.items() 
                       if student_id in c.get('enrolled_students', [])}
    
    if not enrolled_courses:
        st.info("📚 Enroll in courses to access playlists")
        return
    
    # Course selector
    course_options = {course_id: course['name'] for course_id, course in enrolled_courses.items()}
    selected_course_id = st.selectbox(
        "📖 Select Course",
        options=list(course_options.keys()),
        format_func=lambda x: course_options[x]
    )
    
    # Get playlists for selected course
    playlists = youtube_service.get_course_playlists(selected_course_id)
    
    if not playlists:
        st.info("📺 No playlists available for this course yet")
        return
    
    st.markdown("---")
    
    # Display playlists
    for playlist in playlists:
        with st.expander(f"▶️ {playlist['title']} ({playlist['video_count']} videos)", expanded=True):
            st.markdown(f"**{playlist.get('description', '')}**")
            
            if not playlist['videos']:
                st.info("📝 No videos added yet")
                continue
            
            # Video selector
            video_options = {v['video_id']: f"{v['order']}. {v['title']}" for v in playlist['videos']}
            
            selected_video_id = st.selectbox(
                "🎥 Select Video",
                options=list(video_options.keys()),
                format_func=lambda x: video_options[x],
                key=f"video_select_{playlist['playlist_id']}"
            )
            
            # Get selected video
            selected_video = None
            for video in playlist['videos']:
                if video['video_id'] == selected_video_id:
                    selected_video = video
                    break
            
            if selected_video:
                show_video_player(selected_video, selected_course_id, playlist, student_id)


def show_video_player(video: dict, course_id: str, playlist: dict, student_id: str):
    """Display YouTube video player with materials"""
    st.markdown("---")
    st.markdown(f"### 🎥 {video['title']}")
    
    if video.get('description'):
        st.markdown(f"*{video['description']}*")
    
    # Log video start
    log_video_action(student_id, 'video_start', course_id, f"playlist_{playlist['playlist_id']}", video_id=video['video_id'])
    
    # Embed YouTube video
    video_id = video['video_id']
    
    # Create YouTube embed with custom player
    youtube_embed = f"""
    <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; background: #000; border-radius: 10px;">
        <iframe 
            src="https://www.youtube.com/embed/{video_id}?rel=0&modestbranding=1" 
            frameborder="0" 
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
            allowfullscreen
            style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;">
        </iframe>
    </div>
    
    <script>
        // Track video interactions
        var player = document.querySelector('iframe');
        
        // Log video end when user navigates away
        window.addEventListener('beforeunload', function() {{
            // Could send completion event here
        }});
    </script>
    """
    
    st.markdown(youtube_embed, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Display study materials
    if video['materials']:
        st.markdown("### 📎 Study Materials")
        
        for material in video['materials']:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"📄 **{material['title']}** ({material['type']})")
            
            with col2:
                # Download button
                if os.path.exists(material['file_path']):
                    try:
                        with open(material['file_path'], 'rb') as f:
                            file_data = f.read()
                        
                        st.download_button(
                            "📥 Download",
                            data=file_data,
                            file_name=material['file_name'],
                            mime=f"application/{material['type']}",
                            key=f"download_{material['material_id']}",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"Error loading file: {str(e)}")
                else:
                    st.warning("File not found")
    else:
        st.info("📝 No study materials attached to this video")
    
    # Video navigation
    st.markdown("---")
    
    playlist_videos = sorted(playlist['videos'], key=lambda x: x['order'])
    current_index = next((i for i, v in enumerate(playlist_videos) if v['video_id'] == video['video_id']), -1)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if current_index > 0:
            if st.button("⬅️ Previous Video", use_container_width=True):
                st.session_state[f"video_select_{playlist['playlist_id']}"] = playlist_videos[current_index - 1]['video_id']
                st.rerun()
    
    with col2:
        st.markdown(f"<center>Video {current_index + 1} of {len(playlist_videos)}</center>", unsafe_allow_html=True)
    
    with col3:
        if current_index < len(playlist_videos) - 1:
            if st.button("Next Video ➡️", use_container_width=True):
                st.session_state[f"video_select_{playlist['playlist_id']}"] = playlist_videos[current_index + 1]['video_id']
                st.rerun()


if __name__ == "__main__":
    main()
