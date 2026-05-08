"""
Seed script to populate the database with sample data for testing
Run with: python seed_data.py
"""
import os
from dotenv import load_dotenv
load_dotenv()

import uuid
from datetime import datetime, timedelta
from data.database import get_connection
from werkzeug.security import generate_password_hash

def create_users(cursor):
    """Create sample users"""
    users = [
        {"id": str(uuid.uuid4()), "name": "Justin Doe", "email": "justin@example.com", "password": "Password123!"},
        {"id": str(uuid.uuid4()), "name": "Sofia Garcia", "email": "sofia@example.com", "password": "Password123!"},
        {"id": str(uuid.uuid4()), "name": "Layla Smith", "email": "layla@example.com", "password": "Password123!"},
        {"id": str(uuid.uuid4()), "name": "Keith Johnson", "email": "keith@example.com", "password": "Password123!"},
        {"id": str(uuid.uuid4()), "name": "Noah Williams", "email": "noah@example.com", "password": "Password123!"},
    ]

    for user in users:
        cursor.execute("""
            INSERT INTO users (id, name, email, password)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (email) DO NOTHING
        """, (user["id"], user["name"], user["email"], generate_password_hash(user["password"])))

    return {u["email"]: u["id"] for u in users}


def create_activities(cursor, user_ids):
    """Create sample activities"""
    activities = []
    base_date = datetime.now()

    activity_types = [
        {"type": "Running", "duration": 30, "distance": "5.2"},
        {"type": "Cycling", "duration": 60, "distance": "25.0"},
        {"type": "Gym", "duration": 45, "distance": None},
        {"type": "Swimming", "duration": 40, "distance": "1.5"},
        {"type": "Yoga", "duration": 30, "distance": None},
        {"type": "Hiking", "duration": 120, "distance": "12.0"},
        {"type": "Walking", "duration": 20, "distance": "2.0"},
    ]

    user_list = list(user_ids.values())
    for i in range(25):
        user = user_list[i % len(user_list)]
        activity = activity_types[i % len(activity_types)]
        date = (base_date - timedelta(days=i)).strftime("%Y-%m-%d")

        activities.append({
            "id": str(uuid.uuid4()),
            "user_id": user,
            "type": activity["type"],
            "date": date,
            "duration": activity["duration"] + (i % 30),
            "distance": activity["distance"],
            "notes": f"Great {activity['type'].lower()} session! Feeling good.",
            "is_public": 1 if i % 3 != 0 else 0,
        })

    for act in activities:
        cursor.execute("""
            INSERT INTO activities (id, user_id, type, date, duration, distance, notes, is_public)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (act["id"], act["user_id"], act["type"], act["date"], act["duration"], act["distance"], act["notes"], act["is_public"]))

    return activities


def create_likes(cursor, activities, user_ids):
    """Create sample likes"""
    user_list = list(user_ids.values())

    for i, activity in enumerate(activities[:15]):
        for user in user_list[:2]:
            try:
                cursor.execute("""
                    INSERT INTO activity_likes (id, activity_id, user_id, created_at)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (str(uuid.uuid4()), activity["id"], user, datetime.utcnow().isoformat()))
            except:
                pass


def create_comments(cursor, activities, user_ids):
    """Create sample comments"""
    user_list = list(user_ids.values())

    comments_text = [
        "Great workout! 💪",
        "Keep it up!",
        "That's impressive!",
        "Nice work!",
        "Looking strong!",
    ]

    for i, activity in enumerate(activities[:10]):
        for j, user in enumerate(user_list[:2]):
            try:
                cursor.execute("""
                    INSERT INTO activity_comments (id, activity_id, user_id, body, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (str(uuid.uuid4()), activity["id"], user, comments_text[j % len(comments_text)], datetime.utcnow().isoformat()))
            except:
                pass


def create_plans(cursor, user_ids):
    """Create sample exercise plans"""
    user_list = list(user_ids.values())

    plans = [
        {"user_id": user_list[0], "name": "Morning Runs", "exercise_type": "Running", "frequency": "3x per week", "target_duration": 30},
        {"user_id": user_list[1], "name": "Yoga Flow", "exercise_type": "Yoga", "frequency": "2x per week", "target_duration": 45},
        {"user_id": user_list[2], "name": "Strength Training", "exercise_type": "Gym", "frequency": "4x per week", "target_duration": 60},
        {"user_id": user_list[3], "name": "Triathlon Prep", "exercise_type": "Cycling", "frequency": "5x per week", "target_duration": 90},
    ]

    for plan in plans:
        cursor.execute("""
            INSERT INTO plans (id, user_id, name, exercise_type, frequency, target_duration, notes, created_at, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (str(uuid.uuid4()), plan["user_id"], plan["name"], plan["exercise_type"], plan["frequency"], plan["target_duration"], "My training plan", datetime.utcnow().isoformat(), "active"))


def create_races(cursor, user_ids):
    """Create sample races"""
    user_list = list(user_ids.values())

    races = [
        {"user_id": user_list[3], "name": "Spring Marathon", "race_type": "Running", "location": "London", "date": "2026-04-15", "finish_time": "03:45:00", "is_pb": 1, "status": "completed"},
        {"user_id": user_list[3], "name": "Summer Triathlon", "race_type": "Triathlon", "location": "Brighton", "date": "2026-06-20", "status": "upcoming"},
        {"user_id": user_list[0], "name": "Charity 5K", "race_type": "Running", "location": "Manchester", "date": "2026-05-10", "status": "upcoming"},
    ]

    for race in races:
        cursor.execute("""
            INSERT INTO races (name, race_type, location, date, finish_time, is_pb, status, user_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (race["name"], race["race_type"], race["location"], race["date"], race.get("finish_time"), race.get("is_pb", 0), race["status"], race["user_id"]))


def create_friendships(cursor, user_ids):
    """Create sample friendships"""
    user_list = list(user_ids.values())

    friendships = [
        (user_list[0], user_list[1]),
        (user_list[1], user_list[0]),
        (user_list[2], user_list[3]),
        (user_list[3], user_list[2]),
        (user_list[0], user_list[4]),
        (user_list[4], user_list[0]),
    ]

    for frm, to in friendships:
        try:
            cursor.execute("""
                INSERT INTO friendships (from_user_id, to_user_id, status)
                VALUES (%s, %s, 'accepted')
                ON CONFLICT DO NOTHING
            """, (frm, to))
        except:
            pass


def main():
    print("Seeding database...")
    connection = get_connection()
    cursor = connection.cursor()

    # Clear existing seed data (optional - remove if you want to keep existing data)
    print("Clearing existing seed data...")
    cursor.execute("DELETE FROM activity_comments")
    cursor.execute("DELETE FROM activity_likes")
    cursor.execute("DELETE FROM plan_adherence")
    cursor.execute("DELETE FROM activities")
    cursor.execute("DELETE FROM friendships")
    cursor.execute("DELETE FROM races")
    cursor.execute("DELETE FROM plans")
    cursor.execute("DELETE FROM users")
    connection.commit()

    print("Creating users...")
    user_ids = create_users(cursor)
    connection.commit()
    print(f"Created {len(user_ids)} users")

    print("Creating activities...")
    activities = create_activities(cursor, user_ids)
    connection.commit()
    print(f"Created {len(activities)} activities")

    print("Creating likes...")
    create_likes(cursor, activities, user_ids)
    connection.commit()

    print("Creating comments...")
    create_comments(cursor, activities, user_ids)
    connection.commit()

    print("Creating plans...")
    create_plans(cursor, user_ids)
    connection.commit()

    print("Creating races...")
    create_races(cursor, user_ids)
    connection.commit()

    print("Creating friendships...")
    create_friendships(cursor, user_ids)
    connection.commit()

    connection.close()
    print("\n[OK] Database seeded successfully!")
    print("\nTest accounts:")
    print("  Email: justin@example.com  |  Password: Password123!")
    print("  Email: sofia@example.com  |  Password: Password123!")
    print("  Email: layla@example.com   |  Password: Password123!")
    print("  Email: keith@example.com   |  Password: Password123!")
    print("  Email: noah@example.com    |  Password: Password123!")


if __name__ == "__main__":
    main()