DROP TABLE IF EXISTS student_results;
DROP TABLE IF EXISTS student;
DROP TABLE IF EXISTS quizzes;
DROP TABLE IF EXISTS user;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

INSERT INTO user(username, password) VALUES('admin', 'password')

CREATE TABLE student(
	student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_fname VARCHAR(30) NOT NULL,
    student_lname VARCHAR(30) NOT NULL
);

INSERT INTO student(student_fname, student_lname) VALUES('John', 'Smith');

CREATE TABLE quizzes(
	quiz_id INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_subject VARCHAR(50) NOT NULL,
    question_num INTEGER NOT NULL,
    quiz_date DATE UNIQUE NOT NULL
);

INSERT INTO quizzes(quiz_subject, question_num, quiz_date) VALUES('Python Basics', 5, '2015-02-05');

CREATE TABLE student_results(
	student_id INTEGER NOT NULL,
    quiz_id INTEGER NOT NULL,
    score INTEGER NOT NULL,
    PRIMARY KEY (student_id, quiz_id),
    FOREIGN KEY(student_id) REFERENCES student(student_id) ON DELETE CASCADE,
    FOREIGN KEY(quiz_id) REFERENCES quizzes(quiz_id) ON DELETE CASCADE
);
INSERT INTO student_results VALUES(1, 1, 85);