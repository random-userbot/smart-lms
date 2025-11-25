"""
Smart LMS - Ensemble Analytics Dashboard
View and analyze ensemble ML model predictions and reports
"""

import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.auth import get_auth
from services.storage import get_storage
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from pathlib import Path


def load_analysis_reports():
    """Load all ensemble analysis reports"""
    reports_dir = Path("ml_data/ensemble_analysis_reports")
    
    if not reports_dir.exists():
        return []
    
    reports = []
    for report_file in reports_dir.glob("ensemble_analysis_*.json"):
        try:
            with open(report_file, 'r') as f:
                data = json.load(f)
                data['report_file'] = report_file.name
                reports.append(data)
        except Exception as e:
            st.warning(f"Failed to load {report_file.name}: {e}")
    
    return sorted(reports, key=lambda x: x.get('timestamp', ''), reverse=True)


def render_report_summary(report):
    """Render summary of a single report"""
    st.markdown(f"### 📊 Session: `{report['session_id']}`")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📸 Total Frames", report['total_frames'])
    
    with col2:
        st.metric("🤖 AI Predictions", report['ensemble_predictions'])
    
    with col3:
        if 'statistics' in report and 'avg_engagement' in report['statistics']:
            avg_eng = report['statistics']['avg_engagement']
            st.metric("📈 Avg Engagement", f"{avg_eng:.1f}%")
    
    with col4:
        timestamp = datetime.fromisoformat(report['timestamp'])
        st.metric("🕐 Recorded", timestamp.strftime("%m/%d %H:%M"))
    
    # Statistics
    if 'statistics' in report:
        stats = report['statistics']
        
        st.markdown("---")
        st.markdown("#### 📊 Engagement Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Minimum", f"{stats.get('min_engagement', 0):.1f}%")
        with col2:
            st.metric("Average", f"{stats.get('avg_engagement', 0):.1f}%")
        with col3:
            st.metric("Maximum", f"{stats.get('max_engagement', 0):.1f}%")
        
        # Emotion analysis
        if 'emotion_analysis' in stats:
            st.markdown("#### 🎭 Emotion Analysis")
            
            emotion_data = stats['emotion_analysis']
            
            cols = st.columns(len(emotion_data))
            for i, (emotion, data) in enumerate(emotion_data.items()):
                with cols[i]:
                    emoji_map = {
                        'Boredom': '😴',
                        'Engagement': '🎯',
                        'Confusion': '😕',
                        'Frustration': '😤'
                    }
                    st.markdown(f"**{emoji_map.get(emotion, '•')} {emotion}**")
                    st.text(f"Level: {data['most_common_level']}")
                    st.text(f"Conf: {data['avg_confidence']*100:.1f}%")


def render_prediction_timeline(predictions):
    """Render timeline of predictions"""
    if not predictions:
        st.info("No predictions available")
        return
    
    # Extract data for plotting
    frames = [p['frame_number'] for p in predictions]
    scores = [p['prediction']['engagement_score'] for p in predictions]
    modes = [p['prediction']['mode'] for p in predictions]
    
    # Create timeline chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=frames,
        y=scores,
        mode='lines+markers',
        name='Engagement Score',
        line=dict(color='#1f77b4', width=2),
        marker=dict(size=8),
        hovertemplate='Frame: %{x}<br>Score: %{y:.1f}%<extra></extra>'
    ))
    
    # Add threshold lines
    fig.add_hline(y=75, line_dash="dash", line_color="green", annotation_text="Very High")
    fig.add_hline(y=50, line_dash="dash", line_color="yellow", annotation_text="High")
    fig.add_hline(y=25, line_dash="dash", line_color="orange", annotation_text="Moderate")
    
    fig.update_layout(
        title="Engagement Score Timeline",
        xaxis_title="Frame Number",
        yaxis_title="Engagement Score (%)",
        yaxis_range=[0, 100],
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_emotion_breakdown(predictions):
    """Render emotion level breakdown"""
    if not predictions:
        return
    
    # Aggregate emotion data
    emotion_counts = {
        'Boredom': {'Very Low': 0, 'Low': 0, 'High': 0, 'Very High': 0},
        'Engagement': {'Very Low': 0, 'Low': 0, 'High': 0, 'Very High': 0},
        'Confusion': {'Very Low': 0, 'Low': 0, 'High': 0, 'Very High': 0},
        'Frustration': {'Very Low': 0, 'Low': 0, 'High': 0, 'Very High': 0}
    }
    
    for pred in predictions:
        for emotion, data in pred['prediction']['predictions'].items():
            level = data['level']
            emotion_counts[emotion][level] += 1
    
    # Create stacked bar chart
    emotions = list(emotion_counts.keys())
    levels = ['Very Low', 'Low', 'High', 'Very High']
    
    fig = go.Figure()
    
    colors = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c']
    
    for i, level in enumerate(levels):
        values = [emotion_counts[emotion][level] for emotion in emotions]
        fig.add_trace(go.Bar(
            name=level,
            x=emotions,
            y=values,
            marker_color=colors[i]
        ))
    
    fig.update_layout(
        title="Emotion Level Distribution",
        xaxis_title="Emotion",
        yaxis_title="Count",
        barmode='stack',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_detailed_predictions(predictions):
    """Render detailed prediction table"""
    if not predictions:
        return
    
    st.markdown("#### 📋 Detailed Predictions")
    
    # Convert to DataFrame
    data = []
    for pred in predictions:
        row = {
            'Frame': pred['frame_number'],
            'Timestamp': datetime.fromisoformat(pred['timestamp']).strftime("%H:%M:%S"),
            'Engagement': f"{pred['prediction']['engagement_score']:.1f}%",
            'Mode': pred['prediction']['mode']
        }
        
        # Add emotion levels
        for emotion, emotion_data in pred['prediction']['predictions'].items():
            row[emotion] = f"{emotion_data['level']} ({emotion_data['confidence']*100:.0f}%)"
        
        data.append(row)
    
    df = pd.DataFrame(data)
    
    # Display with pagination
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=400
    )


def show_ensemble_analytics():
    """Main analytics dashboard"""
    st.title("🤖 Ensemble ML Analytics Dashboard")
    st.markdown("View and analyze ensemble model predictions and engagement reports")
    
    # Load all reports
    reports = load_analysis_reports()
    
    if not reports:
        st.info("📭 No analysis reports found yet. Start a lecture session with ensemble ML enabled to generate reports.")
        return
    
    st.success(f"✅ Found {len(reports)} analysis reports")
    
    # Report selector
    st.markdown("---")
    st.markdown("### 📂 Select Session")
    
    report_options = {
        f"{r['session_id']} - {datetime.fromisoformat(r['timestamp']).strftime('%Y-%m-%d %H:%M')}": r
        for r in reports
    }
    
    selected_report_name = st.selectbox(
        "Session",
        options=list(report_options.keys()),
        label_visibility="collapsed"
    )
    
    selected_report = report_options[selected_report_name]
    
    # Display report
    st.markdown("---")
    render_report_summary(selected_report)
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Timeline", "🎭 Emotions", "📋 Details", "📄 Raw Data"])
    
    with tab1:
        st.markdown("### Engagement Timeline")
        render_prediction_timeline(selected_report.get('predictions', []))
    
    with tab2:
        st.markdown("### Emotion Breakdown")
        render_emotion_breakdown(selected_report.get('predictions', []))
    
    with tab3:
        render_detailed_predictions(selected_report.get('predictions', []))
    
    with tab4:
        st.markdown("### Raw JSON Data")
        st.json(selected_report)
    
    # Export options
    st.markdown("---")
    st.markdown("### 💾 Export")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Download JSON
        json_str = json.dumps(selected_report, indent=2)
        st.download_button(
            label="📥 Download JSON",
            data=json_str,
            file_name=f"{selected_report['session_id']}_analysis.json",
            mime="application/json"
        )
    
    with col2:
        # Download CSV
        if selected_report.get('predictions'):
            csv_data = []
            for pred in selected_report['predictions']:
                row = {
                    'frame_number': pred['frame_number'],
                    'timestamp': pred['timestamp'],
                    'engagement_score': pred['prediction']['engagement_score'],
                    'mode': pred['prediction']['mode']
                }
                for emotion, data in pred['prediction']['predictions'].items():
                    row[f'{emotion}_level'] = data['level']
                    row[f'{emotion}_confidence'] = data['confidence']
                csv_data.append(row)
            
            df = pd.DataFrame(csv_data)
            csv = df.to_csv(index=False)
            
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"{selected_report['session_id']}_predictions.csv",
                mime="text/csv"
            )


def main():
    """Main entry point"""
    # Check authentication
    auth = get_auth()
    
    if 'user' not in st.session_state or not st.session_state.user:
        st.warning("⚠️ Please login first")
        st.stop()
    
    user = st.session_state.user
    
    # Only admins and teachers can view analytics
    if user['role'] not in ['admin', 'teacher']:
        st.error("❌ Access denied. This page is only available to teachers and admins.")
        st.stop()
    
    show_ensemble_analytics()


if __name__ == "__main__":
    main()
