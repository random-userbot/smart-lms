"""
PDF Reader Service with Reading Time Tracking
Allows students to read PDFs in-browser with automatic time tracking
"""

import streamlit as st
import os
from datetime import datetime, timedelta
from pathlib import Path
import base64
from typing import Dict, Optional
import csv
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.universal_logger import log_pdf_action, log_download


class PDFReaderService:
    """Service for reading PDFs with time tracking"""
    
    def __init__(self, storage_dir: str = "./ml_data/reading_logs"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
    
    def get_pdf_reading_log_file(self, student_id: str) -> str:
        """Get the CSV file path for student's PDF reading logs"""
        year_month = datetime.now().strftime("%Y%m")
        return os.path.join(self.storage_dir, f"pdf_reading_log_{student_id}_{year_month}.csv")
    
    def log_reading_session(self, student_id: str, material_id: str, course_id: str, 
                           lecture_id: str, material_title: str, reading_duration: int):
        """
        Log a PDF reading session to CSV
        
        Args:
            student_id: Student's user ID
            material_id: Unique material identifier
            course_id: Course identifier
            lecture_id: Lecture identifier
            material_title: Title of the material
            reading_duration: Time spent reading in seconds
        """
        log_file = self.get_pdf_reading_log_file(student_id)
        file_exists = os.path.exists(log_file)
        
        with open(log_file, 'a', newline='', encoding='utf-8') as f:
            fieldnames = [
                'timestamp', 'student_id', 'material_id', 'course_id', 
                'lecture_id', 'material_title', 'reading_duration_seconds',
                'reading_duration_minutes', 'session_date'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow({
                'timestamp': datetime.now().isoformat(),
                'student_id': student_id,
                'material_id': material_id,
                'course_id': course_id,
                'lecture_id': lecture_id,
                'material_title': material_title,
                'reading_duration_seconds': reading_duration,
                'reading_duration_minutes': round(reading_duration / 60, 2),
                'session_date': datetime.now().strftime("%Y-%m-%d")
            })
    
    def get_total_reading_time(self, student_id: str, material_id: str) -> int:
        """Get total reading time for a specific material in seconds"""
        log_file = self.get_pdf_reading_log_file(student_id)
        
        if not os.path.exists(log_file):
            return 0
        
        total_seconds = 0
        with open(log_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['material_id'] == material_id:
                    total_seconds += int(row.get('reading_duration_seconds', 0))
        
        return total_seconds
    
    def display_pdf(self, pdf_path: str, material_id: str, material_title: str, 
                    course_id: str, lecture_id: str, student_id: str):
        """
        Display PDF in browser with time tracking
        
        Args:
            pdf_path: Path to the PDF file
            material_id: Unique material identifier
            material_title: Title of the material
            course_id: Course identifier
            lecture_id: Lecture identifier
            student_id: Student's user ID
        """
        if not os.path.exists(pdf_path):
            st.error(f"❌ PDF file not found: {pdf_path}")
            return
        
        # Initialize session state for time tracking
        session_key = f"pdf_reading_{material_id}"
        if session_key not in st.session_state:
            st.session_state[session_key] = {
                'start_time': datetime.now(),
                'last_update': datetime.now(),
                'total_seconds': 0
            }
            # Log PDF open on first view
            log_pdf_action(student_id, 'pdf_open', course_id, lecture_id, material_id)
        
        # Calculate reading time
        reading_session = st.session_state[session_key]
        current_time = datetime.now()
        session_duration = (current_time - reading_session['start_time']).total_seconds()
        
        # Display PDF info header with real-time timer
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"### 📄 {material_title}")
        
        with col2:
            # Placeholder for real-time reading time
            reading_time_placeholder = st.empty()
        
        with col3:
            # Show total reading time across all sessions
            total_time = self.get_total_reading_time(student_id, material_id)
            total_minutes = int(total_time // 60)
            total_time_placeholder = st.empty()
            total_time_placeholder.metric("📊 Total Time", f"{total_minutes} min")
        
        # JavaScript for real-time timer update
        start_timestamp = int(reading_session['start_time'].timestamp() * 1000)
        
        timer_html = f"""
        <script>
            let startTime = {start_timestamp};
            let timerElement = window.parent.document.querySelector('[data-testid="stMetricValue"]');
            
            function updateTimer() {{
                let now = Date.now();
                let elapsed = Math.floor((now - startTime) / 1000);
                let minutes = Math.floor(elapsed / 60);
                let seconds = elapsed % 60;
                
                // Update the reading time display
                let readingTimeElements = window.parent.document.querySelectorAll('[data-testid="stMetric"]');
                if (readingTimeElements.length > 1) {{
                    let readingTimeMetric = readingTimeElements[1];
                    let valueElement = readingTimeMetric.querySelector('[data-testid="stMetricValue"]');
                    if (valueElement) {{
                        valueElement.textContent = minutes + 'm ' + seconds + 's';
                    }}
                }}
                
                // Store time in session storage for tracking
                sessionStorage.setItem('pdf_reading_time_{material_id}', elapsed);
            }}
            
            // Update every second
            setInterval(updateTimer, 1000);
            updateTimer();
            
            // Track page visibility for accurate time tracking
            let isVisible = true;
            let pausedTime = 0;
            
            document.addEventListener('visibilitychange', function() {{
                if (document.hidden) {{
                    isVisible = false;
                    pausedTime = Date.now();
                }} else {{
                    isVisible = true;
                    if (pausedTime > 0) {{
                        // Adjust start time to exclude time when page was hidden
                        startTime += (Date.now() - pausedTime);
                        pausedTime = 0;
                    }}
                }}
            }});
        </script>
        """
        
        st.components.v1.html(timer_html, height=0)
        
        # Update the reading time display
        minutes = int(session_duration // 60)
        seconds = int(session_duration % 60)
        reading_time_placeholder.metric("⏱️ Reading Time", f"{minutes}m {seconds}s")
        
        st.markdown("---")
        
        # Read PDF and encode to base64
        try:
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
            
            base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
            
            # Embedded PDF viewer with full height
            pdf_display = f'''
                <iframe
                    src="data:application/pdf;base64,{base64_pdf}"
                    width="100%"
                    height="800"
                    type="application/pdf"
                    style="border: 2px solid #ddd; border-radius: 8px;">
                    <p>Your browser does not support PDFs. 
                    <a href="data:application/pdf;base64,{base64_pdf}" download="{material_title}.pdf">
                    Download the PDF</a> instead.</p>
                </iframe>
            '''
            
            st.markdown(pdf_display, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Action buttons
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                # Download button
                if st.download_button(
                    label="📥 Download PDF",
                    data=pdf_bytes,
                    file_name=f"{material_title}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                ):
                    # Log download action
                    log_download(student_id, 'pdf', course_id, lecture_id, material_id, 
                               file_size=len(pdf_bytes))
            
            with col2:
                # Mark as read button
                if st.button("✅ Mark as Read", use_container_width=True):
                    # Log the reading session
                    self.log_reading_session(
                        student_id=student_id,
                        material_id=material_id,
                        course_id=course_id,
                        lecture_id=lecture_id,
                        material_title=material_title,
                        reading_duration=int(session_duration)
                    )
                    # Log reading completion for intelligent engagement
                    log_pdf_action(student_id, 'pdf_complete', course_id, lecture_id, 
                                 material_id, duration=int(session_duration))
                    st.success(f"✅ Logged {minutes}m {seconds}s of reading time!")
                    st.balloons()
            
            with col3:
                # Close button
                if st.button("← Back", use_container_width=True, type="secondary"):
                    # Log final reading time
                    self.log_reading_session(
                        student_id=student_id,
                        material_id=material_id,
                        course_id=course_id,
                        lecture_id=lecture_id,
                        material_title=material_title,
                        reading_duration=int(session_duration)
                    )
                    
                    # Clear session state
                    if session_key in st.session_state:
                        del st.session_state[session_key]
                    
                    # Return to previous page
                    if 'previous_page' in st.session_state:
                        st.session_state.current_page = st.session_state.previous_page
                    else:
                        st.session_state.current_page = 'lectures'
                    st.rerun()
            
            # Auto-save reading progress every 30 seconds
            time_since_update = (current_time - reading_session['last_update']).total_seconds()
            if time_since_update >= 30:
                self.log_reading_session(
                    student_id=student_id,
                    material_id=material_id,
                    course_id=course_id,
                    lecture_id=lecture_id,
                    material_title=material_title,
                    reading_duration=int(session_duration)
                )
                reading_session['last_update'] = current_time
                reading_session['total_seconds'] = int(session_duration)
        
        except Exception as e:
            st.error(f"❌ Error loading PDF: {str(e)}")
            st.info("💡 Try downloading the PDF instead.")


# Global instance
_pdf_reader = None

def get_pdf_reader() -> PDFReaderService:
    """Get global PDF reader service instance"""
    global _pdf_reader
    if _pdf_reader is None:
        _pdf_reader = PDFReaderService()
    return _pdf_reader
