from flask import Flask, render_template, request, redirect, session
import sqlite3

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
# Default user
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

        # Optional subjects (safe conversion)
        maths = int(request.form.get('maths') or 0)
        science = int(request.form.get('science') or 0)
        english = int(request.form.get('english') or 0)
        accountancy = int(request.form.get('accountancy') or 0)
        economics = int(request.form.get('economics') or 0)
        business = int(request.form.get('business') or 0)
        it = int(request.form.get('it') or 0)

        marks_list = [maths, science, english, accountancy, economics, business, it]
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
                SET name=?, maths=?, science=?, english=?, accountancy=?, economics=?, business=?, it=?, total=?, percentage=?, grade=?
                WHERE roll=?
            ''', (name, maths, science, english, accountancy, economics, business, it, total, percentage, grade, roll))
        else:
            conn.execute('''
                INSERT INTO students
                (name, roll, maths, science, english, accountancy, economics, business, it, total, percentage, grade)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, roll, maths, science, english, accountancy, economics, business, it, total, percentage, grade))

        conn.commit()
        conn.close()

        return render_template('result.html', name=name, total=total, percentage=percentage, grade=grade)

    return render_template('index.html')

# -------------------------------
# Students list + search
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

        marks_list = [maths, science, english, accountancy, economics, business, it]
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
            SET name=?, roll=?, maths=?, science=?, english=?, accountancy=?, economics=?, business=?, it=?, total=?, percentage=?, grade=?
            WHERE id=?
        ''', (name, roll, maths, science, english, accountancy, economics, business, it, total, percentage, grade, id))

        conn.commit()
        conn.close()
        return redirect('/students')

    cur.execute("SELECT * FROM students WHERE id=?", (id,))
    student = cur.fetchone()
    conn.close()

    return render_template('edit.html', student=student)

# -------------------------------
# Run
# -------------------------------
if __name__ == '__main__':
    app.run(debug=True)
