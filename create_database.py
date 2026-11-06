import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATABASE_DIR = BASE_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "quiz.db"


def create_database():
	DATABASE_DIR.mkdir(parents=True, exist_ok=True)

	with sqlite3.connect(DATABASE_PATH) as connection:
		connection.execute("PRAGMA foreign_keys = ON")

		connection.executescript("""
		CREATE TABLE IF NOT EXISTS users (
			user_id INTEGER PRIMARY KEY,
			full_name TEXT NOT NULL,
			role TEXT NOT NULL
				CHECK (role IN ('admin', 'teacher', 'student')),
			created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
		);

		CREATE TABLE IF NOT EXISTS classes (
			class_id INTEGER PRIMARY KEY AUTOINCREMENT,
			class_name TEXT NOT NULL UNIQUE
		);

		CREATE TABLE IF NOT EXISTS class_members (
			user_id INTEGER NOT NULL,
			class_id INTEGER NOT NULL,
			joined_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

			PRIMARY KEY (user_id, class_id),

			FOREIGN KEY (user_id)
				REFERENCES users(user_id)
				ON DELETE CASCADE,

			FOREIGN KEY (class_id)
				REFERENCES classes(class_id)
				ON DELETE CASCADE
		);

		CREATE TABLE IF NOT EXISTS join_requests (
			request_id INTEGER PRIMARY KEY AUTOINCREMENT,
			user_id INTEGER,
			requester_name TEXT NOT NULL,
			class_id INTEGER NOT NULL,

			status TEXT NOT NULL DEFAULT 'pending'
				CHECK (status IN ('pending', 'approved', 'rejected')),

			requested_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
			reviewed_at TEXT,

			FOREIGN KEY (user_id)
				REFERENCES users(user_id)
				ON DELETE SET NULL,

			FOREIGN KEY (class_id)
				REFERENCES classes(class_id)
				ON DELETE RESTRICT
		);

		CREATE TABLE IF NOT EXISTS join_requests_become_teacher (
			request_id INTEGER PRIMARY KEY AUTOINCREMENT,
			user_id INTEGER,
			requester_name TEXT NOT NULL,
			class_id INTEGER NOT NULL,

			status TEXT NOT NULL DEFAULT 'pending'
				CHECK (status IN ('pending', 'approved', 'rejected')),

			requested_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
			reviewed_at TEXT,

			FOREIGN KEY (user_id)
				REFERENCES users(user_id)
				ON DELETE SET NULL,

			FOREIGN KEY (class_id)
				REFERENCES classes(class_id)
				ON DELETE RESTRICT
		);

		CREATE TABLE IF NOT EXISTS teacher_classes (
			teacher_id INTEGER NOT NULL,
			class_id INTEGER NOT NULL,
			assigned_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

			PRIMARY KEY (teacher_id, class_id),

			FOREIGN KEY (teacher_id)
				REFERENCES users(user_id)
				ON DELETE CASCADE,

			FOREIGN KEY (class_id)
				REFERENCES classes(class_id)
				ON DELETE CASCADE
		);

		CREATE TABLE IF NOT EXISTS quizzes (
			quiz_id INTEGER PRIMARY KEY AUTOINCREMENT,
			class_id INTEGER NOT NULL,
			teacher_id INTEGER,
			title TEXT NOT NULL,
			created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

			is_published INTEGER NOT NULL DEFAULT 0
				CHECK (is_published IN (0, 1)),

			FOREIGN KEY (class_id)
				REFERENCES classes(class_id)
				ON DELETE RESTRICT,

			FOREIGN KEY (teacher_id)
				REFERENCES users(user_id)
				ON DELETE SET NULL
		);

		CREATE TABLE IF NOT EXISTS questions (
			question_id INTEGER PRIMARY KEY AUTOINCREMENT,
			quiz_id INTEGER NOT NULL,
			question_text TEXT NOT NULL,

			option_a TEXT NOT NULL,
			option_b TEXT NOT NULL,
			option_c TEXT NOT NULL,
			option_d TEXT NOT NULL,

			correct_option TEXT NOT NULL
				CHECK (correct_option IN ('A', 'B', 'C', 'D')),

			position INTEGER NOT NULL DEFAULT 1
				CHECK (position > 0),

			FOREIGN KEY (quiz_id)
				REFERENCES quizzes(quiz_id)
				ON DELETE CASCADE,

			UNIQUE (quiz_id, position)
		);

		CREATE TABLE IF NOT EXISTS quiz_attempts (
			attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,
			user_id INTEGER,
			student_name TEXT NOT NULL,
			quiz_id INTEGER NOT NULL,

			started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
			finished_at TEXT,

			score REAL
				CHECK (score IS NULL OR score >= 0),

			status TEXT NOT NULL DEFAULT 'in_progress'
				CHECK (status IN ('in_progress', 'completed', 'cancelled')),

			FOREIGN KEY (user_id)
				REFERENCES users(user_id)
				ON DELETE SET NULL,

			FOREIGN KEY (quiz_id)
				REFERENCES quizzes(quiz_id)
				ON DELETE RESTRICT
		);

		CREATE TABLE IF NOT EXISTS student_answers (
			answer_id INTEGER PRIMARY KEY AUTOINCREMENT,
			attempt_id INTEGER NOT NULL,
			user_id INTEGER,
			student_name TEXT NOT NULL,
			question_id INTEGER NOT NULL,

			selected_option TEXT NOT NULL
				CHECK (selected_option IN ('A', 'B', 'C', 'D')),

			is_correct INTEGER NOT NULL
				CHECK (is_correct IN (0, 1)),

			answered_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

			FOREIGN KEY (attempt_id)
				REFERENCES quiz_attempts(attempt_id)
				ON DELETE CASCADE,

			FOREIGN KEY (user_id)
				REFERENCES users(user_id)
				ON DELETE SET NULL,

			FOREIGN KEY (question_id)
				REFERENCES questions(question_id)
				ON DELETE RESTRICT,

			UNIQUE (attempt_id, question_id)
		);

		CREATE UNIQUE INDEX IF NOT EXISTS unique_pending_join_request
		ON join_requests (user_id, class_id)
		WHERE status = 'pending' AND user_id IS NOT NULL;
		""")

		# ایجاد شش کلاس اولیه
		connection.executemany(
			"INSERT OR IGNORE INTO classes (class_id, class_name) VALUES (?, ?)",
			[(i, f"کلاس {i}") for i in range(1, 7)]
		)

		connection.commit()

	print(f"Database created successfully: {DATABASE_PATH}")


if __name__ == "__main__":
	create_database()