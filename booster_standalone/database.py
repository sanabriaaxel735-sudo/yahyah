import sqlite3
import os

class Database:
    def __init__(self, db_name="booster.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.init_db()

    def init_db(self):
        # Table for licenses/keys
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS licenses (
                key TEXT PRIMARY KEY,
                type TEXT, -- e.g., '1month', 'lifetime'
                boost_count INTEGER,
                redeemed INTEGER DEFAULT 0,
                redeemed_by TEXT -- user id
            )
        ''')
        # Table for stored tokens
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tokens (
                token TEXT PRIMARY KEY,
                username TEXT,
                nitro_type TEXT,
                boosts_available INTEGER,
                last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def add_license(self, key, ltype, boost_count):
        try:
            self.cursor.execute("INSERT INTO licenses (key, type, boost_count) VALUES (?, ?, ?)", (key, ltype, boost_count))
            self.conn.commit()
            return True
        except: return False

    def redeem_license(self, key, user_id):
        self.cursor.execute("SELECT * FROM licenses WHERE key = ? AND redeemed = 0", (key,))
        lic = self.cursor.fetchone()
        if lic:
            self.cursor.execute("UPDATE licenses SET redeemed = 1, redeemed_by = ? WHERE key = ?", (user_id, key))
            self.conn.commit()
            return lic
        return None

    def add_token(self, token, username, nitro_type, boosts):
        self.cursor.execute("REPLACE INTO tokens (token, username, nitro_type, boosts_available) VALUES (?, ?, ?, ?)", 
                           (token, username, nitro_type, boosts))
        self.conn.commit()

db = Database()
