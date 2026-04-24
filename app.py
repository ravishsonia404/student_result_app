from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'secret123'   # required for login session

# -------------------------------
# Database Initialization
# -------------------------------
def init_db():
    conn = sqlite3.connect('database.db')

    # Students table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            roll TEXT UNIQUE,
            maths INTEGER,
            science INTEGER,
            english INTEGER,
            total INTEGER,
            percentage REAL,
            grade TEXT
        )
    ''')

    # Users table
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
# Create Default User
# -------------------------------
def create_user():
    conn = sqlite3.connect('database.db')
    try:
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('sonia', '8765'))
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('pavita', '7856'))
        conn.commit()
    except:
        pass
    conn.close()

create_user()

# -------------------------------
# Grade Function
# -------------------------------
def calculate_grade(percentage):
    if percentage >= 90:
        return "A+"
    elif percentage >= 75:
        return "A"
    elif percentage >= 60:
        return "B"
    else:
        return "C"

# -------------------------------
# Login Route
# -------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        print(username, password)

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user'] = username
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
# Home Page (Add / Update Student)
# -------------------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        name = request.form['name']
        roll = request.form['roll']
        maths = int(request.form['maths'])
        science = int(request.form['science'])
        english = int(request.form['english'])

        total = maths + science + english
        percentage = total / 3
        grade = calculate_grade(percentage)

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM students WHERE roll=?", (roll,))
        existing = cursor.fetchone()

        if existing:
            conn.execute('''
                UPDATE students
                SET name=?, maths=?, science=?, english=?, total=?, percentage=?, grade=?
                WHERE roll=?
            ''', (name, maths, science, english, total, percentage, grade, roll))
        else:
            conn.execute('''
                INSERT INTO students
                (name, roll, maths, science, english, total, percentage, grade)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, roll, maths, science, english, total, percentage, grade))

        conn.commit()
        conn.close()

        return render_template('result.html', name=name, total=total, percentage=percentage, grade=grade)

    return render_template('index.html')

# -------------------------------
# View + Search Students
# -------------------------------
@app.route('/students', methods=['GET', 'POST'])
def students():
    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    search = request.form.get('search')

    if search:
        cursor.execute("SELECT * FROM students WHERE roll LIKE ?", ('%' + search + '%',))
    else:
        cursor.execute("SELECT * FROM students ORDER BY id DESC")

    data = cursor.fetchall()
    conn.close()

    return render_template('students.html', students=data)

# -------------------------------
# Delete Student
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
# Edit Student
# -------------------------------
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        roll = request.form['roll']
        maths = int(request.form['maths'])
        science = int(request.form['science'])
        english = int(request.form['english'])

        total = maths + science + english
        percentage = total / 3
        grade = calculate_grade(percentage)

        conn.execute('''
            UPDATE students
            SET name=?, roll=?, maths=?, science=?, english=?, total=?, percentage=?, grade=?
            WHERE id=?
        ''', (name, roll, maths, science, english, total, percentage, grade, id))

        conn.commit()
        conn.close()

        return redirect('/students')

    cursor.execute("SELECT * FROM students WHERE id=?", (id,))
    student = cursor.fetchone()
    conn.close()

    return render_template('edit.html', student=student)

# -------------------------------
# Run App
# -------------------------------
if __name__ == '__main__':
    app.run(debug=True)