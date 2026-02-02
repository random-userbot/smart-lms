"""
Smart LMS - YouTube Playlist Management Page
Teachers can add playlists to courses and attach materials to videos
"""

import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.auth import get_auth
from services.storage import get_storage
from services.youtube_service import get_youtube_service
from datetime import datetime
import uuid


def main():
    """Main entry point for playlist management"""
    auth = get_auth()
    
    if not auth.is_authenticated():
        st.warning("⚠️ Please log in to manage playlists")
        return
    
    user = st.session_state.user
    
    if user['role'] != 'teacher':
        st.error("❌ Only teachers can manage playlists")
        return
    
    st.title("📺 YouTube Playlist Management")
    st.markdown("Add YouTube playlists to your courses and attach study materials to videos")
    st.markdown("---")
    
    storage = get_storage()
    youtube_service = get_youtube_service()
    
    # Get teacher's courses
    teacher_courses = storage.get_all_courses(user['user_id'])
    
    if not teacher_courses:
        st.info("📚 Create a course first to add playlists")
        return
    
    # Course selector
    course_options = {course['course_id']: course['name'] for course in teacher_courses.values()}
    selected_course_id = st.selectbox(
        "📖 Select Course",
        options=list(course_options.keys()),
        format_func=lambda x: course_options[x]
    )
    
    st.markdown("---")
    
    # Tabs for different operations
    tab1, tab2, tab3 = st.tabs(["📋 View Playlists", "➕ Add Playlist", "🎥 Manage Videos"])
    
    with tab1:
        show_playlists_tab(selected_course_id, youtube_service, storage)
    
    with tab2:
        show_add_playlist_tab(selected_course_id, youtube_service, storage)
    
    with tab3:
        show_manage_videos_tab(selected_course_id, youtube_service, storage)


def show_playlists_tab(course_id: str, youtube_service, storage):
    """Display all playlists for the course"""
    st.markdown("### 📋 Course Playlists")
    
    playlists = youtube_service.get_course_playlists(course_id)
    
    if not playlists:
        st.info("📺 No playlists added yet. Go to 'Add Playlist' tab to add your first playlist!")
        return
    
    for playlist in playlists:
        with st.expander(f"▶️ {playlist['title']} ({playlist['video_count']} videos)", expanded=True):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Description:** {playlist.get('description', 'No description')}")
                st.markdown(f"**Playlist ID:** `{playlist['playlist_id']}`")
                st.markdown(f"**Added:** {playlist['created_at'][:10]}")
                
                # Show playlist URL
                playlist_url = playlist.get('playlist_url', '')
                if playlist_url:
                    st.markdown(f"🔗 [Open in YouTube]({playlist_url})")
            
            with col2:
                if st.button("🗑️ Delete", key=f"del_playlist_{playlist['playlist_id']}", use_container_width=True):
                    if youtube_service.delete_playlist(course_id, playlist['playlist_id']):
                        st.success("✅ Playlist deleted!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to delete playlist")
            
            # Show videos in playlist
            if playlist['videos']:
                st.markdown("#### 🎥 Videos:")
                
                for video in playlist['videos']:
                    video_col1, video_col2 = st.columns([4, 1])
                    
                    with video_col1:
                        st.markdown(f"**{video['order']}. {video['title']}**")
                        
                        # Show attached materials
                        if video['materials']:
                            st.markdown(f"📎 **Materials:** {len(video['materials'])} attached")
                            for material in video['materials']:
                                st.markdown(f"   - 📄 {material['title']} ({material['type']})")
                        else:
                            st.markdown("📎 No materials attached")
                    
                    with video_col2:
                        video_url = video.get('video_url', '')
                        if video_url:
                            st.markdown(f"[▶️ Watch]({video_url})")
                
                st.markdown("---")
            else:
                st.warning("""⚠️ **No videos added yet!**
                
                **How to add videos:**
                1. Go to the **'🎥 Manage Videos'** tab
                2. Select this playlist
                3. Click **'➕ Add Video'** sub-tab
                4. Add each video with its YouTube URL
                5. Set custom order and titles
                
                💡 Then attach study materials in the **'📎 Attach Materials'** sub-tab!""")


def show_add_playlist_tab(course_id: str, youtube_service, storage):
    """Add new playlist to course"""
    st.markdown("### ➕ Import YouTube Playlist")
    
    st.info("💡 **Tip:** Videos will be imported as lectures in your course - manageable via 'My Lectures' and 'Resources' tabs!")
    
    # Check if auto-fetch is available
    from services.youtube_service import AUTO_FETCH_AVAILABLE
    auto_fetch_available = AUTO_FETCH_AVAILABLE
    
    with st.form("add_playlist_form"):
        st.markdown("#### Playlist Information")
        
        playlist_url = st.text_input(
            "📺 YouTube Playlist URL",
            placeholder="https://www.youtube.com/playlist?list=PLxxxxxx",
            help="Paste the full YouTube playlist URL or just the playlist ID"
        )
        
        playlist_title = st.text_input(
            "📝 Playlist Title (Optional for auto-fetch)",
            placeholder="e.g., Introduction to Python Programming",
            help="Leave empty to use YouTube's playlist title (if auto-fetching)"
        )
        
        playlist_description = st.text_area(
            "📄 Description (Optional)",
            placeholder="Describe what this playlist covers...",
            height=100
        )
        
        # Auto-fetch option
        if auto_fetch_available:
            auto_fetch = st.checkbox(
                "🚀 Automatically import all videos from playlist",
                value=True,
                help="Fetches all video titles, descriptions, and order from YouTube automatically (using pytube/yt-dlp)"
            )
        else:
            auto_fetch = False
            st.warning("⚠️ Auto-fetch not available. Install pytube: `pip install pytube`")
        
        submit = st.form_submit_button("➕ Add Playlist", use_container_width=True)
        
        if submit:
            if not playlist_url:
                st.error("❌ Please provide a playlist URL")
                return
            
            try:
                # Auto-fetch or manual mode
                if auto_fetch:
                    with st.spinner("🔄 Fetching playlist and videos from YouTube..."):
                        playlist_data = youtube_service.fetch_playlist_videos(
                            playlist_url,
                            playlist_title or None,
                            playlist_description
                        )
                    
                    # Create lectures from videos
                    import uuid
                    from datetime import datetime
                    
                    created_count = 0
                    for video in playlist_data['videos']:
                        lecture_id = f"youtube_{video['video_id']}_{uuid.uuid4().hex[:8]}"
                        
                        # Create lecture with YouTube URL as video path
                        if storage.create_lecture(
                            lecture_id=lecture_id,
                            title=f"{video['order']}. {video['title']}",
                            course_id=course_id,
                            video_path=video['video_url'],  # YouTube URL
                            duration=video.get('duration', 0),
                            description=video.get('description', ''),
                            video_type='youtube',  # Mark as YouTube video
                            playlist_title=playlist_data['title'],
                            playlist_id=playlist_data['playlist_id'],
                            youtube_video_id=video['video_id']
                        ):
                            created_count += 1
                    
                    if created_count > 0:
                        st.success(f"✅ Successfully created **{created_count} lectures** from playlist '{playlist_data['title']}'!")
                        st.info("""🎯 **What's Next:**
                        - All videos are now available in the **'📚 My Lectures'** tab
                        - Students can watch them like regular lectures
                        - Use **'📎 Resources'** tab to attach study materials to any video
                        - All engagement tracking works automatically!""")
                        st.balloons()
                    else:
                        st.warning("⚠️ No new lectures created - videos may already exist")
                else:
                    # Manual mode
                    if not playlist_title:
                        st.error("❌ Please provide a title for manual mode")
                        return
                    
                    playlist_data = youtube_service.parse_playlist_manual(
                        playlist_url,
                        playlist_title,
                        playlist_description
                    )
                    
                    # Add to course
                    if youtube_service.add_playlist_to_course(course_id, playlist_data):
                        st.success(f"✅ Playlist '{playlist_title}' added successfully!")
                        st.info("""📝 **Next Steps:**
                        1. Go to the **'🎥 Manage Videos'** tab
                        2. Select this playlist
                        3. Click **'➕ Add Video'** to add videos from your YouTube playlist
                        4. Videos will be created as lectures automatically!
                        
                        💡 You need to manually add each video - this gives you control over order and titles!""")
                        st.balloons()
                    else:
                        st.error("❌ This playlist is already added to this course")
            
            except ImportError as e:
                st.error(f"❌ {str(e)}")
                st.info("💡 Install yt-dlp to enable auto-fetch: `pip install yt-dlp`")
            except ValueError as e:
                st.error(f"❌ {str(e)}")
            except Exception as e:
                st.error(f"❌ Error adding playlist: {str(e)}")
                import traceback
                st.code(traceback.format_exc())


def show_manage_videos_tab(course_id: str, youtube_service, storage):
    """Manage videos in playlists"""
    st.markdown("### 🎥 Manage Videos & Materials")
    
    st.info("""💡 **Quick Guide:**
    - Use **'➕ Add Video'** to add videos from your YouTube playlist (you control order & titles)
    - Use **'📎 Attach Materials'** to upload study materials (PDFs, slides, etc.) for each video
    - You can add materials **anytime** - even after students start watching!""")
    
    playlists = youtube_service.get_course_playlists(course_id)
    
    if not playlists:
        st.warning("⚠️ Add a playlist first in the 'Add Playlist' tab")
        return
    
    # Playlist selector
    playlist_options = {p['playlist_id']: p['title'] for p in playlists}
    selected_playlist_id = st.selectbox(
        "📺 Select Playlist",
        options=list(playlist_options.keys()),
        format_func=lambda x: playlist_options[x]
    )
    
    playlist = youtube_service.get_playlist(course_id, selected_playlist_id)
    
    if not playlist:
        st.error("❌ Playlist not found")
        return
    
    st.markdown("---")
    
    # Sub-tabs for adding videos and materials
    video_tab1, video_tab2 = st.tabs(["➕ Add Video", "📎 Attach Materials"])
    
    with video_tab1:
        show_add_video_section(course_id, selected_playlist_id, youtube_service)
    
    with video_tab2:
        show_attach_materials_section(course_id, selected_playlist_id, playlist, youtube_service, storage)


def show_add_video_section(course_id: str, playlist_id: str, youtube_service):
    """Add video to playlist"""
    st.markdown("#### ➕ Add Video to Playlist")
    
    st.markdown("""📝 **Instructions:**
    1. Copy the YouTube video URL from your browser
    2. Paste it below (or just paste the video ID)
    3. Give it a custom title and description
    4. Set the order (1 = first video, 2 = second, etc.)
    5. Click 'Add Video'
    
    ⚠️ **Note:** You need to add each video individually - we don't auto-import to give you full control!""")
    
    st.markdown("---")
    
    with st.form("add_video_form"):
        video_url = st.text_input(
            "🎥 YouTube Video URL",
            placeholder="https://www.youtube.com/watch?v=xxxxxxxxxxx",
            help="Paste the YouTube video URL or video ID"
        )
        
        video_title = st.text_input(
            "📝 Video Title",
            placeholder="e.g., Lecture 1: Python Basics"
        )
        
        video_description = st.text_area(
            "📄 Description (Optional)",
            placeholder="What will students learn in this video?",
            height=80
        )
        
        video_order = st.number_input(
            "📊 Order in Playlist",
            min_value=1,
            value=1,
            help="Position of this video in the playlist (1 = first)"
        )
        
        submit = st.form_submit_button("➕ Add Video", use_container_width=True)
        
        if submit:
            if not video_url or not video_title:
                st.error("❌ Please provide both URL and title")
                return
            
            try:
                # Add video to playlist first
                if youtube_service.add_video_to_playlist(
                    course_id, playlist_id, video_url, 
                    video_title, video_description, int(video_order)
                ):
                    # Extract video ID
                    video_id = youtube_service.extract_video_id(video_url)
                    
                    # Create lecture from video
                    import uuid
                    lecture_id = f"youtube_{video_id}_{uuid.uuid4().hex[:8]}"
                    
                    if storage.create_lecture(
                        lecture_id=lecture_id,
                        title=f"{video_order}. {video_title}",
                        course_id=course_id,
                        video_path=video_url,  # YouTube URL
                        duration=0,
                        description=video_description,
                        video_type='youtube',
                        playlist_id=playlist_id,
                        youtube_video_id=video_id
                    ):
                        st.success(f"✅ Video '{video_title}' added as lecture!")
                        st.info("📚 Students can now watch this in the 'My Lectures' section")
                        st.balloons()
                        st.rerun()
                    else:
                        st.warning("⚠️ Video added to playlist but lecture already exists")
                else:
                    st.error("❌ Failed to add video (might already exist)")
            
            except Exception as e:
                st.error(f"❌ Error adding video: {str(e)}")


def show_attach_materials_section(course_id: str, playlist_id: str, playlist: dict, 
                                  youtube_service, storage):
    """Attach materials to videos"""
    st.markdown("#### 📎 Attach Study Materials to Videos")
    
    if not playlist['videos']:
        st.info("📝 Add videos to this playlist first")
        return
    
    # Video selector
    video_options = {v['video_id']: f"{v['order']}. {v['title']}" for v in playlist['videos']}
    selected_video_id = st.selectbox(
        "🎥 Select Video",
        options=list(video_options.keys()),
        format_func=lambda x: video_options[x],
        key="material_video_selector"
    )
    
    # Get selected video
    selected_video = None
    for video in playlist['videos']:
        if video['video_id'] == selected_video_id:
            selected_video = video
            break
    
    if not selected_video:
        st.error("❌ Video not found")
        return
    
    st.markdown("---")
    
    # Show existing materials
    if selected_video['materials']:
        st.markdown("**📎 Attached Materials:**")
        
        for material in selected_video['materials']:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"📄 **{material['title']}** ({material['type']})")
            
            with col2:
                # Download button
                if os.path.exists(material['file_path']):
                    with open(material['file_path'], 'rb') as f:
                        st.download_button(
                            "📥 Download",
                            data=f.read(),
                            file_name=material['file_name'],
                            key=f"dl_{material['material_id']}"
                        )
            
            with col3:
                if st.button("🗑️", key=f"del_{material['material_id']}"):
                    if youtube_service.remove_material_from_video(
                        course_id, playlist_id, selected_video_id, material['material_id']
                    ):
                        st.success("✅ Material removed!")
                        st.rerun()
        
        st.markdown("---")
    
    # Upload new material
    st.markdown("**➕ Upload New Material:**")
    
    with st.form("upload_material_form"):
        material_title = st.text_input("📝 Material Title", placeholder="e.g., Lecture Notes")
        
        uploaded_file = st.file_uploader(
            "📤 Upload File",
            type=['pdf', 'pptx', 'docx', 'txt', 'zip'],
            help="Supported: PDF, PowerPoint, Word, Text, ZIP"
        )
        
        submit = st.form_submit_button("📎 Attach Material", use_container_width=True)
        
        if submit:
            if not material_title or not uploaded_file:
                st.error("❌ Please provide both title and file")
                return
            
            try:
                # Save file
                upload_dir = f"./data/courses/{course_id}/materials"
                os.makedirs(upload_dir, exist_ok=True)
                
                material_id = str(uuid.uuid4())
                file_ext = os.path.splitext(uploaded_file.name)[1]
                file_name = f"{material_id}{file_ext}"
                file_path = os.path.join(upload_dir, file_name)
                
                # Write file
                with open(file_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())
                
                # Create material data
                material = {
                    'material_id': material_id,
                    'title': material_title,
                    'type': file_ext[1:],  # Remove dot
                    'file_path': file_path,
                    'file_name': uploaded_file.name
                }
                
                # Attach to video
                if youtube_service.attach_material_to_video(
                    course_id, playlist_id, selected_video_id, material
                ):
                    st.success(f"✅ Material '{material_title}' attached successfully!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Failed to attach material")
                    # Clean up file
                    if os.path.exists(file_path):
                        os.remove(file_path)
            
            except Exception as e:
                st.error(f"❌ Error uploading material: {str(e)}")


if __name__ == "__main__":
    main()
