"""
Theme Configuration for Smart LMS
Modern EdTech and Dark Academic themes
"""

# Modern EdTech Theme (Light)
THEME_LIGHT = {
    'name': 'Modern EdTech',
    'colors': {
        'primary': '#2563EB',
        'accent': '#22C55E',
        'background': '#F8FAFC',
        'card': '#FFFFFF',
        'sidebar': '#FFFFFF',
        'text': '#0F172A',
        'text_secondary': '#64748B',
        'border': '#E2E8F0',
        'success': '#22C55E',
        'warning': '#F59E0B',
        'error': '#EF4444',
        'info': '#3B82F6'
    },
    'fonts': {
        'primary': 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
        'heading': 'Inter, sans-serif',
        'mono': 'JetBrains Mono, monospace'
    },
    'spacing': {
        'card_padding': '24px',
        'section_gap': '32px',
        'border_radius': '12px'
    }
}

# Dark Academic Theme (Dark)
THEME_DARK = {
    'name': 'Dark Academic',
    'colors': {
        'primary': '#38BDF8',
        'accent': '#818CF8',
        'background': '#0F172A',
        'card': '#1E293B',
        'sidebar': '#020617',
        'text': '#E5E7EB',
        'text_secondary': '#94A3B8',
        'border': '#334155',
        'success': '#34D399',
        'warning': '#FBBF24',
        'error': '#F87171',
        'info': '#60A5FA'
    },
    'fonts': {
        'primary': 'IBM Plex Sans, -apple-system, BlinkMacSystemFont, sans-serif',
        'heading': 'IBM Plex Sans, sans-serif',
        'mono': 'IBM Plex Mono, monospace'
    },
    'spacing': {
        'card_padding': '24px',
        'section_gap': '32px',
        'border_radius': '12px'
    }
}


def get_theme_css(theme='light'):
    """Generate complete CSS for the selected theme"""
    t = THEME_LIGHT if theme == 'light' else THEME_DARK
    
    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600;700&family=JetBrains+Mono&family=IBM+Plex+Mono&display=swap');
        
        /* Global Styles */
        .stApp {{
            background-color: {t['colors']['background']};
            font-family: {t['fonts']['primary']};
            color: {t['colors']['text']};
        }}
        
        /* Sidebar */
        [data-testid="stSidebar"] {{
            background-color: {t['colors']['sidebar']};
            border-right: 1px solid {t['colors']['border']};
        }}
        
        [data-testid="stSidebar"] .element-container {{
            margin-bottom: 8px;
        }}
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {{
            font-family: {t['fonts']['heading']};
            font-weight: 700;
            color: {t['colors']['text']};
        }}
        
        h1 {{
            font-size: 2.25rem;
            margin-bottom: 1rem;
        }}
        
        h2 {{
            font-size: 1.875rem;
            margin-bottom: 0.875rem;
        }}
        
        h3 {{
            font-size: 1.5rem;
            margin-bottom: 0.75rem;
        }}
        
        /* Cards */
        .css-1r6slb0, .css-12oz5g7 {{
            background-color: {t['colors']['card']};
            border-radius: {t['spacing']['border_radius']};
            padding: {t['spacing']['card_padding']};
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
            border: 1px solid {t['colors']['border']};
        }}
        
        /* Buttons */
        .stButton > button {{
            background-color: {t['colors']['primary']};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.625rem 1.5rem;
            font-weight: 600;
            font-size: 0.95rem;
            transition: all 0.2s ease;
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        }}
        
        .stButton > button:hover {{
            background-color: {t['colors']['primary']};
            opacity: 0.9;
            transform: translateY(-1px);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}
        
        /* Secondary Button */
        .stButton[data-baseweb="button-secondary"] > button {{
            background-color: transparent;
            color: {t['colors']['primary']};
            border: 2px solid {t['colors']['border']};
        }}
        
        .stButton[data-baseweb="button-secondary"] > button:hover {{
            background-color: {t['colors']['background']};
            border-color: {t['colors']['primary']};
        }}
        
        /* Metrics */
        [data-testid="stMetric"] {{
            background-color: {t['colors']['card']};
            padding: 1.25rem;
            border-radius: {t['spacing']['border_radius']};
            border: 1px solid {t['colors']['border']};
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        }}
        
        [data-testid="stMetricValue"] {{
            font-size: 2rem;
            font-weight: 700;
            color: {t['colors']['primary']};
        }}
        
        [data-testid="stMetricLabel"] {{
            color: {t['colors']['text_secondary']};
            font-size: 0.875rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        /* Inputs */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {{
            background-color: {t['colors']['card']};
            border: 1px solid {t['colors']['border']};
            border-radius: 8px;
            color: {t['colors']['text']};
            padding: 0.625rem 1rem;
            font-size: 0.95rem;
        }}
        
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {{
            border-color: {t['colors']['primary']};
            box-shadow: 0 0 0 3px {t['colors']['primary']}20;
        }}
        
        /* Selectbox/Dropdown complete styling */
        .stSelectbox > div > div,
        [data-baseweb="select"],
        [data-baseweb="select"] > div,
        [data-baseweb="popover"] {{
            background-color: {t['colors']['card']} !important;
            color: {t['colors']['text']} !important;
        }}
        
        .stSelectbox [data-baseweb="select"] {{
            background-color: {t['colors']['card']} !important;
            border: 1px solid {t['colors']['border']} !important;
            border-radius: 8px !important;
        }}
        
        .stSelectbox [role="option"] {{
            background-color: {t['colors']['card']} !important;
            color: {t['colors']['text']} !important;
        }}
        
        .stSelectbox [role="option"]:hover {{
            background-color: {t['colors']['primary']}10 !important;
        }}
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            background-color: transparent;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background-color: {t['colors']['card']};
            border-radius: 8px;
            color: {t['colors']['text_secondary']};
            padding: 0.625rem 1.25rem;
            border: 1px solid {t['colors']['border']};
            font-weight: 500;
        }}
        
        .stTabs [aria-selected="true"] {{
            background-color: {t['colors']['primary']};
            color: white;
            border-color: {t['colors']['primary']};
        }}
        
        /* Progress Bar */
        .stProgress > div > div > div {{
            background-color: {t['colors']['primary']};
        }}
        
        /* Info/Warning/Error Boxes */
        .stAlert {{
            border-radius: 8px;
            border-left: 4px solid;
            padding: 1rem;
        }}
        
        [data-testid="stNotification"] {{
            border-radius: 8px;
        }}
        
        /* Success */
        .stSuccess, [data-baseweb="notification"][kind="success"] {{
            background-color: {t['colors']['success']}10;
            border-left-color: {t['colors']['success']};
            color: {t['colors']['success']};
        }}
        
        /* Info */
        .stInfo, [data-baseweb="notification"][kind="info"] {{
            background-color: {t['colors']['info']}10;
            border-left-color: {t['colors']['info']};
            color: {t['colors']['info']};
        }}
        
        /* Warning */
        .stWarning, [data-baseweb="notification"][kind="warning"] {{
            background-color: {t['colors']['warning']}10;
            border-left-color: {t['colors']['warning']};
            color: {t['colors']['warning']};
        }}
        
        /* Error */
        .stError, [data-baseweb="notification"][kind="error"] {{
            background-color: {t['colors']['error']}10;
            border-left-color: {t['colors']['error']};
            color: {t['colors']['error']};
        }}
        
        /* Dataframe/Table */
        .stDataFrame {{
            border-radius: 8px;
            overflow: hidden;
        }}
        
        /* Custom Card Class */
        .custom-card {{
            background-color: {t['colors']['card']};
            padding: {t['spacing']['card_padding']};
            border-radius: {t['spacing']['border_radius']};
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
            border: 1px solid {t['colors']['border']};
            margin-bottom: 1rem;
        }}
        
        /* Stat Card */
        .stat-card {{
            background: linear-gradient(135deg, {t['colors']['primary']}15 0%, {t['colors']['accent']}15 100%);
            border: 1px solid {t['colors']['border']};
            border-radius: {t['spacing']['border_radius']};
            padding: 1.5rem;
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 2.5rem;
            font-weight: 700;
            color: {t['colors']['primary']};
            font-family: {t['fonts']['mono']};
        }}
        
        .stat-label {{
            color: {t['colors']['text_secondary']};
            font-size: 0.875rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-top: 0.5rem;
        }}
        
        /* Spacing */
        .section-gap {{
            margin-top: {t['spacing']['section_gap']};
            margin-bottom: {t['spacing']['section_gap']};
        }}
        
        /* Hover Effects */
        .hover-lift {{
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        
        .hover-lift:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }}
        
        /* Hide Streamlit Branding */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        
        /* Scrollbar */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: {t['colors']['background']};
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: {t['colors']['border']};
            border-radius: 4px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: {t['colors']['text_secondary']};
        }}
    </style>
    """


def render_stat_card(label, value, icon="📊", color=None):
    """Render a beautiful stat card"""
    return f"""
    <div class="stat-card hover-lift">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
        <div class="stat-value">{value}</div>
        <div class="stat-label">{label}</div>
    </div>
    """
