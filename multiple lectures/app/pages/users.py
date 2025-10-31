"""
Smart LMS - Admin User Management Page
Comprehensive user management for administrators
"""

import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.auth import get_auth, AuthService
from services.storage import get_storage
from datetime import datetime
import pandas as pd
import uuid


def show_user_statistics():
    """Display user statistics"""
    storage = get_storage()
    
    all_users = storage.get_all_users()
    students = storage.get_all_users(role='student')
    teachers = storage.get_all_users(role='teacher')
    admins = storage.get_all_users(role='admin')
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 Total Users", len(all_users))
    
    with col2:
        st.metric("🎓 Students", len(students))
    
    with col3:
        st.metric("👨‍🏫 Teachers", len(teachers))
    
    with col4:
        st.metric("🔧 Admins", len(admins))


def show_user_list():
    """Display and manage user list"""
    st.subheader("👥 User Management")
    
    storage = get_storage()
    
    # Filter options
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        role_filter = st.selectbox(
            "Filter by Role",
            ["All Users", "Students", "Teachers", "Admins"]
        )
    
    with col2:
        search_query = st.text_input("🔍 Search by username or email", placeholder="Type to search...")
    
    with col3:
        st.write("")  # Spacing
        st.write("")
        if st.button("➕ Add New User", type="primary", use_container_width=True):
            st.session_state.show_add_user = True
            st.rerun()
    
    # Get users based on filter
    if role_filter == "All Users":
        users = storage.get_all_users()
    elif role_filter == "Students":
        users = storage.get_all_users(role='student')
    elif role_filter == "Teachers":
        users = storage.get_all_users(role='teacher')
    else:  # Admins
        users = storage.get_all_users(role='admin')
    
    # Apply search filter
    if search_query:
        users = {
            uid: u for uid, u in users.items()
            if search_query.lower() in u.get('username', '').lower()
            or search_query.lower() in u.get('email', '').lower()
            or search_query.lower() in u.get('full_name', '').lower()
        }
    
    # Display users
    if users:
        st.markdown(f"**Showing {len(users)} users**")
        
        for user_id, user in users.items():
            with st.expander(f"{'🎓' if user['role'] == 'student' else '👨‍🏫' if user['role'] == 'teacher' else '🔧'} {user.get('full_name', user['username'])} (@{user['username']})"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**User ID:** {user_id}")
                    st.write(f"**Username:** {user['username']}")
                    st.write(f"**Email:** {user.get('email', 'N/A')}")
                    st.write(f"**Role:** {user['role'].upper()}")
                    st.write(f"**Department:** {user.get('department', 'N/A')}")
                    
                    if user['role'] == 'teacher':
                        st.write(f"**Qualification:** {user.get('qualification', 'N/A')}")
                        st.write(f"**Specialization:** {user.get('specialization', 'N/A')}")
                    elif user['role'] == 'student':
                        st.write(f"**Enrollment:** {user.get('enrollment_number', 'N/A')}")
                        st.write(f"**Year/Semester:** Year {user.get('year', 'N/A')}, Semester {user.get('semester', 'N/A')}")
                    
                    st.write(f"**Status:** {'✅ Active' if user.get('is_active', True) else '❌ Inactive'}")
                    st.write(f"**Created:** {user.get('created_at', 'N/A')[:10]}")
                    st.write(f"**Last Login:** {user.get('last_login', 'Never')[:10] if user.get('last_login') else 'Never'}")
                
                with col2:
                    st.write("")  # Spacing
                    
                    if st.button("✏️ Edit", key=f"edit_{user_id}", use_container_width=True):
                        st.session_state.edit_user_id = user_id
                        st.session_state.show_edit_user = True
                        st.rerun()
                    
                    if user.get('is_active', True):
                        if st.button("🔒 Deactivate", key=f"deactivate_{user_id}", use_container_width=True):
                            storage.update_user(user_id, {'is_active': False})
                            st.success(f"User {user['username']} deactivated")
                            st.rerun()
                    else:
                        if st.button("✅ Activate", key=f"activate_{user_id}", use_container_width=True):
                            storage.update_user(user_id, {'is_active': True})
                            st.success(f"User {user['username']} activated")
                            st.rerun()
                    
                    if st.button("🔄 Reset Password", key=f"reset_{user_id}", use_container_width=True):
                        st.session_state.reset_password_user = user_id
                        st.session_state.show_reset_password = True
                        st.rerun()
                    
                    if st.button("🗑️ Delete", key=f"delete_{user_id}", type="secondary", use_container_width=True):
                        st.session_state.delete_user_id = user_id
                        st.session_state.show_delete_confirm = True
                        st.rerun()
    else:
        st.info("No users found matching your criteria.")


def show_add_user_form():
    """Form to add new user"""
    st.subheader("➕ Add New User")
    
    storage = get_storage()
    auth_service = AuthService()
    
    with st.form("add_user_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input("Username*", placeholder="e.g., john_doe")
            full_name = st.text_input("Full Name*", placeholder="e.g., John Doe")
            email = st.text_input("Email*", placeholder="e.g., john@example.com")
            role = st.selectbox("Role*", ["student", "teacher", "admin"])
        
        with col2:
            password = st.text_input("Password*", type="password", placeholder="Min 6 characters")
            confirm_password = st.text_input("Confirm Password*", type="password")
            department = st.text_input("Department", placeholder="e.g., Computer Science")
            is_active = st.checkbox("Active Account", value=True)
        
        # Role-specific fields
        if role == "teacher":
            st.markdown("#### Teacher-Specific Information")
            col1, col2 = st.columns(2)
            with col1:
                qualification = st.text_input("Qualification", placeholder="e.g., Ph.D. in Computer Science")
            with col2:
                specialization = st.text_input("Specialization", placeholder="e.g., Machine Learning")
        
        elif role == "student":
            st.markdown("#### Student-Specific Information")
            col1, col2, col3 = st.columns(3)
            with col1:
                enrollment_number = st.text_input("Enrollment Number", placeholder="e.g., CS2024001")
            with col2:
                year = st.number_input("Year", min_value=1, max_value=5, value=1)
            with col3:
                semester = st.number_input("Semester", min_value=1, max_value=10, value=1)
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("✅ Create User", type="primary", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if cancel:
            st.session_state.show_add_user = False
            st.rerun()
        
        if submit:
            # Validation
            if not username or not full_name or not email or not password:
                st.error("❌ Please fill all required fields marked with *")
                return
            
            if password != confirm_password:
                st.error("❌ Passwords do not match")
                return
            
            if len(password) < 6:
                st.error("❌ Password must be at least 6 characters")
                return
            
            # Check if username exists
            existing_users = storage.get_all_users()
            if any(u.get('username') == username for u in existing_users.values()):
                st.error(f"❌ Username '{username}' already exists")
                return
            
            # Generate user ID
            user_id = f"{role[:3]}_{uuid.uuid4().hex[:8]}"
            
            # Hash password
            password_hash = auth_service.hash_password(password)
            
            # Prepare user data
            user_data = {
                'full_name': full_name,
                'department': department,
                'is_active': is_active
            }
            
            if role == "teacher":
                user_data.update({
                    'qualification': qualification if 'qualification' in locals() else None,
                    'specialization': specialization if 'specialization' in locals() else None
                })
            elif role == "student":
                user_data.update({
                    'enrollment_number': enrollment_number if 'enrollment_number' in locals() else None,
                    'year': year if 'year' in locals() else None,
                    'semester': semester if 'semester' in locals() else None
                })
            
            # Create user
            success = storage.create_user(
                user_id=user_id,
                username=username,
                password_hash=password_hash,
                role=role,
                email=email,
                **user_data
            )
            
            if success:
                st.success(f"✅ User '{username}' created successfully!")
                st.balloons()
                st.session_state.show_add_user = False
                st.rerun()
            else:
                st.error("❌ Failed to create user. User may already exist.")


def show_edit_user_form():
    """Form to edit existing user"""
    st.subheader("✏️ Edit User")
    
    storage = get_storage()
    user_id = st.session_state.edit_user_id
    user = storage.get_user(user_id)
    
    if not user:
        st.error("User not found")
        return
    
    with st.form("edit_user_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input("Username", value=user['username'], disabled=True)
            full_name = st.text_input("Full Name", value=user.get('full_name', ''))
            email = st.text_input("Email", value=user.get('email', ''))
        
        with col2:
            st.text_input("Role", value=user['role'].upper(), disabled=True)
            department = st.text_input("Department", value=user.get('department', ''))
            is_active = st.checkbox("Active Account", value=user.get('is_active', True))
        
        # Role-specific fields
        if user['role'] == "teacher":
            st.markdown("#### Teacher Information")
            col1, col2 = st.columns(2)
            with col1:
                qualification = st.text_input("Qualification", value=user.get('qualification', ''))
            with col2:
                specialization = st.text_input("Specialization", value=user.get('specialization', ''))
        
        elif user['role'] == "student":
            st.markdown("#### Student Information")
            col1, col2, col3 = st.columns(3)
            with col1:
                enrollment_number = st.text_input("Enrollment Number", value=user.get('enrollment_number', ''))
            with col2:
                year = st.number_input("Year", min_value=1, max_value=5, value=user.get('year', 1))
            with col3:
                semester = st.number_input("Semester", min_value=1, max_value=10, value=user.get('semester', 1))
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if cancel:
            st.session_state.show_edit_user = False
            st.rerun()
        
        if submit:
            # Prepare updates
            updates = {
                'full_name': full_name,
                'email': email,
                'department': department,
                'is_active': is_active
            }
            
            if user['role'] == "teacher":
                updates.update({
                    'qualification': qualification if 'qualification' in locals() else None,
                    'specialization': specialization if 'specialization' in locals() else None
                })
            elif user['role'] == "student":
                updates.update({
                    'enrollment_number': enrollment_number if 'enrollment_number' in locals() else None,
                    'year': year if 'year' in locals() else None,
                    'semester': semester if 'semester' in locals() else None
                })
            
            # Update user
            success = storage.update_user(user_id, updates)
            
            if success:
                st.success(f"✅ User '{user['username']}' updated successfully!")
                st.session_state.show_edit_user = False
                st.rerun()
            else:
                st.error("❌ Failed to update user")


def show_reset_password_form():
    """Form to reset user password"""
    user_id = st.session_state.reset_password_user
    storage = get_storage()
    auth_service = AuthService()
    user = storage.get_user(user_id)
    
    if not user:
        st.error("User not found")
        return
    
    st.subheader(f"🔄 Reset Password for {user['username']}")
    
    with st.form("reset_password_form"):
        new_password = st.text_input("New Password", type="password", placeholder="Min 6 characters")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("🔄 Reset Password", type="primary", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if cancel:
            st.session_state.show_reset_password = False
            st.rerun()
        
        if submit:
            if not new_password:
                st.error("❌ Please enter a new password")
                return
            
            if new_password != confirm_password:
                st.error("❌ Passwords do not match")
                return
            
            if len(new_password) < 6:
                st.error("❌ Password must be at least 6 characters")
                return
            
            # Hash new password
            password_hash = auth_service.hash_password(new_password)
            
            # Update user
            success = storage.update_user(user_id, {
                'password_hash': password_hash,
                'failed_login_attempts': 0
            })
            
            if success:
                st.success(f"✅ Password reset successfully for {user['username']}")
                st.session_state.show_reset_password = False
                st.rerun()
            else:
                st.error("❌ Failed to reset password")


def show_delete_confirmation():
    """Confirmation dialog for user deletion"""
    user_id = st.session_state.delete_user_id
    storage = get_storage()
    user = storage.get_user(user_id)
    
    if not user:
        st.error("User not found")
        return
    
    st.warning(f"⚠️ Are you sure you want to delete user **{user['username']}** ({user.get('full_name', 'N/A')})?")
    st.error("This action cannot be undone!")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🗑️ Yes, Delete", type="primary", use_container_width=True):
            success = storage.delete_user(user_id)
            if success:
                st.success(f"✅ User '{user['username']}' deleted successfully")
                st.session_state.show_delete_confirm = False
                st.rerun()
            else:
                st.error("❌ Failed to delete user")
    
    with col2:
        if st.button("❌ Cancel", use_container_width=True):
            st.session_state.show_delete_confirm = False
            st.rerun()


def main():
    """Main admin user management page"""
    st.title("👥 User Management")
    
    # Check if user is admin
    if 'user' not in st.session_state or st.session_state.user['role'] != 'admin':
        st.error("🚫 Access Denied. Admin privileges required.")
        return
    
    # Show statistics
    show_user_statistics()
    
    st.markdown("---")
    
    # Check for active forms
    if st.session_state.get('show_add_user', False):
        show_add_user_form()
    elif st.session_state.get('show_edit_user', False):
        show_edit_user_form()
    elif st.session_state.get('show_reset_password', False):
        show_reset_password_form()
    elif st.session_state.get('show_delete_confirm', False):
        show_delete_confirmation()
    else:
        show_user_list()


if __name__ == "__main__":
    main()
