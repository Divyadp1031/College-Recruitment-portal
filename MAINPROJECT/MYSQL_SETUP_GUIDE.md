# MySQL Setup Guide for College Recruitment Portal

This guide explains how to create the MySQL database, run the provided schema, and connect your Flask app.

## 1. Install MySQL

- Install MySQL Server (Windows): https://dev.mysql.com/downloads/mysql/
- During install, set a root password and remember it.

## 2. Create database and tables

Open a terminal (PowerShell) and run:

```bash
# navigate to project folder
cd "c:\Users\DIVYA PRIYA\Documents\MAINPROJECT"

# run the SQL schema (you will be prompted for MySQL root password)
mysql -u root -p < database_mysql_schema.sql
```

This creates the `college_recruitment` database and all tables.

## 3. Create a dedicated MySQL user (recommended)

Log into MySQL as root:

```bash
mysql -u root -p
```

Then run these SQL commands (replace password and host as needed):

```sql
CREATE USER 'portal_user'@'localhost' IDENTIFIED BY 'StrongPasswordHere';
GRANT ALL PRIVILEGES ON college_recruitment.* TO 'portal_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

## 4. Add Python MySQL connector

You can use `mysql-connector-python` or SQLAlchemy + a MySQL driver.

Install the connector:

```bash
pip install mysql-connector-python
# or if you prefer SQLAlchemy+PyMySQL
pip install sqlalchemy pymysql
```

I added `mysql-connector-python` to `requirements.txt`.

## 5. Example Flask connection (mysql-connector)

Use environment variables in production. Example snippet:

```python
import mysql.connector
from mysql.connector import pooling
import os

dbconfig = {
    'user': os.environ.get('DB_USER', 'portal_user'),
    'password': os.environ.get('DB_PASSWORD', 'StrongPasswordHere'),
    'host': os.environ.get('DB_HOST', '127.0.0.1'),
    'database': os.environ.get('DB_NAME', 'college_recruitment'),
    'raise_on_warnings': True
}

cnxpool = mysql.connector.pooling.MySQLConnectionPool(pool_name='mypool', pool_size=5, **dbconfig)

def get_db():
    return cnxpool.get_connection()
```

## 6. Example Flask connection (SQLAlchemy)

```python
from flask_sqlalchemy import SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://portal_user:StrongPasswordHere@localhost/college_recruitment'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
```

## 7. Testing

- Start Flask app and check pages.
- Verify database tables exist:

```bash
mysql -u portal_user -p -e "USE college_recruitment; SHOW TABLES;"
```

## 8. Notes

- Replace passwords and secrets with environment variables.
- Consider using migrations (Alembic / Flask-Migrate) for schema changes.
- For production, secure MySQL and limit privileges.

---

If you'd like, I can also:

- Add a Flask configuration switch to use MySQL instead of SQLite.
- Create an SQLAlchemy `models.py` mapping the tables.
- Generate sample seed data.
