import sqlite3

conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()


def init_db():
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS documents (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, doc_name TEXT, original_text TEXT, simplified_text TEXT)')
    conn.commit()


def verify_user(username, password):
    """Returns True if the username/password pair matches a row in users."""
    c.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
    return c.fetchone() is not None


def create_user(username, password):
    c.execute('INSERT INTO users VALUES (?, ?)', (username, password))
    conn.commit()


def get_user_documents(username):
    """Returns (id, doc_name, original_text, simplified_text) rows, newest first."""
    c.execute(
        "SELECT id, doc_name, original_text, simplified_text FROM documents WHERE username=? ORDER BY id DESC",
        (username,)
    )
    return c.fetchall()


def insert_document(username, doc_name, original_text, simplified_text=""):
    c.execute(
        "INSERT INTO documents (username, doc_name, original_text, simplified_text) VALUES (?, ?, ?, ?)",
        (username, doc_name, original_text, simplified_text)
    )
    conn.commit()
    return c.lastrowid


def update_document_simplified(doc_id, simplified_text):
    c.execute("UPDATE documents SET simplified_text = ? WHERE id = ?", (simplified_text, doc_id))
    conn.commit()