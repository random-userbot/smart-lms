"""
Script to create initial users for Smart LMS
Creates Admin, Teacher, and Student accounts
"""

import sys
from pathlib import Path

# Add parent directory to path to import services
sys.path.insert(0, str(Path(__file__).parent))

from services.auth import AuthService
from services.storage import get_storage


def create_initial_users():
    """Create three initial users: admin, teacher, and student"""
    
    storage = get_storage()
    auth = AuthService()
    
    users_to_create = [
        {
            'user_id': 'admin_001',
            'username': 'admin',
            'password': 'admin123',
            'role': 'admin',
            'email': 'admin@smartlms.edu',
            'full_name': 'System Administrator',
            'department': 'IT Administration'
        },
        {
            'user_id': 'teacher_001',
            'username': 'dr_ramesh',
            'password': 'teacher123',
            'role': 'teacher',
            'email': 'ramesh@smartlms.edu',
            'full_name': 'Dr. Ramesh Kumar',
            'department': 'Computer Science',
            'qualification': 'Ph.D. in Computer Science',
            'specialization': 'Machine Learning & AI'
        },
        {
            'user_id': 'student_001',
            'username': 'demo_student',
            'password': 'student123',
            'role': 'student',
            'email': 'demo.student@smartlms.edu',
            'full_name': 'Demo Student',
            'department': 'Computer Science',
            'year': 3,
            'semester': 5,
            'enrollment_number': 'CS2022001'
        }
    ]
    
    print("=" * 60)
    print("Creating Initial Users for Smart LMS")
    print("=" * 60)
    print()
    
    for user_data in users_to_create:
        user_id = user_data.pop('user_id')
        username = user_data['username']
        password = user_data.pop('password')
        role = user_data['role']
        
        # Hash the password
        password_hash = auth.hash_password(password)
        
        # Create user
        success = storage.create_user(
            user_id=user_id,
            username=username,
            password_hash=password_hash,
            role=role,
            email=user_data.get('email'),
            full_name=user_data.get('full_name'),
            department=user_data.get('department'),
            qualification=user_data.get('qualification'),
            specialization=user_data.get('specialization'),
            year=user_data.get('year'),
            semester=user_data.get('semester'),
            enrollment_number=user_data.get('enrollment_number')
        )
        
        if success:
            print(f"✅ Created {role.upper()} account:")
            print(f"   Username: {username}")
            print(f"   User ID: {user_id}")
            print(f"   Email: {user_data.get('email', 'N/A')}")
            if role == 'teacher':
                print(f"   Qualification: {user_data.get('qualification', 'N/A')}")
            elif role == 'student':
                print(f"   Enrollment: {user_data.get('enrollment_number', 'N/A')}")
            print()
        else:
            print(f"❌ Failed to create {role} account: {username}")
            print(f"   (User may already exist)")
            print()
    
    print("=" * 60)
    print("User Creation Complete!")
    print("=" * 60)
    print()
    print("Login Credentials:")
    print("-" * 60)
    print("Admin Account:")
    print("  Username: admin")
    print("  Password: admin123")
    print()
    print("Teacher Account:")
    print("  Username: dr_ramesh")
    print("  Password: teacher123")
    print()
    print("Student Account:")
    print("  Username: demo_student")
    print("  Password: student123")
    print("-" * 60)
    print()


if __name__ == "__main__":
    try:
        create_initial_users()
        print("✨ All users created successfully!")
    except Exception as e:
        print(f"❌ Error creating users: {e}")
        import traceback
        traceback.print_exc()
