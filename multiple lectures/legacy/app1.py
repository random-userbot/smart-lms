
from flask import Flask, render_template, request, redirect, url_for, session, flash
import os, csv
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'super_secret_key'

LOG_FILE = 'events.csv'
CREDENTIALS_FILE = 'student_login.csv'

# Ensure files exist
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['StudentID', 'EventType', 'Timestamp', 'AdditionalInfo'])

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
        flash('Invalid ID or Password')
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
    return render_template('index.html')

@app.route('/lecture/<subject>/<lecture>')
def play_lecture(subject, lecture):
    if 'student_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('lecture_template.html', subject=subject, lecture=lecture)

@app.route('/assignment')
def assignment():
    return "<h3>Submit your assignment here.</h3>"

@app.route('/quiz')
def quiz():
    return "<h3>This is a sample quiz interface. Implement quiz form here.</h3>"

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

@app.route('/log', methods=['POST'])
def log_event():
    data = request.json
    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            data.get('studentId'),
            data.get('eventType'),
            data.get('timestamp'),
            f"Subject: {data.get('subjectId')}, Lecture: {data.get('lectureId')}, Info: {data.get('additionalInfo', '')}"
        ])
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)
