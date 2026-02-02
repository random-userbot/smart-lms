"""
Test Transcript Extraction
Check if transcripts are being extracted properly
"""

from services.storage import get_storage
from services.transcript_extractor import get_transcript_from_url

print("=" * 80)
print("TESTING TRANSCRIPT EXTRACTION")
print("=" * 80)

storage = get_storage()
lectures = storage.get_all_lectures()

# Get first 5 YouTube lectures
youtube_lectures = [l for l in lectures if 'youtube.com' in l.get('video_path', '') or 'youtu.be' in l.get('video_path', '')][:5]

print(f"\nTesting {len(youtube_lectures)} YouTube lectures:\n")

success_count = 0
fail_count = 0

for i, lecture in enumerate(youtube_lectures, 1):
    title = lecture.get('title', 'No title')
    url = lecture.get('video_path', '')
    
    print(f"{i}. {title[:60]}")
    print(f"   URL: {url[:80]}")
    print(f"   Testing... ", end='', flush=True)
    
    try:
        transcript = get_transcript_from_url(url)
        
        if transcript:
            print(f"✅ Got {len(transcript)} characters")
            print(f"   Preview: {transcript[:100]}...")
            success_count += 1
        else:
            print("❌ No transcript available")
            fail_count += 1
    except Exception as e:
        print(f"❌ Error: {str(e)[:80]}")
        fail_count += 1
    
    print()

print("=" * 80)
print(f"Results: ✅ {success_count} successful, ❌ {fail_count} failed")
print("=" * 80)

if fail_count > 0:
    print("\n⚠️  Some transcripts failed. Possible reasons:")
    print("   1. Video has no captions/subtitles")
    print("   2. Captions are disabled by uploader")
    print("   3. Video is private or deleted")
    print("   4. Invalid YouTube URL")
