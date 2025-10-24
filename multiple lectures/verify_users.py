"""
Script to verify user login credentials
Tests that all three users can authenticate successfully
"""

import sys
from pathlib import Path

# Add parent directory to path to import services
sys.path.insert(0, str(Path(__file__).parent))

from services.auth import AuthService


def verify_user_login(username: str, password: str):
    """Verify a user can login with given credentials"""
    auth = AuthService()
    user = auth.login(username, password)
    
    if user:
        print(f"✅ {username} login SUCCESS")
        print(f"   Role: {user.get('role').upper()}")
        print(f"   Full Name: {user.get('full_name', 'N/A')}")
        print(f"   Email: {user.get('email', 'N/A')}")
        return True
    else:
        print(f"❌ {username} login FAILED")
        return False


def main():
    print("=" * 70)
    print("SMART LMS - User Login Verification")
    print("=" * 70)
    print()
    
    test_credentials = [
        ('admin', 'admin123'),
        ('dr_ramesh', 'teacher123'),
        ('demo_student', 'student123')
    ]
    
    success_count = 0
    
    for username, password in test_credentials:
        print(f"Testing {username}...")
        if verify_user_login(username, password):
            success_count += 1
        print()
    
    print("=" * 70)
    print(f"Verification Complete: {success_count}/{len(test_credentials)} users verified")
    print("=" * 70)
    print()
    
    if success_count == len(test_credentials):
        print("✨ All user accounts are ready to use!")
        print()
        print("Login Information:")
        print("-" * 70)
        print("Admin Account    → Username: admin          Password: admin123")
        print("Teacher Account  → Username: dr_ramesh      Password: teacher123")
        print("Student Account  → Username: demo_student   Password: student123")
        print("-" * 70)
    else:
        print("⚠️  Some accounts failed verification. Please check the credentials.")


if __name__ == "__main__":
    main()
