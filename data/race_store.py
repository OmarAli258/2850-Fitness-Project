from data.database import get_connection


# inserts a new race row into the database for a specific user
def create_race(user_id, name, race_type, location, date, finish_time, is_pb, status):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO races (name, race_type, location, date, finish_time, is_pb, status, user_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (name, race_type, location, date, finish_time, is_pb, status, user_id)
    )
    connection.commit()
    connection.close()


# returns a list of all races belonging to a user, sorted by date
def get_races_for_user(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT * FROM races
        WHERE user_id = %s
        ORDER BY date ASC
        """,
        (user_id,)
    )
    rows = cursor.fetchall()
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

# deletes a race from the database, only if it belongs to the user
def delete_race(race_id, user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM races
        WHERE id = %s AND user_id = %s
        """,
        (race_id, user_id)
    )

    connection.commit()
    connection.close()

# counts how many total races, upcoming races, past races and PBs a user has
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
#function that auto sends races from upcoming to past when date passes
def update_race_statuses(user_id):
    from datetime import date
    today = str(date.today())

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE races
        SET status = 'past'
        WHERE user_id = %s AND status = 'upcoming' AND date < %s
        """,
        (user_id, today)
    )

    connection.commit()
    connection.close()
# fetches one race by id, used by the edit page
def get_race_by_id(race_id, user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM races WHERE id = %s AND user_id = %s",
        (race_id, user_id)
    )
    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    return {
        "id": row["id"],
        "name": row["name"],
        "race_type": row["race_type"],
        "location": row["location"],
        "date": row["date"],
        "finish_time": row["finish_time"],
        "is_pb": row["is_pb"],
        "status": row["status"],
        "user_id": row["user_id"]
    }
# updates an existing race with new info from the edit form
def update_race(race_id, user_id, name, race_type, location, date, finish_time, is_pb, status):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE races
        SET name = %s, race_type = %s, location = %s, date = %s,
            finish_time = %s, is_pb = %s, status = %s
        WHERE id = %s AND user_id = %s
        """,
        (name, race_type, location, date, finish_time, is_pb, status, race_id, user_id)
    )

    connection.commit()
    connection.close()
# get Pbs for current user and their friends, grouped by race type and length
def get_friends_pbs(user_id):
    from data import friends_store
    
    friend_ids = friends_store.get_friend_ids(user_id)
    all_user_ids = [user_id] + friend_ids
    
    if not all_user_ids:
        return {}
    
    connection = get_connection()
    cursor = connection.cursor()
    
    placeholders = ','.join(['%s'] * len(all_user_ids))
    
    cursor.execute(f"""
        SELECT races.name, races.race_type, races.finish_time, races.user_id, users.name as user_name
        FROM races
        JOIN users ON races.user_id = users.id
        WHERE races.user_id IN ({placeholders})
          AND races.is_pb = 1
          AND races.finish_time IS NOT NULL
          AND races.finish_time != ''
        ORDER BY races.finish_time ASC
    """, all_user_ids)
    
    rows = cursor.fetchall()
    connection.close()
    grouped = {}
    for row in rows:
        key = f"{row['name']} {row['race_type']}km"
        if key not in grouped:
            grouped[key] = []
        grouped[key].append({
            'user_name': row['user_name'],
            'finish_time': row['finish_time'],
            'is_you': row['user_id'] == user_id
        })
    return grouped