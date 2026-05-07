import uuid
from data.database import get_connection
from werkzeug.security import generate_password_hash, check_password_hash


def register(name, email, password):
    email = email.lower()

    connection = get_connection()
    cursor = connection.cursor()

    # Check if this email is already registered
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    existing_user = cursor.fetchone()

    if existing_user is not None:
        connection.close()
        return None

    user_id = str(uuid.uuid4())

    # hash the password before storing it
    password_hash = generate_password_hash(password)

    cursor.execute(
        """
        INSERT INTO users (id, name, email, password)
        VALUES (%s, %s, %s, %s)
        """,
        (user_id, name, email, password_hash),
    )

    connection.commit()
    connection.close()

    return {"id": user_id, "name": name, "email": email, "password": password_hash}


def login(email, password):
    email = email.lower()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    connection.close()

    if user is None:
        return None

    # check typed password against the hashed password in the database
    if not check_password_hash(user["password"], password):
        return None

    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "password": user["password"],
    }


def find_by_id(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    connection.close()

    if user is None:
        return None

    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "password": user["password"],
    }
