"""
Streamlit Integration Example - Ensemble Engagement Detection
Shows how to integrate the ensemble model into Streamlit pages
"""

import streamlit as st
import cv2
import numpy as np
from pathlib import Path
import sys

# Add services to path
sys.path.insert(0, str(Path(__file__).parent))

from services.engagement import get_engagement_tracker


def initialize_ensemble():
    """Initialize ensemble detector (cached)"""
    if 'engagement_tracker' not in st.session_state:
        # Choose mode based on user preference
        mode = st.session_state.get('ensemble_mode', 'balanced')
        
        with st.spinner(f'Loading ensemble detector in {mode} mode...'):
            st.session_state.engagement_tracker = get_engagement_tracker(
                use_ensemble=True,
                ensemble_mode=mode
            )
        
        st.success(f'✓ Ensemble detector ready ({mode} mode)')


def display_ensemble_settings():
    """Display ensemble configuration in sidebar"""
    st.sidebar.header("⚙️ Ensemble Settings")
    
    mode = st.sidebar.radio(
        "Performance Mode",
        options=["fast", "balanced", "accurate"],
        index=1,  # Default to balanced
        help="""
        **Fast**: 1 model, ~30ms inference (real-time video)
        **Balanced**: 2 models, ~80ms inference (live sessions) 
        **Accurate**: 3 models, ~150ms inference (offline analysis)
        """
    )
    
    # Store mode in session state
    if st.session_state.get('ensemble_mode') != mode:
        st.session_state.ensemble_mode = mode
        if 'engagement_tracker' in st.session_state:
            # Reload with new mode
            st.session_state.engagement_tracker.shutdown()
            del st.session_state.engagement_tracker
            st.rerun()
    
    # Display model info
    if 'engagement_tracker' in st.session_state:
        tracker = st.session_state.engagement_tracker
        if tracker.ensemble_detector:
            info = tracker.get_ensemble_info()
            
            st.sidebar.metric("Models Loaded", info.get('num_models', 0))
            
            if st.sidebar.button("Clear Cache"):
                tracker.ensemble_detector.clear_cache()
                st.sidebar.success("Cache cleared!")


def display_engagement_results(features):
    """Display engagement results with ensemble predictions"""
    
    # Traditional scores
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Gaze Score", 
            f"{features.get('gaze_score', 0):.2%}",
            help="Eye direction towards screen"
        )
    
    with col2:
        st.metric(
            "Attention Score",
            f"{features.get('attention_score', 0):.2%}",
            help="Eye openness and alertness"
        )
    
    with col3:
        st.metric(
            "Head Pose Score",
            f"{features.get('head_pose_score', 0):.2%}",
            help="Head stability and orientation"
        )
    
    # Ensemble predictions (if available)
    if 'ensemble_prediction' in features:
        st.divider()
        st.subheader("🤖 AI Engagement Analysis")
        
        ensemble_pred = features['ensemble_prediction']
        ml_score = ensemble_pred.get('engagement_score', 0)
        
        # Overall engagement with progress bar
        st.metric(
            "Overall Engagement Score",
            f"{ml_score:.1%}",
            delta=None,
            help="AI-predicted engagement level"
        )
        st.progress(ml_score)
        
        # Detailed dimensions
        st.write("**Detailed Predictions:**")
        
        predictions = ensemble_pred.get('predictions', {})
        
        # Create 4 columns for dimensions
        cols = st.columns(4)
        
        dimensions = ['Boredom', 'Engagement', 'Confusion', 'Frustration']
        colors = ['red', 'green', 'orange', 'purple']
        
        for i, (dim, color) in enumerate(zip(dimensions, colors)):
            with cols[i]:
                if dim in predictions:
                    pred = predictions[dim]
                    level = pred.get('level', 'Unknown')
                    confidence = pred.get('confidence', 0)
                    
                    # Color-coded display
                    if level in ['Very Low', 'Low']:
                        emoji = "🟢" if dim == 'Engagement' else "🔴"
                    else:
                        emoji = "🔴" if dim == 'Engagement' else "🟢"
                    
                    st.markdown(f"**{emoji} {dim}**")
                    st.write(level)
                    st.caption(f"{confidence:.0%} confidence")
        
        # Mode info
        st.caption(f"Mode: {ensemble_pred.get('mode', 'unknown')} | "
                  f"Timestamp: {ensemble_pred.get('timestamp', 'N/A')}")


def webcam_engagement_page():
    """Complete Streamlit page with webcam engagement tracking"""
    st.title("📹 Real-Time Engagement Tracking")
    st.write("Monitor student engagement using AI-powered facial analysis")
    
    # Initialize ensemble
    initialize_ensemble()
    
    # Display settings
    display_ensemble_settings()
    
    # Webcam controls
    col1, col2 = st.columns([3, 1])
    
    with col1:
        enable_webcam = st.checkbox("Enable Webcam", value=False)
    
    with col2:
        if enable_webcam:
            st.button("📸 Capture", key="capture")
    
    # Webcam feed
    if enable_webcam:
        # Create placeholder for video
        video_placeholder = st.empty()
        results_placeholder = st.empty()
        
        # Start webcam
        cap = cv2.VideoCapture(0)
        
        if 'engagement_tracker' in st.session_state:
            tracker = st.session_state.engagement_tracker
            
            # Process frames
            run = st.checkbox("▶️ Start Tracking", value=True)
            
            while run:
                ret, frame = cap.read()
                if not ret:
                    st.error("Failed to access webcam")
                    break
                
                # Process frame
                features = tracker.process_frame(frame)
                
                # Display frame with annotations
                if features['face_detected']:
                    # Draw on frame
                    cv2.putText(
                        frame,
                        "Face Detected ✓",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 255, 0),
                        2
                    )
                    
                    # Show engagement if available
                    if 'ensemble_prediction' in features:
                        eng_score = features['ensemble_prediction']['engagement_score']
                        cv2.putText(
                            frame,
                            f"Engagement: {eng_score:.0%}",
                            (10, 70),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            (0, 255, 0),
                            2
                        )
                
                # Convert BGR to RGB for Streamlit
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                video_placeholder.image(frame_rgb, channels="RGB", use_column_width=True)
                
                # Display results
                with results_placeholder.container():
                    display_engagement_results(features)
                
                # Check if stop requested
                if not st.session_state.get('run_tracking', True):
                    break
            
            cap.release()
        else:
            st.warning("Ensemble detector not initialized")
    else:
        st.info("👆 Enable webcam to start tracking")
        
        # Show example results
        with st.expander("📊 Example Results"):
            st.write("This is how engagement results will be displayed:")
            
            # Mock features
            mock_features = {
                'gaze_score': 0.85,
                'attention_score': 0.92,
                'head_pose_score': 0.78,
                'ensemble_prediction': {
                    'engagement_score': 0.82,
                    'mode': 'balanced',
                    'timestamp': '2025-11-23T10:30:00',
                    'predictions': {
                        'Boredom': {'level': 'Low', 'confidence': 0.76},
                        'Engagement': {'level': 'High', 'confidence': 0.82},
                        'Confusion': {'level': 'Low', 'confidence': 0.71},
                        'Frustration': {'level': 'Very Low', 'confidence': 0.89}
                    }
                }
            }
            
            display_engagement_results(mock_features)


def lecture_analytics_page():
    """Analytics page showing engagement over time"""
    st.title("📊 Engagement Analytics")
    
    st.write("View detailed engagement statistics from your lectures")
    
    # Example: Load engagement history from session state or database
    if 'engagement_history' in st.session_state:
        import pandas as pd
        import plotly.express as px
        
        # Convert to DataFrame
        df = pd.DataFrame(st.session_state.engagement_history)
        
        # Plot engagement over time
        fig = px.line(
            df,
            x='timestamp',
            y='engagement_score',
            title='Engagement Over Time',
            labels={'engagement_score': 'Engagement Score', 'timestamp': 'Time'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Summary statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Average Engagement", f"{df['engagement_score'].mean():.1%}")
        
        with col2:
            st.metric("Peak Engagement", f"{df['engagement_score'].max():.1%}")
        
        with col3:
            st.metric("Lowest Engagement", f"{df['engagement_score'].min():.1%}")
        
        with col4:
            st.metric("Std Deviation", f"{df['engagement_score'].std():.1%}")
        
        # Dimension breakdown
        st.subheader("Engagement Dimensions")
        
        dimensions_data = []
        for record in st.session_state.engagement_history:
            if 'predictions' in record:
                for dim, pred in record['predictions'].items():
                    dimensions_data.append({
                        'Dimension': dim,
                        'Level': pred['level'],
                        'Timestamp': record['timestamp']
                    })
        
        if dimensions_data:
            dim_df = pd.DataFrame(dimensions_data)
            
            # Count levels per dimension
            fig2 = px.histogram(
                dim_df,
                x='Dimension',
                color='Level',
                title='Engagement Dimension Distribution',
                barmode='stack'
            )
            
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No engagement data available yet. Start a tracking session to see analytics.")


# Example usage in main Streamlit app
if __name__ == "__main__":
    # Page selection
    page = st.sidebar.selectbox(
        "Select Page",
        ["Real-Time Tracking", "Analytics"]
    )
    
    if page == "Real-Time Tracking":
        webcam_engagement_page()
    else:
        lecture_analytics_page()
