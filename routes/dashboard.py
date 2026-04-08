from flask import Blueprint, session, redirect

# Create a blueprint for dashboard routes
dashboard = Blueprint("dashboard", __name__)

@dashboard.route("/dashboard", methods=["GET"])
def dashboard_page():
    #if the user is not logged in, send them to login
    if "user_id" not in session:
        return redirect("/login")
    
    # get the user's name from the session
    user_name = session.get("user_name", "User")

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>FitTrack | Dashboard</title>
        <link rel="stylesheet" href="/static/css/main.css">
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap">
        <style>
            body {{
                margin: 0;
                font-family: 'DM Sans', sans-serif;
                background: #f6f8fb;
                color: #1f2937;
            }}

            .dashboard-page {{
                max-width: 1100px;
                margin: 0 auto;
                padding: 40px 24px;
            }}

            .topbar {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 32px;
            }}

            .brand {{
                font-family: 'Syne', sans-serif;
                font-size: 28px;
                font-weight: 800;
            }}

            .logout-form {{
                margin: 0;
            }}

            .logout-btn {{
                border: none;
                background: #111827;
                color: white;
                padding: 10px 16px;
                border-radius: 10px;
                cursor: pointer;
                font-weight: 500;
            }}

            .hero {{
                background: white;
                border-radius: 20px;
                padding: 28px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.06);
                margin-bottom: 24px;
            }}

            .hero h1 {{
                margin: 0 0 10px 0;
                font-family: 'Syne', sans-serif;
                font-size: 36px;
            }}

            .hero p {{
                margin: 0;
                font-size: 16px;
                color: #6b7280;
            }}

            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                gap: 18px;
                margin-bottom: 24px;
            }}

            .stat-card {{
                background: white;
                border-radius: 18px;
                padding: 22px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.05);
            }}

            .stat-card h3 {{
                margin: 0 0 8px 0;
                font-size: 15px;
                color: #6b7280;
                font-weight: 500;
            }}

            .stat-card p {{
                margin: 0;
                font-size: 28px;
                font-weight: 700;
            }}

            .section {{
                background: white;
                border-radius: 20px;
                padding: 24px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.05);
                margin-bottom: 24px;
            }}

            .section h2 {{
                margin-top: 0;
                font-family: 'Syne', sans-serif;
                font-size: 24px;
            }}

            .quick-links {{
                display: flex;
                flex-wrap: wrap;
                gap: 12px;
                margin-top: 16px;
            }}

            .quick-links a {{
                text-decoration: none;
                background: #2563eb;
                color: white;
                padding: 12px 18px;
                border-radius: 12px;
                font-weight: 500;
            }}

            .empty-state {{
                color: #6b7280;
                line-height: 1.6;
            }}
        </style>
    </head>
    <body>
        <div class="dashboard-page">

            <div class="topbar">
                <div class="brand">FitTrack</div>

                <form action="/logout" method="post" class="logout-form">
                    <button type="submit" class="logout-btn">Log out</button>
                </form>
            </div>

            <div class="hero">
                <h1>Hello, {user_name} 👋</h1>
                <p>
                    Welcome to your fitness dashboard. This is where you’ll manage your workouts,
                    track progress, and stay on top of your training goals.
                </p>
            </div>

            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Total Workouts</h3>
                    <p>0</p>
                </div>

                <div class="stat-card">
                    <h3>Total Minutes</h3>
                    <p>0</p>
                </div>

                <div class="stat-card">
                    <h3>Total Distance</h3>
                    <p>0 km</p>
                </div>

                <div class="stat-card">
                    <h3>Current Streak</h3>
                    <p>0 days</p>
                </div>
            </div>

            <div class="section">
                <h2>Quick Actions</h2>
                <p class="empty-state">
                    Start building the core features of your fitness system from here.
                </p>

                <div class="quick-links">
                    <a href="/activities/new">Log Activity</a>
                    <a href="/activities">View Activities</a>
                    <a href="/plan">Training Plan</a>
                    <a href="/competitions">Competitions</a>
                </div>
            </div>

            <div class="section">
                <h2>Recent Activity</h2>
                <p class="empty-state">
                    You haven’t logged any workouts yet. Once activity tracking is added,
                    your latest sessions will appear here.
                </p>
            </div>

        </div>
    </body>
    </html>
    """