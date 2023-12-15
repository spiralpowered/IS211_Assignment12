import sqlite3
from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from functools import wraps
from werkzeug.exceptions import abort

app = Flask(__name__)
DATABASE = 'hw12.db'
app.secret_key = 'key'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def logged_in(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if session.get('logged_in'):
            return f(*args, **kwargs)
        else:
            return redirect("/")
    return decorated_func

def load_db():
    cur = get_db().cursor()
    cur.execute("DROP TABLE IF EXISTS student_results;")
    cur.execute("DROP TABLE IF EXISTS student;")
    cur.execute("DROP TABLE IF EXISTS quizzes;")
    cur.execute("DROP TABLE IF EXISTS user;")

    cur.execute("""
    CREATE TABLE user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    );
    """)
    cur.execute("INSERT INTO user(username, password) VALUES('admin', 'password')")

    cur.execute("""
    CREATE TABLE student(
        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_fname VARCHAR(30) NOT NULL,
        student_lname VARCHAR(30) NOT NULL
    );
    """)

    cur.execute("INSERT INTO student(student_fname, student_lname) VALUES('John', 'Smith');")

    cur.execute("""
    CREATE TABLE quizzes(
        quiz_id INTEGER PRIMARY KEY AUTOINCREMENT,
        quiz_subject VARCHAR(50) NOT NULL,
        question_num INTEGER NOT NULL,
        quiz_date DATE NOT NULL
    );
    """)

    cur.execute("INSERT INTO quizzes(quiz_subject, question_num, quiz_date) VALUES('Python Basics', 5, '2015-02-05');")

    cur.execute("""
    CREATE TABLE student_results(
        student_id INTEGER NOT NULL,
        quiz_id INTEGER NOT NULL,
        score INTEGER NOT NULL,
        PRIMARY KEY (student_id, quiz_id),
        FOREIGN KEY(student_id) REFERENCES student(student_id) ON DELETE CASCADE,
        FOREIGN KEY(quiz_id) REFERENCES quizzes(quiz_id) ON DELETE CASCADE
    );
    """)
    cur.execute("INSERT INTO student_results VALUES(1, 1, 85);")

    get_db().commit()

def get_student_results(id, check_author=True):
    results = get_db().execute(
        'SELECT * FROM student_results WHERE student_id = ?',
        (id,)
    ).fetchone()

    if results is None:
        abort(404, "Student ID: {0} not entered.".format(id))

    return results

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=('GET', 'POST'))
def login():
    session['logged_in'] = False
    load_db()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        passw = db.execute(
            'SELECT * FROM user WHERE password = ?', (password,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif passw is None:
            error = 'Incorrect password.'

        if error is None:
            id = user[0]
            session.clear()
            session['logged_in'] = True
            return redirect('/dashboard')

        flash(error)

    return render_template('auth/login.html')

@app.route('/dashboard')
@logged_in
def dashboard():
    db = get_db()
    student_list = db.execute("SELECT * FROM student").fetchall()
    quiz_list = db.execute("SELECT * FROM quizzes").fetchall()
    return render_template('dashboard.html', student_list=student_list, quiz_list=quiz_list)


@app.route('/student/add', methods=('GET', 'POST'))
@logged_in
def student_add():
    error = None
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        if firstname is None:
            error = 'First name is required.'
        elif lastname is None:
            error = 'Last name is required'
        else:
            db = get_db()
            db.execute(
                "INSERT INTO student(student_fname, student_lname) VALUES(?, ?);",
                (firstname, lastname))
            db.commit()
            return redirect('/dashboard')

        flash(error)

    return render_template('add/student_add.html')

@app.route('/quiz/add', methods=('GET', 'POST'))
@logged_in
def quiz_add():
    error = None
    if request.method == 'POST':
        subject = request.form['subject']
        questions = request.form['questions']
        date = request.form['date']
        if subject is None:
            error = 'Subject is required.'
        elif questions is None:
            error = 'Number of questions are required.'
        elif date is None:
            error = 'Date is required.'
        else:
            db = get_db()
            db.execute(
                "INSERT INTO quizzes(quiz_subject, question_num, quiz_date) VALUES(?, ?, ?);",
                (subject, questions, date))
            db.commit()
            return redirect('/dashboard')

        flash(error)

    return render_template('add/quiz_add.html')

@app.route('/results/add', methods=('GET', 'POST'))
@logged_in
def result_add():
    error = None
    db = get_db()
    students = db.execute("SELECT student_id FROM student").fetchall()
    quizzes = db.execute("SELECT quiz_id FROM quizzes").fetchall()
    if request.method == 'POST':
        student = request.form['student']
        quiz = request.form['quiz']
        score = request.form['score']
        if (int(student),) not in students:
            error = 'Student not found.'
        elif (int(quiz),) not in quizzes:
            error = 'Quiz not found.'
        elif int(score) < 0 or int(score) > 100:
            error = 'Invalid score.'
        else:
            db = get_db()
            db.execute("INSERT INTO student_results VALUES(?, ?, ?)",
                       (student, quiz, score))
            db.commit()
            return redirect('/dashboard')

        flash(error)

    return render_template('results/add_results.html')

@app.route('/student/<int:id>', methods=('GET', 'POST'))
@logged_in
def student_view(id):
    student = get_student_results(id)
    db = get_db()
    results = db.execute("SELECT quiz_id, score FROM student_results WHERE student_id = ?",
                         (id,)).fetchall()

    return render_template('results/student_results.html', id=id, results=results)

if __name__ == '__main__':
    app.run(debug=True)