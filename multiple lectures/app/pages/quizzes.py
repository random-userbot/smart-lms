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
from services.universal_logger import log_assessment
from datetime import datetime
import uuid


def show_quiz_attempt(quiz, lecture_id, course_id):
    """Display quiz for student to attempt"""
    storage = get_storage()
    user = st.session_state.user
    quiz_id = quiz.get('quiz_id')
    
    # Check if student has already attempted this quiz
    if storage.has_attempted_quiz(user['user_id'], quiz_id):
        st.warning("⚠️ You have already attempted this quiz. Retries are not allowed.")
        
        # Show their previous attempt
        attempt = storage.get_student_quiz_attempt(user['user_id'], quiz_id)
        if attempt:
            st.markdown("### Your Previous Attempt:")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Score", f"{attempt.get('score', 0)}/{attempt.get('max_score', 0)}")
            with col2:
                st.metric("Percentage", f"{attempt.get('percentage', 0):.1f}%")
            with col3:
                percentage = attempt.get('percentage', 0)
                grade = "A" if percentage >= 80 else "B" if percentage >= 60 else "C" if percentage >= 40 else "D"
                st.metric("Grade", grade)
            
            st.caption(f"Submitted: {attempt.get('timestamp', 'Unknown')[:19]}")
        
        if st.button("← Back to Quizzes"):
            st.session_state.current_page = 'quizzes'
            st.rerun()
        
        return
    
    st.title(f"📝 {quiz['title']}")
    st.markdown(f"**Time Limit:** {quiz.get('time_limit', 30)} minutes")
    st.markdown(f"**Questions:** {len(quiz.get('questions', []))}")
    st.warning("⚠️ **Important:** You can only attempt this quiz ONCE. No retries are allowed!")
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
            # Log intelligent engagement
            log_assessment(user['user_id'], 'quiz_start', course_id, lecture_id, quiz_id)
            st.rerun()
        
        return
    
    # Quiz form
    with st.form("quiz_form"):
        answers = {}
        
        for i, question in enumerate(quiz.get('questions', [])):
            st.markdown(f"### Question {i+1}")
            st.markdown(question.get('question', ''))
            
            # Determine question type
            question_type = question.get('question_type', question.get('type', 'multiple_choice'))
            
            if question_type in ['mcq', 'multiple_choice']:
                options = question.get('options', [])
                if options:
                    # Parse options to get just the letters
                    option_keys = []
                    option_texts = {}
                    
                    for opt in options:
                        if isinstance(opt, str) and len(opt) > 0:
                            key = opt[0]  # Get 'A', 'B', 'C', or 'D'
                            option_keys.append(key)
                            option_texts[key] = opt
                    
                    answer = st.radio(
                        "Select your answer:",
                        options=option_keys,
                        format_func=lambda x: option_texts.get(x, x),
                        key=f"q_{i}"
                    )
                    answers[i] = answer
            
            elif question_type == 'true_false':
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
            total_questions = len(quiz.get('questions', []))
            
            for i, question in enumerate(quiz.get('questions', [])):
                student_answer = answers.get(i, '')
                correct_answer = question.get('correct_answer', '')
                
                # Normalize answers for comparison
                if student_answer and correct_answer:
                    if student_answer[0] == correct_answer[0]:
                        correct_count += 1
            
            score = correct_count
            max_score = total_questions
            percentage = (correct_count / total_questions) * 100 if total_questions > 0 else 0
            
            time_taken = (datetime.utcnow() - st.session_state.quiz_start_time).total_seconds()
            
            # Save attempt using new method (prevents retries)
            success = storage.submit_quiz_attempt(
                student_id=user['user_id'],
                course_id=course_id,
                quiz_id=quiz_id,
                answers=answers,
                score=percentage,
                max_score=100
            )
            
            if not success:
                st.error("Failed to submit quiz. You may have already attempted it.")
                return
            
            # Log intelligent engagement
            log_assessment(user['user_id'], 'quiz_submit', course_id, lecture_id, 
                         quiz_id, score=percentage, duration=time_taken)
            
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
    """Render a quiz card with Streamlit native components"""
    # Determine status
    if is_completed and latest_grade:
        percentage = latest_grade['percentage']
        if percentage >= 80:
            grade_emoji = "🟢"
            status_text = f"✅ {percentage:.0f}%"
        elif percentage >= 60:
            grade_emoji = "🟡"
            status_text = f"✅ {percentage:.0f}%"
        else:
            grade_emoji = "🟠"
            status_text = f"✅ {percentage:.0f}%"
    else:
        grade_emoji = "�"
        status_text = "New"
    
    with st.container():
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"### {grade_emoji} {quiz['title']}")
        with col2:
            st.markdown(f"**{status_text}**")
        
        st.caption(f"📚 Lecture: {lecture['title']}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Questions", len(quiz['questions']))
        with col2:
            st.metric("Time Limit", f"{quiz['time_limit']} min")
        with col3:
            if latest_grade:
                st.metric("Score", f"{latest_grade['score']}/{latest_grade['max_score']}")
        
        st.markdown("---")
    
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
            # Check both 'quiz' (singular) and 'quizzes' (plural) for compatibility
            quizzes = []
            if 'quiz' in lecture and lecture['quiz']:
                quizzes = [lecture['quiz']]
            elif 'quizzes' in lecture:
                quizzes = lecture['quizzes']
            
            for quiz in quizzes:
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
            # Check both 'quiz' (singular) and 'quizzes' (plural)
            quizzes = []
            if 'quiz' in lecture and lecture['quiz']:
                quizzes = [lecture['quiz']]
            elif 'quizzes' in lecture:
                quizzes = lecture['quizzes']
            
            for quiz in quizzes:
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
