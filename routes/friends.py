from flask import Blueprint, request, redirect, session, jsonify
from data import friends_store

friends = Blueprint("friends", __name__)


# /friends just redirects to /feed since the friends UI is on the feed page now
@friends.route("/friends")
def friends_page():
    if "user_id" not in session:
        return redirect("/login")
    return redirect("/feed")


# sends a friend request to another user
@friends.route("/friends/request/<user_id>", methods=["POST"])
def send_friend_request(user_id):
    if "user_id" not in session:
        return redirect("/login")

    friends_store.send_request(session["user_id"], user_id)
    return redirect("/feed")


# accepts an incoming friend request
@friends.route("/friends/accept/<request_id>", methods=["POST"])
def accept_friend_request(request_id):
    if "user_id" not in session:
        return redirect("/login")

    friends_store.accept_request(request_id, session["user_id"])
    return redirect("/feed")


# rejects an incoming friend request
@friends.route("/friends/reject/<request_id>", methods=["POST"])
def reject_friend_request(request_id):
    if "user_id" not in session:
        return redirect("/login")

    friends_store.reject_request(request_id, session["user_id"])
    return redirect("/feed")


# api endpoint for the friends search dropdown returns matching users as JSON
@friends.route("/api/users/search")
def search_users_api():
    if "user_id" not in session:
        return jsonify([])

    query = request.args.get("q", "").strip()

    if query == "":
        return jsonify([])

    results = friends_store.search_users(query, session["user_id"])
    return jsonify(results)
