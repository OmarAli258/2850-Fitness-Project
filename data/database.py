import os
import psycopg2
from psycopg2.extras import RealDictCursor


def get_connection():
    DATABASE_URL = os.getenv("DATABASE_URL")
    connection = psycopg2.connect(DATABASE_URL)
    connection.cursor_factory = RealDictCursor
    return connection


def setup_database():
    connection = get_connection()
    cursor = connection.cursor()

    # Stores registered users
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        connection.commit()
    except Exception:
        connection.rollback()

    # Stores logged workout activities
    try:
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
        connection.commit()
    except Exception:
        connection.rollback()
    
    # If the activities table already existed before route_data was added,
    # this updates the old table safely.
    try:
        cursor.execute("ALTER TABLE activities ADD COLUMN route_data TEXT")
        connection.commit()
    except Exception:
        connection.rollback()

    # Stores race tracker information
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS races (
                id SERIAL PRIMARY KEY,
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
    except Exception:
        connection.rollback()

    # Stores exercise plans
    try:
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
    except Exception:
        connection.rollback()

    try:
        cursor.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'activities'
        """)
        columns = [row['column_name'] for row in cursor.fetchall()]
    
    # Add is_public column if it doesn't exist (for existing databases)
        if "is_public" not in columns:
            cursor.execute("ALTER TABLE activities ADD COLUMN is_public INTEGER DEFAULT 0")
            connection.commit()
        
        # Add plan_id column to activities if it doesn't exist
        if "plan_id" not in columns:
            cursor.execute("ALTER TABLE activities ADD COLUMN plan_id TEXT")
            connection.commit()
    except Exception:
        connection.rollback()

    # Stores plan adherence records (how well planned sessions were followed)
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
        connection.rollback()

    connection.close()