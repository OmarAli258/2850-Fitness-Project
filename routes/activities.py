import gpxpy
import json
from flask import Blueprint, request, session, redirect, render_template
from data import activity_store
from datetime import date

activities = Blueprint("activities", __name__)


def _build_form_data(request_form=None, activity=None):
    if activity is not None:
        return {
            "activity_type": activity.get("type", ""),
            "date": activity.get("date", ""),
            "duration": activity.get("duration", ""),
            "distance": activity.get("distance", ""),
            "notes": activity.get("notes", ""),
            "is_public": activity.get("is_public", 0),
        }

    request_form = request_form or {}
    return {
        "activity_type": request_form.get("activity_type", "").strip(),
        "date": request_form.get("date", "").strip(),
        "duration": request_form.get("duration", "").strip(),
        "distance": request_form.get("distance", "").strip(),
        "notes": request_form.get("notes", "").strip(),
        "is_public": 1 if request_form.get("is_public") == "on" else 0,
    }


def _validate_activity(form_data):
    if form_data["activity_type"] == "":
        return "Please choose an activity type."

    if form_data["date"] == "":
        return "Please choose a date."

    if form_data["duration"] == "":
        return "Please enter the duration."

    if not form_data["duration"].isdigit():
        return "Duration must be a number."

    return ""


@activities.route("/activities/new", methods=["GET"])
def show_activity_form():
    if "user_id" not in session:
        return redirect("/login")

    return render_template(
        "activity_form.html",
        heading="Log a Workout",
        action="/activities/new",
        submit_label="Save Activity",
        activity_types=activity_store.ACTIVITY_TYPES,
        form_data=_build_form_data(),
        error="",
    )


@activities.route("/activities/new", methods=["POST"])
def save_activity():
    if "user_id" not in session:
        return redirect("/login")

    form_data = _build_form_data(request.form)
    error = _validate_activity(form_data)

    route_data_json = None
    gpx_file = request.files.get("gpx_file")
    if gpx_file and gpx_file.filename.endswith('.gpx'):
        try:
            gpx = gpxpy.parse(gpx_file)
            route_points = []
            for track in gpx.tracks:
                for segment in track.segments:
                    for point in segment.points:
                        route_points.append([point.latitude, point.longitude])
            
            if route_points:
                route_data_json = json.dumps(route_points)
                
                # Auto-fill duration and distance if they are empty
                # Using basic gpxpy properties
                moving_data = gpx.get_moving_data()
                if moving_data and form_data["distance"] == "":
                    distance_km = moving_data.moving_distance / 1000.0
                    form_data["distance"] = str(round(distance_km, 2))
                
                if form_data["duration"] == "":
                    # approximate duration in minutes
                    duration_min = gpx.get_duration() / 60.0 if gpx.get_duration() else 0
                    form_data["duration"] = str(int(duration_min))
                
                # Re-validate after auto-fill
                error = _validate_activity(form_data)
        except Exception as e:
            error = f"Error parsing GPX file: {str(e)}"

    if error:
        return render_template(
            "activity_form.html",
            heading="Log a Workout",
            action="/activities/new",
            submit_label="Save Activity",
            activity_types=activity_store.ACTIVITY_TYPES,
            form_data=form_data,
            error=error,
        )

    activity_store.create_activity(
        user_id=session["user_id"],
        activity_type=form_data["activity_type"],
        date=form_data["date"],
        duration=form_data["duration"],
        distance=form_data["distance"],
        notes=form_data["notes"],
        route_data=route_data_json,
        is_public=form_data.get("is_public", 0)
    )

    return redirect("/activities")


@activities.route("/activities/<activity_id>", methods=["GET"])
def view_activity(activity_id):
    if "user_id" not in session:
        return redirect("/login")

    activity = activity_store.get_activity(session["user_id"], activity_id)
    if activity is None:
        return redirect("/activities")

    return render_template(
        "activity_detail.html",
        activity=activity
    )

@activities.route("/activities/<activity_id>/edit", methods=["GET"])
def edit_activity(activity_id):
    if "user_id" not in session:
        return redirect("/login")

    activity = activity_store.get_activity(session["user_id"], activity_id)
    if activity is None:
        return redirect("/activities")

    return render_template(
        "activity_form.html",
        heading="Edit Activity",
        action=f"/activities/{activity_id}/edit",
        submit_label="Save Changes",
        activity_types=activity_store.ACTIVITY_TYPES,
        form_data=_build_form_data(activity=activity),
        error="",
    )


@activities.route("/activities/<activity_id>/edit", methods=["POST"])
def save_edited_activity(activity_id):
    if "user_id" not in session:
        return redirect("/login")

    form_data = _build_form_data(request.form)
    error = _validate_activity(form_data)

    if error:
        return render_template(
            "activity_form.html",
            heading="Edit Activity",
            action=f"/activities/{activity_id}/edit",
            submit_label="Save Changes",
            activity_types=activity_store.ACTIVITY_TYPES,
            form_data=form_data,
            error=error,
        )

    activity_store.update_activity(
        activity_id=activity_id,
        user_id=session["user_id"],
        activity_type=form_data["activity_type"],
        date=form_data["date"],
        duration=form_data["duration"],
        distance=form_data["distance"],
        notes=form_data["notes"],
        is_public=form_data.get("is_public", 0)
    )

    return redirect("/activities")


@activities.route("/activities/<activity_id>/delete", methods=["POST"])
def delete_activity(activity_id):
    if "user_id" not in session:
        return redirect("/login")

    activity_store.delete_activity(activity_id, session["user_id"])
    return redirect("/activities")


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
