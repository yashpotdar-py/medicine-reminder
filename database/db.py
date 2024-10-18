import sqlite3

# Function to initialize the authentication database
def init_auth_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS extracted_text (
            id INTEGER PRIMARY KEY,
            username TEXT,
            text TEXT,
            FOREIGN KEY (username) REFERENCES users (username)
        )
    ''')
    conn.commit()
    conn.close()

# Function to register a user
def register_user(username, password):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# Function to log in a user
def login_user(username, password):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

# Function to store extracted text in the database
def store_extracted_text(username, text):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO extracted_text (username, text) VALUES (?, ?)", (username, text))
    conn.commit()
    conn.close()
