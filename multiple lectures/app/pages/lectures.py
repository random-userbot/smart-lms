"""
Smart LMS - Lectures Page
Students can watch lectures with webcam engagement tracking
"""

import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.auth import get_auth
from services.storage import get_storage
from services.nlp import get_nlp_service
from datetime import datetime
import uuid


def show_consent_dialog():
    """Show webcam consent dialog"""
    if 'consent_given' not in st.session_state:
        st.session_state.consent_given = False
    
    if not st.session_state.consent_given:
        st.warning("⚠️ Webcam Engagement Tracking")
        st.markdown("""
        This lecture includes webcam-based engagement tracking to improve your learning experience.
        
        **What we collect:**
        - Gaze direction and attention patterns
        - Head pose and stability
        - Engagement metrics (no raw video stored)
        
        **Your privacy:**
        - Only derived features are stored
        - Raw video is NOT saved
        - You can request data deletion anytime
        - Data is anonymized after 180 days
        
        **You can:**
        - Disable webcam tracking (affects engagement score)
        - View your data in the Ethical AI Dashboard
        - Request data deletion from your profile
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ I Consent", use_container_width=True):
                st.session_state.consent_given = True
                st.rerun()
        with col2:
            if st.button("❌ Continue Without Webcam", use_container_width=True):
                st.session_state.consent_given = False
                st.session_state.webcam_disabled = True
                st.rerun()
        
        st.stop()


def show_lecture_player(lecture):
    """Display video player with engagement tracking"""
    st.subheader(f"🎥 {lecture['title']}")
    
    if lecture.get('description'):
        st.markdown(f"*{lecture['description']}*")
    
    st.markdown("---")
    
    # Check if video file exists
    video_path = lecture['video_path']
    if not os.path.exists(video_path):
        st.error(f"❌ Video file not found: {video_path}")
        st.info("💡 The video may need to be uploaded by the teacher.")
        return
    
    # Show consent dialog if not given
    if 'webcam_disabled' not in st.session_state:
        show_consent_dialog()
    
    # Video player
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.video(video_path)
    
    with col2:
        st.markdown("### 📊 Engagement")
        
        if st.session_state.get('consent_given', False):
            # Webcam tracking enabled
            st.success("✅ Webcam Active")
            
            # Placeholder for real-time engagement score
            engagement_placeholder = st.empty()
            engagement_placeholder.metric(
                "Current Score",
                "85/100",
                "+5",
                help="Real-time engagement score"
            )
            
            # Webcam feed placeholder (will be implemented in Phase 3)
            st.markdown("---")
            st.markdown("**Live Feed:**")
            st.info("📹 Webcam tracking will be implemented in Phase 3")
            
            # Toggle webcam
            if st.button("⏸️ Pause Webcam"):
                st.session_state.webcam_disabled = True
                st.rerun()
        else:
            st.warning("⚠️ Webcam Disabled")
            st.info("Enable webcam for engagement tracking")
            
            if st.button("▶️ Enable Webcam"):
                st.session_state.webcam_disabled = False
                show_consent_dialog()
    
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
                nlp_service = get_nlp_service()
                user = st.session_state.user
                
                # Perform sentiment analysis
                sentiment_result = nlp_service.analyze_sentiment(feedback_text)
                
                feedback_id = str(uuid.uuid4())
                storage.save_feedback(
                    feedback_id=feedback_id,
                    student_id=user['user_id'],
                    lecture_id=lecture['lecture_id'],
                    text=feedback_text,
                    rating=rating,
                    sentiment=sentiment_result
                )
                
                # Show sentiment feedback to student
                sentiment_label = sentiment_result.get('label', 'neutral')
                sentiment_emoji = {'positive': '😊', 'negative': '😟', 'neutral': '😐'}.get(sentiment_label, '😐')
                
                st.success(f"✅ Thank you for your feedback! {sentiment_emoji} Your feedback sentiment: {sentiment_label.capitalize()}")
            else:
                st.warning("⚠️ Please write some feedback")


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
