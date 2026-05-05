from flask import Blueprint, render_template, request, redirect, session
from data import race_store
from datetime import date as today_date, datetime

races = Blueprint("races", __name__)

def check_valid(value):
    import re
    cleaned = re.sub(r'[^\d.]', '', value)
    if cleaned == '':
        return None
    return cleaned

@races.route("/racetracker")
def racetracker():
    if "user_id" not in session:
        return redirect("/login")

    race_store.update_race_statuses(session["user_id"])
    user_races = race_store.get_races_for_user(session["user_id"])
    summary = race_store.get_race_summary(session["user_id"])
    today = today_date.today()
    races_with_countdown = []

    for race in user_races:
        race_dict = dict(race)  # convert to regular dictionary
        if race_dict['status'] == 'upcoming':
            race_date = datetime.strptime(race_dict['date'], '%Y-%m-%d').date()
            diff = (race_date - today).days
            if diff == 0:
                race_dict['countdown'] = 'Today!'
            elif diff == 1:
                race_dict['countdown'] = 'Tomorrow!'
            else:
                race_dict['countdown'] = f'In {diff} days'
        else:
            race_dict['countdown'] = ''
        races_with_countdown.append(race_dict)

    return render_template("racetracker.html", races=races_with_countdown, summary=summary)

@races.route("/addrace", methods=["GET"])
def addrace_page():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("addrace.html", error="")


@races.route("/addrace", methods=["POST"])
def add_race():
    if "user_id" not in session:
        return redirect("/login")

    name        = request.form.get("name", "").strip()
    location    = request.form.get("location", "").strip()
    date        = request.form.get("date", "").strip()
    finish_time = request.form.get("finish_time", "").strip()
    is_pb       = 1 if request.form.get("is_pb") == "on" else 0
    race_type = check_valid(request.form.get("race_type", "").strip())

    if not name or not race_type or not date:
        return render_template("addrace.html", error="Please fill in all required fields.")

    status = 'upcoming' if date >= str(today_date.today()) else 'past'

    race_store.create_race(
        user_id=session["user_id"],
        name=name,
        race_type=race_type,
        location=location,
        date=date,
        finish_time=finish_time,
        is_pb=is_pb,
        status=status
    )

    return redirect("/racetracker")


@races.route("/races/<race_id>/delete", methods=["POST"])
def delete_race(race_id):
    if "user_id" not in session:
        return redirect("/login")

    race_store.delete_race(race_id, session["user_id"])
    return redirect("/racetracker")