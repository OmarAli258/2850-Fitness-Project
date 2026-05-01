import re
import uuid

ACTIVITY_TYPES = [
    "Running",
    "Walking",
    "Cycling",
    "Swimming",
    "Gym",
    "Yoga",
    "Hiking",
    "Rowing",
]

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
        "notes": notes,
    }

    all_activities.append(activity)
    return activity


def get_activities_for_user(user_id, activity_type=None, search=None):
    results = []

    for activity in all_activities:
        if activity["user_id"] != user_id:
            continue

        if activity_type and activity["type"] != activity_type:
            continue

        if search:
            lower_search = search.lower()
            fields = " ".join([
                activity["type"],
                activity["date"],
                activity["distance"],
                activity["notes"],
            ]).lower()
            if lower_search not in fields:
                continue

        results.append(activity)

    results.sort(key=lambda item: item["date"], reverse=True)
    return results