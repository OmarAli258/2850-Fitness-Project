from flask import Blueprint, render_template, redirect, session, request
from data.database import get_connection
from data import friends_store

feed = Blueprint("feed", __name__)


@feed.route("/feed")
def index():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    view = request.args.get("view", "friends")

    friends_list = friends_store.get_friends(user_id)
    pending = friends_store.get_pending_requests(user_id)
    friend_ids = friends_store.get_friend_ids(user_id)

    activities = []
    connection = get_connection()
    cursor = connection.cursor()

    if view == "everyone":
        cursor.execute("""
            SELECT activities.*, users.name as user_name
            FROM activities
            JOIN users ON activities.user_id = users.id
            WHERE activities.is_public = 1
            ORDER BY activities.date DESC
        """)
        activities = [dict(row) for row in cursor.fetchall()]
    elif friend_ids:
        placeholders = ",".join(["%s"] * len(friend_ids))
        cursor.execute(
            f"""
            SELECT activities.*, users.name as user_name
            FROM activities
            JOIN users ON activities.user_id = users.id
            WHERE activities.is_public = 1 AND activities.user_id IN ({placeholders})
            ORDER BY activities.date DESC
        """,
            friend_ids,
        )
        activities = [dict(row) for row in cursor.fetchall()]

    connection.close()

    return render_template(
        "feed.html",
        feed_activities=activities,
        friends=friends_list,
        pending=pending,
        view=view,
    )
