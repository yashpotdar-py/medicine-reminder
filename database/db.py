import sqlite3

def init_auth_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')

    # Create extracted_text table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS extracted_text (
            id INTEGER PRIMARY KEY,
            username TEXT,
            text TEXT,
            FOREIGN KEY (username) REFERENCES users (username)
        )
    ''')

    # Create medicine_schedule table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medicine_schedule (
            id INTEGER PRIMARY KEY,
            username TEXT,
            medicine_name TEXT,
            morning BOOLEAN,
            afternoon BOOLEAN,
            night BOOLEAN,
            FOREIGN KEY (username) REFERENCES users (username)
        )
    ''')

    conn.commit()
    conn.close()

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

def login_user(username, password):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

def store_extracted_text(username, text):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO extracted_text (username, text) VALUES (?, ?)", (username, text))
    conn.commit()
    conn.close()

def store_medicine_schedule(username, medicine_schedule):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO medicine_schedule (username, medicine_name, morning, afternoon, night) 
        VALUES (?, ?, ?, ?, ?)
    ''', (username, medicine_schedule['medicine_name'], medicine_schedule['morning'], medicine_schedule['afternoon'], medicine_schedule['night']))
    conn.commit()
    conn.close()

def get_medicine_schedule(username):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT medicine_name, morning, afternoon, night 
        FROM medicine_schedule 
        WHERE username = ?
    ''', (username,))
    schedule = cursor.fetchall()
    conn.close()

    # Return the schedule in a structured format
    return [{'medicine_name': row[0], 'morning': bool(row[1]), 'afternoon': bool(row[2]), 'night': bool(row[3])} for row in schedule]
