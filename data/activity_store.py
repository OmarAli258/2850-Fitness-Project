#this file handles saving, loading, updating, deleting and summarising activity data from the database
#its used by the activity routes, dashboard and search features

#import uuid for unique activity ids and get connection for database access
import uuid
from data.database import get_connection

ACTIVITY_TYPES = ["Running", "Walking", "Cycling", "Swimming", "Weightlifting", "Crossfit", "Football", "Yoga", "Hiking", "Rowing"]


#this function creates new activity in  atabase and returns saved activity data
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


#this function gets all activities for user, with optional type filtering and search
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
        query += " AND (LOWER(type) LIKE %s OR LOWER(notes) LIKE %s)"
        search_text = f"%{search.lower()}%"
        values.extend([search_text, search_text])

    query += " ORDER BY date DESC"

    cursor.execute(query, values)
    rows = cursor.fetchall()
    connection.close()

    activities = []

    for row in rows:
        #this checks if plan id exists in the row so older databases do not break
        plan_id = row["plan_id"] if "plan_id" in row.keys() else None
        #this checks if is public exists in the row so older databases do not break
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


#this function gets one activity by id, but only if it belongs to the user
def get_activity(user_id, activity_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT * FROM activities
        WHERE user_id = %s AND id = %s
        """,
        (user_id, activity_id)
    )
    row = cursor.fetchone()

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


#this function updates an existing activity for the logged in user
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


#this function deletes an activity from the database if it belongs to the user
def delete_activity(activity_id, user_id):
    connection = get_connection()
    cursor = connection.cursor()

    #this checks ownership first, then clears feed likes and comments before deleting the activity
    cursor.execute(
        """
        SELECT id FROM activities
        WHERE id = %s AND user_id = %s
        """,
        (activity_id, user_id)
    )

    if cursor.fetchone() is None:
        connection.close()
        return

    cursor.execute(
        """
        DELETE FROM activity_likes
        WHERE activity_id = %s
        """,
        (activity_id,)
    )

    cursor.execute(
        """
        DELETE FROM activity_comments
        WHERE activity_id = %s
        """,
        (activity_id,)
    )

    cursor.execute(
        """
        DELETE FROM activities
        WHERE id = %s AND user_id = %s
        """,
        (activity_id, user_id)
    )

    connection.commit()
    connection.close()


#this function calculates dashboard summary numbers from the users past activities
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


#this function prepares the last 7 days of activity data for dashboard charts
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


#this function gets this weeks workout, minute and distance totals for each day
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


#this function counts how many activities the user has for each activity type
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


#this function searches the user's activities and limits the number of results shown
def search_activities(user_id, query, limit=10):
    if not query or not query.strip():
        return []

    activities = get_activities_for_user(user_id, search=query.strip())
    return activities[:limit]

#done comments for data/activity_store.py
#summary of comments:
# - create_activity adds a new workout to the database with type, date, duration and optional distance
# - get_activities_for_user retrieves all workouts for the logged in user with optional search and type filters
# - get_one_activity fetches a single activity by its unique id
# - update_activity saves changes to an existing workout like duration or distance
# - delete_activity removes an activity from the database permanently
# - get_activity_summary calculates totals for workouts, minutes, distance and favourite activity type
# - get_chart_data prepares activity data formatted for the dashboard chart display
# - search_activities provides quick search results for the search dropdown
