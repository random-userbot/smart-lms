"""
Smart LMS - Analytics Dashboard
Real-time engagement tracking and performance analytics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import glob
from datetime import datetime, timedelta
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.auth import get_auth
from services.storage import get_storage

def load_engagement_data(student_id=None, limit_files=50):
    """Load engagement data from CSV logs"""
    log_dir = "ml_data/engagement_logs"
    if not os.path.exists(log_dir):
        return pd.DataFrame()
    
    # Get all CSV files
    all_files = glob.glob(os.path.join(log_dir, "engagement_log_*.csv"))
    
    # Sort by modification time (newest first)
    all_files.sort(key=os.path.getmtime, reverse=True)
    
    # Limit files to process
    files_to_read = all_files[:limit_files]
    
    dfs = []
    for f in files_to_read:
        try:
            df = pd.read_csv(f)
            if not df.empty:
                # Add session ID from filename if not present
                if 'session_id' not in df.columns:
                    session_id = os.path.basename(f).replace('engagement_log_', '').replace('.csv', '')
                    df['session_id'] = session_id
                
                dfs.append(df)
        except Exception as e:
            continue
            
    if not dfs:
        return pd.DataFrame()
        
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Filter by student if requested
    if student_id and 'student_id' in combined_df.columns:
        combined_df = combined_df[combined_df['student_id'] == student_id]
        
    return combined_df

def show_admin_analytics():
    """Show analytics for Admin/Teacher"""
    st.title("📊 Real-time Engagement Dashboard")
    
    tab1, tab2, tab3 = st.tabs(["🔴 Live Monitor", "📈 Historical Trends", "👥 Student Insights"])
    
    # Load recent data
    df = load_engagement_data(limit_files=100)
    
    with tab1:
        st.subheader("Live Active Sessions")
        
        if df.empty:
            st.info("No active sessions detected.")
        else:
            # Identify "live" sessions (data within last 5 minutes)
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                current_time = datetime.utcnow()
                cutoff_time = current_time - timedelta(minutes=5)
                
                live_df = df[df['timestamp'] > cutoff_time]
                
                if live_df.empty:
                    st.info("No active sessions in the last 5 minutes.")
                else:
                    # Group by session/student
                    active_sessions = live_df.groupby('session_id').agg({
                        'student_id': 'first',
                        'engagement_score': 'mean',
                        'timestamp': 'max',
                        'status': lambda x: x.iloc[-1]
                    }).reset_index()
                    
                    # Display metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("👥 Active Students", len(active_sessions))
                    with col2:
                        avg_score = active_sessions['engagement_score'].mean()
                        st.metric("⚡ Avg Engagement", f"{avg_score:.1f}%")
                    with col3:
                        # Count students with low engagement
                        low_engagement = len(active_sessions[active_sessions['engagement_score'] < 50])
                        st.metric("⚠️ Needs Attention", low_engagement)
                    
                    st.markdown("### 🎥 Active Student Feeds")
                    
                    # Display cards for each active student
                    for _, session in active_sessions.iterrows():
                        with st.container():
                            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                            with col1:
                                st.markdown(f"**Student:** {session['student_id']}")
                                st.caption(f"Session: {session['session_id'][:8]}...")
                            with col2:
                                score = session['engagement_score']
                                color = "green" if score > 70 else "orange" if score > 40 else "red"
                                st.markdown(f"Engagement: **:{color}[{score:.1f}%]**")
                                st.progress(score/100)
                            with col3:
                                status = session['status'].replace('_', ' ').title()
                                st.markdown(f"Status: **{status}**")
                            with col4:
                                last_seen = session['timestamp'].strftime('%H:%M:%S')
                                st.caption(f"Last update: {last_seen}")
                            st.markdown("---")
                            
                    if st.button("🔄 Refresh Live Data"):
                        st.rerun()

    with tab2:
        st.subheader("Engagement Trends")
        if not df.empty:
            # Daily average engagement
            df['date'] = df['timestamp'].dt.date
            daily_avg = df.groupby('date')['engagement_score'].mean().reset_index()
            
            fig = px.line(daily_avg, x='date', y='engagement_score', 
                         title='Average Daily Engagement',
                         labels={'engagement_score': 'Engagement Score (%)', 'date': 'Date'})
            st.plotly_chart(fig, use_container_width=True)
            
            # Engagement distribution
            fig2 = px.histogram(df, x='engagement_score', nbins=20,
                               title='Engagement Score Distribution',
                               labels={'engagement_score': 'Score', 'count': 'Frequency'})
            st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        st.subheader("Student Performance")
        if not df.empty:
            student_stats = df.groupby('student_id').agg({
                'engagement_score': ['mean', 'min', 'max', 'count']
            }).reset_index()
            student_stats.columns = ['Student ID', 'Avg Score', 'Min Score', 'Max Score', 'Data Points']
            
            st.dataframe(student_stats, use_container_width=True)

def show_student_analytics(user):
    """Show analytics for Student"""
    st.title(f"📈 My Learning Analytics")
    
    # Load student's data
    df = load_engagement_data(student_id=user['user_id'], limit_files=100)
    
    if df.empty:
        st.info("No engagement data available yet. Watch some lectures to generate insights!")
        return
        
    # Convert timestamp
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Summary Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        avg_score = df['engagement_score'].mean()
        st.metric("⚡ Average Focus", f"{avg_score:.1f}%")
    with col2:
        total_sessions = df['session_id'].nunique()
        st.metric("📚 Study Sessions", total_sessions)
    with col3:
        total_time_mins = len(df) / 60  # Assuming 1 frame per second roughly
        st.metric("⏱️ Total Focus Time", f"{total_time_mins:.1f} min")
        
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Focus Over Time")
        # Resample to 1-minute intervals for smoother graph
        if not df.empty:
            df_resampled = df.set_index('timestamp').resample('1T')['engagement_score'].mean().reset_index()
            fig = px.line(df_resampled, x='timestamp', y='engagement_score',
                         title='Focus Trend (Last Sessions)',
                         labels={'engagement_score': 'Focus Score', 'timestamp': 'Time'})
            fig.update_yaxes(range=[0, 100])
            st.plotly_chart(fig, use_container_width=True)
            
    with col2:
        st.subheader("Attention Breakdown")
        if 'status' in df.columns:
            status_counts = df['status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            status_counts['Status'] = status_counts['Status'].str.replace('_', ' ').str.title()
            
            fig2 = px.pie(status_counts, values='Count', names='Status',
                         title='Focus Distribution',
                         hole=0.4)
            st.plotly_chart(fig2, use_container_width=True)

def main():
    # Check authentication
    auth = get_auth()
    if not auth.check_login():
        st.error("Please login to view analytics")
        return

    user = st.session_state.user
    role = user.get('role', 'student')
    
    if role in ['admin', 'teacher']:
        show_admin_analytics()
    else:
        show_student_analytics(user)

if __name__ == "__main__":
    main()
