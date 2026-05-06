#this file creates the database connection and sets up all tables used by the app

#import sqlite3 so the app can use the local sqlite database file
import sqlite3

#this is the database file name used by the app
DATABASE_NAME = "fittrack.db"


#this function opens a database connection and lets rows behave like dictionaries
def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection


#this function creates the database tables if they do not already exist
def setup_database():
    connection = get_connection()
    cursor = connection.cursor()

    #this table stores registered users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    #this table stores logged workout activities
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
            plan_id TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    #this adds route data to older activity tables if it is missing
    try:
        cursor.execute("ALTER TABLE activities ADD COLUMN route_data TEXT")
    except sqlite3.OperationalError:
        #this means the column already exists so nothing else is needed
        pass

    #this table stores race tracker information
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

    #this table stores exercise plans
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS plans (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            exercise_type TEXT NOT NULL,
            frequency TEXT NOT NULL,
            target_duration INTEGER,
            target_distance TEXT,
            notes TEXT,
            created_at TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    connection.commit()
    
    #this checks which columns already exist in the activities table
    cursor.execute("PRAGMA table_info(activities)")
    columns = [row[1] for row in cursor.fetchall()]

    #this adds the public activity column for older databases if it is missing
    if "is_public" not in columns:
        cursor.execute("ALTER TABLE activities ADD COLUMN is_public INTEGER DEFAULT 0")

    #this adds the plan link column for older databases if it is missing
    if "plan_id" not in columns:
        cursor.execute("ALTER TABLE activities ADD COLUMN plan_id TEXT")
        
    connection.commit()

    #this table stores consistency records for how well planned sessions were followed
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS plan_adherence (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                plan_id TEXT NOT NULL,
                session_date TEXT NOT NULL,
                rating INTEGER NOT NULL,
                notes TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (plan_id) REFERENCES plans(id)
            )
        """)
        connection.commit()
    except Exception:
        pass

    connection.close()


#done comments for data/database.py
#summary of comments:
#- explains the database connection setup
#- shows where the users table is created
#- shows where the activities table is created
#- handles older activity tables with missing columns
#- shows where race and plan tables are created
#- shows where plan consistency records are stored
