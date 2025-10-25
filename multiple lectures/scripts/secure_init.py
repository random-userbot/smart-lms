"""
Smart LMS - Secure Initial Setup Script
Creates admin user with strong password and initializes storage

Usage:
    python scripts/secure_init.py
    
IMPORTANT: 
- This script should be run ONCE during initial deployment
- You will be prompted to create a strong admin password
- Default demo credentials are DISABLED by default
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.auth import get_auth
from services.storage import get_storage
import getpass
import re


def validate_password_strength(password: str) -> tuple:
    """
    Validate password meets security requirements
    
    Returns:
        (is_valid: bool, message: str)
    """
    if len(password) < 12:
        return False, "Password must be at least 12 characters"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    # Check for common weak passwords
    weak_passwords = ['password', 'admin123', '12345678', 'qwerty', 'letmein']
    if password.lower() in weak_passwords:
        return False, "Password is too common. Choose a unique password."
    
    return True, "Password is strong"


def create_admin_user():
    """Create admin user with secure password"""
    auth = get_auth()
    storage = get_storage()
    
    print("\n" + "="*60)
    print("   SMART LMS - SECURE INITIALIZATION")
    print("="*60)
    print("\nThis script will create the initial admin user.")
    print("Please choose a STRONG password.\n")
    print("Password Requirements:")
    print("  • Minimum 12 characters")
    print("  • At least one uppercase letter")
    print("  • At least one lowercase letter")
    print("  • At least one number")
    print("  • At least one special character (!@#$%^&*...)")
    print("  • Not a common password\n")
    
    # Get admin username
    username = input("Admin Username [admin]: ").strip() or "admin"
    
    # Get admin email
    email = input("Admin Email [admin@example.com]: ").strip() or "admin@example.com"
    
    # Get strong password
    while True:
        password = getpass.getpass("Admin Password: ")
        password_confirm = getpass.getpass("Confirm Password: ")
        
        if password != password_confirm:
            print("❌ Passwords do not match. Try again.\n")
            continue
        
        is_valid, message = validate_password_strength(password)
        if not is_valid:
            print(f"❌ {message}\n")
            continue
        
        print(f"✅ {message}")
        break
    
    # Create admin user
    try:
        success = auth.register_user(
            username=username,
            password=password,
            role='admin',
            email=email,
            name='System Administrator'
        )
        
        if success:
            print(f"\n✅ Admin user '{username}' created successfully!")
            print(f"\n⚠️  IMPORTANT: Store these credentials securely!")
            print(f"   Username: {username}")
            print(f"   Email: {email}")
            print(f"\n⚠️  Change your password after first login if needed.")
        else:
            print("\n❌ Failed to create admin user. User may already exist.")
            return False
    except Exception as e:
        print(f"\n❌ Error creating admin user: {e}")
        return False
    
    return True


def create_demo_users():
    """Optionally create demo users for testing (NOT recommended for production)"""
    print("\n" + "="*60)
    print("   DEMO USERS (OPTIONAL)")
    print("="*60)
    print("\n⚠️  WARNING: Demo users have weak passwords and should ONLY be")
    print("   used for development/testing. NEVER enable in production!\n")
    
    create_demos = input("Create demo users? [y/N]: ").strip().lower()
    
    if create_demos != 'y':
        print("✅ Skipping demo users. Production-ready setup.")
        return True
    
    auth = get_auth()
    
    demo_users = [
        {
            'username': 'demo_teacher',
            'password': f'Teacher_{os.urandom(4).hex()}!',  # Random suffix
            'role': 'teacher',
            'email': 'teacher@demo.local',
            'name': 'Demo Teacher'
        },
        {
            'username': 'demo_student',
            'password': f'Student_{os.urandom(4).hex()}!',  # Random suffix
            'role': 'student',
            'email': 'student@demo.local',
            'name': 'Demo Student'
        }
    ]
    
    print("\n⚠️  Demo user credentials (save these):\n")
    
    for user_data in demo_users:
        try:
            success = auth.register_user(
                username=user_data['username'],
                password=user_data['password'],
                role=user_data['role'],
                email=user_data['email'],
                name=user_data['name']
            )
            
            if success:
                print(f"✅ {user_data['role'].title()}: {user_data['username']} / {user_data['password']}")
            else:
                print(f"⚠️  User {user_data['username']} may already exist")
        except Exception as e:
            print(f"❌ Error creating {user_data['username']}: {e}")
    
    print("\n⚠️  Remember to delete demo users before production deployment!")
    return True


def main():
    """Main setup routine"""
    print("\n🚀 Starting Smart LMS secure initialization...\n")
    
    # Initialize storage structure
    storage = get_storage()
    print("✅ Storage structure initialized")
    
    # Create admin user
    if not create_admin_user():
        print("\n❌ Setup failed. Please try again.")
        sys.exit(1)
    
    # Optionally create demo users
    create_demo_users()
    
    print("\n" + "="*60)
    print("   SETUP COMPLETE")
    print("="*60)
    print("\n✅ Smart LMS is ready to use!")
    print("\nNext steps:")
    print("  1. Review and customize config.yaml")
    print("  2. Set up environment variables (.env)")
    print("  3. Review SECURITY.md for deployment best practices")
    print("  4. Start the application: streamlit run app/streamlit_app.py")
    print("\n📖 Documentation: See README.md and SECURITY.md")
    print("="*60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)
