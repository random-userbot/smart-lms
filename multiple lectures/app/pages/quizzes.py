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
    
    if st.button("🏠 Back to Quizzes"):
        del st.session_state.quiz_result
        st.session_state.current_page = 'quizzes'
        st.rerun()


def show_available_quizzes():
    """Display list of available quizzes"""
    st.title("📝 Available Quizzes")
    
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
    completed_quizzes = {g['assessment_id'] for g in grades.get('quizzes', [])}
    
    # Display quizzes by course
    for course_id, course in enrolled_courses.items():
        st.subheader(f"📚 {course['name']}")
        
        # Get lectures for this course
        lectures = storage.get_course_lectures(course_id)
        
        has_quizzes = False
        for lecture in lectures:
            if lecture.get('quizzes'):
                has_quizzes = True
                
                for quiz in lecture['quizzes']:
                    quiz_id = quiz['quiz_id']
                    is_completed = quiz_id in completed_quizzes
                    
                    with st.expander(
                        f"{'✅' if is_completed else '📝'} {quiz['title']} - {lecture['title']}",
                        expanded=not is_completed
                    ):
                        st.markdown(f"**Lecture:** {lecture['title']}")
                        st.markdown(f"**Questions:** {len(quiz['questions'])}")
                        st.markdown(f"**Time Limit:** {quiz['time_limit']} minutes")
                        
                        if is_completed:
                            # Show previous score
                            quiz_grades = [g for g in grades['quizzes'] if g['assessment_id'] == quiz_id]
                            if quiz_grades:
                                latest_grade = quiz_grades[-1]
                                st.success(f"✅ Completed | Score: {latest_grade['score']}/{latest_grade['max_score']} ({latest_grade['percentage']:.1f}%)")
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button("📊 View Details", key=f"view_{quiz_id}"):
                                        st.info("Detailed results view coming soon!")
                                with col2:
                                    if st.button("🔄 Retake Quiz", key=f"retake_{quiz_id}"):
                                        st.session_state.selected_quiz = quiz
                                        st.session_state.selected_lecture_id = lecture['lecture_id']
                                        st.session_state.selected_course_id = course_id
                                        st.session_state.current_page = 'take_quiz'
                                        st.rerun()
                        else:
                            if st.button("▶️ Start Quiz", key=f"start_{quiz_id}", use_container_width=True):
                                st.session_state.selected_quiz = quiz
                                st.session_state.selected_lecture_id = lecture['lecture_id']
                                st.session_state.selected_course_id = course_id
                                st.session_state.current_page = 'take_quiz'
                                st.rerun()
        
        if not has_quizzes:
            st.info("📝 No quizzes available for this course yet.")
        
        st.markdown("---")


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
