"""
Bulk Quiz Generator
Automatically generates AI quizzes for all lectures based on their content
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.japanese_ai_service import get_japanese_ai_service
from services.storage import get_storage
import uuid
from datetime import datetime
import json
import re


def extract_lecture_context(lecture):
    """
    Extract relevant context from lecture for quiz generation
    Includes video transcript if available
    
    Args:
        lecture: Lecture dictionary
        
    Returns:
        String with lecture context
    """
    context_parts = []
    
    # Title
    if lecture.get('title'):
        context_parts.append(f"Lecture Title: {lecture['title']}")
    
    # Description
    if lecture.get('description'):
        desc = lecture['description']
        # Remove HTML tags if present
        import re
        desc = re.sub(r'<[^>]+>', '', desc)
        context_parts.append(f"Description: {desc[:500]}")  # Limit to 500 chars
    
    # YouTube video title/description might have more context
    if lecture.get('playlist_title'):
        context_parts.append(f"Playlist: {lecture['playlist_title']}")
    
    # Try to get video transcript if it's a YouTube video
    video_path = lecture.get('video_path', '')
    if 'youtube.com' in video_path or 'youtu.be' in video_path:
        try:
            from services.transcript_extractor import get_transcript_from_url, get_transcript_summary
            
            print("  📝 Extracting video transcript...")
            transcript = get_transcript_from_url(video_path)
            
            if transcript:
                # Use first 1500 chars of transcript for context
                transcript_summary = get_transcript_summary(transcript, 1500)
                context_parts.append(f"\nVideo Transcript:\n{transcript_summary}")
                print(f"  ✓ Transcript extracted ({len(transcript)} characters)")
            else:
                print("  ⚠️  No transcript available")
        except Exception as e:
            print(f"  ⚠️  Could not extract transcript: {e}")
    
    # Materials titles
    materials = lecture.get('materials', [])
    if materials:
        material_titles = [m.get('title', '') for m in materials[:3]]  # First 3
        context_parts.append(f"Materials: {', '.join(material_titles)}")
    
    return "\n".join(context_parts)


def detect_optimal_model(lecture, course_name=""):
    """
    Detect optimal Groq model based on lecture/course content
    
    Args:
        lecture: Lecture dictionary
        course_name: Optional course name
        
    Returns:
        Model name string
    """
    # Combine all text for analysis
    text_parts = [
        course_name,
        lecture.get('title', ''),
        lecture.get('description', ''),
        lecture.get('playlist_title', '')
    ]
    combined_text = ' '.join(text_parts).lower()
    
    # Language course detection
    language_keywords = ['japanese', 'chinese', 'korean', 'spanish', 'french', 
                         'german', 'language', 'asian', 'vocabulary', 'hiragana', 
                         'katakana', 'kanji', 'grammar']
    
    if any(keyword in combined_text for keyword in language_keywords):
        return 'qwen/qwen3-32b'  # Specialized for languages
    
    # Default to best reasoning model for other subjects
    return 'openai/gpt-oss-120b'


def generate_quiz_for_lecture(lecture, ai_service, difficulty="beginner", question_count=5, course_name=""):
    """
    Generate quiz for a single lecture with optimal model
    
    Args:
        lecture: Lecture dictionary
        ai_service: Japanese AI service instance
        difficulty: Quiz difficulty level
        question_count: Number of questions
        course_name: Optional course name for context
        
    Returns:
        Quiz data or None if failed
    """
    # Extract context
    context = extract_lecture_context(lecture)
    
    # Determine topic from lecture title
    topic = lecture.get('title', 'this lecture')
    
    # Add context to the topic
    full_topic = f"{topic}\n\nLecture Context:\n{context}"
    
    # Detect and set optimal model
    optimal_model = detect_optimal_model(lecture, course_name)
    ai_service.model = optimal_model
    
    model_emoji = "🌏" if optimal_model == 'qwen/qwen3-32b' else "🧠"
    print(f"  {model_emoji} Generating quiz with {optimal_model}")
    
    try:
        quiz_data = ai_service.generate_japanese_quiz(
            topic=full_topic,
            difficulty=difficulty,
            question_count=question_count,
            quiz_type="mixed"
        )
        
        if quiz_data:
            # Add lecture-specific metadata
            quiz_data['quiz_id'] = f"quiz_{uuid.uuid4().hex[:8]}"
            quiz_data['lecture_id'] = lecture['lecture_id']
            quiz_data['auto_generated'] = True
            quiz_data['generated_at'] = datetime.now().isoformat()
            
            return quiz_data
            
    except Exception as e:
        print(f"  ❌ Error generating quiz: {e}")
        return None


def bulk_generate_quizzes(course_id=None, difficulty="beginner", question_count=5, 
                          skip_existing=True, ai_provider="groq"):
    """
    Generate quizzes for all lectures in a course (or all courses)
    
    Args:
        course_id: Specific course ID or None for all courses
        difficulty: Quiz difficulty
        question_count: Questions per quiz
        skip_existing: Skip lectures that already have quizzes
        ai_provider: AI provider to use
        
    Returns:
        Dictionary with results
    """
    storage = get_storage()
    ai_service = get_japanese_ai_service(provider=ai_provider)
    
    if not ai_service.is_available():
        print("❌ AI service not available. Please configure API keys.")
        return {
            'success': False,
            'error': 'AI service not available',
            'quizzes_generated': 0
        }
    
    print(f"🤖 Starting context-aware bulk quiz generation...")
    print(f"   Provider: {ai_provider}")
    print(f"   Difficulty: {difficulty}")
    print(f"   Questions per quiz: {question_count}")
    print(f"   🧠 Auto-selecting optimal models per course")
    print()
    
    # Get course name if specific course
    course_name = ""
    if course_id:
        course = storage.get_course(course_id)
        course_name = course.get('name', '') if course else ''
    
    # Get lectures
    if course_id:
        lectures = storage.get_course_lectures(course_id)
        print(f"📚 Found {len(lectures)} lectures in course: {course_name}")
    else:
        all_lectures = storage.get_all_lectures()
        lectures = list(all_lectures.values()) if isinstance(all_lectures, dict) else all_lectures
        print(f"📚 Found {len(lectures)} lectures across all courses")
    
    results = {
        'success': True,
        'total_lectures': len(lectures),
        'quizzes_generated': 0,
        'skipped': 0,
        'failed': 0,
        'details': []
    }
    
    for i, lecture in enumerate(lectures, 1):
        lecture_id = lecture['lecture_id']
        title = lecture.get('title', 'Untitled')
        
        print(f"\n[{i}/{len(lectures)}] Processing: {title}")
        
        # Check if already has quiz
        existing_quizzes = lecture.get('quizzes', [])
        if skip_existing and existing_quizzes:
            print(f"  ⏭️  Skipping (already has {len(existing_quizzes)} quiz(es))")
            results['skipped'] += 1
            results['details'].append({
                'lecture_id': lecture_id,
                'title': title,
                'status': 'skipped',
                'reason': 'already_has_quiz'
            })
            continue
        
        # Generate quiz with optimal model
        quiz_data = generate_quiz_for_lecture(
            lecture, 
            ai_service, 
            difficulty, 
            question_count,
            course_name
        )
        
        if quiz_data:
            # Add quiz to lecture
            quizzes = lecture.get('quizzes', [])
            quizzes.append(quiz_data)
            
            # Update lecture in storage
            success = storage.update_lecture(lecture_id, {'quizzes': quizzes})
            
            if success:
                print(f"  ✅ Quiz generated: {quiz_data['title']}")
                results['quizzes_generated'] += 1
                results['details'].append({
                    'lecture_id': lecture_id,
                    'title': title,
                    'status': 'success',
                    'quiz_title': quiz_data['title'],
                    'question_count': len(quiz_data.get('questions', []))
                })
            else:
                print(f"  ❌ Failed to save quiz")
                results['failed'] += 1
                results['details'].append({
                    'lecture_id': lecture_id,
                    'title': title,
                    'status': 'failed',
                    'reason': 'save_error'
                })
        else:
            print(f"  ❌ Failed to generate quiz")
            results['failed'] += 1
            results['details'].append({
                'lecture_id': lecture_id,
                'title': title,
                'status': 'failed',
                'reason': 'generation_error'
            })
    
    # Summary
    print("\n" + "="*50)
    print("📊 BULK QUIZ GENERATION SUMMARY")
    print("="*50)
    print(f"Total lectures: {results['total_lectures']}")
    print(f"✅ Quizzes generated: {results['quizzes_generated']}")
    print(f"⏭️  Skipped: {results['skipped']}")
    print(f"❌ Failed: {results['failed']}")
    print("="*50)
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Bulk generate quizzes for lectures")
    parser.add_argument('--course', type=str, help='Course ID (optional, generates for all if not provided)')
    parser.add_argument('--difficulty', type=str, default='beginner', choices=['beginner', 'intermediate', 'advanced'])
    parser.add_argument('--questions', type=int, default=5, help='Number of questions per quiz')
    parser.add_argument('--regenerate', action='store_true', help='Regenerate quizzes even if they exist')
    parser.add_argument('--provider', type=str, default='groq', choices=['groq', 'openai', 'gemini'])
    
    args = parser.parse_args()
    
    # Run bulk generation
    results = bulk_generate_quizzes(
        course_id=args.course,
        difficulty=args.difficulty,
        question_count=args.questions,
        skip_existing=not args.regenerate,
        ai_provider=args.provider
    )
    
    # Save results to file
    output_file = f"quiz_generation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: {output_file}")
