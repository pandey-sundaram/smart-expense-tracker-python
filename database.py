import sqlite3

def get_connection():
    conn = sqlite3.connect("expense.db", check_same_thread=False)
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        date TEXT,
        category TEXT,
        amount REAL
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS budgets (
        username TEXT UNIQUE,
        monthly_budget REAL
    )
    """)

    conn.commit()
    conn.close()
