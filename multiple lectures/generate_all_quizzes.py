"""
Generate Comprehensive Quizzes for All YouTube Lectures
Uses transcripts and context-aware model selection
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.storage import get_storage
from services.japanese_ai_service import get_japanese_ai_service
from services.transcript_extractor import get_transcript_from_url, get_transcript_summary
from bulk_quiz_generator import detect_optimal_model
import uuid
from datetime import datetime
import re

def extract_comprehensive_context(lecture):
    """Extract all available context from lecture"""
    context_parts = []
    
    # Title
    if lecture.get('title'):
        context_parts.append(f"Title: {lecture['title']}")
    
    # Description
    if lecture.get('description'):
        desc = re.sub(r'<[^>]+>', '', lecture['description'])
        context_parts.append(f"Description: {desc[:800]}")
    
    # Playlist info
    if lecture.get('playlist_title'):
        context_parts.append(f"Course: {lecture['playlist_title']}")
    
    # Try to get FULL transcript for better questions
    video_path = lecture.get('video_path', '')
    if 'youtube.com' in video_path or 'youtu.be' in video_path:
        try:
            print("    📝 Extracting full video transcript...")
            transcript = get_transcript_from_url(video_path)
            
            if transcript:
                # Use up to 3000 chars for comprehensive coverage
                transcript_summary = get_transcript_summary(transcript, 3000)
                context_parts.append(f"\n=== VIDEO CONTENT ===\n{transcript_summary}")
                print(f"    ✓ Got {len(transcript)} chars of transcript")
            else:
                print("    ⚠️  No transcript available")
        except Exception as e:
            print(f"    ⚠️  Transcript error: {str(e)[:50]}")
    
    return "\n".join(context_parts)


def generate_comprehensive_quiz(lecture, ai_service, course_name=""):
    """Generate a comprehensive quiz covering the lecture"""
    
    # Get full context
    context = extract_comprehensive_context(lecture)
    
    # Always use gpt-oss-120b for reliable JSON output
    optimal_model = 'openai/gpt-oss-120b'
    ai_service.model = optimal_model
    
    print(f"    🧠 Using {optimal_model}")
    
    # Determine appropriate number of questions based on content length
    content_length = len(context)
    if content_length > 2000:
        question_count = 10  # Comprehensive quiz for long content
    elif content_length > 1000:
        question_count = 7   # Good coverage for medium content
    else:
        question_count = 5   # Basic quiz for short content
    
    # Create enhanced prompt
    topic = lecture.get('title', 'this lecture')
    
    enhanced_prompt = f"""Create a comprehensive quiz for: {topic}

LECTURE CONTENT:
{context}

Generate {question_count} multiple-choice questions that:
1. Cover KEY CONCEPTS from the video content
2. Test understanding of MAIN IDEAS
3. Include practical application questions
4. Range from basic recall to deeper understanding
5. Use actual information from the transcript

Focus on the most important takeaways from this lecture."""
    
    print(f"    📊 Generating {question_count} questions...")
    
    try:
        quiz_data = ai_service.generate_japanese_quiz(
            topic=enhanced_prompt,
            difficulty="mixed",  # Mix of easy and challenging
            question_count=question_count,
            quiz_type="mixed"
        )
        
        if quiz_data:
            # Add metadata
            quiz_data['quiz_id'] = f"quiz_{uuid.uuid4().hex[:8]}"
            quiz_data['lecture_id'] = lecture['lecture_id']
            quiz_data['auto_generated'] = True
            quiz_data['generated_at'] = datetime.now().isoformat()
            quiz_data['used_transcript'] = 'youtube.com' in lecture.get('video_path', '')
            quiz_data['question_count'] = question_count
            
            return quiz_data
    except Exception as e:
        print(f"    ❌ Error: {str(e)[:100]}")
        return None


def generate_all_quizzes():
    """Generate quizzes for all lectures without quizzes"""
    
    print("=" * 80)
    print("🎓 GENERATING COMPREHENSIVE QUIZZES FOR ALL YOUTUBE LECTURES")
    print("=" * 80)
    
    storage = get_storage()
    ai_service = get_japanese_ai_service(provider="groq")
    
    if not ai_service.is_available():
        print("❌ AI service not available. Check your Groq API key.")
        return
    
    # Get all lectures
    lectures = storage.get_all_lectures()
    
    # Filter YouTube lectures without quizzes
    youtube_lectures = [
        l for l in lectures 
        if ('youtube.com' in l.get('video_path', '') or 'youtu.be' in l.get('video_path', ''))
        and not l.get('quizzes', [])
    ]
    
    print(f"\n📚 Found {len(lectures)} total lectures")
    print(f"🎥 YouTube lectures: {len([l for l in lectures if 'youtube.com' in l.get('video_path', '')])}")
    print(f"✅ With quizzes: {len([l for l in lectures if l.get('quizzes', [])])}")
    print(f"❌ Without quizzes: {len(youtube_lectures)}")
    print(f"\n🚀 Will generate quizzes for {len(youtube_lectures)} lectures\n")
    
    if not youtube_lectures:
        print("✅ All lectures already have quizzes!")
        return
    
    success_count = 0
    failed_count = 0
    
    for i, lecture in enumerate(youtube_lectures, 1):
        title = lecture.get('title', 'Untitled')
        lecture_id = lecture['lecture_id']
        
        print(f"\n[{i}/{len(youtube_lectures)}] 📖 {title}")
        print(f"    ID: {lecture_id}")
        
        # Get course name if available
        course_name = ""
        if lecture.get('course_id'):
            course = storage.get_course(lecture['course_id'])
            course_name = course.get('name', '') if course else ''
        
        # Generate quiz
        quiz_data = generate_comprehensive_quiz(lecture, ai_service, course_name)
        
        if quiz_data:
            # Save to lecture
            quizzes = lecture.get('quizzes', [])
            quizzes.append(quiz_data)
            
            success = storage.update_lecture(lecture_id, {'quizzes': quizzes})
            
            if success:
                print(f"    ✅ Quiz saved ({quiz_data['question_count']} questions)")
                success_count += 1
            else:
                print(f"    ❌ Failed to save quiz")
                failed_count += 1
        else:
            print(f"    ❌ Quiz generation failed")
            failed_count += 1
    
    print("\n" + "=" * 80)
    print("📊 RESULTS")
    print("=" * 80)
    print(f"✅ Success: {success_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"📈 Total processed: {success_count + failed_count}")
    print("\n🎉 Quiz generation complete!")
    print("=" * 80)


if __name__ == "__main__":
    generate_all_quizzes()
