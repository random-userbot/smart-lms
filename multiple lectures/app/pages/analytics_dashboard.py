"""
Analytics Dashboard for Teachers
Shows teaching scores, course analytics, and actionable recommendations
Includes AI Chatbot for explainable insights
"""

import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.auth import get_auth
from services.storage import get_storage
from services.activity_tracker import get_activity_tracker
from services.teaching_score import get_teaching_score_calculator
from services.ai_explainer_bot import get_explainer_bot
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from collections import defaultdict


def render_score_gauge(score: float, title: str):
    """Render a gauge chart for scores"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 20}},
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
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig


def show_component_scores(components: dict):
    """Show breakdown of score components"""
    st.subheader("📊 Score Components Breakdown")
    
    # Create bar chart
    component_names = []
    component_scores = []
    component_contributions = []
    
    for name, data in components.items():
        component_names.append(name.replace('_', ' ').title())
        component_scores.append(data['score'])
        component_contributions.append(data['contribution'])
    
    # Create two columns for charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Scores chart
        fig1 = go.Figure(data=[
            go.Bar(
                x=component_scores,
                y=component_names,
                orientation='h',
                marker=dict(
                    color=component_scores,
                    colorscale='RdYlGn',
                    showscale=True,
                    cmin=0,
                    cmax=100
                ),
                text=[f"{s:.1f}" for s in component_scores],
                textposition='auto',
            )
        ])
        
        fig1.update_layout(
            title="Component Scores",
            xaxis_title="Score (0-100)",
            yaxis_title="Component",
            height=400,
            margin=dict(l=150)
        )
        
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Contributions chart
        fig2 = go.Figure(data=[
            go.Bar(
                x=component_contributions,
                y=component_names,
                orientation='h',
                marker=dict(color='#1f77b4'),
                text=[f"{c:.1f}" for c in component_contributions],
                textposition='auto',
            )
        ])
        
        fig2.update_layout(
            title="Weighted Contributions",
            xaxis_title="Contribution to Overall Score",
            yaxis_title="Component",
            height=400,
            margin=dict(l=150)
        )
        
        st.plotly_chart(fig2, use_container_width=True)


def show_component_details(components: dict):
    """Show detailed explanations for each component"""
    st.subheader("🔍 Detailed Component Analysis")
    
    for component_name, data in components.items():
        with st.expander(f"📌 {component_name.replace('_', ' ').title()} - Score: {data['score']:.1f}/100"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Component Score", f"{data['score']:.1f}/100")
            
            with col2:
                st.metric("Weight", f"{data['weight']*100:.0f}%")
            
            with col3:
                st.metric("Contribution", f"{data['contribution']:.1f}")
            
            st.markdown("---")
            st.markdown("**📝 Explanation:**")
            
            explanation = data['explanation']
            for key, value in explanation.items():
                st.write(f"- **{key.replace('_', ' ').title()}:** {value}")


def generate_recommendations(score_data: dict) -> list:
    """Generate actionable recommendations based on score data"""
    recommendations = []
    components = score_data['components']
    
    # Check engagement
    if components['engagement']['score'] < 60:
        recommendations.append({
            'priority': 'High',
            'area': 'Student Engagement',
            'issue': 'Low student engagement detected',
            'recommendation': 'Consider adding more interactive elements to your lectures, such as live polls, Q&A sessions, or discussion forums.',
            'icon': '📉'
        })
    
    # Check quiz performance
    if components['quiz_performance']['score'] < 60:
        recommendations.append({
            'priority': 'High',
            'area': 'Quiz Performance',
            'issue': 'Students struggling with assessments',
            'recommendation': 'Review quiz difficulty, provide more practice materials, or offer additional tutoring sessions. Consider breaking complex topics into smaller units.',
            'icon': '📝'
        })
    
    # Check attendance
    if components['attendance']['score'] < 70:
        recommendations.append({
            'priority': 'Medium',
            'area': 'Attendance',
            'issue': 'Low attendance rates',
            'recommendation': 'Send regular reminders, make lectures more engaging, or consider flexible attendance policies. Check if technical issues are preventing access.',
            'icon': '✋'
        })
    
    # Check lecture completion
    if components['lecture_completion']['score'] < 70:
        recommendations.append({
            'priority': 'Medium',
            'area': 'Lecture Completion',
            'issue': 'Students not completing lectures',
            'recommendation': 'Ensure lectures are appropriately paced and not too long. Add chapter markers and summaries. Consider breaking long lectures into shorter segments.',
            'icon': '⏹️'
        })
    
    # Check sentiment
    if components['sentiment']['score'] < 60:
        recommendations.append({
            'priority': 'High',
            'area': 'Student Sentiment',
            'issue': 'Negative feedback patterns detected',
            'recommendation': 'Review student feedback carefully. Address common complaints, improve communication, and be more responsive to student needs.',
            'icon': '😟'
        })
    
    # Check resource usage
    if components['resource_usage']['score'] < 50:
        recommendations.append({
            'priority': 'Low',
            'area': 'Resource Usage',
            'issue': 'Low engagement with course materials',
            'recommendation': 'Promote course materials more actively. Ensure resources are easily accessible and well-organized. Add more diverse materials (videos, PDFs, interactive content).',
            'icon': '📚'
        })
    
    # Check activity patterns
    if components['activity_patterns']['score'] < 60:
        recommendations.append({
            'priority': 'Medium',
            'area': 'Activity Patterns',
            'issue': 'Inconsistent student activity',
            'recommendation': 'Establish regular weekly rhythms (e.g., Monday lectures, Wednesday quizzes). Send consistent reminders and maintain a predictable schedule.',
            'icon': '📅'
        })
    
    # Positive reinforcements
    if score_data['overall_score'] >= 80:
        recommendations.append({
            'priority': 'Info',
            'area': 'Overall Performance',
            'issue': 'Excellent teaching performance!',
            'recommendation': 'Keep up the great work! Consider sharing your successful strategies with other teachers.',
            'icon': '🌟'
        })
    
    return recommendations


def show_recommendations(recommendations: list):
    """Display actionable recommendations"""
    st.subheader("💡 Actionable Recommendations")
    
    if not recommendations:
        st.success("✨ Everything looks great! No specific recommendations at this time.")
        return
    
    # Group by priority
    high_priority = [r for r in recommendations if r['priority'] == 'High']
    medium_priority = [r for r in recommendations if r['priority'] == 'Medium']
    low_priority = [r for r in recommendations if r['priority'] == 'Low']
    info_items = [r for r in recommendations if r['priority'] == 'Info']
    
    # Show high priority first
    if high_priority:
        st.markdown("### 🔴 High Priority")
        for rec in high_priority:
            with st.expander(f"{rec['icon']} {rec['area']} - {rec['issue']}"):
                st.warning(f"**Issue:** {rec['issue']}")
                st.info(f"**Recommendation:** {rec['recommendation']}")
    
    if medium_priority:
        st.markdown("### 🟡 Medium Priority")
        for rec in medium_priority:
            with st.expander(f"{rec['icon']} {rec['area']} - {rec['issue']}"):
                st.warning(f"**Issue:** {rec['issue']}")
                st.info(f"**Recommendation:** {rec['recommendation']}")
    
    if low_priority:
        st.markdown("### 🟢 Low Priority")
        for rec in low_priority:
            with st.expander(f"{rec['icon']} {rec['area']} - {rec['issue']}"):
                st.info(f"**Issue:** {rec['issue']}")
                st.info(f"**Recommendation:** {rec['recommendation']}")
    
    if info_items:
        for rec in info_items:
            st.success(f"{rec['icon']} **{rec['area']}:** {rec['recommendation']}")


def calculate_course_score(course_id: str, teacher_id: str) -> dict:
    """Calculate teaching score for a course"""
    storage = get_storage()
    tracker = get_activity_tracker()
    calculator = get_teaching_score_calculator()
    
    # Get course data
    course = storage.get_course(course_id)
    if not course:
        return None
    
    # Get enrolled students
    enrolled_students = course.get('enrolled_students', [])
    
    # Get activities
    activities = tracker.get_course_activities(course_id, teacher_id=None)
    
    # Get grades
    all_grades = []
    for student_id in enrolled_students:
        student_grades = storage.get_student_grades(student_id)
        if student_grades:
            # Filter by course
            for quiz in student_grades.get('quizzes', []):
                if quiz.get('course_id') == course_id:
                    all_grades.append({**quiz, 'assessment_type': 'quiz', 'student_id': student_id})
    
    # Get attendance (mock for now - implement actual attendance retrieval)
    attendance_records = []
    
    # Get feedback analysis (mock for now - implement NLP analysis)
    feedback_analysis = {
        'positive': 5,
        'neutral': 3,
        'negative': 1
    }
    
    # Get lectures
    lectures = storage.get_course_lectures(course_id)
    total_lectures = len(lectures)
    
    # Count materials (mock for now)
    total_materials = 10  # Implement actual count
    
    # Calculate score
    score_data = calculator.calculate_overall_teaching_score(
        activities=activities,
        grades=all_grades,
        attendance_records=attendance_records,
        feedback_analysis=feedback_analysis,
        course_students=enrolled_students,
        total_lectures=total_lectures,
        total_materials=total_materials,
        course_duration_days=60
    )
    
    # Save score
    calculator.save_teaching_score(teacher_id, course_id, score_data)
    
    return score_data


def show_course_analytics():
    """Show analytics for selected course"""
    user = st.session_state.user
    storage = get_storage()
    
    # Get teacher's courses
    courses = storage.get_all_courses(teacher_id=user['user_id'])
    
    if not courses:
        st.info("📚 No courses found. Create a course first.")
        return
    
    # Course selection
    course_options = {cid: c['name'] for cid, c in courses.items()}
    selected_course = st.selectbox(
        "Select Course",
        options=list(course_options.keys()),
        format_func=lambda x: course_options[x]
    )
    
    if not selected_course:
        return
    
    st.markdown("---")
    
    # Calculate/load teaching score
    with st.spinner("📊 Calculating teaching score..."):
        score_data = calculate_course_score(selected_course, user['user_id'])
    
    if not score_data:
        st.error("Failed to calculate teaching score.")
        return
    
    # Display overall score
    st.markdown("### 🎯 Overall Teaching Score")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        # Gauge chart
        fig = render_score_gauge(score_data['overall_score'], "Teaching Score")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
        st.metric("Grade", score_data['grade'], delta=None)
        st.metric("Calculated", datetime.fromisoformat(score_data['calculated_at']).strftime("%Y-%m-%d"))
    
    with col3:
        st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
        # Interpretation
        if score_data['overall_score'] >= 90:
            st.success("🌟 Excellent!")
        elif score_data['overall_score'] >= 80:
            st.success("✅ Very Good")
        elif score_data['overall_score'] >= 70:
            st.info("👍 Good")
        elif score_data['overall_score'] >= 60:
            st.warning("⚠️ Needs Improvement")
        else:
            st.error("❌ Poor")
    
    st.markdown("---")
    
    # Show component scores
    show_component_scores(score_data['components'])
    
    st.markdown("---")
    
    # Show detailed analysis
    show_component_details(score_data['components'])
    
    st.markdown("---")
    
    # Generate and show recommendations
    recommendations = generate_recommendations(score_data)
    show_recommendations(recommendations)


def show_overall_analytics():
    """Show overall analytics across all courses"""
    user = st.session_state.user
    storage = get_storage()
    calculator = get_teaching_score_calculator()
    
    # Get all teacher scores
    teacher_scores = calculator.get_teacher_scores(user['user_id'])
    
    if not teacher_scores:
        st.info("📊 No analytics available yet. Teaching scores will appear after course activities are tracked.")
        return
    
    st.markdown("### 📈 Overall Performance")
    
    # Calculate average score
    if teacher_scores:
        avg_score = sum(s['overall_score'] for s in teacher_scores) / len(teacher_scores)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Average Teaching Score", f"{avg_score:.1f}/100")
        
        with col2:
            st.metric("Courses Evaluated", len(teacher_scores))
        
        with col3:
            latest = max(teacher_scores, key=lambda x: x['calculated_at'])
            st.metric("Latest Evaluation", datetime.fromisoformat(latest['calculated_at']).strftime("%Y-%m-%d"))
        
        st.markdown("---")
        
        # Show trend over time
        st.markdown("### 📊 Score Trends")
        
        # Prepare data for chart
        courses = storage.get_all_courses(teacher_id=user['user_id'])
        course_names = {cid: c['name'] for cid, c in courses.items()}
        
        chart_data = []
        for score in sorted(teacher_scores, key=lambda x: x['calculated_at']):
            chart_data.append({
                'Date': datetime.fromisoformat(score['calculated_at']).strftime("%Y-%m-%d"),
                'Score': score['overall_score'],
                'Course': course_names.get(score['course_id'], 'Unknown')
            })
        
        if chart_data:
            import pandas as pd
            df = pd.DataFrame(chart_data)
            
            fig = px.line(df, x='Date', y='Score', color='Course', markers=True,
                         title="Teaching Score Trends Over Time")
            fig.update_layout(yaxis_range=[0, 100])
            st.plotly_chart(fig, use_container_width=True)


def main():
    """Main analytics dashboard"""
    # Check authentication
    auth = get_auth()
    user = st.session_state.get('user')
    
    if not user:
        st.error("🚫 Please login to access this page.")
        return
    
    if user['role'] != 'teacher':
        st.error("🚫 Access Denied. This page is for teachers only.")
        return
    
    st.title("📊 Analytics & Teaching Score Dashboard")
    st.markdown("View your teaching scores, course analytics, and get actionable recommendations.")
    st.markdown("---")
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📚 Course Analytics", "📈 Overall Performance", "🤖 AI Insights"])
    
    with tab1:
        show_course_analytics()
    
    with tab2:
        show_overall_analytics()
    
    with tab3:
        show_ai_chatbot()


def show_ai_chatbot():
    """Show AI chatbot interface for explaining scores"""
    st.subheader("🤖 AI Explanation Chatbot")
    st.markdown("Ask questions about your teaching score and get data-backed explanations.")
    
    user = st.session_state.user
    storage = get_storage()
    calculator = get_teaching_score_calculator()
    bot = get_explainer_bot()
    
    # Check bot availability
    if not bot.is_available():
        st.error("❌ AI Chatbot is not available. Please configure GROQ_API_KEY in your environment or config.yaml.")
        st.info("💡 To get a free API key, visit: https://console.groq.com/keys")
        return
    
    # Get teacher's courses
    courses = storage.get_all_courses(teacher_id=user['user_id'])
    
    if not courses:
        st.info("📚 No courses found. Create a course first to see analytics.")
        return
    
    # Course selection
    course_options = {cid: c['name'] for cid, c in courses.items()}
    selected_course = st.selectbox(
        "Select Course for AI Insights",
        options=list(course_options.keys()),
        format_func=lambda x: course_options[x],
        key='ai_course_select'
    )
    
    if not selected_course:
        return
    
    # Get score data
    score_data = calculator.get_course_score(selected_course)
    
    if not score_data:
        st.warning("⚠️ No teaching score calculated for this course yet. Check the Course Analytics tab.")
        return
    
    # Initialize conversation history in session state
    if 'chatbot_history' not in st.session_state:
        st.session_state.chatbot_history = []
    
    # Pre-defined options
    st.markdown("### 💬 Quick Questions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Explain My Score", use_container_width=True):
            with st.spinner("🤖 Generating explanation..."):
                explanation = bot.explain_score(score_data)
                st.session_state.chatbot_history.append({
                    "role": "assistant",
                    "content": explanation,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })
                st.rerun()
    
    with col2:
        if st.button("💡 Get Improvement Plan", use_container_width=True):
            with st.spinner("🤖 Creating improvement plan..."):
                plan = bot.generate_improvement_plan(score_data)
                st.session_state.chatbot_history.append({
                    "role": "assistant",
                    "content": plan,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })
                st.rerun()
    
    with col3:
        if st.button("📈 Compare Benchmarks", use_container_width=True):
            with st.spinner("🤖 Analyzing benchmarks..."):
                comparison = bot.compare_with_benchmarks(score_data)
                st.session_state.chatbot_history.append({
                    "role": "assistant",
                    "content": comparison,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })
                st.rerun()
    
    st.markdown("---")
    
    # Display conversation history
    st.markdown("### 💭 Conversation")
    
    if st.session_state.chatbot_history:
        for idx, message in enumerate(st.session_state.chatbot_history):
            if message['role'] == 'user':
                st.markdown(f"""
                <div style="
                    background: #e3f2fd;
                    border-left: 4px solid #2196f3;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 5px;
                ">
                    <strong>🧑‍🏫 You ({message['timestamp']}):</strong><br>
                    {message['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="
                    background: #f5f5f5;
                    border-left: 4px solid #4caf50;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 5px;
                ">
                    <strong>🤖 AI Assistant ({message['timestamp']}):</strong><br>
                    {message['content']}
                </div>
                """, unsafe_allow_html=True)
        
        # Clear conversation button
        if st.button("🗑️ Clear Conversation"):
            st.session_state.chatbot_history = []
            st.rerun()
    else:
        st.info("👋 Start by clicking one of the quick questions above, or ask your own question below!")
    
    # Custom question input
    st.markdown("---")
    st.markdown("### ✍️ Ask Your Own Question")
    
    with st.form("chatbot_form", clear_on_submit=True):
        user_question = st.text_area(
            "Type your question here:",
            placeholder="e.g., Why is my quiz performance score low? How can I improve student engagement?",
            height=100
        )
        
        col1, col2 = st.columns([4, 1])
        with col2:
            submit = st.form_submit_button("Send 📤", use_container_width=True, type="primary")
        
        if submit and user_question:
            # Add user question to history
            st.session_state.chatbot_history.append({
                "role": "user",
                "content": user_question,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            
            # Get tracker data for additional context
            tracker = get_activity_tracker()
            activities = tracker.get_course_activities(selected_course)
            activity_summary = tracker.get_statistics(course_id=selected_course)
            
            # Get AI response
            with st.spinner("🤖 Thinking..."):
                # Build conversation history for context
                conv_history = []
                for msg in st.session_state.chatbot_history[:-1]:  # Exclude the just-added user message
                    conv_history.append({
                        "role": msg['role'],
                        "content": msg['content']
                    })
                
                answer = bot.answer_question(
                    question=user_question,
                    score_data=score_data,
                    activity_summary=activity_summary,
                    conversation_history=conv_history
                )
                
                st.session_state.chatbot_history.append({
                    "role": "assistant",
                    "content": answer,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })
            
            st.rerun()


if __name__ == "__main__":
    main()
