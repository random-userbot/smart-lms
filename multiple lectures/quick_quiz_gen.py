"""
Quick Quiz Generator - Generates quizzes 5 at a time with better error handling
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.storage import get_storage
from services.japanese_ai_service import get_japanese_ai_service
from services.transcript_extractor import get_transcript_from_url, get_transcript_summary
import uuid
from datetime import datetime
import json
import time
import re

def clean_json_response(response_text):
    """Remove markdown code blocks and extra whitespace from AI response"""
    # Remove ```json and ``` markers
    cleaned = re.sub(r'```json\s*', '', response_text)
    cleaned = re.sub(r'```\s*$', '', cleaned)
    cleaned = cleaned.strip()
    return cleaned

def generate_quiz_batch(storage, ai_service, start_idx=0, batch_size=5):
    """Generate quizzes for a small batch of lectures"""
    
    # Get all lectures directly
    all_lectures_raw = storage.get_all_lectures()
    
    # Get courses for course names
    courses = storage.get_all_courses()
    course_map = {cid: c.get('title', '') for cid, c in courses.items()}
    
    # Filter lectures without quizzes
    all_lectures = []
    for lecture in all_lectures_raw:
        if not lecture.get('quiz'):
            course_name = course_map.get(lecture.get('course_id', ''), '')
            all_lectures.append({
                'lecture': lecture,
                'course_name': course_name
            })
    
    # Get batch
    batch = all_lectures[start_idx:start_idx + batch_size]
    
    print(f"\n{'='*80}")
    print(f"📚 GENERATING QUIZZES FOR LECTURES {start_idx+1}-{start_idx+len(batch)}")
    print(f"{'='*80}\n")
    
    success_count = 0
    failed_count = 0
    
    for idx, item in enumerate(batch, start=start_idx+1):
        lecture = item['lecture']
        course_name = item['course_name']
        
        print(f"[{idx}] 📖 {lecture['title'][:60]}")
        print(f"    ID: {lecture['lecture_id']}")
        
        try:
            # Get transcript
            video_path = lecture.get('video_path', '')
            transcript = ""
            
            if 'youtube.com' in video_path or 'youtu.be' in video_path:
                try:
                    print("    📝 Getting transcript...")
                    full_transcript = get_transcript_from_url(video_path)
                    if full_transcript:
                        transcript = get_transcript_summary(full_transcript, 2000)
                        print(f"    ✓ Got {len(transcript)} chars")
                    else:
                        print("    ⚠️  No transcript")
                except Exception as e:
                    print(f"    ⚠️  Transcript error: {str(e)[:50]}")
            
            # Build context
            context = f"""Title: {lecture['title']}
Course: {course_name}"""
            
            if lecture.get('description'):
                desc = re.sub(r'<[^>]+>', '', lecture['description'])
                context += f"\nDescription: {desc[:400]}"
            
            if transcript:
                context += f"\n\nVideo Content:\n{transcript}"
            
            # Generate quiz
            ai_service.model = 'openai/gpt-oss-120b'
            
            # Determine question count
            if len(context) > 1500:
                question_count = 7
            elif len(context) > 800:
                question_count = 5
            else:
                question_count = 3
            
            prompt = f"""Create a quiz about: {lecture['title']}

Content:
{context}

Generate {question_count} multiple-choice questions that test key concepts from this content.
IMPORTANT: Return ONLY valid JSON without markdown code blocks."""
            
            print(f"    🧠 Generating {question_count} questions...")
            
            # Call AI
            quiz_data = ai_service.generate_japanese_quiz(
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
                
                # Save quiz to lecture
                storage.update_lecture(lecture['lecture_id'], {'quiz': quiz_data})
                print(f"    ✅ Saved quiz with {len(quiz_data.get('questions', []))} questions")
                success_count += 1
            else:
                print("    ❌ Failed - no quiz data returned")
                failed_count += 1
                
        except Exception as e:
            print(f"    ❌ Error: {str(e)[:100]}")
            failed_count += 1
        
        # Rate limiting
        time.sleep(2)
    
    print(f"\n{'='*80}")
    print(f"📊 BATCH RESULTS")
    print(f"{'='*80}")
    print(f"✅ Success: {success_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"{'='*80}\n")
    
    return success_count, failed_count, len(all_lectures)


if __name__ == "__main__":
    storage = get_storage()
    ai_service = get_japanese_ai_service()
    
    # Get starting index
    start_idx = int(input("Start at lecture number (1-100): ")) - 1
    batch_size = int(input("How many quizzes to generate (recommended: 5-10): "))
    
    success, failed, total = generate_quiz_batch(storage, ai_service, start_idx, batch_size)
    
    print(f"\n🎉 Batch complete!")
    print(f"Progress: {start_idx + batch_size}/{total} lectures processed")
    print(f"To continue, run again with start index: {start_idx + batch_size + 1}")
