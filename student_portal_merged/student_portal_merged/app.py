from flask import Flask, render_template, request, jsonify
import sqlite3
from pathlib import Path

app = Flask(__name__)
DB_PATH = Path(__file__).with_name("students.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_no TEXT NOT NULL UNIQUE,
            department TEXT,
            year INTEGER,
            email TEXT
        )
    """)
    return conn


def student_dict(row):
    return dict(row)


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/api/students")
def list_students():
    keyword = request.args.get("q", "").strip()
    conn = get_connection()
    try:
        if keyword:
            rows = conn.execute("""
                SELECT id, name, roll_no, department, year, email
                FROM students
                WHERE name LIKE ? OR roll_no LIKE ? OR department LIKE ?
                   OR email LIKE ?
                ORDER BY id DESC
            """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")).fetchall()
        else:
            rows = conn.execute("""
                SELECT id, name, roll_no, department, year, email
                FROM students ORDER BY id DESC
            """).fetchall()
        return jsonify([student_dict(row) for row in rows])
    finally:
        conn.close()


@app.post("/api/students")
def add_student():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    roll_no = str(data.get("roll_no", "")).strip()
    department = str(data.get("department", "")).strip()
    year_raw = str(data.get("year", "")).strip()
    email = str(data.get("email", "")).strip()

    if not name or not roll_no:
        return jsonify(error="Name and roll number are required."), 400
    if year_raw:
        try:
            year = int(year_raw)
            if year not in range(1, 5):
                raise ValueError
        except ValueError:
            return jsonify(error="Year must be a number from 1 to 4."), 400
    else:
        year = None

    conn = get_connection()
    try:
        cur = conn.execute("""
            INSERT INTO students (name, roll_no, department, year, email)
            VALUES (?, ?, ?, ?, ?)
        """, (name, roll_no, department, year, email))
        conn.commit()
        row = conn.execute("""
            SELECT id, name, roll_no, department, year, email
            FROM students WHERE id = ?
        """, (cur.lastrowid,)).fetchone()
        return jsonify(student_dict(row)), 201
    except sqlite3.IntegrityError:
        return jsonify(error="That roll number already exists. Please use a unique roll number."), 409
    finally:
        conn.close()


@app.put("/api/students/<int:student_id>")
def update_student(student_id):
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    roll_no = str(data.get("roll_no", "")).strip()
    department = str(data.get("department", "")).strip()
    year_raw = str(data.get("year", "")).strip()
    email = str(data.get("email", "")).strip()

    if not name or not roll_no:
        return jsonify(error="Name and roll number are required."), 400
    if year_raw:
        try:
            year = int(year_raw)
            if year not in range(1, 5):
                raise ValueError
        except ValueError:
            return jsonify(error="Year must be a number from 1 to 4."), 400
    else:
        year = None

    conn = get_connection()
    try:
        cur = conn.execute("""
            UPDATE students
            SET name = ?, roll_no = ?, department = ?, year = ?, email = ?
            WHERE id = ?
        """, (name, roll_no, department, year, email, student_id))
        if cur.rowcount == 0:
            conn.rollback()
            return jsonify(error="Student record not found."), 404
        conn.commit()
        row = conn.execute("""
            SELECT id, name, roll_no, department, year, email
            FROM students WHERE id = ?
        """, (student_id,)).fetchone()
        return jsonify(student_dict(row))
    except sqlite3.IntegrityError:
        return jsonify(error="That roll number belongs to another student."), 409
    finally:
        conn.close()


@app.delete("/api/students/<int:student_id>")
def delete_student(student_id):
    conn = get_connection()
    try:
        cur = conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()
        if cur.rowcount == 0:
            return jsonify(error="Student record not found."), 404
        return jsonify(message="Student deleted.")
    finally:
        conn.close()


if __name__ == "__main__":
    # For local development only. Do not expose Flask's debug server publicly.
    get_connection().close()
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
