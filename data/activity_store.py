import uuid
from data.database import get_connection

ACTIVITY_TYPES = ["Running", "Walking", "Cycling", "Swimming", "Weightlifting", "Crossfit", "Football", "Yoga", "Hiking", "Rowing", "Gym", "Weights"]


def create_activity(user_id, activity_type, date, duration, distance, notes, route_data=None, is_public=0, plan_id=None):
    activity_id = str(uuid.uuid4())

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO activities (id, user_id, type, date, duration, distance, notes, route_data, is_public, plan_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (activity_id, user_id, activity_type, date, int(duration), distance, notes, route_data, is_public, plan_id)
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
        "is_public": is_public,
        "plan_id": plan_id
    }


def get_activities_for_user(user_id, activity_type=None, search=None):
    connection = get_connection()
    cursor = connection.cursor()

    query = """
        SELECT * FROM activities
        WHERE user_id = %s
    """

    values = [user_id]

    if activity_type:
        query += " AND type = %s"
        values.append(activity_type)

    if search:
        query += " AND (type LIKE %s OR date LIKE %s OR notes LIKE %s)"
        search_text = f"%{search}%"
        values.extend([search_text, search_text, search_text])

    query += " ORDER BY date DESC"

    rows = cursor.execute(query, values).fetchall()
    connection.close()

    activities = []

    for row in rows:
        # Check if plan_id exists in the row (for backward compatibility if schema hasn't updated yet)
        plan_id = row["plan_id"] if "plan_id" in row.keys() else None
        # Same for is_public
        is_public = row["is_public"] if "is_public" in row.keys() else 0
        
        activities.append({
            "id": row["id"],
            "user_id": row["user_id"],
            "type": row["type"],
            "date": row["date"],
            "duration": row["duration"],
            "distance": row["distance"],
            "notes": row["notes"],
            "route_data": row["route_data"],
            "is_public": is_public,
            "plan_id": plan_id
        })

    return activities


def get_activity(user_id, activity_id):
    connection = get_connection()
    cursor = connection.cursor()

    row = cursor.execute(
        """
        SELECT * FROM activities
        WHERE user_id = %s AND id = %s
        """,
        (user_id, activity_id)
    ).fetchone()

    connection.close()

    if row is None:
        return None

    plan_id = row["plan_id"] if "plan_id" in row.keys() else None
    is_public = row["is_public"] if "is_public" in row.keys() else 0

    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "type": row["type"],
        "date": row["date"],
        "duration": row["duration"],
        "distance": row["distance"],
        "notes": row["notes"],
        "route_data": row["route_data"],
        "is_public": is_public,
        "plan_id": plan_id
    }


def update_activity(activity_id, user_id, activity_type, date, duration, distance, notes, is_public=0, plan_id=None):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE activities
        SET type = %s, date = %s, duration = %s, distance = %s, notes = %s, is_public = %s, plan_id = %s
        WHERE id = %s AND user_id = %s
        """,
        (activity_type, date, int(duration), distance, notes, is_public, plan_id, activity_id, user_id)
    )

    connection.commit()
    connection.close()


def delete_activity(activity_id, user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM activities
        WHERE id = %s AND user_id = %s
        """,
        (activity_id, user_id)
    )

    connection.commit()
    connection.close()

def get_activity_summary(user_id):
    from datetime import date

    activities = get_activities_for_user(user_id)
    today_str = date.today().isoformat()

    total_workouts = 0
    total_minutes = 0
    total_distance = 0.0
    activity_counts = {}

    for activity in activities:
        if activity["date"] > today_str:
            continue
        total_workouts += 1
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
            WHERE user_id = %s AND date = %s
            """,
            (user_id, date_str)
        ).fetchone()

        dist_row = cursor.execute(
            """
            SELECT distance FROM activities
            WHERE user_id = %s AND date = %s AND distance IS NOT NULL AND distance != ''
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

def search_activities(user_id, query, limit=10):
    if not query or not query.strip():
        return []

    activities = get_activities_for_user(user_id, search=query.strip())
    return activities[:limit]
