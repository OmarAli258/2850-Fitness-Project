from flask import Blueprint, render_template, redirect, session, request, jsonify
from data.database import get_connection
from data import friends_store
from datetime import datetime
import uuid

feed = Blueprint('feed', __name__)

@feed.route('/feed')
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
        placeholders = ','.join(['%s'] * len(friend_ids))
        cursor.execute(f"""
            SELECT activities.*, users.name as user_name
            FROM activities
            JOIN users ON activities.user_id = users.id
            WHERE activities.is_public = 1 AND activities.user_id IN ({placeholders})
            ORDER BY activities.date DESC
        """, friend_ids)
        activities = [dict(row) for row in cursor.fetchall()]
    else:
        cursor.execute("""
            SELECT activities.*, users.name as user_name
            FROM activities
            JOIN users ON activities.user_id = users.id
            WHERE activities.is_public = 1 AND activities.user_id = %s
            ORDER BY activities.date DESC
        """, (user_id,))
        activities = [dict(row) for row in cursor.fetchall()]

    for activity in activities:
        cursor.execute("SELECT COUNT(*) as count FROM activity_likes WHERE activity_id = %s", (activity['id'],))
        activity['like_count'] = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM activity_likes WHERE activity_id = %s AND user_id = %s", (activity['id'], user_id))
        activity['liked_by_user'] = cursor.fetchone()['count'] > 0

        cursor.execute("""
            SELECT ac.*, u.name as user_name
            FROM activity_comments ac
            JOIN users u ON ac.user_id = u.id
            WHERE ac.activity_id = %s
            ORDER BY ac.created_at ASC
        """, (activity['id'],))
        activity['comments'] = [dict(row) for row in cursor.fetchall()]
        activity['comment_count'] = len(activity['comments'])

        type_messages = {
            'Running': 'went for a run',
            'Cycling': 'went cycling',
            'Swimming': 'went swimming',
            'Gym': 'hit the gym',
            'Walking': 'went for a walk',
            'Yoga': 'did yoga',
            'Hiking': 'went hiking',
            'Rowing': 'went rowing',
            'Football': 'played football',
            'Other': 'did a workout'
        }
        activity['feed_message'] = type_messages.get(activity['type'], 'did an activity')

    connection.close()

    return render_template(
        'feed.html',
        feed_activities=activities,
        friends=friends_list,
        pending=pending,
        view=view
    )


@feed.route('/feed/<activity_id>/like', methods=['POST'])
def toggle_like(activity_id):
    if "user_id" not in session:
        return redirect("/login")

    try:
        user_id = session["user_id"]
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT id FROM activity_likes WHERE activity_id = %s AND user_id = %s", (activity_id, user_id))
        existing_like = cursor.fetchone()

        if existing_like:
            cursor.execute("DELETE FROM activity_likes WHERE activity_id = %s AND user_id = %s", (activity_id, user_id))
        else:
            like_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO activity_likes (id, activity_id, user_id, created_at)
                VALUES (%s, %s, %s, %s)
            """, (like_id, activity_id, user_id, datetime.now().isoformat()))

        connection.commit()
        connection.close()
    except Exception as e:
        print(f"Error toggling like: {e}")
        return f"Error: {str(e)}", 500

    view = request.args.get("view", "friends")
    return redirect(f"/feed?view={view}")


@feed.route('/feed/<activity_id>/comments', methods=['POST'])
def add_comment(activity_id):
    if "user_id" not in session:
        return redirect("/login")

    try:
        user_id = session["user_id"]
        comment_text = request.form.get('comment', '').strip()

        if not comment_text:
            return redirect("/feed")

        connection = get_connection()
        cursor = connection.cursor()

        comment_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO activity_comments (id, activity_id, user_id, body, created_at)
            VALUES (%s, %s, %s, %s, %s)
        """, (comment_id, activity_id, user_id, comment_text, datetime.now().isoformat()))

        connection.commit()
        connection.close()
    except Exception as e:
        print(f"Error adding comment: {e}")
        return f"Error: {str(e)}", 500

    view = request.args.get("view", "friends")
    return redirect(f"/feed?view={view}")


@feed.route('/feed/comments/<comment_id>/delete', methods=['POST'])
def delete_comment(comment_id):
    if "user_id" not in session:
        return redirect("/login")

    try:
        user_id = session["user_id"]
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT user_id FROM activity_comments WHERE id = %s", (comment_id,))
        comment = cursor.fetchone()

        if comment and comment['user_id'] == user_id:
            cursor.execute("DELETE FROM activity_comments WHERE id = %s", (comment_id,))
            connection.commit()

        connection.close()
    except Exception as e:
        print(f"Error deleting comment: {e}")
        return f"Error: {str(e)}", 500

    view = request.args.get("view", "friends")
    return redirect(f"/feed?view={view}")
