"""
Audio Practice Service
Provides Text-to-Speech and Speech-to-Text for language learning
Supports listening and speaking practice
"""

import os
import logging
from typing import Optional, Dict
import base64

# Import config loader for API keys
from services.config_loader import get_api_key

# Text-to-Speech providers
TTS_AVAILABLE = False
GTTS_AVAILABLE = False

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
    TTS_AVAILABLE = True
    logging.info("✓ Google TTS (gTTS) available")
except ImportError:
    logging.info("gTTS not installed. Install with: pip install gTTS")

# Speech-to-Text with Groq Whisper
STT_AVAILABLE = False
GROQ_WHISPER_AVAILABLE = False

try:
    from groq import Groq
    GROQ_WHISPER_AVAILABLE = True
    STT_AVAILABLE = True
    logging.info("✓ Groq Whisper (STT) available")
except ImportError:
    logging.info("Groq not installed. Install with: pip install groq")


class AudioPracticeService:
    """Service for audio-based language practice"""
    
    # Whisper model for speech-to-text
    WHISPER_MODEL = "whisper-large-v3-turbo"  # Fast and accurate
    
    def __init__(self):
        self.tts_engine = "gtts" if GTTS_AVAILABLE else None
        self.stt_engine = None
        self.groq_client = None
        
        # Initialize Groq Whisper if available
        if GROQ_WHISPER_AVAILABLE:
            api_key = get_api_key("groq")
            if api_key:
                self.groq_client = Groq(api_key=api_key)
                self.stt_engine = "whisper"
                logging.info(f"✓ Groq Whisper initialized with model: {self.WHISPER_MODEL}")
    
    def is_available(self) -> bool:
        """Check if audio services are available"""
        return TTS_AVAILABLE or STT_AVAILABLE
    
    def text_to_speech(self, text: str, language: str = 'ja', slow: bool = False) -> Optional[str]:
        """
        Convert text to speech audio
        
        Args:
            text: Text to convert
            language: Language code ('ja', 'en', 'es', etc.)
            slow: Whether to speak slowly
            
        Returns:
            Base64 encoded audio data or file path
        """
        if not GTTS_AVAILABLE:
            logging.error("TTS not available")
            return None
        
        try:
            # Create TTS object
            tts = gTTS(text=text, lang=language, slow=slow)
            
            # Save to temporary file
            import tempfile
            import time
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            temp_path = temp_file.name
            temp_file.close()  # Close before saving
            
            tts.save(temp_path)
            
            # Read and encode
            with open(temp_path, 'rb') as f:
                audio_data = f.read()
            
            # Clean up with retry
            try:
                time.sleep(0.1)  # Small delay
                os.unlink(temp_path)
            except:
                pass  # Ignore cleanup errors
            
            # Return base64 encoded
            return base64.b64encode(audio_data).decode('utf-8')
            
        except Exception as e:
            logging.error(f"TTS error: {e}")
            return None
    
    def create_listening_exercise(self, text: str, language: str = 'ja') -> Dict:
        """
        Create listening comprehension exercise
        
        Args:
            text: Text for listening
            language: Language code
            
        Returns:
            Exercise dictionary with audio
        """
        # Generate audio
        audio_data = self.text_to_speech(text, language)
        
        if not audio_data:
            return None
        
        return {
            'text': text,
            'audio': audio_data,
            'language': language,
            'type': 'listening_comprehension'
        }
    
    def get_pronunciation_feedback(self, expected_text: str, spoken_text: str, 
                                   language: str = 'ja') -> Dict:
        """
        Compare expected text with what was spoken
        
        Args:
            expected_text: What should be said
            spoken_text: What was actually said (from STT)
            language: Language code
            
        Returns:
            Feedback dictionary
        """
        # Simple character-level comparison
        if not expected_text or not spoken_text:
            return {
                'accuracy': 0,
                'feedback': 'Could not process audio',
                'expected': expected_text,
                'spoken': spoken_text
            }
        
        # Calculate similarity
        expected_chars = list(expected_text.lower().replace(' ', ''))
        spoken_chars = list(spoken_text.lower().replace(' ', ''))
        
        matches = sum(1 for e, s in zip(expected_chars, spoken_chars) if e == s)
        max_len = max(len(expected_chars), len(spoken_chars))
        
        accuracy = (matches / max_len * 100) if max_len > 0 else 0
        
        # Generate feedback
        if accuracy >= 90:
            feedback = "✅ Excellent pronunciation!"
        elif accuracy >= 70:
            feedback = "👍 Good! Keep practicing."
        elif accuracy >= 50:
            feedback = "📝 Getting there. Try again."
        else:
            feedback = "💪 Keep practicing! Listen carefully and repeat."
        
        return {
            'accuracy': round(accuracy, 1),
            'feedback': feedback,
            'expected': expected_text,
            'spoken': spoken_text,
            'matches': matches,
            'total': max_len
        }
    
    @staticmethod
    def get_speech_recognition_html() -> str:
        """
        Get HTML/JavaScript for browser-based speech recognition
        
        Returns:
            HTML string with speech recognition code
        """
        return """
        <script>
        // Web Speech API for Speech-to-Text
        if ('webkitSpeechRecognition' in window) {
            const recognition = new webkitSpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            
            window.startRecording = function(language = 'ja-JP') {
                recognition.lang = language;
                recognition.start();
                
                recognition.onresult = function(event) {
                    const transcript = event.results[0][0].transcript;
                    window.parent.postMessage({
                        type: 'speech_result',
                        transcript: transcript,
                        confidence: event.results[0][0].confidence
                    }, '*');
                };
                
                recognition.onerror = function(event) {
                    window.parent.postMessage({
                        type: 'speech_error',
                        error: event.error
                    }, '*');
                };
            };
        } else {
            console.log('Speech recognition not supported');
        }
        </script>
        """
    
    def transcribe_audio(self, audio_file_path: str, language: str = 'ja') -> Optional[str]:
        """
        Transcribe audio file to text using Groq Whisper
        
        Args:
            audio_file_path: Path to audio file (.mp3, .wav, .m4a, .webm)
            language: Language code ('ja', 'en', 'es', 'zh', 'ko', etc.)
            
        Returns:
            Transcribed text or None if error
        """
        if not self.stt_engine or not self.groq_client:
            logging.error("Groq Whisper not available for transcription")
            return None
        
        try:
            # Check if file exists
            if not os.path.exists(audio_file_path):
                logging.error(f"Audio file not found: {audio_file_path}")
                return None
            
            # Open and transcribe audio file
            with open(audio_file_path, 'rb') as audio_file:
                transcription = self.groq_client.audio.transcriptions.create(
                    file=(os.path.basename(audio_file_path), audio_file.read()),
                    model=self.WHISPER_MODEL,  # whisper-large-v3-turbo
                    language=language,  # Optional: helps accuracy
                    response_format="text"  # Get plain text
                )
                
                logging.info(f"✓ Transcribed audio: {len(transcription)} characters")
                return transcription
                
        except Exception as e:
            logging.error(f"Whisper transcription error: {e}")
            return None


# Singleton instance
_audio_service = None

def get_audio_service() -> AudioPracticeService:
    """Get singleton audio service instance"""
    global _audio_service
    if _audio_service is None:
        _audio_service = AudioPracticeService()
    return _audio_service


if __name__ == "__main__":
    # Test
    service = get_audio_service()
    
    if service.is_available():
        print("✓ Audio service available")
        
        # Test TTS
        print("\nTesting TTS...")
        audio = service.text_to_speech("こんにちは", "ja")
        if audio:
            print(f"✓ Generated audio ({len(audio)} bytes)")
        
        # Test pronunciation feedback
        print("\nTesting pronunciation feedback...")
        feedback = service.get_pronunciation_feedback(
            "こんにちは",
            "こんにちわ"
        )
        print(f"Accuracy: {feedback['accuracy']}%")
        print(f"Feedback: {feedback['feedback']}")
    else:
        print("✗ Audio service not available")
        print("Install with: pip install gTTS")
