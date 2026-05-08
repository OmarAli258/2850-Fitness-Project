import sqlite3
import pytest
from unittest.mock import patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestDBConnection:
    def __init__(self, conn):
        self._conn = conn

    def cursor(self):
        return SQLiteQueryHelper(self._conn)

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        pass  # do nothing, keep connection open

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


class SQLiteQueryHelper:
    # converts postgres %s place holders into sqlite ? format.

    def __init__(self, conn):
        self._conn = conn
        self._cursor = conn.cursor()

    def execute(self, query, params=None):
        translated_query = query.replace("%s", "?")
        if params is None:
            return self._cursor.execute(translated_query)
        return self._cursor.execute(translated_query, params)

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


test_db_file = os.path.join(os.path.dirname(__file__), "test.db")


# creates test database in sqlite
def setup_test_db():
    if os.path.exists(test_db_file):
        os.remove(test_db_file)

    conn = sqlite3.connect(test_db_file)
    conn.row_factory = sqlite3.Row  # lets us access columns by name like row['email']

    cursor = conn.cursor()

    # create all the tables the app needs

    # users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # activities table
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

    # activity_likes table
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

    # activity_comments table
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

    # races table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS races (
            id INTEGER PRIMARY KEY,
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

    # plans table
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

    # plan_adherence table
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

    # friendships table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS friendships (
            id INTEGER PRIMARY KEY,
            from_user_id TEXT NOT NULL,
            to_user_id TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            FOREIGN KEY (from_user_id) REFERENCES users(id),
            FOREIGN KEY (to_user_id) REFERENCES users(id),
            UNIQUE(from_user_id, to_user_id)
        )
    """)

    conn.commit()

    return TestDBConnection(conn)


_db_connection = None


def get_db_connection():
    """
    returns the cached test database connection
    creates it once and reuses it so we dont keep opening new connections
    """
    global _db_connection
    if _db_connection is None:
        _db_connection = setup_test_db()
    return _db_connection


# pytest fixtures


@pytest.fixture(scope="function")
def app():
    global _db_connection
    _db_connection = None  # reset for each test

    # patch the database connection function so the app uses our test db
    with patch("data.database.get_connection", side_effect=get_db_connection):
        from app import app as flask_app

        flask_app.config["TESTING"] = True
        flask_app.config["SECRET_KEY"] = "test-secret-key"

        yield flask_app, get_db_connection()._conn


@pytest.fixture
def client(app):
    # gives us a test client that can make fake http requests to the flask app lets us test routes without actually running a server

    test_app, _ = app
    with test_app.test_client() as client:
        yield client


@pytest.fixture
def db_connection(app):
    """
    gives direct access to the test database
    lets us check that data was actually saved when we run tests
    """
    _, conn = app
    return conn


@pytest.fixture
def authenticated_client(client, db_connection):
    """
    returns a test client thats already logged in as a test user
    handy for testing routes that require login without having to login each time
    """
    # insert a test user directly into the db
    cursor = db_connection.cursor()
    cursor.execute(
        "INSERT INTO users (id, name, email, password) VALUES (?, ?, ?, ?)",
        ("test-user-id", "Test User", "test@example.com", "hashed_password_here"),
    )
    db_connection.commit()

    # simulate login by setting session variables
    with client.session_transaction() as sess:
        sess["user_id"] = "test-user-id"
        sess["user_name"] = "Test User"

    return client
