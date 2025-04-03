import sqlite3 as sql3

class Database:
    def __init__(self, db_name="money_manager_database.db"):
        self.conn = sql3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._create_table()
    
    def _create_table(self):
        self.cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users(
            tg_user_id INTEGER PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            tg_username TEXT,
            tg_user_last_name TEXT,
            tg_user_first_name TEXT
        );
        """)
        self.conn.commit()

    def add_user(self, user_id, username, last_name, first_name):
        self.cursor.execute(
            """
            INSERT OR IGNORE INTO users
            (tg_user_id, tg_username, tg_user_last_name, tg_user_first_name)
            VALUES (?, ?, ?, ?)""",
            (user_id, username, last_name, first_name)
        )
        self.conn.commit()

    def get_all_user(self):
        self.cursor.execute("""
        SELECT * FROM users
        """)
        return self.cursor.fetchall()

    def get_user(self, user_id):
        self.cursor.execute("""
        SELECT * FROM users
        WHERE tg_user_id = ?
        """, (user_id,))
        return self.cursor.fetchone()

    def conn_close(self):
        self.conn.close()
