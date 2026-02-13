#!/usr/bin/env python
"""
Quick test script to verify database setup and registration/login flow
"""
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Test database connection
db_file = "database.db"
print(f"Testing database: {db_file}")

if not os.path.exists(db_file):
    print("❌ database.db not found. Running app.py first will create it.")
else:
    print(f"✅ database.db exists")

conn = sqlite3.connect(db_file)
cur = conn.cursor()

# Check if tables exist
try:
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cur.fetchall()
    print(f"✅ Found tables: {[t[0] for t in tables]}")
except Exception as e:
    print(f"❌ Error reading tables: {e}")

# Check users table
try:
    cur.execute("PRAGMA table_info(users)")
    cols = cur.fetchall()
    print(f"✅ users table columns: {[c[1] for c in cols]}")
except Exception as e:
    print(f"❌ Error reading users schema: {e}")

# List existing users
try:
    cur.execute("SELECT id, username, user_type FROM users")
    users = cur.fetchall()
    if users:
        print(f"✅ Found {len(users)} users:")
        for u in users:
            print(f"   - ID: {u[0]}, Username: {u[1]}, Type: {u[2]}")
    else:
        print("⚠️  No users in database yet. Register to create one.")
except Exception as e:
    print(f"❌ Error reading users: {e}")

conn.close()

print("\n--- Next steps ---")
print("1. Start the Flask app: python app.py")
print("2. Go to http://localhost:5000")
print("3. Register a new student or company")
print("4. Check terminal for debug logs (should show 'Student registered: ...')")
print("5. Login with the registered username and password")
print("6. Run this script again to verify user was saved")
