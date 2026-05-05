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
    race_summary = race_store.get_race_summary(user_id)
    chart_data = activity_store.get_chart_data(user_id)
    chart_data["upcoming_races"] = race_summary["upcoming_races"]
    chart_data["past_races"] = race_summary["past_races"]
    chart_data["personal_bests"] = race_summary["personal_bests"]
    return render_template(
        "dashboard.html",
        user_name=user_name,
        summary=summary,
        recent_activities=recent_activities,
        race_summary=race_summary,
        chart_data=chart_data
    )