from flask import Blueprint, render_template
from data.database import get_connection

feed = Blueprint('feed', __name__)

@feed.route('/feed')
def index():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT activities.*, users.name as user_name
        FROM activities
        JOIN users ON activities.user_id = users.id
        ORDER BY activities.date DESC
    """)

    activities = [dict(row) for row in cursor.fetchall()]
    connection.close()

    return render_template('feed.html', feed_activities=activities)