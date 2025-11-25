"""
Smart LMS - Bulk Feedback Analysis
Analyze multiple student feedbacks in batch using NLP
"""

import streamlit as st
import sys
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Add parent directory to path to import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.auth import get_auth
from services.nlp import get_nlp_service

def show_bulk_analysis():
    st.title("📊 Bulk Feedback Analysis")
    st.markdown("Analyze large volumes of student feedback using AI to extract insights, sentiment, and themes.")

    nlp_service = get_nlp_service()

    # Input section
    st.markdown("### 1. Input Feedback")
    
    input_method = st.radio("Choose input method:", ["Upload File (.txt, .csv)", "Paste Text"])
    
    feedbacks = []
    
    if input_method == "Upload File (.txt, .csv)":
        uploaded_file = st.file_uploader("Upload a file containing feedbacks (one per line for .txt)", type=['txt', 'csv'])
        if uploaded_file is not None:
            if uploaded_file.name.endswith('.txt'):
                stringio = uploaded_file.getvalue().decode("utf-8")
                feedbacks = [line.strip() for line in stringio.split('\n') if line.strip()]
            elif uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
                # Try to find a text column
                text_cols = [col for col in df.columns if 'text' in col.lower() or 'feedback' in col.lower() or 'comment' in col.lower()]
                if text_cols:
                    feedbacks = df[text_cols[0]].dropna().astype(str).tolist()
                    st.success(f"Loaded {len(feedbacks)} feedbacks from column '{text_cols[0]}'")
                else:
                    st.error("Could not identify a feedback text column in the CSV. Please ensure one column is named 'text', 'feedback', or 'comment'.")
            
            st.info(f"Loaded {len(feedbacks)} feedback items.")
            
    else:
        text_input = st.text_area("Paste feedbacks here (one per line):", height=200)
        if text_input:
            feedbacks = [line.strip() for line in text_input.split('\n') if line.strip()]
            st.info(f"Loaded {len(feedbacks)} feedback items.")

    # Analysis section
    if feedbacks:
        if st.button("🚀 Analyze Feedback"):
            with st.spinner("Analyzing sentiments and extracting themes..."):
                # Perform batch analysis
                # We can use analyze_feedback_batch from nlp_service if it exists, or loop manually
                # Checking nlp.py content from previous turns, it has analyze_feedback_batch(feedback_texts)
                
                results = nlp_service.analyze_feedback_batch(feedbacks)
                
                # Display Results
                st.markdown("---")
                st.markdown("### 2. Analysis Results")
                
                # Summary Metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Feedbacks", results['total_count'])
                with col2:
                    st.metric("Positive", f"{results['positive_percentage']:.1f}%")
                with col3:
                    st.metric("Negative", f"{results['negative_percentage']:.1f}%")
                with col4:
                    st.metric("Avg Sentiment", f"{results['avg_compound']:.2f}")

                # Charts
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Sentiment Distribution")
                    # Pie chart
                    labels = ['Positive', 'Neutral', 'Negative']
                    values = [results['positive_count'], results['neutral_count'], results['negative_count']]
                    colors = ['#2ecc71', '#f1c40f', '#e74c3c']
                    
                    fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, marker=dict(colors=colors), hole=0.4)])
                    fig_pie.update_layout(height=350, margin=dict(t=0, b=0, l=0, r=0))
                    st.plotly_chart(fig_pie, use_container_width=True)
                    
                with col2:
                    st.subheader("Top Topics")
                    if results['topics']:
                        # Bar chart for topics (simulated frequency since extract_topics returns a list)
                        # If extract_topics just returns a list of top words, we can just show them.
                        # But nlp.py extract_topics returns a list of strings.
                        # Let's visualize them as tags or a list
                        st.write("Key themes identified in the feedback:")
                        for topic in results['topics']:
                            st.markdown(f"- **{topic}**")
                    else:
                        st.info("No specific topics extracted.")

                # Detailed Dataframe
                st.markdown("### 3. Detailed Breakdown")
                
                # Create a DataFrame for the detailed view
                detailed_data = []
                for i, sentiment in enumerate(results['sentiments']):
                    detailed_data.append({
                        "Feedback": feedbacks[i],
                        "Sentiment": sentiment['label'],
                        "Score": f"{sentiment['compound']:.2f}",
                        "Positive": f"{sentiment['positive']:.2f}",
                        "Negative": f"{sentiment['negative']:.2f}"
                    })
                
                df_details = pd.DataFrame(detailed_data)
                
                # Color coding for the dataframe
                def color_sentiment(val):
                    color = 'black'
                    if val == 'positive': color = 'green'
                    elif val == 'negative': color = 'red'
                    elif val == 'neutral': color = 'orange'
                    return f'color: {color}'

                st.dataframe(df_details.style.applymap(color_sentiment, subset=['Sentiment']), use_container_width=True)
                
                # Download option
                csv = df_details.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Download Analysis Report",
                    csv,
                    "feedback_analysis_report.csv",
                    "text/csv",
                    key='download-csv'
                )

def main():
    auth = get_auth()
    
    # Check login (optional, depending on requirements, but good practice)
    if 'user' not in st.session_state:
        st.warning("Please log in to use this feature.")
        return

    show_bulk_analysis()

if __name__ == "__main__":
    main()
