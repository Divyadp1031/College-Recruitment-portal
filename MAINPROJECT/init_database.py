#!/usr/bin/env python
"""
Initialize database.db and verify it's working
Run this BEFORE starting the Flask app
"""
import sqlite3
import os
from datetime import datetime

DB_FILE = "database.db"

print("=" * 70)
print("DATABASE INITIALIZATION - database.db")
print("=" * 70)

# Remove old database to start fresh
if os.path.exists(DB_FILE):
    print(f"\n⚠️  Found existing {DB_FILE}")
    response = input("Delete and recreate? (y/n): ").strip().lower()
    if response == 'y':
        os.remove(DB_FILE)
        print(f"✅ Deleted {DB_FILE}")
    else:
        print("Using existing database")
else:
    print(f"\n📝 Creating new {DB_FILE}")

# Create connection
conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

print("\n1️⃣  Creating tables...")

try:
    # Users table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password TEXT,
        user_type TEXT,
        created_at TIMESTAMP
    )
    """)
    print("   ✅ users table")

    # Students table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        name TEXT,
        phone TEXT,
        department TEXT,
        year INTEGER,
        cgpa REAL,
        skills TEXT,
        projects TEXT,
        resume_link TEXT,
        bio TEXT,
        profile_picture TEXT,
        created_at TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)
    print("   ✅ students table")

    # Companies table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        company_name TEXT,
        email TEXT,
        phone TEXT,
        website TEXT,
        industry TEXT,
        description TEXT,
        logo TEXT,
        verified BOOLEAN DEFAULT 0,
        created_at TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)
    print("   ✅ companies table")

    # Jobs table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
        job_title TEXT,
        role TEXT,
        description TEXT,
        skills_required TEXT,
        min_cgpa REAL,
        department TEXT,
        experience_level TEXT,
        job_type TEXT,
        salary_min REAL,
        salary_max REAL,
        location TEXT,
        application_deadline TIMESTAMP,
        created_at TIMESTAMP,
        FOREIGN KEY(company_id) REFERENCES companies(id)
    )
    """)
    print("   ✅ jobs table")

    # Applications table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        job_id INTEGER,
        status TEXT DEFAULT 'pending',
        applied_at TIMESTAMP,
        FOREIGN KEY(student_id) REFERENCES students(id),
        FOREIGN KEY(job_id) REFERENCES jobs(id)
    )
    """)
    print("   ✅ applications table")

    # Shortlist table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS shortlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
        student_id INTEGER,
        created_at TIMESTAMP,
        FOREIGN KEY(company_id) REFERENCES companies(id),
        FOREIGN KEY(student_id) REFERENCES students(id)
    )
    """)
    print("   ✅ shortlist table")

    conn.commit()
    print("\n✅ All tables created successfully!")

except Exception as e:
    print(f"\n❌ Error creating tables: {e}")
    conn.close()
    exit(1)

print("\n2️⃣  Verifying database...")

try:
    # Check tables exist
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cur.fetchall()]
    expected = ['users', 'students', 'companies', 'jobs', 'applications', 'shortlist']
    
    for table in expected:
        if table in tables:
            print(f"   ✅ {table}")
        else:
            print(f"   ❌ {table} MISSING!")
    
    # Check users table structure
    cur.execute("PRAGMA table_info(users)")
    user_cols = [c[1] for c in cur.fetchall()]
    print(f"\n   users columns: {user_cols}")

except Exception as e:
    print(f"\n❌ Error verifying database: {e}")
    conn.close()
    exit(1)

conn.close()

print("\n" + "=" * 70)
print("✅ DATABASE READY!")
print("=" * 70)
print("\nNext step:")
print("  python app.py")
print("\nThen:")
print("  1. Go to http://localhost:5000")
print("  2. Register a new student or company")
print("  3. Watch the terminal for [DB] logs")
print("  4. Login with your credentials")
print("=" * 70)
