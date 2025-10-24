"""
Smart LMS - Lectures Page
Students can watch lectures with real-time engagement tracking, behavioral logging, and anti-cheating
Supports both local videos and YouTube links
"""

import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.auth import get_auth
from services.storage import get_storage
from services.pip_webcam_live import render_pip_webcam, render_engagement_sidebar
from services.behavioral_logger import get_behavioral_logger, cleanup_logger
from services.anti_cheating import get_anti_cheating_monitor, cleanup_monitor, render_integrity_widget, check_browser_visibility
from datetime import datetime
import uuid
import re


def extract_youtube_id(url: str) -> str:
    """
    Extract YouTube video ID from URL
    
    Args:
        url: YouTube URL (various formats supported)
    
    Returns:
        YouTube video ID or None
    """
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/v/([a-zA-Z0-9_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    # If it's just the ID
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
        return url
    
    return None


def show_lecture_player(lecture):
    """Display video player with real-time engagement tracking and anti-cheating"""
    user = st.session_state.user
    student_id = user['user_id']
    lecture_id = lecture['lecture_id']
    course_id = lecture.get('course_id', 'unknown')
    
    st.subheader(f"🎥 {lecture['title']}")
    
    if lecture.get('description'):
        st.markdown(f"*{lecture['description']}*")
    
    st.markdown("---")
    
    # Initialize behavioral logger
    behavioral_logger = get_behavioral_logger(student_id, lecture_id, course_id)
    behavioral_logger.log_lecture_start(lecture_id, course_id, 
                                        video_type='youtube' if lecture.get('youtube_url') else 'local')
    
    # Initialize anti-cheating monitor
    anti_cheating = get_anti_cheating_monitor(student_id, lecture_id, course_id)
    
    # Inject browser visibility detection JavaScript
    st.components.v1.html(check_browser_visibility(), height=0)
    
    # Video player section
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Check if YouTube URL is provided
        if lecture.get('youtube_url'):
            youtube_id = extract_youtube_id(lecture['youtube_url'])
            
            if youtube_id:
                st.markdown("### 📺 YouTube Lecture")
                
                # Embed YouTube video with custom player
                youtube_embed = f"""
                <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; background: #000;">
                    <iframe 
                        id="youtube-player"
                        style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
                        src="https://www.youtube.com/embed/{youtube_id}?enablejsapi=1&rel=0&modestbranding=1&playsinline=1"
                        frameborder="0"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowfullscreen>
                    </iframe>
                </div>
                
                <script src="https://www.youtube.com/iframe_api"></script>
                <script>
                var player;
                var lastSpeed = 1.0;
                
                function onYouTubeIframeAPIReady() {{
                    player = new YT.Player('youtube-player', {{
                        events: {{
                            'onReady': onPlayerReady,
                            'onStateChange': onPlayerStateChange
                        }}
                    }});
                }}
                
                function onPlayerReady(event) {{
                    // Monitor playback speed changes
                    setInterval(function() {{
                        var currentSpeed = player.getPlaybackRate();
                        if (currentSpeed != lastSpeed) {{
                            console.log('Speed changed from ' + lastSpeed + ' to ' + currentSpeed);
                            
                            // Check if speed exceeds 1.25x
                            if (currentSpeed > 1.25) {{
                                alert('⚠️ Playback speed too high! Maximum allowed: 1.25x');
                                player.setPlaybackRate(1.0);
                            }}
                            
                            lastSpeed = currentSpeed;
                        }}
                    }}, 1000);
                }}
                
                function onPlayerStateChange(event) {{
                    if (event.data == YT.PlayerState.PLAYING) {{
                        console.log('Video playing');
                    }} else if (event.data == YT.PlayerState.PAUSED) {{
                        console.log('Video paused');
                    }}
                }}
                </script>
                """
                
                st.components.v1.html(youtube_embed, height=450)
                
                # Speed control warning
                st.info("ℹ️ **Note:** Playback speed is limited to 1.25x for integrity monitoring.")
            else:
                st.error("❌ Invalid YouTube URL. Please contact your instructor.")
                st.info(f"URL: {lecture['youtube_url']}")
        else:
            # Local video file
            video_path = lecture.get('video_path', '')
            
            if video_path and os.path.exists(video_path):
                st.video(video_path)
            else:
                st.error(f"❌ Video file not found: {video_path}")
                st.info("� The video may need to be uploaded by the teacher, or a YouTube link may be added.")
    
    with col2:
        st.markdown("### 📊 Live Monitoring")
        
        # Real-time engagement tracking with PiP webcam
        st.markdown("**🎥 Webcam Tracking:**")
        
        try:
            # Render PiP webcam (bottom-right, always visible)
            pip_webcam = render_pip_webcam(lecture_id, course_id, student_id)
            
            # Show current engagement in sidebar
            render_engagement_sidebar(pip_webcam)
            
        except Exception as e:
            st.error(f"❌ Webcam error: {str(e)}")
            st.info("💡 Please allow camera access for engagement tracking.")
    
    # Render integrity monitoring in sidebar
    render_integrity_widget(anti_cheating)
    
    st.markdown("---")
    
    # Lecture materials
    if lecture.get('materials'):
        st.markdown("### 📚 Course Materials")
        for material in lecture['materials']:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"📄 **{material['title']}** ({material['type']})")
            with col2:
                if st.button("📥 Download", key=f"download_{material['material_id']}"):
                    behavioral_logger.log_resource_download(material['material_id'], material['type'])
                    st.info("Download functionality will be implemented")
    
    # Quiz section
    if lecture.get('quizzes'):
        st.markdown("### 📝 Quizzes")
        for quiz in lecture['quizzes']:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"📝 **{quiz['title']}** ({len(quiz['questions'])} questions)")
            with col2:
                if st.button("▶️ Take Quiz", key=f"quiz_{quiz['quiz_id']}"):
                    st.session_state.selected_quiz = quiz
                    st.session_state.current_page = 'take_quiz'
                    st.rerun()
    
    # Feedback section
    st.markdown("---")
    st.markdown("### 💬 Lecture Feedback")
    
    with st.form("feedback_form"):
        rating = st.slider("Rate this lecture", 1, 5, 3)
        feedback_text = st.text_area(
            "Your feedback",
            placeholder="What did you think about this lecture? Any suggestions?",
            height=100
        )
        
        submit_feedback = st.form_submit_button("📤 Submit Feedback")
        
        if submit_feedback:
            if feedback_text:
                storage = get_storage()
                
                feedback_id = str(uuid.uuid4())
                storage.save_feedback(
                    feedback_id=feedback_id,
                    student_id=student_id,
                    lecture_id=lecture_id,
                    text=feedback_text,
                    rating=rating,
                    sentiment={}  # Will be computed in Phase 4
                )
                
                # Log feedback submission
                behavioral_logger.log_feedback_submission('lecture', rating)
                
                st.success("✅ Thank you for your feedback!")
            else:
                st.warning("⚠️ Please write some feedback")
    
    # Session end cleanup
    if st.button("🏁 End Session", type="secondary"):
        cleanup_logger(student_id, lecture_id)
        cleanup_monitor(student_id, lecture_id)
        st.success("✅ Session ended. Data saved.")
        st.rerun()


def show_lecture_list(course_id):
    """Display list of lectures for a course"""
    storage = get_storage()
    
    # Get course info
    course = storage.get_course(course_id)
    if not course:
        st.error("❌ Course not found")
        return
    
    st.title(f"📚 {course['name']}")
    st.markdown(f"*{course.get('description', '')}*")
    st.markdown("---")
    
    # Get lectures
    lectures = storage.get_course_lectures(course_id)
    
    if not lectures:
        st.info("📝 No lectures available yet. Check back later!")
        return
    
    # Display lectures
    st.subheader("🎥 Available Lectures")
    
    user = st.session_state.user
    
    for lecture in lectures:
        with st.expander(f"📖 {lecture['title']}", expanded=False):
            st.markdown(f"**Description:** {lecture.get('description', 'No description')}")
            st.markdown(f"**Duration:** {lecture.get('duration', 0) // 60} minutes")
            
            # Check if student has watched
            engagement_logs = storage.get_engagement_logs(
                student_id=user['user_id'],
                lecture_id=lecture['lecture_id']
            )
            
            if engagement_logs:
                latest_log = engagement_logs[-1]
                st.success(f"✅ Watched | Engagement Score: {latest_log['engagement_score']:.1f}/100")
            else:
                st.info("📺 Not watched yet")
            
            # Show materials count
            materials_count = len(lecture.get('materials', []))
            quizzes_count = len(lecture.get('quizzes', []))
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📄 Materials", materials_count)
            with col2:
                st.metric("📝 Quizzes", quizzes_count)
            with col3:
                if st.button("▶️ Watch Now", key=f"watch_{lecture['lecture_id']}"):
                    st.session_state.selected_lecture = lecture
                    st.session_state.current_page = 'watch_lecture'
                    st.rerun()


def main():
    """Main lectures page"""
    # Check authentication
    auth = get_auth()
    auth.require_role('student')
    
    # Check if watching a specific lecture
    if st.session_state.get('current_page') == 'watch_lecture' and 'selected_lecture' in st.session_state:
        lecture = st.session_state.selected_lecture
        
        # Back button
        if st.button("← Back to Lectures"):
            st.session_state.current_page = 'lectures'
            del st.session_state.selected_lecture
            st.rerun()
        
        show_lecture_player(lecture)
    else:
        # Show lecture list
        st.title("🎥 My Lectures")
        
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
        
        # Course selection
        course_options = {cid: c['name'] for cid, c in enrolled_courses.items()}
        
        if 'selected_course' not in st.session_state:
            st.session_state.selected_course = list(course_options.keys())[0]
        
        selected_course = st.selectbox(
            "Select Course",
            options=list(course_options.keys()),
            format_func=lambda x: course_options[x],
            key='course_selector'
        )
        
        st.session_state.selected_course = selected_course
        
        # Show lectures for selected course
        show_lecture_list(selected_course)


if __name__ == "__main__":
    main()
