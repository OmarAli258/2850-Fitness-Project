# this file creates the database connection and sets up all tables used by the app

# import os for environment variables and psycopg2 for the neon postgres database
import os
import psycopg2
from psycopg2.extras import RealDictCursor


# this function opens a database connection and lets rows behave like dictionaries
def get_connection():
    DATABASE_URL = os.getenv("DATABASE_URL")
    connection = psycopg2.connect(DATABASE_URL)
    connection.cursor_factory = RealDictCursor
    return connection


# this function creates the database tables if they do not already exist
def setup_database():
    connection = get_connection()
    cursor = connection.cursor()

    # this table stores registered users
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

    # this table stores logged workout activities
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

    # this adds route data to older activity tables if it is missing
    try:
        cursor.execute("ALTER TABLE activities ADD COLUMN route_data TEXT")
        connection.commit()
    except Exception:
        connection.rollback()

    # this table stores likes that users add to public feed activities
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_likes (
                id TEXT PRIMARY KEY,
                activity_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE (activity_id, user_id),
                FOREIGN KEY (activity_id) REFERENCES activities(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        connection.commit()
    except Exception:
        connection.rollback()

    # this table stores comments users leave on public feed activities
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_comments (
                id TEXT PRIMARY KEY,
                activity_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                body TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (activity_id) REFERENCES activities(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        connection.commit()
    except Exception:
        connection.rollback()

    # this table stores race tracker information
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

    # this table stores exercise plans
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
        columns = [row["column_name"] for row in cursor.fetchall()]

        # this adds the public activity column for older databases if it is missing
        if "is_public" not in columns:
            cursor.execute(
                "ALTER TABLE activities ADD COLUMN is_public INTEGER DEFAULT 0"
            )
            connection.commit()

        # this adds the plan link column for older databases if it is missing
        if "plan_id" not in columns:
            cursor.execute("ALTER TABLE activities ADD COLUMN plan_id TEXT")
            connection.commit()
    except Exception:
        connection.rollback()

    # this table stores consistency records for how well planned sessions were followed
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
    # this table stores friend requests and accepted friendships
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS friendships (
                id SERIAL PRIMARY KEY,
                from_user_id TEXT NOT NULL,
                to_user_id TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                FOREIGN KEY (from_user_id) REFERENCES users(id),
                FOREIGN KEY (to_user_id) REFERENCES users(id),
                UNIQUE(from_user_id, to_user_id)
            )
        """)
        connection.commit()
    except Exception:
        connection.rollback()
    connection.close()


# done comments for data/database.py
# summary of comments:
# - explains the database connection setup
# - shows where the users table is created
# - shows where the activities table is created
# - handles older activity tables with missing columns
# - shows where feed likes and comments are stored
# - shows where race and plan tables are created
# - shows where plan consistency records are stored
# - shows where friendships and friend requests are stored
