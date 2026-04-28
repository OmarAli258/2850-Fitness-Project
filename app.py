from flask import Flask, session, redirect, render_template
from routes.auth import auth
from routes.activities import activities
from routes.dashboard import dashboard
from routes.races import races

app = Flask(__name__)
app.secret_key = "fittrack-secret-2025"

app.register_blueprint(auth)
app.register_blueprint(activities)
app.register_blueprint(dashboard)
app.register_blueprint(races) 

@app.route("/")
def home():

    return render_template("home.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)