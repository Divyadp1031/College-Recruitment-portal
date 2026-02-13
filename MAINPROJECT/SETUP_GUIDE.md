# College Recruitment Portal - Quick Start

## Issues Fixed

✅ Added debug logging to registration and login routes
✅ Improved error handling in `db_query()` to show actual error messages
✅ Registration now prints when users are successfully saved

## Setup & Test

### 1. Using SQLite (default, local testing)

```powershell
cd "C:\Users\DIVYA PRIYA\Documents\MAINPROJECT"

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

Visit: http://localhost:5000

**Register → Check console for "Student registered" log → Login**

### 2. Using MySQL/XAMPP (production-ready)

```powershell
# In phpMyAdmin or MySQL shell:
CREATE DATABASE college_recruitment CHARACTER SET utf8mb4;
CREATE USER 'portal_user'@'localhost' IDENTIFIED BY 'StrongPasswordHere';
GRANT ALL PRIVILEGES ON college_recruitment.* TO 'portal_user'@'localhost';
FLUSH PRIVILEGES;

# Set environment variables (PowerShell)
setx USE_MYSQL "1"
setx DB_USER "portal_user"
setx DB_PASSWORD "StrongPasswordHere"
setx DB_HOST "127.0.0.1"
setx DB_PORT "3306"
setx DB_NAME "college_recruitment"

# Restart terminal, then run:
python app.py
```

### 3. Debug Database Issues

```powershell
python test_db.py
```

This script will:

- Check if database.db exists
- List all tables
- Show users table schema
- Display registered users

## Key Routes

| Route                | Method    | Purpose                            |
| -------------------- | --------- | ---------------------------------- |
| `/`                  | GET       | Home page                          |
| `/student-register`  | GET, POST | Student registration               |
| `/company-register`  | GET, POST | Company registration               |
| `/login`             | GET, POST | Login (both user types)            |
| `/dashboard-student` | GET       | Student dashboard (requires login) |
| `/dashboard-company` | GET       | Company dashboard (requires login) |
| `/post-job`          | GET, POST | Post a job (company only)          |
| `/job-listings`      | GET       | Browse jobs (student only)         |
| `/filter-candidates` | GET       | Search candidates (company only)   |

## Troubleshooting

### "Invalid username or password" always shows

1. Check **test_db.py** output — does your user appear in the users table?
2. Check Flask console for logs like:
   - `"Student registered: [username] with ID X"` — user was saved ✅
   - `"Login query error: ..."` — database read failed ❌
   - `"Login attempt for user: [username], found: False"` — user not in DB ❌

### Registration error appears

The actual error is now shown! Examples:

- `"UNIQUE constraint failed: users.username"` → username already exists
- `"UNIQUE constraint failed: users.email"` → email already registered
- `"table students has no column named user_id"` → database migration issue (run app.py again)

### MySQL connection fails (if using XAMPP)

- Verify MySQL is running in XAMPP Control Panel
- Check credentials match what you set in the environment variables
- Try without password if using XAMPP default root: `setx DB_PASSWORD ""`
- Check XAMPP MySQL port (usually 3306, see my.ini if different)

## Database Schema

### SQLite (database.db)

Auto-created by Flask app on first run. Uses standard SQLite syntax.

### MySQL (XAMPP)

See `database_mysql_schema.sql` for the full schema definition.
Tables: users, students, companies, jobs, applications, shortlist

## Notes

- SQLite (default) is fine for development and small deployments
- MySQL/XAMPP is recommended for production
- Passwords are hashed using werkzeug.security
- Sessions are stored in Flask memory (use server-side sessions for production)
