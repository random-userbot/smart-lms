"""
Japanese Learning AI Service
Integrates AI assistance for Japanese language learning:
- Reading comprehension help
- Writing feedback and correction
- Speaking practice evaluation (with text-to-speech)
- Conversation practice
- Quiz generation
- Assignment grading

Supports multiple AI providers:
1. Groq (FREE, recommended) - Very fast, generous free tier
2. OpenAI (paid) - Higher quality, more features
3. Google Gemini (FREE) - Good multilingual support
"""

import os
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import re

# Try importing different AI providers
GROQ_AVAILABLE = False
OPENAI_AVAILABLE = False
GEMINI_AVAILABLE = False

try:
    from groq import Groq
    GROQ_AVAILABLE = True
    logging.info("✓ Groq AI available")
except ImportError:
    logging.info("Groq not installed. Install with: pip install groq")

try:
    import openai
    OPENAI_AVAILABLE = True
    logging.info("✓ OpenAI available")
except ImportError:
    logging.info("OpenAI not installed. Install with: pip install openai")

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
    logging.info("✓ Google Gemini available")
except ImportError:
    logging.info("Gemini not installed. Install with: pip install google-generativeai")


class JapaneseAIService:
    """AI service specialized for Japanese language learning"""
    
    def __init__(self, provider: str = "groq", model: str = None):
        """
        Initialize Japanese AI service
        
        Args:
            provider: "groq" (free, fast), "openai" (paid, quality), or "gemini" (free)
            model: Specific model to use (auto-selected if None)
        """
        self.provider = provider
        self.model = model
        self.client = None
        self._initialize_client()
        
        # Auto-select best model if not specified
        if not self.model and provider == "groq":
            self.model = "openai/gpt-oss-120b"  # Best reasoning model
        
    def _initialize_client(self):
        """Initialize the selected AI provider"""
        # Try to import config loader
        try:
            from services.config_loader import get_api_key
            get_key = lambda provider: get_api_key(provider)
        except ImportError:
            # Fallback to environment variables only
            get_key = lambda provider: os.getenv({
                'groq': 'GROQ_API_KEY',
                'openai': 'OPENAI_API_KEY',
                'gemini': 'GOOGLE_API_KEY'
            }.get(provider))
        
        if self.provider == "groq" and GROQ_AVAILABLE:
            api_key = get_key("groq")
            if api_key:
                self.client = Groq(api_key=api_key)
                logging.info("✓ Groq client initialized")
            else:
                logging.warning("GROQ_API_KEY not found in config.yaml or environment")
                
        elif self.provider == "openai" and OPENAI_AVAILABLE:
            api_key = get_key("openai")
            if api_key:
                openai.api_key = api_key
                self.client = openai
                logging.info("✓ OpenAI client initialized")
            else:
                logging.warning("OPENAI_API_KEY not found in config.yaml or environment")
                
        elif self.provider == "gemini" and GEMINI_AVAILABLE:
            api_key = get_key("gemini")
            if api_key:
                genai.configure(api_key=api_key)
                self.client = genai
                logging.info("✓ Gemini client initialized")
            else:
                logging.warning("GOOGLE_API_KEY not found in config.yaml or environment")
    
    def is_available(self) -> bool:
        """Check if AI service is available"""
        return self.client is not None
    
    def _call_ai(self, prompt: str, system_prompt: str = None, temperature: float = 0.7) -> str:
        """
        Generic AI call wrapper
        
        Args:
            prompt: User prompt
            system_prompt: System instructions
            temperature: Creativity (0.0-1.0)
            
        Returns:
            AI response text
        """
        try:
            if self.provider == "groq":
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                # Use specified model or default
                model_to_use = self.model or "openai/gpt-oss-120b"
                
                response = self.client.chat.completions.create(
                    model=model_to_use,
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
                    model="gpt-4",  # Best quality
                    messages=messages,
                    temperature=temperature,
                    max_tokens=2000
                )
                return response.choices[0].message.content
                
            elif self.provider == "gemini":
                # Use gemini-2.0-flash (current stable model)
                model = self.client.GenerativeModel('gemini-2.0-flash')
                full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
                response = model.generate_content(full_prompt)
                return response.text
                
        except Exception as e:
            logging.error(f"AI call failed: {e}")
            return f"Error: {str(e)}"
    
    # ========================
    # READING COMPREHENSION
    # ========================
    
    def explain_japanese_text(self, text: str, difficulty: str = "beginner") -> Dict:
        """
        Explain Japanese text with translations, grammar, and cultural notes
        
        Args:
            text: Japanese text to explain
            difficulty: "beginner", "intermediate", "advanced"
            
        Returns:
            Dictionary with explanations
        """
        system_prompt = """You are a patient Japanese language tutor. 
        Help students understand Japanese text by providing:
        1. English translation
        2. Word-by-word breakdown with readings (furigana)
        3. Grammar explanations
        4. Cultural context if relevant
        
        Format your response as JSON with keys: translation, breakdown, grammar, cultural_notes"""
        
        prompt = f"""Explain this Japanese text for a {difficulty} level student:

{text}

Provide a comprehensive explanation including translation, vocabulary breakdown, grammar points, and any cultural context."""
        
        response = self._call_ai(prompt, system_prompt, temperature=0.3)
        
        try:
            # Try to parse JSON response
            return json.loads(response)
        except:
            # Fallback to plain text
            return {
                "translation": response,
                "breakdown": "See above",
                "grammar": "See above",
                "cultural_notes": "See above"
            }
    
    def generate_reading_questions(self, text: str, count: int = 5) -> List[Dict]:
        """
        Generate comprehension questions for Japanese text
        
        Args:
            text: Japanese text
            count: Number of questions
            
        Returns:
            List of question dictionaries
        """
        system_prompt = """You are a Japanese language assessment expert.
        Generate multiple-choice reading comprehension questions in JSON format.
        Each question should test understanding of the text."""
        
        prompt = f"""Based on this Japanese text, generate {count} multiple-choice questions:

{text}

Format as JSON array with structure:
[
  {{
    "question": "Question in English",
    "question_ja": "Question in Japanese",
    "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
    "correct_answer": "A",
    "explanation": "Why this is correct"
  }}
]"""
        
        response = self._call_ai(prompt, system_prompt, temperature=0.5)
        
        try:
            return json.loads(response)
        except:
            return []
    
    # ========================
    # WRITING ASSISTANCE
    # ========================
    
    def correct_japanese_writing(self, text: str, context: str = "general") -> Dict:
        """
        Correct Japanese writing and provide feedback
        
        Args:
            text: Student's Japanese writing
            context: Writing context (email, essay, conversation, etc.)
            
        Returns:
            Dictionary with corrections and feedback
        """
        system_prompt = """You are a Japanese writing tutor. 
        Correct the student's Japanese writing and provide:
        1. Corrected version
        2. List of errors with explanations
        3. Suggestions for improvement
        4. Overall feedback
        
        Be encouraging while being thorough about corrections."""
        
        prompt = f"""Please review and correct this Japanese {context} writing:

{text}

Provide detailed feedback on:
- Grammar mistakes
- Vocabulary usage
- Particle usage
- Kanji/Hiragana/Katakana errors
- Style and naturalness
- Suggestions for improvement"""
        
        response = self._call_ai(prompt, system_prompt, temperature=0.3)
        
        return {
            "corrected_text": response,
            "feedback": response,
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_writing_prompts(self, level: str = "beginner", count: int = 3) -> List[str]:
        """
        Generate Japanese writing prompts
        
        Args:
            level: Student level
            count: Number of prompts
            
        Returns:
            List of writing prompts
        """
        system_prompt = f"""Generate {count} creative writing prompts appropriate for {level} level Japanese learners."""
        
        prompt = f"""Create {count} engaging writing prompts that will help {level} students practice Japanese writing. Include topics like daily life, hobbies, travel, food, etc."""
        
        response = self._call_ai(prompt, system_prompt, temperature=0.8)
        
        # Parse response into list
        prompts = [p.strip() for p in response.split('\n') if p.strip() and not p.strip().startswith('#')]
        return prompts[:count]
    
    # ========================
    # CONVERSATION PRACTICE
    # ========================
    
    def practice_conversation(self, user_message: str, conversation_history: List[Dict] = None, 
                            scenario: str = "casual") -> Dict:
        """
        AI conversation partner for Japanese practice
        
        Args:
            user_message: Student's message in Japanese
            conversation_history: Previous messages
            scenario: Conversation scenario (casual, business, travel, etc.)
            
        Returns:
            Dictionary with AI response and feedback
        """
        system_prompt = f"""You are a friendly Japanese conversation partner for a {scenario} scenario.
        Respond naturally in Japanese, then provide:
        1. English translation of your response
        2. Feedback on the student's Japanese (if they wrote in Japanese)
        3. Suggestions for alternative expressions
        
        Keep responses natural and at an appropriate level."""
        
        # Build conversation context
        context = ""
        if conversation_history:
            for msg in conversation_history[-5:]:  # Last 5 messages
                role = "Student" if msg['role'] == 'user' else "Tutor"
                context += f"{role}: {msg['content']}\n"
        
        prompt = f"""Conversation scenario: {scenario}

{context}
Student: {user_message}

Respond naturally in Japanese and provide helpful feedback."""
        
        response = self._call_ai(prompt, system_prompt, temperature=0.7)
        
        return {
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "scenario": scenario
        }
    
    # ========================
    # QUIZ GENERATION
    # ========================
    
    def generate_japanese_quiz(self, topic: str, difficulty: str = "beginner", 
                              question_count: int = 10, quiz_type: str = "mixed") -> Dict:
        """
        Generate Japanese language quiz
        
        Args:
            topic: Quiz topic (vocabulary, grammar, kanji, etc.)
            difficulty: beginner, intermediate, advanced
            question_count: Number of questions
            quiz_type: "vocabulary", "grammar", "kanji", "reading", "mixed"
            
        Returns:
            Complete quiz dictionary
        """
        system_prompt = f"""You are a Japanese language assessment expert.
        Create a {difficulty} level quiz on {topic} with {question_count} questions.
        
        Format as JSON with structure:
        {{
          "title": "Quiz title",
          "description": "Brief description",
          "time_limit": minutes,
          "questions": [
            {{
              "type": "mcq",
              "question": "Question text",
              "question_ja": "Question in Japanese (if applicable)",
              "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
              "correct_answer": "A",
              "explanation": "Why this is correct",
              "difficulty": "easy/medium/hard"
            }}
          ]
        }}"""
        
        prompt = f"""Generate a {difficulty} level Japanese {quiz_type} quiz on the topic: {topic}

Create {question_count} varied questions that test different aspects of Japanese language skills.
Include questions about:
- Vocabulary usage and meanings
- Grammar patterns and particles
- Kanji readings and meanings (if applicable)
- Sentence structure
- Cultural context

Make questions engaging and educational."""
        
        response = self._call_ai(prompt, system_prompt, temperature=0.6)
        
        try:
            # Clean response - remove markdown code blocks
            import re
            cleaned = re.sub(r'```json\s*', '', response)
            cleaned = re.sub(r'```\s*$', '', cleaned)
            cleaned = cleaned.strip()
            
            quiz_data = json.loads(cleaned)
            # Add metadata
            quiz_data['quiz_id'] = f"ai_quiz_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            quiz_data['created_by'] = 'ai_generated'
            quiz_data['created_at'] = datetime.now().isoformat()
            quiz_data['topic'] = topic
            quiz_data['difficulty'] = difficulty
            return quiz_data
        except Exception as e:
            logging.error(f"Failed to parse quiz JSON: {cleaned if 'cleaned' in locals() else response[:500]}")
            return None
    
    # ========================
    # ASSIGNMENT GRADING
    # ========================
    
    def grade_japanese_assignment(self, assignment_text: str, rubric: Dict = None) -> Dict:
        """
        Grade Japanese language assignment
        
        Args:
            assignment_text: Student's submission
            rubric: Grading rubric (optional)
            
        Returns:
            Dictionary with grade, feedback, and detailed scoring
        """
        rubric_text = ""
        if rubric:
            rubric_text = f"\n\nGrading Rubric:\n{json.dumps(rubric, indent=2)}"
        
        system_prompt = f"""You are a Japanese language teacher grading student work.
        Evaluate the assignment on:
        1. Grammar accuracy (25%)
        2. Vocabulary usage (25%)
        3. Content/completeness (25%)
        4. Style/naturalness (25%)
        
        Provide:
        - Overall score (0-100)
        - Detailed breakdown by category
        - Constructive feedback
        - Specific corrections
        - Suggestions for improvement{rubric_text}"""
        
        prompt = f"""Grade this Japanese language assignment:

{assignment_text}

Provide a detailed evaluation with scores and feedback."""
        
        response = self._call_ai(prompt, system_prompt, temperature=0.3)
        
        # Try to extract score from response
        score_match = re.search(r'(\d+)/100|score:?\s*(\d+)', response.lower())
        score = int(score_match.group(1) or score_match.group(2)) if score_match else 75
        
        return {
            "score": score,
            "max_score": 100,
            "percentage": score,
            "feedback": response,
            "graded_by": "ai",
            "graded_at": datetime.now().isoformat(),
            "breakdown": {
                "grammar": score * 0.25,
                "vocabulary": score * 0.25,
                "content": score * 0.25,
                "style": score * 0.25
            }
        }
    
    def suggest_assignment_topics(self, level: str = "beginner", count: int = 5) -> List[Dict]:
        """
        Generate Japanese assignment topics
        
        Args:
            level: Student level
            count: Number of topics
            
        Returns:
            List of assignment topic dictionaries
        """
        system_prompt = f"""Generate {count} engaging assignment topics for {level} level Japanese students."""
        
        prompt = f"""Create {count} creative assignment topics that help {level} students practice Japanese.
        
        For each topic, include:
        - Title
        - Description
        - Learning objectives
        - Suggested word count
        - Key grammar/vocabulary to practice
        
        Format as JSON array."""
        
        response = self._call_ai(prompt, system_prompt, temperature=0.7)
        
        try:
            return json.loads(response)
        except:
            return []
    
    # ========================
    # SPEAKING PRACTICE
    # ========================
    
    def evaluate_pronunciation_text(self, text: str, student_text: str) -> Dict:
        """
        Evaluate pronunciation by comparing expected vs student text
        (For use with speech-to-text transcription)
        
        Args:
            text: Expected Japanese text
            student_text: What student said (transcribed)
            
        Returns:
            Dictionary with pronunciation feedback
        """
        system_prompt = """You are a Japanese pronunciation tutor.
        Compare the expected text with what the student actually said.
        Provide feedback on pronunciation accuracy."""
        
        prompt = f"""Expected: {text}
Student said: {student_text}

Provide feedback on:
- Pronunciation accuracy
- Common mistakes
- Suggestions for improvement"""
        
        response = self._call_ai(prompt, system_prompt, temperature=0.3)
        
        # Calculate similarity score
        similarity = self._calculate_similarity(text, student_text)
        
        return {
            "accuracy_score": similarity,
            "feedback": response,
            "expected": text,
            "actual": student_text
        }
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple similarity score between two texts"""
        # Simple character-level similarity
        if not text1 or not text2:
            return 0.0
        
        matches = sum(1 for c1, c2 in zip(text1, text2) if c1 == c2)
        max_len = max(len(text1), len(text2))
        return (matches / max_len) * 100 if max_len > 0 else 0.0


# ========================
# SINGLETON INSTANCE
# ========================

_japanese_ai_service = None

def get_japanese_ai_service(provider: str = "groq") -> JapaneseAIService:
    """
    Get singleton instance of Japanese AI service
    
    Args:
        provider: "groq" (free, recommended), "openai" (paid), or "gemini" (free)
        
    Returns:
        JapaneseAIService instance
    """
    global _japanese_ai_service
    if _japanese_ai_service is None:
        _japanese_ai_service = JapaneseAIService(provider=provider)
    return _japanese_ai_service


# ========================
# AVAILABILITY CHECK
# ========================

def check_ai_availability() -> Dict[str, bool]:
    """
    Check which AI providers are available
    
    Returns:
        Dictionary of provider availability
    """
    # Try to import config loader
    try:
        from services.config_loader import get_api_key
        get_key = lambda provider: get_api_key(provider)
    except ImportError:
        # Fallback to environment variables only
        get_key = lambda provider: os.getenv({
            'groq': 'GROQ_API_KEY',
            'openai': 'OPENAI_API_KEY',
            'gemini': 'GOOGLE_API_KEY'
        }.get(provider))
    
    return {
        "groq": GROQ_AVAILABLE and get_key("groq") is not None,
        "openai": OPENAI_AVAILABLE and get_key("openai") is not None,
        "gemini": GEMINI_AVAILABLE and get_key("gemini") is not None
    }


if __name__ == "__main__":
    # Test the service
    print("AI Provider Availability:")
    availability = check_ai_availability()
    for provider, available in availability.items():
        status = "✓ Available" if available else "✗ Not available"
        print(f"  {provider}: {status}")
    
    if any(availability.values()):
        provider = next(p for p, avail in availability.items() if avail)
        print(f"\nTesting with {provider}...")
        
        service = get_japanese_ai_service(provider=provider)
        
        # Test text explanation
        result = service.explain_japanese_text("こんにちは、元気ですか？", "beginner")
        print("\nText Explanation:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
