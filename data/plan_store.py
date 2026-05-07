# this file handles saving, loading, updating, deleting and summarising plan data from the database
# it also handles sessions progress and consistency (adherence) records for plans
# note: we changed the user-facing word adherence because it was too complex for users
# we chose the simpler word consistency, but some code was already named adherence
# so consistency is the main word in comments, with adherence shown because the code still uses that label

# import uuid for unique ids, datetime for dates and get_connection for database access
import uuid
from datetime import datetime
from data.database import get_connection


# this function creates a new plan in the database and starts it as active
def create_plan(
    user_id, name, exercise_type, frequency, target_duration, target_distance, notes
):
    plan_id = str(uuid.uuid4())
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO plans (id, user_id, name, exercise_type, frequency, target_duration, target_distance, notes, created_at, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'active')
        """,
        (
            plan_id,
            user_id,
            name,
            exercise_type,
            frequency,
            int(target_duration) if target_duration else None,
            target_distance,
            notes,
            created_at,
        ),
    )

    connection.commit()
    connection.close()

    return {
        "id": plan_id,
        "user_id": user_id,
        "name": name,
        "exercise_type": exercise_type,
        "frequency": frequency,
        "target_duration": target_duration,
        "target_distance": target_distance,
        "notes": notes,
        "created_at": created_at,
        "status": "active",
    }


# this function gets all plans for a user, with optional filtering by status
def get_plans_for_user(user_id, status=None):
    connection = get_connection()
    cursor = connection.cursor()

    query = "SELECT * FROM plans WHERE user_id = %s"
    values = [user_id]

    if status:
        query += " AND status = %s"
        values.append(status)

    query += " ORDER BY created_at DESC"

    cursor.execute(query, values)
    rows = cursor.fetchall()
    connection.close()

    plans = []
    for row in rows:
        plans.append(
            {
                "id": row["id"],
                "user_id": row["user_id"],
                "name": row["name"],
                "exercise_type": row["exercise_type"],
                "frequency": row["frequency"],
                "target_duration": row["target_duration"],
                "target_distance": row["target_distance"],
                "notes": row["notes"],
                "created_at": row["created_at"],
                "status": row["status"],
            }
        )

    return plans


# this function gets only active plans for a user
def get_active_plans_for_user(user_id):
    return get_plans_for_user(user_id, status="active")


# this function gets one plan by id, but only if it belongs to the user
def get_plan(user_id, plan_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM plans WHERE user_id = %s AND id = %s", (user_id, plan_id)
    )
    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "name": row["name"],
        "exercise_type": row["exercise_type"],
        "frequency": row["frequency"],
        "target_duration": row["target_duration"],
        "target_distance": row["target_distance"],
        "notes": row["notes"],
        "created_at": row["created_at"],
        "status": row["status"],
    }


# this function updates an existing plan and can also update its status
def update_plan(
    plan_id,
    user_id,
    name,
    exercise_type,
    frequency,
    target_duration,
    target_distance,
    notes,
    status=None,
):
    connection = get_connection()
    cursor = connection.cursor()

    if status:
        cursor.execute(
            """
            UPDATE plans
            SET name = %s, exercise_type = %s, frequency = %s, target_duration = %s, target_distance = %s, notes = %s, status = %s
            WHERE id = %s AND user_id = %s
            """,
            (
                name,
                exercise_type,
                frequency,
                int(target_duration) if target_duration else None,
                target_distance,
                notes,
                status,
                plan_id,
                user_id,
            ),
        )
    else:
        cursor.execute(
            """
            UPDATE plans
            SET name = %s, exercise_type = %s, frequency = %s, target_duration = %s, target_distance = %s, notes = %s
            WHERE id = %s AND user_id = %s
            """,
            (
                name,
                exercise_type,
                frequency,
                int(target_duration) if target_duration else None,
                target_distance,
                notes,
                plan_id,
                user_id,
            ),
        )

    connection.commit()
    connection.close()


# this function deletes a plan and unlinks any activities that were connected to it
def delete_plan(plan_id, user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "UPDATE activities SET plan_id = NULL WHERE plan_id = %s AND user_id = %s",
        (plan_id, user_id),
    )

    cursor.execute(
        "DELETE FROM plans WHERE id = %s AND user_id = %s", (plan_id, user_id)
    )

    connection.commit()
    connection.close()


# this function calculates a plan's linked sessions, progress numbers and completed activities
def get_plan_completion(user_id, plan_id):
    plan = get_plan(user_id, plan_id)
    if plan is None:
        return None

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT * FROM activities
        WHERE user_id = %s AND plan_id = %s AND type = %s
        ORDER BY date DESC
        """,
        (user_id, plan_id, plan["exercise_type"]),
    )
    completed_activities = cursor.fetchall()

    connection.close()

    activities = []
    total_duration = 0
    for row in completed_activities:
        activity = {
            "id": row["id"],
            "type": row["type"],
            "date": row["date"],
            "duration": row["duration"],
            "distance": row["distance"],
            "notes": row["notes"],
        }
        activities.append(activity)
        total_duration += int(row["duration"])

    created_date = datetime.strptime(plan["created_at"], "%Y-%m-%d %H:%M:%S")
    now = datetime.now()
    days_since_created = max((now - created_date).days, 1)

    frequency = plan["frequency"].lower().strip()
    expected_sessions = _calculate_expected_sessions(frequency, days_since_created)
    frequency_target = _get_frequency_target(frequency)

    completion_rate = 0
    if expected_sessions > 0 and len(activities) > 0:
        completion_rate = min(
            100, round((len(activities) / expected_sessions) * 100, 1)
        )

    return {
        "plan": plan,
        "completed_count": len(activities),
        "expected_sessions": expected_sessions,
        "frequency_target": frequency_target,
        "completion_rate": completion_rate,
        "total_duration": total_duration,
        "activities": activities,
    }


# this function estimates expected sessions based on frequency and how long the plan has existed
def _calculate_expected_sessions(frequency, days):
    weeks = days / 7.0

    if frequency == "daily":
        return days
    elif frequency == "weekly":
        return int(weeks)
    elif frequency.startswith("every"):
        parts = frequency.split()
        if len(parts) >= 2:
            try:
                interval = int(parts[1])
                if "week" in parts[2] if len(parts) > 2 else "":
                    return int(weeks / interval)
                return int(days / interval)
            except (ValueError, IndexError):
                pass
    elif "per week" in frequency or "x week" in frequency:
        try:
            count = int(frequency.split("x")[0].strip())
            return int(weeks * count)
        except (ValueError, IndexError):
            pass
    elif "per month" in frequency:
        try:
            count = int(frequency.split("x")[0].strip())
            months = days / 30.0
            return int(months * count)
        except (ValueError, IndexError):
            pass
    else:
        try:
            count = int(frequency.split("x")[0].strip())
            if "week" in frequency:
                return int(weeks * count)
            elif "month" in frequency:
                months = days / 30.0
                return int(months * count)
        except (ValueError, IndexError):
            pass

    return int(weeks)


# this function gets the target session number directly from the plan frequency
def _get_frequency_target(frequency):
    if "x" in frequency:
        try:
            return int(frequency.split("x")[0].strip())
        except (ValueError, IndexError):
            pass
    elif frequency in ("daily", "weekly"):
        return 1
    return 1


# this function calculates summary numbers for all of a user's plans
def get_plan_summary(user_id):
    plans = get_plans_for_user(user_id)

    total_plans = len(plans)
    active_plans = sum(1 for p in plans if p["status"] == "active")
    paused_plans = sum(1 for p in plans if p["status"] == "paused")
    completed_plans = sum(1 for p in plans if p["status"] == "completed")

    total_activities_logged = 0

    for plan in plans:
        completion = get_plan_completion(user_id, plan["id"])
        if completion:
            total_activities_logged += completion["completed_count"]

    return {
        "total_plans": total_plans,
        "active_plans": active_plans,
        "paused_plans": paused_plans,
        "completed_plans": completed_plans,
        "total_activities_logged": total_activities_logged,
    }


# this function records a consistency (adherence) rating for a plan session
def record_adherence(user_id, plan_id, session_date, rating, notes):
    adherence_id = str(uuid.uuid4())
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO plan_adherence (id, user_id, plan_id, session_date, rating, notes, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (adherence_id, user_id, plan_id, session_date, int(rating), notes, created_at),
    )

    connection.commit()
    connection.close()

    return {
        "id": adherence_id,
        "plan_id": plan_id,
        "session_date": session_date,
        "rating": int(rating),
        "notes": notes,
        "created_at": created_at,
    }


# this function gets all consistency (adherence) records for one plan
def get_adherence_for_plan(user_id, plan_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT * FROM plan_adherence
        WHERE user_id = %s AND plan_id = %s
        ORDER BY session_date DESC
        """,
        (user_id, plan_id),
    )
    rows = cursor.fetchall()

    connection.close()

    records = []
    for row in rows:
        records.append(
            {
                "id": row["id"],
                "plan_id": row["plan_id"],
                "session_date": row["session_date"],
                "rating": row["rating"],
                "notes": row["notes"],
                "created_at": row["created_at"],
            }
        )

    return records


# this function calculates a consistency (adherence) summary for one plan
def get_adherence_summary(user_id, plan_id):
    records = get_adherence_for_plan(user_id, plan_id)

    if not records:
        return {
            "avg_rating": 0,
            "total_sessions": 0,
            "missed_sessions": 0,
            "on_track_sessions": 0,
            "excellent_sessions": 0,
        }

    total = len(records)
    avg_rating = round(sum(r["rating"] for r in records) / total, 1)
    missed = sum(1 for r in records if r["rating"] <= 2)
    on_track = sum(1 for r in records if r["rating"] == 3)
    excellent = sum(1 for r in records if r["rating"] >= 4)

    return {
        "avg_rating": avg_rating,
        "total_sessions": total,
        "missed_sessions": missed,
        "on_track_sessions": on_track,
        "excellent_sessions": excellent,
    }


# this function deletes one consistency (adherence) record from the database
def delete_adherence(adherence_id, user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM plan_adherence WHERE id = %s AND user_id = %s",
        (adherence_id, user_id),
    )

    connection.commit()
    connection.close()


# done comments for data/plan_store.py
# summary of comments:
# - create_plan adds a new training plan to the database with name, exercise type, frequency and optional targets
# - get_plans_for_user retrieves all plans for the logged in user with optional status filter
# - get_one_plan fetches a single plan by its unique id
# - update_plan saves changes to an existing plan like name, exercise type or status
# - delete_plan removes a plan from the database permanently
# - get_plan_summary calculates total plans and active plans counts for the plans page
# - record_consistency lets users rate how well they followed the plan after each session
# - get_consistency_records fetches all recorded ratings for one plan with dates
# - get_consistency_summary totals up all consistency ratings for the plan detail page
# - delete_consistency removes one consistency record from the database
# note: consistency is the user friendly word we use because it is easier to understand
# the code still uses adherence in some function and variable names from the original implementation
