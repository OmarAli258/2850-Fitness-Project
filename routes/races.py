from flask import Blueprint, render_template, request, redirect, session
from data import race_store
from datetime import date as today_date, datetime

races = Blueprint("races", __name__)

def check_valid(value):
    import re
    match = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*(?:km)?\s*", value, re.IGNORECASE)
    if match is None:
        return None
    distance = float(match.group(1))
    if distance <= 0:
        return None
    if distance.is_integer():
        return str(int(distance))
    return str(distance).rstrip("0").rstrip(".")

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
        race_dict = dict(race)
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

    races_with_countdown = race_store.add_race_rankings(races_with_countdown)

    days_since_last = None
    past_races = [r for r in races_with_countdown if r['status'] == 'past']
    if past_races:
        most_recent_past = max(past_races, key=lambda r: r['date'])
        last_date = datetime.strptime(most_recent_past['date'], '%Y-%m-%d').date()
        days_since_last = (today - last_date).days

    return render_template(
        "racetracker.html",
        races=races_with_countdown,
        summary=summary,
        days_since_last=days_since_last
    )


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
    race_type   = check_valid(request.form.get("race_type", "").strip())

    if not name or not race_type or not date:
        return render_template("addrace.html", error="Please fill in all required fields.")

    if any(char.isdigit() for char in location):
        return render_template("addrace.html", error="Location cannot contain numbers.")

    if finish_time and race_store.parse_finish_time(finish_time) is None:
        return render_template("addrace.html", error="Finish time must be minutes, MM:SS, or HH:MM:SS.")

    status = 'upcoming' if date >= str(today_date.today()) else 'past'

    race_store.create_race(
        user_id=session["user_id"],
        name=name,
        race_type=race_type,
        location=location,
        date=date,
        finish_time=finish_time,
        is_pb=0,
        status=status
    )

    return redirect("/racetracker")


@races.route("/races/<race_id>/delete", methods=["POST"])
def delete_race(race_id):
    if "user_id" not in session:
        return redirect("/login")

    race_store.delete_race(race_id, session["user_id"])
    return redirect("/racetracker")
