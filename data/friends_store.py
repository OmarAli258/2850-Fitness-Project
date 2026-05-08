from data.database import get_connection


def send_request(from_user_id, to_user_id):
    # send a friend request from one user to another, blocks duplicates and self-requests
    if from_user_id == to_user_id:
        return False

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT * FROM friendships
        WHERE (from_user_id = %s AND to_user_id = %s)
           OR (from_user_id = %s AND to_user_id = %s)
        """,
        (from_user_id, to_user_id, to_user_id, from_user_id),
    )
    existing = cursor.fetchone()

    if existing is not None:
        connection.close()
        return False

    cursor.execute(
        """
        INSERT INTO friendships (from_user_id, to_user_id, status)
        VALUES (%s, %s, 'pending')
        """,
        (from_user_id, to_user_id),
    )

    connection.commit()
    connection.close()
    return True


def accept_request(request_id, user_id):
    # accept a pending friend request, only works if user is the recipient
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE friendships
        SET status = 'accepted'
        WHERE id = %s AND to_user_id = %s AND status = 'pending'
        """,
        (request_id, user_id),
    )

    connection.commit()
    connection.close()


def reject_request(request_id, user_id):
    # reject (delete) a pending friend request, only works if user is the recipient
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM friendships
        WHERE id = %s AND to_user_id = %s AND status = 'pending'
        """,
        (request_id, user_id),
    )

    connection.commit()
    connection.close()


def get_friends(user_id):
    # get a list of all accepted friends for a user with their info
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT DISTINCT users.id, users.name, users.email
        FROM friendships
        JOIN users ON (
            (friendships.from_user_id = users.id AND friendships.to_user_id = %s)
            OR
            (friendships.to_user_id = users.id AND friendships.from_user_id = %s)
        )
        WHERE friendships.status = 'accepted'
        GROUP BY users.id
        """,
        (user_id, user_id),
    )

    friends = [dict(row) for row in cursor.fetchall()]
    connection.close()
    return friends


def get_pending_requests(user_id):
    # get all incoming pending requests for this user
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT friendships.id as request_id, users.id as user_id, users.name, users.email
        FROM friendships
        JOIN users ON friendships.from_user_id = users.id
        WHERE friendships.to_user_id = %s AND friendships.status = 'pending'
        """,
        (user_id,),
    )

    requests = [dict(row) for row in cursor.fetchall()]
    connection.close()
    return requests


def get_friend_ids(user_id):
    # helper that returns just a list of friend IDs, used by the feed filter
    friends = get_friends(user_id)
    return [friend["id"] for friend in friends]


def search_users(query, current_user_id):
    # search users by name and include existing friendship status for the current user
    connection = get_connection()
    cursor = connection.cursor()

    search = f"%{query.lower()}%"

    cursor.execute(
        """
        SELECT
            users.id,
            users.name,
            users.email,
            CASE
                WHEN friendships.status = 'accepted' THEN 'friends'
                WHEN friendships.status = 'pending' AND friendships.from_user_id = %s THEN 'request_sent'
                WHEN friendships.status = 'pending' AND friendships.to_user_id = %s THEN 'request_received'
                ELSE 'none'
            END as friendship_status
        FROM users
        LEFT JOIN friendships ON (
            (friendships.from_user_id = %s AND friendships.to_user_id = users.id)
            OR
            (friendships.to_user_id = %s AND friendships.from_user_id = users.id)
        )
        WHERE LOWER(users.name) LIKE %s AND users.id != %s
        LIMIT 10
        """,
        (current_user_id, current_user_id, current_user_id, current_user_id, search, current_user_id),
    )

    users = [dict(row) for row in cursor.fetchall()]
    connection.close()
    return users
