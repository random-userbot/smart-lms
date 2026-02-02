"""
Automated Quiz Generator Service
Automatically generates quizzes for lectures without them
"""

import threading
import time
import logging
from datetime import datetime
from typing import List, Dict
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.storage import get_storage
from services.japanese_ai_service import get_japanese_ai_service
from services.transcript_extractor import get_transcript_from_url, get_transcript_summary
import uuid
import re

logger = logging.getLogger(__name__)


class AutoQuizGenerator:
    """Background service for automated quiz generation"""
    
    def __init__(self, batch_size=3, check_interval=300):
        """
        Initialize auto quiz generator
        
        Args:
            batch_size: Number of quizzes to generate per batch
            check_interval: Seconds between checks (default: 5 minutes)
        """
        self.batch_size = batch_size
        self.check_interval = check_interval
        self.storage = get_storage()
        self.ai_service = get_japanese_ai_service()
        self.is_running = False
        self.thread = None
        self.stats = {
            'total_generated': 0,
            'last_run': None,
            'last_batch_count': 0
        }
    
    def start(self):
        """Start background quiz generation"""
        if self.is_running:
            logger.warning("Auto quiz generator already running")
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        logger.info(f"Auto quiz generator started (batch size: {self.batch_size})")
    
    def stop(self):
        """Stop background quiz generation"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Auto quiz generator stopped")
    
    def _run_loop(self):
        """Main loop for checking and generating quizzes"""
        # Initial delay to let app start
        time.sleep(10)
        
        while self.is_running:
            try:
                self._check_and_generate()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in auto quiz generator: {str(e)}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def _check_and_generate(self):
        """Check for lectures without quizzes and generate them"""
        logger.info("Checking for lectures without quizzes...")
        
        # Get lectures without quizzes
        all_lectures = self.storage.get_all_lectures()
        lectures_needing_quiz = []
        
        for lecture in all_lectures:
            if not lecture.get('quiz') and not lecture.get('quizzes'):
                lectures_needing_quiz.append(lecture)
        
        if not lectures_needing_quiz:
            logger.info("All lectures have quizzes!")
            return
        
        logger.info(f"Found {len(lectures_needing_quiz)} lectures without quizzes")
        
        # Generate batch
        batch = lectures_needing_quiz[:self.batch_size]
        success_count = 0
        
        for lecture in batch:
            try:
                if self._generate_quiz_for_lecture(lecture):
                    success_count += 1
                    time.sleep(3)  # Rate limiting
            except Exception as e:
                logger.error(f"Failed to generate quiz for {lecture['lecture_id']}: {str(e)}")
        
        # Update stats
        self.stats['total_generated'] += success_count
        self.stats['last_run'] = datetime.now().isoformat()
        self.stats['last_batch_count'] = success_count
        
        logger.info(f"Generated {success_count}/{len(batch)} quizzes successfully")
    
    def _generate_quiz_for_lecture(self, lecture: Dict) -> bool:
        """Generate a single quiz for a lecture"""
        try:
            # Get transcript if YouTube
            video_path = lecture.get('video_path', '')
            transcript = ""
            
            if 'youtube.com' in video_path or 'youtu.be' in video_path:
                try:
                    full_transcript = get_transcript_from_url(video_path)
                    if full_transcript:
                        transcript = get_transcript_summary(full_transcript, 2000)
                        logger.info(f"Got transcript ({len(transcript)} chars) for {lecture['title'][:50]}")
                except Exception as e:
                    logger.warning(f"No transcript for {lecture['lecture_id']}: {str(e)}")
            
            # Build context
            context = f"""Title: {lecture['title']}"""
            
            if lecture.get('description'):
                desc = re.sub(r'<[^>]+>', '', lecture['description'])
                context += f"\nDescription: {desc[:400]}"
            
            if transcript:
                context += f"\n\nVideo Content:\n{transcript}"
            
            # Determine question count
            if len(context) > 1500:
                question_count = 7
            elif len(context) > 800:
                question_count = 5
            else:
                question_count = 3
            
            # Generate quiz
            self.ai_service.model = 'openai/gpt-oss-120b'
            
            prompt = f"""Create a quiz about: {lecture['title']}

Content:
{context}

Generate {question_count} multiple-choice questions that test key concepts from this content.
IMPORTANT: Return ONLY valid JSON without markdown code blocks."""
            
            quiz_data = self.ai_service.generate_japanese_quiz(
                topic=prompt,
                difficulty="mixed",
                question_count=question_count,
                quiz_type="mixed"
            )
            
            if quiz_data:
                # Add metadata
                quiz_data['quiz_id'] = f"quiz_{uuid.uuid4().hex[:8]}"
                quiz_data['lecture_id'] = lecture['lecture_id']
                quiz_data['auto_generated'] = True
                quiz_data['generated_at'] = datetime.now().isoformat()
                
                # Save
                self.storage.update_lecture(lecture['lecture_id'], {'quiz': quiz_data})
                logger.info(f"✅ Generated quiz for: {lecture['title'][:50]}")
                return True
            
        except Exception as e:
            logger.error(f"Error generating quiz: {str(e)}")
        
        return False
    
    def get_stats(self) -> Dict:
        """Get generator statistics"""
        return {
            **self.stats,
            'is_running': self.is_running,
            'batch_size': self.batch_size,
            'check_interval': self.check_interval
        }


# Singleton instance
_auto_quiz_generator = None


def get_auto_quiz_generator(batch_size=3, check_interval=300) -> AutoQuizGenerator:
    """Get singleton auto quiz generator instance"""
    global _auto_quiz_generator
    if _auto_quiz_generator is None:
        _auto_quiz_generator = AutoQuizGenerator(batch_size, check_interval)
    return _auto_quiz_generator
