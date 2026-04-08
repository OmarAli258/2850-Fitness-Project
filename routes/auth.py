from flask import Blueprint, request, session, redirect
from data import user_store

# Group all auth routes under one blueprint
auth = Blueprint("auth", __name__)


# -------------------------------------------------------
# LOGIN
# -------------------------------------------------------

# User visits /login - just show the form
@auth.route("/login", methods=["GET"])
def login_page():
    # If already logged in, skip the login page
    if "user_id" in session:
        return redirect("/dashboard")
    return login_form()


# User submits the login form
@auth.route("/login", methods=["POST"])
def login_submit():
    # Grab what the user typed in the form
    email = request.form.get("email", "")
    password = request.form.get("password", "")

    # Check if email and password are correct
    user = user_store.login(email, password)

    # Wrong details - show the form again with an error
    if user is None:
        return login_form(error="Invalid email or password.")

    # Correct - save to session so they stay logged in
    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    return redirect("/login")


# -------------------------------------------------------
# SIGNUP
# -------------------------------------------------------

# User visits /signup - just show the form
@auth.route("/signup", methods=["GET"])
def signup_page():
    # If already logged in, skip the signup page
    if "user_id" in session:
        return redirect("/dashboard")
    return signup_form()


# User submits the signup form
@auth.route("/signup", methods=["POST"])
def signup_submit():
    # Grab what the user typed in the form
    name = request.form.get("name", "")
    email = request.form.get("email", "")
    password = request.form.get("password", "")
    confirm = request.form.get("confirm", "")

    # Check each field one by one
    error = None
    if not name:
        error = "Name is required."
    elif not email:
        error = "Email is required."
    elif len(password) < 6:
        error = "Password must be at least 6 characters."
    elif password != confirm:
        error = "Passwords do not match."

    # If any field failed, show the form again with the error
    if error:
        return signup_form(
            error=error,
            prefill_name=name,
            prefill_email=email
        )

    # Try to create the account
    user = user_store.register(name, email, password)

    # Email already taken
    if user is None:
        return signup_form(
            error="An account with that email already exists.",
            prefill_name=name,
            prefill_email=email
        )

    # Account created - log them in straight away
    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    return redirect("/dashboard")


# -------------------------------------------------------
# LOGOUT
# -------------------------------------------------------

@auth.route("/logout", methods=["POST"])
def logout():
    # Wipe the session and send them home
    session.clear()
    return redirect("/")


# -------------------------------------------------------
# HTML FORMS
# -------------------------------------------------------

def login_form(error=None):
    # Build the error message if there is one
    error_html = ""
    if error:
        error_html = f'<div class="auth-error">⚠ {error}</div>'

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>FitTrack | Login</title>
        <link rel="stylesheet" href="/static/css/main.css">
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap">
    </head>
    <body>
        <div class="auth-page">
            <div class="auth-card">

                <!-- Header -->
                <div class="auth-header">
                    <h1>Welcome back</h1>
                    <p class="auth-sub">Log in to track your training.</p>
                </div>

                <!-- Error message (only shows if there is one) -->
                {error_html}

                <!-- Login form -->
                <form action="/login" method="post" class="auth-form">
                    <div class="form-group">
                        <label>Email</label>
                        <input type="email" name="email"
                               placeholder="alex@example.com" required>
                    </div>
                    <div class="form-group">
                        <label>Password</label>
                        <input type="password" name="password"
                               placeholder="••••••••" required>
                    </div>
                    <button type="submit" class="btn btn-primary btn-full">
                        Log in
                    </button>
                </form>

                <!-- Link to signup page -->
                <p class="auth-switch">
                    Don't have an account?
                    <a href="/signup">Sign up free</a>
                </p>

            </div>
        </div>
    </body>
    </html>
    """


def signup_form(error=None, prefill_name="", prefill_email=""):
    # Build the error message if there is one
    error_html = ""
    if error:
        error_html = f'<div class="auth-error">⚠ {error}</div>'

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>FitTrack | Sign Up</title>
        <link rel="stylesheet" href="/static/css/main.css">
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap">
    </head>
    <body>
        <div class="auth-page">
            <div class="auth-card">

                <!-- Header -->
                <div class="auth-header">
                    <h1>Create account</h1>
                    <p class="auth-sub">Start tracking your fitness today.</p>
                </div>

                <!-- Error message (only shows if there is one) -->
                {error_html}

                <!-- Signup form -->
                <form action="/signup" method="post" class="auth-form">
                    <div class="form-group">
                        <label>Full name</label>
                        <input type="text" name="name"
                               placeholder="Alex Johnson"
                               value="{prefill_name}" required>
                    </div>
                    <div class="form-group">
                        <label>Email</label>
                        <input type="email" name="email"
                               placeholder="alex@example.com"
                               value="{prefill_email}" required>
                    </div>
                    <div class="form-group">
                        <label>Password</label>
                        <input type="password" name="password"
                               placeholder="At least 6 characters" required>
                    </div>
                    <div class="form-group">
                        <label>Confirm password</label>
                        <input type="password" name="confirm"
                               placeholder="••••••••" required>
                    </div>
                    <button type="submit" class="btn btn-primary btn-full">
                        Create account
                    </button>
                </form>

                <!-- Link to login page -->
                <p class="auth-switch">
                    Already have an account?
                    <a href="/login">Log in</a>
                </p>

            </div>
        </div>
    </body>
    </html>
    """