from flask import Blueprint, session, redirect, render_template, request, jsonify
from data import activity_store, race_store, plan_store

dashboard = Blueprint("dashboard", __name__)

#main dashboard route shows stats, recent activities, plans and chart data
@dashboard.route("/dashboard")
def show_dashboard():
    if "user_id" not in session:
        return redirect("/login")

    user_name = session.get("user_name", "User")
    user_id = session["user_id"]

    # get all the data needed 
    summary = activity_store.get_activity_summary(user_id)
    all_activities = activity_store.get_activities_for_user(user_id)

    #split activities into past and upcoming 
    from datetime import date
    today = date.today().isoformat()
    past_activities = [a for a in all_activities if a["date"] < today][:4]
    upcoming_activities = [a for a in all_activities if a["date"] >= today]
    recent_activities = past_activities

    plans = plan_store.get_plans_for_user(user_id)
    race_summary = race_store.get_race_summary(user_id)

    # build chart data and combine activity stats with race stats
    chart_data = activity_store.get_chart_data(user_id)
    chart_data["upcoming_races"] = race_summary["upcoming_races"]
    chart_data["past_races"] = race_summary["past_races"]
    chart_data["personal_bests"] = race_summary["personal_bests"]

    return render_template(
        "dashboard.html",
        user_name=user_name,
        summary=summary,
        recent_activities=recent_activities,
        upcoming_activities=upcoming_activities,
        plans=plans,
        race_summary=race_summary,
        chart_data=chart_data
    )


# api endpoint used by the dashboard search bar to get matching activities as JSON
@dashboard.route("/api/search")
def api_search():
    if "user_id" not in session:
        return jsonify([]), 401

    query = request.args.get("q", "").strip()
    results = activity_store.search_activities(session["user_id"], query)

    return jsonify([
        {
            "id": activity["id"],
            "type": activity["type"],
            "date": activity["date"],
            "duration": activity["duration"],
            "distance": activity["distance"],
            "notes": activity["notes"] or "",
        }
        for activity in results
    ])