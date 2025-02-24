import sqlite3

def create_users_db():
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()


        conn.execute("""
                CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                login TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
                )
        """)

        conn.commit()
        conn.close()