# 🚀 Quick Start Guide - Advanced Features

## For Teachers

### 1. View Student Activity Tracking
1. Login as Teacher
2. Click **"📊 Tracking"** in the sidebar
3. Select a course (click on the card)
4. View enrolled students
5. Click on any student to see detailed activity logs
6. Use filters to narrow down activities
7. Export to CSV for analysis

### 2. Check Your Teaching Score
1. Login as Teacher
2. Click **"📊 Teaching Score"** in the sidebar
3. Select a course from the dropdown
4. View your overall score and grade
5. Explore component breakdowns
6. Read detailed explanations
7. Review actionable recommendations

### 3. Use the AI Chatbot
1. In the Teaching Score page, go to **"🤖 AI Insights"** tab
2. Select a course
3. Choose a quick question:
   - **"📊 Explain My Score"** - Get comprehensive explanation
   - **"💡 Get Improvement Plan"** - Receive 30-day action plan
   - **"📈 Compare Benchmarks"** - See how you compare
4. Or type your own question
5. Chat history is maintained for context

### 4. Create Manual Quizzes
1. Go to **"📤 Upload Content"**
2. Click **"📝 Create Quiz"** tab
3. Select course and lecture
4. Enter quiz details
5. Add questions (multiple choice or true/false)
6. Submit to create quiz
7. Students can now take the quiz

---

## For Students

### 1. View Your Activity
1. Login as Student
2. Click **"📊 My Activity"** in the sidebar
3. Explore tabs:
   - **Overview** - Statistics and breakdown
   - **By Course** - Course-specific activities
   - **Engagement** - Engagement metrics
   - **Timeline** - Chronological activity log
4. Export your data to CSV

### 2. Check Progress
All your activities are automatically tracked:
- Lecture watching
- Quiz attempts
- Material downloads
- Notes reading
- AI tool usage

### 3. Give Feedback
Your feedback is anonymized - teachers only see that you gave feedback, not the content.

---

## For Admins

### 1. Monitor System-Wide Activity
1. Login as Admin
2. Click **"📊 Activity Tracking"** in sidebar
3. View all courses and students
4. Access complete tracking data
5. Export system-wide reports

### 2. Review Teaching Scores
1. Click **"📊 Teaching Scores"**
2. View all teachers' performance
3. Compare across courses
4. Generate reports

---

## 🔧 Configuration

### Set Up Groq API (for AI Chatbot)

#### Option 1: Config File
Edit `config.yaml`:
```yaml
api_keys:
  groq: "gsk_your_api_key_here"
```

#### Option 2: Environment Variable
```bash
# Windows PowerShell
$env:GROQ_API_KEY="gsk_your_api_key_here"

# Linux/Mac
export GROQ_API_KEY="gsk_your_api_key_here"
```

#### Get Free API Key
1. Visit https://console.groq.com/keys
2. Sign up (free)
3. Generate API key
4. Copy and paste into config

---

## 📊 Key Features at a Glance

| Feature | Students | Teachers | Admins |
|---------|----------|----------|--------|
| View Own Activity | ✅ | ✅ | ✅ |
| Track Students | ❌ | ✅ (own courses) | ✅ (all) |
| Teaching Scores | ❌ | ✅ | ✅ |
| AI Chatbot | ❌ | ✅ | ✅ |
| Create Quizzes | ❌ | ✅ | ✅ |
| Export Data | ✅ (own) | ✅ (course) | ✅ (all) |

---

## 🎯 Best Practices

### For Teachers
1. **Check tracking regularly** - Monitor student engagement weekly
2. **Review teaching scores monthly** - Track improvement trends
3. **Use AI chatbot** - Get insights and improvement suggestions
4. **Export data** - Keep records for course evaluation
5. **Act on recommendations** - Implement suggested improvements

### For Students
1. **Review your activity** - Understand your learning patterns
2. **Stay consistent** - Regular engagement improves outcomes
3. **Use AI tools** - Leverage available resources
4. **Complete lectures** - Finish what you start
5. **Take quizzes seriously** - They reflect your understanding

### For Admins
1. **Monitor trends** - Look for system-wide patterns
2. **Support teachers** - Share insights and best practices
3. **Ensure privacy** - Protect student data
4. **Regular reports** - Export data for institutional reporting
5. **System maintenance** - Archive old data periodically

---

## ❓ FAQ

### Q: Is automatic quiz generation disabled?
**A:** Yes, teachers now manually create all quizzes for better control.

### Q: Can students see other students' activities?
**A:** No, students can only see their own activity data.

### Q: Is student feedback visible to teachers?
**A:** No, feedback content is anonymized. Teachers only see that feedback was given.

### Q: How accurate are teaching scores?
**A:** Scores are data-driven using multiple metrics. More student activity = more accurate scores.

### Q: Is the AI chatbot free?
**A:** Yes, Groq API offers a generous free tier. API key required.

### Q: Can I export all data?
**A:** Yes, CSV export is available. Students can export their own data, teachers can export course data, admins can export all data.

### Q: How often are scores updated?
**A:** Scores are calculated on-demand when you view the analytics dashboard.

### Q: What if I don't have any activities yet?
**A:** Scores require minimum data. Start tracking activities, and scores will improve in accuracy over time.

---

## 🆘 Need Help?

### Common Issues

**Problem**: AI Chatbot shows "not available"  
**Solution**: Add GROQ_API_KEY to config.yaml

**Problem**: No activities showing  
**Solution**: Activities auto-track - start using the system

**Problem**: Score shows 0  
**Solution**: Need student activities and data - give it time

**Problem**: Can't see tracking page  
**Solution**: Check your role - only teachers/admins have access

---

## 📞 Support

- Check `ADVANCED_FEATURES_GUIDE.md` for detailed documentation
- Review error messages carefully
- Verify API keys are configured
- Ensure proper role permissions

---

**Quick Start Complete!** 🎉

Start exploring the new features now!
