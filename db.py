import sqlite3


def init_auth_db():
    conn = sqlite3.connect('auth.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS medicine_schedule (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            medicine_name TEXT,
            morning BOOLEAN,
            afternoon BOOLEAN,
            night BOOLEAN,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            medicine_name TEXT,
            reminder_time TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()


def register_user(username, password):
    conn = sqlite3.connect('auth.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                  (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def login_user(username, password):
    conn = sqlite3.connect('auth.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?',
              (username, password))
    user = c.fetchone()
    conn.close()
    return user


def store_medicine_schedule(user, medicine_schedule):
    conn = sqlite3.connect('auth.db')
    c = conn.cursor()
    c.execute('INSERT INTO medicine_schedule (user_id, medicine_name, morning, afternoon, night) VALUES (?, ?, ?, ?, ?)',
              (user[0], medicine_schedule['medicine_name'], medicine_schedule['morning'], medicine_schedule['afternoon'], medicine_schedule['night']))
    conn.commit()
    conn.close()


def get_medicine_schedule(user):
    conn = sqlite3.connect('auth.db')
    c = conn.cursor()
    c.execute('SELECT * FROM medicine_schedule WHERE user_id = ?', (user[0],))
    schedules = c.fetchall()
    conn.close()
    return [{'medicine_name': item[2], 'morning': item[3], 'afternoon': item[4], 'night': item[5]} for item in schedules]


def store_reminder(user, medicine_name, reminder_time):
    conn = sqlite3.connect('auth.db')
    c = conn.cursor()
    c.execute('INSERT INTO reminders (user_id, medicine_name, reminder_time) VALUES (?, ?, ?)',
              (user[0], medicine_name, reminder_time))
    conn.commit()
    conn.close()


def get_reminders(user):
    conn = sqlite3.connect('auth.db')
    c = conn.cursor()
    c.execute('SELECT * FROM reminders WHERE user_id = ?', (user[0],))
    reminders = c.fetchall()
    conn.close()
    return reminders


def delete_medicine_schedule(user, medicine_name):
    conn = sqlite3.connect('auth.db')
    c = conn.cursor()
    c.execute('DELETE FROM medicine_schedule WHERE user_id = ? AND medicine_name = ?',
              (user[0], medicine_name))
    conn.commit()
    conn.close()


def delete_reminder(user, medicine_name):
    conn = sqlite3.connect('auth.db')
    c = conn.cursor()
    c.execute('DELETE FROM reminders WHERE user_id = ? AND medicine_name = ?',
              (user[0], medicine_name))
    conn.commit()
    conn.close()


def update_medicine_schedule(user, old_name, new_schedule):
    conn = sqlite3.connect('auth.db')
    c = conn.cursor()
    c.execute('UPDATE medicine_schedule SET medicine_name = ?, morning = ?, afternoon = ?, night = ? WHERE user_id = ? AND medicine_name = ?',
              (new_schedule['medicine_name'], new_schedule['morning'], new_schedule['afternoon'], new_schedule['night'], user[0], old_name))
    conn.commit()
    conn.close()


def update_reminder(user, medicine_name, new_time):
    conn = sqlite3.connect('auth.db')
    c = conn.cursor()
    c.execute('UPDATE reminders SET reminder_time = ? WHERE user_id = ? AND medicine_name = ?',
              (new_time, user[0], medicine_name))
    conn.commit()
    conn.close()
