# this file defines routes and logic for creating, viewing, editing and deleting activities
# also shows main activities page with search, filtering and grouping by upcoming and past

# import libraries for gpx parsing, json handling, flask routing/session features, activity/plan data access and date comparisons

import gpxpy
import json
from flask import Blueprint, request, session, redirect, render_template
from data import activity_store, plan_store
from datetime import date

activities = Blueprint("activities", __name__)


# this function prepares activity form data for creating, editing, or redisplaying the form after an error


def _build_form_data(request_form=None, activity=None):
    if activity is not None:
        return {
            "activity_type": activity.get("type", ""),
            "date": activity.get("date", ""),
            "duration": activity.get("duration", ""),
            "duration_unit": "minutes",
            "distance": activity.get("distance", ""),
            "notes": activity.get("notes", ""),
            "is_public": activity.get("is_public", 0),
            "plan_id": activity.get("plan_id", ""),
        }

    request_form = request_form or {}
    return {
        "activity_type": request_form.get("activity_type", "").strip(),
        "date": request_form.get("date", "").strip(),
        "duration": request_form.get("duration", "").strip(),
        "duration_unit": request_form.get("duration_unit", "minutes").strip(),
        "distance": request_form.get("distance", "").strip(),
        "notes": request_form.get("notes", "").strip(),
        "is_public": 2 if request_form.get("visibility", "").lower() == "friends" else (1 if request_form.get("visibility", "").lower() == "public" else 0),
        "plan_id": request_form.get("plan_id", "").strip(),
    }


# this function validates the required activity form fields before saving or updating an activity
def _validate_activity(form_data):
    if form_data["activity_type"] == "":
        return "Please choose an activity type."

    if form_data["date"] == "":
        return "Please choose a date."

    if form_data["duration"] == "":
        return "Please enter the duration."

    try:
        duration = float(form_data["duration"])
    except ValueError:
        return "Duration must be a number."

    if duration <= 0:
        return "Duration must be more than 0."

    # max limits to prevent unrealistic inputs
    if duration > 480:
        return "Duration cannot exceed 8 hours (480 minutes)."

    if form_data["duration_unit"] not in ["minutes", "hours"]:
        return "Please choose minutes or hours for the duration."

    if form_data["distance"] != "":
        try:
            distance = float(form_data["distance"])
        except ValueError:
            return "Distance must be a number."

        if distance < 0:
            return "Distance cannot be negative."

        # Cap distance at 100km
        if distance > 100:
            form_data["distance"] = "100"

    return ""


# this function converts the activity duration into minutes before it is saved
def _duration_to_minutes(form_data):
    duration = float(form_data["duration"])
    if form_data["duration_unit"] == "hours":
        duration = duration * 60

    return max(1, int(round(duration)))


# this function shows the blank activity form for logging a new workout
@activities.route("/activities/new", methods=["GET"])
def show_activity_form():
    if "user_id" not in session:
        return redirect("/login")

    active_plans = plan_store.get_plans_for_user(session["user_id"])

    return render_template(
        "activity_form.html",
        heading="Log a Workout",
        action="/activities/new",
        submit_label="Save Activity",
        activity_types=activity_store.ACTIVITY_TYPES,
        active_plans=active_plans,
        form_data=_build_form_data(),
        error="",
    )


# this function saves a new activity, including optional GPX route parsing and plan linking
@activities.route("/activities/new", methods=["POST"])
def save_activity():
    if "user_id" not in session:
        return redirect("/login")

    form_data = _build_form_data(request.form)
    error = _validate_activity(form_data)

    route_data_json = None
    gpx_file = request.files.get("gpx_file")
    if gpx_file and gpx_file.filename.endswith(".gpx"):
        try:
            gpx = gpxpy.parse(gpx_file)
            route_points = []
            for track in gpx.tracks:
                for segment in track.segments:
                    for point in segment.points:
                        route_points.append([point.latitude, point.longitude])

            if route_points:
                route_data_json = json.dumps(route_points)

                # this autofills duration and distance if they are empty
                # using basic gpxpy properties
                moving_data = gpx.get_moving_data()
                if moving_data and form_data["distance"] == "":
                    distance_km = moving_data.moving_distance / 1000.0
                    form_data["distance"] = str(round(distance_km, 2))

                if form_data["duration"] == "":
                    # approximate duration in minutes
                    duration_min = (
                        gpx.get_duration() / 60.0 if gpx.get_duration() else 0
                    )
                    form_data["duration"] = str(int(duration_min))

                # revalidate after autofill
                error = _validate_activity(form_data)
        except Exception:
            error = "Could not parse GPX file. Please ensure it's a valid GPX file."

    if error:
        active_plans = plan_store.get_plans_for_user(session["user_id"])
        return render_template(
            "activity_form.html",
            heading="Log a Workout",
            action="/activities/new",
            submit_label="Save Activity",
            activity_types=activity_store.ACTIVITY_TYPES,
            active_plans=active_plans,
            form_data=form_data,
            error=error,
        )

    plan_id = form_data["plan_id"] if form_data["plan_id"] else None

    activity_store.create_activity(
        user_id=session["user_id"],
        activity_type=form_data["activity_type"],
        date=form_data["date"],
        duration=_duration_to_minutes(form_data),
        distance=form_data["distance"],
        notes=form_data["notes"],
        route_data=route_data_json,
        is_public=form_data.get("is_public", 0),
        plan_id=plan_id,
    )

    return redirect("/activities")


# this function shows the detail page for one activity if it belongs to the logged in user
@activities.route("/activities/<activity_id>", methods=["GET"])
def view_activity(activity_id):
    if "user_id" not in session:
        return redirect("/login")

    activity = activity_store.get_activity(session["user_id"], activity_id)
    if activity is None:
        return redirect("/activities")

    return render_template("activity_detail.html", activity=activity)


# this function shows the edit form for an existing activity
@activities.route("/activities/<activity_id>/edit", methods=["GET"])
def edit_activity(activity_id):
    if "user_id" not in session:
        return redirect("/login")

    activity = activity_store.get_activity(session["user_id"], activity_id)
    if activity is None:
        return redirect("/activities")

    active_plans = plan_store.get_plans_for_user(session["user_id"])

    return render_template(
        "activity_form.html",
        heading="Edit Activity",
        action=f"/activities/{activity_id}/edit",
        submit_label="Save Changes",
        activity_types=activity_store.ACTIVITY_TYPES,
        active_plans=active_plans,
        form_data=_build_form_data(activity=activity),
        error="",
    )


# this function validates and saves changes to an existing activity
@activities.route("/activities/<activity_id>/edit", methods=["POST"])
def save_edited_activity(activity_id):
    if "user_id" not in session:
        return redirect("/login")

    form_data = _build_form_data(request.form)
    error = _validate_activity(form_data)

    if error:
        active_plans = plan_store.get_plans_for_user(session["user_id"])
        return render_template(
            "activity_form.html",
            heading="Edit Activity",
            action=f"/activities/{activity_id}/edit",
            submit_label="Save Changes",
            activity_types=activity_store.ACTIVITY_TYPES,
            active_plans=active_plans,
            form_data=form_data,
            error=error,
        )

    plan_id = form_data["plan_id"] if form_data["plan_id"] else None

    activity_store.update_activity(
        activity_id=activity_id,
        user_id=session["user_id"],
        activity_type=form_data["activity_type"],
        date=form_data["date"],
        duration=_duration_to_minutes(form_data),
        distance=form_data["distance"],
        notes=form_data["notes"],
        is_public=form_data.get("is_public", 0),
        plan_id=plan_id,
    )

    return redirect("/activities")


# this function deletes an activity owned by the logged in user
@activities.route("/activities/<activity_id>/delete", methods=["POST"])
def delete_activity(activity_id):
    if "user_id" not in session:
        return redirect("/login")

    activity_store.delete_activity(activity_id, session["user_id"])
    return redirect("/activities")


# this function shows the activities page with search, type filtering, and upcomign and past grouping
@activities.route("/activities", methods=["GET"])
def show_activities():
    if "user_id" not in session:
        return redirect("/login")

    user_name = session.get("user_name", "User")
    filter_type = request.args.get("type", "").strip()
    search = request.args.get("search", "").strip()

    activities_list = activity_store.get_activities_for_user(
        session["user_id"],
        activity_type=filter_type or None,
        search=search or None,
    )

    today_str = date.today().isoformat()
    upcoming_activities = []
    past_activities = []

    for activity in activities_list:
        activity_date = activity.get("date", "")

        if activity_date >= today_str:
            upcoming_activities.append(activity)
        else:
            past_activities.append(activity)

    return render_template(
        "activities.html",
        user_name=user_name,
        activity_types=activity_store.ACTIVITY_TYPES,
        upcoming_activities=upcoming_activities,
        past_activities=past_activities,
        summary=activity_store.get_activity_summary(session["user_id"]),
        filter_type=filter_type,
        search=search,
    )


# done comments for routes/activities.py
# summary of comments:
# - blank form route shows an empty activity form so users can log a new workout
# - create route handles saving a newly logged workout to the database
# - view route displays one activity with all its details like date, duration and distance
# - edit route shows the activity form pre filled with existing data for changes
# - update route saves any edits made to an existing activity in the database
# - delete route removes an activity from the database and shows the activities list
# - main activities page shows all activities split into upcoming and past groups
# - search and filter parameters work together to find specific activities
