import uuid
from data.database import get_connection

ACTIVITY_TYPES = ["Running", "Walking", "Cycling", "Swimming", "Gym"]


def create_activity(user_id, activity_type, date, duration, distance, notes):
    activity_id = str(uuid.uuid4())

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO activities (id, user_id, type, date, duration, distance, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (activity_id, user_id, activity_type, date, int(duration), distance, notes)
    )

    connection.commit()
    connection.close()

    return {
        "id": activity_id,
        "user_id": user_id,
        "type": activity_type,
        "date": date,
        "duration": int(duration),
        "distance": distance,
        "notes": notes
    }


def get_activities_for_user(user_id, activity_type=None, search=None):
    connection = get_connection()
    cursor = connection.cursor()

    query = """
        SELECT * FROM activities
        WHERE user_id = ?
    """

    values = [user_id]

    if activity_type:
        query += " AND type = ?"
        values.append(activity_type)

    if search:
        query += " AND (type LIKE ? OR date LIKE ? OR notes LIKE ?)"
        search_text = f"%{search}%"
        values.extend([search_text, search_text, search_text])

    query += " ORDER BY date DESC"

    rows = cursor.execute(query, values).fetchall()
    connection.close()

    activities = []

    for row in rows:
        activities.append({
            "id": row["id"],
            "user_id": row["user_id"],
            "type": row["type"],
            "date": row["date"],
            "duration": row["duration"],
            "distance": row["distance"],
            "notes": row["notes"]
        })

    return activities


def get_activity(user_id, activity_id):
    connection = get_connection()
    cursor = connection.cursor()

    row = cursor.execute(
        """
        SELECT * FROM activities
        WHERE user_id = ? AND id = ?
        """,
        (user_id, activity_id)
    ).fetchone()

    connection.close()

    if row is None:
        return None

    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "type": row["type"],
        "date": row["date"],
        "duration": row["duration"],
        "distance": row["distance"],
        "notes": row["notes"]
    }


def update_activity(activity_id, user_id, activity_type, date, duration, distance, notes):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE activities
        SET type = ?, date = ?, duration = ?, distance = ?, notes = ?
        WHERE id = ? AND user_id = ?
        """,
        (activity_type, date, int(duration), distance, notes, activity_id, user_id)
    )

    connection.commit()
    connection.close()


def delete_activity(activity_id, user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM activities
        WHERE id = ? AND user_id = ?
        """,
        (activity_id, user_id)
    )

    connection.commit()
    connection.close()


def get_activity_summary(user_id):
    activities = get_activities_for_user(user_id)

    total_workouts = len(activities)
    total_minutes = 0
    total_distance = 0.0
    activity_counts = {}

    for activity in activities:
        total_minutes += int(activity["duration"])

        activity_type = activity["type"]

        if activity_type in activity_counts:
            activity_counts[activity_type] += 1
        else:
            activity_counts[activity_type] = 1

        distance = activity["distance"]

        if distance:
            try:
                total_distance += float(distance)
            except ValueError:
                pass

    favorite_activity = "None yet"

    if activity_counts:
        favorite_activity = max(activity_counts, key=activity_counts.get)

    return {
        "total_workouts": total_workouts,
        "total_minutes": total_minutes,
        "total_distance": round(total_distance, 2),
        "favorite_activity": favorite_activity
    }