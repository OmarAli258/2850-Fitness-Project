from flask import Blueprint, session, redirect, render_template

dashboard = Blueprint("dashboard", __name__)


@dashboard.route("/dashboard")
def show_dashboard():
    if "user_id" not in session:
        return redirect("/login")

    user_name = session.get("user_name", "User")

    return render_template("dashboard.html", user_name=user_name)

 