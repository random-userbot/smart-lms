"""
Smart LMS - Authentication Service
Secure password hashing and role-based access control
"""

import bcrypt
import streamlit as st
from typing import Optional, Dict
from datetime import datetime
from services.storage import get_storage


class AuthService:
    """Authentication and authorization service"""
    
    def __init__(self):
        self.storage = get_storage()
        self.max_login_attempts = 5
        self.lockout_duration = 900  # 15 minutes in seconds
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception:
            return False
    
    def login(self, username: str, password: str) -> Optional[Dict]:
        """
        Authenticate user and return user data if successful
        Returns None if authentication fails
        """
        # Get all users and find by username
        all_users = self.storage.get_all_users()
        user = None
        user_id = None
        
        for uid, u in all_users.items():
            if u.get('username') == username:
                user = u
                user_id = uid
                break
        
        if not user:
            return None
        
        # Check if account is locked
        if not user.get('is_active', True):
            return None
        
        # Verify password
        if not self.verify_password(password, user['password_hash']):
            # Increment failed login attempts
            failed_attempts = user.get('failed_login_attempts', 0) + 1
            self.storage.update_user(user_id, {
                'failed_login_attempts': failed_attempts,
                'last_failed_login': datetime.utcnow().isoformat()
            })
            
            # Lock account if too many attempts
            if failed_attempts >= self.max_login_attempts:
                self.storage.update_user(user_id, {'is_active': False})
            
            return None
        
        # Successful login - update user record
        self.storage.update_user(user_id, {
            'last_login': datetime.utcnow().isoformat(),
            'failed_login_attempts': 0
        })
        
        return {
            'user_id': user_id,
            'username': user['username'],
            'role': user['role'],
            'email': user.get('email'),
            'full_name': user.get('full_name', username)
        }
    
    def register(self, username: str, password: str, role: str,
                email: Optional[str] = None, full_name: Optional[str] = None) -> bool:
        """
        Register new user
        Returns True if successful, False if username exists
        """
        # Check if username already exists
        all_users = self.storage.get_all_users()
        for user in all_users.values():
            if user.get('username') == username:
                return False
        
        # Generate user ID
        user_id = f"{role}_{len(all_users) + 1}"
        
        # Hash password
        password_hash = self.hash_password(password)
        
        # Create user
        return self.storage.create_user(
            user_id=user_id,
            username=username,
            password_hash=password_hash,
            role=role,
            email=email,
            full_name=full_name or username
        )
    
    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """Change user password"""
        user = self.storage.get_user(user_id)
        if not user:
            return False
        
        # Verify old password
        if not self.verify_password(old_password, user['password_hash']):
            return False
        
        # Hash and update new password
        new_hash = self.hash_password(new_password)
        return self.storage.update_user(user_id, {'password_hash': new_hash})
    
    def reset_password(self, username: str, new_password: str) -> bool:
        """Reset password (admin function)"""
        all_users = self.storage.get_all_users()
        
        for user_id, user in all_users.items():
            if user.get('username') == username:
                new_hash = self.hash_password(new_password)
                return self.storage.update_user(user_id, {
                    'password_hash': new_hash,
                    'is_active': True,
                    'failed_login_attempts': 0
                })
        
        return False
    
    @staticmethod
    def check_role(required_role: str) -> bool:
        """
        Check if current user has required role
        Use in Streamlit pages to restrict access
        """
        if 'user' not in st.session_state:
            return False
        
        user_role = st.session_state.user.get('role')
        
        # Admin has access to everything
        if user_role == 'admin':
            return True
        
        # Check specific role
        if user_role == required_role:
            return True
        
        return False
    
    @staticmethod
    def require_auth(redirect_to_login: bool = True):
        """
        Decorator/function to require authentication
        Use at the top of Streamlit pages
        """
        if 'user' not in st.session_state:
            if redirect_to_login:
                st.warning("⚠️ Please log in to access this page")
                st.stop()
            return False
        return True
    
    @staticmethod
    def require_role(role: str):
        """
        Require specific role to access page
        Use at the top of Streamlit pages
        """
        if 'user' not in st.session_state:
            st.warning("⚠️ Please log in to access this page")
            st.stop()
        
        user_role = st.session_state.user.get('role')
        
        # Admin has access to everything
        if user_role == 'admin':
            return True
        
        if user_role != role:
            st.error(f"🚫 Access denied. This page requires {role} role.")
            st.stop()
        
        return True
    
    @staticmethod
    def logout():
        """Clear session and logout user"""
        if 'user' in st.session_state:
            del st.session_state.user
        if 'consent_given' in st.session_state:
            del st.session_state.consent_given
        st.session_state.clear()
    
    @staticmethod
    def get_current_user() -> Optional[Dict]:
        """Get currently logged in user"""
        return st.session_state.get('user')
    
    @staticmethod
    def is_authenticated() -> bool:
        """Check if user is authenticated"""
        return 'user' in st.session_state


# Singleton instance
_auth_instance = None

def get_auth() -> AuthService:
    """Get auth service singleton"""
    global _auth_instance
    if _auth_instance is None:
        _auth_instance = AuthService()
    return _auth_instance
