import sqlite3
import os
from config import Config
from pathlib import Path

class Database:
    def __init__(self, db_name="money_manager_database.db"):

        ### Create the database directory if it doesn't exist
        self.db_path = os.path.join(Config.ROOT_DIR, "data", db_name)
        self.db_dir = Path(self.db_path).parent

        if not os.path.exists(self.db_dir):
            os.makedirs(self.db_dir)

        ### Create the database file if it doesn't exist
        self.conn = sqlite3.connect(self.db_path)

        ### Create a cursor object to execute SQL commands
        self.cursor = self.conn.cursor()
        self._create_table()

    
    def _create_table(self):
        self.cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users(
            tg_user_id INTEGER PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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

    def get_user_by_id(self, user_id):
        self.cursor.execute("""
        SELECT * FROM users
        WHERE tg_user_id = ?
        """, (user_id,))
        return self.cursor.fetchall()

    def conn_close(self):
        self.conn.close()