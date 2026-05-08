import re

from flask import Blueprint, request, session, redirect, render_template
from data import user_store

auth = Blueprint("auth", __name__)

# this file handles account signup, login, logout, validation and session setup



# LOGIN



@auth.route("/login", methods=["GET"])
def login_page():
    # this shows the login page, but sends already logged in users to the dashboard
    if "user_id" in session:
        return redirect("/dashboard")

    return render_template("login.html")


@auth.route("/login", methods=["POST"])
def login_submit():
    # this checks the submitted login details against the stored user account
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    user = user_store.login(email, password)

    if user is None:
        return render_template("login.html", error="Invalid email or password.")

    # this stores the logged in user in the session so protected pages can identify them
    session["user_id"] = user["id"]
    session["user_name"] = user["name"]

    return redirect("/dashboard")


# -------------------------
# SIGNUP
# -------------------------


@auth.route("/signup", methods=["GET"])
def signup_page():
    # this shows the signup page, but skips it if the user already has a session
    if "user_id" in session:
        return redirect("/dashboard")

    return render_template("signup.html")


@auth.route("/signup", methods=["POST"])
def signup_submit():
    # this collects and validates the signup form before creating an account
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    confirm = request.form.get("confirm", "")

    error = None

    if name == "":
        error = "Name is required."
    elif not re.match(r"^[a-zA-Z\s\-]+$", name):
        error = "Name cannot contain numbers or special characters."
    elif email == "":
        error = "Email is required."
    elif len(password) < 8:
        error = "Password must be at least 8 characters."
    elif not re.search(r"[a-z]", password):
        error = "Password must contain at least one lowercase letter."
    elif not re.search(r"[A-Z]", password):
        error = "Password must contain at least one uppercase letter."
    elif not re.search(r"[ !\"#$%&'()*+,\-./:;<=>?@[\\\]^_`{|}~]", password):
        error = "Password must contain at least one special character."
    elif password != confirm:
        error = "Passwords do not match."

    if error:
        return render_template(
            "signup.html", error=error, prefill_name=name, prefill_email=email
        )

    user = user_store.register(name, email, password)

    # this handles duplicate emails because register returns none if the account exists
    if user is None:
        return render_template(
            "signup.html",
            error="An account with that email already exists.",
            prefill_name=name,
            prefill_email=email,
        )

    session["user_id"] = user["id"]
    session["user_name"] = user["name"]

    return redirect("/dashboard")


# -------------------------
# LOGOUT
# -------------------------


@auth.route("/logout", methods=["POST"])
def logout():
    # this clears the session so the user is signed out of protected pages
    session.clear()
    return redirect("/")
