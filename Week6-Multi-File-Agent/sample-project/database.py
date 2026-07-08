def connect():
    # Establishes a connection to the database
    print("Connected to the Database")
    return "connection-object"

def query(sql):
    print(f"Running query:{sql}")
    return []

def close_connection():
    print("Connection closed")