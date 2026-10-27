from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "karan_water_saving_super_secret_key_2010"

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            video_url TEXT,
            content TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            exam_topic TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            password_hash TEXT NOT NULL
        )
    ''')
    cursor.execute('SELECT COUNT(*) FROM admin')
    if cursor.fetchone()[0] == 0:
        default_pass = generate_password_hash('2010')
        cursor.execute('INSERT INTO admin (password_hash) VALUES (?)', (default_pass,))
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM topics ORDER BY id DESC')
    topics = cursor.fetchall()
    conn.close()
    return render_template('index.html', topics=topics)

@app.route('/login', methods=['POST'])
def login():
    entered_pass = request.form.get('password')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT password_hash FROM admin WHERE id=1')
    row = cursor.fetchone()
    conn.close()
    if row and check_password_hash(row[0], entered_pass):
        session['owner_logged_in'] = True
        flash('Owner Mode Activated Successfully!', 'success')
    else:
        flash('Incorrect Password!', 'error')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('owner_logged_in', None)
    flash('Logged out from Owner mode.', 'info')
    return redirect(url_for('index'))

@app.route('/add_topic', methods=['POST'])
def add_topic():
    if not session.get('owner_logged_in'):
        return redirect(url_for('index'))
    title = request.form.get('title')
    description = request.form.get('description')
    video_url = request.form.get('video_url')
    content = request.form.get('content')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO topics (title, description, video_url, content) VALUES (?, ?, ?, ?)',
                   (title, description, video_url, content))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/edit_topic/<int:id>', methods=['POST'])
def edit_topic(id):
    if not session.get('owner_logged_in'):
        return redirect(url_for('index'))
    title = request.form.get('title')
    description = request.form.get('description')
    video_url = request.form.get('video_url')
    content = request.form.get('content')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE topics SET title=?, description=?, video_url=?, content=? WHERE id=?',
                   (title, description, video_url, content, id))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/delete_topic/<int:id>')
def delete_topic(id):
    if not session.get('owner_logged_in'):
        return redirect(url_for('index'))
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM topics WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/register_exam', methods=['POST'])
def register_exam():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    exam_topic = request.form.get('exam_topic')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO registrations (name, email, phone, exam_topic) VALUES (?, ?, ?, ?)',
                   (name, email, phone, exam_topic))
    conn.commit()
    conn.close()
    flash('Exam Registration Successful! Best of Luck.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
