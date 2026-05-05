import uuid
from data.database import get_connection

ACTIVITY_TYPES = ["Running", "Walking", "Cycling", "Swimming", "Weightlifitng","Crossfit","Football","Yoga","Hiking","Rowing"]


def create_activity(user_id, activity_type, date, duration, distance, notes, route_data=None):
    activity_id = str(uuid.uuid4())

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO activities (id, user_id, type, date, duration, distance, notes, route_data)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (activity_id, user_id, activity_type, date, int(duration), distance, notes, route_data)
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
            "notes": row["notes"],
            "route_data": row["route_data"]
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
        "route_data": row["route_data"]
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
#function for gettings statistics data
def get_chart_data(user_id):
    from datetime import date, timedelta

    activities = get_activities_for_user(user_id)

    today = date.today()
    days = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
    day_labels = [d.strftime("%a") for d in days]
    day_strings = [d.strftime("%Y-%m-%d") for d in days]

    workouts_per_day = [0] * 7
    minutes_per_day = [0] * 7
    distance_per_day = [0.0] * 7
    type_counts = {}

    for activity in activities:
        if activity["date"] in day_strings:
            index = day_strings.index(activity["date"])
            workouts_per_day[index] += 1
            minutes_per_day[index] += int(activity["duration"])
            if activity["distance"]:
                try:
                    distance_per_day[index] += float(activity["distance"])
                except ValueError:
                    pass

        activity_type = activity["type"]
        if activity_type in type_counts:
            type_counts[activity_type] += 1
        else:
            type_counts[activity_type] = 1

    return {
        "labels": day_labels,
        "workouts": workouts_per_day,
        "minutes": minutes_per_day,
        "distance": [round(d, 2) for d in distance_per_day],
        "type_labels": list(type_counts.keys()),
        "type_counts": list(type_counts.values())
    }