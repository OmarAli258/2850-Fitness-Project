from flask import Blueprint, request, session, redirect
from data import activity_store
import datetime

activities = Blueprint("activities", __name__)


@activities.route("/activities/create" \
"", methods=["GET"])
def show_activity_form():
    if "user_id" not in session:
        return redirect("/login")

    return activity_form()


@activities.route("/activities/create", methods=["POST"])
def save_activity():
    if "user_id" not in session:
        return redirect("/login")

    activity_type = request.form.get("activity_type", "").strip()
    custom_activity = request.form.get("custom_activity", "").strip()
    date = request.form.get("date", "").strip()
    duration = request.form.get("duration", "").strip()
    distance = request.form.get("distance", "").strip()
    notes = request.form.get("notes", "").strip()

    if activity_type == "":
        return activity_form(error="Please choose an activity type.")

    if activity_type == "Other":
        if custom_activity == "":
            return activity_form(error="Please enter a custom activity type.")
        activity_type = custom_activity

    if date == "":
        return activity_form(error="Please choose a date.")

    if duration == "":
        return activity_form(error="Please enter the duration.")

    if not duration.isdigit():
        return activity_form(error="Duration must be a number.")

    activity_store.create_activity(
        user_id=session["user_id"],
        activity_type=activity_type,
        date=date,
        duration=duration,
        distance=distance,
        notes=notes
    )

    return redirect("/activities")


def edit_activity_form(activity, error=""):
    error_html = ""

    if error != "":
        error_html = f"<p style='color:red;'><strong>{error}</strong></p>"

    # Determine if it's a custom type
    predefined = ["Running", "Walking", "Cycling", "Swimming", "Gym"]
    is_custom = activity["type"] not in predefined
    selected_type = activity["type"] if not is_custom else "Other"
    custom_value = activity["type"] if is_custom else ""

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>FitTrack | Edit Activity</title>
        <link rel="stylesheet" href="/static/css/style.css">
    </head>
    <body>
        <nav>
            <a href="/">FitTrack</a>
            <ul>
                <li><a href="/">Home</a></li>
                <li><a href="/activities">Activities</a></li>
                <li><a href="/dashboard">Dashboard</a></li>
                <li><a href="/racetracker">Racetracker</a></li>
                <li><a href="/login">Login</a></li>
                <li><a href="/signup">Sign up</a></li>
            </ul>
        </nav>
        <main style="padding: 2rem 5%; display: flex; justify-content: center; align-items: center; min-height: 80vh;">
            <div style="background: var(--card); border: 2px solid var(--border); border-radius: 8px; padding: 2rem; width: 100%; max-width: 500px;">
                <h1 style="text-align: center; margin-bottom: 1rem;">Edit Activity</h1>
                <p style="text-align: center; color: var(--text-muted); margin-bottom: 2rem;">Update your activity details.</p>

                {error_html}

                <form action="/activities/edit/{activity['id']}" method="post" style="display: flex; flex-direction: column; gap: 1rem;">
                    <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                        <label for="activity_type" style="font-weight: bold;">Activity Type</label>
                        <select name="activity_type" id="activity_type" style="padding: 0.8rem; border: 1px solid var(--border); border-radius: 6px; background: var(--bg); color: var(--text);">
                            <option value="">Select one</option>
                            <option value="Running" {'selected' if selected_type == 'Running' else ''}>Running</option>
                            <option value="Walking" {'selected' if selected_type == 'Walking' else ''}>Walking</option>
                            <option value="Cycling" {'selected' if selected_type == 'Cycling' else ''}>Cycling</option>
                            <option value="Swimming" {'selected' if selected_type == 'Swimming' else ''}>Swimming</option>
                            <option value="Gym" {'selected' if selected_type == 'Gym' else ''}>Gym</option>
                            <option value="Other" {'selected' if selected_type == 'Other' else ''}>Other</option>
                        </select>
                        <input type="text" name="custom_activity" id="custom_activity" placeholder="Enter custom activity type" value="{custom_value}" style="padding: 0.8rem; border: 1px solid var(--border); border-radius: 6px; background: var(--bg); color: var(--text); display: {'block' if is_custom else 'none'};">
                    </div>

                    <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                        <label for="date" style="font-weight: bold;">Date</label>
                        <input type="date" name="date" id="date" value="{activity['date']}" style="padding: 0.8rem; border: 1px solid var(--border); border-radius: 6px; background: var(--bg); color: var(--text);">
                    </div>

                    <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                        <label for="duration" style="font-weight: bold;">Duration (minutes)</label>
                        <input type="text" name="duration" id="duration" placeholder="e.g. 45" value="{activity['duration']}" style="padding: 0.8rem; border: 1px solid var(--border); border-radius: 6px; background: var(--bg); color: var(--text);">
                    </div>

                    <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                        <label for="distance" style="font-weight: bold;">Distance (optional)</label>
                        <input type="text" name="distance" id="distance" placeholder="e.g. 5 km" value="{activity['distance']}" style="padding: 0.8rem; border: 1px solid var(--border); border-radius: 6px; background: var(--bg); color: var(--text);">
                    </div>

                    <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                        <label for="notes" style="font-weight: bold;">Notes (optional)</label>
                        <textarea name="notes" id="notes" rows="4" style="padding: 0.8rem; border: 1px solid var(--border); border-radius: 6px; background: var(--bg); color: var(--text); resize: vertical;">{activity['notes']}</textarea>
                    </div>

                    <button type="submit" class="btn btna" style="align-self: flex-start;">Save Changes</button>
                </form>

                <p style="text-align: center; margin-top: 1rem;"><a href="/activities" style="color: var(--yellow);">Back to activities</a></p>
            </div>
        </main>
        <script>
            document.getElementById('activity_type').addEventListener('change', function() {{
                var customInput = document.getElementById('custom_activity');
                if (this.value === 'Other') {{
                    customInput.style.display = 'block';
                    customInput.required = true;
                }} else {{
                    customInput.style.display = 'none';
                    customInput.required = false;
                }}
            }});
        </script>
    </body>
    </html>
    """


@activities.route("/activities/edit/<activity_id>", methods=["GET"])
def show_edit_activity(activity_id):
    if "user_id" not in session:
        return redirect("/login")

    activity = activity_store.get_activity_by_id(activity_id, session["user_id"])
    if not activity:
        return redirect("/activities")

    return edit_activity_form(activity)


@activities.route("/activities/edit/<activity_id>", methods=["POST"])
def save_edit_activity(activity_id):
    if "user_id" not in session:
        return redirect("/login")

    activity_type = request.form.get("activity_type", "").strip()
    custom_activity = request.form.get("custom_activity", "").strip()
    date = request.form.get("date", "").strip()
    duration = request.form.get("duration", "").strip()
    distance = request.form.get("distance", "").strip()
    notes = request.form.get("notes", "").strip()

    if activity_type == "":
        return edit_activity_form(activity_store.get_activity_by_id(activity_id, session["user_id"]), error="Please choose an activity type.")

    if activity_type == "Other":
        if custom_activity == "":
            return edit_activity_form(activity_store.get_activity_by_id(activity_id, session["user_id"]), error="Please enter a custom activity type.")
        activity_type = custom_activity

    if date == "":
        return edit_activity_form(activity_store.get_activity_by_id(activity_id, session["user_id"]), error="Please choose a date.")

    if duration == "":
        return edit_activity_form(activity_store.get_activity_by_id(activity_id, session["user_id"]), error="Please enter the duration.")

    if not duration.isdigit():
        return edit_activity_form(activity_store.get_activity_by_id(activity_id, session["user_id"]), error="Duration must be a number.")

    success = activity_store.update_activity(activity_id, session["user_id"], activity_type, date, duration, distance, notes)
    if not success:
        return redirect("/activities")

    return redirect("/activities")


@activities.route("/activities/delete/<activity_id>", methods=["POST"])
def delete_activity(activity_id):
    if "user_id" not in session:
        return redirect("/login")

    activity_store.delete_activity(activity_id, session["user_id"])
    return redirect("/activities")


@activities.route("/activities", methods=["GET"])
def show_activities():
    if "user_id" not in session:
        return redirect("/login")

    user_name = session.get("user_name", "User")
    filter_type = request.args.get("filter_type", "").strip()

    activities_list = activity_store.get_activities_for_user(session["user_id"])
    total_activities = len(activities_list)

    # Get unique activity types for filter
    all_types = sorted(set(a["type"] for a in activities_list))

    if filter_type:
        activities_list = [a for a in activities_list if a["type"] == filter_type]

    today = datetime.date.today()
    upcoming_activities = []
    past_activities = []

    for activity in activities_list:
        try:
            activity_date = datetime.date.fromisoformat(activity["date"])
        except ValueError:
            activity_date = today

        if activity_date > today:
            upcoming_activities.append((activity_date, activity))
        else:
            past_activities.append((activity_date, activity))

    upcoming_activities.sort(key=lambda item: item[0])
    past_activities.sort(key=lambda item: item[0], reverse=True)

    upcoming_count = len(upcoming_activities)
    past_count = len(past_activities)
    displayed_activities = upcoming_count + past_count
    latest_activity = past_activities[0][1] if past_activities else (upcoming_activities[-1][1] if upcoming_activities else None)

    def render_activity_card(activity):
        distance = activity["distance"] or "Not given"
        notes = activity["notes"] or "No notes"
        return f"""
            <article class="activity-card">
                <div>
                    <h3>{activity['type']}</h3>
                    <p class="card-pill">{activity['date']}</p>
                </div>
                <div class="activity-details">
                    <p><strong>Duration:</strong> {activity['duration']} minutes</p>
                    <p><strong>Distance:</strong> {distance}</p>
                    <p><strong>Notes:</strong> {notes}</p>
                </div>
                <div class="card-actions">
                    <a href="/activities/edit/{activity['id']}" class="btn btna">Edit</a>
                    <form action="/activities/delete/{activity['id']}" method="post" style="display: inline;" onsubmit="return confirm('Are you sure you want to delete this activity?');">
                        <button type="submit" class="btn btn-ghost" style="color: #ff4d4d; border-color: rgba(255, 77, 77, 0.35);">Delete</button>
                    </form>
                </div>
            </article>
        """

    def render_section(title, activities):
        if not activities:
            return f"""
            <div class="section-empty">
                <h2>{title}</h2>
                <p>No activities in this section yet.</p>
            </div>
            """

        section_html = f'<div class="activity-section"><h2>{title}</h2><div class="activities-grid">'
        for _, activity in activities:
            section_html += render_activity_card(activity)
        section_html += '</div></div>'
        return section_html

    if displayed_activities == 0:
        activity_html = """
        <div class="empty-state">
            <h2>Log your first activity</h2>
            <p>Start tracking workouts, runs, and strength sessions to build your activity history.</p>
            <a href="/activities/create" class="btn btna">Add an activity</a>
        </div>
        """
    else:
        activity_html = render_section("Upcoming Activities", upcoming_activities)
        activity_html += render_section("Past Activities", past_activities)

    filter_options = '<option value="">All Activities</option>'
    for typ in all_types:
        selected = ' selected' if filter_type == typ else ''
        filter_options += f'<option value="{typ}"{selected}>{typ}</option>'

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>FitTrack | Activities</title>
        <link rel="stylesheet" href="/static/css/style.css">
    </head>
    <body>
        <nav>
            <a href="/">FitTrack</a>
            <ul>
                <li><a href="/">Home</a></li>
                <li><a href="/activities">Activities</a></li>
                <li><a href="/dashboard">Dashboard</a></li>
                <li><a href="/racetracker">Racetracker</a></li>
                <li><a href="/login"></a></li>
                <li><a href="/signup"></a></li>
            </ul>
        </nav>
        <main class="activities-page">
            <section class="activities-header">
                <div>
                    <p class="page-label">Activity Log</p>
                    <h1>{user_name}'s Activities</h1>
                </div>
                <div class="activities-tools">
                    <form action="/activities" method="get" style="display: flex; gap: 0.75rem; align-items: center; flex-wrap: wrap;">
                        <label for="filter_type" style="font-weight: 700;">Filter by type:</label>
                        <select name="filter_type" id="filter_type" style="padding: 0.8rem; border: 1px solid var(--border); border-radius: 8px; background: var(--card); color: var(--text); min-width: 180px;">
                            {filter_options}
                        </select>
                        <button type="submit" class="btn btn-ghost">Filter</button>
                    </form>
                    <a href="/activities/create" class="btn btna">Log a new activity</a>
                </div>
            </section>
            <section class="activities-summary">
                <div class="summary-card">
                    <strong>{total_activities}</strong>
                    Total activities logged
                </div>
                <div class="summary-card">
                    <strong>{upcoming_count}</strong>
                    Upcoming activities
                </div>
                <div class="summary-card">
                    <strong>{past_count}</strong>
                    Past activities
                </div>
            </section>
            <section class="activity-list">
                {activity_html}
            </section>
        </main>
    </body>
    </html>
    """


def activity_form(error=""):
    error_html = ""

    if error != "":
        error_html = f"<p style='color:red;'><strong>{error}</strong></p>"

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>FitTrack | Log Activity</title>
        <link rel="stylesheet" href="/static/css/style.css">
    </head>
    <body>
        <nav>
            <a href="/">FitTrack</a>
            <ul>
                <li><a href="/">Home</a></li>
                <li><a href="/activities">Activities</a></li>
                <li><a href="/dashboard">Dashboard</a></li>
                <li><a href="/racetracker">Racetracker</a></li>
                <li><a href="/login"></a></li>
                <li><a href="/signup"></a></li>
            </ul>
        </nav>
        <main style="padding: 2rem 5%; display: flex; justify-content: center; align-items: center; min-height: 80vh;">
            <div style="background: var(--card); border: 2px solid var(--border); border-radius: 8px; padding: 2rem; width: 100%; max-width: 500px;">
                <h1 style="text-align: center; margin-bottom: 1rem;">Log a Workout</h1>
                <p style="text-align: center; color: var(--text-muted); margin-bottom: 2rem;">Add your activity below.</p>

                {error_html}

                <form action="/activities/create" method="post" style="display: flex; flex-direction: column; gap: 1rem;">
                    <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                        <label for="activity_type" style="font-weight: bold;">Activity Type</label>
                        <select name="activity_type" id="activity_type" style="padding: 0.8rem; border: 1px solid var(--border); border-radius: 6px; background: var(--bg); color: var(--text);">
                            <option value="">Select one</option>
                            <option value="Running">Running</option>
                            <option value="Walking">Walking</option>
                            <option value="Cycling">Cycling</option>
                            <option value="Swimming">Swimming</option>
                            <option value="Gym">Gym</option>
                            <option value="Other">Other</option>
                        </select>
                        <input type="text" name="custom_activity" id="custom_activity" placeholder="Enter custom activity type" style="padding: 0.8rem; border: 1px solid var(--border); border-radius: 6px; background: var(--bg); color: var(--text); display: none;">
                    </div>

                    <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                        <label for="date" style="font-weight: bold;">Date</label>
                        <input type="date" name="date" id="date" style="padding: 0.8rem; border: 1px solid var(--border); border-radius: 6px; background: var(--bg); color: var(--text);">
                    </div>

                    <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                        <label for="duration" style="font-weight: bold;">Duration (minutes)</label>
                        <input type="text" name="duration" id="duration" placeholder="e.g. 45" style="padding: 0.8rem; border: 1px solid var(--border); border-radius: 6px; background: var(--bg); color: var(--text);">
                    </div>

                    <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                        <label for="distance" style="font-weight: bold;">Distance (optional)</label>
                        <input type="text" name="distance" id="distance" placeholder="e.g. 5 km" style="padding: 0.8rem; border: 1px solid var(--border); border-radius: 6px; background: var(--bg); color: var(--text);">
                    </div>

                    <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                        <label for="notes" style="font-weight: bold;">Notes (optional)</label>
                        <textarea name="notes" id="notes" rows="4" style="padding: 0.8rem; border: 1px solid var(--border); border-radius: 6px; background: var(--bg); color: var(--text); resize: vertical;"></textarea>
                    </div>

                    <button type="submit" class="btn btna" style="align-self: flex-start;">Save Activity</button>
                </form>

                <p style="text-align: center; margin-top: 1rem;"><a href="/dashboard" style="color: var(--yellow);">Back to dashboard</a></p>
            </div>
        </main>
        <script>
            document.getElementById('activity_type').addEventListener('change', function() {{
                var customInput = document.getElementById('custom_activity');
                if (this.value === 'Other') {{
                    customInput.style.display = 'block';
                    customInput.required = true;
                }} else {{
                    customInput.style.display = 'none';
                    customInput.required = false;
                }}
            }});
        </script>
    </body>
    </html>
    """