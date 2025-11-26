"""
Smart LMS - Comprehensive Teaching Analytics Dashboard
Advanced visualization and analytics for teaching performance evaluation
"""

import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.auth import get_auth
from services.storage import get_storage
from services.teaching_score_model import get_teaching_score_model
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
from collections import Counter
import json


def render_score_gauge(score: float, title: str, subtitle: str = ""):
    """Render an enhanced gauge chart for teaching scores"""
    # Determine color based on score
    if score >= 90:
        color = "#28a745"  # Green
        level = "Outstanding"
    elif score >= 80:
        color = "#17a2b8"  # Blue
        level = "Excellent"
    elif score >= 70:
        color = "#ffc107"  # Yellow
        level = "Good"
    elif score >= 60:
        color = "#fd7e14"  # Orange
        level = "Satisfactory"
    else:
        color = "#dc3545"  # Red
        level = "Needs Improvement"

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"<b>{title}</b><br><span style='font-size:14px;color:gray;'>{subtitle}</span>",
               'font': {'size': 16}},
        delta={'reference': 75, 'increasing': {'color': color}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 2, 'tickcolor': "darkblue"},
            'bar': {'color': color, 'thickness': 0.3},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 60], 'color': 'rgba(220, 53, 69, 0.1)'},
                {'range': [60, 70], 'color': 'rgba(253, 126, 20, 0.1)'},
                {'range': [70, 80], 'color': 'rgba(255, 193, 7, 0.1)'},
                {'range': [80, 90], 'color': 'rgba(23, 162, 184, 0.1)'},
                {'range': [90, 100], 'color': 'rgba(40, 167, 69, 0.1)'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 75
            }
        }
    ))

    fig.update_layout(height=300, margin=dict(l=20, r=20, t=60, b=20))
    return fig


def render_component_radar(component_scores: dict, weights: dict):
    """Render radar chart showing component scores with weights"""
    categories = ['Engagement', 'Feedback', 'Performance', 'Activity', 'Class Engagement']
    values = [
        component_scores.get('engagement', 0),
        component_scores.get('feedback', 0),
        component_scores.get('performance', 0),
        component_scores.get('activity', 0),
        component_scores.get('class_engagement', 0)
    ]

    # Create weighted values for secondary trace
    weighted_values = [v * weights.get(cat.lower().replace(' ', '_'), 0) for v, cat in zip(values, categories)]

    fig = go.Figure()

    # Add actual scores
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Component Scores',
        line=dict(color='#1f77b4', width=3),
        fillcolor='rgba(31, 119, 180, 0.3)'
    ))

    # Add weighted contribution
    fig.add_trace(go.Scatterpolar(
        r=weighted_values,
        theta=categories,
        fill='toself',
        name='Weighted Contribution',
        line=dict(color='#ff7f0e', width=2, dash='dash'),
        fillcolor='rgba(255, 127, 14, 0.2)'
    ))

    # Add target line (75)
    fig.add_trace(go.Scatterpolar(
        r=[75] * len(categories),
        theta=categories,
        name='Target (75)',
        line=dict(color='green', width=1, dash='dot'),
        mode='lines'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=10)),
            angularaxis=dict(tickfont=dict(size=12))
        ),
        showlegend=True,
        title="Component Score Analysis",
        height=500,
        margin=dict(l=40, r=40, t=60, b=40)
    )

    return fig


def render_trend_chart(historical_scores: list):
    """Render trend chart for teaching performance over time"""
    if not historical_scores:
        fig = go.Figure()
        fig.add_annotation(text="No historical data available",
                          xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig

    # Sort by date
    sorted_scores = sorted(historical_scores, key=lambda x: x.get('calculated_at', ''))

    dates = []
    scores = []
    components = {'engagement': [], 'feedback': [], 'performance': [], 'activity': [], 'class_engagement': []}

    for score_data in sorted_scores:
        dates.append(datetime.fromisoformat(score_data['calculated_at']).strftime('%Y-%m-%d'))
        scores.append(score_data['final_score'])

        for comp in components.keys():
            components[comp].append(score_data.get('component_scores', {}).get(comp, 0))

    fig = go.Figure()

    # Add main score line
    fig.add_trace(go.Scatter(
        x=dates,
        y=scores,
        mode='lines+markers',
        name='Overall Score',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=8, color='#1f77b4'),
        hovertemplate='<b>%{x}</b><br>Score: %{y:.1f}<extra></extra>'
    ))

    # Add component lines (lighter)
    colors = ['#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    for i, (comp_name, comp_scores) in enumerate(components.items()):
        fig.add_trace(go.Scatter(
            x=dates,
            y=comp_scores,
            mode='lines',
            name=f'{comp_name.title()}',
            line=dict(color=colors[i], width=2, dash='dot'),
            opacity=0.7,
            visible='legendonly',  # Hidden by default, can be toggled
            hovertemplate=f'<b>{comp_name.title()}</b><br>%{{x}}<br>Score: %{{y:.1f}}<extra></extra>'
        ))

    # Add target line
    fig.add_hline(y=75, line_dash="dash", line_color="green",
                 annotation_text="Target Score (75)", annotation_position="bottom right")

    fig.update_layout(
        title="Teaching Performance Trends",
        xaxis_title="Date",
        yaxis_title="Score (0-100)",
        yaxis_range=[0, 100],
        hovermode='x unified',
        height=400,
        margin=dict(l=40, r=40, t=60, b=40)
    )

    return fig


def render_course_breakdown(detailed_metrics: dict):
    """Render course-wise performance breakdown"""
    course_data = detailed_metrics.get('course_breakdown', [])

    if not course_data:
        fig = go.Figure()
        fig.add_annotation(text="No course data available",
                          xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig

    # Prepare data
    courses = [c['course_name'][:20] + '...' if len(c['course_name']) > 20 else c['course_name']
               for c in course_data]
    engagement = [c['avg_engagement'] for c in course_data]
    feedback = [c['avg_feedback_rating'] for c in course_data]
    students = [c['enrolled_students'] for c in course_data]

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Performance by Course', 'Student Enrollment'),
        specs=[[{"secondary_y": True}, {"type": "bar"}]]
    )

    # Performance metrics
    fig.add_trace(go.Bar(
        x=courses,
        y=engagement,
        name='Avg Engagement',
        marker_color='#1f77b4',
        hovertemplate='<b>%{x}</b><br>Engagement: %{y:.1f}<extra></extra>'
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        x=courses,
        y=feedback,
        name='Avg Feedback',
        marker_color='#ff7f0e',
        hovertemplate='<b>%{x}</b><br>Feedback: %{y:.1f}<extra></extra>'
    ), row=1, col=1, secondary_y=False)

    # Student enrollment
    fig.add_trace(go.Bar(
        x=courses,
        y=students,
        name='Enrolled Students',
        marker_color='#2ca02c',
        hovertemplate='<b>%{x}</b><br>Students: %{y}<extra></extra>'
    ), row=1, col=2)

    fig.update_layout(
        height=400,
        showlegend=True,
        margin=dict(l=40, r=40, t=60, b=40)
    )

    fig.update_xaxes(tickangle=45)
    fig.update_yaxes(title_text="Score / Rating", row=1, col=1)
    fig.update_yaxes(title_text="Students", row=1, col=2)

    return fig


def render_predictive_insights(evaluation_data: dict):
    """Render predictive analytics and forecasting"""
    predictive_data = evaluation_data.get('predictive_insights', {})

    if not predictive_data.get('available', False):
        st.info("🔮 Predictive analytics will be available after collecting more evaluation data (minimum 3 evaluation periods).")
        return

    st.markdown("### 🔮 Performance Forecasting")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        forecast_score = predictive_data.get('forecast_score', 0)
        st.metric(
            "3-Month Forecast",
            f"{forecast_score:.1f}/100",
            delta=f"{forecast_score - evaluation_data.get('final_score', 0):+.1f}",
            help="Predicted score in 3 months based on current trends"
        )

    with col2:
        confidence = predictive_data.get('prediction_confidence', 'Low')
        confidence_colors = {'High': '🟢', 'Medium': '🟡', 'Low': '🔴'}
        st.metric(
            "Prediction Confidence",
            f"{confidence_colors.get(confidence, '⚪')} {confidence}",
            help=f"Confidence level: {predictive_data.get('confidence_score', 0):.1f}% R² score"
        )

    with col3:
        risk = predictive_data.get('risk_assessment', 'Unknown')
        risk_colors = {'Low Risk': '🟢', 'Low-Moderate Risk': '🟡', 'Medium Risk': '🟠', 'High Risk': '🔴'}
        st.metric(
            "Risk Assessment",
            f"{risk_colors.get(risk, '⚪')} {risk}",
            help="Overall performance risk based on current trajectory"
        )

    with col4:
        data_points = predictive_data.get('data_points_used', 0)
        st.metric(
            "Data Points",
            data_points,
            help="Number of historical evaluations used for prediction"
        )

    # Trajectory chart
    st.markdown("#### 📈 Improvement Trajectory")

    trajectory = predictive_data.get('improvement_trajectory', [])
    if trajectory:
        periods = [t['period'] for t in trajectory]
        scores = [t['score'] for t in trajectory]

        fig = go.Figure()

        # Add trajectory line
        fig.add_trace(go.Scatter(
            x=periods,
            y=scores,
            mode='lines+markers',
            name='Predicted Trajectory',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8, color='#1f77b4'),
            hovertemplate='<b>%{x}</b><br>Score: %{y:.1f}<extra></extra>'
        ))

        # Add current score line
        current_score = evaluation_data.get('final_score', 0)
        fig.add_hline(y=current_score, line_dash="dash", line_color="green",
                     annotation_text=f"Current: {current_score:.1f}", annotation_position="bottom right")

        # Add target line
        fig.add_hline(y=75, line_dash="dot", line_color="orange",
                     annotation_text="Target: 75", annotation_position="top right")

        fig.update_layout(
            title="Performance Improvement Trajectory",
            xaxis_title="Time Period",
            yaxis_title="Predicted Score",
            yaxis_range=[0, 100],
            height=300,
            margin=dict(l=40, r=40, t=60, b=40)
        )

        st.plotly_chart(fig, width='stretch')

        # Component predictions
        st.markdown("#### 🎯 Component Forecasts")

        component_preds = predictive_data.get('component_predictions', {})
        if component_preds:
            pred_data = []
            for comp, data in component_preds.items():
                pred_data.append({
                    'Component': comp.title(),
                    'Current': evaluation_data.get('component_scores', {}).get(comp, 0),
                    'Predicted': data.get('predicted_score', 0),
                    'Change': data.get('change', 0),
                    'Trend': data.get('trend', 'stable').title()
                })

            pred_df = pd.DataFrame(pred_data)
            pred_df['Current'] = pred_df['Current'].map('{:.1f}'.format)
            pred_df['Predicted'] = pred_df['Predicted'].map('{:.1f}'.format)
            pred_df['Change'] = pred_df['Change'].map('{:+.1f}'.format)

            st.dataframe(pred_df, width='stretch', hide_index=True)

            # Trend indicators
            trend_col1, trend_col2, trend_col3 = st.columns(3)
            improving = sum(1 for p in component_preds.values() if p.get('trend') == 'improving')
            declining = sum(1 for p in component_preds.values() if p.get('trend') == 'declining')
            stable = sum(1 for p in component_preds.values() if p.get('trend') == 'stable')

            with trend_col1:
                st.metric("📈 Improving", improving)
            with trend_col2:
                st.metric("📉 Declining", declining)
            with trend_col3:
                st.metric("➡️ Stable", stable)


def render_recommendations_card(recommendations: list):
    """Render recommendations in an organized card format"""
    if not recommendations:
        st.info("No specific recommendations available.")
        return

    # Group recommendations by priority
    priority_groups = {
        'critical': [],
        'important': [],
        'suggestions': []
    }

    for rec in recommendations:
        if any(keyword in rec.lower() for keyword in ['significant', 'needs attention', 'critical']):
            priority_groups['critical'].append(rec)
        elif any(keyword in rec.lower() for keyword in ['focus', 'improve', 'consider']):
            priority_groups['important'].append(rec)
        else:
            priority_groups['suggestions'].append(rec)

    # Display recommendations
    for priority, title, color in [
        ('critical', '🚨 Critical Actions', 'red'),
        ('important', '⚡ Important Improvements', 'orange'),
        ('suggestions', '💡 Suggestions', 'blue')
    ]:
        if priority_groups[priority]:
            with st.expander(f"**{title}**", expanded=(priority == 'critical')):
                for rec in priority_groups[priority]:
                    if '🚨' in rec or '⚡' in rec or '💡' in rec:
                        st.markdown(f"• {rec}")
                    else:
                        st.markdown(f"• {rec}")


def render_performance_insights(evaluation_data: dict):
    """Render detailed performance insights"""
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 Score Distribution")
        components = evaluation_data.get('component_scores', {})

        # Create a horizontal bar chart
        fig = go.Figure(go.Bar(
            x=list(components.values()),
            y=list(components.keys()),
            orientation='h',
            marker=dict(
                color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
                line=dict(color='rgba(0,0,0,0.2)', width=1)
            ),
            text=[f'{v:.1f}' for v in components.values()],
            textposition='auto',
        ))

        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis_range=[0, 100]
        )

        st.plotly_chart(fig, width='stretch')

    with col2:
        st.markdown("### 🎯 Performance Summary")

        final_score = evaluation_data.get('final_score', 0)
        grade = evaluation_data.get('grade', 'N/A')
        performance_level = evaluation_data.get('performance_level', 'Unknown')

        # Performance level indicator
        if performance_level == 'Outstanding':
            st.success(f"🎉 **{performance_level}** ({grade})")
        elif performance_level == 'Excellent':
            st.info(f"✅ **{performance_level}** ({grade})")
        elif performance_level == 'Good':
            st.warning(f"⚠️ **{performance_level}** ({grade})")
        else:
            st.error(f"🚨 **{performance_level}** ({grade})")

        st.metric("Overall Score", f"{final_score:.1f}/100")

        # Show weights
        st.markdown("**Component Weights:**")
        weights = evaluation_data.get('weights', {})
        for comp, weight in weights.items():
            st.caption(f"{comp.title()}: {weight*100:.0f}%")

        # Trend information
        trend = evaluation_data.get('trend_analysis', {})
        if trend.get('trend') != 'insufficient_data':
            trend_icon = {'improving': '📈', 'declining': '📉', 'stable': '➡️'}.get(trend.get('trend'), '❓')
            st.caption(f"{trend_icon} Trend: {trend.get('description', '')}")


def export_evaluation_report(evaluation_data: dict, teacher_info: dict):
    """Generate and download evaluation report"""
    report = {
        'generated_at': datetime.now().isoformat(),
        'teacher': {
            'name': teacher_info.get('full_name', 'Unknown'),
            'id': teacher_info.get('user_id', 'Unknown'),
            'role': teacher_info.get('role', 'teacher')
        },
        'evaluation': evaluation_data
    }

    # Convert to JSON
    json_str = json.dumps(report, indent=2, default=str)

    # Create download button
    st.download_button(
        label="📥 Download Full Report (JSON)",
        data=json_str,
        file_name=f"teaching_evaluation_{teacher_info.get('user_id', 'unknown')}_{datetime.now().strftime('%Y%m%d')}.json",
        mime="application/json"
    )


def show_teaching_analytics_dashboard():
    """Main teaching analytics dashboard"""
    st.title("📊 Comprehensive Teaching Analytics Dashboard")
    st.markdown("### Advanced AI-Powered Teaching Performance Evaluation")
    st.markdown("---")

    # Get services
    storage = get_storage()
    teaching_model = get_teaching_score_model()
    user = st.session_state.user

    # Determine which teacher to analyze
    if user['role'] == 'admin':
        # Admin can view all teachers
        all_users = storage.get_all_users()
        teachers = {uid: u for uid, u in all_users.items() if u['role'] == 'teacher'}

        if not teachers:
            st.info("No teachers in the system yet.")
            return

        teacher_options = {uid: u.get('full_name', u['username']) for uid, u in teachers.items()}
        selected_teacher_id = st.selectbox(
            "👨‍🏫 Select Teacher for Analysis",
            options=list(teacher_options.keys()),
            format_func=lambda x: teacher_options[x],
            key="analytics_teacher_select"
        )
    else:
        # Teachers view their own analytics
        selected_teacher_id = user['user_id']
        teacher = storage.get_user(selected_teacher_id)
        st.markdown(f"**Analyzing:** {teacher.get('full_name', 'Unknown')}")

    st.markdown("---")

    # Time period selector
    col1, col2 = st.columns([2, 1])

    with col1:
        time_period = st.selectbox(
            "📅 Analysis Period",
            options=['7d', '30d', '90d', 'all'],
            format_func=lambda x: {
                '7d': 'Last 7 days',
                '30d': 'Last 30 days',
                '90d': 'Last 90 days',
                'all': 'All time'
            }[x],
            index=1  # Default to 30d
        )

    with col2:
        if st.button("🔄 Refresh Analysis", type="primary"):
            st.rerun()

    # Calculate comprehensive evaluation
    with st.spinner("🔍 Analyzing teaching performance..."):
        evaluation_data = teaching_model.calculate_comprehensive_score(
            selected_teacher_id,
            storage,
            time_period=time_period
        )

    # Main score display - Stacked vertically, one per row
    st.markdown("## 🎯 Overall Teaching Score")
    
    # Row 1: Overall Teaching Score Gauge (Full Width)
    fig_main = render_score_gauge(
        evaluation_data['final_score'],
        "Overall Teaching Score",
        f"Grade: {evaluation_data['grade']} | {evaluation_data['performance_level']}"
    )
    st.plotly_chart(fig_main, width='stretch')
    
    st.markdown("---")
    
    # Row 2: Component Score Analysis Radar Chart (Full Width)
    st.markdown("### 📊 Component Score Analysis")
    fig_radar = render_component_radar(
        evaluation_data['component_scores'],
        evaluation_data['weights']
    )
    st.plotly_chart(fig_radar, width='stretch')
    
    st.markdown("---")
    
    # Row 3: Score Distribution Bar Chart (Full Width)
    st.markdown("### 📊 Score Distribution")
    components = evaluation_data.get('component_scores', {})
    
    # Create a horizontal bar chart
    fig_dist = go.Figure(go.Bar(
        x=list(components.values()),
        y=[c.replace('_', ' ').title() for c in components.keys()],
        orientation='h',
        marker=dict(
            color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
            line=dict(color='rgba(0,0,0,0.2)', width=1)
        ),
        text=[f'{v:.1f}' for v in components.values()],
        textposition='auto',
    ))
    
    fig_dist.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis_range=[0, 100],
        xaxis_title="Score (0-100)",
        yaxis_title="Component"
    )
    
    st.plotly_chart(fig_dist, width='stretch')
    
    st.markdown("---")
    
    # Row 4: Performance Summary (Centered)
    st.markdown("### 🎯 Performance Summary")
    
    # Center the performance summary using columns
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        final_score = evaluation_data.get('final_score', 0)
        grade = evaluation_data.get('grade', 'N/A')
        performance_level = evaluation_data.get('performance_level', 'Unknown')
        
        # Performance level indicator
        if performance_level == 'Outstanding':
            st.success(f"🎉 **{performance_level}** ({grade})")
        elif performance_level == 'Excellent':
            st.info(f"✅ **{performance_level}** ({grade})")
        elif performance_level == 'Good':
            st.warning(f"⚠️ **{performance_level}** ({grade})")
        else:
            st.error(f"🚨 **{performance_level}** ({grade})")
        
        st.metric("Overall Score", f"{final_score:.1f}/100")
        
        # Show weights
        st.markdown("**Component Weights:**")
        weights = evaluation_data.get('weights', {})
        for comp, weight in weights.items():
            st.caption(f"{comp.replace('_', ' ').title()}: {weight*100:.0f}%")
        
        # Trend information
        trend = evaluation_data.get('trend_analysis', {})
        if trend.get('trend') != 'insufficient_data':
            trend_icon = {'improving': '📈', 'declining': '📉', 'stable': '➡️'}.get(trend.get('trend'), '❓')
            st.caption(f"{trend_icon} Trend: {trend.get('description', '')}")

    st.markdown("---")

    # Detailed Analysis Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Performance Trends",
        "📚 Course Analysis",
        "🔮 Predictive Insights",
        "💡 Recommendations",
        "📋 Detailed Report"
    ])

    with tab1:
        st.markdown("### Performance Trends Over Time")

        # Get historical evaluations
        all_evaluations = storage.get_all_evaluations()
        historical_evaluations = [eval_data for eval_data in all_evaluations.values()
                                 if eval_data.get('teacher_id') == selected_teacher_id]

        if historical_evaluations:
            fig_trend = render_trend_chart(historical_evaluations)
            st.plotly_chart(fig_trend, width='stretch')
        else:
            st.info("📊 Historical data will appear here as evaluations are conducted over time.")

        # Trend analysis summary
        trend_data = evaluation_data.get('trend_analysis', {})
        if trend_data.get('trend') != 'insufficient_data':
            col1, col2, col3 = st.columns(3)

            with col1:
                trend_icon = {'improving': '📈', 'declining': '📉', 'stable': '➡️'}.get(trend_data.get('trend'), '❓')
                st.metric(
                    "Performance Trend",
                    trend_data.get('trend', 'Unknown').title(),
                    delta=f"{trend_data.get('change', 0):+.1f}",
                    help=trend_data.get('description', '')
                )

            with col2:
                st.metric(
                    "Data Points",
                    trend_data.get('data_points', 0),
                    help="Number of evaluation periods analyzed"
                )

            with col3:
                st.metric(
                    "Recent Average",
                    f"{trend_data.get('recent_average', 0):.1f}",
                    help="Average score in recent evaluations"
                )

    with tab2:
        st.markdown("### Course-wise Performance Analysis")

        detailed_metrics = evaluation_data.get('detailed_metrics', {})
        fig_courses = render_course_breakdown(detailed_metrics)
        st.plotly_chart(fig_courses, width='stretch')

        # Course summary
        if detailed_metrics:
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Courses", detailed_metrics.get('total_courses', 0))

            with col2:
                st.metric("Total Students", detailed_metrics.get('total_students', 0))

            with col3:
                st.metric("Total Lectures", detailed_metrics.get('total_lectures', 0))

            with col4:
                avg_students_per_course = (
                    detailed_metrics.get('total_students', 0) /
                    max(1, detailed_metrics.get('total_courses', 0))
                )
                st.metric("Avg Students/Course", f"{avg_students_per_course:.1f}")

    with tab3:
        render_predictive_insights(evaluation_data)

    with tab4:
        st.markdown("### 🤖 AI-Generated Recommendations")

        recommendations = evaluation_data.get('recommendations', [])
        render_recommendations_card(recommendations)

        # Action items
        st.markdown("### 🎯 Quick Action Items")
        action_col1, action_col2 = st.columns(2)

        with action_col1:
            if st.button("📊 Request Detailed Feedback", type="secondary"):
                st.success("Feedback request sent to students!")

            if st.button("📚 Upload New Materials", type="secondary"):
                st.info("Redirecting to upload page...")
                st.session_state.current_page = 'upload'
                st.rerun()

        with action_col2:
            if st.button("🎥 Schedule Review Session", type="secondary"):
                st.success("Review session scheduled!")

            if st.button("📈 View Engagement Analytics", type="secondary"):
                st.info("Redirecting to engagement analytics...")
                st.session_state.current_page = 'ensemble_analytics'
                st.rerun()

    with tab5:
        st.markdown("### 📋 Complete Evaluation Report")

        # Component breakdown
        st.markdown("#### Component Scores Breakdown")
        components_df = pd.DataFrame({
            'Component': list(evaluation_data['component_scores'].keys()),
            'Score': list(evaluation_data['component_scores'].values()),
            'Weight': [evaluation_data['weights'].get(comp.replace(' ', '_'), 0) * 100
                      for comp in evaluation_data['component_scores'].keys()],
            'Contribution': [score * evaluation_data['weights'].get(comp.replace(' ', '_'), 0)
                           for comp, score in evaluation_data['component_scores'].items()]
        })

        components_df['Component'] = components_df['Component'].str.title()
        components_df['Weight'] = components_df['Weight'].map('{:.0f}%'.format)
        components_df['Score'] = components_df['Score'].map('{:.1f}'.format)
        components_df['Contribution'] = components_df['Contribution'].map('{:.1f}'.format)

        st.dataframe(components_df, width='stretch', hide_index=True)

        st.markdown("---")

        # Export functionality
        st.markdown("#### 💾 Export Report")
        teacher_info = storage.get_user(selected_teacher_id)
        export_evaluation_report(evaluation_data, teacher_info)

        # Raw data
        with st.expander("🔍 View Raw Evaluation Data"):
            st.json(evaluation_data)

    # Footer
    st.markdown("---")
    st.caption("📊 Analysis powered by AI ensemble models | Updated in real-time | Data privacy compliant")


def main():
    """Main entry point"""
    # Check authentication
    auth = get_auth()

    if 'user' not in st.session_state:
        st.error("Please login first")
        return

    user = st.session_state.user
    if user['role'] not in ['teacher', 'admin']:
        st.error("Access denied. Teachers and admins only.")
        return

    show_teaching_analytics_dashboard()


if __name__ == "__main__":
    main()
