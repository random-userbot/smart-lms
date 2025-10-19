
from flask import Flask, request, render_template, redirect, url_for, session, flash
import csv, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'super_secret_key'

LOG_FILE = 'clickstream_logs.csv'
CREDENTIALS_FILE = 'student_login.csv'

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['StudentID', 'Subject', 'Lecture', 'EventType', 'Timestamp', 'Details'])

if not os.path.exists(CREDENTIALS_FILE):
    with open(CREDENTIALS_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['StudentID', 'Password'])

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
        return redirect(url_for('index'))
    else:
        flash('Invalid ID or password')
        return redirect(url_for('login_page'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        student_id = request.form.get('studentId')
        password = request.form.get('password')
        credentials = load_credentials()
        if student_id in credentials:
            flash('Student ID already exists.')
            return redirect(url_for('login_page'))
        with open(CREDENTIALS_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([student_id, password])
        flash('Registration successful. Please login.')
        return redirect(url_for('login_page'))
    return render_template('register.html')

@app.route('/index')
def index():
    if 'student_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('index_clickstream.html')

@app.route('/log', methods=['POST'])
def log_event():
    data = request.json
    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            data.get('studentId', 'unknown'),
            data.get('subjectId', 'unknown'),
            data.get('lectureId', 'unknown'),
            data.get('eventType', 'unknown'),
            data.get('timestamp', datetime.utcnow().isoformat()),
            data.get('additionalInfo', '')
        ])
    return '', 204

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

if __name__ == '__main__':
    app.run(debug=True)
