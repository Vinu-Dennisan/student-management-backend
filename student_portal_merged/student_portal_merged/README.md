# Student Portal — merged Python + SQLite + HTML app

This project combines the browser-based Student Portal with the Python/SQLite Student Management System.

## Features
- Add student records (name, unique roll number, department, year, email)
- View and search records
- Edit and delete records
- SQLite persistence in `students.db`
- Responsive portal UI
- Duplicate roll numbers rejected
- Year validation (1–4)

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
4. Start the server:
   ```bash
   python app.py
   ```
5. Open the address printed in the terminal, usually `http://127.0.0.1:5000`.

The database file is created automatically in this folder when the app starts.

## Important
- This is a local development server, not a production deployment. Do not expose Flask's debug server to the public internet.
- The registration form in this merged version stores student details; it does not create user accounts or store passwords.
- Back up `students.db` to preserve records.
