import sqlite3

class Database:
    def __init__(self):
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = sqlite3.connect('database.db')
            self.cursor = self.conn.cursor()
            # Create table if it doesn't exist
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS states (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    capital TEXT NOT NULL
                )
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")

    def query(self, sql):
        try:
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"SQL error: {e}")
            return []

    def close_connection(self):
        if self.conn:
            self.conn.close()

def get_capitals_of_indian_states():
    db = Database()
    db.connect()
    sql = "SELECT capital FROM states WHERE name IN ('Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chandigarh', 'Chhattisgarh', 'Delhi', 'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jammu and Kashmir', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura', 'Uttarakhand', 'Uttar Pradesh', 'West Bengal')'"
    capitals = db.query(sql)
    for capital in capitals:
        print(capital[0])
    db.close_connection()

get_capitals_of_indian_states()