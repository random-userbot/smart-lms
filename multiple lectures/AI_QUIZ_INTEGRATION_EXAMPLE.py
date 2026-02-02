"""
Example: Integrating Japanese AI with Existing Quiz System

This file shows how to integrate AI quiz generation into your existing upload.py
"""

# ============================================
# OPTION 1: Add AI Generation to Upload Page
# ============================================

# Add this to app/pages/upload.py in the show_create_quiz() function

def show_create_quiz_with_ai():
    """Create quiz with optional AI generation"""
    st.subheader("📝 Create Quiz")
    
    storage = get_storage()
    user = st.session_state.user
    
    # Get teacher's courses
    courses = storage.get_all_courses(teacher_id=user['user_id'])
    
    if not courses:
        st.warning("⚠️ You don't have any courses yet.")
        return
    
    # AI Generation Toggle
    use_ai = st.toggle("🤖 Generate Quiz with AI", 
                       help="AI will create questions based on your topic")
    
    with st.form("create_quiz_form"):
        # Course selection
        course_options = {cid: c['name'] for cid, c in courses.items()}
        selected_course = st.selectbox(
            "Select Course",
            options=list(course_options.keys()),
            format_func=lambda x: course_options[x]
        )
        
        # Get course lectures
        lectures = storage.get_course_lectures(selected_course)
        lecture_options = {l['lecture_id']: l['title'] for l in lectures}
        lecture_options['none'] = "Not linked to specific lecture"
        
        linked_lecture = st.selectbox(
            "Link to Lecture (Optional)",
            options=list(lecture_options.keys()),
            format_func=lambda x: lecture_options[x],
            index=len(lecture_options) - 1
        )
        
        if use_ai:
            # AI-powered quiz generation
            st.markdown("### 🤖 AI Quiz Generation")
            
            col1, col2 = st.columns(2)
            with col1:
                ai_topic = st.text_input(
                    "Quiz Topic",
                    placeholder="e.g., JLPT N5 Vocabulary, Particles, Hiragana",
                    help="What should the quiz cover?"
                )
                
                ai_difficulty = st.selectbox(
                    "Difficulty Level",
                    ["beginner", "intermediate", "advanced"]
                )
            
            with col2:
                ai_question_count = st.number_input(
                    "Number of Questions",
                    min_value=5,
                    max_value=30,
                    value=10
                )
                
                ai_quiz_type = st.selectbox(
                    "Quiz Type",
                    ["mixed", "vocabulary", "grammar", "kanji", "reading"]
                )
            
            # Optional: Manual quiz details
            quiz_title = st.text_input(
                "Quiz Title (optional - AI will generate)",
                placeholder="Leave blank for AI-generated title"
            )
            
            time_limit = st.number_input(
                "Time Limit (minutes)",
                min_value=5,
                max_value=180,
                value=30
            )
            
            submit = st.form_submit_button("🎯 Generate AI Quiz", type="primary")
            
            if submit:
                if not ai_topic:
                    st.error("❌ Please enter a quiz topic")
                    return
                
                # Import AI service
                from services.japanese_ai_service import get_japanese_ai_service
                
                with st.spinner(f"🤖 Generating {ai_question_count} questions..."):
                    ai_service = get_japanese_ai_service("groq")
                    
                    if not ai_service.is_available():
                        st.error("❌ AI service not available. Please configure API keys.")
                        st.info("See JAPANESE_AI_GUIDE.md for setup")
                        return
                    
                    # Generate quiz
                    quiz_data = ai_service.generate_japanese_quiz(
                        topic=ai_topic,
                        difficulty=ai_difficulty,
                        question_count=ai_question_count,
                        quiz_type=ai_quiz_type
                    )
                
                if quiz_data:
                    # Use custom title if provided
                    if quiz_title:
                        quiz_data['title'] = quiz_title
                    
                    quiz_data['time_limit'] = time_limit
                    quiz_data['quiz_id'] = f"quiz_{uuid.uuid4().hex[:8]}"
                    
                    # Save to lecture or course
                    if linked_lecture != 'none':
                        lecture = storage.get_lecture(linked_lecture)
                        if lecture:
                            quizzes = lecture.get('quizzes', [])
                            quizzes.append(quiz_data)
                            storage.update_lecture(linked_lecture, {'quizzes': quizzes})
                    
                    # Log activity
                    storage.log_teacher_activity(
                        activity_id=str(uuid.uuid4()),
                        teacher_id=user['user_id'],
                        action='create_ai_quiz',
                        details={
                            'quiz_id': quiz_data['quiz_id'],
                            'topic': ai_topic,
                            'question_count': len(quiz_data['questions']),
                            'ai_generated': True
                        }
                    )
                    
                    st.success(f"✅ AI Quiz '{quiz_data['title']}' created successfully!")
                    st.balloons()
                    
                    # Show preview
                    with st.expander("👀 Preview Quiz"):
                        st.markdown(f"**Title:** {quiz_data['title']}")
                        st.markdown(f"**Description:** {quiz_data.get('description', 'N/A')}")
                        st.markdown(f"**Questions:** {len(quiz_data['questions'])}")
                        
                        for i, q in enumerate(quiz_data['questions'][:3]):
                            st.markdown(f"---")
                            st.markdown(f"**Q{i+1}:** {q['question']}")
                            for opt, val in q['options'].items():
                                st.markdown(f"  {opt}. {val}")
                        
                        if len(quiz_data['questions']) > 3:
                            st.info(f"... plus {len(quiz_data['questions']) - 3} more questions")
                else:
                    st.error("❌ Failed to generate quiz. Please try again.")
        
        else:
            # Manual quiz creation (existing code)
            st.markdown("### ✍️ Manual Quiz Creation")
            # ... existing manual quiz code ...


# ============================================
# USAGE INSTRUCTIONS
# ============================================

"""
To integrate: Copy the function above to upload.py and replace/extend show_create_quiz()

Minimal integration example:

from services.japanese_ai_service import get_japanese_ai_service

use_ai = st.checkbox("🤖 Generate with AI")
if use_ai:
    ai = get_japanese_ai_service("groq")
    quiz = ai.generate_japanese_quiz("JLPT N5", "beginner", 10)
"""
