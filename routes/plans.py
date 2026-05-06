#this file defines routes and logic for creating, viewing, editing and deleting plans
#also handles plan status, sessions progress and consistency (adherence) ratings
#note: we changed the user-facing word adherence because it was too complex for users
#we chose the simpler word consistency, but some code was already named adherence
#so consistency is the main word in comments, with adherence shown because the code still uses that label

#import flask routing and session features and data access for plans and activity types
from flask import Blueprint, request, session, redirect, render_template
from data import plan_store, activity_store

plans = Blueprint("plans", __name__)


#this function prepares plan form data for creating, editing, or redisplaying the form after an error
def _build_form_data(request_form=None, plan=None):
    if plan is not None:
        freq_num = ""
        freq_unit = "weekly"
        if plan.get("frequency"):
            freq_parts = plan["frequency"].split(" ", 1)
            if len(freq_parts) == 2:
                freq_num = freq_parts[0]
                freq_unit = freq_parts[1]
            elif freq_parts[0].isdigit():
                freq_num = freq_parts[0]
            else:
                freq_num = "1"
                freq_unit = freq_parts[0]

        dur_unit = "minutes"
        if plan.get("target_duration"):
            try:
                dur = int(plan["target_duration"])
                if dur >= 60:
                    dur_unit = "hours"
            except:
                pass

        return {
            "name": plan.get("name", ""),
            "exercise_type": plan.get("exercise_type", ""),
            "frequency_number": freq_num,
            "frequency_unit": freq_unit,
            "target_duration": plan.get("target_duration", ""),
            "target_duration_unit": dur_unit,
            "target_distance": plan.get("target_distance", ""),
            "notes": plan.get("notes", ""),
            "status": plan.get("status", "active"),
        }

    request_form = request_form or {}
    freq_num = request_form.get("frequency_number", "").strip()
    freq_unit = request_form.get("frequency_unit", "weekly").strip()
    target_duration = request_form.get("target_duration", "").strip()
    target_duration_unit = request_form.get("target_duration_unit", "minutes").strip()

    return {
        "name": request_form.get("name", "").strip(),
        "exercise_type": request_form.get("exercise_type", "").strip(),
        "frequency_number": freq_num,
        "frequency_unit": freq_unit,
        "target_duration": target_duration,
        "target_duration_unit": target_duration_unit,
        "target_distance": request_form.get("target_distance", "").strip(),
        "notes": request_form.get("notes", "").strip(),
        "status": request_form.get("status", "active").strip(),
    }


#this function validates the required plan form fields before saving or updating a plan
def _validate_plan(form_data):
    if form_data["name"] == "":
        return "Please enter a plan name."
    if form_data["exercise_type"] == "":
        return "Please choose an exercise type."
    if form_data["frequency_number"] == "":
        return "Please enter a frequency number."
    try:
        freq_num = int(form_data["frequency_number"])
    except ValueError:
        return "Frequency number must be a number."
    if freq_num < 1:
        return "Frequency number must be at least 1."
    if form_data["frequency_unit"] not in ["daily", "weekly", "monthly", "yearly"]:
        return "Please choose a valid frequency unit."

    if form_data["target_duration"] != "":
        try:
            dur = int(form_data["target_duration"])
        except ValueError:
            return "Target duration must be a number."
        if dur < 0:
            return "Target duration cannot be negative."

    return ""


#this function formats frequency as number + unit string for database storage
def _format_frequency(form_data):
    freq_num = form_data["frequency_number"]
    freq_unit = form_data["frequency_unit"]
    if freq_unit == "daily":
        return f"{freq_num}x daily"
    elif freq_unit == "monthly":
        return f"{freq_num}x monthly"
    elif freq_unit == "yearly":
        return f"{freq_num}x yearly"
    else:
        return f"{freq_num}x weekly"


#this function converts target duration to minutes before saving
def _duration_to_minutes(form_data):
    if not form_data["target_duration"]:
        return None
    duration = int(form_data["target_duration"])
    if form_data["target_duration_unit"] == "hours":
        duration = duration * 60
    return duration


#this function shows all plans for the logged in user with session progress data
@plans.route("/plans", methods=["GET"])
def show_plans():
    if "user_id" not in session:
        return redirect("/login")

    plans_list = plan_store.get_plans_for_user(session["user_id"])
    summary = plan_store.get_plan_summary(session["user_id"])

    plans_with_completion = []
    for plan in plans_list:
        completion = plan_store.get_plan_completion(session["user_id"], plan["id"])
        plans_with_completion.append({
            **plan,
            "completed_count": completion["completed_count"] if completion else 0,
            "expected_sessions": completion["expected_sessions"] if completion else 0,
            "frequency_target": completion["frequency_target"] if completion else 1,
            "completion_rate": completion["completion_rate"] if completion else 0,
        })

    return render_template(
        "plans.html",
        plans=plans_with_completion,
        summary=summary,
    )


#this function shows the blank form for creating a new plan
@plans.route("/plans/new", methods=["GET"])
def show_plan_form():
    if "user_id" not in session:
        return redirect("/login")

    return render_template(
        "plan_form.html",
        heading="Create Plan",
        action="/plans/new",
        submit_label="Create Plan",
        activity_types=activity_store.ACTIVITY_TYPES,
        form_data=_build_form_data(),
        error="",
    )


#this function validates and saves a new plan
@plans.route("/plans/new", methods=["POST"])
def save_plan():
    if "user_id" not in session:
        return redirect("/login")

    form_data = _build_form_data(request.form)
    error = _validate_plan(form_data)

    if error:
        return render_template(
            "plan_form.html",
            heading="Create Plan",
            action="/plans/new",
            submit_label="Create Plan",
            activity_types=activity_store.ACTIVITY_TYPES,
            form_data=form_data,
            error=error,
        )

    plan_store.create_plan(
        user_id=session["user_id"],
        name=form_data["name"],
        exercise_type=form_data["exercise_type"],
        frequency=_format_frequency(form_data),
        target_duration=_duration_to_minutes(form_data),
        target_distance=form_data["target_distance"],
        notes=form_data["notes"],
    )

    return redirect("/plans")


#this function shows one plan detail page with sessions progress and consistency (adherence) records
@plans.route("/plans/<plan_id>", methods=["GET"])
def view_plan(plan_id):
    if "user_id" not in session:
        return redirect("/login")

    completion = plan_store.get_plan_completion(session["user_id"], plan_id)
    if completion is None:
        return redirect("/plans")

    adherence = plan_store.get_adherence_for_plan(session["user_id"], plan_id)
    adherence_summary = plan_store.get_adherence_summary(session["user_id"], plan_id)

    return render_template(
        "plan_detail.html",
        completion=completion,
        adherence=adherence,
        adherence_summary=adherence_summary,
    )


#this function shows the edit form for an existing plan
@plans.route("/plans/<plan_id>/edit", methods=["GET"])
def edit_plan(plan_id):
    if "user_id" not in session:
        return redirect("/login")

    plan = plan_store.get_plan(session["user_id"], plan_id)
    if plan is None:
        return redirect("/plans")

    return render_template(
        "plan_form.html",
        heading="Edit Plan",
        action=f"/plans/{plan_id}/edit",
        submit_label="Save Changes",
        activity_types=activity_store.ACTIVITY_TYPES,
        form_data=_build_form_data(plan=plan),
        error="",
    )


#this function validates and saves changes to an existing plan
@plans.route("/plans/<plan_id>/edit", methods=["POST"])
def save_edited_plan(plan_id):
    if "user_id" not in session:
        return redirect("/login")

    form_data = _build_form_data(request.form)
    error = _validate_plan(form_data)

    if error:
        return render_template(
            "plan_form.html",
            heading="Edit Plan",
            action=f"/plans/{plan_id}/edit",
            submit_label="Save Changes",
            activity_types=activity_store.ACTIVITY_TYPES,
            form_data=form_data,
            error=error,
        )

    plan_store.update_plan(
        plan_id=plan_id,
        user_id=session["user_id"],
        name=form_data["name"],
        exercise_type=form_data["exercise_type"],
        frequency=_format_frequency(form_data),
        target_duration=_duration_to_minutes(form_data),
        target_distance=form_data["target_distance"],
        notes=form_data["notes"],
        status=form_data["status"],
    )

    return redirect("/plans")


#this function deletes a plan owned by the logged in user
@plans.route("/plans/<plan_id>/delete", methods=["POST"])
def delete_plan(plan_id):
    if "user_id" not in session:
        return redirect("/login")

    plan_store.delete_plan(plan_id, session["user_id"])
    return redirect("/plans")


#this function updates the status of a plan, like active, paused or completed
@plans.route("/plans/<plan_id>/status", methods=["POST"])
def update_plan_status(plan_id):
    if "user_id" not in session:
        return redirect("/login")

    new_status = request.form.get("status", "active").strip()
    if new_status not in ["active", "paused", "completed"]:
        return redirect(f"/plans/{plan_id}")

    plan = plan_store.get_plan(session["user_id"], plan_id)
    if plan is None:
        return redirect("/plans")

    plan_store.update_plan(
        plan_id=plan_id,
        user_id=session["user_id"],
        name=plan["name"],
        exercise_type=plan["exercise_type"],
        frequency=plan["frequency"],
        target_duration=plan["target_duration"],
        target_distance=plan["target_distance"],
        notes=plan["notes"],
        status=new_status,
    )

    return redirect("/plans")


#this function records a consistency (adherence) rating for a plan session
@plans.route("/plans/<plan_id>/adherence", methods=["POST"])
def record_plan_adherence(plan_id):
    if "user_id" not in session:
        return redirect("/login")

    session_date = request.form.get("session_date", "").strip()
    rating = request.form.get("rating", "").strip()
    notes = request.form.get("adherence_notes", "").strip()

    if not session_date or not rating:
        return redirect(f"/plans/{plan_id}")

    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            return redirect(f"/plans/{plan_id}")
    except ValueError:
        return redirect(f"/plans/{plan_id}")

    plan_store.record_adherence(
        user_id=session["user_id"],
        plan_id=plan_id,
        session_date=session_date,
        rating=rating,
        notes=notes,
    )

    return redirect(f"/plans/{plan_id}")


#this function deletes one consistency (adherence) record from a plan
@plans.route("/plans/<plan_id>/adherence/<adherence_id>/delete", methods=["POST"])
def delete_plan_adherence(plan_id, adherence_id):
    if "user_id" not in session:
        return redirect("/login")

    plan_store.delete_adherence(adherence_id, session["user_id"])
    return redirect(f"/plans/{plan_id}")

#done comments for routes/plans.py
#summary of comments:
# - shows all plans and one plan detail page
# - shows blank and edit forms for plans
# - validates plan form input
# - saves new and edited plans
# - deletes plans and updates plan status
# - records and deletes plan consistency (adherence) ratings
# - connects plans to activity types and session progress
#note: consistency is the main word we use for users because it is easier to understand than adherence
#the code still says adherence in some function and variable names because that was the original label
#that is why comments show consistency (adherence), so the simple user word and the code word both make sense
