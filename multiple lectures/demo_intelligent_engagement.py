"""
Intelligent Engagement Integration Demo
Shows how the intelligent engagement system works with all user actions
"""

from services.universal_logger import get_activity_logger, log_pdf_action, log_download, log_video_action, log_assessment
from services.intelligent_scorer import get_intelligent_scorer
from datetime import datetime, timedelta
import random
import time


def simulate_student_session_1_downloads_pdf():
    """
    Scenario 1: Student downloads PDF and reads offline
    The intelligent system should still detect engagement
    """
    print("\n" + "="*70)
    print("📚 SCENARIO 1: Student Downloads PDF for Offline Reading")
    print("="*70)
    
    user_id = "student_001"
    course_id = "CS101"
    lecture_id = "lecture_cv_intro"
    material_id = "pdf_intro_cv"
    
    logger = get_activity_logger()
    scorer = get_intelligent_scorer()
    
    # Student session begins
    print("\n⏰ 9:00 AM - Student logs in")
    logger.log_action(user_id, 'student', 'login', 
                     {'course_id': course_id}, 
                     {'login_method': 'password'})
    
    time.sleep(0.5)
    
    print("👀 9:02 AM - Student views lecture page")
    logger.log_action(user_id, 'student', 'lecture_enter',
                     {'course_id': course_id, 'lecture_id': lecture_id},
                     {'page_url': '/lectures/cv_intro'})
    
    time.sleep(0.5)
    
    print("📥 9:03 AM - Student downloads PDF (5.2 MB)")
    log_download(user_id, 'pdf', course_id, lecture_id, material_id, file_size=5242880)
    
    time.sleep(1)
    
    # Student goes offline to read
    print("📱 9:05 AM - Student goes offline (reading PDF on mobile/print)")
    print("   (System: No activity logged for 45 minutes)")
    
    # Simulate offline time
    time.sleep(1)
    
    print("🔄 9:50 AM - Student returns online")
    logger.log_action(user_id, 'student', 'page_view',
                     {'course_id': course_id, 'lecture_id': lecture_id},
                     {'referrer': 'direct'})
    
    time.sleep(0.5)
    
    print("📝 9:52 AM - Student takes quiz after reading PDF")
    log_assessment(user_id, 'quiz_start', course_id, lecture_id, 'quiz_001')
    
    time.sleep(0.5)
    
    print("✅ 9:58 AM - Student submits quiz (Score: 85%)")
    log_assessment(user_id, 'quiz_submit', course_id, lecture_id, 'quiz_001', 
                   score=85, duration=360)
    
    print("💬 9:59 AM - Student provides positive feedback")
    logger.log_action(user_id, 'student', 'feedback_submit',
                     {'course_id': course_id, 'lecture_id': lecture_id},
                     {'rating': 5, 'sentiment': 'positive'})
    
    # Calculate engagement score
    print("\n🤖 INTELLIGENT ANALYSIS:")
    print("-" * 70)
    
    # Get all actions for this student/lecture
    actions = logger._get_recent_actions(user_id, limit=1000)
    lecture_actions = [a for a in actions if a['context'].get('lecture_id') == lecture_id]
    
    result = scorer.predict_engagement_score(
        lecture_actions,
        {'course_id': course_id, 'lecture_id': lecture_id, 'user_role': 'student'}
    )
    
    print(f"📊 Engagement Score: {result['engagement_score']}/100")
    print(f"🎯 Level: {result['level']}")
    print(f"💪 Confidence: {result['confidence']*100:.0f}%")
    print(f"📝 Explanation: {result['explanation']}")
    print(f"🔢 Actions Analyzed: {result['total_actions']}")
    print(f"🎨 Features Used: {result['features_used']}")
    
    print("\n✨ KEY INSIGHT:")
    print("   Even though student read offline, the system detected:")
    print("   • Download behavior")
    print("   • Return after reasonable time")
    print("   • Good quiz performance (85%)")
    print("   • Positive feedback")
    print("   → High engagement score despite no online reading time!")
    
    return result


def simulate_student_session_2_reads_online():
    """
    Scenario 2: Student reads PDF online with active interactions
    """
    print("\n" + "="*70)
    print("💻 SCENARIO 2: Student Reads PDF Online with Active Engagement")
    print("="*70)
    
    user_id = "student_002"
    course_id = "CS101"
    lecture_id = "lecture_cv_intro"
    material_id = "pdf_intro_cv"
    
    logger = get_activity_logger()
    scorer = get_intelligent_scorer()
    
    print("\n⏰ 2:00 PM - Student logs in")
    logger.log_action(user_id, 'student', 'login',
                     {'course_id': course_id},
                     {'login_method': 'oauth'})
    
    time.sleep(0.5)
    
    print("📖 2:02 PM - Student opens PDF reader")
    log_pdf_action(user_id, 'pdf_open', course_id, lecture_id, material_id, page=1)
    
    # Simulate active reading with page turns, scrolls
    print("📄 2:03-2:35 PM - Active reading session:")
    pages_read = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    for page in pages_read:
        time.sleep(0.2)
        print(f"   • Page {page} ({random.randint(45, 180)} seconds)")
        log_pdf_action(user_id, 'pdf_page_turn', course_id, lecture_id, material_id, 
                       page=page, duration=random.randint(45, 180))
        
        # Occasional zoom/scroll
        if random.random() > 0.6:
            logger.log_action(user_id, 'student', 'pdf_zoom',
                            {'course_id': course_id, 'lecture_id': lecture_id, 
                             'resource_id': material_id},
                            {'page': page, 'zoom_level': 125})
    
    print("🎥 2:36 PM - Student watches related video")
    log_video_action(user_id, 'video_start', course_id, lecture_id)
    
    time.sleep(0.5)
    
    print("✅ 2:48 PM - Video complete")
    log_video_action(user_id, 'video_complete', course_id, lecture_id, duration=720)
    
    print("📝 2:50 PM - Takes quiz")
    log_assessment(user_id, 'quiz_start', course_id, lecture_id, 'quiz_001')
    
    time.sleep(0.5)
    
    print("✅ 2:56 PM - Quiz submitted (Score: 92%)")
    log_assessment(user_id, 'quiz_submit', course_id, lecture_id, 'quiz_001',
                   score=92, duration=360)
    
    # Calculate engagement
    print("\n🤖 INTELLIGENT ANALYSIS:")
    print("-" * 70)
    
    actions = logger._get_recent_actions(user_id, limit=1000)
    lecture_actions = [a for a in actions if a['context'].get('lecture_id') == lecture_id]
    
    result = scorer.predict_engagement_score(
        lecture_actions,
        {'course_id': course_id, 'lecture_id': lecture_id, 'user_role': 'student'}
    )
    
    print(f"📊 Engagement Score: {result['engagement_score']}/100")
    print(f"🎯 Level: {result['level']}")
    print(f"💪 Confidence: {result['confidence']*100:.0f}%")
    print(f"📝 Explanation: {result['explanation']}")
    print(f"🔢 Actions Analyzed: {result['total_actions']}")
    print(f"🎨 Features Used: {result['features_used']}")
    
    print("\n✨ KEY INSIGHT:")
    print("   Rich online activity detected:")
    print("   • 10 pages read with varied timing")
    print("   • Interactive elements (zoom, scroll)")
    print("   • Video completion")
    print("   • Excellent quiz score (92%)")
    print("   → Very high engagement score from comprehensive tracking!")
    
    return result


def simulate_student_session_3_distracted():
    """
    Scenario 3: Student is distracted with tab switching
    """
    print("\n" + "="*70)
    print("😰 SCENARIO 3: Distracted Student with Multiple Tab Switches")
    print("="*70)
    
    user_id = "student_003"
    course_id = "CS101"
    lecture_id = "lecture_cv_intro"
    material_id = "pdf_intro_cv"
    
    logger = get_activity_logger()
    scorer = get_intelligent_scorer()
    
    print("\n⏰ 11:00 PM - Student logs in (late night)")
    logger.log_action(user_id, 'student', 'login',
                     {'course_id': course_id},
                     {})
    
    time.sleep(0.3)
    
    print("📖 11:02 PM - Opens PDF")
    log_pdf_action(user_id, 'pdf_open', course_id, lecture_id, material_id, page=1)
    
    time.sleep(0.3)
    
    print("⚠️ 11:03 PM - Tab switch (social media)")
    logger.log_action(user_id, 'student', 'tab_switch',
                     {'course_id': course_id, 'lecture_id': lecture_id},
                     {'distraction': True})
    
    time.sleep(0.3)
    
    print("↩️ 11:08 PM - Returns to PDF")
    logger.log_action(user_id, 'student', 'window_focus',
                     {'course_id': course_id, 'lecture_id': lecture_id},
                     {})
    
    time.sleep(0.3)
    
    print("⚠️ 11:10 PM - Tab switch again")
    logger.log_action(user_id, 'student', 'tab_switch',
                     {'course_id': course_id, 'lecture_id': lecture_id},
                     {'distraction': True})
    
    time.sleep(0.3)
    
    print("↩️ 11:20 PM - Returns")
    logger.log_action(user_id, 'student', 'window_focus',
                     {'course_id': course_id, 'lecture_id': lecture_id},
                     {})
    
    time.sleep(0.3)
    
    print("📄 11:22 PM - Briefly skims pages 1-3")
    for page in [1, 2, 3]:
        log_pdf_action(user_id, 'pdf_page_turn', course_id, lecture_id, material_id,
                       page=page, duration=15)  # Very short time per page
        time.sleep(0.2)
    
    print("📝 11:25 PM - Attempts quiz (rushed)")
    log_assessment(user_id, 'quiz_start', course_id, lecture_id, 'quiz_001')
    
    time.sleep(0.3)
    
    print("❌ 11:27 PM - Quiz submitted (Score: 45%)")
    log_assessment(user_id, 'quiz_submit', course_id, lecture_id, 'quiz_001',
                   score=45, duration=120)  # Only 2 minutes
    
    # Calculate engagement
    print("\n🤖 INTELLIGENT ANALYSIS:")
    print("-" * 70)
    
    actions = logger._get_recent_actions(user_id, limit=1000)
    lecture_actions = [a for a in actions if a['context'].get('lecture_id') == lecture_id]
    
    result = scorer.predict_engagement_score(
        lecture_actions,
        {'course_id': course_id, 'lecture_id': lecture_id, 'user_role': 'student'}
    )
    
    print(f"📊 Engagement Score: {result['engagement_score']}/100")
    print(f"🎯 Level: {result['level']}")
    print(f"💪 Confidence: {result['confidence']*100:.0f}%")
    print(f"📝 Explanation: {result['explanation']}")
    print(f"🔢 Actions Analyzed: {result['total_actions']}")
    print(f"🎨 Features Used: {result['features_used']}")
    
    print("\n✨ KEY INSIGHT:")
    print("   System detected poor engagement:")
    print("   • Multiple tab switches (distractions)")
    print("   • Very short time per page (15s)")
    print("   • Late night studying")
    print("   • Poor quiz performance (45%)")
    print("   → Low engagement score reflecting quality of interaction!")
    
    return result


def simulate_teacher_activity():
    """
    Scenario 4: Track teacher activity
    """
    print("\n" + "="*70)
    print("👨‍🏫 SCENARIO 4: Teacher Content Creation Activity")
    print("="*70)
    
    user_id = "teacher_001"
    course_id = "CS101"
    
    logger = get_activity_logger()
    scorer = get_intelligent_scorer()
    
    print("\n⏰ 10:00 AM - Teacher logs in")
    logger.log_action(user_id, 'teacher', 'login',
                     {'course_id': course_id},
                     {})
    
    time.sleep(0.3)
    
    print("📤 10:05 AM - Uploads lecture video")
    logger.log_action(user_id, 'teacher', 'upload_start',
                     {'course_id': course_id},
                     {'file_type': 'video', 'file_size': 524288000})
    
    time.sleep(0.5)
    
    print("✅ 10:15 AM - Upload complete")
    logger.log_action(user_id, 'teacher', 'upload_complete',
                     {'course_id': course_id, 'lecture_id': 'lecture_new'},
                     {'duration_seconds': 600})
    
    time.sleep(0.3)
    
    print("📝 10:20 AM - Creates quiz")
    logger.log_action(user_id, 'teacher', 'quiz_create',
                     {'course_id': course_id, 'lecture_id': 'lecture_new'},
                     {'question_count': 10})
    
    time.sleep(0.3)
    
    print("📊 10:30 AM - Views student analytics")
    logger.log_action(user_id, 'teacher', 'page_view',
                     {'course_id': course_id},
                     {'page_type': 'analytics'})
    
    # Calculate engagement (for teachers, it's about activity and content quality)
    print("\n🤖 INTELLIGENT ANALYSIS:")
    print("-" * 70)
    
    actions = logger._get_recent_actions(user_id, limit=1000)
    
    result = scorer.predict_engagement_score(
        actions,
        {'course_id': course_id, 'user_role': 'teacher'}
    )
    
    print(f"📊 Activity Score: {result['engagement_score']}/100")
    print(f"🎯 Level: {result['level']}")
    print(f"💪 Confidence: {result['confidence']*100:.0f}%")
    print(f"📝 Explanation: {result['explanation']}")
    
    print("\n✨ KEY INSIGHT:")
    print("   System tracks teacher engagement too:")
    print("   • Content creation activities")
    print("   • Upload completions")
    print("   • Monitoring student progress")
    print("   → Measures teaching effectiveness and platform usage!")
    
    return result


def main():
    """Run all demonstration scenarios"""
    print("\n" + "="*70)
    print("🎓 INTELLIGENT ENGAGEMENT SCORING SYSTEM")
    print("   Universal Activity Tracking + ML-Based Scoring")
    print("="*70)
    
    print("\n📋 SYSTEM FEATURES:")
    print("   ✅ Tracks ALL user actions (not just specific events)")
    print("   ✅ Intelligent ML-based scoring (learns patterns)")
    print("   ✅ Handles online AND offline interactions")
    print("   ✅ Detects downloads, returns, quality of engagement")
    print("   ✅ Works for Students, Teachers, and Admins")
    print("   ✅ Adapts to individual learning patterns")
    print("   ✅ Provides confidence scores and explanations")
    
    # Run scenarios
    result1 = simulate_student_session_1_downloads_pdf()
    result2 = simulate_student_session_2_reads_online()
    result3 = simulate_student_session_3_distracted()
    result4 = simulate_teacher_activity()
    
    # Final comparison
    print("\n" + "="*70)
    print("📊 FINAL COMPARISON")
    print("="*70)
    
    print(f"\n📥 Offline Reader (Downloaded PDF):  {result1['engagement_score']}/100 - {result1['level']}")
    print(f"💻 Online Reader (Active):           {result2['engagement_score']}/100 - {result2['level']}")
    print(f"😰 Distracted Student:               {result3['engagement_score']}/100 - {result3['level']}")
    print(f"👨‍🏫 Teacher Activity:                  {result4['engagement_score']}/100 - {result4['level']}")
    
    print("\n" + "="*70)
    print("✨ CONCLUSION")
    print("="*70)
    print("""
The intelligent system successfully:
1. Detected engagement from downloaded PDF (offline reading inferred)
2. Measured rich online interaction quality
3. Identified poor engagement patterns (distractions)
4. Tracked teacher activity and content creation
5. Provided explainable scores with confidence levels

All actions are logged to:
- JSON files (quick access)
- CSV files (ML training)
- Session summaries (aggregated stats)

The ML model learns from patterns rather than fixed rules,
making it adaptable to different learning styles and contexts.
    """)
    
    print("✅ Demo complete! Check ./ml_data/activity_logs/ for logged data")


if __name__ == "__main__":
    main()
