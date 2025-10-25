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
    
    # Check if it's a YouTube video (either in youtube_url field or video_path)
    youtube_url = lecture.get('youtube_url') or (
        lecture.get('video_path') if lecture.get('video_type') == 'youtube' 
        or ('youtube.com' in lecture.get('video_path', '') or 'youtu.be' in lecture.get('video_path', ''))
        else None
    )
    
    behavioral_logger.log_lecture_start(lecture_id, course_id, 
                                        video_type='youtube' if youtube_url else 'local')
    
    # Initialize anti-cheating monitor
    anti_cheating = get_anti_cheating_monitor(student_id, lecture_id, course_id)
    
    # Inject browser visibility detection JavaScript
    st.components.v1.html(check_browser_visibility(), height=0)
    
    # Video player section
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Check if YouTube URL is provided
        if youtube_url:
            youtube_id = extract_youtube_id(youtube_url)
            
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
    
    # Enhanced Feedback section
    st.markdown("---")
    st.markdown("### 💬 Comprehensive Lecture Feedback")
    st.caption("Your feedback helps improve teaching quality and course content")
    
    # Check if already submitted
    storage = get_storage()
    existing_feedback = storage.get_feedback(lecture_id=lecture_id, student_id=student_id)
    
    if existing_feedback:
        st.info("✅ You have already submitted feedback for this lecture. You can update it below.")
    
    with st.form("detailed_feedback_form"):
        st.markdown("#### 📊 Rate Your Learning Experience")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Overall Rating
            overall_rating = st.slider(
                "⭐ Overall Rating",
                min_value=1,
                max_value=5,
                value=3,
                help="Your overall experience with this lecture"
            )
            
            # Content Quality
            content_quality = st.slider(
                "📚 Content Quality",
                min_value=1,
                max_value=5,
                value=3,
                help="How relevant and useful was the content?"
            )
            
            # Clarity
            clarity_rating = st.slider(
                "💡 Clarity & Understanding",
                min_value=1,
                max_value=5,
                value=3,
                help="How clear and understandable were the explanations?"
            )
        
        with col2:
            # Teaching Pace
            pace_rating = st.slider(
                "⏱️ Teaching Pace",
                min_value=1,
                max_value=5,
                value=3,
                help="1=Too Slow, 3=Just Right, 5=Too Fast"
            )
            
            # Engagement Level
            engagement_rating = st.slider(
                "🎯 Engagement Level",
                min_value=1,
                max_value=5,
                value=3,
                help="How engaging and interesting was the lecture?"
            )
            
            # Visual Aids Quality
            visual_aids = st.slider(
                "📊 Visual Aids & Examples",
                min_value=1,
                max_value=5,
                value=3,
                help="Quality of slides, diagrams, and examples"
            )
        
        st.markdown("---")
        st.markdown("#### 📝 Written Feedback")
        
        # What went well
        strengths = st.text_area(
            "✅ What did you like most about this lecture?",
            placeholder="e.g., Clear explanations, good examples, interactive demonstrations...",
            height=80,
            key="strengths"
        )
        
        # Areas for improvement
        improvements = st.text_area(
            "🔧 What could be improved?",
            placeholder="e.g., More examples needed, faster pace, better visual aids...",
            height=80,
            key="improvements"
        )
        
        # Additional comments
        additional_comments = st.text_area(
            "💬 Additional Comments (Optional)",
            placeholder="Any other thoughts, suggestions, or questions?",
            height=80,
            key="comments"
        )
        
        # Difficulty level
        st.markdown("---")
        difficulty_level = st.select_slider(
            "📊 Difficulty Level",
            options=["Too Easy", "Easy", "Just Right", "Challenging", "Too Difficult"],
            value="Just Right"
        )
        
        # Would recommend
        would_recommend = st.checkbox(
            "✅ I would recommend this lecture to other students",
            value=True
        )
        
        # Technical issues
        had_technical_issues = st.checkbox(
            "⚠️ I experienced technical issues during this lecture"
        )
        
        if had_technical_issues:
            technical_details = st.text_area(
                "Please describe the technical issues:",
                placeholder="e.g., Video buffering, audio problems, login issues...",
                height=60,
                key="technical"
            )
        else:
            technical_details = ""
        
        st.markdown("---")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.caption("🔒 Your feedback is anonymous and will be used to improve teaching quality")
        with col2:
            submit_feedback = st.form_submit_button("📤 Submit Feedback", use_container_width=True, type="primary")
        
        if submit_feedback:
            # Validate feedback
            if not strengths and not improvements and not additional_comments:
                st.warning("⚠️ Please provide at least some written feedback")
            else:
                # Combine all text feedback for NLP analysis
                combined_text = f"""
                Strengths: {strengths}
                Improvements: {improvements}
                Additional Comments: {additional_comments}
                """.strip()
                
                # Perform NLP analysis
                from services.nlp import get_nlp_service
                nlp_service = get_nlp_service()
                sentiment_analysis = nlp_service.analyze_sentiment(combined_text)
                keywords = nlp_service.extract_keywords(combined_text, top_n=10)
                themes = nlp_service.detect_themes(combined_text)
                
                # Calculate composite scores
                composite_score = (overall_rating + content_quality + clarity_rating + 
                                 engagement_rating + visual_aids) / 5
                
                # Save comprehensive feedback
                feedback_id = existing_feedback[0]['feedback_id'] if existing_feedback else str(uuid.uuid4())
                
                storage.save_detailed_feedback(
                    feedback_id=feedback_id,
                    student_id=student_id,
                    lecture_id=lecture_id,
                    course_id=course_id,
                    # Rating scores
                    overall_rating=overall_rating,
                    content_quality=content_quality,
                    clarity_rating=clarity_rating,
                    pace_rating=pace_rating,
                    engagement_rating=engagement_rating,
                    visual_aids_rating=visual_aids,
                    composite_score=composite_score,
                    # Written feedback
                    strengths=strengths,
                    improvements=improvements,
                    additional_comments=additional_comments,
                    # Metadata
                    difficulty_level=difficulty_level,
                    would_recommend=would_recommend,
                    had_technical_issues=had_technical_issues,
                    technical_details=technical_details,
                    # NLP Analysis
                    sentiment=sentiment_analysis,
                    keywords=keywords,
                    themes=themes,
                    combined_text=combined_text
                )
                
                # Log feedback submission
                behavioral_logger.log_feedback_submission('lecture', overall_rating)
                
                # Get teacher info
                lecture_data = storage.get_lecture(lecture_id)
                course_data = storage.get_course(course_id)
                teacher_id = course_data.get('teacher_id') if course_data else None
                
                # Update teacher evaluation metrics
                if teacher_id:
                    storage.update_teacher_evaluation(
                        teacher_id=teacher_id,
                        lecture_id=lecture_id,
                        course_id=course_id,
                        feedback_id=feedback_id,
                        ratings={
                            'overall': overall_rating,
                            'content_quality': content_quality,
                            'clarity': clarity_rating,
                            'pace': pace_rating,
                            'engagement': engagement_rating,
                            'visual_aids': visual_aids,
                            'composite': composite_score
                        },
                        sentiment=sentiment_analysis
                    )
                
                st.success("✅ Thank you for your detailed feedback!")
                st.balloons()
                
                # Show sentiment analysis result
                sentiment_label = sentiment_analysis.get('label', 'neutral')
                sentiment_emoji = {"positive": "😊", "negative": "😟", "neutral": "😐"}.get(sentiment_label, "😐")
                st.info(f"{sentiment_emoji} Feedback sentiment: **{sentiment_label.title()}**")
                
                st.rerun()
    
    # Session end cleanup
    if st.button("🏁 End Session", type="secondary"):
        cleanup_logger(student_id, lecture_id)
        cleanup_monitor(student_id, lecture_id)
        st.success("✅ Session ended. Data saved.")
        st.rerun()


def render_lecture_card(lecture, course, user):
    """Render a lecture card with visual styling"""
    storage = get_storage()
    
    # Check if student has watched
    engagement_logs = storage.get_engagement_logs(
        student_id=user['user_id'],
        lecture_id=lecture['lecture_id']
    )
    
    has_watched = len(engagement_logs) > 0
    latest_engagement = engagement_logs[-1] if engagement_logs else None
    
    # Determine status and color
    if has_watched:
        status_color = "#28a745"  # Green
        status_text = "✅ Watched"
        status_badge = "watched"
        button_type = "primary"
    else:
        status_color = "#007bff"  # Blue
        status_text = "� New"
        status_badge = "new"
        button_type = "secondary"
    
    # Duration in minutes
    duration_minutes = lecture.get('duration', 0) // 60 if lecture.get('duration') else 0
    
    # Video type indicator
    video_type = lecture.get('video_type', 'file')
    video_icon = "🎬" if video_type == 'youtube' else "📹"
    
    # Materials and quizzes count
    materials_count = len(lecture.get('materials', []))
    quizzes_count = len(lecture.get('quizzes', []))
    
    card_html = f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    ">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
            <h3 style="color: white; margin: 0; font-size: 1.3em;">
                {video_icon} {lecture['title']}
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
        
        <p style="color: rgba(255,255,255,0.9); margin: 10px 0; font-size: 0.95em;">
            {lecture.get('description', 'No description available')}
        </p>
        
        <div style="display: flex; gap: 20px; margin-top: 15px; flex-wrap: wrap;">
            <div style="color: white;">
                <span style="font-size: 1.2em;">⏱️</span>
                <span style="margin-left: 5px;">{duration_minutes} min</span>
            </div>
            <div style="color: white;">
                <span style="font-size: 1.2em;">📄</span>
                <span style="margin-left: 5px;">{materials_count} Materials</span>
            </div>
            <div style="color: white;">
                <span style="font-size: 1.2em;">📝</span>
                <span style="margin-left: 5px;">{quizzes_count} Quizzes</span>
            </div>
            {f'''<div style="color: white;">
                <span style="font-size: 1.2em;">📊</span>
                <span style="margin-left: 5px;">Score: {latest_engagement['engagement_score']:.0f}%</span>
            </div>''' if latest_engagement else ''}
        </div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)
    
    # Action button
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        if has_watched:
            button_text = "▶️ Watch Again"
        else:
            button_text = "▶️ Watch Now"
        
        if st.button(button_text, key=f"watch_{lecture['lecture_id']}", type=button_type, use_container_width=True):
            st.session_state.selected_lecture = lecture
            st.session_state.current_page = 'watch_lecture'
            st.rerun()
    
    with col2:
        if materials_count > 0:
            if st.button(f"📄 Materials ({materials_count})", key=f"materials_{lecture['lecture_id']}", use_container_width=True):
                st.session_state.current_page = 'resources'
                st.session_state.selected_lecture_id = lecture['lecture_id']
                st.rerun()
    
    with col3:
        if quizzes_count > 0:
            if st.button(f"📝 Quizzes ({quizzes_count})", key=f"quizzes_{lecture['lecture_id']}", use_container_width=True):
                st.session_state.current_page = 'quizzes'
                st.session_state.selected_lecture_id = lecture['lecture_id']
                st.rerun()


def show_lecture_list(course_id):
    """Display list of lectures for a course with card-based UI"""
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
        st.info("� No lectures available yet. Check back later!")
        return
    
    # Statistics
    user = st.session_state.user
    watched_count = 0
    total_engagement = 0
    
    for lecture in lectures:
        engagement_logs = storage.get_engagement_logs(
            student_id=user['user_id'],
            lecture_id=lecture['lecture_id']
        )
        if engagement_logs:
            watched_count += 1
            total_engagement += engagement_logs[-1].get('engagement_score', 0)
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📚 Total Lectures", len(lectures))
    with col2:
        st.metric("✅ Watched", watched_count)
    with col3:
        st.metric("📺 Remaining", len(lectures) - watched_count)
    with col4:
        avg_engagement = total_engagement / watched_count if watched_count > 0 else 0
        st.metric("� Avg Engagement", f"{avg_engagement:.0f}%")
    
    st.markdown("---")
    
    # Search and filter
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("🔍 Search lectures", placeholder="Search by title or description...", key="lecture_search")
    with col2:
        filter_option = st.selectbox("Filter", ["All", "Watched", "Not Watched"], key="lecture_filter")
    
    # Filter lectures
    filtered_lectures = lectures
    
    if search_query:
        filtered_lectures = [
            lec for lec in filtered_lectures
            if search_query.lower() in lec['title'].lower() or
               search_query.lower() in lec.get('description', '').lower()
        ]
    
    if filter_option == "Watched":
        filtered_lectures = [
            lec for lec in filtered_lectures
            if storage.get_engagement_logs(user['user_id'], lec['lecture_id'])
        ]
    elif filter_option == "Not Watched":
        filtered_lectures = [
            lec for lec in filtered_lectures
            if not storage.get_engagement_logs(user['user_id'], lec['lecture_id'])
        ]
    
    st.markdown("---")
    
    # Display lecture cards
    if not filtered_lectures:
        st.info("🔍 No lectures match your search criteria.")
    else:
        st.subheader(f"🎥 Lectures ({len(filtered_lectures)})")
        for lecture in filtered_lectures:
            render_lecture_card(lecture, course, user)


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
