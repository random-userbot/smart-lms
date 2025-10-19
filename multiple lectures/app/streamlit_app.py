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

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #555;
        text-align: center;
        margin-bottom: 1rem;
    }
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background-color: #f8f9fa;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #155a8a;
    }
    .success-message {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        color: #155724;
    }
    .error-message {
        padding: 1rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        color: #721c24;
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
    
    # Show demo credentials
    with st.expander("🔑 Demo Credentials"):
        st.markdown("""
        **Admin Account:**
        - Username: `admin`
        - Password: `admin123`
        
        **Teacher Account:**
        - Username: `dr_ramesh`
        - Password: `teacher123`
        
        **Student Account:**
        - Username: `demo_student`
        - Password: `student123`
        """)


def show_login_form():
    """Display login form"""
    st.markdown("### Login to your account")
    
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submit = st.form_submit_button("🔓 Login")
        
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
    """Display registration form"""
    st.markdown("### Create a new account")
    
    with st.form("register_form"):
        username = st.text_input("Username", placeholder="Choose a username")
        full_name = st.text_input("Full Name", placeholder="Enter your full name")
        email = st.text_input("Email", placeholder="your.email@university.edu")
        password = st.text_input("Password", type="password", placeholder="Choose a strong password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
        role = st.selectbox("Role", ["student", "teacher"], index=0)
        
        submit = st.form_submit_button("📝 Register")
        
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
    if page == 'upload' and role == 'teacher':
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
    
    if st.button("📊 Dashboard", use_container_width=True):
        st.session_state.current_page = 'dashboard'
        st.rerun()
    
    if st.button("👥 Manage Users", use_container_width=True):
        st.session_state.current_page = 'users'
        st.rerun()
    
    if st.button("📚 Manage Courses", use_container_width=True):
        st.session_state.current_page = 'courses'
        st.rerun()
    
    if st.button("📈 Analytics", use_container_width=True):
        st.session_state.current_page = 'analytics'
        st.rerun()
    
    if st.button("🌲 Teacher Evaluation", use_container_width=True):
        st.session_state.current_page = 'evaluation'
        st.rerun()
    
    if st.button("🔒 Ethical AI Dashboard", use_container_width=True):
        st.session_state.current_page = 'ethical_ai'
        st.rerun()


def show_teacher_navigation():
    """Teacher navigation menu"""
    st.markdown("### 👨‍🏫 Teacher Panel")
    
    if st.button("📊 Dashboard", use_container_width=True):
        st.session_state.current_page = 'dashboard'
        st.rerun()
    
    if st.button("📚 My Courses", use_container_width=True):
        st.session_state.current_page = 'courses'
        st.rerun()
    
    if st.button("📤 Upload Content", use_container_width=True):
        st.session_state.current_page = 'upload'
        st.rerun()
    
    if st.button("📈 Analytics", use_container_width=True):
        st.session_state.current_page = 'analytics'
        st.rerun()
    
    if st.button("👥 Students", use_container_width=True):
        st.session_state.current_page = 'students'
        st.rerun()
    
    if st.button("📅 Attendance", use_container_width=True):
        st.session_state.current_page = 'attendance'
        st.rerun()


def show_student_navigation():
    """Student navigation menu"""
    st.markdown("### 🎓 Student Panel")
    
    if st.button("📊 Dashboard", use_container_width=True):
        st.session_state.current_page = 'dashboard'
        st.rerun()
    
    if st.button("📚 My Courses", use_container_width=True):
        st.session_state.current_page = 'courses'
        st.rerun()
    
    if st.button("🎥 Lectures", use_container_width=True):
        st.session_state.current_page = 'lectures'
        st.rerun()
    
    if st.button("📝 Quizzes", use_container_width=True):
        st.session_state.current_page = 'quizzes'
        st.rerun()
    
    if st.button("📋 Assignments", use_container_width=True):
        st.session_state.current_page = 'assignments'
        st.rerun()
    
    if st.button("📈 My Progress", use_container_width=True):
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
    
    # Statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📚 Enrolled Courses", len(enrolled_courses))
    
    with col2:
        # Get student grades
        grades = storage.get_student_grades(user['user_id'])
        avg_quiz_score = 0
        if grades.get('quizzes'):
            avg_quiz_score = sum(q['percentage'] for q in grades['quizzes']) / len(grades['quizzes'])
        st.metric("📝 Avg Quiz Score", f"{avg_quiz_score:.1f}%")
    
    with col3:
        # Get engagement logs
        engagement_logs = storage.get_engagement_logs(student_id=user['user_id'])
        avg_engagement = 0
        if engagement_logs:
            avg_engagement = sum(log['engagement_score'] for log in engagement_logs) / len(engagement_logs)
        st.metric("📊 Avg Engagement", f"{avg_engagement:.1f}/100")
    
    st.markdown("---")
    
    # Course list
    st.subheader("📚 My Courses")
    
    if enrolled_courses:
        for course_id, course in enrolled_courses.items():
            with st.expander(f"📖 {course['name']}", expanded=True):
                st.write(f"**Teacher:** {course.get('teacher_id', 'N/A')}")
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
                    if st.button(f"📈 My Progress", key=f"progress_{course_id}"):
                        st.session_state.selected_course = course_id
                        st.session_state.current_page = 'progress'
                        st.rerun()
    else:
        st.info("📝 You are not enrolled in any courses yet.")
        st.markdown("Contact your administrator to enroll in courses.")


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
