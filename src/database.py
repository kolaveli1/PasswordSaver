import sqlite3
from encryption import encrypt_password, decrypt_password

DB_NAME = "passwords.db"

def setup_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            website TEXT NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()

def add_category(name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

def get_categories():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()
    conn.close()
    return categories

def add_password(category_name, website, username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (category_name,))
    cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
    category_id = cursor.fetchone()[0]

    encrypted_password = encrypt_password(password)

    cursor.execute("INSERT INTO passwords (category_id, website, username, password) VALUES (?, ?, ?, ?)",
                   (category_id, website, username, encrypted_password))

    conn.commit()
    conn.close()

def get_passwords_by_category(category_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
    category = cursor.fetchone()
    if not category:
        return []

    category_id = category[0]

    cursor.execute("SELECT website, username, password FROM passwords WHERE category_id = ?", (category_id,))
    passwords = cursor.fetchall()

    conn.close()
    return passwords

def delete_password(website, username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM passwords WHERE website = ? AND username = ?", (website, username))
    
    conn.commit()
    conn.close()

def update_password(website, old_username, new_username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("UPDATE passwords SET username = ? WHERE website = ? AND username = ?", (new_username, website, old_username))
    
    conn.commit()
    conn.close()