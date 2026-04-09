import uuid

# This list keeps all activities for now
all_activities = []


def create_activity(user_id, activity_type, date, duration, distance, notes):
    activity = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "type": activity_type,
        "date": date,
        "duration": duration,
        "distance": distance,
        "notes": notes
    }

    all_activities.append(activity)
    return activity


def get_activities_for_user(user_id):
    results = []

    for activity in all_activities:
        if activity["user_id"] == user_id:
            results.append(activity)

    return results