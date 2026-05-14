import sqlite3

class AIDatabase:
    def __init__(self, db_name="nova_ai.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.init_db()

    def init_db(self):
        # Table for AI licenses
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_licenses (
                key TEXT PRIMARY KEY,
                duration TEXT DEFAULT 'lifetime', -- '1day', '1week', '1month', '1year', 'lifetime'
                redeemed INTEGER DEFAULT 0,
                redeemed_by TEXT -- discord user id
            )
        ''')
        # Table for authorized users
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS authorized_users (
                user_id TEXT PRIMARY KEY,
                access_level TEXT DEFAULT 'pro',
                expiry TIMESTAMP -- NULL for lifetime
            )
        ''')
        self.conn.commit()

    def redeem_key(self, key, user_id):
        import datetime
        # AI Key Redemption
        self.cursor.execute("SELECT duration FROM ai_licenses WHERE key = ? AND redeemed = 0", (key,))
        lic = self.cursor.fetchone()
        if lic:
            duration = lic[0]
            expiry = None
            now = datetime.datetime.now()
            
            if duration == '1day': expiry = now + datetime.timedelta(days=1)
            elif duration == '1week': expiry = now + datetime.timedelta(weeks=1)
            elif duration == '1month': expiry = now + datetime.timedelta(days=30)
            elif duration == '1year': expiry = now + datetime.timedelta(days=365)
            
            expiry_str = expiry.strftime('%Y-%m-%d %H:%M:%S') if expiry else None
            
            self.cursor.execute("UPDATE ai_licenses SET redeemed = 1, redeemed_by = ? WHERE key = ?", (user_id, key))
            self.cursor.execute("INSERT OR REPLACE INTO authorized_users (user_id, expiry) VALUES (?, ?)", (user_id, expiry_str))
            self.conn.commit()
            return True
        return False

    def redeem_license(self, key, user_id):
        # Support for Booster licenses as well
        return self.redeem_key(key, user_id)

    def is_authorized(self, user_id):
        import datetime
        self.cursor.execute("SELECT expiry FROM authorized_users WHERE user_id = ?", (user_id,))
        res = self.cursor.fetchone()
        if not res: return False
        
        expiry_str = res[0]
        if expiry_str is None: return True # Lifetime
        
        expiry = datetime.datetime.strptime(expiry_str, '%Y-%m-%d %H:%M:%S')
        if datetime.datetime.now() < expiry:
            return True
        return False

    def add_ai_license(self, key, duration='lifetime'):
        try:
            self.cursor.execute("INSERT INTO ai_licenses (key, duration) VALUES (?, ?)", (key, duration))
            self.conn.commit()
            return True
        except: return False

    def add_debug_key(self, key):
        try:
            self.cursor.execute("INSERT INTO ai_licenses (key) VALUES (?)", (key,))
            self.conn.commit()
        except: pass

db = AIDatabase()
