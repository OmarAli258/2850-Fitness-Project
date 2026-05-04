from data.database import get_connection


def _parse_time_to_seconds(finish_time):
    if not finish_time:
        return None
    parts = finish_time.strip().split(":")
    total = 0
    for p in parts:
        total = total * 60 + int(p)
    return total


def create_race(user_id, name, race_type, location, date, finish_time, is_pb, status):
    connection = get_connection()
    cursor = connection.cursor()

    if finish_time:
        new_time_seconds = _parse_time_to_seconds(finish_time)
        if new_time_seconds is not None:
            existing = cursor.execute(
                """
                SELECT id, finish_time FROM races
                WHERE user_id = ? AND race_type = ? AND is_pb = 1
                """,
                (user_id, race_type)
            ).fetchone()

            if existing:
                existing_seconds = _parse_time_to_seconds(existing["finish_time"])
                if existing_seconds is None or new_time_seconds < existing_seconds:
                    cursor.execute(
                        "UPDATE races SET is_pb = 0 WHERE user_id = ? AND race_type = ? AND is_pb = 1",
                        (user_id, race_type)
                    )
                    is_pb = 1
            else:
                is_pb = 1

    cursor.execute(
        """
        INSERT INTO races (name, race_type, location, date, finish_time, is_pb, status, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (name, race_type, location, date, finish_time, is_pb, status, user_id)
    )

    connection.commit()
    connection.close()


def get_races_for_user(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    rows = cursor.execute(
        """
        SELECT * FROM races
        WHERE user_id = ?
        ORDER BY date ASC
        """,
        (user_id,)
    ).fetchall()

    connection.close()

    races = []

    for row in rows:
        races.append({
            "id": row["id"],
            "name": row["name"],
            "race_type": row["race_type"],
            "location": row["location"],
            "date": row["date"],
            "finish_time": row["finish_time"],
            "is_pb": row["is_pb"],
            "status": row["status"],
            "user_id": row["user_id"]
        })

    return races


def get_personal_bests(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    rows = cursor.execute(
        """
        SELECT * FROM races
        WHERE user_id = ? AND is_pb = 1
        ORDER BY race_type ASC
        """,
        (user_id,)
    ).fetchall()

    connection.close()

    pbs = []
    for row in rows:
        pbs.append({
            "id": row["id"],
            "name": row["name"],
            "race_type": row["race_type"],
            "location": row["location"],
            "date": row["date"],
            "finish_time": row["finish_time"],
            "is_pb": row["is_pb"],
            "status": row["status"],
            "user_id": row["user_id"]
        })

    return pbs


def delete_race(race_id, user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM races
        WHERE id = ? AND user_id = ?
        """,
        (race_id, user_id)
    )

    connection.commit()
    connection.close()


def get_race_summary(user_id):
    races = get_races_for_user(user_id)

    total_races = len(races)
    upcoming_races = 0
    past_races = 0
    personal_bests = 0

    for race in races:
        if race["status"] == "upcoming":
            upcoming_races += 1

        if race["status"] == "past":
            past_races += 1

        if race["is_pb"] == 1:
            personal_bests += 1

    return {
        "total_races": total_races,
        "upcoming_races": upcoming_races,
        "past_races": past_races,
        "personal_bests": personal_bests
    }


def get_monthly_race_counts(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    rows = cursor.execute(
        """
        SELECT strftime('%%Y-%%m', date) as month, COUNT(*) as count
        FROM races
        WHERE user_id = ? AND status = 'past'
        GROUP BY month
        ORDER BY month DESC
        LIMIT 6
        """,
        (user_id,)
    ).fetchall()

    connection.close()

    months = []
    counts = []
    for row in rows:
        month_label = row["month"]
        if month_label:
            try:
                from datetime import datetime
                dt = datetime.strptime(month_label, "%Y-%m")
                month_label = dt.strftime("%b")
            except ValueError:
                pass
        months.append(month_label)
        counts.append(row["count"])

    months.reverse()
    counts.reverse()

    return {"labels": months, "data": counts}