"""
Smart LMS - Teacher Evaluation Dashboard
Comprehensive analytics and feedback for teacher performance
"""

import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.auth import get_auth
from services.storage import get_storage
from services.nlp import get_nlp_service
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from collections import Counter


def render_rating_gauge(rating: float, title: str):
    """Render a gauge chart for rating"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=rating,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 16}},
        delta={'reference': 3.0, 'increasing': {'color': "green"}},
        gauge={
            'axis': {'range': [None, 5], 'tickwidth': 1},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 2], 'color': "#ffcccb"},
                {'range': [2, 3.5], 'color': "#ffffcc"},
                {'range': [3.5, 5], 'color': "#90EE90"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 4.0
            }
        }
    ))
    
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
    return fig


def render_sentiment_pie(sentiment_dist: dict):
    """Render sentiment distribution pie chart"""
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
        height=350,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig


def render_ratings_radar(avg_ratings: dict):
    """Render radar chart for different rating categories"""
    categories = ['Overall', 'Content Quality', 'Clarity', 'Pace', 'Engagement', 'Visual Aids']
    values = [
        avg_ratings.get('overall', 0),
        avg_ratings.get('content_quality', 0),
        avg_ratings.get('clarity', 0),
        avg_ratings.get('pace', 0),
        avg_ratings.get('engagement', 0),
        avg_ratings.get('visual_aids', 0)
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Current Ratings',
        line=dict(color='#4169E1')
    ))
    
    # Add benchmark line
    fig.add_trace(go.Scatterpolar(
        r=[4.0] * len(categories),
        theta=categories,
        fill='toself',
        name='Target (4.0)',
        line=dict(color='green', dash='dash'),
        opacity=0.3
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 5])
        ),
        showlegend=True,
        title="Performance Across Categories",
        height=400
    )
    return fig


def render_feedback_timeline(feedbacks: list):
    """Render feedback timeline with sentiment"""
    if not feedbacks:
        return None
    
    # Sort by date
    sorted_feedback = sorted(feedbacks, key=lambda x: x.get('created_at', ''))
    
    dates = []
    ratings = []
    sentiments = []
    
    for fb in sorted_feedback:
        dates.append(fb.get('created_at', '')[:10])
        ratings.append(fb.get('ratings', {}).get('composite_score', 0))
        
        sentiment = fb.get('nlp_analysis', {}).get('sentiment', {})
        sentiments.append(sentiment.get('compound', 0))
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=ratings,
        mode='lines+markers',
        name='Composite Rating',
        line=dict(color='blue', width=2),
        yaxis='y1'
    ))
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=sentiments,
        mode='lines+markers',
        name='Sentiment Score',
        line=dict(color='green', width=2, dash='dash'),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title="Feedback Trends Over Time",
        xaxis=dict(title="Date"),
        yaxis=dict(title="Rating (1-5)", side='left', range=[0, 5]),
        yaxis2=dict(title="Sentiment (-1 to 1)", side='right', overlaying='y', range=[-1, 1]),
        height=350,
        hovermode='x unified'
    )
    
    return fig


def show_teacher_evaluation():
    """Display comprehensive teacher evaluation dashboard"""
    st.title("👨‍🏫 Teacher Evaluation Dashboard")
    st.markdown("### Comprehensive Analytics and Student Feedback")
    
    storage = get_storage()
    nlp_service = get_nlp_service()
    user = st.session_state.user
    
    # Determine which teacher to show
    if user['role'] == 'admin':
        # Admin can view all teachers
        all_users = storage.get_all_users()
        teachers = {uid: u for uid, u in all_users.items() if u['role'] == 'teacher'}
        
        if not teachers:
            st.info("No teachers in the system yet.")
            return
        
        teacher_options = {uid: u.get('full_name', u['username']) for uid, u in teachers.items()}
        selected_teacher_id = st.selectbox(
            "Select Teacher",
            options=list(teacher_options.keys()),
            format_func=lambda x: teacher_options[x],
            key="teacher_select"
        )
    else:
        # Teachers view their own evaluation
        selected_teacher_id = user['user_id']
        teacher = storage.get_user(selected_teacher_id)
        st.markdown(f"**Teacher:** {teacher.get('full_name', 'Unknown')}")
    
    st.markdown("---")
    
    # Get teacher evaluation data
    eval_data = storage.get_teacher_evaluation(selected_teacher_id)
    teacher_feedback = storage.get_teacher_feedback(selected_teacher_id)
    
    if not eval_data or not teacher_feedback:
        st.info("📊 No feedback data available yet. Students haven't submitted feedback for your lectures.")
        return
    
    # Summary Statistics
    st.markdown("## 📊 Overall Performance Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Feedback",
            eval_data['total_feedback_count'],
            help="Total number of feedback submissions received"
        )
    
    with col2:
        composite_avg = eval_data['average_ratings']['composite']
        st.metric(
            "Overall Rating",
            f"{composite_avg:.2f} / 5.00",
            delta=f"{composite_avg - 3.0:.2f}" if composite_avg >= 3.0 else f"{composite_avg - 3.0:.2f}",
            help="Average composite rating across all feedback"
        )
    
    with col3:
        sentiment_dist = eval_data['sentiment_distribution']
        positive_pct = (sentiment_dist['positive'] / eval_data['total_feedback_count'] * 100) if eval_data['total_feedback_count'] > 0 else 0
        st.metric(
            "Positive Feedback",
            f"{positive_pct:.1f}%",
            help="Percentage of feedback with positive sentiment"
        )
    
    with col4:
        recommendation_rate = sum(1 for fb in teacher_feedback if fb.get('metadata', {}).get('would_recommend', False))
        rec_pct = (recommendation_rate / len(teacher_feedback) * 100) if teacher_feedback else 0
        st.metric(
            "Recommendation Rate",
            f"{rec_pct:.1f}%",
            help="Students who would recommend this teacher"
        )
    
    st.markdown("---")
    
    # Detailed Ratings
    st.markdown("## 📈 Detailed Performance Metrics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Radar chart
        fig_radar = render_ratings_radar(eval_data['average_ratings'])
        st.plotly_chart(fig_radar, use_container_width=True)
    
    with col2:
        # Sentiment pie chart
        fig_sentiment = render_sentiment_pie(eval_data['sentiment_distribution'])
        st.plotly_chart(fig_sentiment, use_container_width=True)
    
    # Individual Rating Gauges
    st.markdown("### 🎯 Rating Breakdown")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fig1 = render_rating_gauge(eval_data['average_ratings']['overall'], "Overall Rating")
        st.plotly_chart(fig1, use_container_width=True)
        
        fig2 = render_rating_gauge(eval_data['average_ratings']['clarity'], "Clarity")
        st.plotly_chart(fig2, use_container_width=True)
    
    with col2:
        fig3 = render_rating_gauge(eval_data['average_ratings']['content_quality'], "Content Quality")
        st.plotly_chart(fig3, use_container_width=True)
        
        fig4 = render_rating_gauge(eval_data['average_ratings']['engagement'], "Engagement")
        st.plotly_chart(fig4, use_container_width=True)
    
    with col3:
        fig5 = render_rating_gauge(eval_data['average_ratings']['pace'], "Teaching Pace")
        st.plotly_chart(fig5, use_container_width=True)
        
        fig6 = render_rating_gauge(eval_data['average_ratings']['visual_aids'], "Visual Aids")
        st.plotly_chart(fig6, use_container_width=True)
    
    st.markdown("---")
    
    # Feedback Timeline
    st.markdown("## 📅 Performance Trends")
    fig_timeline = render_feedback_timeline(teacher_feedback)
    if fig_timeline:
        st.plotly_chart(fig_timeline, use_container_width=True)
    
    st.markdown("---")
    
    # NLP Analysis
    st.markdown("## 🤖 AI-Powered Feedback Analysis")
    
    # Aggregate NLP analysis
    nlp_aggregate = nlp_service.analyze_feedback_aggregate(teacher_feedback)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔑 Most Common Keywords")
        if nlp_aggregate['top_keywords']:
            keywords_df = pd.DataFrame({
                'Keyword': nlp_aggregate['top_keywords'][:10],
                'Rank': range(1, min(11, len(nlp_aggregate['top_keywords']) + 1))
            })
            st.dataframe(keywords_df, use_container_width=True, hide_index=True)
        else:
            st.info("No keywords extracted yet")
    
    with col2:
        st.markdown("### 🎭 Common Themes")
        if nlp_aggregate['common_themes']:
            themes_df = pd.DataFrame({
                'Theme': [t.replace('_', ' ').title() for t in nlp_aggregate['common_themes'][:10]],
                'Rank': range(1, min(11, len(nlp_aggregate['common_themes']) + 1))
            })
            st.dataframe(themes_df, use_container_width=True, hide_index=True)
        else:
            st.info("No themes detected yet")
    
    st.markdown("---")
    
    # Course-wise breakdown
    st.markdown("## 📚 Performance by Course")
    
    course_data = []
    for course_id, course_eval in eval_data['feedback_by_course'].items():
        course = storage.get_course(course_id)
        if course:
            course_data.append({
                'Course': course['name'],
                'Feedback Count': course_eval['count'],
                'Average Rating': f"{course_eval['avg_composite']:.2f}"
            })
    
    if course_data:
        df_courses = pd.DataFrame(course_data)
        st.dataframe(df_courses, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Recent Feedback Details
    st.markdown("## 💬 Recent Student Feedback")
    
    # Sort by date
    recent_feedback = sorted(teacher_feedback, key=lambda x: x.get('created_at', ''), reverse=True)[:10]
    
    for fb in recent_feedback:
        # Get lecture and course info
        lecture = storage.get_lecture(fb.get('lecture_id', ''))
        course = storage.get_course(fb.get('course_id', ''))
        
        lecture_title = lecture.get('title', 'Unknown Lecture') if lecture else 'Unknown Lecture'
        course_name = course.get('name', 'Unknown Course') if course else 'Unknown Course'
        
        # Sentiment color
        sentiment = fb.get('nlp_analysis', {}).get('sentiment', {})
        sentiment_label = sentiment.get('label', 'neutral')
        sentiment_color = {
            'positive': '🟢',
            'neutral': '🟡',
            'negative': '🔴'
        }.get(sentiment_label, '⚪')
        
        with st.expander(f"{sentiment_color} {lecture_title} - {course_name} | {fb.get('created_at', '')[:10]}"):
            ratings = fb.get('ratings', {})
            written = fb.get('written_feedback', {})
            metadata = fb.get('metadata', {})
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Overall Rating", f"{ratings.get('overall', 0)}/5")
            with col2:
                st.metric("Composite Score", f"{ratings.get('composite_score', 0):.2f}/5")
            with col3:
                st.metric("Sentiment", sentiment_label.title())
            
            st.markdown("---")
            
            if written.get('strengths'):
                st.markdown("**✅ Strengths:**")
                st.info(written['strengths'])
            
            if written.get('improvements'):
                st.markdown("**🔧 Areas for Improvement:**")
                st.warning(written['improvements'])
            
            if written.get('additional_comments'):
                st.markdown("**💬 Additional Comments:**")
                st.markdown(written['additional_comments'])
            
            st.caption(f"Difficulty Level: {metadata.get('difficulty_level', 'N/A')} | Would Recommend: {'✅ Yes' if metadata.get('would_recommend') else '❌ No'}")


def main():
    """Main teacher evaluation page"""
    # Check authentication
    auth = get_auth()
    
    # Allow teachers and admins
    if 'user' not in st.session_state:
        st.error("Please login first")
        return
    
    user = st.session_state.user
    if user['role'] not in ['teacher', 'admin']:
        st.error("Access denied. Teachers and admins only.")
        return
    
    show_teacher_evaluation()


if __name__ == "__main__":
    main()
