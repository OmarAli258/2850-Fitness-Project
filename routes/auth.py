from flask import Blueprint, request, session, redirect, render_template
from data import user_store

auth = Blueprint("auth", __name__)


# -------------------------
# LOGIN
# -------------------------

@auth.route("/login", methods=["GET"])
def login_page():
    if "user_id" in session:
        return redirect("/dashboard")

    return render_template("login.html")


@auth.route("/login", methods=["POST"])
def login_submit():
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    user = user_store.login(email, password)

    if user is None:
        return render_template(
            "login.html",
            error="Invalid email or password."
        )

    session["user_id"] = user["id"]
    session["user_name"] = user["name"]

    return redirect("/dashboard")


# -------------------------
# SIGNUP
# -------------------------

@auth.route("/signup", methods=["GET"])
def signup_page():
    if "user_id" in session:
        return redirect("/dashboard")

    return render_template("signup.html")


@auth.route("/signup", methods=["POST"])
def signup_submit():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    confirm = request.form.get("confirm", "")

    error = None

    if name == "":
        error = "Name is required."
    elif email == "":
        error = "Email is required."
    elif len(password) < 6:
        error = "Password must be at least 6 characters."
    elif password != confirm:
        error = "Passwords do not match."

    if error:
        return render_template(
            "signup.html",
            error=error,
            prefill_name=name,
            prefill_email=email
        )

    user = user_store.register(name, email, password)

    if user is None:
        return render_template(
            "signup.html",
            error="An account with that email already exists.",
            prefill_name=name,
            prefill_email=email
        )

    session["user_id"] = user["id"]
    session["user_name"] = user["name"]

    return redirect("/dashboard")


# -------------------------
# LOGOUT
# -------------------------

@auth.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect("/")