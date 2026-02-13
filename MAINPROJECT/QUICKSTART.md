# Quick Start Guide - database.db

## Step 1: Initialize Database

```powershell
cd "C:\Users\DIVYA PRIYA\Documents\MAINPROJECT"
python init_database.py
```

Expected output:

```
✅ All tables created successfully!
✅ DATABASE READY!
```

## Step 2: Install Dependencies

```powershell
pip install -r requirements.txt
```

## Step 3: Start Flask App

```powershell
python app.py
```

You should see:

```
 * Running on http://127.0.0.1:5000
```

## Step 4: Test Registration

1. Open browser: http://localhost:5000
2. Click "Register as Student"
3. Fill in the form:
   - Full Name: Test User
   - Username: testuser
   - Email: test@example.com
   - Password: password123
4. Click "Register"
5. Watch the **Flask terminal** for:
   ```
   [DB] Commit successful for query
   [DB] Last row ID: 1
   Student registered: testuser with ID 1
   ```

## Step 5: Test Login

1. Click "Login"
2. Username: testuser
3. Password: password123
4. Watch terminal for:
   ```
   Login attempt for user: testuser, found: True
   Login successful for user: testuser
   ```
5. You should be redirected to Student Dashboard

## Troubleshooting

### "Invalid username or password"

Check the **Flask terminal** for logs:

- `found: True` = user exists in DB
- `found: False` = user NOT in DB (registration failed)
- `[DB ERROR]` = database error

### Registration fails silently

The error is shown on the registration page. Read it carefully:

- `UNIQUE constraint failed: users.username` = username already taken
- `UNIQUE constraint failed: users.email` = email already registered
- Other errors will tell you the issue

### Database file not created

Run:

```powershell
python init_database.py
```

This creates a fresh `database.db` with all 6 tables.

## Database Location

`database.db` is created in your project root:

```
C:\Users\DIVYA PRIYA\Documents\MAINPROJECT\database.db
```

You can inspect it with any SQLite viewer or in Python:

```powershell
python - <<'PY'
import sqlite3
conn = sqlite3.connect("database.db")
cur = conn.cursor()
cur.execute("SELECT id, username, user_type FROM users")
print(cur.fetchall())
conn.close()
PY
```

## Key Environment Variables (for MySQL, if needed later)

If you want to switch to MySQL/XAMPP later:

```powershell
setx USE_MYSQL "1"
setx DB_USER "root"
setx DB_PASSWORD ""
setx DB_HOST "127.0.0.1"
setx DB_PORT "3306"
setx DB_NAME "college_recruitment"
```

For now, **USE_MYSQL is NOT set**, so app.py uses SQLite (database.db).
