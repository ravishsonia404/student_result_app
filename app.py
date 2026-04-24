from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3
import io

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)
app.secret_key = 'secret123'

# -------------------------------
# Database
# -------------------------------
def init_db():
    conn = sqlite3.connect('database.db')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            roll TEXT UNIQUE,
            maths INTEGER,
            science INTEGER,
            english INTEGER,
            accountancy INTEGER,
            economics INTEGER,
            business INTEGER,
            it INTEGER,
            hindi INTEGER,
            sanskrit INTEGER,
            total INTEGER,
            percentage REAL,
            grade TEXT
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')

    conn.close()

init_db()

# -------------------------------
# Default User
# -------------------------------
def create_user():
    conn = sqlite3.connect('database.db')
    try:
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', '1234'))
        conn.commit()
    except:
        pass
    conn.close()

create_user()

# -------------------------------
# Grade
# -------------------------------
def calculate_grade(p):
    if p >= 90: return "A+"
    elif p >= 75: return "A"
    elif p >= 60: return "B"
    else: return "C"

# -------------------------------
# Login
# -------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p))
        user = cur.fetchone()
        conn.close()

        if user:
            session['user'] = u
            return redirect('/')
        else:
            return "Invalid Login ❌"

    return render_template('login.html')

# -------------------------------
# Logout
# -------------------------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

# -------------------------------
# Add / Update Student
# -------------------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        name = request.form['name']
        roll = request.form['roll']

        # Optional subjects
        maths = int(request.form.get('maths') or 0)
        science = int(request.form.get('science') or 0)
        english = int(request.form.get('english') or 0)
        accountancy = int(request.form.get('accountancy') or 0)
        economics = int(request.form.get('economics') or 0)
        business = int(request.form.get('business') or 0)
        it = int(request.form.get('it') or 0)
        hindi = int(request.form.get('hindi') or 0)
        sanskrit = int(request.form.get('sanskrit') or 0)

        marks_list = [
            maths, science, english,
            accountancy, economics, business, it,
            hindi, sanskrit
        ]

        valid_subjects = [m for m in marks_list if m > 0]

        if len(valid_subjects) > 0:
            total = sum(valid_subjects)
            percentage = total / len(valid_subjects)
        else:
            total = 0
            percentage = 0

        grade = calculate_grade(percentage)

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        cur.execute("SELECT id FROM students WHERE roll=?", (roll,))
        existing = cur.fetchone()

        if existing:
            conn.execute('''
                UPDATE students
                SET name=?, maths=?, science=?, english=?, accountancy=?, economics=?, business=?, it=?, hindi=?, sanskrit=?, total=?, percentage=?, grade=?
                WHERE roll=?
            ''', (name, maths, science, english, accountancy, economics, business, it, hindi, sanskrit, total, percentage, grade, roll))
        else:
            conn.execute('''
                INSERT INTO students
                (name, roll, maths, science, english, accountancy, economics, business, it, hindi, sanskrit, total, percentage, grade)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, roll, maths, science, english, accountancy, economics, business, it, hindi, sanskrit, total, percentage, grade))

        conn.commit()
        conn.close()

        return render_template('result.html', name=name, total=total, percentage=percentage, grade=grade)

    return render_template('index.html')

# -------------------------------
# Students List
# -------------------------------
@app.route('/students', methods=['GET', 'POST'])
def students():
    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    search = request.form.get('search')

    if search:
        cur.execute("SELECT * FROM students WHERE roll LIKE ?", ('%' + search + '%',))
    else:
        cur.execute("SELECT * FROM students ORDER BY id DESC")

    data = cur.fetchall()
    conn.close()

    return render_template('students.html', students=data)

# -------------------------------
# Delete
# -------------------------------
@app.route('/delete/<int:id>')
def delete(id):
    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    conn.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/students')

# -------------------------------
# Edit
# -------------------------------
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        roll = request.form['roll']

        maths = int(request.form.get('maths') or 0)
        science = int(request.form.get('science') or 0)
        english = int(request.form.get('english') or 0)
        accountancy = int(request.form.get('accountancy') or 0)
        economics = int(request.form.get('economics') or 0)
        business = int(request.form.get('business') or 0)
        it = int(request.form.get('it') or 0)
        hindi = int(request.form.get('hindi') or 0)
        sanskrit = int(request.form.get('sanskrit') or 0)

        marks_list = [
            maths, science, english,
            accountancy, economics, business, it,
            hindi, sanskrit
        ]

        valid_subjects = [m for m in marks_list if m > 0]

        if len(valid_subjects) > 0:
            total = sum(valid_subjects)
            percentage = total / len(valid_subjects)
        else:
            total = 0
            percentage = 0

        grade = calculate_grade(percentage)

        conn.execute('''
            UPDATE students
            SET name=?, roll=?, maths=?, science=?, english=?, accountancy=?, economics=?, business=?, it=?, hindi=?, sanskrit=?, total=?, percentage=?, grade=?
            WHERE id=?
        ''', (name, roll, maths, science, english, accountancy, economics, business, it, hindi, sanskrit, total, percentage, grade, id))

        conn.commit()
        conn.close()
        return redirect('/students')

    cur.execute("SELECT * FROM students WHERE id=?", (id,))
    student = cur.fetchone()
    conn.close()

    return render_template('edit.html', student=student)

# -------------------------------
# PDF Download
# -------------------------------
@app.route('/download/<int:id>')
def download_pdf(id):
    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM students WHERE id=?", (id,))
    s = cur.fetchone()
    conn.close()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph("Student Result", styles['Title']))
    content.append(Spacer(1, 10))

    content.append(Paragraph(f"Name: {s[1]}", styles['Normal']))
    content.append(Paragraph(f"Roll: {s[2]}", styles['Normal']))
    content.append(Spacer(1, 10))

    subjects = [
        ("Maths", s[3]), ("Science", s[4]), ("English", s[5]),
        ("Accountancy", s[6]), ("Economics", s[7]), ("Business", s[8]),
        ("IT", s[9]), ("Hindi", s[10]), ("Sanskrit", s[11])
    ]

    for sub, marks in subjects:
        if marks > 0:
            content.append(Paragraph(f"{sub}: {marks}", styles['Normal']))

    content.append(Spacer(1, 10))
    content.append(Paragraph(f"Total: {s[12]}", styles['Normal']))
    content.append(Paragraph(f"Percentage: {round(s[13],2)}%", styles['Normal']))
    content.append(Paragraph(f"Grade: {s[14]}", styles['Normal']))

    doc.build(content)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True,
                     download_name=f"result_{s[1]}.pdf",
                     mimetype='application/pdf')

# -------------------------------
# Run
# -------------------------------
if __name__ == '__main__':
    app.run(debug=True)
