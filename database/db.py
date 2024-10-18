import sqlite3
import hashlib

# Initialize the database to include user authentication


def init_auth_db():
    conn = sqlite3.connect('medicines.db')
    cursor = conn.cursor()

    # Create a users table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    ''')

    conn.commit()
    conn.close()

# Hash the password using SHA256


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Add a new user to the database


def register_user(username, password):
    conn = sqlite3.connect('medicines.db')
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                       (username, hash_password(password)))
        conn.commit()
    except sqlite3.IntegrityError:
        return False  # Username already exists
    finally:
        conn.close()
    return True

# Check user credentials for login


def login_user(username, password):
    conn = sqlite3.connect('medicines.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?",
                   (username, hash_password(password)))
    user = cursor.fetchone()

    conn.close()
    return user  # Returns None if no match is found
