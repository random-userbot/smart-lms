"""
Universal AI Tutor - WhatsApp Style Chat UI
Context-aware AI assistant with modern messaging interface
"""

import streamlit as st
import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.context_aware_tutor import get_context_aware_tutor
from services.storage import get_storage


def show_ai_tutor():
    """Display AI tutor with WhatsApp-like chat interface"""
    
    # Custom CSS for WhatsApp-like UI
    st.markdown("""
    <style>
    /* Chat container */
    .chat-container {
        height: 500px;
        overflow-y: auto;
        padding: 20px;
        background: linear-gradient(to bottom, #e5ddd5 0%, #f0f0f0 100%);
        border-radius: 10px;
        margin-bottom: 20px;
    }
    
    /* User message (right side - green) */
    .user-message {
        background: #dcf8c6;
        padding: 12px 16px;
        border-radius: 12px;
        margin: 8px 0;
        margin-left: 20%;
        text-align: left;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        position: relative;
    }
    
    .user-message::before {
        content: "You";
        position: absolute;
        top: -18px;
        right: 10px;
        font-size: 11px;
        color: #666;
        font-weight: 600;
    }
    
    /* AI message (left side - white) */
    .ai-message {
        background: white;
        padding: 12px 16px;
        border-radius: 12px;
        margin: 8px 0;
        margin-right: 20%;
        text-align: left;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        position: relative;
    }
    
    .ai-message::before {
        content: "🤖 AI Tutor";
        position: absolute;
        top: -18px;
        left: 10px;
        font-size: 11px;
        color: #666;
        font-weight: 600;
    }
    
    /* Timestamp */
    .timestamp {
        font-size: 10px;
        color: #999;
        margin-top: 4px;
        text-align: right;
    }
    
    /* Input area */
    .stTextInput input {
        border-radius: 24px !important;
        padding: 12px 20px !important;
        border: 2px solid #128C7E !important;
    }
    
    .stButton button {
        border-radius: 24px !important;
        background: #128C7E !important;
        color: white !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
    }
    
    .stButton button:hover {
        background: #075E54 !important;
    }
    
    /* Header */
    .chat-header {
        background: #128C7E;
        color: white;
        padding: 15px 20px;
        border-radius: 10px 10px 0 0;
        margin-bottom: 0;
    }
    
    .status-online {
        width: 10px;
        height: 10px;
        background: #25D366;
        border-radius: 50%;
        display: inline-block;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize tutor and storage
    tutor = get_context_aware_tutor()
    storage = get_storage()
    
    # Initialize session state for chat history
    if 'ai_tutor_messages' not in st.session_state:
        st.session_state.ai_tutor_messages = []
    
    if 'current_course_context' not in st.session_state:
        st.session_state.current_course_context = None
    
    # Get courses
    courses_dict = storage.get_all_courses()
    courses = list(courses_dict.values()) if courses_dict else []
    
    # Header with context info
    st.markdown("""
    <div class="chat-header">
        <div style="font-size: 24px; font-weight: 600;">🤖 AI Tutor</div>
        <div style="font-size: 12px; opacity: 0.9;">
            <span class="status-online"></span> Online - Ready to help you learn
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Context selection (compact)
    if courses:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Course selection
            course_names = {c['course_id']: f"{c.get('name', 'Unnamed Course')}" for c in courses}
            selected_course_id = st.selectbox(
                "📚 Course",
                options=list(course_names.keys()),
                format_func=lambda x: course_names[x],
                key="tutor_course_chat"
            )
            
            # Get selected course
            selected_course = next((c for c in courses if c['course_id'] == selected_course_id), None)
            
            # Auto-set context when course changes
            if selected_course and selected_course_id != st.session_state.current_course_context:
                st.session_state.current_course_context = selected_course_id
                tutor.set_context(selected_course, None)
                
                # Add welcome message
                subject_emoji = {
                    'language': '🗣️', 'history': '📜', 'math': '🔢', 
                    'science': '🔬', 'general': '📚'
                }.get(tutor.current_subject, '📚')
                
                welcome_msg = f"Hi! I'm your AI tutor for **{selected_course.get('name', 'this course')}** {subject_emoji}\n\nI've detected this is a **{tutor.current_subject}** course. Ask me anything!"
                
                if not st.session_state.ai_tutor_messages or st.session_state.ai_tutor_messages[-1]['content'] != welcome_msg:
                    st.session_state.ai_tutor_messages.append({
                        'role': 'ai',
                        'content': welcome_msg,
                        'timestamp': datetime.now().strftime('%I:%M %p')
                    })
        
        with col2:
            # Show active model
            model_display = tutor.model.split('/')[-1] if hasattr(tutor, 'model') else 'gpt-oss-120b'
            model_emoji = '🌏' if 'qwen' in tutor.model.lower() else '🧠'
            st.info(f"{model_emoji} **{model_display}**")
    
    else:
        st.warning("📚 No courses available. Please add courses first.")
        return
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Chat messages display
    if st.session_state.ai_tutor_messages:
        for msg in st.session_state.ai_tutor_messages:
            if msg['role'] == 'user':
                st.markdown(f"""
                <div class="user-message">
                    {msg['content']}
                    <div class="timestamp">{msg['timestamp']}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="ai-message">
                    {msg['content']}
                    <div class="timestamp">{msg['timestamp']}</div>
                </div>
                """, unsafe_allow_html=True)
    
    # Input area at bottom
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_question = st.text_input(
            "Message",
            key="user_input_chat",
            placeholder="Type your question here... 💬",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.button("📤 Send", use_container_width=True, type="primary")
    
    # Quick action buttons
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("❓ Explain", use_container_width=True):
            st.session_state.quick_action = "explain"
    with col2:
        if st.button("📝 Quiz", use_container_width=True):
            st.session_state.quick_action = "quiz"
    with col3:
        if st.button("💡 Example", use_container_width=True):
            st.session_state.quick_action = "example"
    with col4:
        if st.button("🔄 Clear", use_container_width=True):
            st.session_state.ai_tutor_messages = []
            st.rerun()
    
    # Handle message sending
    if send_button and user_question:
        # Add user message
        st.session_state.ai_tutor_messages.append({
            'role': 'user',
            'content': user_question,
            'timestamp': datetime.now().strftime('%I:%M %p')
        })
        
        # Get AI response
        with st.spinner('🤖 Thinking...'):
            try:
                response = tutor.solve_doubt(user_question, None)
                
                # Add AI response
                st.session_state.ai_tutor_messages.append({
                    'role': 'ai',
                    'content': response,
                    'timestamp': datetime.now().strftime('%I:%M %p')
                })
                
            except Exception as e:
                st.session_state.ai_tutor_messages.append({
                    'role': 'ai',
                    'content': f"Sorry, I encountered an error: {str(e)}",
                    'timestamp': datetime.now().strftime('%I:%M %p')
                })
        
        st.rerun()
    
    # Handle quick actions
    if hasattr(st.session_state, 'quick_action'):
        action = st.session_state.quick_action
        delattr(st.session_state, 'quick_action')
        
        if action == "explain":
            prompt = "Can you explain the main topics in this course?"
        elif action == "quiz":
            prompt = "Generate a 5-question quiz for me"
        elif action == "example":
            prompt = "Give me a practical example"
        else:
            return
        
        # Add to messages and process
        st.session_state.ai_tutor_messages.append({
            'role': 'user',
            'content': prompt,
            'timestamp': datetime.now().strftime('%I:%M %p')
        })
        
        with st.spinner('🤖 Thinking...'):
            try:
                response = tutor.solve_doubt(prompt, None)
                st.session_state.ai_tutor_messages.append({
                    'role': 'ai',
                    'content': response,
                    'timestamp': datetime.now().strftime('%I:%M %p')
                })
            except Exception as e:
                st.session_state.ai_tutor_messages.append({
                    'role': 'ai',
                    'content': f"Sorry, error: {str(e)}",
                    'timestamp': datetime.now().strftime('%I:%M %p')
                })
        
        st.rerun()
