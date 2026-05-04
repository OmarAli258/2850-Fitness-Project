from flask import Blueprint, request, session, redirect, render_template
from data import plan_store, activity_store

plans = Blueprint("plans", __name__)


def _build_form_data(request_form=None, plan=None):
    if plan is not None:
        return {
            "name": plan.get("name", ""),
            "exercise_type": plan.get("exercise_type", ""),
            "frequency": plan.get("frequency", ""),
            "target_duration": plan.get("target_duration", ""),
            "target_distance": plan.get("target_distance", ""),
            "notes": plan.get("notes", ""),
            "status": plan.get("status", "active"),
        }

    request_form = request_form or {}
    return {
        "name": request_form.get("name", "").strip(),
        "exercise_type": request_form.get("exercise_type", "").strip(),
        "frequency": request_form.get("frequency", "").strip(),
        "target_duration": request_form.get("target_duration", "").strip(),
        "target_distance": request_form.get("target_distance", "").strip(),
        "notes": request_form.get("notes", "").strip(),
        "status": request_form.get("status", "active").strip(),
    }


def _validate_plan(form_data):
    if form_data["name"] == "":
        return "Please enter a plan name."
    if form_data["exercise_type"] == "":
        return "Please choose an exercise type."
    if form_data["frequency"] == "":
        return "Please enter a frequency."
    if form_data["target_duration"] and not form_data["target_duration"].isdigit():
        return "Target duration must be a number."
    return ""


@plans.route("/plans", methods=["GET"])
def show_plans():
    if "user_id" not in session:
        return redirect("/login")

    plans_list = plan_store.get_plans_for_user(session["user_id"])
    summary = plan_store.get_plan_summary(session["user_id"])

    plans_with_completion = []
    for plan in plans_list:
        completion = plan_store.get_plan_completion(plan["id"], session["user_id"])
        plans_with_completion.append({
            **plan,
            "completed_count": completion["completed_count"] if completion else 0,
            "expected_sessions": completion["expected_sessions"] if completion else 0,
            "completion_rate": completion["completion_rate"] if completion else 0,
        })

    return render_template(
        "plans.html",
        plans=plans_with_completion,
        summary=summary,
    )


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
        frequency=form_data["frequency"],
        target_duration=form_data["target_duration"],
        target_distance=form_data["target_distance"],
        notes=form_data["notes"],
    )

    return redirect("/plans")


@plans.route("/plans/<plan_id>", methods=["GET"])
def view_plan(plan_id):
    if "user_id" not in session:
        return redirect("/login")

    completion = plan_store.get_plan_completion(session["user_id"], plan_id)
    if completion is None:
        return redirect("/plans")

    return render_template(
        "plan_detail.html",
        completion=completion,
    )


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
        frequency=form_data["frequency"],
        target_duration=form_data["target_duration"],
        target_distance=form_data["target_distance"],
        notes=form_data["notes"],
        status=form_data["status"],
    )

    return redirect("/plans")


@plans.route("/plans/<plan_id>/delete", methods=["POST"])
def delete_plan(plan_id):
    if "user_id" not in session:
        return redirect("/login")

    plan_store.delete_plan(plan_id, session["user_id"])
    return redirect("/plans")
