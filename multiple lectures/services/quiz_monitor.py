"""
Smart LMS - Quiz Monitoring System
Real-time webcam monitoring during quizzes with comprehensive cheating detection
"""

import streamlit as st
from datetime import datetime
import time
from typing import Dict, List, Optional
import os
import csv
import logging

from services.pip_webcam_live import render_pip_webcam
from services.anti_cheating import get_anti_cheating_monitor, render_integrity_widget
from services.session_tracker import get_global_session_tracker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QuizMonitor:
    """
    Comprehensive quiz monitoring with webcam tracking and violation detection
    """
    
    def __init__(self, quiz_id: str, lecture_id: str, student_id: str):
        """
        Initialize quiz monitor
        
        Args:
            quiz_id: Quiz identifier
            lecture_id: Associated lecture ID
            student_id: Student ID
        """
        self.quiz_id = quiz_id
        self.lecture_id = lecture_id
        self.student_id = student_id
        
        # Quiz session tracking
        self.start_time = datetime.utcnow()
        self.session_id = f"{student_id}_{quiz_id}_{self.start_time.strftime('%Y%m%d_%H%M%S')}"
        
        # Tracking data
        self.quiz_data = {
            'session_id': self.session_id,
            'quiz_id': quiz_id,
            'lecture_id': lecture_id,
            'student_id': student_id,
            'start_time': self.start_time.isoformat(),
            'end_time': None,
            'duration': 0,
            
            # Answers
            'answers': {},
            'question_times': {},  # Time spent per question
            
            # Violations
            'tab_switches': 0,
            'focus_losses': 0,
            'copy_paste_attempts': 0,
            'low_engagement_events': 0,
            'multiple_faces_detected': 0,
            'no_face_duration': 0,
            
            # Engagement
            'avg_engagement_score': 0,
            'engagement_samples': [],
            
            # Final metrics
            'score': None,
            'integrity_score': 100,
            'flagged_for_review': False
        }
        
        # Directories
        self.quiz_logs_dir = "ml_data/quiz_logs"
        os.makedirs(self.quiz_logs_dir, exist_ok=True)
        
        self.quiz_violations_file = os.path.join(
            self.quiz_logs_dir,
            f"quiz_violations_{student_id}_{datetime.utcnow().strftime('%Y%m')}.csv"
        )
        
        # Current question tracking
        self.current_question = None
        self.question_start_time = None
        
        logger.info(f"QuizMonitor initialized for quiz {quiz_id}")
    
    def start_question(self, question_id: str):
        """Start tracking a question"""
        # End previous question
        if self.current_question:
            self._end_current_question()
        
        self.current_question = question_id
        self.question_start_time = time.time()
    
    def _end_current_question(self):
        """End current question and record time"""
        if self.current_question and self.question_start_time:
            time_spent = time.time() - self.question_start_time
            self.quiz_data['question_times'][self.current_question] = time_spent
    
    def record_answer(self, question_id: str, answer: str):
        """Record student's answer"""
        self.quiz_data['answers'][question_id] = {
            'answer': answer,
            'timestamp': datetime.utcnow().isoformat(),
            'time_spent': self.quiz_data['question_times'].get(question_id, 0)
        }
    
    def log_violation(self, violation_type: str, details: str = None):
        """
        Log quiz violation
        
        Args:
            violation_type: Type of violation
            details: Additional details
        """
        # Increment violation counter
        if violation_type == 'tab_switch':
            self.quiz_data['tab_switches'] += 1
        elif violation_type == 'focus_loss':
            self.quiz_data['focus_losses'] += 1
        elif violation_type == 'copy_paste':
            self.quiz_data['copy_paste_attempts'] += 1
        elif violation_type == 'low_engagement':
            self.quiz_data['low_engagement_events'] += 1
        elif violation_type == 'multiple_faces':
            self.quiz_data['multiple_faces_detected'] += 1
        
        # Calculate integrity score
        total_violations = (
            self.quiz_data['tab_switches'] * 5 +
            self.quiz_data['focus_losses'] * 2 +
            self.quiz_data['copy_paste_attempts'] * 10 +
            self.quiz_data['low_engagement_events'] * 3 +
            self.quiz_data['multiple_faces_detected'] * 15
        )
        
        self.quiz_data['integrity_score'] = max(0, 100 - total_violations)
        
        # Flag for review if integrity drops below 50
        if self.quiz_data['integrity_score'] < 50:
            self.quiz_data['flagged_for_review'] = True
        
        # Save to violations CSV
        self._save_violation(violation_type, details)
    
    def _save_violation(self, violation_type: str, details: str):
        """Save violation to CSV"""
        file_exists = os.path.exists(self.quiz_violations_file)
        
        violation = {
            'timestamp': datetime.utcnow().isoformat(),
            'session_id': self.session_id,
            'student_id': self.student_id,
            'quiz_id': self.quiz_id,
            'violation_type': violation_type,
            'details': details or '',
            'integrity_score': self.quiz_data['integrity_score']
        }
        
        with open(self.quiz_violations_file, 'a', newline='') as f:
            fieldnames = ['timestamp', 'session_id', 'student_id', 'quiz_id', 
                          'violation_type', 'details', 'integrity_score']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(violation)
    
    def update_engagement(self, engagement_score: float):
        """Update engagement score"""
        self.quiz_data['engagement_samples'].append(engagement_score)
        
        # Calculate average
        if self.quiz_data['engagement_samples']:
            self.quiz_data['avg_engagement_score'] = sum(
                self.quiz_data['engagement_samples']
            ) / len(self.quiz_data['engagement_samples'])
        
        # Check for low engagement
        if engagement_score < 30:
            self.log_violation('low_engagement', f'Score: {engagement_score}')
    
    def end_quiz(self, final_score: float):
        """End quiz and save results"""
        # End current question
        if self.current_question:
            self._end_current_question()
        
        self.quiz_data['end_time'] = datetime.utcnow().isoformat()
        self.quiz_data['duration'] = (datetime.utcnow() - self.start_time).total_seconds()
        self.quiz_data['score'] = final_score
        
        # Save detailed quiz log
        import json
        quiz_log_file = os.path.join(
            self.quiz_logs_dir,
            f"quiz_session_{self.session_id}.json"
        )
        
        with open(quiz_log_file, 'w') as f:
            json.dump(self.quiz_data, f, indent=2)
        
        logger.info(f"Quiz {self.quiz_id} ended. Score: {final_score}, Integrity: {self.quiz_data['integrity_score']}")
    
    def get_summary(self) -> Dict:
        """Get quiz summary"""
        return {
            'session_id': self.session_id,
            'duration': self.quiz_data['duration'],
            'questions_answered': len(self.quiz_data['answers']),
            'avg_engagement': round(self.quiz_data['avg_engagement_score'], 2),
            'total_violations': (
                self.quiz_data['tab_switches'] +
                self.quiz_data['focus_losses'] +
                self.quiz_data['copy_paste_attempts'] +
                self.quiz_data['low_engagement_events'] +
                self.quiz_data['multiple_faces_detected']
            ),
            'integrity_score': self.quiz_data['integrity_score'],
            'flagged_for_review': self.quiz_data['flagged_for_review']
        }


def render_quiz_with_monitoring(quiz: Dict, lecture_id: str, student_id: str):
    """
    Render quiz with comprehensive monitoring
    
    Args:
        quiz: Quiz dictionary
        lecture_id: Associated lecture ID
        student_id: Student ID
    """
    quiz_id = quiz['quiz_id']
    
    # Initialize quiz monitor
    if 'quiz_monitor' not in st.session_state:
        st.session_state.quiz_monitor = QuizMonitor(quiz_id, lecture_id, student_id)
    
    quiz_monitor = st.session_state.quiz_monitor
    
    # Initialize anti-cheating
    anti_cheating = get_anti_cheating_monitor(student_id, f"quiz_{quiz_id}", lecture_id)
    
    # Title and instructions
    st.title(f"📝 {quiz['title']}")
    st.markdown("---")
    
    # Warning banner
    st.warning("""
    ⚠️ **Quiz Monitoring Active**
    - Your webcam is recording for integrity verification
    - Tab switches and focus changes are tracked
    - Copy-paste is monitored
    - Low engagement will be flagged
    
    **Please stay focused on the quiz!**
    """)
    
    st.markdown("---")
    
    # Layout: Quiz on left, monitoring on right
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### Questions")
        
        # Quiz questions
        if 'quiz_answers' not in st.session_state:
            st.session_state.quiz_answers = {}
        
        questions = quiz.get('questions', [])
        
        for idx, question in enumerate(questions, 1):
            question_id = question.get('question_id', f"q_{idx}")
            
            # Track question start
            quiz_monitor.start_question(question_id)
            
            with st.container():
                st.markdown(f"**Question {idx}:** {question['text']}")
                
                # Multiple choice
                if question['type'] == 'multiple_choice':
                    answer = st.radio(
                        "Select your answer:",
                        options=question['options'],
                        key=f"q_{question_id}",
                        label_visibility="collapsed"
                    )
                    
                    if answer:
                        st.session_state.quiz_answers[question_id] = answer
                        quiz_monitor.record_answer(question_id, answer)
                
                # Text answer
                elif question['type'] == 'text':
                    answer = st.text_area(
                        "Your answer:",
                        key=f"q_{question_id}",
                        label_visibility="collapsed"
                    )
                    
                    if answer:
                        st.session_state.quiz_answers[question_id] = answer
                        quiz_monitor.record_answer(question_id, answer)
                
                st.markdown("---")
        
        # Submit button
        if st.button("📤 Submit Quiz", type="primary", use_container_width=True):
            # Calculate score
            correct = 0
            total = len(questions)
            
            for question in questions:
                question_id = question.get('question_id', f"q_{idx}")
                student_answer = st.session_state.quiz_answers.get(question_id)
                correct_answer = question.get('correct_answer')
                
                if student_answer == correct_answer:
                    correct += 1
            
            score = (correct / total * 100) if total > 0 else 0
            
            # End quiz monitoring
            quiz_monitor.end_quiz(score)
            
            # Log to global session
            session_tracker = get_global_session_tracker(student_id)
            session_tracker.log_quiz_taken(
                quiz_id=quiz_id,
                lecture_id=lecture_id,
                score=score,
                duration=quiz_monitor.quiz_data['duration'],
                violations=sum([
                    quiz_monitor.quiz_data['tab_switches'],
                    quiz_monitor.quiz_data['focus_losses'],
                    quiz_monitor.quiz_data['copy_paste_attempts']
                ])
            )
            
            # Show results
            st.success(f"✅ Quiz submitted! Score: {score:.1f}/100")
            
            # Show integrity report
            summary = quiz_monitor.get_summary()
            
            st.markdown("### 🛡️ Integrity Report")
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("📊 Score", f"{score:.1f}/100")
            with col_b:
                st.metric("🛡️ Integrity", f"{summary['integrity_score']:.0f}/100")
            with col_c:
                st.metric("⚠️ Violations", summary['total_violations'])
            
            if summary['flagged_for_review']:
                st.error("🚨 **This quiz has been flagged for manual review due to integrity concerns.**")
            
            # Cleanup
            del st.session_state.quiz_monitor
            del st.session_state.quiz_answers
    
    with col2:
        st.markdown("### 🎥 Monitoring")
        
        # PiP webcam (smaller in sidebar)
        st.info("📹 Recording in progress...")
        
        try:
            # Render PiP webcam
            pip_webcam = render_pip_webcam(f"quiz_{quiz_id}", lecture_id, student_id)
            
            # Get engagement
            engagement = pip_webcam.get_current_engagement()
            quiz_monitor.update_engagement(engagement['score'])
            
            # Display engagement
            st.metric("📊 Engagement", f"{engagement['score']:.1f}/100")
            
            # Display status
            status = engagement['status']
            if status == 'highly_engaged':
                st.success("✅ Focused")
            elif status in ['engaged', 'partially_engaged']:
                st.info("👍 Good")
            else:
                st.warning("⚠️ Pay attention!")
        
        except Exception as e:
            st.error("❌ Webcam error")
            logger.error(f"Webcam error in quiz: {e}")
        
        # Integrity widget
        render_integrity_widget(anti_cheating)
        
        # Quiz progress
        st.markdown("---")
        st.markdown("### ⏱️ Progress")
        
        elapsed = (datetime.utcnow() - quiz_monitor.start_time).total_seconds()
        st.metric("Time Elapsed", f"{int(elapsed//60)}m {int(elapsed%60)}s")
        
        answered = len(st.session_state.quiz_answers)
        total_q = len(questions)
        st.progress(answered / total_q if total_q > 0 else 0)
        st.text(f"Answered: {answered}/{total_q}")


# Export
__all__ = ['QuizMonitor', 'render_quiz_with_monitoring']
