"""
Smart LMS - Unified Teaching Analytics Dashboard
Consolidated page merging: Analytics, Tracking, Teaching Score, and Teacher Evaluation
Features card-based UI for better user experience
"""

import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.auth import get_auth
from services.storage import get_storage
from services.activity_tracker import get_activity_tracker
from services.universal_logger import get_activity_logger
from services.intelligent_scorer import get_intelligent_scorer
from services.teaching_score import get_teaching_score_calculator
from services.ai_explainer_bot import get_explainer_bot
from services.nlp import get_nlp_service
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from collections import defaultdict, Counter
from io import BytesIO


def render_course_card(course_id: str, course: dict, action_callback=None):
    """Render interactive course card"""
    enrolled_count = len(course.get('enrolled_students', []))
    teacher_name = course.get('teacher_name', 'Unknown')
    
    # Gradient colors for variety
    gradients = [
        "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
        "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
        "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
        "linear-gradient(135deg, #fa709a 0%, #fee140 100%)",
    ]
    gradient = gradients[hash(course_id) % len(gradients)]
    
    st.markdown(f"""
    <div style="
        background: {gradient};
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        transition: transform 0.2s, box-shadow 0.2s;
        cursor: pointer;
    " onmouseover="this.style.transform='translateY(-5px)'; this.style.boxShadow='0 8px 25px rgba(0,0,0,0.25)';"
       onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 6px 20px rgba(0,0,0,0.15)';">
        <h3 style="color: white; margin: 0 0 12px 0; font-size: 22px;">📚 {course.get('name', 'Untitled Course')}</h3>
        <p style="color: #f5f5f5; margin: 8px 0; font-size: 15px; line-height: 1.5;">
            {course.get('description', 'No description available')[:120]}...
        </p>
        <div style="display: flex; justify-content: space-between; margin-top: 18px; flex-wrap: wrap;">
            <span style="color: white; font-weight: bold; font-size: 15px;">👥 {enrolled_count} Students</span>
            <span style="color: white; font-size: 14px;">👨‍🏫 {teacher_name}</span>
        </div>
        <div style="margin-top: 10px;">
            <span style="color: rgba(255,255,255,0.8); font-size: 13px;">ID: {course_id}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button(f"📊 View Analytics", key=f"course_card_{course_id}", type="primary", use_container_width=True):
        if action_callback:
            action_callback(course_id)
        else:
            st.session_state.selected_course = course_id
            st.rerun()


def render_score_gauge(score: float, title: str, subtitle: str = ""):
    """Render gauge chart for teaching scores"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"<b>{title}</b><br><span style='font-size:14px'>{subtitle}</span>", 'font': {'size': 18}},
        delta={'reference': 70, 'increasing': {'color': "green"}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 60], 'color': '#ffcccc'},
                {'range': [60, 80], 'color': '#ffffcc'},
                {'range': [80, 100], 'color': '#ccffcc'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(height=280, margin=dict(l=20, r=20, t=60, b=20))
    return fig


def render_radar_chart(categories: list, values: list, title: str = "Performance Metrics"):
    """Render radar chart for multi-dimensional performance"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Current Performance',
        line=dict(color='#4169E1', width=2)
    ))
    
    # Add target benchmark
    fig.add_trace(go.Scatterpolar(
        r=[4.0] * len(categories),
        theta=categories,
        fill='toself',
        name='Target (4.0)',
        line=dict(color='green', dash='dash', width=2),
        opacity=0.3
    ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
        showlegend=True,
        title=title,
        height=400,
        font=dict(size=12)
    )
    return fig


def format_timestamp(timestamp_str: str) -> str:
    """Format ISO timestamp"""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return timestamp_str


def get_event_icon(event_type: str) -> str:
    """Get icon for event type"""
    icons = {
        'login': '🔐', 'logout': '🚪', 'lecture_start': '▶️', 'lecture_end': '⏹️',
        'quiz_start': '📝', 'quiz_submit': '✅', 'material_download': '📥',
        'notes_reading': '📖', 'assignment_interaction': '📋', 'attendance': '✋',
        'ai_tool_usage': '🤖', 'tab_switch': '🔄', 'feedback_given': '💬',
        'teacher_action': '👨‍🏫', 'course_view': '👁️', 'resource_access': '📚'
    }
    return icons.get(event_type, '📌')


def show_live_tracking_tab(user, storage):
    """Live Activity Tracking - Real-time student activities"""
    st.markdown("## 📡 Live Activity Tracking")
    st.markdown("Monitor student activities in real-time across all your courses")
    
    tracker = get_activity_tracker()
    
    # Get teacher's courses
    if user['role'] == 'teacher':
        all_courses = storage.get_all_courses()
        teacher_courses = {cid: c for cid, c in all_courses.items() 
                          if c.get('teacher_id') == user['user_id']}
    else:  # admin
        teacher_courses = storage.get_all_courses()
    
    if not teacher_courses:
        st.info("📚 No courses available. Create a course to start tracking student activity.")
        return
    
    st.markdown("### 📚 Select Course to Track")
    
    # Display courses as cards
    selected_course = st.session_state.get('selected_course_tracking')
    
    if not selected_course:
        # Show all courses as cards
        cols = st.columns(2)
        for idx, (course_id, course) in enumerate(teacher_courses.items()):
            with cols[idx % 2]:
                render_course_card(course_id, course, lambda cid: set_selected_course_tracking(cid))
        return
    
    # Selected course view
    course = teacher_courses.get(selected_course)
    if not course:
        st.error("Course not found")
        if st.button("← Back to Courses"):
            st.session_state.selected_course_tracking = None
            st.rerun()
        return
    
    # Back button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.selected_course_tracking = None
            st.rerun()
    with col2:
        st.markdown(f"### 📚 {course.get('name', 'Course')}")
    
    st.markdown("---")
    
    # Get enrolled students
    student_ids = course.get('enrolled_students', [])
    if not student_ids:
        st.info("No students enrolled in this course yet.")
        return
    
    # Activity summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_activities = 0
    active_today = 0
    recent_actions = []
    
    for student_id in student_ids:
        student_data = tracker.get_student_activity_summary(student_id, selected_course)
        total_activities += student_data.get('total_actions', 0)
        
        # Check if active today
        last_active = student_data.get('last_active')
        if last_active:
            try:
                last_dt = datetime.fromisoformat(last_active.replace('Z', '+00:00'))
                if last_dt.date() == datetime.now().date():
                    active_today += 1
            except:
                pass
        
        # Get recent actions
        actions = tracker.get_recent_activities(student_id, limit=10)
        recent_actions.extend([a for a in actions if a.get('context', {}).get('course_id') == selected_course])
    
    with col1:
        st.metric("👥 Total Students", len(student_ids))
    with col2:
        st.metric("✅ Active Today", active_today)
    with col3:
        st.metric("📊 Total Activities", total_activities)
    with col4:
        engagement_rate = (active_today / len(student_ids) * 100) if student_ids else 0
        st.metric("📈 Engagement Rate", f"{engagement_rate:.1f}%")
    
    st.markdown("---")
    
    # Recent Activities Feed
    st.markdown("### 🔄 Recent Activities (Live)")
    
    if not recent_actions:
        st.info("No recent activity recorded.")
    else:
        # Sort by timestamp
        recent_actions = sorted(recent_actions, key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Show last 20 activities
        for action in recent_actions[:20]:
            event_type = action.get('action_type', 'unknown')
            timestamp = format_timestamp(action.get('timestamp', ''))
            student_id = action.get('user_id', 'Unknown')
            student = storage.get_user(student_id)
            student_name = student.get('full_name', 'Unknown') if student else 'Unknown'
            
            icon = get_event_icon(event_type)
            details = action.get('details', {})
            
            with st.container():
                col1, col2, col3 = st.columns([1, 3, 2])
                with col1:
                    st.markdown(f"### {icon}")
                with col2:
                    st.markdown(f"**{student_name}** • {event_type.replace('_', ' ').title()}")
                    if details:
                        detail_str = " • ".join([f"{k}: {v}" for k, v in list(details.items())[:2]])
                        st.caption(detail_str)
                with col3:
                    st.caption(timestamp)
                st.markdown("---")
    
    # Download CSV
    if st.button("📥 Download Activity Report (CSV)", use_container_width=True):
        df_data = []
        for action in recent_actions:
            student_id = action.get('user_id')
            student = storage.get_user(student_id)
            df_data.append({
                'Timestamp': format_timestamp(action.get('timestamp', '')),
                'Student': student.get('full_name', 'Unknown') if student else 'Unknown',
                'Student ID': student_id,
                'Action Type': action.get('action_type', ''),
                'Details': str(action.get('details', {}))
            })
        
        if df_data:
            df = pd.DataFrame(df_data)
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"activity_report_{selected_course}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )


def set_selected_course_tracking(course_id):
    """Helper to set selected course for tracking"""
    st.session_state.selected_course_tracking = course_id
    st.rerun()


def show_teaching_score_tab(user, storage):
    """Teaching Effectiveness Score - ML-based teaching performance"""
    st.markdown("## 🎯 Teaching Effectiveness Score")
    st.markdown("Data-driven indicators of teaching performance with ML insights")
    
    calculator = get_teaching_score_calculator()
    explainer_bot = get_explainer_bot()
    
    # Get teacher ID
    if user['role'] == 'teacher':
        teacher_id = user['user_id']
    else:  # admin selecting teacher
        all_users = storage.get_all_users()
        teachers = {uid: u for uid, u in all_users.items() if u['role'] == 'teacher'}
        
        if not teachers:
            st.info("No teachers in the system.")
            return
        
        st.markdown("### 👨‍🏫 Select Teacher")
        teacher_cards = st.columns(min(3, len(teachers)))
        
        for idx, (tid, teacher) in enumerate(list(teachers.items())[:6]):
            with teacher_cards[idx % 3]:
                teacher_name = teacher.get('full_name', teacher['username'])
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 12px;
                    padding: 20px;
                    margin: 10px 0;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                    color: white;
                    text-align: center;
                ">
                    <h4 style="margin: 0;">👨‍🏫 {teacher_name}</h4>
                    <p style="margin: 5px 0; font-size: 12px; opacity: 0.9;">{tid}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"View Score", key=f"teacher_select_{tid}", use_container_width=True):
                    st.session_state.selected_teacher_score = tid
                    st.rerun()
        
        if 'selected_teacher_score' not in st.session_state:
            return
        
        teacher_id = st.session_state.selected_teacher_score
    
    # Calculate teaching score
    score_data = calculator.calculate_teaching_score(teacher_id)
    
    if not score_data or score_data.get('overall_score', 0) == 0:
        st.warning("⚠️ Insufficient data to calculate teaching effectiveness score. More student interactions are needed.")
        return
    
    st.markdown("---")
    
    # Overall Score Display
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        st.plotly_chart(
            render_score_gauge(
                score_data['overall_score'],
                "Overall Teaching Effectiveness",
                "Composite indicator from multiple factors"
            ),
            use_container_width=True
        )
    
    with col2:
        # Component breakdown
        components = score_data.get('components', {})
        if components:
            component_names = [c.replace('_', ' ').title() for c in components.keys()]
            component_values = [components[c]['score'] for c in components.keys()]
            
            fig = go.Figure(data=[
                go.Bar(
                    y=component_names,
                    x=component_values,
                    orientation='h',
                    marker=dict(
                        color=component_values,
                        colorscale='RdYlGn',
                        showscale=False,
                        cmin=0,
                        cmax=100
                    ),
                    text=[f"{v:.1f}" for v in component_values],
                    textposition='auto',
                )
            ])
            
            fig.update_layout(
                title="Score Components",
                xaxis_title="Score (0-100)",
                height=280,
                margin=dict(l=150, r=20, t=40, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        st.metric("📊 Overall Score", f"{score_data['overall_score']:.1f}/100")
        st.metric("📈 Trend", score_data.get('trend', 'Stable'))
        st.metric("🎯 Confidence", f"{score_data.get('confidence', 0.8)*100:.0f}%")
    
    st.markdown("---")
    
    # Key Insights
    st.markdown("### 💡 Key Insights & Recommendations")
    
    insights = score_data.get('insights', [])
    if insights:
        for insight in insights[:5]:
            st.info(f"💡 {insight}")
    else:
        st.info("No specific insights available yet. Continue teaching to generate personalized recommendations.")
    
    # AI Chatbot Integration
    st.markdown("---")
    st.markdown("### 🤖 Ask AI About Your Score")
    st.markdown("Get explanations and suggestions based on your data")
    
    user_question = st.text_input(
        "Ask a question",
        placeholder="e.g., Why is my student engagement score lower than my content quality?",
        key="teaching_score_question"
    )
    
    if st.button("Get Answer", key="ask_ai_teaching_score"):
        if user_question:
            with st.spinner("Analyzing your data..."):
                # Build context for AI
                context = {
                    'teacher_id': teacher_id,
                    'score_data': score_data,
                    'question': user_question
                }
                
                response = explainer_bot.answer_question(user_question, context)
                
                st.markdown("#### 🤖 AI Response:")
                st.markdown(response.get('answer', 'Unable to generate response.'))
                
                # Show confidence and limitations
                if response.get('confidence'):
                    st.caption(f"Confidence: {response['confidence']*100:.0f}%")
                if response.get('limitations'):
                    st.warning(f"⚠️ Limitations: {response['limitations']}")


def show_engagement_analytics_tab(user, storage):
    """Student Engagement Analytics - ML-powered engagement tracking"""
    st.markdown("## 📊 Student Engagement Analytics")
    st.markdown("ML-powered insights into learning engagement and patterns")
    
    logger = get_activity_logger()
    scorer = get_intelligent_scorer()
    
    # Get teacher's courses
    if user['role'] == 'teacher':
        all_courses = storage.get_all_courses()
        teacher_courses = {cid: c for cid, c in all_courses.items() 
                          if c.get('teacher_id') == user['user_id']}
    else:  # admin
        teacher_courses = storage.get_all_courses()
    
    if not teacher_courses:
        st.info("📚 No courses available.")
        return
    
    st.markdown("### 📚 Select Course")
    
    # Course selection with cards
    selected_course = st.session_state.get('selected_course_engagement')
    
    if not selected_course:
        cols = st.columns(2)
        for idx, (course_id, course) in enumerate(teacher_courses.items()):
            with cols[idx % 2]:
                render_course_card(course_id, course, lambda cid: set_selected_course_engagement(cid))
        return
    
    # Selected course analytics
    course = teacher_courses.get(selected_course)
    if not course:
        st.error("Course not found")
        if st.button("← Back"):
            st.session_state.selected_course_engagement = None
            st.rerun()
        return
    
    # Back button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.selected_course_engagement = None
            st.rerun()
    with col2:
        st.markdown(f"### 📚 {course.get('name')}")
    
    st.markdown("---")
    
    # Get enrolled students
    student_ids = course.get('enrolled_students', [])
    
    if not student_ids:
        st.info("No students enrolled yet.")
        return
    
    st.markdown(f"### 📊 Engagement Overview ({len(student_ids)} students)")
    
    # Calculate engagement for all students
    student_scores = []
    
    for student_id in student_ids:
        student = storage.get_user(student_id)
        if not student:
            continue
            
        student_actions = logger._get_recent_actions(student_id, limit=2000)
        course_actions = [a for a in student_actions 
                         if a['context'].get('course_id') == selected_course]
        
        if course_actions:
            result = scorer.predict_engagement_score(
                course_actions,
                {'course_id': selected_course, 'user_role': 'student'}
            )
            
            student_scores.append({
                'Student': student.get('full_name', 'Unknown'),
                'Student ID': student_id,
                'Score': result['engagement_score'],
                'Level': result['level'],
                'Actions': result['total_actions'],
                'Confidence': f"{result['confidence']*100:.0f}%"
            })
    
    if not student_scores:
        st.warning("No student activity recorded yet.")
        return
    
    # Create dataframe
    df = pd.DataFrame(student_scores)
    df = df.sort_values('Score', ascending=False)
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_score = df['Score'].mean()
        st.metric("Average Engagement", f"{avg_score:.1f}/100")
    
    with col2:
        high_engagement = len(df[df['Score'] >= 80])
        st.metric("High Engagement", f"{high_engagement} students")
    
    with col3:
        low_engagement = len(df[df['Score'] < 50])
        st.metric("Needs Attention", f"{low_engagement} students")
    
    with col4:
        total_actions = df['Actions'].sum()
        st.metric("Total Actions", total_actions)
    
    st.markdown("---")
    
    # Engagement distribution
    col1, col2 = st.columns(2)
    
    with col1:
        # Bar chart of students by engagement level
        level_counts = df['Level'].value_counts()
        fig = px.bar(
            x=level_counts.index,
            y=level_counts.values,
            labels={'x': 'Engagement Level', 'y': 'Number of Students'},
            title="Students by Engagement Level",
            color=level_counts.values,
            color_continuous_scale='RdYlGn'
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Score distribution histogram
        fig = px.histogram(
            df,
            x='Score',
            nbins=10,
            title="Engagement Score Distribution",
            labels={'Score': 'Engagement Score', 'count': 'Number of Students'}
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # Quiz Performance Section
    st.markdown("---")
    st.markdown("### 📝 Quiz Performance")
    
    # Get all quizzes for this course
    quizzes = storage.get_course_quizzes(selected_course)
    
    if quizzes and len(quizzes) > 0:
        quiz_stats = []
        
        for quiz in quizzes:
            quiz_id = quiz.get('quiz_id')
            quiz_attempts = storage.get_quiz_attempts(quiz_id)
            
            if quiz_attempts:
                scores = [attempt.get('score', 0) for attempt in quiz_attempts]
                avg_score = sum(scores) / len(scores) if scores else 0
                pass_rate = len([s for s in scores if s >= 60]) / len(scores) * 100 if scores else 0
                
                quiz_stats.append({
                    'Quiz': quiz.get('title', 'Untitled')[:30],
                    'Attempts': len(quiz_attempts),
                    'Avg Score': f"{avg_score:.1f}%",
                    'Pass Rate': f"{pass_rate:.1f}%",
                    'Difficulty': quiz.get('difficulty', 'medium').title()
                })
        
        if quiz_stats:
            quiz_df = pd.DataFrame(quiz_stats)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Quizzes", len(quizzes))
            with col2:
                total_attempts = sum([stat['Attempts'] for stat in quiz_stats])
                st.metric("Total Attempts", total_attempts)
            with col3:
                if quiz_stats:
                    avg_pass_rate = sum([float(stat['Pass Rate'].rstrip('%')) for stat in quiz_stats]) / len(quiz_stats)
                    st.metric("Avg Pass Rate", f"{avg_pass_rate:.1f}%")
            
            st.dataframe(quiz_df, use_container_width=True, height=200)
            
            # Quiz performance chart
            fig = px.bar(
                quiz_df,
                x='Quiz',
                y=[float(s.rstrip('%')) for s in quiz_df['Avg Score']],
                title="Average Quiz Scores",
                labels={'y': 'Average Score (%)'},
                color=[float(s.rstrip('%')) for s in quiz_df['Avg Score']],
                color_continuous_scale='RdYlGn'
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No quiz attempts yet. Students haven't taken any quizzes.")
    else:
        st.info("No quizzes created for this course yet. Use the Quiz Generator to create quizzes!")
    
    st.markdown("---")
    
    # Student details table
    st.markdown("### 👥 Student Details")
    st.dataframe(df, use_container_width=True, height=400)
    
    # Download button
    csv = df.to_csv(index=False)
    st.download_button(
        "📥 Download Engagement Report (CSV)",
        data=csv,
        file_name=f"engagement_report_{selected_course}_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )


def set_selected_course_engagement(course_id):
    """Helper to set selected course for engagement analytics"""
    st.session_state.selected_course_engagement = course_id
    st.rerun()


def show_teacher_evaluation_tab(user, storage):
    """Teacher Evaluation - Student feedback and ratings"""
    st.markdown("## 👨‍🏫 Teacher Evaluation")
    st.markdown("Comprehensive feedback and ratings from students")
    
    nlp_service = get_nlp_service()
    
    # Get teacher ID
    if user['role'] == 'teacher':
        teacher_id = user['user_id']
        teacher = storage.get_user(teacher_id)
        st.markdown(f"**Teacher:** {teacher.get('full_name', 'Unknown')}")
    else:  # admin
        all_users = storage.get_all_users()
        teachers = {uid: u for uid, u in all_users.items() if u['role'] == 'teacher'}
        
        if not teachers:
            st.info("No teachers in the system.")
            return
        
        st.markdown("### 👨‍🏫 Select Teacher")
        
        # Teacher selection cards
        teacher_cards = st.columns(min(3, len(teachers)))
        
        for idx, (tid, teacher) in enumerate(list(teachers.items())[:6]):
            with teacher_cards[idx % 3]:
                teacher_name = teacher.get('full_name', teacher['username'])
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    border-radius: 12px;
                    padding: 20px;
                    margin: 10px 0;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                    color: white;
                    text-align: center;
                ">
                    <h4 style="margin: 0;">👨‍🏫 {teacher_name}</h4>
                    <p style="margin: 5px 0; font-size: 12px; opacity: 0.9;">{tid}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"View Evaluation", key=f"teacher_eval_{tid}", use_container_width=True):
                    st.session_state.selected_teacher_eval = tid
                    st.rerun()
        
        if 'selected_teacher_eval' not in st.session_state:
            return
        
        teacher_id = st.session_state.selected_teacher_eval
    
    st.markdown("---")
    
    # Get evaluation data
    eval_data = storage.get_teacher_evaluation(teacher_id)
    teacher_feedback = storage.get_teacher_feedback(teacher_id)
    
    if not eval_data or not teacher_feedback:
        st.info("📊 No feedback data available yet. Students haven't submitted feedback for lectures.")
        return
    
    # Summary metrics
    st.markdown("## 📊 Performance Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Feedback",
            eval_data['total_feedback_count'],
            help="Total feedback submissions"
        )
    
    with col2:
        composite_avg = eval_data['average_ratings']['composite']
        st.metric(
            "Overall Rating",
            f"{composite_avg:.2f}/5.00",
            delta=f"{composite_avg - 3.0:.2f}",
            help="Average rating across all feedback"
        )
    
    with col3:
        sentiment_dist = eval_data['sentiment_distribution']
        positive_pct = (sentiment_dist['positive'] / eval_data['total_feedback_count'] * 100) if eval_data['total_feedback_count'] > 0 else 0
        st.metric(
            "Positive Feedback",
            f"{positive_pct:.1f}%",
            help="Percentage of positive sentiment"
        )
    
    with col4:
        recommendation_rate = sum(1 for fb in teacher_feedback if fb.get('metadata', {}).get('would_recommend', False))
        rec_pct = (recommendation_rate / len(teacher_feedback) * 100) if teacher_feedback else 0
        st.metric(
            "Recommendation Rate",
            f"{rec_pct:.1f}%",
            help="Students who would recommend"
        )
    
    st.markdown("---")
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Radar chart for performance categories
        avg_ratings = eval_data['average_ratings']
        categories = ['Overall', 'Content Quality', 'Clarity', 'Pace', 'Engagement', 'Visual Aids']
        values = [
            avg_ratings.get('overall', 0),
            avg_ratings.get('content_quality', 0),
            avg_ratings.get('clarity', 0),
            avg_ratings.get('pace', 0),
            avg_ratings.get('engagement', 0),
            avg_ratings.get('visual_aids', 0)
        ]
        
        fig = render_radar_chart(categories, values, "Performance Across Categories")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Sentiment pie chart
        labels = ['Positive', 'Neutral', 'Negative']
        values = [
            sentiment_dist.get('positive', 0),
            sentiment_dist.get('neutral', 0),
            sentiment_dist.get('negative', 0)
        ]
        colors = ['#90EE90', '#FFD700', '#FFB6C1']
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            marker=dict(colors=colors),
            hole=0.4,
            textinfo='label+percent'
        )])
        
        fig.update_layout(
            title="Feedback Sentiment Distribution",
            height=400,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent feedback
    st.markdown("---")
    st.markdown("### 💬 Recent Feedback")
    
    # Sort by date
    sorted_feedback = sorted(teacher_feedback, key=lambda x: x.get('created_at', ''), reverse=True)
    
    for feedback in sorted_feedback[:10]:
        sentiment = feedback.get('nlp_analysis', {}).get('sentiment', {})
        sentiment_label = sentiment.get('label', 'neutral')
        sentiment_emoji = {'positive': '😊', 'neutral': '😐', 'negative': '😟'}.get(sentiment_label, '😐')
        
        with st.container():
            col1, col2 = st.columns([1, 5])
            with col1:
                st.markdown(f"## {sentiment_emoji}")
            with col2:
                rating = feedback.get('ratings', {}).get('composite_score', 0)
                st.markdown(f"**Rating:** {'⭐' * int(rating)} ({rating:.1f}/5.0)")
                st.markdown(f"**Comment:** {feedback.get('comment', 'No comment')}")
                st.caption(f"Submitted: {feedback.get('created_at', 'Unknown')[:10]}")
            st.markdown("---")


def show_teaching_analytics():
    """Main unified teaching analytics page"""
    st.title("📊 Teaching Analytics Hub")
    st.markdown("Comprehensive analytics for teaching effectiveness, student engagement, and performance evaluation")
    st.markdown("---")
    
    user = st.session_state.user
    storage = get_storage()
    
    # Check authorization
    if user['role'] not in ['teacher', 'admin']:
        st.error("🚫 Access denied. This page is for teachers and administrators only.")
        return
    
    # Tab navigation
    tabs = st.tabs([
        "📡 Live Tracking",
        "🎯 Teaching Score",
        "📊 Engagement Analytics",
        "👨‍🏫 Teacher Evaluation"
    ])
    
    with tabs[0]:
        show_live_tracking_tab(user, storage)
    
    with tabs[1]:
        show_teaching_score_tab(user, storage)
    
    with tabs[2]:
        show_engagement_analytics_tab(user, storage)
    
    with tabs[3]:
        show_teacher_evaluation_tab(user, storage)
