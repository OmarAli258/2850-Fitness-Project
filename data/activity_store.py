import uuid
from data.database import get_connection

ACTIVITY_TYPES = ["Running", "Walking", "Cycling", "Swimming", "Gym", "Weights"]


def create_activity(user_id, activity_type, date, duration, distance, notes, route_data=None, plan_id=None):
    activity_id = str(uuid.uuid4())

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO activities (id, user_id, type, date, duration, distance, notes, route_data, plan_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (activity_id, user_id, activity_type, date, int(duration), distance, notes, route_data, plan_id)
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
        "notes": notes,
        "plan_id": plan_id,
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
            "notes": row["notes"],
            "route_data": row["route_data"],
            "plan_id": row["plan_id"],
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
        "notes": row["notes"],
        "route_data": row["route_data"],
        "plan_id": row["plan_id"],
    }


def update_activity(activity_id, user_id, activity_type, date, duration, distance, notes, plan_id=None):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE activities
        SET type = ?, date = ?, duration = ?, distance = ?, notes = ?, plan_id = ?
        WHERE id = ? AND user_id = ?
        """,
        (activity_type, date, int(duration), distance, notes, plan_id, activity_id, user_id)
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


def get_weekly_activity_data(user_id):
    from datetime import datetime, timedelta

    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())

    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    workouts = [0] * 7
    minutes = [0] * 7
    distances = [0.0] * 7

    for i in range(7):
        day = start_of_week + timedelta(days=i)
        date_str = day.strftime("%Y-%m-%d")

        connection = get_connection()
        cursor = connection.cursor()

        row = cursor.execute(
            """
            SELECT COUNT(*) as count, COALESCE(SUM(duration), 0) as total_min
            FROM activities
            WHERE user_id = ? AND date = ?
            """,
            (user_id, date_str)
        ).fetchone()

        dist_row = cursor.execute(
            """
            SELECT distance FROM activities
            WHERE user_id = ? AND date = ? AND distance IS NOT NULL AND distance != ''
            """,
            (user_id, date_str)
        ).fetchall()

        connection.close()

        workouts[i] = row["count"]
        minutes[i] = row["total_min"]

        for d in dist_row:
            try:
                distances[i] += float(d["distance"])
            except (ValueError, TypeError):
                pass

    return {
        "labels": days,
        "workouts": workouts,
        "minutes": minutes,
        "distances": [round(d, 2) for d in distances]
    }


def get_activity_type_counts(user_id):
    activities = get_activities_for_user(user_id)

    counts = {}
    for activity in activities:
        t = activity["type"]
        if t in counts:
            counts[t] += 1
        else:
            counts[t] = 1

    labels = list(counts.keys())
    data = list(counts.values())

    return {"labels": labels, "data": data}


def get_chart_data(user_id):
    from datetime import datetime, timedelta

    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    workouts = [0] * 7
    minutes = [0] * 7
    distance = [0.0] * 7

    for i in range(7):
        day = start_of_week + timedelta(days=i)
        date_str = day.strftime("%Y-%m-%d")

        connection = get_connection()
        cursor = connection.cursor()

        row = cursor.execute(
            """
            SELECT COUNT(*) as count, COALESCE(SUM(duration), 0) as total_min
            FROM activities
            WHERE user_id = ? AND date = ?
            """,
            (user_id, date_str)
        ).fetchone()

        dist_row = cursor.execute(
            """
            SELECT distance FROM activities
            WHERE user_id = ? AND date = ? AND distance IS NOT NULL AND distance != ''
            """,
            (user_id, date_str)
        ).fetchall()

        connection.close()

        workouts[i] = row["count"]
        minutes[i] = row["total_min"]

        for d in dist_row:
            try:
                distance[i] += float(d["distance"])
            except (ValueError, TypeError):
                pass

    activities = get_activities_for_user(user_id)
    type_counts = {}
    for a in activities:
        t = a["type"]
        type_counts[t] = type_counts.get(t, 0) + 1

    return {
        "labels": days,
        "workouts": workouts,
        "minutes": minutes,
        "distance": [round(d, 2) for d in distance],
        "type_labels": list(type_counts.keys()),
        "type_counts": list(type_counts.values()),
    }