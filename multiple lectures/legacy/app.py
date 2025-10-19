
from flask import Flask, request, render_template, redirect, url_for, session, flash
import csv, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, 'events1.csv')
CREDENTIALS_FILE = os.path.join(BASE_DIR, 'student_login.csv')
ASSIGNMENT_FILE = os.path.join(BASE_DIR, 'assignment_status.csv')

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['StudentID', 'EventType', 'Timestamp', 'AdditionalInfo'])

if not os.path.exists(CREDENTIALS_FILE):
    with open(CREDENTIALS_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['StudentID', 'Password'])

if not os.path.exists(ASSIGNMENT_FILE):
    with open(ASSIGNMENT_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['StudentID', 'Subject', 'Lecture', 'Submitted', 'Timestamp', 'DocLink'])

def load_credentials():
    credentials = {}
    with open(CREDENTIALS_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            credentials[row['StudentID']] = row['Password']
    return credentials

@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    student_id = request.form.get('studentId')
    password = request.form.get('password')
    credentials = load_credentials()

    if student_id in credentials and credentials[student_id] == password:
        session['student_id'] = student_id
        log_event(student_id, 'Login', f'Login Time: {datetime.utcnow()}')
        return redirect(url_for('index'))
    else:
        flash('❌ Invalid ID or password')
        return redirect(url_for('login_page'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        student_id = request.form.get('studentId')
        password = request.form.get('password')
        credentials = load_credentials()
        if student_id in credentials:
            flash('⚠️ Student ID already exists. Please login.')
            return redirect(url_for('login_page'))

        with open(CREDENTIALS_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([student_id, password])
        flash('✅ Registration successful! Please login.')
        return redirect(url_for('login_page'))

    return render_template('register.html')

@app.route('/index')
def index():
    if 'student_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('index_clickstream.html', student_id=session['student_id'])

@app.route('/log', methods=['POST'])
def log_event_api():
    data = request.json
    log_event(
        student_id=data.get('studentId'),
        event=data.get('eventType'),
        info=f"Subject: {data.get('subjectId')}, Lecture: {data.get('lectureId')}, Info: {data.get('additionalInfo', '')}",
        timestamp=data.get('timestamp')
    )
    return '', 204

def log_event(student_id, event, info="", timestamp=None):
    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            student_id,
            event,
            timestamp if timestamp else datetime.utcnow().isoformat(),
            info
        ])

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'student_id' not in session:
        return redirect(url_for('login_page'))

    if request.method == 'POST':
        student_id = session['student_id']
        subject_id = request.form.get('subjectId')
        lecture_id = request.form.get('lectureId')
        score = request.form.get('score')
        duration = request.form.get('duration')

        log_event(student_id, 'QuizCompleted',
                  f'Subject: {subject_id}, Lecture: {lecture_id}, Score: {score}, Duration: {duration}')
        return f"<h3>✅ Thank you, {student_id}. Your score for {subject_id} - {lecture_id}: {score}</h3>"

    return render_template('quiz.html')

@app.route('/assignment', methods=['GET', 'POST'])
def assignment():
    if 'student_id' not in session:
        return redirect(url_for('login_page'))

    if request.method == 'POST':
        student_id = session['student_id']
        subject_id = request.form.get('subjectId')
        lecture_id = request.form.get('lectureId')
        doc_link = request.form.get('docLink')

        with open(ASSIGNMENT_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                student_id,
                subject_id,
                lecture_id,
                1 if doc_link else 0,
                datetime.utcnow().isoformat(),
                doc_link
            ])
        log_event(student_id, 'AssignmentSubmitted',
                  f'Subject: {subject_id}, Lecture: {lecture_id}, Document: {doc_link}')
        return f"<h3>✅ Thank you, {student_id}. Assignment submitted.</h3>"

    return render_template('assignment.html')

@app.route('/logout')
def logout():
    if 'student_id' in session:
        log_event(session['student_id'], 'Logout', f'Logout Time: {datetime.utcnow()}')
        session.clear()
    return redirect(url_for('login_page'))

if __name__ == '__main__':
    app.run(debug=True)
