from flask import Blueprint, session, redirect, render_template
from data import activity_store

dashboard = Blueprint("dashboard", __name__)


@dashboard.route("/dashboard")
def show_dashboard():
    if "user_id" not in session:
        return redirect("/login")

    user_name = session.get("user_name", "User")
    user_id = session["user_id"]

    summary = activity_store.get_activity_summary(user_id)
    recent_activities = activity_store.get_activities_for_user(user_id)[:4]

    return render_template("dashboard.html", user_name=user_name, summary=summary, recent_activities=recent_activities)

 