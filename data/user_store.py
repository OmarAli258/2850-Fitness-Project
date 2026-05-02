import uuid
from data.database import get_connection

def register(name, email, password):
    email = email.lower()

    connection = get_connection()
    cursor = connection.cursor()

    # Check if this email is already registered
    existing_user = cursor.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,)
    ).fetchone()

    if existing_user is not None:
        connection.close()
        return None
    
    user_id = str(uuid.uuid4())

    cursor.execute(
        """
        INSERT INTO users (id, name, email, password)
        VALUES (?, ?, ?, ?)
        """,
        (user_id, name, email, password)
    )

    connection.commit()
    connection.close()

    return {
        "id": user_id,
        "name": name,
        "email": email,
        "password": password
    }

def login(email, password):
    email = email.lower()
    
    connection = get_connection()
    cursor = connection.cursor()

    user = cursor.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,)
    ).fetchone()

    if user is None:
        return None

    # wrong password
    if user["password"] != password:
         return None

    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "password": user["password"]
    }

def find_by_id(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    user = cursor.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()

    connection.close()

    if user is None:
        return None
    
    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "password": user["password"]
    }