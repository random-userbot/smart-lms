import json
import re

# Load lectures
with open('storage/lectures.json', 'r') as f:
    lectures = json.load(f)

# Clean descriptions
for lec_id, lecture in lectures.items():
    desc = lecture.get('description', '')
    if desc:
        # Remove any HTML tags
        desc_clean = re.sub(r'<[^>]+>', '', desc)
        # Remove HTML entities
        desc_clean = desc_clean.replace('&lt;', '').replace('&gt;', '').replace('&amp;', '')
        # Remove extra whitespace
        desc_clean = ' '.join(desc_clean.split())
        lectures[lec_id]['description'] = desc_clean
    else:
        lectures[lec_id]['description'] = f"Content for {lecture.get('title', 'this lecture')}"

# Save back
with open('storage/lectures.json', 'w') as f:
    json.dump(lectures, f, indent=2)

print("✅ Fixed all lecture descriptions")
