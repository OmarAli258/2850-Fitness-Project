from data.database import get_connection


def create_race(user_id, name, race_type, location, date, finish_time, is_pb, status):
    connection = get_connection()
    cursor = connection.cursor()

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