import uuid
from datetime import datetime
from data.database import get_connection


def create_plan(user_id, name, exercise_type, frequency, target_duration, target_distance, notes):
    plan_id = str(uuid.uuid4())
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO plans (id, user_id, name, exercise_type, frequency, target_duration, target_distance, notes, created_at, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')
        """,
        (plan_id, user_id, name, exercise_type, frequency, int(target_duration) if target_duration else None, target_distance, notes, created_at)
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
        "status": "active"
    }


def get_plans_for_user(user_id, status=None):
    connection = get_connection()
    cursor = connection.cursor()

    query = "SELECT * FROM plans WHERE user_id = ?"
    values = [user_id]

    if status:
        query += " AND status = ?"
        values.append(status)

    query += " ORDER BY created_at DESC"

    rows = cursor.execute(query, values).fetchall()
    connection.close()

    plans = []
    for row in rows:
        plans.append({
            "id": row["id"],
            "user_id": row["user_id"],
            "name": row["name"],
            "exercise_type": row["exercise_type"],
            "frequency": row["frequency"],
            "target_duration": row["target_duration"],
            "target_distance": row["target_distance"],
            "notes": row["notes"],
            "created_at": row["created_at"],
            "status": row["status"]
        })

    return plans


def get_active_plans_for_user(user_id):
    return get_plans_for_user(user_id, status="active")


def get_plan(user_id, plan_id):
    connection = get_connection()
    cursor = connection.cursor()

    row = cursor.execute(
        "SELECT * FROM plans WHERE user_id = ? AND id = ?",
        (user_id, plan_id)
    ).fetchone()

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
        "status": row["status"]
    }


def update_plan(plan_id, user_id, name, exercise_type, frequency, target_duration, target_distance, notes, status=None):
    connection = get_connection()
    cursor = connection.cursor()

    if status:
        cursor.execute(
            """
            UPDATE plans
            SET name = ?, exercise_type = ?, frequency = ?, target_duration = ?, target_distance = ?, notes = ?, status = ?
            WHERE id = ? AND user_id = ?
            """,
            (name, exercise_type, frequency, int(target_duration) if target_duration else None, target_distance, notes, status, plan_id, user_id)
        )
    else:
        cursor.execute(
            """
            UPDATE plans
            SET name = ?, exercise_type = ?, frequency = ?, target_duration = ?, target_distance = ?, notes = ?
            WHERE id = ? AND user_id = ?
            """,
            (name, exercise_type, frequency, int(target_duration) if target_duration else None, target_distance, notes, plan_id, user_id)
        )

    connection.commit()
    connection.close()


def delete_plan(plan_id, user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "UPDATE activities SET plan_id = NULL WHERE plan_id = ? AND user_id = ?",
        (plan_id, user_id)
    )

    cursor.execute(
        "DELETE FROM plans WHERE id = ? AND user_id = ?",
        (plan_id, user_id)
    )

    connection.commit()
    connection.close()


def get_plan_completion(user_id, plan_id):
    plan = get_plan(user_id, plan_id)
    if plan is None:
        return None

    connection = get_connection()
    cursor = connection.cursor()

    completed_activities = cursor.execute(
        """
        SELECT * FROM activities
        WHERE user_id = ? AND plan_id = ? AND type = ?
        ORDER BY date DESC
        """,
        (user_id, plan_id, plan["exercise_type"])
    ).fetchall()

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
            "notes": row["notes"]
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
        completion_rate = min(100, round((len(activities) / expected_sessions) * 100, 1))

    return {
        "plan": plan,
        "completed_count": len(activities),
        "expected_sessions": expected_sessions,
        "frequency_target": frequency_target,
        "completion_rate": completion_rate,
        "total_duration": total_duration,
        "activities": activities
    }


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


def _get_frequency_target(frequency):
    if "x" in frequency:
        try:
            return int(frequency.split("x")[0].strip())
        except (ValueError, IndexError):
            pass
    elif frequency in ("daily", "weekly"):
        return 1
    return 1


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
        "total_activities_logged": total_activities_logged
    }


def record_adherence(user_id, plan_id, session_date, rating, notes):
    adherence_id = str(uuid.uuid4())
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO plan_adherence (id, user_id, plan_id, session_date, rating, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (adherence_id, user_id, plan_id, session_date, int(rating), notes, created_at)
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


def get_adherence_for_plan(user_id, plan_id):
    connection = get_connection()
    cursor = connection.cursor()

    rows = cursor.execute(
        """
        SELECT * FROM plan_adherence
        WHERE user_id = ? AND plan_id = ?
        ORDER BY session_date DESC
        """,
        (user_id, plan_id)
    ).fetchall()

    connection.close()

    records = []
    for row in rows:
        records.append({
            "id": row["id"],
            "plan_id": row["plan_id"],
            "session_date": row["session_date"],
            "rating": row["rating"],
            "notes": row["notes"],
            "created_at": row["created_at"],
        })

    return records


def get_adherence_summary(user_id, plan_id):
    records = get_adherence_for_plan(user_id, plan_id)

    if not records:
        return {"avg_rating": 0, "total_sessions": 0, "missed_sessions": 0, "on_track_sessions": 0, "excellent_sessions": 0}

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


def delete_adherence(adherence_id, user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM plan_adherence WHERE id = ? AND user_id = ?",
        (adherence_id, user_id)
    )

    connection.commit()
    connection.close()
