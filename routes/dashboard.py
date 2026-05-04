import json
from flask import Blueprint, session, redirect, render_template
from data import activity_store, race_store

dashboard = Blueprint("dashboard", __name__)


@dashboard.route("/dashboard")
def show_dashboard():
    if "user_id" not in session:
        return redirect("/login")

    user_name = session.get("user_name", "User")
    user_id = session["user_id"]

    summary = activity_store.get_activity_summary(user_id)
    recent_activities = activity_store.get_activities_for_user(user_id)[:4]

    weekly_data = activity_store.get_weekly_activity_data(user_id)
    type_counts = activity_store.get_activity_type_counts(user_id)
    race_counts = race_store.get_monthly_race_counts(user_id)

    chart_data = {
        "workouts": {"labels": weekly_data["labels"], "data": weekly_data["workouts"]},
        "time": {"labels": weekly_data["labels"], "data": weekly_data["minutes"]},
        "distance": {"labels": weekly_data["labels"], "data": weekly_data["distances"]},
        "favorite": {"labels": type_counts["labels"], "data": type_counts["data"]},
        "races": {"labels": race_counts["labels"], "data": race_counts["data"]}
    }

    return render_template(
        "dashboard.html",
        user_name=user_name,
        summary=summary,
        recent_activities=recent_activities,
        chart_data=json.dumps(chart_data)
    )

 