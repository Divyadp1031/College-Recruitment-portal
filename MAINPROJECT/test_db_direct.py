#!/usr/bin/env python
"""
Direct database test - bypass Flask to test SQLite directly
"""
import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash

db_file = "database.db"

print("=" * 60)
print("DIRECT DATABASE TEST - SQLite Only")
print("=" * 60)

# Delete old DB if exists to start fresh
if os.path.exists(db_file):
    os.remove(db_file)
    print(f"✅ Removed old {db_file}")

# Create connection and tables (same as Flask app)
conn = sqlite3.connect(db_file)
cur = conn.cursor()

print("\n1. Creating tables...")
try:
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
    
    conn.commit()
    print("✅ Tables created successfully")
except Exception as e:
    print(f"❌ Error creating tables: {e}")
    conn.close()
    exit(1)

print("\n2. Inserting test user...")
try:
    username = "testuser"
    email = "test@example.com"
    password = generate_password_hash("password123")
    
    cur.execute("""INSERT INTO users (username, email, password, user_type, created_at) 
                   VALUES (?, ?, ?, ?, ?)""",
                (username, email, password, 'student', datetime.now()))
    
    user_id = cur.lastrowid
    print(f"✅ User inserted with ID: {user_id}")
    
    # Insert student record
    cur.execute("""INSERT INTO students (user_id, name, cgpa, skills, created_at) 
                   VALUES (?, ?, ?, ?, ?)""",
                (user_id, "Test Student", 8.5, "Python,Django", datetime.now()))
    
    conn.commit()
    print(f"✅ Student record inserted")
    
except Exception as e:
    print(f"❌ Error inserting user: {e}")
    conn.close()
    exit(1)

print("\n3. Reading back the user...")
try:
    cur.execute("SELECT id, username, user_type FROM users WHERE username = ?", (username,))
    user = cur.fetchone()
    
    if user:
        print(f"✅ User found:")
        print(f"   ID: {user[0]}")
        print(f"   Username: {user[1]}")
        print(f"   Type: {user[2]}")
    else:
        print("❌ User not found after insert!")
        
except Exception as e:
    print(f"❌ Error reading user: {e}")

print("\n4. Listing all users...")
try:
    cur.execute("SELECT id, username, user_type FROM users")
    users = cur.fetchall()
    print(f"Total users: {len(users)}")
    for u in users:
        print(f"   - {u[1]} ({u[2]})")
except Exception as e:
    print(f"❌ Error listing users: {e}")

conn.close()

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
print("\nIf all tests passed (✅), then:")
print("1. Run: python app.py")
print("2. Register a new user")
print("3. Run this script again to see if the new user appears")
