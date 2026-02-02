"""
Smart LMS - AI Quiz Generator Page
Interactive quiz generation interface for teachers
Teacher reviews and approves each AI-generated question
"""

import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.auth import get_auth
from services.storage import get_storage
from services.ai_quiz_generator import get_ai_quiz_generator
from services.activity_tracker import get_activity_tracker
from datetime import datetime
import json


def render_course_card_quiz(course_id: str, course: dict, on_select):
    """Render course card for quiz generation"""
    enrolled_count = len(course.get('enrolled_students', []))
    lectures_count = len(course.get('lectures', []))
    
    gradients = [
        "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
        "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
        "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
    ]
    gradient = gradients[hash(course_id) % len(gradients)]
    
    st.markdown(f"""
    <div style="
        background: {gradient};
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    ">
        <h3 style="color: white; margin: 0 0 12px 0;">📚 {course.get('name', 'Untitled')}</h3>
        <p style="color: #f5f5f5; margin: 8px 0;">
            {course.get('description', '')[:100]}...
        </p>
        <div style="display: flex; justify-content: space-between; margin-top: 15px;">
            <span style="color: white;">📹 {lectures_count} Lectures</span>
            <span style="color: white;">👥 {enrolled_count} Students</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button(f"📝 Generate Quiz", key=f"quiz_course_{course_id}", type="primary", use_container_width=True):
        on_select(course_id)


def render_lecture_card(lecture_id: str, lecture: dict, on_select):
    """Render lecture card for selection"""
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    ">
        <h4 style="color: white; margin: 0;">📹 {lecture.get('title', 'Untitled Lecture')}</h4>
        <p style="color: rgba(255,255,255,0.9); margin: 8px 0; font-size: 14px;">
            Duration: {lecture.get('duration', 'Unknown')}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button(f"Select Lecture", key=f"select_lec_{lecture_id}", use_container_width=True):
        on_select(lecture_id)


def show_question_preview(question_data: dict, question_number: int):
    """Display generated question for teacher review"""
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 100%);
        border-radius: 12px;
        padding: 25px;
        margin: 20px 0;
        border-left: 5px solid #00acc1;
    ">
        <h3 style="color: #00695c; margin: 0 0 15px 0;">Question #{question_number}</h3>
        <p style="font-size: 18px; color: #004d40; font-weight: 500; margin: 15px 0;">
            {question_data.get('question', '')}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display options
    options = question_data.get('options', [])
    correct = question_data.get('correct_answer', '')
    
    st.markdown("**Options:**")
    for option in options:
        # Highlight correct answer
        is_correct = option.strip()[0] == correct
        style = "background-color: #c8e6c9; padding: 10px; border-radius: 8px; margin: 5px 0;" if is_correct else "padding: 10px;"
        
        st.markdown(f"""
        <div style="{style}">
            {option} {"✅" if is_correct else ""}
        </div>
        """, unsafe_allow_html=True)
    
    # Explanation
    if question_data.get('explanation'):
        with st.expander("💡 Explanation"):
            st.info(question_data['explanation'])


def show_ai_quiz_generator():
    """Main AI quiz generator page"""
    st.title("🤖 AI Quiz Generator")
    st.markdown("Generate intelligent quizzes with AI - review and approve each question")
    st.markdown("---")
    
    auth = get_auth()
    if not auth.is_authenticated():
        st.warning("Please log in to generate quizzes.")
        return
    
    user = st.session_state.user
    if user['role'] != 'teacher':
        st.error("🚫 This feature is only available to teachers.")
        return
    
    storage = get_storage()
    ai_generator = get_ai_quiz_generator()
    tracker = get_activity_tracker()
    
    # Initialize session state
    if 'quiz_gen_step' not in st.session_state:
        st.session_state.quiz_gen_step = 'select_course'
    if 'quiz_gen_questions' not in st.session_state:
        st.session_state.quiz_gen_questions = []
    if 'current_question_data' not in st.session_state:
        st.session_state.current_question_data = None
    
    # Step 1: Select Course
    if st.session_state.quiz_gen_step == 'select_course':
        show_course_selection(user, storage)
    
    # Step 2: Select Lecture
    elif st.session_state.quiz_gen_step == 'select_lecture':
        show_lecture_selection(user, storage)
    
    # Step 3: Configure Quiz
    elif st.session_state.quiz_gen_step == 'configure':
        show_quiz_configuration(user, storage)
    
    # Step 4: Generate Questions Interactively
    elif st.session_state.quiz_gen_step == 'generate':
        show_interactive_generation(user, storage, ai_generator, tracker)
    
    # Step 5: Review and Save
    elif st.session_state.quiz_gen_step == 'review':
        show_quiz_review(user, storage, tracker)


def show_course_selection(user, storage):
    """Step 1: Select course"""
    st.markdown("## 📚 Step 1: Select Course")
    
    all_courses = storage.get_all_courses()
    teacher_courses = {cid: c for cid, c in all_courses.items() 
                      if c.get('teacher_id') == user['user_id']}
    
    if not teacher_courses:
        st.info("Create a course first to generate quizzes.")
        return
    
    def select_course(course_id):
        st.session_state.quiz_gen_course = course_id
        st.session_state.quiz_gen_step = 'select_lecture'
        st.rerun()
    
    cols = st.columns(2)
    for idx, (course_id, course) in enumerate(teacher_courses.items()):
        with cols[idx % 2]:
            render_course_card_quiz(course_id, course, select_course)


def show_lecture_selection(user, storage):
    """Step 2: Select lecture"""
    st.markdown("## 📹 Step 2: Select Lecture")
    
    if st.button("← Back to Courses"):
        st.session_state.quiz_gen_step = 'select_course'
        st.rerun()
    
    course_id = st.session_state.get('quiz_gen_course')
    course = storage.get_course(course_id)
    
    if not course:
        st.error("Course not found")
        return
    
    st.markdown(f"**Course:** {course.get('name')}")
    st.markdown("---")
    
    lectures = course.get('lectures', [])
    
    if not lectures:
        st.info("No lectures available. Upload lectures first.")
        return
    
    def select_lecture(lecture_id):
        st.session_state.quiz_gen_lecture = lecture_id
        st.session_state.quiz_gen_step = 'configure'
        st.rerun()
    
    cols = st.columns(2)
    for idx, lecture in enumerate(lectures):
        with cols[idx % 2]:
            render_lecture_card(lecture.get('lecture_id'), lecture, select_lecture)


def show_quiz_configuration(user, storage):
    """Step 3: Configure quiz settings"""
    st.markdown("## ⚙️ Step 3: Quiz Configuration")
    
    if st.button("← Back to Lectures"):
        st.session_state.quiz_gen_step = 'select_lecture'
        st.rerun()
    
    course_id = st.session_state.get('quiz_gen_course')
    lecture_id = st.session_state.get('quiz_gen_lecture')
    
    course = storage.get_course(course_id)
    lecture = next((l for l in course.get('lectures', []) if l.get('lecture_id') == lecture_id), None)
    
    if not lecture:
        st.error("Lecture not found")
        return
    
    st.markdown(f"**Course:** {course.get('name')}")
    st.markdown(f"**Lecture:** {lecture.get('title')}")
    st.markdown("---")
    
    with st.form("quiz_config_form"):
        quiz_title = st.text_input("Quiz Title *", value=f"Quiz: {lecture.get('title')}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            num_questions = st.number_input("Number of Questions", min_value=1, max_value=20, value=5)
        with col2:
            difficulty = st.selectbox("Difficulty", ["easy", "medium", "hard"], index=1)
        with col3:
            time_limit = st.number_input("Time Limit (minutes)", min_value=5, max_value=180, value=30)
        
        start_generation = st.form_submit_button("🚀 Start Generating", type="primary", use_container_width=True)
        
        if start_generation:
            if not quiz_title:
                st.error("Quiz title is required!")
                return
            
            # Store configuration
            st.session_state.quiz_gen_config = {
                'title': quiz_title,
                'num_questions': num_questions,
                'difficulty': difficulty,
                'time_limit': time_limit
            }
            
            # Initialize AI generator with lecture context
            ai_generator = get_ai_quiz_generator()
            
            # Get transcript from lecture
            transcript = lecture.get('transcript', lecture.get('description', ''))
            if not transcript:
                transcript = f"Lecture about {lecture.get('title')}. {lecture.get('description', '')}"
            
            ai_generator.set_lecture_context(
                lecture_title=lecture.get('title'),
                transcript=transcript,
                description=lecture.get('description', '')
            )
            
            # Track quiz generation start
            tracker = get_activity_tracker()
            tracker.track_activity(
                user_id=user['user_id'],
                action_type='quiz_generation_started',
                details={
                    'course_id': course_id,
                    'course_name': course.get('name'),
                    'lecture_id': lecture_id,
                    'lecture_name': lecture.get('title'),
                    'num_questions': num_questions
                }
            )
            
            st.session_state.quiz_gen_step = 'generate'
            st.session_state.quiz_gen_questions = []
            st.session_state.current_question_data = None
            st.rerun()


def show_interactive_generation(user, storage, ai_generator, tracker):
    """Step 4: Interactive question generation"""
    st.markdown("## 🎯 Step 4: Generate Questions")
    
    config = st.session_state.quiz_gen_config
    questions = st.session_state.quiz_gen_questions
    
    course_id = st.session_state.get('quiz_gen_course')
    lecture_id = st.session_state.get('quiz_gen_lecture')
    
    course = storage.get_course(course_id)
    lecture = next((l for l in course.get('lectures', []) if l.get('lecture_id') == lecture_id), None)
    
    st.markdown(f"**Quiz:** {config['title']}")
    st.markdown(f"**Progress:** {len(questions)} / {config['num_questions']} questions")
    
    progress = len(questions) / config['num_questions']
    st.progress(progress)
    
    st.markdown("---")
    
    # Check if quiz is complete
    if len(questions) >= config['num_questions']:
        st.success(f"✅ Quiz complete! {len(questions)} questions generated.")
        
        if st.button("Review and Save Quiz", type="primary", use_container_width=True):
            st.session_state.quiz_gen_step = 'review'
            st.rerun()
        return
    
    # Generate or display current question
    current_q = st.session_state.current_question_data
    
    if not current_q:
        st.markdown(f"### Generating Question #{len(questions) + 1}...")
        
        # Custom prompt from teacher (optional)
        with st.expander("➕ Custom Instructions (Optional)"):
            custom_prompt = st.text_area(
                "Provide specific instructions for this question",
                placeholder="e.g., Focus on the main concept explained in the beginning",
                key="custom_prompt_input"
            )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🤖 Generate Question", type="primary", use_container_width=True):
                with st.spinner("AI is generating a question..."):
                    custom_prompt = st.session_state.get('custom_prompt_input', '')
                    question_data = ai_generator.generate_question(
                        custom_prompt=custom_prompt if custom_prompt else None,
                        difficulty=config['difficulty'],
                        question_type='multiple_choice'
                    )
                    
                    st.session_state.current_question_data = question_data
                    st.rerun()
        
        with col2:
            if st.button("⏭️ Skip to Review", use_container_width=True):
                if len(questions) > 0:
                    st.session_state.quiz_gen_step = 'review'
                    st.rerun()
                else:
                    st.warning("Generate at least one question first!")
    
    else:
        # Display current question for review
        st.markdown(f"### 🔍 Review Question #{len(questions) + 1}")
        
        show_question_preview(current_q, len(questions) + 1)
        
        st.markdown("---")
        st.markdown("### ✅ Teacher Decision")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✅ Accept Question", type="primary", use_container_width=True):
                # Add question to quiz
                questions.append(current_q)
                st.session_state.quiz_gen_questions = questions
                st.session_state.current_question_data = None
                st.success("Question added to quiz!")
                st.rerun()
        
        with col2:
            if st.button("🔄 Regenerate", use_container_width=True):
                with st.expander("Feedback for Regeneration", expanded=True):
                    feedback = st.text_area(
                        "What should be improved?",
                        placeholder="e.g., Too difficult, focus more on...",
                        key="regen_feedback"
                    )
                    
                    if st.button("Generate New Version"):
                        with st.spinner("Regenerating..."):
                            new_question = ai_generator.regenerate_question(
                                feedback=feedback,
                                previous_question=current_q,
                                difficulty=config['difficulty']
                            )
                            st.session_state.current_question_data = new_question
                            st.rerun()
        
        with col3:
            if st.button("❌ Reject & Skip", use_container_width=True):
                st.session_state.current_question_data = None
                st.warning("Question rejected. Generate a new one.")
                st.rerun()


def show_quiz_review(user, storage, tracker):
    """Step 5: Review all questions and save quiz"""
    st.markdown("## 📋 Step 5: Review & Save Quiz")
    
    config = st.session_state.quiz_gen_config
    questions = st.session_state.quiz_gen_questions
    
    course_id = st.session_state.get('quiz_gen_course')
    lecture_id = st.session_state.get('quiz_gen_lecture')
    
    st.markdown(f"**Quiz Title:** {config['title']}")
    st.markdown(f"**Total Questions:** {len(questions)}")
    st.markdown(f"**Difficulty:** {config['difficulty'].title()}")
    st.markdown(f"**Time Limit:** {config['time_limit']} minutes")
    
    st.markdown("---")
    
    if st.button("← Back to Generation", key="back_to_gen"):
        st.session_state.quiz_gen_step = 'generate'
        st.rerun()
    
    # Display all questions
    st.markdown("### 📝 All Questions")
    
    for idx, q in enumerate(questions):
        with st.expander(f"Question {idx + 1}: {q.get('question', '')[:80]}..."):
            show_question_preview(q, idx + 1)
            
            if st.button(f"🗑️ Remove", key=f"remove_q_{idx}"):
                questions.pop(idx)
                st.session_state.quiz_gen_questions = questions
                st.rerun()
    
    st.markdown("---")
    
    # Save quiz
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Save Quiz", type="primary", use_container_width=True):
            if len(questions) == 0:
                st.error("Cannot save quiz with no questions!")
                return
            
            # Save to storage
            quiz_id = storage.create_quiz(
                course_id=course_id,
                lecture_id=lecture_id,
                title=config['title'],
                questions=questions,
                time_limit=config['time_limit'],
                difficulty=config['difficulty']
            )
            
            if quiz_id:
                # Track quiz generation completion
                tracker.track_activity(
                    user_id=user['user_id'],
                    action_type='quiz_generation_completed',
                    details={
                        'course_id': course_id,
                        'lecture_id': lecture_id,
                        'quiz_id': quiz_id,
                        'num_questions': len(questions)
                    }
                )
                
                st.success(f"✅ Quiz saved successfully! Quiz ID: {quiz_id}")
                
                # Reset session
                st.session_state.quiz_gen_step = 'select_course'
                st.session_state.quiz_gen_questions = []
                st.session_state.current_question_data = None
                
                if st.button("🎉 Create Another Quiz"):
                    st.rerun()
            else:
                st.error("Failed to save quiz. Please try again.")
    
    with col2:
        if st.button("🗑️ Discard Quiz", use_container_width=True):
            if st.checkbox("I understand this will delete all questions"):
                st.session_state.quiz_gen_step = 'select_course'
                st.session_state.quiz_gen_questions = []
                st.session_state.current_question_data = None
                st.rerun()
