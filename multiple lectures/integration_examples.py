"""
Quick Integration Example
Shows how to integrate intelligent engagement tracking into existing pages
"""

# ============================================================================
# EXAMPLE 1: PDF Reader Integration
# File: services/pdf_reader.py
# ============================================================================

from services.universal_logger import get_activity_logger, log_pdf_action, log_download

def display_pdf(self, pdf_path: str, material_id: str, material_title: str, 
                course_id: str, lecture_id: str, student_id: str):
    """Display PDF with intelligent tracking"""
    
    logger = get_activity_logger()
    
    # Log PDF open
    log_pdf_action(student_id, 'pdf_open', course_id, lecture_id, material_id)
    
    # ... PDF display code ...
    
    # Log page turns (in callback or timer)
    if st.button("Next Page"):
        current_page += 1
        log_pdf_action(student_id, 'pdf_page_turn', course_id, lecture_id, 
                      material_id, page=current_page, duration=time_on_page)
    
    # Log download
    if st.download_button("Download PDF"):
        log_download(student_id, 'pdf', course_id, lecture_id, material_id,
                    file_size=os.path.getsize(pdf_path))
    
    # Log zoom
    if zoom_changed:
        logger.log_action(student_id, 'student', 'pdf_zoom',
                         {'course_id': course_id, 'lecture_id': lecture_id,
                          'resource_id': material_id},
                         {'zoom_level': new_zoom})


# ============================================================================
# EXAMPLE 2: Quiz Page Integration
# File: app/pages/quizzes.py
# ============================================================================

from services.universal_logger import log_assessment

def take_quiz(quiz_id: str, course_id: str, lecture_id: str):
    """Quiz taking with intelligent tracking"""
    
    user_id = st.session_state.user['id']
    start_time = time.time()
    
    # Log quiz start
    log_assessment(user_id, 'quiz_start', course_id, lecture_id, quiz_id)
    
    # Display questions...
    
    if st.button("Submit Quiz"):
        duration = time.time() - start_time
        score = calculate_score(answers)
        
        # Log quiz submission with score
        log_assessment(user_id, 'quiz_submit', course_id, lecture_id, quiz_id,
                      score=score, duration=duration)
        
        st.success(f"Score: {score}%")


# ============================================================================
# EXAMPLE 3: Video Player Integration
# File: app/pages/lectures.py
# ============================================================================

from services.universal_logger import log_video_action

def show_video_player(lecture: dict):
    """Video player with intelligent tracking"""
    
    user_id = st.session_state.user['id']
    course_id = lecture['course_id']
    lecture_id = lecture['lecture_id']
    
    # Log video start
    if video_playing:
        log_video_action(user_id, 'video_start', course_id, lecture_id)
    
    # Track pauses
    if video_paused:
        log_video_action(user_id, 'video_pause', course_id, lecture_id,
                        video_time=current_time)
    
    # Track completion
    if video_ended:
        log_video_action(user_id, 'video_complete', course_id, lecture_id,
                        duration=video_duration)
    
    # Track seeks
    if seek_occurred:
        log_video_action(user_id, 'video_seek', course_id, lecture_id,
                        video_time=new_time)


# ============================================================================
# EXAMPLE 4: Navigation Tracking
# File: app/streamlit_app.py
# ============================================================================

from services.universal_logger import get_activity_logger

def track_navigation():
    """Track page views and navigation"""
    
    logger = get_activity_logger()
    user_id = st.session_state.user['id']
    user_role = st.session_state.user['role']
    
    # Track page view
    current_page = st.session_state.get('current_page', 'dashboard')
    
    logger.log_action(user_id, user_role, 'page_view',
                     {'page_name': current_page},
                     {'referrer': st.session_state.get('previous_page')})
    
    # Track tab/window focus
    st.components.v1.html("""
        <script>
            window.addEventListener('blur', function() {
                // Send blur event to Streamlit
                window.parent.postMessage({type: 'window_blur'}, '*');
            });
            
            window.addEventListener('focus', function() {
                window.parent.postMessage({type: 'window_focus'}, '*');
            });
            
            document.addEventListener('visibilitychange', function() {
                if (document.hidden) {
                    window.parent.postMessage({type: 'tab_switch'}, '*');
                }
            });
        </script>
    """, height=0)


# ============================================================================
# EXAMPLE 5: Teacher Activity Tracking
# File: app/pages/upload.py
# ============================================================================

from services.universal_logger import get_activity_logger

def upload_content():
    """Track teacher uploads"""
    
    logger = get_activity_logger()
    user_id = st.session_state.user['id']
    course_id = st.session_state.selected_course
    
    uploaded_file = st.file_uploader("Upload Lecture")
    
    if uploaded_file:
        # Log upload start
        logger.log_action(user_id, 'teacher', 'upload_start',
                         {'course_id': course_id},
                         {'file_type': uploaded_file.type,
                          'file_size': uploaded_file.size})
        
        # Process upload...
        save_file(uploaded_file)
        
        # Log upload complete
        logger.log_action(user_id, 'teacher', 'upload_complete',
                         {'course_id': course_id, 'lecture_id': new_lecture_id},
                         {'duration_seconds': upload_time})


# ============================================================================
# EXAMPLE 6: Analytics Dashboard
# File: app/pages/analytics.py
# ============================================================================

from services.universal_logger import get_activity_logger
from services.intelligent_scorer import get_intelligent_scorer

def show_student_engagement(student_id: str, lecture_id: str):
    """Display intelligent engagement score"""
    
    logger = get_activity_logger()
    scorer = get_intelligent_scorer()
    
    # Get all actions for this student/lecture
    actions = logger._get_recent_actions(student_id, limit=1000)
    lecture_actions = [a for a in actions 
                       if a['context'].get('lecture_id') == lecture_id]
    
    # Calculate intelligent engagement score
    result = scorer.predict_engagement_score(
        lecture_actions,
        {'lecture_id': lecture_id, 'user_role': 'student'}
    )
    
    # Display results
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Engagement Score", f"{result['engagement_score']}/100")
    
    with col2:
        st.metric("Level", result['level'])
    
    with col3:
        st.metric("Confidence", f"{result['confidence']*100:.0f}%")
    
    # Show explanation
    st.info(f"📝 {result['explanation']}")
    
    # Show activity summary
    st.subheader("Activity Details")
    st.write(f"Total Actions: {result['total_actions']}")
    st.write(f"Features Analyzed: {result['features_used']}")
    
    # Show breakdown
    with st.expander("Feature Breakdown"):
        features = scorer.extract_features_from_actions(lecture_actions, {})
        
        # Group by category
        st.write("**Temporal Patterns:**")
        st.write(f"- Avg time between actions: {features['avg_time_between_actions']:.0f}s")
        st.write(f"- Session duration: {features['total_session_duration']/60:.1f} min")
        st.write(f"- Actions per minute: {features['actions_per_minute']:.1f}")
        
        st.write("**Content Engagement:**")
        st.write(f"- PDF downloaded: {'Yes' if features['pdf_downloaded'] else 'No'}")
        st.write(f"- PDF viewed online: {'Yes' if features['pdf_viewed_online'] else 'No'}")
        st.write(f"- Video completions: {int(features['video_completions'])}")
        
        st.write("**Quality Metrics:**")
        st.write(f"- Action diversity: {int(features['action_type_diversity'])} types")
        st.write(f"- Tab switches: {int(features['tab_switches'])}")
        st.write(f"- Focus loss ratio: {features['focus_loss_ratio']:.1%}")


# ============================================================================
# EXAMPLE 7: Real-time Monitoring
# File: app/pages/monitor.py
# ============================================================================

def show_realtime_monitoring():
    """Show real-time engagement for all students"""
    
    logger = get_activity_logger()
    scorer = get_intelligent_scorer()
    
    st.title("📊 Real-Time Engagement Monitor")
    
    # Get list of active students
    active_students = get_active_students()  # Your function
    
    # Create table
    rows = []
    for student in active_students:
        actions = logger._get_recent_actions(student['id'], limit=100)
        recent_actions = [a for a in actions 
                         if datetime.now().timestamp() - a['unix_timestamp'] < 3600]
        
        if recent_actions:
            result = scorer.predict_engagement_score(recent_actions, {})
            
            rows.append({
                'Student': student['name'],
                'Score': result['engagement_score'],
                'Level': result['level'],
                'Actions (1h)': len(recent_actions),
                'Last Active': format_time(recent_actions[-1]['timestamp'])
            })
    
    # Display as dataframe
    df = pd.DataFrame(rows)
    
    # Color code by score
    def color_score(val):
        if val >= 80:
            return 'background-color: #d4edda'
        elif val >= 60:
            return 'background-color: #fff3cd'
        else:
            return 'background-color: #f8d7da'
    
    st.dataframe(df.style.applymap(color_score, subset=['Score']))
    
    # Alert for low engagement
    low_engagement = df[df['Score'] < 50]
    if not low_engagement.empty:
        st.warning(f"⚠️ {len(low_engagement)} student(s) with low engagement!")
        st.dataframe(low_engagement)


# ============================================================================
# USAGE SUMMARY
# ============================================================================

"""
INTEGRATION CHECKLIST:

1. Import loggers in your page:
   from services.universal_logger import get_activity_logger, log_*
   from services.intelligent_scorer import get_intelligent_scorer

2. Log actions at key points:
   - Page views: logger.log_action(..., 'page_view', ...)
   - Content access: log_pdf_action, log_video_action
   - Downloads: log_download
   - Assessments: log_assessment
   - Navigation: track tab switches, focus changes

3. Calculate scores:
   - Get actions: logger._get_recent_actions(user_id)
   - Score: scorer.predict_engagement_score(actions, context)
   - Display: Use result['engagement_score'], result['level'], etc.

4. Monitor:
   - Real-time dashboard for teachers
   - Alerts for low engagement
   - Trend analysis over time

5. Privacy:
   - Only log behavioral actions (no personal content)
   - Provide data export for users
   - Allow deletion requests
"""
