"""
Smart LMS - Main Streamlit Application
Role-based Learning Management System with AI-powered features
"""

import streamlit as st
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.auth import get_auth
from services.storage import get_storage
from services.ui_theme import get_theme_manager


# Page configuration
st.set_page_config(
    page_title="Smart LMS",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI and visibility
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background-color: #ffffff;
    }
    
    /* Headers with high contrast */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    .sub-header {
        font-size: 1.5rem;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    /* Login/Register container */
    .login-container {
        max-width: 500px;
        margin: 0 auto;
        padding: 2rem;
        background-color: #f8f9fa;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }
    
    /* Improve text input visibility */
    .stTextInput > div > div > input {
        background-color: #ffffff !important;
        color: #2c3e50 !important;
        border: 2px solid #ddd !important;
        font-size: 16px !important;
        padding: 12px !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #95a5a6 !important;
        opacity: 1 !important;
    }
    
    .stTextInput > label {
        color: #2c3e50 !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        margin-bottom: 8px !important;
    }
    
    /* Improve selectbox visibility */
    .stSelectbox > div > div > div {
        background-color: #ffffff !important;
        color: #2c3e50 !important;
        border: 2px solid #ddd !important;
    }
    
    .stSelectbox > label {
        color: #2c3e50 !important;
        font-weight: 600 !important;
        font-size: 16px !important;
    }
    
    /* Button styling with high contrast */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #1f77b4 0%, #155a8a 100%);
        color: white !important;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: bold;
        font-size: 16px;
        border: none;
        box-shadow: 0 4px 10px rgba(31, 119, 180, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #155a8a 0%, #0d3d5c 100%);
        box-shadow: 0 6px 15px rgba(31, 119, 180, 0.4);
        transform: translateY(-2px);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        color: #2c3e50 !important;
        border-radius: 6px;
        padding: 10px 20px;
        font-weight: 600;
        border: 2px solid transparent;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1f77b4 0%, #155a8a 100%);
        color: white !important;
        border-color: #1f77b4;
    }
    
    /* Expander styling */
    .stExpander {
        background-color: #ffffff;
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    
    .stExpander > div > div > div > div {
        color: #2c3e50 !important;
        font-weight: 600;
    }
    
    /* Messages */
    .success-message {
        padding: 1rem;
        background-color: #d4edda;
        border: 2px solid #c3e6cb;
        border-radius: 8px;
        color: #155724 !important;
        font-weight: 600;
    }
    
    .error-message {
        padding: 1rem;
        background-color: #f8d7da;
        border: 2px solid #f5c6cb;
        border-radius: 8px;
        color: #721c24 !important;
        font-weight: 600;
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        color: #2c3e50 !important;
        font-size: 2rem !important;
        font-weight: bold !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #555 !important;
        font-weight: 600 !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    
    [data-testid="stSidebar"] .stButton>button {
        background-color: #ffffff;
        color: #2c3e50 !important;
        border: 2px solid #e0e0e0;
        margin-bottom: 8px;
    }
    
    [data-testid="stSidebar"] .stButton>button:hover {
        background: linear-gradient(135deg, #1f77b4 0%, #155a8a 100%);
        color: white !important;
        border-color: #1f77b4;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        border: 2px solid #e0e0e0;
        border-radius: 8px;
    }
    
    /* Markdown text */
    .stMarkdown {
        color: #2c3e50 !important;
    }
    
    /* Info/Warning/Error boxes */
    .stAlert {
        border-radius: 8px;
        border-width: 2px;
    }
    
    /* Form labels */
    label {
        color: #2c3e50 !important;
        font-weight: 600 !important;
    }
    
    /* Checkbox */
    .stCheckbox > label {
        color: #2c3e50 !important;
        font-weight: 500 !important;
    }
    
    /* File uploader */
    .stFileUploader > div {
        background-color: #ffffff;
        border: 2px dashed #1f77b4;
        border-radius: 8px;
        padding: 20px;
    }
    
    .stFileUploader label {
        color: #2c3e50 !important;
        font-weight: 600 !important;
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background-color: #1f77b4;
    }
    
    /* Text area */
    .stTextArea > div > div > textarea {
        background-color: #ffffff !important;
        color: #2c3e50 !important;
        border: 2px solid #ddd !important;
        font-size: 16px !important;
    }
    
    .stTextArea > label {
        color: #2c3e50 !important;
        font-weight: 600 !important;
    }
    
    /* Number input */
    .stNumberInput > div > div > input {
        background-color: #ffffff !important;
        color: #2c3e50 !important;
        border: 2px solid #ddd !important;
    }
    
    .stNumberInput > label {
        color: #2c3e50 !important;
        font-weight: 600 !important;
    }
    
    /* Download button */
    .stDownloadButton > button {
        background-color: #28a745 !important;
        color: white !important;
    }
    
    .stDownloadButton > button:hover {
        background-color: #218838 !important;
    }
    
    /* High contrast for all text */
    p, span, div {
        color: #2c3e50;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #1f77b4 !important;
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)


def show_login_page():
    """Display login page"""
    st.markdown('<div class="main-header">🎓 Smart LMS</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-Powered Learning Management System</div>', unsafe_allow_html=True)
    
    # Create tabs for login and register
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        show_login_form()
    
    with tab2:
        show_register_form()


def show_login_form():
    """Display login form with clear labels and red cursor"""
    # Add custom CSS for red cursor in login form
    st.markdown("""
    <style>
    /* Red cursor for login form inputs */
    div[data-testid="stForm"] input[type="text"],
    div[data-testid="stForm"] input[type="password"] {
        caret-color: #dc3545 !important;
    }
    
    /* Enhanced input field styling for login */
    div[data-testid="stForm"] input {
        border: 2px solid #007bff !important;
        border-radius: 8px !important;
        padding: 12px !important;
        font-size: 16px !important;
    }
    
    div[data-testid="stForm"] input:focus {
        border-color: #0056b3 !important;
        box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25) !important;
        caret-color: #dc3545 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🔐 Login to your account")
    st.markdown("---")
    
    with st.form("login_form", clear_on_submit=False):
        st.markdown("#### Enter your credentials")
        username = st.text_input(
            "👤 Username", 
            placeholder="Enter your username",
            help="Use your registered username",
            key="login_username"
        )
        password = st.text_input(
            "🔒 Password", 
            type="password", 
            placeholder="Enter your password",
            help="Enter your password",
            key="login_password"
        )
        
        st.markdown("")  # Spacing
        submit = st.form_submit_button("🔓 Login", use_container_width=True, type="primary")
        
        if submit:
            if not username or not password:
                st.error("❌ Please enter both username and password")
                return
            
            auth = get_auth()
            user = auth.login(username, password)
            
            if user:
                st.session_state.user = user
                st.success(f"✅ Welcome back, {user['full_name']}!")
                st.rerun()
            else:
                st.error("❌ Invalid username or password")


def show_register_form():
    """Display registration form with clear labels"""
    st.markdown("### 📝 Create a new account")
    st.markdown("---")
    
    with st.form("register_form", clear_on_submit=False):
        st.markdown("#### Registration Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input(
                "👤 Username *", 
                placeholder="Choose a unique username",
                help="This will be used to login",
                key="register_username"
            )
            full_name = st.text_input(
                "📝 Full Name *", 
                placeholder="Enter your full name",
                help="Your complete name",
                key="register_fullname"
            )
            email = st.text_input(
                "📧 Email *", 
                placeholder="your.email@university.edu",
                help="Your email address",
                key="register_email"
            )
        
        with col2:
            password = st.text_input(
                "🔒 Password *", 
                type="password", 
                placeholder="Choose a strong password",
                help="Minimum 6 characters",
                key="register_password"
            )
            confirm_password = st.text_input(
                "🔒 Confirm Password *", 
                type="password", 
                placeholder="Re-enter your password",
                help="Must match the password above",
                key="register_confirm_password"
            )
            role = st.selectbox(
                "🎯 Role *", 
                ["student", "teacher"], 
                index=0,
                help="Select your role in the system",
                key="register_role"
            )
        
        st.markdown("---")
        st.markdown("*Required fields")
        st.markdown("")  # Spacing
        
        submit = st.form_submit_button("📝 Create Account", use_container_width=True, type="primary")
        
        if submit:
            # Validation
            if not all([username, full_name, email, password, confirm_password]):
                st.error("❌ Please fill in all fields")
                return
            
            if password != confirm_password:
                st.error("❌ Passwords do not match")
                return
            
            if len(password) < 6:
                st.error("❌ Password must be at least 6 characters long")
                return
            
            # Register user
            auth = get_auth()
            success = auth.register(
                username=username,
                password=password,
                role=role,
                email=email,
                full_name=full_name
            )
            
            if success:
                st.success("✅ Registration successful! Please login.")
            else:
                st.error("❌ Username already exists. Please choose a different username.")


def show_dashboard():
    """Display role-based dashboard"""
    user = st.session_state.user
    role = user['role']
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown(f"### 👤 {user['full_name']}")
        st.markdown(f"**Role:** {role.capitalize()}")
        st.markdown("---")
        
        # Theme toggle
        theme_manager = get_theme_manager()
        theme_manager.render_theme_toggle()
        st.markdown("---")
        
        # Role-based navigation
        if role == 'admin':
            show_admin_navigation()
        elif role == 'teacher':
            show_teacher_navigation()
        elif role == 'student':
            show_student_navigation()
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            auth = get_auth()
            auth.logout()
            st.rerun()
    
    # Main content area
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'dashboard'
    
    # Route to appropriate page based on current_page
    page = st.session_state.current_page
    
    # Import page modules
    if page == 'users' and role == 'admin':
        from pages import users
        users.main()
    elif page == 'courses' and role in ['admin', 'teacher']:
        from pages import courses
        courses.main()
    elif page == 'student_courses' and role == 'student':
        from pages import student_courses
        student_courses.main()
    elif page == 'enrollment_requests' and role in ['teacher', 'admin']:
        from pages import enrollment_requests
        enrollment_requests.main()
    elif page == 'resources':
        from pages import resources
        resources.main()
    elif page == 'upload' and role == 'teacher':
        from pages import upload
        upload.main()
    elif page in ['lectures', 'watch_lecture'] and role == 'student':
        from pages import lectures
        lectures.main()
    elif page in ['quizzes', 'take_quiz'] and role == 'student':
        from pages import quizzes
        quizzes.main()
    elif page in ['assignments', 'submit_assignment'] and role == 'student':
        from pages import assignments
        assignments.main()
    elif page == 'progress':
        from pages import progress
        progress.main()
    elif page == 'attendance':
        from pages import attendance
        attendance.main()
    elif page == 'teacher_evaluation':
        from pages import teacher_evaluation
        teacher_evaluation.show_teacher_evaluation()
    elif page == 'dashboard':
        if role == 'admin':
            show_admin_dashboard()
        elif role == 'teacher':
            show_teacher_dashboard()
        elif role == 'student':
            show_student_dashboard()
    else:
        # Default dashboard
        if role == 'admin':
            show_admin_dashboard()
        elif role == 'teacher':
            show_teacher_dashboard()
        elif role == 'student':
            show_student_dashboard()


def show_admin_navigation():
    """Admin navigation menu"""
    st.markdown("### 🔧 Admin Panel")
    
    if st.button("📊 Dashboard", key="admin_nav_dashboard", use_container_width=True):
        st.session_state.current_page = 'dashboard'
        st.rerun()
    
    if st.button("👥 Manage Users", key="admin_nav_users", use_container_width=True):
        st.session_state.current_page = 'users'
        st.rerun()
    
    if st.button("📚 Manage Courses", key="admin_nav_courses", use_container_width=True):
        st.session_state.current_page = 'courses'
        st.rerun()
    
    if st.button("� Resources", key="admin_nav_resources", use_container_width=True):
        st.session_state.current_page = 'resources'
        st.rerun()
    
    if st.button("�📈 Analytics", key="admin_nav_analytics", use_container_width=True):
        st.session_state.current_page = 'analytics'
        st.rerun()
    
    if st.button("🌲 Teacher Evaluation", key="admin_nav_evaluation", use_container_width=True):
        st.session_state.current_page = 'evaluation'
        st.rerun()
    
    if st.button("🔒 Ethical AI Dashboard", key="admin_nav_ethical", use_container_width=True):
        st.session_state.current_page = 'ethical_ai'
        st.rerun()


def show_teacher_navigation():
    """Teacher navigation menu"""
    st.markdown("### 👨‍🏫 Teacher Panel")
    
    if st.button("📊 Dashboard", key="teacher_nav_dashboard", use_container_width=True):
        st.session_state.current_page = 'dashboard'
        st.rerun()
    
    if st.button("📚 My Courses", key="teacher_nav_courses", use_container_width=True):
        st.session_state.current_page = 'courses'
        st.rerun()
    
    if st.button("📤 Upload Content", key="teacher_nav_upload", use_container_width=True):
        st.session_state.current_page = 'upload'
        st.rerun()
    
    if st.button("📝 Enrollment Requests", key="teacher_nav_enrollment", use_container_width=True):
        st.session_state.current_page = 'enrollment_requests'
        st.rerun()
    
    if st.button("�‍🏫 My Evaluation", key="teacher_nav_evaluation", use_container_width=True):
        st.session_state.current_page = 'teacher_evaluation'
        st.rerun()
    
    if st.button("�📄 Resources", key="teacher_nav_resources", use_container_width=True):
        st.session_state.current_page = 'resources'
        st.rerun()
    
    if st.button("📈 Analytics", key="teacher_nav_analytics", use_container_width=True):
        st.session_state.current_page = 'analytics'
        st.rerun()
    
    if st.button("👥 Students", key="teacher_nav_students", use_container_width=True):
        st.session_state.current_page = 'students'
        st.rerun()
    
    if st.button("📅 Attendance", key="teacher_nav_attendance", use_container_width=True):
        st.session_state.current_page = 'attendance'
        st.rerun()


def show_student_navigation():
    """Student navigation menu"""
    st.markdown("### 🎓 Student Panel")
    
    if st.button("📊 Dashboard", key="nav_dashboard", use_container_width=True):
        st.session_state.current_page = 'dashboard'
        st.rerun()
    
    if st.button("📚 Browse Courses", key="nav_browse_courses", use_container_width=True):
        st.session_state.current_page = 'student_courses'
        st.rerun()
    
    if st.button("🎥 My Lectures", key="nav_my_lectures", use_container_width=True):
        st.session_state.current_page = 'lectures'
        st.rerun()
    
    if st.button("📄 Resources", key="nav_resources", use_container_width=True):
        st.session_state.current_page = 'resources'
        st.rerun()
    
    if st.button("📝 Quizzes", key="nav_quizzes", use_container_width=True):
        st.session_state.current_page = 'quizzes'
        st.rerun()
    
    if st.button("📋 Assignments", key="nav_assignments", use_container_width=True):
        st.session_state.current_page = 'assignments'
        st.rerun()
    
    if st.button("📈 My Progress", key="nav_progress", use_container_width=True):
        st.session_state.current_page = 'progress'
        st.rerun()


def show_admin_dashboard():
    """Admin dashboard content"""
    st.title("🔧 Admin Dashboard")
    
    storage = get_storage()
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        users = storage.get_all_users()
        st.metric("👥 Total Users", len(users))
    
    with col2:
        students = storage.get_all_users(role='student')
        st.metric("🎓 Students", len(students))
    
    with col3:
        teachers = storage.get_all_users(role='teacher')
        st.metric("👨‍🏫 Teachers", len(teachers))
    
    with col4:
        courses = storage.get_all_courses()
        st.metric("📚 Courses", len(courses))
    
    st.markdown("---")
    
    # Recent activity
    st.subheader("📊 System Overview")
    st.info("Admin dashboard with full system statistics will be displayed here.")
    st.markdown("Navigate using the sidebar to manage users, courses, and view analytics.")


def show_teacher_dashboard():
    """Teacher dashboard content"""
    st.title("👨‍🏫 Teacher Dashboard")
    
    user = st.session_state.user
    storage = get_storage()
    
    # Get teacher's courses
    courses = storage.get_all_courses(teacher_id=user['user_id'])
    
    # Statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📚 My Courses", len(courses))
    
    with col2:
        total_students = sum(len(c.get('enrolled_students', [])) for c in courses.values())
        st.metric("👥 Total Students", total_students)
    
    with col3:
        total_lectures = 0
        for course in courses.values():
            total_lectures += len(course.get('lectures', []))
        st.metric("🎥 Total Lectures", total_lectures)
    
    st.markdown("---")
    
    # Course list
    st.subheader("📚 My Courses")
    
    if courses:
        for course_id, course in courses.items():
            with st.expander(f"📖 {course['name']}"):
                st.write(f"**Description:** {course.get('description', 'No description')}")
                st.write(f"**Enrolled Students:** {len(course.get('enrolled_students', []))}")
                st.write(f"**Lectures:** {len(course.get('lectures', []))}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"📈 View Analytics", key=f"analytics_{course_id}"):
                        st.session_state.selected_course = course_id
                        st.session_state.current_page = 'analytics'
                        st.rerun()
                
                with col2:
                    if st.button(f"📤 Upload Content", key=f"upload_{course_id}"):
                        st.session_state.selected_course = course_id
                        st.session_state.current_page = 'upload'
                        st.rerun()
    else:
        st.info("📝 No courses assigned yet. Contact admin to create courses.")


def show_student_dashboard():
    """Student dashboard content"""
    st.title("🎓 Student Dashboard")
    
    user = st.session_state.user
    storage = get_storage()
    
    # Get all courses
    all_courses = storage.get_all_courses()
    
    # Filter enrolled courses
    enrolled_courses = {
        cid: c for cid, c in all_courses.items()
        if user['user_id'] in c.get('enrolled_students', [])
    }
    
    # Get pending requests
    pending_requests = storage.get_enrollment_requests(student_id=user['user_id'], status='pending')
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📚 Enrolled Courses", len(enrolled_courses))
    
    with col2:
        st.metric("⏳ Pending Requests", len(pending_requests))
    
    with col3:
        # Get student grades
        grades = storage.get_student_grades(user['user_id'])
        avg_quiz_score = 0
        if grades.get('quizzes'):
            avg_quiz_score = sum(q['percentage'] for q in grades['quizzes']) / len(grades['quizzes'])
        st.metric("📝 Avg Quiz Score", f"{avg_quiz_score:.1f}%")
    
    with col4:
        # Get engagement logs
        engagement_logs = storage.get_engagement_logs(student_id=user['user_id'])
        avg_engagement = 0
        if engagement_logs:
            avg_engagement = sum(log['engagement_score'] for log in engagement_logs) / len(engagement_logs)
        st.metric("📊 Avg Engagement", f"{avg_engagement:.1f}/100")
    
    st.markdown("---")
    
    # Quick action buttons
    st.subheader("🚀 Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📚 Browse All Courses", key="dashboard_browse_courses", type="primary", use_container_width=True):
            st.session_state.current_page = 'student_courses'
            st.rerun()
    
    with col2:
        if enrolled_courses:
            if st.button("🎥 My Lectures", key="dashboard_my_lectures", use_container_width=True):
                st.session_state.current_page = 'lectures'
                st.rerun()
        else:
            st.button("🎥 My Lectures", key="dashboard_my_lectures_disabled", disabled=True, use_container_width=True)
    
    with col3:
        if enrolled_courses:
            if st.button("📈 My Progress", key="dashboard_my_progress", use_container_width=True):
                st.session_state.current_page = 'progress'
                st.rerun()
        else:
            st.button("📈 My Progress", key="dashboard_my_progress_disabled", disabled=True, use_container_width=True)
    
    st.markdown("---")
    
    # Recently enrolled courses
    if enrolled_courses:
        st.subheader("📚 My Enrolled Courses")
        
        for course_id, course in list(enrolled_courses.items())[:3]:  # Show top 3
            with st.expander(f"📖 {course['name']}", expanded=False):
                # Get teacher info
                teacher = storage.get_user(course.get('teacher_id'))
                teacher_name = teacher.get('full_name', 'Unknown') if teacher else 'Unknown'
                
                st.write(f"**Teacher:** {teacher_name}")
                st.write(f"**Description:** {course.get('description', 'No description')}")
                
                # Get lectures
                lectures = storage.get_course_lectures(course_id)
                st.write(f"**Lectures:** {len(lectures)}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"🎥 View Lectures", key=f"lectures_{course_id}"):
                        st.session_state.selected_course = course_id
                        st.session_state.current_page = 'lectures'
                        st.rerun()
                
                with col2:
                    if st.button(f"📝 Take Quiz", key=f"quiz_{course_id}"):
                        st.session_state.selected_course = course_id
                        st.session_state.current_page = 'quizzes'
                        st.rerun()
                
                with col3:
                    if st.button(f"📈 Progress", key=f"progress_{course_id}"):
                        st.session_state.selected_course = course_id
                        st.session_state.current_page = 'progress'
                        st.rerun()
        
        if len(enrolled_courses) > 3:
            if st.button("➕ View All My Courses", key="dashboard_view_all_courses"):
                st.session_state.current_page = 'student_courses'
                st.rerun()
    else:
        st.info("📝 You are not enrolled in any courses yet.")
        
        # Show browse button prominently
        if st.button("🔍 Browse Available Courses", key="dashboard_browse_no_courses", type="primary", use_container_width=True):
            st.session_state.current_page = 'student_courses'
            st.rerun()


def main():
    """Main application entry point"""
    # Apply theme
    theme_manager = get_theme_manager()
    theme_manager.apply_theme()
    
    # Check if user is logged in
    if 'user' not in st.session_state:
        show_login_page()
    else:
        show_dashboard()


if __name__ == "__main__":
    main()
