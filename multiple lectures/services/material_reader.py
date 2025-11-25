"""
Smart LMS - Material Reader Component
In-app reading with comprehensive time tracking and analytics
"""

import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import time
import os
from typing import Dict, Optional
import base64


class MaterialReader:
    """
    In-app material reader with time tracking and engagement monitoring
    Supports PDF, TXT, MD, HTML, and images
    """
    
    def __init__(self, material_id: str, lecture_id: str, student_id: str):
        """
        Initialize material reader
        
        Args:
            material_id: Material identifier
            lecture_id: Associated lecture ID
            student_id: Student ID
        """
        self.material_id = material_id
        self.lecture_id = lecture_id
        self.student_id = student_id
        
        # Tracking data
        self.start_time = datetime.utcnow()
        self.last_interaction = datetime.utcnow()
        self.total_time_spent = 0
        self.pages_viewed = []
        self.scroll_events = []
        self.current_page = 1
        
        # Session state keys
        self.reader_key = f"reader_{material_id}"
        
        # Initialize session state
        if self.reader_key not in st.session_state:
            st.session_state[self.reader_key] = {
                'start_time': self.start_time.isoformat(),
                'time_spent': 0,
                'pages_viewed': [],
                'interactions': 0,
                'scroll_depth': 0
            }
    
    def render_pdf(self, pdf_path: str, material_title: str):
        """
        Render PDF with time tracking
        
        Args:
            pdf_path: Path to PDF file
            material_title: Title of material
        """
        st.markdown(f"### 📄 {material_title}")
        st.markdown("---")
        
        # Read PDF file
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        
        # Convert to base64
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        # PDF viewer with tracking
        pdf_viewer_html = f"""
        <style>
            .pdf-container {{
                width: 100%;
                height: 800px;
                border: 2px solid #ddd;
                border-radius: 8px;
                overflow: hidden;
            }}
            .pdf-controls {{
                background: #f0f0f0;
                padding: 10px;
                border-bottom: 1px solid #ddd;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .pdf-stats {{
                font-size: 14px;
                color: #555;
            }}
        </style>
        
        <div class="pdf-container">
            <div class="pdf-controls">
                <div class="pdf-stats">
                    <span id="time-spent">⏱️ Time: 0:00</span>
                    <span style="margin-left: 20px;" id="page-info">📄 Page: 1</span>
                </div>
                <div>
                    <button onclick="updateInteraction()" style="padding: 5px 15px; cursor: pointer;">
                        📌 Mark as Read
                    </button>
                </div>
            </div>
            <iframe 
                src="data:application/pdf;base64,{pdf_base64}" 
                width="100%" 
                height="750px"
                id="pdf-frame"
                style="border: none;">
            </iframe>
        </div>
        
        <script>
        var startTime = new Date();
        var interactions = 0;
        
        // Update time spent every second
        setInterval(function() {{
            var elapsed = Math.floor((new Date() - startTime) / 1000);
            var minutes = Math.floor(elapsed / 60);
            var seconds = elapsed % 60;
            document.getElementById('time-spent').textContent = 
                '⏱️ Time: ' + minutes + ':' + (seconds < 10 ? '0' : '') + seconds;
            
            // Send to parent (Streamlit)
            window.parent.postMessage({{
                type: 'material_tracking',
                material_id: '{self.material_id}',
                time_spent: elapsed,
                interactions: interactions
            }}, '*');
        }}, 1000);
        
        // Track interactions
        function updateInteraction() {{
            interactions++;
            alert('✅ Progress saved!');
        }}
        
        // Track scroll/navigation
        document.getElementById('pdf-frame').addEventListener('load', function() {{
            interactions++;
        }});
        
        // Track page visibility
        document.addEventListener('visibilitychange', function() {{
            if (document.hidden) {{
                console.log('User switched away from material');
            }} else {{
                console.log('User returned to material');
                interactions++;
            }}
        }});
        </script>
        """
        
        components.html(pdf_viewer_html, height=850)
    
    def render_text(self, text_content: str, material_title: str, file_type: str = 'txt'):
        """
        Render text/markdown with time tracking
        
        Args:
            text_content: Text content to display
            material_title: Title of material
            file_type: 'txt', 'md', 'html'
        """
        st.markdown(f"### 📝 {material_title}")
        st.markdown("---")
        
        # Start time tracking
        start_time = time.time()
        
        # Display content in scrollable container
        content_html = f"""
        <style>
            .text-container {{
                width: 100%;
                max-height: 700px;
                overflow-y: auto;
                border: 2px solid #ddd;
                border-radius: 8px;
                padding: 30px;
                background: white;
                font-size: 16px;
                line-height: 1.8;
            }}
            .text-header {{
                background: #f0f0f0;
                padding: 15px;
                border-bottom: 1px solid #ddd;
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-radius: 8px 8px 0 0;
            }}
            .text-stats {{
                font-size: 14px;
                color: #555;
            }}
        </style>
        
        <div style="border: 2px solid #ddd; border-radius: 8px; overflow: hidden;">
            <div class="text-header">
                <div class="text-stats">
                    <span id="read-time">⏱️ Reading Time: 0:00</span>
                    <span style="margin-left: 20px;" id="scroll-pct">📊 Progress: 0%</span>
                </div>
                <button onclick="markComplete()" style="padding: 8px 20px; cursor: pointer; background: #4CAF50; color: white; border: none; border-radius: 4px;">
                    ✅ Mark Complete
                </button>
            </div>
            <div class="text-container" id="text-content" onscroll="trackScroll()">
                {text_content if file_type == 'html' else f'<pre style="white-space: pre-wrap; font-family: inherit;">{text_content}</pre>'}
            </div>
        </div>
        
        <script>
        var readStartTime = new Date();
        var scrollDepth = 0;
        var completed = false;
        
        // Update reading time
        setInterval(function() {{
            var elapsed = Math.floor((new Date() - readStartTime) / 1000);
            var minutes = Math.floor(elapsed / 60);
            var seconds = elapsed % 60;
            document.getElementById('read-time').textContent = 
                '⏱️ Reading Time: ' + minutes + ':' + (seconds < 10 ? '0' : '') + seconds;
            
            // Send to parent
            window.parent.postMessage({{
                type: 'material_reading',
                material_id: '{self.material_id}',
                time_spent: elapsed,
                scroll_depth: scrollDepth,
                completed: completed
            }}, '*');
        }}, 1000);
        
        // Track scroll depth
        function trackScroll() {{
            var container = document.getElementById('text-content');
            var scrollPct = Math.round(
                (container.scrollTop / (container.scrollHeight - container.clientHeight)) * 100
            );
            scrollDepth = Math.max(scrollDepth, scrollPct || 0);
            document.getElementById('scroll-pct').textContent = '📊 Progress: ' + scrollDepth + '%';
            
            // Auto-complete if scrolled to bottom
            if (scrollDepth >= 95 && !completed) {{
                completed = true;
                setTimeout(function() {{
                    alert('🎉 Material completed! Well done!');
                }}, 500);
            }}
        }}
        
        function markComplete() {{
            completed = true;
            alert('✅ Material marked as complete!');
        }}
        </script>
        """
        
        components.html(content_html, height=800)
    
    def render_image(self, image_path: str, material_title: str):
        """
        Render image with time tracking
        
        Args:
            image_path: Path to image file
            material_title: Title of material
        """
        st.markdown(f"### 🖼️ {material_title}")
        st.markdown("---")
        
        # Display image
        st.image(image_path, use_column_width=True)
        
        # Time tracking
        if 'image_view_start' not in st.session_state:
            st.session_state.image_view_start = time.time()
        
        elapsed = time.time() - st.session_state.image_view_start
        st.info(f"⏱️ Viewing time: {int(elapsed)} seconds")
    
    def get_reading_stats(self) -> Dict:
        """Get reading statistics"""
        reader_data = st.session_state.get(self.reader_key, {})
        
        return {
            'material_id': self.material_id,
            'lecture_id': self.lecture_id,
            'student_id': self.student_id,
            'time_spent': reader_data.get('time_spent', 0),
            'pages_viewed': len(reader_data.get('pages_viewed', [])),
            'interactions': reader_data.get('interactions', 0),
            'scroll_depth': reader_data.get('scroll_depth', 0),
            'completed': reader_data.get('scroll_depth', 0) >= 95
        }


def render_material_viewer(material: Dict, lecture_id: str, student_id: str):
    """
    Render material viewer with automatic time tracking
    
    Args:
        material: Material dictionary with path, title, type
        lecture_id: Associated lecture ID
        student_id: Student ID
    """
    from services.session_tracker import get_global_session_tracker
    
    material_id = material.get('material_id')
    material_path = material.get('path')
    material_title = material.get('title', 'Untitled Material')
    material_type = material.get('type', '').lower()
    
    # Initialize reader
    reader = MaterialReader(material_id, lecture_id, student_id)
    
    # Track activity start
    session_tracker = get_global_session_tracker(student_id)
    session_tracker.start_activity('material', material_id, {
        'lecture_id': lecture_id,
        'title': material_title,
        'type': material_type
    })
    
    # Render based on type
    if not os.path.exists(material_path):
        st.error(f"❌ Material file not found: {material_path}")
        return
    
    if material_type == 'pdf':
        reader.render_pdf(material_path, material_title)
    
    elif material_type in ['txt', 'md', 'markdown']:
        with open(material_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if material_type in ['md', 'markdown']:
            # Convert markdown to HTML
            try:
                import markdown
                content_html = markdown.markdown(content)
                reader.render_text(content_html, material_title, 'html')
            except ImportError:
                st.markdown(content)
        else:
            reader.render_text(content, material_title, 'txt')
    
    elif material_type in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
        reader.render_image(material_path, material_title)
    
    else:
        st.warning(f"⚠️ Unsupported material type: {material_type}")
        st.info("💡 Download the file to view it externally.")
    
    # Display reading stats
    with st.expander("📊 Your Reading Progress"):
        stats = reader.get_reading_stats()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("⏱️ Time Spent", f"{stats['time_spent']//60}m {stats['time_spent']%60}s")
        with col2:
            st.metric("👆 Interactions", stats['interactions'])
        with col3:
            st.metric("📊 Progress", f"{stats['scroll_depth']}%")
        
        if stats['completed']:
            st.success("✅ Material completed!")
        
        # Save button
        if st.button("💾 Save Progress"):
            # Log to global session tracker
            session_tracker.log_material_read(
                material_id=material_id,
                lecture_id=lecture_id,
                title=material_title,
                time_spent=stats['time_spent'],
                pages_viewed=stats['pages_viewed']
            )
            st.success("✅ Progress saved!")


# Export
__all__ = ['MaterialReader', 'render_material_viewer']
