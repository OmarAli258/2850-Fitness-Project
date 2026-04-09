from flask import Blueprint, request, session, redirect
from data import activity_store

activities = Blueprint("activities", __name__)


@activities.route("/activities/new", methods=["GET"])
def show_activity_form():
    if "user_id" not in session:
        return redirect("/login")

    return activity_form()


@activities.route("/activities/new", methods=["POST"])
def save_activity():
    if "user_id" not in session:
        return redirect("/login")

    activity_type = request.form.get("activity_type", "").strip()
    date = request.form.get("date", "").strip()
    duration = request.form.get("duration", "").strip()
    distance = request.form.get("distance", "").strip()
    notes = request.form.get("notes", "").strip()

    if activity_type == "":
        return activity_form(error="Please choose an activity type.")

    if date == "":
        return activity_form(error="Please choose a date.")

    if duration == "":
        return activity_form(error="Please enter the duration.")

    if not duration.isdigit():
        return activity_form(error="Duration must be a number.")

    activity_store.create_activity(
        user_id=session["user_id"],
        activity_type=activity_type,
        date=date,
        duration=duration,
        distance=distance,
        notes=notes
    )

    return redirect("/activities")


@activities.route("/activities", methods=["GET"])
def show_activities():
    if "user_id" not in session:
        return redirect("/login")

    user_name = session.get("user_name", "User")
    activities_list = activity_store.get_activities_for_user(session["user_id"])

    activity_html = ""

    if len(activities_list) == 0:
        activity_html = """
        <p>No activities yet.</p>
        <a href="/activities/new">Log your first workout</a>
        """
    else:
        for activity in reversed(activities_list):
            distance = activity["distance"]
            notes = activity["notes"]

            if distance == "":
                distance = "Not given"

            if notes == "":
                notes = "No notes"

            activity_html += f"""
            <div style="border:1px solid black; padding:15px; margin-bottom:15px; border-radius:10px;">
                <h3>{activity["type"]}</h3>
                <p><strong>Date:</strong> {activity["date"]}</p>
                <p><strong>Duration:</strong> {activity["duration"]} minutes</p>
                <p><strong>Distance:</strong> {distance}</p>
                <p><strong>Notes:</strong> {notes}</p>
            </div>
            """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>FitTrack | Activities</title>
        <link rel="stylesheet" href="/static/css/main.css">
    </head>
    <body style="font-family: Arial; padding: 30px;">
        <h1>{user_name}'s Activities</h1>
        <p><a href="/dashboard">Back to dashboard</a></p>
        <p><a href="/activities/new">Log a new activity</a></p>
        {activity_html}
    </body>
    </html>
    """


def activity_form(error=""):
    error_html = ""

    if error != "":
        error_html = f"<p style='color:red;'><strong>{error}</strong></p>"

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>FitTrack | Log Activity</title>
        <link rel="stylesheet" href="/static/css/main.css">
    </head>
    <body style="font-family: Arial; padding: 30px;">
        <h1>Log a Workout</h1>
        <p>Add your activity below.</p>

        {error_html}

        <form action="/activities/new" method="post">
            <p>
                <label>Activity Type</label><br>
                <select name="activity_type">
                    <option value="">Select one</option>
                    <option value="Running">Running</option>
                    <option value="Walking">Walking</option>
                    <option value="Cycling">Cycling</option>
                    <option value="Swimming">Swimming</option>
                    <option value="Gym">Gym</option>
                </select>
            </p>

            <p>
                <label>Date</label><br>
                <input type="date" name="date">
            </p>

            <p>
                <label>Duration (minutes)</label><br>
                <input type="text" name="duration" placeholder="e.g. 45">
            </p>

            <p>
                <label>Distance (optional)</label><br>
                <input type="text" name="distance" placeholder="e.g. 5 km">
            </p>

            <p>
                <label>Notes (optional)</label><br>
                <textarea name="notes" rows="4" cols="40"></textarea>
            </p>

            <button type="submit">Save Activity</button>
        </form>

        <p><a href="/dashboard">Back to dashboard</a></p>
    </body>
    </html>
    """