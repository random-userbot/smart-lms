"""
YouTube Transcript Extractor
Extracts transcripts/subtitles from YouTube videos for quiz generation
"""

import logging
from typing import Optional, Dict

# Try different transcript libraries
TRANSCRIPT_AVAILABLE = False

try:
    from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
    TRANSCRIPT_AVAILABLE = True
    logging.info("✓ YouTube Transcript API available")
except ImportError:
    logging.info("youtube-transcript-api not installed. Install with: pip install youtube-transcript-api")


def extract_youtube_id(url: str) -> Optional[str]:
    """Extract video ID from YouTube URL"""
    import re
    
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/v/([a-zA-Z0-9_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    # If it's just the ID
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
        return url
    
    return None


def get_youtube_transcript(video_id: str, languages=['ja', 'en', 'en-US', 'auto']) -> Optional[str]:
    """
    Get transcript/subtitles from YouTube video
    
    Args:
        video_id: YouTube video ID
        languages: List of language codes to try
        
    Returns:
        Transcript text or None if not available
    """
    if not TRANSCRIPT_AVAILABLE:
        logging.warning("YouTube Transcript API not available")
        return None
    
    try:
        # Create API instance
        api = YouTubeTranscriptApi()
        
        # Try to fetch transcript
        # fetch() returns a FetchedTranscript object with .snippets attribute
        transcript = api.fetch(video_id, languages=languages)
        
        # Get the text from all snippets
        full_transcript = " ".join([snippet.text for snippet in transcript.snippets])
        
        # Clean up transcript
        full_transcript = full_transcript.replace('\n', ' ')
        full_transcript = ' '.join(full_transcript.split())  # Remove extra whitespace
        
        logging.info(f"✓ Retrieved transcript: {len(full_transcript)} characters")
        return full_transcript
        
    except NoTranscriptFound as e:
        logging.warning(f"No transcript found for video {video_id}: {str(e)[:100]}")
        return None
    except TranscriptsDisabled:
        logging.info(f"Transcripts disabled for video {video_id}")
        return None
    except Exception as e:
        logging.error(f"Error getting transcript for {video_id}: {str(e)[:150]}")
        return None


def get_transcript_from_url(youtube_url: str) -> Optional[str]:
    """
    Get transcript from YouTube URL
    
    Args:
        youtube_url: YouTube video URL
        
    Returns:
        Transcript text or None
    """
    video_id = extract_youtube_id(youtube_url)
    
    if not video_id:
        logging.error(f"Could not extract video ID from URL: {youtube_url}")
        return None
    
    return get_youtube_transcript(video_id)


def get_transcript_summary(transcript: str, max_length: int = 1000) -> str:
    """
    Get a summary of the transcript for context
    
    Args:
        transcript: Full transcript text
        max_length: Maximum characters to return
        
    Returns:
        Truncated transcript
    """
    if not transcript:
        return ""
    
    if len(transcript) <= max_length:
        return transcript
    
    # Try to cut at sentence boundary
    truncated = transcript[:max_length]
    last_period = truncated.rfind('.')
    
    if last_period > max_length * 0.8:  # If period is in last 20%
        return truncated[:last_period + 1]
    
    return truncated + "..."


if __name__ == "__main__":
    # Test
    print("Testing YouTube Transcript Extractor...")
    
    if TRANSCRIPT_AVAILABLE:
        # Test with a sample video
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        print(f"\nTesting with URL: {test_url}")
        
        video_id = extract_youtube_id(test_url)
        print(f"Extracted video ID: {video_id}")
        
        if video_id:
            transcript = get_youtube_transcript(video_id)
            if transcript:
                print(f"\n✓ Transcript found ({len(transcript)} characters)")
                print(f"Preview: {transcript[:200]}...")
            else:
                print("✗ No transcript available")
    else:
        print("✗ YouTube Transcript API not installed")
        print("Install with: pip install youtube-transcript-api")
