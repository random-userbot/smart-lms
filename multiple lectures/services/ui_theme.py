"""
Smart LMS - UI Theme Service
Light/Dark mode toggle and aesthetic styling
"""

import streamlit as st
from typing import Dict


class ThemeManager:
    """Manage UI themes and styling"""
    
    def __init__(self):
        # Initialize theme in session state
        if 'theme' not in st.session_state:
            st.session_state.theme = 'light'
    
    def get_theme(self) -> str:
        """Get current theme"""
        return st.session_state.get('theme', 'light')
    
    def toggle_theme(self):
        """Toggle between light and dark mode"""
        current = st.session_state.get('theme', 'light')
        st.session_state.theme = 'dark' if current == 'light' else 'light'
    
    def get_colors(self) -> Dict[str, str]:
        """Get color palette for current theme"""
        if self.get_theme() == 'dark':
            return {
                'primary': '#4A90E2',
                'secondary': '#7B68EE',
                'success': '#50C878',
                'warning': '#FFB347',
                'danger': '#FF6B6B',
                'info': '#5DADE2',
                'background': '#1E1E1E',
                'surface': '#2D2D2D',
                'text': '#E0E0E0',
                'text_secondary': '#B0B0B0',
                'border': '#404040',
                'shadow': 'rgba(0, 0, 0, 0.5)'
            }
        else:
            return {
                'primary': '#1f77b4',
                'secondary': '#ff7f0e',
                'success': '#2ecc71',
                'warning': '#f39c12',
                'danger': '#e74c3c',
                'info': '#3498db',
                'background': '#FFFFFF',
                'surface': '#F8F9FA',
                'text': '#2C3E50',
                'text_secondary': '#7F8C8D',
                'border': '#E0E0E0',
                'shadow': 'rgba(0, 0, 0, 0.1)'
            }
    
    def apply_theme(self):
        """Apply theme styling to the app"""
        colors = self.get_colors()
        theme = self.get_theme()
        
        # Custom CSS for the theme
        css = f"""
        <style>
            /* Global Theme Variables */
            :root {{
                --primary-color: {colors['primary']};
                --secondary-color: {colors['secondary']};
                --success-color: {colors['success']};
                --warning-color: {colors['warning']};
                --danger-color: {colors['danger']};
                --background-color: {colors['background']};
                --surface-color: {colors['surface']};
                --text-color: {colors['text']};
                --border-color: {colors['border']};
            }}
            
            /* Main App Background */
            .stApp {{
                background-color: {colors['background']};
                color: {colors['text']};
            }}
            
            /* Sidebar Styling */
            [data-testid="stSidebar"] {{
                background-color: {colors['surface']};
                border-right: 1px solid {colors['border']};
            }}
            
            [data-testid="stSidebar"] .stMarkdown {{
                color: {colors['text']};
            }}
            
            /* Card Styling */
            .card {{
                background: {colors['surface']};
                border-radius: 12px;
                padding: 1.5rem;
                margin: 1rem 0;
                box-shadow: 0 4px 6px {colors['shadow']};
                border: 1px solid {colors['border']};
                transition: all 0.3s ease;
            }}
            
            .card:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 12px {colors['shadow']};
            }}
            
            /* Button Styling */
            .stButton > button {{
                background: linear-gradient(135deg, {colors['primary']} 0%, {colors['secondary']} 100%);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0.75rem 1.5rem;
                font-weight: 600;
                transition: all 0.3s ease;
                box-shadow: 0 2px 4px {colors['shadow']};
            }}
            
            .stButton > button:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 8px {colors['shadow']};
            }}
            
            /* Metric Cards */
            [data-testid="stMetricValue"] {{
                color: {colors['primary']};
                font-size: 2rem;
                font-weight: 700;
            }}
            
            [data-testid="stMetricLabel"] {{
                color: {colors['text_secondary']};
                font-size: 0.9rem;
                font-weight: 500;
            }}
            
            /* Expander Styling */
            .streamlit-expanderHeader {{
                background-color: {colors['surface']};
                border-radius: 8px;
                border: 1px solid {colors['border']};
                color: {colors['text']};
                font-weight: 600;
            }}
            
            .streamlit-expanderHeader:hover {{
                background-color: {colors['primary']};
                color: white;
            }}
            
            /* Input Fields */
            .stTextInput > div > div > input,
            .stTextArea > div > div > textarea,
            .stSelectbox > div > div > select {{
                background-color: {colors['surface']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
                border-radius: 8px;
                padding: 0.75rem;
            }}
            
            /* Success/Warning/Error Messages */
            .stSuccess {{
                background-color: {colors['success']}20;
                color: {colors['success']};
                border-left: 4px solid {colors['success']};
                border-radius: 4px;
                padding: 1rem;
            }}
            
            .stWarning {{
                background-color: {colors['warning']}20;
                color: {colors['warning']};
                border-left: 4px solid {colors['warning']};
                border-radius: 4px;
                padding: 1rem;
            }}
            
            .stError {{
                background-color: {colors['danger']}20;
                color: {colors['danger']};
                border-left: 4px solid {colors['danger']};
                border-radius: 4px;
                padding: 1rem;
            }}
            
            .stInfo {{
                background-color: {colors['info']}20;
                color: {colors['info']};
                border-left: 4px solid {colors['info']};
                border-radius: 4px;
                padding: 1rem;
            }}
            
            /* Headers */
            h1, h2, h3 {{
                color: {colors['text']};
                font-weight: 700;
            }}
            
            h1 {{
                background: linear-gradient(135deg, {colors['primary']} 0%, {colors['secondary']} 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            
            /* Tabs */
            .stTabs [data-baseweb="tab-list"] {{
                gap: 8px;
                background-color: {colors['surface']};
                border-radius: 8px;
                padding: 0.5rem;
            }}
            
            .stTabs [data-baseweb="tab"] {{
                background-color: transparent;
                border-radius: 6px;
                color: {colors['text']};
                font-weight: 600;
                padding: 0.75rem 1.5rem;
            }}
            
            .stTabs [aria-selected="true"] {{
                background: linear-gradient(135deg, {colors['primary']} 0%, {colors['secondary']} 100%);
                color: white;
            }}
            
            /* Progress Bar */
            .stProgress > div > div > div > div {{
                background: linear-gradient(90deg, {colors['primary']} 0%, {colors['secondary']} 100%);
            }}
            
            /* File Uploader */
            [data-testid="stFileUploader"] {{
                background-color: {colors['surface']};
                border: 2px dashed {colors['border']};
                border-radius: 8px;
                padding: 2rem;
            }}
            
            /* Dataframe */
            .dataframe {{
                background-color: {colors['surface']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
                border-radius: 8px;
            }}
            
            /* Scrollbar */
            ::-webkit-scrollbar {{
                width: 10px;
                height: 10px;
            }}
            
            ::-webkit-scrollbar-track {{
                background: {colors['surface']};
            }}
            
            ::-webkit-scrollbar-thumb {{
                background: {colors['primary']};
                border-radius: 5px;
            }}
            
            ::-webkit-scrollbar-thumb:hover {{
                background: {colors['secondary']};
            }}
            
            /* Animations */
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(10px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            
            .card {{
                animation: fadeIn 0.5s ease-out;
            }}
            
            /* Theme Toggle Button */
            .theme-toggle {{
                position: fixed;
                top: 1rem;
                right: 1rem;
                z-index: 999;
                background: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 50%;
                width: 50px;
                height: 50px;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                box-shadow: 0 2px 8px {colors['shadow']};
                transition: all 0.3s ease;
            }}
            
            .theme-toggle:hover {{
                transform: scale(1.1);
                box-shadow: 0 4px 12px {colors['shadow']};
            }}
            
            /* Badge Styling */
            .badge {{
                display: inline-block;
                padding: 0.25rem 0.75rem;
                border-radius: 12px;
                font-size: 0.85rem;
                font-weight: 600;
                margin: 0.25rem;
            }}
            
            .badge-success {{
                background-color: {colors['success']}20;
                color: {colors['success']};
                border: 1px solid {colors['success']};
            }}
            
            .badge-warning {{
                background-color: {colors['warning']}20;
                color: {colors['warning']};
                border: 1px solid {colors['warning']};
            }}
            
            .badge-danger {{
                background-color: {colors['danger']}20;
                color: {colors['danger']};
                border: 1px solid {colors['danger']};
            }}
            
            .badge-info {{
                background-color: {colors['info']}20;
                color: {colors['info']};
                border: 1px solid {colors['info']};
            }}
        </style>
        """
        
        st.markdown(css, unsafe_allow_html=True)
    
    def render_theme_toggle(self):
        """Render theme toggle button in sidebar"""
        theme = self.get_theme()
        icon = "🌙" if theme == 'light' else "☀️"
        label = "Dark Mode" if theme == 'light' else "Light Mode"
        
        if st.sidebar.button(f"{icon} {label}", use_container_width=True, key="theme_toggle"):
            self.toggle_theme()
            st.rerun()
    
    def create_card(self, content: str, title: str = None):
        """Create a styled card"""
        if title:
            st.markdown(f"""
            <div class="card">
                <h3>{title}</h3>
                {content}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="card">
                {content}
            </div>
            """, unsafe_allow_html=True)
    
    def create_badge(self, text: str, badge_type: str = "info"):
        """Create a styled badge"""
        return f'<span class="badge badge-{badge_type}">{text}</span>'


# Singleton instance
_theme_manager = None

def get_theme_manager() -> ThemeManager:
    """Get theme manager singleton"""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager
