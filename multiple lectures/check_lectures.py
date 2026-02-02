from services.storage import get_storage

s = get_storage()
courses = s.get_all_courses()

print(f"Total courses: {len(courses)}")

for course_id, course in list(courses.items())[:1]:
    print(f"\nCourse: {course.get('title', 'No title')}")
    lectures = course.get('lectures', [])
    print(f"Lectures: {len(lectures)}")
    print(f"Lectures type: {type(lectures)}")
    
    if lectures:
        first_lec = lectures[0]
        print(f"First lecture type: {type(first_lec)}")
        print(f"First lecture sample: {str(first_lec)[:300]}")
        
        if isinstance(first_lec, dict):
            print(f"  - Has 'quiz' key: {'quiz' in first_lec}")
            print(f"  - Keys: {list(first_lec.keys())[:10]}")
