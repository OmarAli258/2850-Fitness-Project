from flask import Blueprint, session, redirect, render_template

dashboard = Blueprint("dashboard", __name__)


@dashboard.route("/dashboard")
def show_dashboard():
    if "user_id" not in session:
        return redirect("/login")

    user_name = session.get("user_name", "User")

    return render_template("dashboard.html", user_name=user_name)

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>FitTrack | Dashboard</title>
        <link rel="stylesheet" href="/static/css/main.css">
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap">
    </head>
    <body>

        <!-- Top navigation bar -->
        <nav class="navbar">
    <div class="nav-brand">
        <a href="/">⚡ FitTrack</a>
    </div>
    <div class="nav-actions">
        <span style="color: #7a7a8a; font-size: 0.9rem; font-weight: 500;">👤 {user_name}</span>
        <form action="/logout" method="post" style="display:inline; margin:0;">
            <button type="submit" class="btn btn-ghost">Log out</button>
        </form>
    </div>
</nav>

        <!-- Main content -->
        <div style="max-width: 1000px; margin: 0 auto; padding: 3rem 5%;">

            <!-- Welcome section -->
            <div style="margin-bottom: 2.5rem;">
                <h1 style="font-family: 'Syne', sans-serif; font-size: 2.5rem; margin-bottom: 0.4rem;">
                    Hello, {user_name} 👋
                </h1>
                <p style="color: #7a7a8a;">Welcome back. Here is your training overview.</p>
            </div>

            <!-- Stats cards -->
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2.5rem;">

                <div class="stat-card">
                    <span class="stat-icon">🏃</span>
                    <strong class="stat-value">0</strong>
                    <span class="stat-label">Total Workouts</span>
                    <span class="stat-sub">sessions logged</span>
                </div>

                <div class="stat-card">
                    <span class="stat-icon">⏱</span>
                    <strong class="stat-value">0</strong>
                    <span class="stat-label">Total Minutes</span>
                    <span class="stat-sub">time spent training</span>
                </div>

                <div class="stat-card">
                    <span class="stat-icon">📍</span>
                    <strong class="stat-value">0 km</strong>
                    <span class="stat-label">Total Distance</span>
                    <span class="stat-sub">across all sessions</span>
                </div>

                <div class="stat-card">
                    <span class="stat-icon">🔥</span>
                    <strong class="stat-value">0</strong>
                    <span class="stat-label">This Week</span>
                    <span class="stat-sub">activities in last 7 days</span>
                </div>

            </div>

            <!-- Quick actions -->
            <div style="background: #141417; border: 1px solid #2a2a32; border-radius: 12px; padding: 1.8rem; margin-bottom: 1.5rem;">
                <h2 style="font-family: 'Syne', sans-serif; margin-top: 0; margin-bottom: 1rem;">Quick Actions</h2>
                <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
                    <a href="/activities/new" class="btn btn-primary">Log Activity</a>
                    <a href="/activities" class="btn btn-ghost">View Activities</a>
                </div>
            </div>

            <!-- Recent activity -->
            <div style="background: #141417; border: 1px solid #2a2a32; border-radius: 12px; padding: 1.8rem;">
                <h2 style="font-family: 'Syne', sans-serif; margin-top: 0; margin-bottom: 1rem;">Recent Activity</h2>
                <p style="color: #7a7a8a;">
                    You have not logged any workouts yet.
                    Once you start adding activities, they will appear here.
                </p>
            </div>

        </div>

        <!-- Footer -->
        <footer class="site-footer">
            <p>© 2025 FitTrack · Built for COMP2850</p>
        </footer>

    </body>
    </html>
    """