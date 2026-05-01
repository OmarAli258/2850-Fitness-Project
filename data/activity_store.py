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


def get_activity(user_id, activity_id):
    for activity in all_activities:
        if activity["user_id"] == user_id and activity["id"] == activity_id:
            return activity
    return None


def update_activity(activity_id, user_id, activity_type, date, duration, distance, notes):
    activity = get_activity(user_id, activity_id)
    if activity is None:
        return None

    activity["type"] = activity_type
    activity["date"] = date
    activity["duration"] = duration
    activity["distance"] = distance
    activity["notes"] = notes
    return activity


def delete_activity(activity_id, user_id):
    global all_activities
    before_count = len(all_activities)
    all_activities = [
        activity for activity in all_activities
        if not (activity["user_id"] == user_id and activity["id"] == activity_id)
    ]
    return len(all_activities) < before_count


def get_activity_summary(user_id):
    activities = get_activities_for_user(user_id)
    total_duration = 0
    total_distance = 0.0
    type_counts = {}

    for activity in activities:
        if activity["duration"].isdigit():
            total_duration += int(activity["duration"])

        distance_match = re.search(r"([0-9]+(?:\.[0-9]+)?)", activity["distance"])
        if distance_match:
            total_distance += float(distance_match.group(1))

        type_counts[activity["type"]] = type_counts.get(activity["type"], 0) + 1

    favorite_type = "N/A"
    if type_counts:
        favorite_type = max(type_counts, key=type_counts.get)

    return {
        "total_workouts": len(activities),
        "total_duration": total_duration,
        "total_distance": round(total_distance, 1),
        "favorite_type": favorite_type,
    }
