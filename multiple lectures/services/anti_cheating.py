"""
Smart LMS - Anti-Cheating Service
Detects integrity violations and displays warnings
Monitors: tab switches, excessive playback speed, focus losses
"""

import streamlit as st
from datetime import datetime
from typing import Dict, List, Optional
import csv
import os
import logging

from services.behavioral_logger import get_behavioral_logger

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AntiCheatingMonitor:
    """
    Monitors student behavior for potential integrity violations
    Displays warnings and records violations for teacher analytics
    """
    
    def __init__(self, student_id: str, lecture_id: str, course_id: str):
        """
        Initialize anti-cheating monitor
        
        Args:
            student_id: Student user ID
            lecture_id: Current lecture ID
            course_id: Current course ID
        """
        self.student_id = student_id
        self.lecture_id = lecture_id
        self.course_id = course_id
        
        # Get behavioral logger
        self.logger = get_behavioral_logger(student_id, lecture_id, course_id)
        
        # Violation thresholds
        self.thresholds = {
            'max_playback_speed': 1.25,  # Maximum allowed playback speed
            'max_tab_switches': 3,  # Warning after N tab switches
            'max_speed_changes': 5,  # Warning after N speed changes
            'min_engagement_score': 30,  # Alert if engagement drops below
            'max_consecutive_focus_losses': 2  # Alert after N consecutive focus losses
        }
        
        # Violation counts
        self.violations = {
            'tab_switches': 0,
            'excessive_speed': 0,
            'focus_losses': 0,
            'low_engagement': 0,
            'total': 0
        }
        
        # Violation log directory
        self.violations_dir = "ml_data/session_logs"
        os.makedirs(self.violations_dir, exist_ok=True)
        
        self.violations_file = os.path.join(
            self.violations_dir,
            f"violations_{student_id}_{datetime.utcnow().strftime('%Y%m')}.csv"
        )
        
        logger.info(f"AntiCheatingMonitor initialized for {student_id} on lecture {lecture_id}")
    
    def check_tab_switch(self, away: bool = True) -> bool:
        """
        Check for tab switch violation
        
        Args:
            away: True if switching away from app
        
        Returns:
            True if violation detected
        """
        if away:
            self.violations['tab_switches'] += 1
            
            # Log behavioral event
            self.logger.log_tab_switch(away=True)
            
            # Check threshold
            if self.violations['tab_switches'] >= self.thresholds['max_tab_switches']:
                self._record_violation(
                    violation_type='tab_switch',
                    severity='medium',
                    details={
                        'total_switches': self.violations['tab_switches'],
                        'threshold': self.thresholds['max_tab_switches']
                    }
                )
                return True
        else:
            # Returning to app
            self.logger.log_tab_switch(away=False)
        
        return False
    
    def check_playback_speed(self, new_speed: float, old_speed: float = 1.0) -> bool:
        """
        Check for excessive playback speed violation
        
        Args:
            new_speed: New playback speed
            old_speed: Previous playback speed
        
        Returns:
            True if violation detected
        """
        # Log speed change
        self.logger.log_playback_speed_change(old_speed, new_speed)
        
        # Check if speed exceeds threshold
        if new_speed > self.thresholds['max_playback_speed']:
            self.violations['excessive_speed'] += 1
            
            self._record_violation(
                violation_type='excessive_playback_speed',
                severity='high',
                details={
                    'speed': new_speed,
                    'threshold': self.thresholds['max_playback_speed'],
                    'old_speed': old_speed
                }
            )
            return True
        
        return False
    
    def check_focus_loss(self) -> bool:
        """
        Check for focus loss violation
        
        Returns:
            True if violation detected
        """
        self.violations['focus_losses'] += 1
        
        # Log behavioral event
        self.logger.log_focus_lost()
        
        # Check threshold
        if self.violations['focus_losses'] >= self.thresholds['max_consecutive_focus_losses']:
            self._record_violation(
                violation_type='focus_loss',
                severity='low',
                details={
                    'total_losses': self.violations['focus_losses']
                }
            )
            return True
        
        return False
    
    def check_engagement_score(self, engagement_score: float) -> bool:
        """
        Check for low engagement violation
        
        Args:
            engagement_score: Current engagement score (0-100)
        
        Returns:
            True if violation detected
        """
        if engagement_score < self.thresholds['min_engagement_score']:
            self.violations['low_engagement'] += 1
            
            self._record_violation(
                violation_type='low_engagement',
                severity='medium',
                details={
                    'engagement_score': engagement_score,
                    'threshold': self.thresholds['min_engagement_score']
                }
            )
            return True
        
        return False
    
    def _record_violation(self, violation_type: str, severity: str, details: Dict):
        """
        Record violation to behavioral logger and CSV
        
        Args:
            violation_type: Type of violation
            severity: 'low', 'medium', 'high'
            details: Additional violation details
        """
        self.violations['total'] += 1
        
        # Log to behavioral logger
        self.logger.log_violation(violation_type, severity, details)
        
        # Save to violations CSV
        violation_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'student_id': self.student_id,
            'lecture_id': self.lecture_id,
            'course_id': self.course_id,
            'violation_type': violation_type,
            'severity': severity,
            'details': str(details)
        }
        
        self._append_to_violations_csv(violation_entry)
        
        logger.warning(f"Violation recorded: {violation_type} ({severity}) | Student: {self.student_id}")
    
    def _append_to_violations_csv(self, violation: Dict):
        """Append violation to CSV file"""
        file_exists = os.path.exists(self.violations_file)
        
        with open(self.violations_file, 'a', newline='') as f:
            fieldnames = [
                'timestamp', 'student_id', 'lecture_id', 'course_id',
                'violation_type', 'severity', 'details'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(violation)
    
    def show_violation_warning(self, violation_type: str, message: str = None):
        """
        Display violation warning popup
        
        Args:
            violation_type: Type of violation
            message: Custom warning message
        """
        # Default messages
        messages = {
            'tab_switch': "⚠️ **Tab Switch Detected!** Please stay focused on the lecture.",
            'excessive_playback_speed': "🚫 **Playback Speed Too High!** Maximum allowed speed is 1.25x.",
            'focus_loss': "👀 **Focus Lost!** Please return your attention to the lecture.",
            'low_engagement': "😴 **Low Engagement Detected!** Try to stay attentive."
        }
        
        warning_msg = message or messages.get(violation_type, "⚠️ Integrity violation detected!")
        
        # Display warning
        st.warning(warning_msg)
        
        # Display violation count
        st.error(f"🔔 **Total Violations:** {self.violations['total']}")
        
        # Severity-based messaging
        if self.violations['total'] >= 5:
            st.error("⛔ **Multiple violations detected!** Your teacher will be notified.")
        elif self.violations['total'] >= 3:
            st.warning("⚠️ **Warning:** Continued violations may affect your integrity score.")
    
    def get_integrity_summary(self) -> Dict:
        """
        Get integrity summary for teacher analytics
        
        Returns:
            Dictionary with integrity metrics
        """
        # Get behavioral logger summary
        behavioral_summary = self.logger.get_session_summary()
        
        return {
            'student_id': self.student_id,
            'lecture_id': self.lecture_id,
            'course_id': self.course_id,
            'total_violations': self.violations['total'],
            'tab_switches': self.violations['tab_switches'],
            'excessive_speed_violations': self.violations['excessive_speed'],
            'focus_losses': self.violations['focus_losses'],
            'low_engagement_violations': self.violations['low_engagement'],
            'integrity_score': behavioral_summary['integrity_score'],
            'session_duration': behavioral_summary['total_duration']
        }
    
    def get_violations_by_type(self) -> Dict[str, int]:
        """Get violation counts by type"""
        return {
            'tab_switches': self.violations['tab_switches'],
            'excessive_speed': self.violations['excessive_speed'],
            'focus_losses': self.violations['focus_losses'],
            'low_engagement': self.violations['low_engagement']
        }


def render_integrity_widget(monitor: AntiCheatingMonitor):
    """
    Render integrity monitoring widget in sidebar
    
    Args:
        monitor: AntiCheatingMonitor instance
    """
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🛡️ Integrity Monitor")
    
    # Get integrity summary
    summary = monitor.get_integrity_summary()
    
    # Display integrity score
    integrity_score = summary['integrity_score']
    
    if integrity_score >= 90:
        color = "🟢"
        status = "Excellent"
    elif integrity_score >= 75:
        color = "🟡"
        status = "Good"
    elif integrity_score >= 60:
        color = "🟠"
        status = "Fair"
    else:
        color = "🔴"
        status = "Poor"
    
    st.sidebar.metric(
        label=f"{color} Integrity Score",
        value=f"{integrity_score:.0f}/100",
        delta=status
    )
    
    # Display violation counts
    if summary['total_violations'] > 0:
        st.sidebar.warning(f"⚠️ Violations: {summary['total_violations']}")
        
        # Breakdown
        violations = monitor.get_violations_by_type()
        for vtype, count in violations.items():
            if count > 0:
                st.sidebar.text(f"• {vtype.replace('_', ' ').title()}: {count}")
    else:
        st.sidebar.success("✅ No violations")
    
    # Progress bar
    st.sidebar.progress(integrity_score / 100)


def check_browser_visibility():
    """
    Add JavaScript to detect tab switches and focus changes
    Returns JavaScript code for injection
    """
    js_code = """
    <script>
    // Detect tab visibility changes
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            // Tab is hidden - log violation
            console.log('Tab switched away');
            
            // Send event to Streamlit (requires custom component)
            // For now, we'll use session state
            window.parent.postMessage({
                type: 'tab_switch',
                away: true
            }, '*');
        } else {
            // Tab is visible again
            console.log('Tab switched back');
            
            window.parent.postMessage({
                type: 'tab_switch',
                away: false
            }, '*');
        }
    });
    
    // Detect focus changes
    window.addEventListener('blur', function() {
        console.log('Window lost focus');
        window.parent.postMessage({
            type: 'focus_lost'
        }, '*');
    });
    
    window.addEventListener('focus', function() {
        console.log('Window gained focus');
        window.parent.postMessage({
            type: 'focus_gained'
        }, '*');
    });
    </script>
    """
    
    return js_code


# Singleton instances per lecture session
_anti_cheating_monitors = {}

def get_anti_cheating_monitor(student_id: str, lecture_id: str, 
                                course_id: str) -> AntiCheatingMonitor:
    """
    Get or create anti-cheating monitor
    
    Args:
        student_id: Student user ID
        lecture_id: Lecture ID
        course_id: Course ID
    
    Returns:
        AntiCheatingMonitor instance
    """
    key = f"{student_id}_{lecture_id}"
    
    if key not in _anti_cheating_monitors:
        _anti_cheating_monitors[key] = AntiCheatingMonitor(student_id, lecture_id, course_id)
    
    return _anti_cheating_monitors[key]


def cleanup_monitor(student_id: str, lecture_id: str):
    """Clean up monitor instance"""
    key = f"{student_id}_{lecture_id}"
    
    if key in _anti_cheating_monitors:
        del _anti_cheating_monitors[key]


# Export
__all__ = [
    'AntiCheatingMonitor', 
    'get_anti_cheating_monitor', 
    'cleanup_monitor',
    'render_integrity_widget',
    'check_browser_visibility'
]
