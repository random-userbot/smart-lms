"""
AI Audio Practice - WhatsApp Style Chat UI
Listening and Speaking practice with modern messaging interface
"""

import streamlit as st
import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.audio_practice import get_audio_service
from services.japanese_ai_service import get_japanese_ai_service


def show_audio_practice():
    """Display audio practice with WhatsApp-like chat interface"""
    
    # Custom CSS for WhatsApp-like UI
    st.markdown("""
    <style>
    /* User message (right side - green) */
    .user-message-audio {
        background: #dcf8c6;
        padding: 12px 16px;
        border-radius: 12px;
        margin: 8px 0;
        margin-left: 20%;
        text-align: left;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        position: relative;
    }
    
    .user-message-audio::before {
        content: "You";
        position: absolute;
        top: -18px;
        right: 10px;
        font-size: 11px;
        color: #666;
        font-weight: 600;
    }
    
    /* AI message (left side - white) */
    .ai-message-audio {
        background: white;
        padding: 12px 16px;
        border-radius: 12px;
        margin: 8px 0;
        margin-right: 20%;
        text-align: left;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        position: relative;
    }
    
    .ai-message-audio::before {
        content: "🎧 Audio Tutor";
        position: absolute;
        top: -18px;
        left: 10px;
        font-size: 11px;
        color: #666;
        font-weight: 600;
    }
    
    /* Audio message style */
    .audio-message {
        background: #f0f0f0;
        padding: 12px 16px;
        border-radius: 12px;
        margin: 8px 0;
        margin-right: 20%;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    
    /* Timestamp */
    .timestamp {
        font-size: 10px;
        color: #999;
        margin-top: 4px;
        text-align: right;
    }
    
    /* Input area */
    .stTextInput input, .stTextArea textarea {
        border-radius: 16px !important;
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
    
    # Initialize services
    audio_service = get_audio_service()
    ai_service = get_japanese_ai_service()
    
    # Check if audio service is available
    if not audio_service.is_available():
        st.error("⚠️ Audio service not available. Please install: `pip install gTTS`")
        return
    
    # Initialize session state
    if 'audio_messages' not in st.session_state:
        st.session_state.audio_messages = [{
            'role': 'ai',
            'content': "👋 Hi! I'm your audio practice assistant. I can help you with listening and speaking practice in multiple languages!\n\n🎧 Send me text and I'll convert it to audio\n🎤 Describe what you want to practice",
            'timestamp': datetime.now().strftime('%I:%M %p')
        }]
    
    if 'selected_language' not in st.session_state:
        st.session_state.selected_language = 'ja'
    
    # Header
    st.markdown("""
    <div class="chat-header">
        <div style="font-size: 24px; font-weight: 600;">🎧 Audio Practice</div>
        <div style="font-size: 12px; opacity: 0.9;">
            <span class="status-online"></span> Ready for listening & speaking practice
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Language selection (compact)
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        language = st.selectbox(
            "🌐 Language",
            options=['ja', 'en', 'es', 'fr', 'de', 'ko', 'zh-CN'],
            format_func=lambda x: {
                'ja': '🇯🇵 Japanese',
                'en': '🇬🇧 English',
                'es': '🇪🇸 Spanish',
                'fr': '🇫🇷 French',
                'de': '🇩🇪 German',
                'ko': '🇰🇷 Korean',
                'zh-CN': '🇨🇳 Chinese'
            }.get(x, x),
            key="audio_language"
        )
        st.session_state.selected_language = language
    
    with col2:
        slow_speech = st.checkbox("🐌 Slow", value=False)
    
    with col3:
        st.info(f"🎯 **{language.upper()}**")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Display chat messages
    if st.session_state.audio_messages:
        for msg in st.session_state.audio_messages:
            if msg['role'] == 'user':
                st.markdown(f"""
                <div class="user-message-audio">
                    {msg['content']}
                    <div class="timestamp">{msg['timestamp']}</div>
                </div>
                """, unsafe_allow_html=True)
            elif msg['role'] == 'audio':
                # Audio message
                st.markdown(f"""
                <div class="audio-message">
                    🔊 Audio Message
                    <div class="timestamp">{msg['timestamp']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Display audio player
                if 'audio_data' in msg:
                    st.audio(msg['audio_data'], format='audio/mp3')
                    
                    if 'text' in msg:
                        with st.expander("📝 View Text"):
                            st.write(msg['text'])
            else:
                st.markdown(f"""
                <div class="ai-message-audio">
                    {msg['content']}
                    <div class="timestamp">{msg['timestamp']}</div>
                </div>
                """, unsafe_allow_html=True)
    
    # Input area at bottom
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Mode selection
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🎧 Listening Practice", use_container_width=True):
            st.session_state.audio_mode = "listening"
    
    with col2:
        if st.button("💬 Conversation", use_container_width=True):
            st.session_state.audio_mode = "conversation"
    
    with col3:
        if st.button("🔄 Clear Chat", use_container_width=True):
            st.session_state.audio_messages = [{
                'role': 'ai',
                'content': "Chat cleared! Ready to practice again. 🎯",
                'timestamp': datetime.now().strftime('%I:%M %p')
            }]
            st.rerun()
    
    # Text input and send
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_text = st.text_area(
            "Message",
            key="audio_text_input",
            placeholder="Type text to convert to audio, or ask for practice... 💬",
            height=80,
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        generate_button = st.button("🔊 Audio", use_container_width=True, type="primary")
        send_button = st.button("📤 Send", use_container_width=True)
    
    # Handle audio generation
    if generate_button and user_text:
        # Add user message
        st.session_state.audio_messages.append({
            'role': 'user',
            'content': f"🔊 Generate audio: \"{user_text}\"",
            'timestamp': datetime.now().strftime('%I:%M %p')
        })
        
        # Generate audio
        with st.spinner('🔊 Generating audio...'):
            try:
                audio_b64 = audio_service.text_to_speech(
                    user_text,
                    language=st.session_state.selected_language,
                    slow=slow_speech
                )
                
                if audio_b64:
                    import base64
                    audio_bytes = base64.b64decode(audio_b64)
                    
                    # Add audio message
                    st.session_state.audio_messages.append({
                        'role': 'audio',
                        'audio_data': audio_bytes,
                        'text': user_text,
                        'timestamp': datetime.now().strftime('%I:%M %p')
                    })
                    
                    st.session_state.audio_messages.append({
                        'role': 'ai',
                        'content': "✅ Audio generated! Listen above. Try repeating it for speaking practice! 🎤",
                        'timestamp': datetime.now().strftime('%I:%M %p')
                    })
                else:
                    st.session_state.audio_messages.append({
                        'role': 'ai',
                        'content': "❌ Sorry, couldn't generate audio. Please try again.",
                        'timestamp': datetime.now().strftime('%I:%M %p')
                    })
                    
            except Exception as e:
                st.session_state.audio_messages.append({
                    'role': 'ai',
                    'content': f"❌ Error: {str(e)}",
                    'timestamp': datetime.now().strftime('%I:%M %p')
                })
        
        st.rerun()
    
    # Handle text conversation
    if send_button and user_text:
        # Add user message
        st.session_state.audio_messages.append({
            'role': 'user',
            'content': user_text,
            'timestamp': datetime.now().strftime('%I:%M %p')
        })
        
        # Get AI response
        with st.spinner('🤖 Thinking...'):
            try:
                # Use AI to generate conversational response
                response = ai_service.practice_conversation(
                    user_message=user_text,
                    scenario="casual"
                )
                
                ai_response = response.get('response', 'Sorry, I could not generate a response.')
                
                # Add AI response
                st.session_state.audio_messages.append({
                    'role': 'ai',
                    'content': ai_response,
                    'timestamp': datetime.now().strftime('%I:%M %p')
                })
                
                # Optionally generate audio for AI response
                if len(ai_response) < 200:  # Only for short responses
                    audio_b64 = audio_service.text_to_speech(
                        ai_response,
                        language=st.session_state.selected_language,
                        slow=slow_speech
                    )
                    
                    if audio_b64:
                        import base64
                        audio_bytes = base64.b64decode(audio_b64)
                        
                        st.session_state.audio_messages.append({
                            'role': 'audio',
                            'audio_data': audio_bytes,
                            'text': ai_response,
                            'timestamp': datetime.now().strftime('%I:%M %p')
                        })
                
            except Exception as e:
                st.session_state.audio_messages.append({
                    'role': 'ai',
                    'content': f"Sorry, error: {str(e)}",
                    'timestamp': datetime.now().strftime('%I:%M %p')
                })
        
        st.rerun()
