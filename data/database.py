import sqlite3

DATABASE_NAME = "fittrack.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def setup_database():
    connection = get_connection()
    cursor = connection.cursor()

    # Stores registered users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Stores logged workout activities
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activities (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            type TEXT NOT NULL,
            date TEXT NOT NULL,
            duration INTEGER NOT NULL,
            distance TEXT,
            notes TEXT,
            route_data TEXT,
            is_public INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # If the activities table already existed before route_data was added,
    # this updates the old table safely.
    try:
        cursor.execute("ALTER TABLE activities ADD COLUMN route_data TEXT")
    except sqlite3.OperationalError:
        # Column already exists, so no action is needed.
        pass

    # Stores race tracker information
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS races (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            race_type TEXT NOT NULL,
            location TEXT NOT NULL,
            date TEXT NOT NULL,
            finish_time TEXT,
            is_pb INTEGER DEFAULT 0,
            status TEXT NOT NULL,
            user_id TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    connection.commit()
    
    # Add is_public column if it doesn't exist (for existing databases)
    cursor.execute("PRAGMA table_info(activities)")
    columns = [row[1] for row in cursor.fetchall()]
    if "is_public" not in columns:
        cursor.execute("ALTER TABLE activities ADD COLUMN is_public INTEGER DEFAULT 0")
    
    connection.commit()
    connection.close()