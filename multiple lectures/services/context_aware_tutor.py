"""
Context-Aware AI Tutor Service
Adapts behavior based on course subject and content type
Provides doubt-solving, practice, and personalized learning
"""

import os
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json

# Import the base AI service
try:
    from services.config_loader import get_api_key
except ImportError:
    get_api_key = lambda provider: os.getenv({
        'groq': 'GROQ_API_KEY',
        'openai': 'OPENAI_API_KEY',
        'gemini': 'GOOGLE_API_KEY'
    }.get(provider))

# AI provider availability
GROQ_AVAILABLE = False
OPENAI_AVAILABLE = False
GEMINI_AVAILABLE = False

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    pass

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    pass

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    pass


class ContextAwareAITutor:
    """
    Intelligent AI tutor that adapts to different subjects and learning needs
    
    Modes:
    - language_learning: For Japanese, Spanish, etc. (speaking, listening, reading)
    - subject_tutor: For History, Math, Science (concept explanation, Q&A)
    - study_assistant: General help (homework, exam prep, note-taking)
    - doubt_solver: Answer specific questions about content
    """
    
    # Available Groq models for different tasks
    MODELS = {
        'reasoning': 'openai/gpt-oss-120b',  # Best for complex explanations
        'fast': 'openai/gpt-oss-20b',         # Faster for simple Q&A
        'japanese': 'qwen/qwen3-32b',         # Best for Asian languages
        'long_context': 'moonshotai/kimi-k2-instruct'  # For long transcripts
    }
    
    def __init__(self, provider: str = "groq", model: str = None):
        """
        Initialize context-aware AI tutor
        
        Args:
            provider: AI provider ("groq", "openai", "gemini")
            model: Specific model to use (auto-selected if None)
        """
        self.provider = provider
        self.model = model or self.MODELS['reasoning']  # Default to best reasoning model
        self.client = None
        self._initialize_client()
        
        # Context tracking
        self.current_course = None
        self.current_lecture = None
        self.current_subject = None
        self.current_mode = "subject_tutor"  # Default mode
        
    def _initialize_client(self):
        """Initialize AI client"""
        if self.provider == "groq" and GROQ_AVAILABLE:
            api_key = get_api_key("groq")
            if api_key:
                self.client = Groq(api_key=api_key)
                logging.info("✓ Groq tutor initialized")
        elif self.provider == "openai" and OPENAI_AVAILABLE:
            api_key = get_api_key("openai")
            if api_key:
                openai.api_key = api_key
                self.client = openai
                logging.info("✓ OpenAI tutor initialized")
        elif self.provider == "gemini" and GEMINI_AVAILABLE:
            api_key = get_api_key("gemini")
            if api_key:
                genai.configure(api_key=api_key)
                self.client = genai
                logging.info("✓ Gemini tutor initialized")
    
    def is_available(self) -> bool:
        """Check if tutor is ready"""
        return self.client is not None
    
    def set_context(self, course: Dict, lecture: Dict = None):
        """
        Set learning context and auto-select optimal model
        
        Args:
            course: Course dictionary with name, description, subject
            lecture: Optional lecture dictionary
        """
        self.current_course = course
        self.current_lecture = lecture
        
        # Detect subject type
        course_name = course.get('name', '').lower()
        course_desc = course.get('description', '').lower()
        
        if any(word in course_name or word in course_desc 
               for word in ['japanese', 'chinese', 'korean', 'spanish', 'french', 'german', 'language', 'asian']):
            self.current_subject = 'language'
            self.subject_type = 'language'  # Keep for backward compatibility
            self.current_mode = 'language_learning'
            self.mode = 'language_learning'
            # Use specialized Asian language model for better results
            self.model = self.MODELS['japanese']
            logging.info(f"✓ Context: Language course detected, using {self.model}")
        elif any(word in course_name or word in course_desc
                for word in ['history', 'geography', 'social']):
            self.current_subject = 'history'
            self.subject_type = 'history'
            self.current_mode = 'subject_tutor'
            self.mode = 'subject_tutor'
            self.model = self.MODELS['reasoning']  # Best for explanations
        elif any(word in course_name or word in course_desc
                for word in ['math', 'calculus', 'algebra', 'geometry']):
            self.current_subject = 'math'
            self.subject_type = 'math'
            self.current_mode = 'subject_tutor'
            self.mode = 'subject_tutor'
            self.model = self.MODELS['reasoning']  # Best for math explanations
        elif any(word in course_name or word in course_desc
                for word in ['science', 'physics', 'chemistry', 'biology']):
            self.current_subject = 'science'
            self.subject_type = 'science'
            self.current_mode = 'subject_tutor'
            self.mode = 'subject_tutor'
            self.model = self.MODELS['reasoning']  # Best for detailed explanations
        else:
            self.current_subject = 'general'
            self.subject_type = 'general'
            self.current_mode = 'subject_tutor'
            self.mode = 'subject_tutor'
            self.model = self.MODELS['reasoning']  # Default to best quality model
    
    def _get_system_prompt(self, mode: str = None) -> str:
        """Get system prompt based on mode and context"""
        mode = mode or self.mode
        
        course_name = self.current_course.get('name', 'this course') if self.current_course else 'this course'
        lecture_title = self.current_lecture.get('title', 'this lecture') if self.current_lecture else 'this lecture'
        
        prompts = {
            'language_learning': f"""You are a patient language tutor for {course_name}.
Help students with:
- Reading comprehension and translation
- Grammar explanations
- Vocabulary building
- Pronunciation tips
- Cultural context
- Writing practice feedback

Current lecture: {lecture_title}

Be encouraging, explain clearly, and provide examples.""",
            
            'subject_tutor': f"""You are an expert tutor for {course_name}.
Help students understand concepts by:
- Explaining difficult topics clearly
- Providing examples and analogies
- Answering questions thoroughly
- Breaking down complex ideas
- Connecting concepts to real-world applications

Current lecture: {lecture_title}

Be patient, thorough, and encouraging.""",
            
            'doubt_solver': f"""You are a helpful teaching assistant for {course_name}.
Answer student questions by:
- Providing clear, accurate answers
- Explaining the reasoning
- Giving examples
- Suggesting related resources
- Checking understanding

Current lecture: {lecture_title}

Be concise but thorough.""",
            
            'study_assistant': f"""You are a study coach helping with {course_name}.
Assist students with:
- Study strategies
- Exam preparation
- Note-taking techniques
- Time management
- Practice problems
- Review sessions

Current lecture: {lecture_title}

Be practical and supportive."""
        }
        
        return prompts.get(mode, prompts['subject_tutor'])
    
    def _call_ai(self, prompt: str, system_prompt: str = None, temperature: float = 0.7) -> str:
        """Call AI with prompt"""
        try:
            if self.provider == "groq":
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                # Use current model (auto-selected based on subject/task)
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=2000
                )
                return response.choices[0].message.content
                
            elif self.provider == "openai":
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                response = self.client.ChatCompletion.create(
                    model="gpt-4",
                    messages=messages,
                    temperature=temperature,
                    max_tokens=2000
                )
                return response.choices[0].message.content
                
            elif self.provider == "gemini":
                model = self.client.GenerativeModel('gemini-pro')
                full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
                response = model.generate_content(full_prompt)
                return response.text
                
        except Exception as e:
            logging.error(f"AI call failed: {e}")
            return f"Error: {str(e)}"
    
    def solve_doubt(self, question: str, context: str = None) -> str:
        """
        Answer student's question
        
        Args:
            question: Student's question
            context: Optional additional context (lecture content, transcript, etc.)
            
        Returns:
            AI answer
        """
        system_prompt = self._get_system_prompt('doubt_solver')
        
        prompt_parts = []
        if context:
            prompt_parts.append(f"Context:\n{context}\n")
        
        prompt_parts.append(f"Student Question: {question}")
        prompt_parts.append("\nProvide a clear, helpful answer.")
        
        prompt = "\n".join(prompt_parts)
        
        return self._call_ai(prompt, system_prompt, temperature=0.5)
    
    def generate_contextual_quiz(self, content: str, question_count: int = 5) -> Dict:
        """
        Generate quiz based on actual content (transcript, notes, etc.)
        
        Args:
            content: Lecture content (transcript, description, etc.)
            question_count: Number of questions
            
        Returns:
            Quiz dictionary
        """
        system_prompt = f"""You are a quiz creator for {self.subject_type or 'this subject'}.
Generate {question_count} multiple-choice questions based on the provided content.

Format as JSON:
{{
  "title": "Quiz Title",
  "questions": [
    {{
      "question": "Question text",
      "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
      "correct_answer": "A",
      "explanation": "Why this is correct"
    }}
  ]
}}"""
        
        prompt = f"""Based on this lecture content, generate {question_count} questions:

{content[:2000]}

Create questions that test understanding of the key concepts."""
        
        response = self._call_ai(prompt, system_prompt, temperature=0.6)
        
        try:
            quiz_data = json.loads(response)
            quiz_data['quiz_id'] = f"quiz_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            quiz_data['auto_generated'] = True
            quiz_data['context_aware'] = True
            quiz_data['subject_type'] = self.subject_type
            return quiz_data
        except:
            logging.error(f"Failed to parse quiz JSON: {response}")
            return None
    
    def explain_concept(self, concept: str, difficulty: str = "simple") -> str:
        """
        Explain a concept in simple terms
        
        Args:
            concept: Concept to explain
            difficulty: simple/detailed/advanced
            
        Returns:
            Explanation
        """
        system_prompt = self._get_system_prompt()
        
        difficulty_instructions = {
            'simple': 'Explain in simple, easy-to-understand terms. Use analogies.',
            'detailed': 'Provide a comprehensive explanation with examples.',
            'advanced': 'Give an in-depth, technical explanation.'
        }
        
        prompt = f"""Explain this concept: {concept}

{difficulty_instructions.get(difficulty, difficulty_instructions['simple'])}

Make it clear and engaging."""
        
        return self._call_ai(prompt, system_prompt, temperature=0.6)
    
    def chat(self, message: str, conversation_history: List[Dict] = None) -> str:
        """
        General chat with context awareness
        
        Args:
            message: User message
            conversation_history: Previous messages
            
        Returns:
            AI response
        """
        system_prompt = self._get_system_prompt()
        
        # Build context from history
        context = ""
        if conversation_history:
            for msg in conversation_history[-5:]:  # Last 5 messages
                role = "Student" if msg['role'] == 'user' else "Tutor"
                context += f"{role}: {msg['content']}\n"
        
        prompt = f"""{context}Student: {message}

Respond helpfully and encouragingly."""
        
        return self._call_ai(prompt, system_prompt, temperature=0.7)


# Singleton instance
_context_aware_tutor = None

def get_context_aware_tutor(provider: str = "groq") -> ContextAwareAITutor:
    """Get singleton tutor instance"""
    global _context_aware_tutor
    if _context_aware_tutor is None:
        _context_aware_tutor = ContextAwareAITutor(provider=provider)
    return _context_aware_tutor


if __name__ == "__main__":
    # Test
    tutor = get_context_aware_tutor("groq")
    
    if tutor.is_available():
        # Test with Japanese course
        japanese_course = {
            'name': 'Japanese for Beginners',
            'description': 'Learn Japanese language basics'
        }
        
        tutor.set_context(japanese_course)
        print(f"Mode: {tutor.mode}")
        print(f"Subject: {tutor.subject_type}")
        
        # Test with History course
        history_course = {
            'name': 'World History',
            'description': 'Study of major historical events'
        }
        
        tutor.set_context(history_course)
        print(f"Mode: {tutor.mode}")
        print(f"Subject: {tutor.subject_type}")
    else:
        print("Tutor not available - set API key")
