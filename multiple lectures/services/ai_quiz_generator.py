"""
Smart LMS - AI-Powered Quiz Generator Service
Interactive quiz generation with Groq AI
Teacher reviews and approves each question before adding to quiz
"""

import os
from groq import Groq
from typing import List, Dict, Optional
import json
from datetime import datetime


class AIQuizGenerator:
    """AI-powered quiz generator using Groq"""
    
    def __init__(self):
        self.api_key = os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        
        self.client = Groq(api_key=self.api_key)
        self.model = "mixtral-8x7b-32768"  # Groq's Mixtral model
        
        self.question_history = []  # Track generated questions for context
        self.lecture_context = None
    
    def set_lecture_context(self, lecture_title: str, transcript: str, description: str = ""):
        """Set the lecture context for quiz generation"""
        self.lecture_context = {
            'title': lecture_title,
            'transcript': transcript,
            'description': description
        }
        self.question_history = []  # Reset history for new lecture
    
    def generate_question(
        self, 
        custom_prompt: Optional[str] = None,
        difficulty: str = "medium",
        question_type: str = "multiple_choice"
    ) -> Dict:
        """
        Generate a single quiz question based on lecture content
        
        Args:
            custom_prompt: Custom instructions from teacher (optional)
            difficulty: "easy", "medium", or "hard"
            question_type: "multiple_choice", "true_false", or "short_answer"
        
        Returns:
            Dict with question, options, correct_answer, explanation
        """
        if not self.lecture_context:
            raise ValueError("Lecture context not set. Call set_lecture_context() first.")
        
        # Build context-aware prompt
        system_prompt = self._build_system_prompt(difficulty, question_type)
        user_prompt = self._build_user_prompt(custom_prompt, difficulty, question_type)
        
        try:
            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Parse response
            generated_text = response.choices[0].message.content
            question_data = self._parse_question_response(generated_text, question_type)
            
            # Add to history
            self.question_history.append(question_data)
            
            return question_data
        
        except Exception as e:
            return {
                'error': True,
                'message': f"Failed to generate question: {str(e)}",
                'question': "Error generating question",
                'options': [],
                'correct_answer': "",
                'explanation': ""
            }
    
    def _build_system_prompt(self, difficulty: str, question_type: str) -> str:
        """Build system prompt for AI"""
        return f"""You are an expert educational quiz generator. Your task is to create high-quality quiz questions based on lecture content.

Guidelines:
- Generate {difficulty} difficulty questions
- Question type: {question_type}
- Questions must be clear, unambiguous, and educational
- For multiple choice: provide exactly 4 options labeled A, B, C, D
- One option must be clearly correct
- Include a brief explanation for the correct answer
- Avoid questions that are too easy or trick questions
- Focus on testing understanding, not memorization
- DO NOT repeat topics from previous questions in this quiz

Output Format (JSON):
{{
    "question": "The question text here",
    "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
    "correct_answer": "A",
    "explanation": "Brief explanation of why this is correct"
}}

Return ONLY the JSON, no additional text."""
    
    def _build_user_prompt(self, custom_prompt: Optional[str], difficulty: str, question_type: str) -> str:
        """Build user prompt with lecture context"""
        # Get previous questions summary
        previous_topics = []
        if self.question_history:
            previous_topics = [q.get('topic', q.get('question', '')[:50]) for q in self.question_history[-5:]]
        
        prompt = f"""Lecture Title: {self.lecture_context['title']}

Lecture Transcript/Content:
{self.lecture_context['transcript'][:3000]}  

{"Previous Questions Topics (avoid these): " + ", ".join(previous_topics) if previous_topics else ""}

Difficulty: {difficulty}
Question Type: {question_type}

{f"Teacher's Custom Instructions: {custom_prompt}" if custom_prompt else ""}

Generate a new quiz question based on the lecture content above. Follow the JSON format specified in the system prompt."""
        
        return prompt
    
    def _parse_question_response(self, response_text: str, question_type: str) -> Dict:
        """Parse AI response into structured question data"""
        try:
            # Try to extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                data = json.loads(json_str)
                
                # Validate required fields
                if 'question' in data and 'correct_answer' in data:
                    # Add metadata
                    data['question_type'] = question_type
                    data['generated_at'] = datetime.now().isoformat()
                    
                    # Extract topic from question for history tracking
                    data['topic'] = data['question'][:50]
                    
                    return data
        
        except json.JSONDecodeError:
            pass
        
        # Fallback: manual parsing
        return self._manual_parse(response_text, question_type)
    
    def _manual_parse(self, text: str, question_type: str) -> Dict:
        """Manually parse response if JSON parsing fails"""
        lines = text.strip().split('\n')
        
        question = ""
        options = []
        correct_answer = ""
        explanation = ""
        
        for line in lines:
            line = line.strip()
            if line.startswith('Question:') or line.startswith('Q:'):
                question = line.split(':', 1)[1].strip()
            elif line.startswith(('A)', 'B)', 'C)', 'D)')):
                options.append(line)
            elif line.startswith('Correct:') or line.startswith('Answer:'):
                correct_answer = line.split(':', 1)[1].strip()[0]  # Get first character (A, B, C, or D)
            elif line.startswith('Explanation:'):
                explanation = line.split(':', 1)[1].strip()
        
        return {
            'question': question or "Could not parse question",
            'options': options or ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
            'correct_answer': correct_answer or "A",
            'explanation': explanation or "No explanation provided",
            'question_type': question_type,
            'generated_at': datetime.now().isoformat()
        }
    
    def regenerate_question(
        self,
        feedback: str,
        previous_question: Dict,
        difficulty: str = "medium"
    ) -> Dict:
        """Regenerate a question based on teacher feedback"""
        custom_prompt = f"""The previous question was not satisfactory. 
Previous question: {previous_question.get('question', '')}
Teacher feedback: {feedback}

Please generate a new, improved question that addresses this feedback."""
        
        return self.generate_question(
            custom_prompt=custom_prompt,
            difficulty=difficulty,
            question_type=previous_question.get('question_type', 'multiple_choice')
        )
    
    def get_quiz_summary(self) -> Dict:
        """Get summary of generated questions"""
        return {
            'total_questions': len(self.question_history),
            'difficulty_distribution': self._get_difficulty_distribution(),
            'topics_covered': [q.get('topic', '') for q in self.question_history]
        }
    
    def _get_difficulty_distribution(self) -> Dict[str, int]:
        """Get distribution of question difficulties"""
        distribution = {'easy': 0, 'medium': 0, 'hard': 0}
        # This would need difficulty to be stored with each question
        # For now, return estimated distribution
        return distribution
    
    def reset_session(self):
        """Reset the quiz generation session"""
        self.question_history = []
        self.lecture_context = None


# Singleton instance
_quiz_generator = None


def get_ai_quiz_generator() -> AIQuizGenerator:
    """Get singleton instance of AI quiz generator"""
    global _quiz_generator
    if _quiz_generator is None:
        _quiz_generator = AIQuizGenerator()
    return _quiz_generator
