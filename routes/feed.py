import uuid
from datetime import datetime

from flask import Blueprint, redirect, render_template, request, session
from data.database import get_connection

feed = Blueprint('feed', __name__)


#this helper checks that users can only interact with activities that are public on the feed
def _activity_is_public(cursor, activity_id):
    cursor.execute(
        """
        SELECT id FROM activities
        WHERE id = %s AND is_public = 1
        """,
        (activity_id,)
    )
    return cursor.fetchone() is not None


#this helper formats stored comment timestamps into a cleaner feed display
def _format_comment_time(timestamp):
    try:
        comment_time = datetime.fromisoformat(timestamp)
        return comment_time.strftime("%b %d, %Y at %I:%M %p").replace(" 0", " ")
    except ValueError:
        return timestamp

@feed.route('/feed')
def index():
    #this route loads public activities and adds social counts for likes and comments
    user_id = session.get("user_id")
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            activities.*,
            users.name as user_name,
            COALESCE(like_totals.like_count, 0) as like_count,
            COALESCE(comment_totals.comment_count, 0) as comment_count,
            CASE WHEN user_likes.id IS NULL THEN 0 ELSE 1 END as liked_by_user
        FROM activities
        JOIN users ON activities.user_id = users.id
        LEFT JOIN (
            SELECT activity_id, COUNT(*) as like_count
            FROM activity_likes
            GROUP BY activity_id
        ) like_totals ON like_totals.activity_id = activities.id
        LEFT JOIN (
            SELECT activity_id, COUNT(*) as comment_count
            FROM activity_comments
            GROUP BY activity_id
        ) comment_totals ON comment_totals.activity_id = activities.id
        LEFT JOIN activity_likes user_likes
            ON user_likes.activity_id = activities.id AND user_likes.user_id = %s
        WHERE activities.is_public = 1
        ORDER BY activities.date DESC
        """,
        (user_id,)
    )

    activities = [dict(row) for row in cursor.fetchall()]

    comments_by_activity = {}
    activity_ids = [activity["id"] for activity in activities]

    if activity_ids:
        cursor.execute(
            """
            SELECT activity_comments.*, users.name as user_name
            FROM activity_comments
            JOIN users ON activity_comments.user_id = users.id
            WHERE activity_comments.activity_id = ANY(%s)
            ORDER BY activity_comments.created_at ASC
            """,
            (activity_ids,)
        )

        for row in cursor.fetchall():
            comment = dict(row)
            comment["display_created_at"] = _format_comment_time(comment["created_at"])
            comments_by_activity.setdefault(comment["activity_id"], []).append(comment)

    for activity in activities:
        activity["comments"] = comments_by_activity.get(activity["id"], [])

    connection.close()

    return render_template('feed.html', feed_activities=activities)


@feed.route('/feed/<activity_id>/like', methods=["POST"])
def toggle_like(activity_id):
    #this route lets a logged in user like or unlike one public feed activity
    if "user_id" not in session:
        return redirect("/login")

    connection = get_connection()
    cursor = connection.cursor()

    if not _activity_is_public(cursor, activity_id):
        connection.close()
        return redirect("/feed")

    cursor.execute(
        """
        SELECT id FROM activity_likes
        WHERE activity_id = %s AND user_id = %s
        """,
        (activity_id, session["user_id"])
    )
    existing_like = cursor.fetchone()

    if existing_like:
        cursor.execute(
            """
            DELETE FROM activity_likes
            WHERE activity_id = %s AND user_id = %s
            """,
            (activity_id, session["user_id"])
        )
    else:
        cursor.execute(
            """
            INSERT INTO activity_likes (id, activity_id, user_id, created_at)
            VALUES (%s, %s, %s, %s)
            """,
            (str(uuid.uuid4()), activity_id, session["user_id"], datetime.now().isoformat(timespec="seconds"))
        )

    connection.commit()
    connection.close()
    return redirect(f"/feed#activity-{activity_id}")


@feed.route('/feed/<activity_id>/comments', methods=["POST"])
def add_comment(activity_id):
    #this route saves a new comment on a public feed activity for the logged in user
    if "user_id" not in session:
        return redirect("/login")

    body = request.form.get("comment", "").strip()
    if body == "":
        return redirect(f"/feed#activity-{activity_id}")

    connection = get_connection()
    cursor = connection.cursor()

    if not _activity_is_public(cursor, activity_id):
        connection.close()
        return redirect("/feed")

    cursor.execute(
        """
        INSERT INTO activity_comments (id, activity_id, user_id, body, created_at)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (str(uuid.uuid4()), activity_id, session["user_id"], body, datetime.now().isoformat(timespec="seconds"))
    )

    connection.commit()
    connection.close()
    return redirect(f"/feed#activity-{activity_id}")


@feed.route('/feed/comments/<comment_id>/delete', methods=["POST"])
def delete_comment(comment_id):
    #this route lets users delete comments they wrote on the feed
    if "user_id" not in session:
        return redirect("/login")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT activity_id FROM activity_comments
        WHERE id = %s AND user_id = %s
        """,
        (comment_id, session["user_id"])
    )
    comment = cursor.fetchone()

    if comment is None:
        connection.close()
        return redirect("/feed")

    activity_id = comment["activity_id"]

    cursor.execute(
        """
        DELETE FROM activity_comments
        WHERE id = %s AND user_id = %s
        """,
        (comment_id, session["user_id"])
    )

    connection.commit()
    connection.close()
    return redirect(f"/feed#activity-{activity_id}")
