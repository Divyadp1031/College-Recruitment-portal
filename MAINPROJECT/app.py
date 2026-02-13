from flask import Flask, render_template, request, redirect, session, jsonify, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here_change_in_production'

# ---------- DATABASE CONNECTION ----------
# Toggle to use MySQL by setting environment variable USE_MYSQL=1
USE_MYSQL = os.environ.get('USE_MYSQL', '0') == '1'


if USE_MYSQL:
    # Initialize MySQL connection pool when requested (XAMPP / MySQL)
    try:
        import mysql.connector
        from mysql.connector import pooling

        dbconfig = {
            'user': os.environ.get('DB_USER', 'root'),
            'password': os.environ.get('DB_PASSWORD', ''),
            'host': os.environ.get('DB_HOST', '127.0.0.1'),
            'port': int(os.environ.get('DB_PORT', 3306)),
            'database': os.environ.get('DB_NAME', 'college_recruitment')
        }

        cnxpool = pooling.MySQLConnectionPool(pool_name='mypool', pool_size=5, **dbconfig)

        def get_db():
            return cnxpool.get_connection()
    except Exception as e:
        # If MySQL connector is not available or pool init fails, fallback to sqlite
        print('MySQL pool init failed, falling back to SQLite:', e)
        def get_db():
            return sqlite3.connect("database.db")
else:
    def get_db():
        return sqlite3.connect("database.db")


# Database helper to execute queries with correct param style for SQLite/MySQL
def db_query(query, params=(), commit=False, fetchone=False, fetchall=False, get_lastrowid=False):
    conn = get_db()
    cur = conn.cursor()
    result = None
    try:
        exec_query = query.replace('?', '%s') if USE_MYSQL else query
        if params:
            cur.execute(exec_query, params)
        else:
            cur.execute(exec_query)
        
        if commit:
            conn.commit()
            print(f"[DB] Commit successful for query")
        if fetchone:
            result = cur.fetchone()
        if fetchall:
            result = cur.fetchall()
        if get_lastrowid:
            result = cur.lastrowid
            print(f"[DB] Last row ID: {result}")
        return result
    except Exception as e:
        print(f"[DB ERROR] {str(e)}")
        try:
            conn.rollback()
        except:
            pass
        raise
    finally:
        try:
            cur.close()
        except:
            pass
        try:
            conn.close()
        except:
            pass

# ---------- CREATE TABLES ----------
def create_tables():
    conn = get_db()
    cur = conn.cursor()

    # Users Table (Students & Companies)
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

    # Students Table (Enhanced)
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

    # Companies Table (Enhanced)
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

    # Jobs Table (Enhanced with descriptions)
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

    # Applications Table
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

    # Shortlist Table
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

    conn.commit()
    conn.close()

create_tables()

# ---------- RUN SIMPLE MIGRATIONS FOR EXISTING SQLITE DB ----------
def migrate_sqlite_schema():
    conn = get_db()
    cur = conn.cursor()

    def has_column(table, column):
        cur.execute(f"PRAGMA table_info({table})")
        cols = [r[1] for r in cur.fetchall()]
        return column in cols

    # Ensure students table has modern columns
    if not has_column('students', 'user_id'):
        try:
            cur.execute("ALTER TABLE students ADD COLUMN user_id INTEGER")
        except Exception:
            pass

    # Add other commonly missing student columns if absent
    student_columns = {
        'phone': 'TEXT',
        'department': 'TEXT',
        'year': 'INTEGER',
        'skills': 'TEXT',
        'projects': 'TEXT',
        'resume_link': 'TEXT',
        'bio': 'TEXT',
        'profile_picture': 'TEXT',
        'created_at': 'TIMESTAMP'
    }
    for col, col_type in student_columns.items():
        if not has_column('students', col):
            try:
                cur.execute(f"ALTER TABLE students ADD COLUMN {col} {col_type}")
            except Exception:
                pass

    # Ensure companies table has user_id and expected columns
    if not has_column('companies', 'user_id'):
        try:
            cur.execute("ALTER TABLE companies ADD COLUMN user_id INTEGER")
        except Exception:
            pass

    company_columns = {
        'company_name': 'TEXT',
        'email': 'TEXT',
        'phone': 'TEXT',
        'website': 'TEXT',
        'industry': 'TEXT',
        'description': 'TEXT',
        'logo': 'TEXT',
        'verified': 'INTEGER',
        'created_at': 'TIMESTAMP'
    }
    for col, col_type in company_columns.items():
        if not has_column('companies', col):
            try:
                cur.execute(f"ALTER TABLE companies ADD COLUMN {col} {col_type}")
            except Exception:
                pass

    conn.commit()
    conn.close()


migrate_sqlite_schema()


# ---------- HOME ----------
@app.route('/')
def index():
    return render_template('index.html')

# ---------- STUDENT REGISTER ----------
@app.route('/student-register', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        name = request.form.get('name', '')
        try:
            hashed_password = generate_password_hash(password)
            user_id = db_query("INSERT INTO users (username, email, password, user_type, created_at) VALUES (?, ?, ?, ?, ?)",
                                (username, email, hashed_password, 'student', datetime.now()), commit=True, get_lastrowid=True)

            db_query("INSERT INTO students (user_id, name, cgpa, skills, created_at) VALUES (?, ?, ?, ?, ?)",
                     (user_id, name, 0.0, '', datetime.now()), commit=True)

            print(f"Student registered: {username} with ID {user_id}")
            return redirect('/login')
        except Exception as e:
            error_msg = str(e)
            print(f"Registration error: {error_msg}")
            return render_template('student_register.html', error=f'Error: {error_msg}')

    return render_template('student_register.html')

# ---------- COMPANY REGISTER ----------
@app.route('/company-register', methods=['GET', 'POST'])
def company_register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        company_name = request.form['company_name']
        try:
            hashed_password = generate_password_hash(password)
            user_id = db_query("INSERT INTO users (username, email, password, user_type, created_at) VALUES (?, ?, ?, ?, ?)",
                                (username, email, hashed_password, 'company', datetime.now()), commit=True, get_lastrowid=True)

            db_query("INSERT INTO companies (user_id, company_name, email, created_at) VALUES (?, ?, ?, ?)",
                     (user_id, company_name, email, datetime.now()), commit=True)

            print(f"Company registered: {username} with ID {user_id}")
            return redirect('/login')
        except Exception as e:
            error_msg = str(e)
            print(f"Company registration error: {error_msg}")
            return render_template('company_register.html', error=f'Error: {error_msg}')

    return render_template('company_register.html')

# ---------- LOGIN ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            # Try to find user by username OR email
            user = db_query("SELECT id, password, user_type, username FROM users WHERE username = ? OR email = ?", (username, username), fetchone=True)
            print(f"[LOGIN] Login attempt with: {username}")
            print(f"[LOGIN] User found in DB: {user is not None}")
            
            if user:
                user_id, stored_hash, user_type, registered_username = user
                print(f"[LOGIN] Found user: {registered_username} (ID: {user_id}, Type: {user_type})")
                print(f"[LOGIN] Stored hash: {stored_hash[:50]}...")
                print(f"[LOGIN] Password provided: {password}")
                
                # Test password verification
                hash_match = check_password_hash(stored_hash, password)
                print(f"[LOGIN] Password hash match: {hash_match}")
                
                if hash_match:
                    session['user_id'] = user_id
                    session['user_type'] = user_type
                    print(f"[LOGIN] ✅ Login successful for user: {registered_username}")
                    
                    if user_type == 'student':
                        return redirect('/dashboard-student')
                    else:
                        return redirect('/dashboard-company')
                else:
                    print(f"[LOGIN] ❌ Password mismatch")
            else:
                print(f"[LOGIN] ❌ User not found with username or email: {username}")
                
        except Exception as e:
            print(f"[LOGIN] ❌ Query error: {str(e)}")
            user = None

        return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')

# ---------- LOGOUT ----------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ---------- STUDENT DASHBOARD ----------
@app.route('/dashboard-student')
def dashboard_student():
    if 'user_id' not in session or session['user_type'] != 'student':
        return redirect('/login')
    
    conn = get_db()
    cur = conn.cursor()
    
    # Get student info
    cur.execute("""SELECT s.*, u.email FROM students s 
                   JOIN users u ON s.user_id = u.id WHERE s.user_id = ?""", (session['user_id'],))
    student = cur.fetchone()
    
    # Get applied jobs
    cur.execute("""SELECT j.*, c.company_name FROM applications a
                   JOIN jobs j ON a.job_id = j.id
                   JOIN companies c ON j.company_id = c.id
                   WHERE a.student_id = ?""", (student[0],))
    applications = cur.fetchall()
    
    conn.close()
    return render_template('dashboard_student.html', student=student, applications=applications)

# ---------- STUDENT PROFILE EDIT ----------
@app.route('/edit-profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session or session['user_type'] != 'student':
        return redirect('/login')
    
    if request.method == 'POST':
        conn = get_db()
        cur = conn.cursor()

        # Get current resume filename (if any)
        cur.execute("SELECT resume_link FROM students WHERE user_id = ?", (session['user_id'],))
        row = cur.fetchone()
        current_resume = row[0] if row and len(row) > 0 else None

        # Handle resume upload
        resume_filename = current_resume
        file = request.files.get('resume')
        if file and file.filename:
            filename = secure_filename(file.filename)
            save_dir = os.path.join('static', 'resumes')
            try:
                os.makedirs(save_dir, exist_ok=True)
            except Exception:
                pass
            timestamp = int(datetime.now().timestamp())
            stored_name = f"{session['user_id']}_{timestamp}_{filename}"
            file_path = os.path.join(save_dir, stored_name)
            file.save(file_path)
            resume_filename = stored_name

        cur.execute("""UPDATE students SET name=?, phone=?, department=?, year=?, cgpa=?, skills=?, projects=?, bio=?, resume_link=?
                      WHERE user_id = ?""",
                   (request.form['name'], request.form.get('phone', ''),
                    request.form.get('department', ''), request.form.get('year', 0),
                    request.form['cgpa'], request.form['skills'],
                    request.form.get('projects', ''), request.form.get('bio', ''),
                    resume_filename, session['user_id']))

        conn.commit()
        conn.close()
        return redirect('/dashboard-student')
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM students WHERE user_id = ?", (session['user_id'],))
    student = cur.fetchone()
    conn.close()
    
    return render_template('edit_profile.html', student=student)

# ---------- JOB LISTINGS (For Students) ----------
@app.route('/job-listings')
def job_listings():
    if 'user_id' not in session or session['user_type'] != 'student':
        return redirect('/login')
    
    conn = get_db()
    cur = conn.cursor()
    
    # Get filters
    role = request.args.get('role', '')
    skills = request.args.get('skills', '')
    min_cgpa = request.args.get('min_cgpa', 0)
    department = request.args.get('department', '')
    job_type = request.args.get('job_type', '')
    
    # Build query
    query = "SELECT j.*, c.company_name FROM jobs j JOIN companies c ON j.company_id = c.id WHERE 1=1"
    params = []
    
    if role:
        query += " AND j.role LIKE ?"
        params.append(f'%{role}%')
    if skills:
        query += " AND j.skills_required LIKE ?"
        params.append(f'%{skills}%')
    if min_cgpa:
        query += " AND j.min_cgpa <= ?"
        params.append(float(min_cgpa))
    if department:
        query += " AND j.department LIKE ?"
        params.append(f'%{department}%')
    if job_type:
        query += " AND j.job_type = ?"
        params.append(job_type)
    
    query += " ORDER BY j.created_at DESC"
    
    cur.execute(query, params)
    jobs = cur.fetchall()
    conn.close()
    
    return render_template('job_listings.html', jobs=jobs)

# ---------- JOB DETAIL ----------
@app.route('/job/<int:job_id>')
def job_detail(job_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""SELECT j.*, c.company_name, c.description FROM jobs j
                   JOIN companies c ON j.company_id = c.id WHERE j.id = ?""", (job_id,))
    job = cur.fetchone()
    
    conn.close()
    return render_template('job_detail.html', job=job)

# ---------- APPLY FOR JOB ----------
@app.route('/apply-job/<int:job_id>', methods=['POST'])
def apply_job(job_id):
    if 'user_id' not in session or session['user_type'] != 'student':
        return redirect('/login')
    
    conn = get_db()
    cur = conn.cursor()
    
    # Get student ID
    cur.execute("SELECT id FROM students WHERE user_id = ?", (session['user_id'],))
    student_id = cur.fetchone()[0]
    
    # Check if already applied
    cur.execute("SELECT id FROM applications WHERE student_id = ? AND job_id = ?", (student_id, job_id))
    if cur.fetchone():
        conn.close()
        return jsonify({'status': 'already_applied'})
    
    # Create application
    cur.execute("INSERT INTO applications (student_id, job_id, applied_at) VALUES (?, ?, ?)",
               (student_id, job_id, datetime.now()))
    
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success'})

# ---------- COMPANY DASHBOARD ----------
@app.route('/dashboard-company')
def dashboard_company():
    if 'user_id' not in session or session['user_type'] != 'company':
        return redirect('/login')
    
    conn = get_db()
    cur = conn.cursor()
    
    # Get company info
    cur.execute("SELECT * FROM companies WHERE user_id = ?", (session['user_id'],))
    company = cur.fetchone()
    
    if not company:
        conn.close()
        return redirect('/login')
    
    # Get company jobs
    cur.execute("SELECT * FROM jobs WHERE company_id = ? ORDER BY created_at DESC", (company[0],))
    jobs = cur.fetchall()
    
    # Count applications
    cur.execute("SELECT COUNT(*) FROM applications a JOIN jobs j ON a.job_id = j.id WHERE j.company_id = ?", (company[0],))
    total_applications = cur.fetchone()[0]
    
    conn.close()
    return render_template('dashboard_company.html', company=company, jobs=jobs, total_applications=total_applications)

# ---------- POST JOB ----------
@app.route('/post-job', methods=['GET', 'POST'])
def post_job():
    if 'user_id' not in session or session['user_type'] != 'company':
        return redirect('/login')
    
    if request.method == 'POST':
        conn = get_db()
        cur = conn.cursor()
        
        # Get company ID
        cur.execute("SELECT id FROM companies WHERE user_id = ?", (session['user_id'],))
        company_id = cur.fetchone()[0]
        
        # Create job
        cur.execute("""INSERT INTO jobs (company_id, job_title, role, description, skills_required,
                                         min_cgpa, department, experience_level, job_type, 
                                         salary_min, salary_max, location, created_at)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                   (company_id, request.form['job_title'], request.form['role'],
                    request.form['description'], request.form['skills_required'],
                    float(request.form['min_cgpa']), request.form['department'],
                    request.form['experience_level'], request.form['job_type'],
                    float(request.form.get('salary_min', 0)), float(request.form.get('salary_max', 0)),
                    request.form['location'], datetime.now()))
        
        conn.commit()
        conn.close()
        
        return redirect('/dashboard-company')
    
    return render_template('post_job.html')

# ---------- FILTER CANDIDATES ----------
@app.route('/filter-candidates')
def filter_candidates():
    if 'user_id' not in session or session['user_type'] != 'company':
        return redirect('/login')
    
    conn = get_db()
    cur = conn.cursor()
    
    # Get company ID
    cur.execute("SELECT id FROM companies WHERE user_id = ?", (session['user_id'],))
    company_id = cur.fetchone()[0]
    
    # Get filters
    role = request.args.get('role', '')
    skills = request.args.get('skills', '')
    min_cgpa = request.args.get('min_cgpa', 0)
    department = request.args.get('department', '')
    job_description = request.args.get('job_description', '')
    
    # Build query
    query = "SELECT DISTINCT s.* FROM students s WHERE 1=1"
    params = []
    
    if role:
        query += " AND s.skills LIKE ?"
        params.append(f'%{role}%')
    if skills:
        query += " AND s.skills LIKE ?"
        params.append(f'%{skills}%')
    if min_cgpa:
        query += " AND s.cgpa >= ?"
        params.append(float(min_cgpa))
    if department:
        query += " AND s.department LIKE ?"
        params.append(f'%{department}%')
    
    query += " ORDER BY s.cgpa DESC"
    
    cur.execute(query, params)
    students = cur.fetchall()
    
    # Get company's jobs for reference
    cur.execute("SELECT id, job_title, role FROM jobs WHERE company_id = ?", (company_id,))
    company_jobs = cur.fetchall()
    
    conn.close()
    return render_template('filter_candidates.html', students=students, company_jobs=company_jobs)

# ---------- SHORTLIST STUDENT ----------
@app.route('/shortlist-student/<int:student_id>', methods=['POST'])
def shortlist_student(student_id):
    if 'user_id' not in session or session['user_type'] != 'company':
        return jsonify({'status': 'unauthorized'})
    
    conn = get_db()
    cur = conn.cursor()
    
    # Get company ID
    cur.execute("SELECT id FROM companies WHERE user_id = ?", (session['user_id'],))
    company_id = cur.fetchone()[0]
    
    # Check if already shortlisted
    cur.execute("SELECT id FROM shortlist WHERE company_id = ? AND student_id = ?", (company_id, student_id))
    if cur.fetchone():
        conn.close()
        return jsonify({'status': 'already_shortlisted'})
    
    # Add to shortlist
    cur.execute("INSERT INTO shortlist (company_id, student_id, created_at) VALUES (?, ?, ?)",
               (company_id, student_id, datetime.now()))
    
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success'})

# ---------- RUN ----------
if __name__ == '__main__':
    app.run(debug=True)