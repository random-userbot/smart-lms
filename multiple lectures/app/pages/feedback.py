

import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.auth import get_auth
from services.storage import get_storage
from services.nlp import get_nlp_service
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime


def show_feedback_analytics():
    """Display feedback analytics with NLP insights for teachers"""
    st.title("💬 Student Feedback Analytics")
    st.markdown("View and analyze student feedback with sentiment analysis")
    
    storage = get_storage()
    nlp_service = get_nlp_service()
    user = st.session_state.user
    
    # Get teacher's courses
    courses = storage.get_all_courses(teacher_id=user['user_id'])
    
    if not courses:
        st.info("📝 No courses assigned yet. Contact admin to create courses.")
        return
    
    # Course selection
    course_options = {cid: c['name'] for cid, c in courses.items()}
    
    selected_course = st.selectbox(
        "Select Course",
        options=list(course_options.keys()),
        format_func=lambda x: course_options[x],
        key='feedback_course_selector'
    )
    
    if not selected_course:
        return
    
    course = courses[selected_course]
    
    # Get all lectures for this course
    lectures = storage.get_course_lectures(selected_course)
    
    if not lectures:
        st.info("📝 No lectures available in this course.")
        return
    
    # Lecture selection
    lecture_options = {lec['lecture_id']: lec['title'] for lec in lectures}
    
    selected_lecture_id = st.selectbox(
        "Select Lecture (or 'All Lectures')",
        options=['all'] + list(lecture_options.keys()),
        format_func=lambda x: 'All Lectures' if x == 'all' else lecture_options[x],
        key='feedback_lecture_selector'
    )
    
    # Get feedback
    if selected_lecture_id == 'all':
        all_feedback = []
        for lecture in lectures:
            feedback = storage.get_feedback(lecture_id=lecture['lecture_id'])
            all_feedback.extend(feedback)
    else:
        all_feedback = storage.get_feedback(lecture_id=selected_lecture_id)
    
    if not all_feedback:
        st.info("📝 No feedback received yet for this selection.")
        return
    
    # Display statistics
    st.markdown("---")
    st.markdown("### 📊 Feedback Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_feedback = len(all_feedback)
    avg_rating = sum(f['rating'] for f in all_feedback) / total_feedback if all_feedback else 0
    
    with col1:
        st.metric("Total Feedback", total_feedback)
    
    with col2:
        st.metric("Average Rating", f"{avg_rating:.2f}/5.0")
    
    # Sentiment analysis
    sentiments = [f.get('sentiment', {}) for f in all_feedback]
    sentiment_labels = [s.get('label', 'neutral') for s in sentiments if s]
    
    positive_count = sum(1 for label in sentiment_labels if label == 'positive')
    negative_count = sum(1 for label in sentiment_labels if label == 'negative')
    neutral_count = sum(1 for label in sentiment_labels if label == 'neutral')
    
    with col3:
        st.metric("😊 Positive", positive_count)
    
    with col4:
        st.metric("😟 Negative", negative_count)
    
    # Sentiment distribution chart
    st.markdown("---")
    st.markdown("### 📈 Sentiment Distribution")
    
    if sentiment_labels:
        sentiment_df = pd.DataFrame({
            'Sentiment': sentiment_labels
        })
        
        sentiment_counts = sentiment_df['Sentiment'].value_counts()
        
        fig = px.pie(
            values=sentiment_counts.values,
            names=sentiment_counts.index,
            title="Feedback Sentiment Distribution",
            color_discrete_map={
                'positive': '#2ecc71',
                'neutral': '#95a5a6',
                'negative': '#e74c3c'
            }
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    # Rating distribution
    st.markdown("---")
    st.markdown("### ⭐ Rating Distribution")
    
    ratings = [f['rating'] for f in all_feedback]
    rating_counts = pd.Series(ratings).value_counts().sort_index()
    
    fig = px.bar(
        x=rating_counts.index,
        y=rating_counts.values,
        labels={'x': 'Rating', 'y': 'Count'},
        title="Feedback Rating Distribution",
        color=rating_counts.values,
        color_continuous_scale='YlOrRd'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Sentiment trend over time
    if len(all_feedback) > 1:
        st.markdown("---")
        st.markdown("### 📉 Sentiment Trend")
        
        # Sort by date
        sorted_feedback = sorted(all_feedback, key=lambda x: x.get('created_at', ''))
        
        dates = []
        compound_scores = []
        
        for feedback in sorted_feedback:
            sentiment = feedback.get('sentiment', {})
            if sentiment and 'compound' in sentiment:
                dates.append(feedback.get('created_at', '')[:10])  # Just date part
                compound_scores.append(sentiment['compound'])
        
        if dates and compound_scores:
            trend_df = pd.DataFrame({
                'Date': dates,
                'Sentiment Score': compound_scores
            })
            
            # Aggregate by date if multiple per day
            daily_avg = trend_df.groupby('Date')['Sentiment Score'].mean().reset_index()
            
            fig = px.line(
                daily_avg,
                x='Date',
                y='Sentiment Score',
                title="Average Sentiment Over Time",
                markers=True
            )
            fig.add_hline(y=0.05, line_dash="dash", line_color="green", 
                         annotation_text="Positive Threshold")
            fig.add_hline(y=-0.05, line_dash="dash", line_color="red", 
                         annotation_text="Negative Threshold")
            fig.update_layout(yaxis_range=[-1, 1])
            st.plotly_chart(fig, use_container_width=True)
    
    # Topic extraction
    st.markdown("---")
    st.markdown("### 🔍 Key Topics")
    
    feedback_texts = [f['text'] for f in all_feedback if f.get('text')]
    
    if feedback_texts:
        try:
            topics = nlp_service.extract_topics(feedback_texts, top_n=5)
            
            if topics:
                st.markdown("**Most mentioned topics:**")
                for i, topic in enumerate(topics, 1):
                    st.markdown(f"{i}. **{topic}**")
            else:
                st.info("Not enough feedback data to extract topics.")
        except Exception as e:
            st.warning(f"Could not extract topics: {str(e)}")
    
    # Detailed feedback list
    st.markdown("---")
    st.markdown("### 📋 Detailed Feedback")
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        filter_sentiment = st.selectbox(
            "Filter by Sentiment",
            options=['All', 'Positive', 'Neutral', 'Negative'],
            key='sentiment_filter'
        )
    
    with col2:
        min_rating = st.slider("Minimum Rating", 1, 5, 1, key='min_rating_filter')
    
    # Apply filters
    filtered_feedback = all_feedback.copy()
    
    if filter_sentiment != 'All':
        filter_sentiment_lower = filter_sentiment.lower()
        filtered_feedback = [
            f for f in filtered_feedback
            if f.get('sentiment', {}).get('label') == filter_sentiment_lower
        ]
    
    filtered_feedback = [f for f in filtered_feedback if f['rating'] >= min_rating]
    
    # Display feedback
    if filtered_feedback:
        for feedback in filtered_feedback:
            sentiment = feedback.get('sentiment', {})
            sentiment_label = sentiment.get('label', 'neutral')
            
            # Get student name
            student = storage.get_user(feedback['student_id'])
            student_name = student['full_name'] if student else feedback['student_id']
            
            # Get lecture title
            lecture = storage.get_lecture(feedback['lecture_id'])
            lecture_title = lecture['title'] if lecture else feedback['lecture_id']
            
            # Sentiment color
            sentiment_color = {
                'positive': '🟢',
                'neutral': '🟡',
                'negative': '🔴'
            }.get(sentiment_label, '⚪')
            
            with st.expander(
                f"{sentiment_color} {lecture_title} - {student_name} | Rating: {feedback['rating']}/5 | Sentiment: {sentiment_label.capitalize()}"
            ):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Feedback:**")
                    st.write(feedback['text'])
                
                with col2:
                    st.markdown("**Details:**")
                    st.write(f"**Date:** {feedback.get('created_at', 'Unknown')[:10]}")
                    st.write(f"**Rating:** {feedback['rating']}/5")
                    
                    if sentiment:
                        st.write(f"**Sentiment:** {sentiment_label.capitalize()}")
                        if 'compound' in sentiment:
                            st.write(f"**Compound Score:** {sentiment['compound']:.3f}")
                        if 'positive' in sentiment:
                            st.write(f"**Positive:** {sentiment['positive']:.2%}")
                        if 'negative' in sentiment:
                            st.write(f"**Negative:** {sentiment['negative']:.2%}")
    else:
        st.info("No feedback matches the selected filters.")
    
    # Batch analysis
    if len(all_feedback) > 0:
        st.markdown("---")
        st.markdown("### 📊 Batch Analysis")
        
        if st.button("🔍 Run Advanced Analysis"):
            feedback_texts_list = [f['text'] for f in all_feedback if f.get('text')]
            
            if feedback_texts_list:
                with st.spinner("Analyzing feedback..."):
                    batch_result = nlp_service.analyze_feedback_batch(feedback_texts_list)
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Positive %", f"{batch_result['positive_percentage']:.1f}%")
                    with col2:
                        st.metric("Neutral %", f"{batch_result['neutral_percentage']:.1f}%")
                    with col3:
                        st.metric("Negative %", f"{batch_result['negative_percentage']:.1f}%")
                    
                    st.write(f"**Average Compound Score:** {batch_result['avg_compound']:.3f}")
                    
                    if batch_result.get('topics'):
                        st.write("**Extracted Topics:**")
                        for topic in batch_result['topics']:
                            st.write(f"- {topic}")


def main():
    """Main feedback analytics page"""
    # Check authentication
    auth = get_auth()
    auth.require_role('teacher')
    
    show_feedback_analytics()


if __name__ == "__main__":
    main()

