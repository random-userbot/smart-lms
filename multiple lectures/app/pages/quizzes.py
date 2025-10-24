"""
Smart LMS - Quizzes Page
Students can take quizzes and view results
"""

import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.auth import get_auth
from services.storage import get_storage
from datetime import datetime
import uuid


def show_quiz_attempt(quiz, lecture_id, course_id):
    """Display quiz for student to attempt"""
    st.title(f"📝 {quiz['title']}")
    st.markdown(f"**Time Limit:** {quiz['time_limit']} minutes")
    st.markdown(f"**Questions:** {len(quiz['questions'])}")
    st.markdown("---")
    
    # Initialize quiz state
    if 'quiz_started' not in st.session_state:
        st.session_state.quiz_started = False
        st.session_state.quiz_start_time = None
        st.session_state.quiz_answers = {}
    
    if not st.session_state.quiz_started:
        st.info("📋 Read all questions carefully before starting. The timer will begin once you click 'Start Quiz'.")
        
        if st.button("▶️ Start Quiz", use_container_width=True):
            st.session_state.quiz_started = True
            st.session_state.quiz_start_time = datetime.utcnow()
            st.rerun()
        
        return
    
    # Quiz form
    with st.form("quiz_form"):
        answers = {}
        
        for i, question in enumerate(quiz['questions']):
            st.markdown(f"### Question {i+1}")
            st.markdown(question['question'])
            
            if question['type'] == 'mcq':
                options = question['options']
                answer = st.radio(
                    "Select your answer:",
                    options=['A', 'B', 'C', 'D'],
                    format_func=lambda x: f"{x}. {options[x]}",
                    key=f"q_{i}"
                )
                answers[i] = answer
            
            elif question['type'] == 'true_false':
                answer = st.radio(
                    "Select your answer:",
                    options=['True', 'False'],
                    key=f"q_{i}"
                )
                answers[i] = answer
            
            st.markdown("---")
        
        submit = st.form_submit_button("✅ Submit Quiz")
        
        if submit:
            # Calculate score
            correct_count = 0
            total_questions = len(quiz['questions'])
            
            for i, question in enumerate(quiz['questions']):
                if answers.get(i) == question['correct_answer']:
                    correct_count += 1
            
            score = correct_count
            max_score = total_questions
            percentage = (correct_count / total_questions) * 100
            
            # Save grade
            storage = get_storage()
            user = st.session_state.user
            
            storage.save_grade(
                student_id=user['user_id'],
                course_id=course_id,
                assessment_type='quiz',
                assessment_id=quiz['quiz_id'],
                score=score,
                max_score=max_score,
                lecture_id=lecture_id,
                answers=answers,
                time_taken=(datetime.utcnow() - st.session_state.quiz_start_time).total_seconds()
            )
            
            # Show results
            st.session_state.quiz_result = {
                'score': score,
                'max_score': max_score,
                'percentage': percentage,
                'correct_count': correct_count,
                'total_questions': total_questions
            }
            
            # Clear quiz state
            st.session_state.quiz_started = False
            del st.session_state.quiz_start_time
            
            st.rerun()


def show_quiz_result():
    """Display quiz results"""
    if 'quiz_result' not in st.session_state:
        return
    
    result = st.session_state.quiz_result
    
    st.success("✅ Quiz Submitted Successfully!")
    
    # Display score
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Score", f"{result['score']}/{result['max_score']}")
    
    with col2:
        st.metric("Percentage", f"{result['percentage']:.1f}%")
    
    with col3:
        if result['percentage'] >= 80:
            grade = "A"
            color = "🟢"
        elif result['percentage'] >= 60:
            grade = "B"
            color = "🟡"
        elif result['percentage'] >= 40:
            grade = "C"
            color = "🟠"
        else:
            grade = "F"
            color = "🔴"
        
        st.metric("Grade", f"{color} {grade}")
    
    st.markdown("---")
    
    # Performance message
    if result['percentage'] >= 80:
        st.success("🎉 Excellent work! You've mastered this material.")
    elif result['percentage'] >= 60:
        st.info("👍 Good job! Review the material to improve further.")
    else:
        st.warning("📚 Keep practicing! Review the lecture and try again.")
    
    if st.button("🏠 Back to Quizzes", key="back_to_quizzes_result"):
        del st.session_state.quiz_result
        st.session_state.current_page = 'quizzes'
        st.rerun()


def render_quiz_card(quiz, lecture, course_id, is_completed, latest_grade=None):
    """Render a quiz card with visual styling"""
    # Determine status and color
    if is_completed and latest_grade:
        percentage = latest_grade['percentage']
        if percentage >= 80:
            status_color = "#28a745"  # Green
            status_text = f"✅ {percentage:.0f}%"
            grade_emoji = "🟢"
        elif percentage >= 60:
            status_color = "#ffc107"  # Yellow
            status_text = f"✅ {percentage:.0f}%"
            grade_emoji = "🟡"
        else:
            status_color = "#fd7e14"  # Orange
            status_text = f"✅ {percentage:.0f}%"
            grade_emoji = "🟠"
    else:
        status_color = "#007bff"  # Blue
        status_text = "📝 New"
        grade_emoji = "📝"
    
    card_html = f"""
    <div style="
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    ">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
            <h3 style="color: white; margin: 0; font-size: 1.3em;">
                {grade_emoji} {quiz['title']}
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
        
        <p style="color: rgba(255,255,255,0.95); margin: 10px 0; font-size: 0.9em;">
            <strong>📚 Lecture:</strong> {lecture['title']}
        </p>
        
        <div style="display: flex; gap: 20px; margin-top: 15px; flex-wrap: wrap;">
            <div style="color: white;">
                <span style="font-size: 1.2em;">❓</span>
                <span style="margin-left: 5px;">{len(quiz['questions'])} Questions</span>
            </div>
            <div style="color: white;">
                <span style="font-size: 1.2em;">⏱️</span>
                <span style="margin-left: 5px;">{quiz['time_limit']} min</span>
            </div>
            {f'''<div style="color: white;">
                <span style="font-size: 1.2em;">📊</span>
                <span style="margin-left: 5px;">Score: {latest_grade['score']}/{latest_grade['max_score']}</span>
            </div>''' if latest_grade else ''}
        </div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)
    
    # Action buttons
    if is_completed:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Retake Quiz", key=f"retake_{quiz['quiz_id']}", type="primary", use_container_width=True):
                st.session_state.selected_quiz = quiz
                st.session_state.selected_lecture_id = lecture['lecture_id']
                st.session_state.selected_course_id = course_id
                st.session_state.current_page = 'take_quiz'
                st.rerun()
        with col2:
            if st.button("📊 View Details", key=f"view_{quiz['quiz_id']}", use_container_width=True):
                st.info("📈 Detailed results view coming soon!")
    else:
        if st.button("▶️ Start Quiz", key=f"start_{quiz['quiz_id']}", type="primary", use_container_width=True):
            st.session_state.selected_quiz = quiz
            st.session_state.selected_lecture_id = lecture['lecture_id']
            st.session_state.selected_course_id = course_id
            st.session_state.current_page = 'take_quiz'
            st.rerun()


def show_available_quizzes():
    """Display list of available quizzes with card-based UI"""
    st.title("📝 My Quizzes")
    
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
    
    # Get student's grades
    grades = storage.get_student_grades(user['user_id'])
    completed_quizzes = {g['assessment_id']: g for g in grades.get('quizzes', [])}
    
    # Calculate statistics
    total_quizzes = 0
    completed_count = 0
    total_score = 0
    
    for course_id, course in enrolled_courses.items():
        lectures = storage.get_course_lectures(course_id)
        for lecture in lectures:
            for quiz in lecture.get('quizzes', []):
                total_quizzes += 1
                if quiz['quiz_id'] in completed_quizzes:
                    completed_count += 1
                    total_score += completed_quizzes[quiz['quiz_id']]['percentage']
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📝 Total Quizzes", total_quizzes)
    with col2:
        st.metric("✅ Completed", completed_count)
    with col3:
        st.metric("📋 Pending", total_quizzes - completed_count)
    with col4:
        avg_score = total_score / completed_count if completed_count > 0 else 0
        st.metric("📊 Avg Score", f"{avg_score:.0f}%")
    
    st.markdown("---")
    
    # Search and filter
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("� Search quizzes", placeholder="Search by title or lecture...", key="quiz_search")
    with col2:
        filter_option = st.selectbox("Filter", ["All", "Completed", "Pending"], key="quiz_filter")
    
    st.markdown("---")
    
    # Display quizzes by course
    for course_id, course in enrolled_courses.items():
        
        # Get lectures for this course
        lectures = storage.get_course_lectures(course_id)
        
        course_quizzes = []
        for lecture in lectures:
            for quiz in lecture.get('quizzes', []):
                quiz_id = quiz['quiz_id']
                is_completed = quiz_id in completed_quizzes
                
                # Apply filters
                if filter_option == "Completed" and not is_completed:
                    continue
                if filter_option == "Pending" and is_completed:
                    continue
                
                # Apply search
                if search_query:
                    if search_query.lower() not in quiz['title'].lower() and \
                       search_query.lower() not in lecture['title'].lower():
                        continue
                
                course_quizzes.append((quiz, lecture, is_completed))
        
        if course_quizzes:
            st.subheader(f"📚 {course['name']}")
            
            for quiz, lecture, is_completed in course_quizzes:
                latest_grade = completed_quizzes.get(quiz['quiz_id'])
                render_quiz_card(quiz, lecture, course_id, is_completed, latest_grade)
            
            st.markdown("---")
    
    if total_quizzes == 0:
        st.info("📝 No quizzes available yet. Check back later!")


def main():
    """Main quizzes page"""
    # Check authentication
    auth = get_auth()
    auth.require_role('student')
    
    # Check if showing quiz result
    if 'quiz_result' in st.session_state:
        show_quiz_result()
        return
    
    # Check if taking a quiz
    if st.session_state.get('current_page') == 'take_quiz' and 'selected_quiz' in st.session_state:
        quiz = st.session_state.selected_quiz
        lecture_id = st.session_state.selected_lecture_id
        course_id = st.session_state.selected_course_id
        
        # Back button
        if st.button("← Back to Quizzes"):
            st.session_state.current_page = 'quizzes'
            if 'selected_quiz' in st.session_state:
                del st.session_state.selected_quiz
            if 'quiz_started' in st.session_state:
                del st.session_state.quiz_started
            st.rerun()
        
        show_quiz_attempt(quiz, lecture_id, course_id)
    else:
        # Show available quizzes
        show_available_quizzes()


if __name__ == "__main__":
    main()
