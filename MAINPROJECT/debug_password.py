#!/usr/bin/env python
"""
Debug password hash issue in database.db
Shows stored hashes and tests verification
"""
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

DB_FILE = "database.db"

print("=" * 70)
print("PASSWORD HASH DEBUGGING")
print("=" * 70)

conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

print("\n1️⃣  Checking users in database.db...")
try:
    cur.execute("SELECT id, username, password, user_type FROM users")
    users = cur.fetchall()
    
    if not users:
        print("❌ No users found in database!")
        conn.close()
        exit(1)
    
    print(f"✅ Found {len(users)} user(s):\n")
    
    for uid, username, stored_hash, user_type in users:
        print(f"   ID: {uid}")
        print(f"   Username: {username}")
        print(f"   Type: {user_type}")
        print(f"   Hash: {stored_hash[:50]}...")
        
        # Test password verification
        test_password = input(f"   Enter password to test for '{username}': ").strip()
        
        try:
            match = check_password_hash(stored_hash, test_password)
            if match:
                print(f"   ✅ PASSWORD CORRECT!\n")
            else:
                print(f"   ❌ Password incorrect\n")
        except Exception as e:
            print(f"   ❌ Error verifying hash: {e}\n")

except Exception as e:
    print(f"❌ Error reading users: {e}")

conn.close()

print("\n" + "=" * 70)
print("HASH FORMAT CHECK")
print("=" * 70)

# Check if hash format is valid (should start with pbkdf2:sha256$)
print("\nValid Werkzeug hashes start with: pbkdf2:sha256$")
print("\nIf hashes don't start with that, they may be corrupted.")

# Create a test hash to show the format
test_hash = generate_password_hash("testpassword")
print(f"\nExample valid hash: {test_hash[:50]}...")

print("\n" + "=" * 70)
