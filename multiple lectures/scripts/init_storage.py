"""
Initialize Smart LMS storage with sample data
Migrates existing CSV data to JSON format
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import csv
from services.storage import get_storage
from services.auth import AuthService
from datetime import datetime
import uuid


def migrate_users_from_csv():
    """Migrate users from student_login.csv to users.json"""
    print("📊 Migrating users from CSV...")
    
    storage = get_storage()
    auth = AuthService()
    
    csv_path = "student_login.csv"
    if not os.path.exists(csv_path):
        csv_path = "data_archive/student_login.csv"
    
    if not os.path.exists(csv_path):
        print("⚠️  student_login.csv not found, creating default users...")
        create_default_users()
        return
    
    migrated_count = 0
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            student_id = row.get('StudentID', '').strip()
            password = row.get('Password', '').strip()
            
            if not student_id or not password:
                continue
            
            # Hash password
            password_hash = auth.hash_password(password)
            
            # Create user
            user_id = f"student_{student_id}"
            success = storage.create_user(
                user_id=user_id,
                username=student_id,
                password_hash=password_hash,
                role='student',
                email=f"{student_id}@university.edu",
                full_name=f"Student {student_id}"
            )
            
            if success:
                migrated_count += 1
    
    print(f"✅ Migrated {migrated_count} students")
    
    # Add default admin and teacher accounts
    create_default_users()


def create_default_users():
    """Create default admin and teacher accounts"""
    print("👥 Creating default users...")
    
    storage = get_storage()
    auth = AuthService()
    
    default_users = [
        {
            'user_id': 'admin_1',
            'username': 'admin',
            'password': 'admin123',
            'role': 'admin',
            'email': 'admin@university.edu',
            'full_name': 'System Administrator'
        },
        {
            'user_id': 'teacher_1',
            'username': 'dr_ramesh',
            'password': 'teacher123',
            'role': 'teacher',
            'email': 'ramesh@university.edu',
            'full_name': 'Dr. Ramesh G'
        },
        {
            'user_id': 'teacher_2',
            'username': 'dr_priya',
            'password': 'teacher123',
            'role': 'teacher',
            'email': 'priya@university.edu',
            'full_name': 'Dr. Priya Kumar'
        },
        {
            'user_id': 'student_demo',
            'username': 'demo_student',
            'password': 'student123',
            'role': 'student',
            'email': 'demo@university.edu',
            'full_name': 'Demo Student'
        }
    ]
    
    for user_data in default_users:
        password = user_data.pop('password')
        password_hash = auth.hash_password(password)
        
        storage.create_user(
            password_hash=password_hash,
            **user_data
        )
    
    print("✅ Default users created:")
    print("   - Admin: admin / admin123")
    print("   - Teacher: dr_ramesh / teacher123")
    print("   - Teacher: dr_priya / teacher123")
    print("   - Student: demo_student / student123")


def create_sample_courses():
    """Create sample courses from existing video files"""
    print("📚 Creating sample courses...")
    
    storage = get_storage()
    
    courses = [
        {
            'course_id': 'cv_101',
            'name': 'Computer Vision',
            'teacher_id': 'teacher_1',
            'description': 'Introduction to Computer Vision and Image Processing',
            'enrolled_students': ['student_11', 'student_12', 'student_demo']
        },
        {
            'course_id': 'cns_101',
            'name': 'Cryptography and Network Security',
            'teacher_id': 'teacher_1',
            'description': 'Fundamentals of Cryptography and Network Security',
            'enrolled_students': ['student_11', 'student_13', 'student_demo']
        },
        {
            'course_id': 'ds_101',
            'name': 'Data Science',
            'teacher_id': 'teacher_2',
            'description': 'Introduction to Data Science and Machine Learning',
            'enrolled_students': ['student_12', 'student_13', 'student_demo']
        }
    ]
    
    for course in courses:
        storage.create_course(**course)
    
    print(f"✅ Created {len(courses)} courses")


def create_sample_lectures():
    """Create sample lectures from existing videos"""
    print("🎥 Creating sample lectures...")
    
    storage = get_storage()
    
    lectures = [
        # Computer Vision lectures
        {
            'lecture_id': 'cv_lec_1',
            'title': 'Introduction to Computer Vision',
            'course_id': 'cv_101',
            'video_path': './storage/courses/computer_vision/lectures/Lec_video.mp4',
            'duration': 3600,
            'description': 'Overview of computer vision fundamentals'
        },
        {
            'lecture_id': 'cv_lec_2',
            'title': 'Image Processing Techniques',
            'course_id': 'cv_101',
            'video_path': './storage/courses/computer_vision/lectures/CV_L2.mp4',
            'duration': 3600,
            'description': 'Advanced image processing methods'
        },
        # Cryptography lectures
        {
            'lecture_id': 'cns_lec_1',
            'title': 'Introduction to Cryptography',
            'course_id': 'cns_101',
            'video_path': './storage/courses/cryptography/lectures/CNS_Lec_1.mp4',
            'duration': 3000,
            'description': 'Basic cryptographic concepts'
        },
        {
            'lecture_id': 'cns_lec_2',
            'title': 'Network Security Protocols',
            'course_id': 'cns_101',
            'video_path': './storage/courses/cryptography/lectures/CNS_Lec_2.mp4',
            'duration': 3000,
            'description': 'Security protocols and implementations'
        },
        # Data Science lectures
        {
            'lecture_id': 'ds_lec_1',
            'title': 'Introduction to Data Science',
            'course_id': 'ds_101',
            'video_path': './storage/courses/data_science/lectures/Lec_1.mp4',
            'duration': 4000,
            'description': 'Data science fundamentals and tools'
        }
    ]
    
    for lecture in lectures:
        storage.create_lecture(**lecture)
    
    print(f"✅ Created {len(lectures)} lectures")


def create_sample_engagement_data():
    """Create sample engagement data from existing CSV"""
    print("📈 Creating sample engagement data...")
    
    storage = get_storage()
    
    # Create a few sample engagement logs
    sample_logs = [
        {
            'log_id': str(uuid.uuid4()),
            'student_id': 'student_demo',
            'lecture_id': 'cv_lec_1',
            'session_start': '2025-10-19T10:00:00Z',
            'events': [
                {'type': 'play', 'timestamp': '2025-10-19T10:00:00Z'},
                {'type': 'pause', 'timestamp': '2025-10-19T10:15:00Z'},
                {'type': 'play', 'timestamp': '2025-10-19T10:16:00Z'},
            ],
            'engagement_score': 85.5,
            'face_features': {
                'avg_gaze_score': 0.9,
                'avg_attention_score': 0.85,
                'avg_head_pose_stability': 0.88
            }
        }
    ]
    
    for log in sample_logs:
        storage.save_engagement_log(**log)
    
    print(f"✅ Created {len(sample_logs)} engagement logs")


def create_sample_grades():
    """Create sample quiz and assignment grades"""
    print("📝 Creating sample grades...")
    
    storage = get_storage()
    
    # Sample quiz grades
    storage.save_grade(
        student_id='student_demo',
        course_id='cv_101',
        assessment_type='quiz',
        assessment_id='cv_quiz_1',
        score=8,
        max_score=10,
        lecture_id='cv_lec_1'
    )
    
    # Sample assignment grades
    storage.save_grade(
        student_id='student_demo',
        course_id='cv_101',
        assessment_type='assignment',
        assessment_id='cv_assign_1',
        score=85,
        max_score=100,
        lecture_id='cv_lec_1'
    )
    
    print("✅ Created sample grades")


def main():
    """Main initialization function"""
    print("=" * 60)
    print("🚀 Smart LMS Storage Initialization")
    print("=" * 60)
    print()
    
    # Migrate users
    migrate_users_from_csv()
    print()
    
    # Create courses
    create_sample_courses()
    print()
    
    # Create lectures
    create_sample_lectures()
    print()
    
    # Create sample engagement data
    create_sample_engagement_data()
    print()
    
    # Create sample grades
    create_sample_grades()
    print()
    
    print("=" * 60)
    print("✅ Storage initialization complete!")
    print("=" * 60)
    print()
    print("📋 Next steps:")
    print("   1. Run: streamlit run app/streamlit_app.py")
    print("   2. Login with:")
    print("      - Admin: admin / admin123")
    print("      - Teacher: dr_ramesh / teacher123")
    print("      - Student: demo_student / student123")
    print()


if __name__ == "__main__":
    main()
