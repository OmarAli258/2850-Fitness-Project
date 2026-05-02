from flask import Blueprint, render_template, request, redirect, session
from data import race_store

races = Blueprint("races", __name__)


@races.route("/racetracker")
def racetracker():
    if "user_id" not in session:
        return redirect("/login")

    user_races = race_store.get_races_for_user(session["user_id"])
    summary = race_store.get_race_summary(session["user_id"])

    return render_template(
        "racetracker.html",
        races=user_races,
        summary=summary
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

    name = request.form.get("name", "").strip()
    race_type = request.form.get("race_type", "").strip()
    location = request.form.get("location", "").strip()
    date = request.form.get("date", "").strip()
    finish_time = request.form.get("finish_time", "").strip()
    status = request.form.get("status", "").strip()
    is_pb = request.form.get("is_pb", "0")

    if is_pb == "on":
        is_pb = 1
    else:
        is_pb = 0

    if name == "":
        return render_template("addrace.html", error="Race name is required.")

    if race_type == "":
        return render_template("addrace.html", error="Race type is required.")

    if location == "":
        return render_template("addrace.html", error="Location is required.")

    if date == "":
        return render_template("addrace.html", error="Date is required.")

    if status == "":
        return render_template("addrace.html", error="Status is required.")

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