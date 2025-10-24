"""
Smart LMS - Enrollment Requests Management (Teacher)
Teachers can approve or reject student enrollment requests
"""

import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.storage import get_storage
from services.auth import get_auth
from datetime import datetime


def main():
    """Main enrollment requests page"""
    
    # Check authentication
    auth = get_auth()
    if not auth.is_authenticated():
        st.warning("⚠️ Please login to manage enrollment requests")
        st.stop()
    
    user = st.session_state.user
    
    if user['role'] not in ['teacher', 'admin']:
        st.error("❌ This page is only for teachers and admins")
        st.stop()
    
    st.title("📝 Enrollment Requests")
    
    storage = get_storage()
    
    # Get teacher's courses
    if user['role'] == 'admin':
        courses = storage.get_all_courses()
    else:
        courses = storage.get_all_courses(teacher_id=user['user_id'])
    
    if not courses:
        st.info("You don't have any courses yet.")
        st.stop()
    
    # Tabs for pending and processed requests
    tab1, tab2 = st.tabs(["⏳ Pending Requests", "✅ Processed Requests"])
    
    with tab1:
        st.subheader("Pending Enrollment Requests")
        
        # Get pending requests for teacher's courses
        all_pending = storage.get_enrollment_requests(status='pending')
        
        # Filter by teacher's courses
        course_ids = list(courses.keys())
        pending_requests = {
            rid: r for rid, r in all_pending.items() 
            if r.get('course_id') in course_ids
        }
        
        if pending_requests:
            st.markdown(f"**{len(pending_requests)} pending requests**")
            
            for request_id, request in pending_requests.items():
                course_id = request.get('course_id')
                student_id = request.get('student_id')
                course = courses.get(course_id, {})
                student = storage.get_user(student_id)
                
                # Request card
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                    
                    with col1:
                        st.markdown(f"""
                        **Student:** {request.get('student_name', 'Unknown')}  
                        **Email:** {student.get('email', 'N/A') if student else 'N/A'}  
                        **Enrollment:** {student.get('enrollment_number', 'N/A') if student else 'N/A'}
                        """)
                    
                    with col2:
                        st.markdown(f"""
                        **Course:** {course.get('name', 'Unknown')}  
                        **Code:** {course.get('code', 'N/A')}  
                        **Requested:** {request.get('requested_at', '')[:10]}
                        """)
                    
                    with col3:
                        if st.button("✅ Approve", key=f"approve_{request_id}", 
                                   type="primary", use_container_width=True):
                            success = storage.update_enrollment_request(
                                request_id, 
                                'approved', 
                                user['user_id']
                            )
                            if success:
                                st.success(f"✅ Approved {request.get('student_name')}")
                                st.rerun()
                            else:
                                st.error("Failed to approve request")
                    
                    with col4:
                        if st.button("❌ Reject", key=f"reject_{request_id}", 
                                   use_container_width=True):
                            success = storage.update_enrollment_request(
                                request_id, 
                                'rejected', 
                                user['user_id']
                            )
                            if success:
                                st.warning(f"❌ Rejected {request.get('student_name')}")
                                st.rerun()
                            else:
                                st.error("Failed to reject request")
                    
                    st.divider()
        else:
            st.info("No pending enrollment requests.")
    
    with tab2:
        st.subheader("Processed Requests")
        
        # Get processed requests
        approved_requests = storage.get_enrollment_requests(status='approved')
        rejected_requests = storage.get_enrollment_requests(status='rejected')
        
        # Filter by teacher's courses
        course_ids = list(courses.keys())
        approved = {
            rid: r for rid, r in approved_requests.items() 
            if r.get('course_id') in course_ids
        }
        rejected = {
            rid: r for rid, r in rejected_requests.items() 
            if r.get('course_id') in course_ids
        }
        
        # Display approved
        if approved:
            st.markdown(f"### ✅ Approved ({len(approved)})")
            for request_id, request in list(approved.items())[:10]:  # Show last 10
                course = courses.get(request.get('course_id'), {})
                st.markdown(f"""
                - **{request.get('student_name')}** → **{course.get('name')}**  
                  Approved on {request.get('processed_at', '')[:10]}
                """)
        
        # Display rejected
        if rejected:
            st.markdown(f"### ❌ Rejected ({len(rejected)})")
            for request_id, request in list(rejected.items())[:10]:  # Show last 10
                course = courses.get(request.get('course_id'), {})
                st.markdown(f"""
                - **{request.get('student_name')}** → **{course.get('name')}**  
                  Rejected on {request.get('processed_at', '')[:10]}
                """)
        
        if not approved and not rejected:
            st.info("No processed requests yet.")
    
    # Summary statistics
    st.sidebar.markdown("### 📊 Request Statistics")
    
    all_pending = storage.get_enrollment_requests(status='pending')
    pending_count = len([r for r in all_pending.values() if r.get('course_id') in course_ids])
    
    all_approved = storage.get_enrollment_requests(status='approved')
    approved_count = len([r for r in all_approved.values() if r.get('course_id') in course_ids])
    
    all_rejected = storage.get_enrollment_requests(status='rejected')
    rejected_count = len([r for r in all_rejected.values() if r.get('course_id') in course_ids])
    
    st.sidebar.metric("⏳ Pending", pending_count)
    st.sidebar.metric("✅ Approved", approved_count)
    st.sidebar.metric("❌ Rejected", rejected_count)


if __name__ == "__main__":
    main()
