from flask import Flask, session, redirect
from routes.auth import auth
from routes.activities import activities
from routes.dashboard import dashboard

app = Flask(__name__)
app.secret_key = "fittrack-secret-2025"

app.register_blueprint(auth)
app.register_blueprint(activities)
app.register_blueprint(dashboard)

@app.route("/")
def home():
    if "user_id" in session:
        return redirect("/dashboard")

    return """
    <h1>FitTrack</h1>
    <a href="/login">Login</a>
    <a href="/signup">Sign Up</a>
    """

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)