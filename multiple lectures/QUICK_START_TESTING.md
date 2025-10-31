# Quick Start Guide - User & Resource Management

## 🚀 Start the Application

```bash
cd "c:\Users\revan\Downloads\multiple lectures\multiple lectures"
streamlit run app/streamlit_app.py
```

---

## 👤 Test Admin Features

### 1. Login as Admin
```
Username: admin
Password: admin123
```

### 2. Manage Users
- Click **"👥 Manage Users"** in sidebar
- Try these actions:
  - ✅ Click **"➕ Add New User"** to create a new user
  - ✅ Click **"✏️ Edit"** on any user to modify details
  - ✅ Click **"🔄 Reset Password"** to change a user's password
  - ✅ Use the search bar to find users
  - ✅ Filter by role (Students, Teachers, Admins)

### 3. Manage Courses
- Click **"📚 Manage Courses"** in sidebar
- Try these actions:
  - ✅ Click **"➕ Create Course"** to add a new course
  - ✅ Click **"✏️ Edit"** to modify course details
  - ✅ Click **"👥 Manage Students"** to enroll/remove students
  - ✅ Click **"📄 View Materials"** to see course content

### 4. View All Resources
- Click **"📁 Resources"** in sidebar
- Browse resources by:
  - **By Course**: Organized view
  - **All Resources**: Table format
  - **Recent**: Latest uploads

---

## 👨‍🏫 Test Teacher Features

### 1. Login as Teacher
```
Username: dr_ramesh
Password: teacher123
```

### 2. View Your Courses
- Click **"📚 My Courses"** in sidebar
- See all courses assigned to you
- Manage student enrollments

### 3. Upload Content
- Click **"📤 Upload Content"** in sidebar
- **Upload Lecture Video**:
  - Select your course
  - Enter lecture title and description
  - Upload video file (MP4, AVI, MOV, MKV)
  - Set duration
  - Click **"📤 Upload Lecture"**

- **Upload Course Materials**:
  - Select your course
  - Enter material title
  - Choose material type (Lecture Notes, Slides, etc.)
  - Upload file (PDF, PPTX, DOCX, ZIP)
  - Optionally link to specific lecture
  - Click **"📤 Upload Material"**

### 4. View Resources
- Click **"📁 Resources"** in sidebar
- Download videos and materials
- See upload statistics

---

## 🎓 Test Student Features

### 1. Login as Student
```
Username: demo_student
Password: student123
```

### 2. View Enrolled Courses
- Click **"📚 My Courses"** in sidebar
- See courses you're enrolled in
- No courses? Ask admin to enroll you!

### 3. Access Resources
- Click **"📁 Resources"** in sidebar
- Browse course materials:
  - Watch lecture videos
  - Download lecture notes
  - Download slides and documents
- Use search to find specific resources

### 4. Watch Lectures
- Click **"🎥 Lectures"** in sidebar
- Select a course
- Watch lectures with engagement tracking

---

## 🧪 Complete Test Workflow

### Step 1: Admin Creates Everything
1. Login as **admin**
2. Go to **"👥 Manage Users"**
3. Create a new teacher account
4. Create some student accounts
5. Go to **"📚 Manage Courses"**
6. Create a new course
7. Assign the teacher
8. Enroll the students

### Step 2: Teacher Uploads Content
1. Logout and login as **dr_ramesh**
2. Go to **"📤 Upload Content"**
3. Upload a lecture video
4. Upload course materials (PDFs, slides)
5. Check **"📁 Resources"** to verify uploads

### Step 3: Student Accesses Resources
1. Logout and login as **demo_student**
2. Go to **"📁 Resources"**
3. Find your enrolled course
4. Download lecture video
5. Download course materials

---

## ✅ Features to Test

### User Management (Admin)
- [ ] Add new user (student, teacher, admin)
- [ ] Edit user details
- [ ] Reset user password
- [ ] Activate/Deactivate user
- [ ] Delete user
- [ ] Search users
- [ ] Filter by role

### Course Management (Admin & Teacher)
- [ ] Create new course
- [ ] Edit course details
- [ ] Add students to course
- [ ] Remove students from course
- [ ] View course materials
- [ ] Archive/Activate course

### Resource Management (All)
- [ ] Browse resources by course
- [ ] View all resources table
- [ ] Download lecture videos
- [ ] Download course materials
- [ ] Search resources
- [ ] Filter by type
- [ ] View recent uploads

### Upload System (Teacher)
- [ ] Upload lecture video
- [ ] Upload course materials
- [ ] Link materials to lectures
- [ ] Verify uploads appear in resources

---

## 📊 Expected Results

### After Admin Setup:
✅ New users appear in "Manage Users" list  
✅ New courses appear in "Manage Courses" list  
✅ Students enrolled in courses  
✅ Statistics updated (user counts, course counts)  

### After Teacher Upload:
✅ Lecture appears in course  
✅ Video file saved to `storage/courses/{course_id}/lectures/`  
✅ Materials saved to `storage/courses/{course_id}/materials/`  
✅ Resources visible in "📁 Resources" page  
✅ Download buttons functional  

### After Student Access:
✅ Student can see enrolled courses  
✅ Student can browse resources  
✅ Student can download files  
✅ Engagement tracking active during lectures  

---

## 🐛 Common Issues & Solutions

### Issue: "No courses available"
**Solution**: Admin needs to create courses and enroll you

### Issue: "Cannot download file"
**Solution**: Check if file path exists in `storage/courses/` directory

### Issue: "Upload failed"
**Solution**: 
- Check file size (large files may take time)
- Ensure storage directory has write permissions
- Verify file format is supported

### Issue: "User already exists"
**Solution**: Username must be unique. Try a different username

### Issue: "Access denied"
**Solution**: Check you're logged in with correct role (admin/teacher/student)

---

## 💡 Tips for Testing

1. **Use Different Browsers**: Test different roles in different browser tabs
2. **Check File System**: Verify files are saved in `storage/` directory
3. **Check Console**: Look for any error messages in terminal
4. **Test Permissions**: Each role should only see their allowed features
5. **Test Search**: Make sure search works across all pages

---

## 📝 Test Checklist

### Admin Tests:
- [ ] Create 3 new users (1 teacher, 2 students)
- [ ] Create 2 courses
- [ ] Assign teacher to courses
- [ ] Enroll students in courses
- [ ] Edit a user's details
- [ ] Reset a user's password
- [ ] View all resources

### Teacher Tests:
- [ ] View assigned courses
- [ ] Upload 1 video lecture
- [ ] Upload 2 course materials (PDF, PPTX)
- [ ] Link materials to lecture
- [ ] Add a student to course
- [ ] Remove a student from course
- [ ] Download own uploaded files

### Student Tests:
- [ ] View enrolled courses
- [ ] Browse resources by course
- [ ] Download 1 video
- [ ] Download 1 material
- [ ] Search for specific material
- [ ] View recent uploads

---

## 🎉 Success Indicators

✅ **All Users Created** - Visible in Manage Users  
✅ **All Courses Created** - Visible in Manage Courses  
✅ **Students Enrolled** - Visible in course enrollment list  
✅ **Content Uploaded** - Files in storage directory  
✅ **Downloads Working** - Files can be downloaded  
✅ **Search Functional** - Results show correctly  
✅ **No Errors** - No red error messages  

---

## 🚀 Ready to Use!

Your Smart LMS platform now has:
- ✅ Complete user management
- ✅ Comprehensive course management
- ✅ Intuitive resource browser
- ✅ File upload/download system
- ✅ Role-based access control

**Everything is ready for production use!** 🎓
