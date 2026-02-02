"""
Modern UI Components for Smart LMS
Consistent, beautiful components following the theme
"""

import streamlit as st


def render_page_header(title, subtitle=None, icon="🎓"):
    """Render a modern page header"""
    st.markdown(f"""
    <div style="margin-bottom: 2rem;">
        <h1 style="margin-bottom: 0.5rem;">
            <span style="font-size: 2.5rem;">{icon}</span> {title}
        </h1>
        {f'<p style="color: var(--text-secondary); font-size: 1.1rem; margin-top: 0.5rem;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)


def render_stat_cards(stats):
    """
    Render beautiful stat cards
    
    Args:
        stats: List of dicts with keys: label, value, icon, delta (optional)
    """
    cols = st.columns(len(stats))
    for col, stat in zip(cols, stats):
        with col:
            delta = stat.get('delta')
            st.metric(
                label=f"{stat.get('icon', '📊')} {stat['label']}",
                value=stat['value'],
                delta=delta if delta else None
            )


def render_card(content, title=None, icon=None):
    """Render a content card"""
    if title:
        st.markdown(f"### {icon + ' ' if icon else ''}{title}")
    
    with st.container():
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        content()
        st.markdown('</div>', unsafe_allow_html=True)


def render_action_button(label, icon="▶️", key=None, type="primary", full_width=True):
    """Render a styled action button"""
    return st.button(
        f"{icon} {label}",
        key=key,
        type=type,
        use_container_width=full_width
    )


def render_empty_state(message, icon="📭", action_label=None, action_key=None):
    """Render an empty state message"""
    st.markdown(f"""
    <div style="text-align: center; padding: 4rem 2rem;">
        <div style="font-size: 4rem; margin-bottom: 1rem;">{icon}</div>
        <p style="font-size: 1.25rem; color: var(--text-secondary); margin-bottom: 1.5rem;">{message}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if action_label and action_key:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            return st.button(action_label, key=action_key, use_container_width=True)
    return False


def render_search_filter_bar(search_placeholder="Search...", filters=None):
    """
    Render search and filter bar
    
    Args:
        search_placeholder: Placeholder text for search
        filters: Dict of filter options {label: [options]}
    
    Returns:
        Tuple of (search_query, filter_values)
    """
    if filters:
        cols = st.columns([3] + [1] * len(filters))
        search_query = cols[0].text_input(
            "🔍",
            placeholder=search_placeholder,
            label_visibility="collapsed"
        )
        
        filter_values = {}
        for i, (label, options) in enumerate(filters.items(), 1):
            filter_values[label] = cols[i].selectbox(
                label,
                options,
                label_visibility="collapsed"
            )
        
        return search_query, filter_values
    else:
        search_query = st.text_input(
            "🔍",
            placeholder=search_placeholder,
            label_visibility="collapsed"
        )
        return search_query, {}


def render_progress_ring(percentage, label, size=120):
    """Render a circular progress indicator"""
    color = "#22C55E" if percentage >= 70 else "#F59E0B" if percentage >= 40 else "#EF4444"
    
    st.markdown(f"""
    <div style="text-align: center;">
        <svg width="{size}" height="{size}" viewBox="0 0 120 120">
            <circle cx="60" cy="60" r="54" fill="none" stroke="#E5E7EB" stroke-width="8"/>
            <circle cx="60" cy="60" r="54" fill="none" stroke="{color}" stroke-width="8"
                    stroke-dasharray="{339.29 * percentage / 100} 339.29"
                    stroke-dashoffset="0"
                    transform="rotate(-90 60 60)"
                    stroke-linecap="round"/>
            <text x="60" y="65" text-anchor="middle" font-size="24" font-weight="bold" fill="{color}">
                {int(percentage)}%
            </text>
        </svg>
        <p style="margin-top: 0.5rem; font-weight: 600; color: var(--text-secondary);">{label}</p>
    </div>
    """, unsafe_allow_html=True)


def render_tag(text, color="primary"):
    """Render a small tag/badge"""
    colors = {
        "primary": "#2563EB",
        "success": "#22C55E",
        "warning": "#F59E0B",
        "error": "#EF4444",
        "info": "#3B82F6"
    }
    bg_color = colors.get(color, colors["primary"])
    
    return f"""
    <span style="
        display: inline-block;
        padding: 0.25rem 0.75rem;
        background-color: {bg_color}15;
        color: {bg_color};
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 600;
        margin-right: 0.5rem;
    ">{text}</span>
    """


def render_timeline_item(title, description, time, icon="🔵", is_complete=False):
    """Render a timeline item"""
    color = "#22C55E" if is_complete else "#94A3B8"
    
    st.markdown(f"""
    <div style="display: flex; gap: 1rem; margin-bottom: 1.5rem;">
        <div style="flex-shrink: 0;">
            <div style="
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background-color: {color}15;
                color: {color};
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.25rem;
            ">{icon}</div>
        </div>
        <div style="flex-grow: 1;">
            <h4 style="margin: 0; color: var(--text-primary);">{title}</h4>
            <p style="margin: 0.25rem 0; color: var(--text-secondary);">{description}</p>
            <p style="margin: 0; font-size: 0.875rem; color: var(--text-secondary);">{time}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
