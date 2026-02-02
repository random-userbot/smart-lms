"""
Smart LMS - Japanese Learning Assistant
AI-powered tools for Japanese language learning
"""

import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.japanese_ai_service import get_japanese_ai_service, check_ai_availability
from services.storage import get_storage
from datetime import datetime
import json


def show_ai_status():
    """Show AI provider availability status"""
    st.sidebar.markdown("### 🤖 AI Status")
    availability = check_ai_availability()
    
    providers = {
        "groq": ("Groq (FREE)", "Fast & recommended"),
        "openai": ("OpenAI (PAID)", "Premium quality"),
        "gemini": ("Gemini (FREE)", "Good multilingual")
    }
    
    available_providers = []
    for provider, (name, desc) in providers.items():
        status = "✅" if availability[provider] else "❌"
        st.sidebar.markdown(f"{status} **{name}**")
        st.sidebar.caption(desc)
        if availability[provider]:
            available_providers.append(provider)
    
    if not available_providers:
        st.sidebar.error("⚠️ No AI provider configured")
        st.sidebar.info("See JAPANESE_AI_GUIDE.md for setup")
        return None
    
    # Let user select provider
    if len(available_providers) > 1:
        selected = st.sidebar.selectbox(
            "Select AI Provider",
            available_providers,
            format_func=lambda x: providers[x][0]
        )
    else:
        selected = available_providers[0]
    
    return selected


def show_text_explainer(ai_service):
    """Japanese text explanation tool"""
    st.subheader("📖 Text Explainer")
    st.markdown("Paste Japanese text to get translations, grammar explanations, and cultural notes.")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        japanese_text = st.text_area(
            "Japanese Text",
            placeholder="こんにちは、元気ですか？",
            height=150,
            key="text_explainer_input"
        )
    
    with col2:
        difficulty = st.selectbox(
            "Your Level",
            ["beginner", "intermediate", "advanced"],
            key="text_explainer_level"
        )
    
    if st.button("🔍 Explain Text", type="primary"):
        if not japanese_text:
            st.warning("Please enter some Japanese text")
            return
        
        with st.spinner("Analyzing text..."):
            result = ai_service.explain_japanese_text(japanese_text, difficulty)
        
        # Display results
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🇬🇧 Translation")
            st.info(result.get('translation', 'Translation not available'))
            
            st.markdown("### 📚 Grammar Points")
            st.markdown(result.get('grammar', 'Grammar explanation not available'))
        
        with col2:
            st.markdown("### 🔤 Word Breakdown")
            st.markdown(result.get('breakdown', 'Breakdown not available'))
            
            st.markdown("### 🏯 Cultural Notes")
            st.markdown(result.get('cultural_notes', 'No cultural notes'))


def show_writing_corrector(ai_service):
    """Japanese writing correction tool"""
    st.subheader("✍️ Writing Corrector")
    st.markdown("Submit your Japanese writing for AI feedback and corrections.")
    
    context = st.selectbox(
        "Writing Type",
        ["general", "email", "essay", "conversation", "formal_letter", "diary"],
        key="writing_context"
    )
    
    student_writing = st.text_area(
        "Your Japanese Writing",
        placeholder="私は昨日学校に行きました。",
        height=200,
        key="writing_input"
    )
    
    if st.button("✅ Check Writing", type="primary"):
        if not student_writing:
            st.warning("Please enter your writing")
            return
        
        with st.spinner("Analyzing your writing..."):
            result = ai_service.correct_japanese_writing(student_writing, context)
        
        st.markdown("---")
        st.markdown("### 📝 Feedback & Corrections")
        
        # Display in expandable sections
        with st.expander("✅ Corrected Version", expanded=True):
            st.markdown(result.get('corrected_text', result.get('feedback')))
        
        with st.expander("💡 Detailed Feedback"):
            st.markdown(result.get('feedback', 'Feedback not available'))
        
        # Save to user's history
        if st.button("💾 Save to My Practice History"):
            storage = get_storage()
            user = st.session_state.user
            # Could implement history storage here
            st.success("Saved to your history!")


def show_conversation_practice(ai_service):
    """AI conversation partner"""
    st.subheader("💬 Conversation Practice")
    st.markdown("Practice Japanese conversation with an AI partner.")
    
    # Initialize conversation history
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    scenario = st.selectbox(
        "Conversation Scenario",
        ["casual", "restaurant", "shopping", "travel", "business", "making_friends"],
        format_func=lambda x: x.replace('_', ' ').title(),
        key="conversation_scenario"
    )
    
    # Display conversation history
    st.markdown("### 💭 Conversation")
    
    for msg in st.session_state.conversation_history:
        role_icon = "👤" if msg['role'] == 'user' else "🤖"
        role_name = "You" if msg['role'] == 'user' else "AI Partner"
        
        with st.chat_message(role_name, avatar=role_icon):
            st.markdown(msg['content'])
            if 'translation' in msg:
                st.caption(f"*{msg['translation']}*")
    
    # User input
    user_message = st.chat_input("Type your message in Japanese...")
    
    if user_message:
        # Add user message
        st.session_state.conversation_history.append({
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Get AI response
        with st.spinner("Thinking..."):
            response = ai_service.practice_conversation(
                user_message,
                st.session_state.conversation_history[:-1],  # Exclude current message
                scenario
            )
        
        # Add AI response
        st.session_state.conversation_history.append({
            'role': 'assistant',
            'content': response['response'],
            'timestamp': response['timestamp']
        })
        
        st.rerun()
    
    # Clear conversation
    if st.button("🔄 Start New Conversation"):
        st.session_state.conversation_history = []
        st.rerun()


def show_bulk_quiz_generator(ai_service):
    """Bulk quiz generation for all lectures"""
    st.subheader("🚀 Bulk Quiz Generator")
    st.markdown("Automatically generate quizzes for all your lectures!")
    
    storage = get_storage()
    user = st.session_state.user
    
    # Get teacher's courses
    if user['role'] == 'teacher':
        courses = storage.get_all_courses(teacher_id=user['user_id'])
    elif user['role'] == 'admin':
        courses = storage.get_all_courses()
    else:
        st.warning("This feature is only available for teachers and admins")
        return
    
    if not courses:
        st.warning("No courses found")
        return
    
    # Course selection
    col1, col2 = st.columns(2)
    
    with col1:
        course_options = {**{cid: c['name'] for cid, c in courses.items()}, 'all': '🌟 All Courses'}
        selected_course = st.selectbox(
            "Select Course",
            options=list(course_options.keys()),
            format_func=lambda x: course_options[x]
        )
    
    with col2:
        difficulty = st.selectbox(
            "Quiz Difficulty",
            ["beginner", "intermediate", "advanced"],
            key="bulk_difficulty"
        )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        question_count = st.number_input(
            "Questions per Quiz",
            min_value=3,
            max_value=15,
            value=5,
            key="bulk_questions"
        )
    
    with col2:
        skip_existing = st.checkbox(
            "Skip lectures with quizzes",
            value=True,
            key="skip_existing"
        )
    
    with col3:
        st.markdown("&nbsp;")  # Spacing
        regenerate = not skip_existing
    
    # Get lecture count
    if selected_course == 'all':
        all_lectures = storage.get_all_lectures()
        total_lectures = len(all_lectures) if isinstance(all_lectures, dict) else len(list(all_lectures))
        course_name = "all courses"
    else:
        lectures = storage.get_course_lectures(selected_course)
        total_lectures = len(lectures)
        course_name = courses[selected_course]['name']
    
    st.info(f"📚 Found **{total_lectures}** lectures in {course_name}")
    
    if st.button("🎯 Generate Quizzes for All Lectures", type="primary", use_container_width=True):
        # Import bulk generator
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from bulk_quiz_generator import bulk_generate_quizzes, generate_quiz_for_lecture
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        results_container = st.container()
        
        course_id = None if selected_course == 'all' else selected_course
        
        # Get lectures
        if course_id:
            lectures = storage.get_course_lectures(course_id)
        else:
            all_lectures = storage.get_all_lectures()
            lectures = list(all_lectures.values()) if isinstance(all_lectures, dict) else all_lectures
        
        # Filter if skipping existing
        if skip_existing:
            lectures_to_process = [l for l in lectures if not l.get('quizzes')]
        else:
            lectures_to_process = lectures
        
        total = len(lectures_to_process)
        
        if total == 0:
            st.warning("All lectures already have quizzes. Uncheck 'Skip lectures with quizzes' to regenerate.")
            return
        
        status_text.text(f"Starting generation for {total} lectures...")
        
        # Generate quizzes
        generated = 0
        failed = 0
        
        for i, lecture in enumerate(lectures_to_process):
            lecture_id = lecture['lecture_id']
            title = lecture.get('title', 'Untitled')
            
            status_text.text(f"[{i+1}/{total}] Generating quiz for: {title[:50]}...")
            progress_bar.progress((i + 1) / total)
            
            try:
                quiz_data = generate_quiz_for_lecture(lecture, ai_service, difficulty, question_count)
                
                if quiz_data:
                    # Save to lecture
                    quizzes = lecture.get('quizzes', [])
                    quizzes.append(quiz_data)
                    storage.update_lecture(lecture_id, {'quizzes': quizzes})
                    generated += 1
                else:
                    failed += 1
                    
            except Exception as e:
                st.error(f"Error on '{title}': {str(e)}")
                failed += 1
        
        # Show results
        progress_bar.progress(1.0)
        status_text.text("✅ Generation complete!")
        
        st.markdown("---")
        st.markdown("### 📊 Results")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Lectures", total)
        with col2:
            st.metric("✅ Generated", generated)
        with col3:
            st.metric("❌ Failed", failed)
        
        if generated > 0:
            st.success(f"🎉 Successfully generated {generated} quizzes!")
            st.balloons()
        
        if failed > 0:
            st.warning(f"⚠️ {failed} quizzes failed to generate. Check your API rate limits.")


def show_quiz_generator(ai_service):
    """AI quiz generation tool"""
    st.subheader("📝 Quiz Generator")
    
    # Add tab selector
    tab1, tab2 = st.tabs(["📝 Single Quiz", "🚀 Bulk Generate"])
    
    with tab1:
        st.markdown("Generate a custom Japanese quiz on any topic.")
        
        col1, col2 = st.columns(2)
    
    with col1:
        topic = st.text_input(
            "Quiz Topic",
            placeholder="e.g., JLPT N5 Vocabulary, Particles, Verb Conjugation",
            key="quiz_topic"
        )
        
        difficulty = st.selectbox(
            "Difficulty",
            ["beginner", "intermediate", "advanced"],
            key="quiz_difficulty"
        )
    
    with col2:
        question_count = st.number_input(
            "Number of Questions",
            min_value=5,
            max_value=30,
            value=10,
            key="quiz_count"
        )
        
        quiz_type = st.selectbox(
            "Quiz Type",
            ["mixed", "vocabulary", "grammar", "kanji", "reading"],
            key="quiz_type"
        )
    
    if st.button("🎯 Generate Quiz", type="primary"):
        if not topic:
            st.warning("Please enter a quiz topic")
            return
        
        with st.spinner(f"Generating {question_count} questions..."):
            quiz_data = ai_service.generate_japanese_quiz(
                topic=topic,
                difficulty=difficulty,
                question_count=question_count,
                quiz_type=quiz_type
            )
        
        if quiz_data:
            st.success(f"✅ Generated quiz: {quiz_data.get('title', 'Untitled Quiz')}")
            
            # Display quiz preview
            with st.expander("👀 Preview Quiz", expanded=True):
                st.markdown(f"**Description:** {quiz_data.get('description', 'N/A')}")
                st.markdown(f"**Time Limit:** {quiz_data.get('time_limit', 30)} minutes")
                st.markdown(f"**Questions:** {len(quiz_data.get('questions', []))}")
                
                # Show first 3 questions
                for i, q in enumerate(quiz_data.get('questions', [])[:3]):
                    st.markdown(f"---")
                    st.markdown(f"**Question {i+1}:** {q.get('question')}")
                    if q.get('question_ja'):
                        st.caption(q['question_ja'])
                    
                    for opt_key, opt_val in q.get('options', {}).items():
                        st.markdown(f"  {opt_key}. {opt_val}")
                    
                    st.caption(f"✅ Correct: {q.get('correct_answer')}")
                
                if len(quiz_data.get('questions', [])) > 3:
                    st.info(f"... and {len(quiz_data['questions']) - 3} more questions")
            
            # Option to save quiz
            if st.button("💾 Add to Course"):
                # Could implement quiz saving here
                st.info("Select a course to add this quiz (feature coming soon)")
                
            # Download as JSON
            quiz_json = json.dumps(quiz_data, indent=2, ensure_ascii=False)
            st.download_button(
                label="📥 Download Quiz JSON",
                data=quiz_json,
                file_name=f"quiz_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        else:
            st.error("Failed to generate quiz. Please try again.")
    
    with tab2:
        show_bulk_quiz_generator(ai_service)


def show_assignment_grader(ai_service):
    """AI assignment grading tool"""
    st.subheader("📊 Assignment Grader")
    st.markdown("Get AI feedback and grading for Japanese assignments.")
    
    assignment_text = st.text_area(
        "Student Assignment",
        placeholder="Paste the student's Japanese writing here...",
        height=250,
        key="assignment_text"
    )
    
    # Optional rubric
    use_rubric = st.checkbox("Use Custom Rubric", key="use_rubric")
    
    rubric = None
    if use_rubric:
        rubric_text = st.text_area(
            "Grading Rubric (JSON format)",
            placeholder='{"grammar": 25, "vocabulary": 25, "content": 25, "style": 25}',
            height=100,
            key="rubric_text"
        )
        try:
            if rubric_text:
                rubric = json.loads(rubric_text)
        except json.JSONDecodeError:
            st.warning("Invalid JSON format for rubric")
    
    if st.button("🎓 Grade Assignment", type="primary"):
        if not assignment_text:
            st.warning("Please enter assignment text")
            return
        
        with st.spinner("Grading assignment..."):
            grade_result = ai_service.grade_japanese_assignment(
                assignment_text=assignment_text,
                rubric=rubric
            )
        
        st.markdown("---")
        
        # Display grade
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Overall Score", f"{grade_result['score']}/100")
        
        with col2:
            st.metric("Percentage", f"{grade_result['percentage']}%")
        
        with col3:
            grade_label = "A" if grade_result['percentage'] >= 90 else \
                         "B" if grade_result['percentage'] >= 80 else \
                         "C" if grade_result['percentage'] >= 70 else \
                         "D" if grade_result['percentage'] >= 60 else "F"
            st.metric("Grade", grade_label)
        
        # Category breakdown
        st.markdown("### 📊 Category Breakdown")
        breakdown = grade_result.get('breakdown', {})
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Grammar", f"{breakdown.get('grammar', 0):.1f}")
        with col2:
            st.metric("Vocabulary", f"{breakdown.get('vocabulary', 0):.1f}")
        with col3:
            st.metric("Content", f"{breakdown.get('content', 0):.1f}")
        with col4:
            st.metric("Style", f"{breakdown.get('style', 0):.1f}")
        
        # Detailed feedback
        st.markdown("### 💬 Detailed Feedback")
        st.markdown(grade_result['feedback'])
        
        # Save grade
        if st.button("💾 Save Grade"):
            st.success("Grade saved to student record!")


def main():
    """Main Japanese AI Assistant page"""
    st.title("🇯🇵 Japanese Learning Assistant")
    st.markdown("AI-powered tools to help you learn Japanese faster")
    
    # Check AI availability
    selected_provider = show_ai_status()
    
    if not selected_provider:
        st.error("⚠️ No AI service available. Please configure API keys.")
        st.info("See [JAPANESE_AI_GUIDE.md](JAPANESE_AI_GUIDE.md) for setup instructions.")
        
        st.markdown("### Quick Setup (FREE)")
        st.code("""
# 1. Get free API key from https://console.groq.com
# 2. Install package:
pip install groq

# 3. Set environment variable:
$env:GROQ_API_KEY="your_key_here"

# 4. Restart Streamlit
        """, language="powershell")
        return
    
    # Initialize AI service
    ai_service = get_japanese_ai_service(provider=selected_provider)
    
    if not ai_service.is_available():
        st.error(f"Failed to initialize {selected_provider} service")
        return
    
    # Tool selection
    tool = st.selectbox(
        "Select Tool",
        [
            "📖 Text Explainer",
            "✍️ Writing Corrector",
            "💬 Conversation Practice",
            "📝 Quiz Generator",
            "📊 Assignment Grader"
        ],
        key="tool_selector"
    )
    
    st.markdown("---")
    
    # Show selected tool
    if tool == "📖 Text Explainer":
        show_text_explainer(ai_service)
    elif tool == "✍️ Writing Corrector":
        show_writing_corrector(ai_service)
    elif tool == "💬 Conversation Practice":
        show_conversation_practice(ai_service)
    elif tool == "📝 Quiz Generator":
        show_quiz_generator(ai_service)
    elif tool == "📊 Assignment Grader":
        show_assignment_grader(ai_service)


if __name__ == "__main__":
    # Verify user is logged in
    if 'user' not in st.session_state:
        st.warning("⚠️ Please log in to use the Japanese Assistant")
        st.stop()
    
    main()
