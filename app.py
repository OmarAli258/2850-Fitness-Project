from flask import Flask, session, redirect
from routes.auth import auth
from routes.dashboard import dashboard

app = Flask(__name__)
app.secret_key = "fittrack-secret-2025"

app.register_blueprint(auth)
app.register_blueprint(dashboard)

@app.route("/")
def home():
    # If already logged in, send them straight to dashboard
    if "user_id" in session:
        return redirect("/dashboard")

    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>FitTrack</title>
        <link rel="stylesheet" href="/static/css/main.css">
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap">
        <style>
            body {
                margin: 0;
                font-family: 'DM Sans', sans-serif;
                background: #f8f5e9;
                color: #111;
            }

            .home-page {
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 40px 20px;
            }

            .home-card {
                max-width: 700px;
                width: 100%;
                background: white;
                border: 3px solid #111;
                border-radius: 24px;
                padding: 40px;
                box-shadow: 8px 8px 0 #111;
                text-align: center;
            }

            .home-card h1 {
                font-family: 'Syne', sans-serif;
                font-size: 48px;
                margin-bottom: 12px;
            }

            .home-card p {
                font-size: 18px;
                line-height: 1.6;
                margin-bottom: 28px;
            }

            .home-actions {
                display: flex;
                gap: 16px;
                justify-content: center;
                flex-wrap: wrap;
            }

            .home-btn {
                display: inline-block;
                text-decoration: none;
                padding: 14px 22px;
                border-radius: 14px;
                font-weight: 700;
                border: 2px solid #111;
                transition: 0.2s ease;
            }

            .home-btn-primary {
                background: #f5c400;
                color: #111;
            }

            .home-btn-secondary {
                background: #111;
                color: white;
            }

            .home-btn:hover {
                transform: translateY(-2px);
            }
        </style>
    </head>
    <body>
        <div class="home-page">
            <div class="home-card">
                <h1>FitTrack</h1>
                <p>
                    Plan workouts, log activities, and track your fitness progress all in one place.
                    Whether you're training casually or preparing for a big event, FitTrack helps you stay on track.
                </p>

                <div class="home-actions">
                    <a href="/login" class="home-btn home-btn-secondary">Log In</a>
                    <a href="/signup" class="home-btn home-btn-primary">Sign Up</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(debug=True, port=8080)