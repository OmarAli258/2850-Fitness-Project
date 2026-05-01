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


def get_activity_by_id(activity_id, user_id):
    for activity in all_activities:
        if activity["id"] == activity_id and activity["user_id"] == user_id:
            return activity
    return None


def update_activity(activity_id, user_id, activity_type, date, duration, distance, notes):
    for activity in all_activities:
        if activity["id"] == activity_id and activity["user_id"] == user_id:
            activity["type"] = activity_type
            activity["date"] = date
            activity["duration"] = duration
            activity["distance"] = distance
            activity["notes"] = notes
            return True
    return False


def delete_activity(activity_id, user_id):
    for i, activity in enumerate(all_activities):
        if activity["id"] == activity_id and activity["user_id"] == user_id:
            del all_activities[i]
            return True
    return False