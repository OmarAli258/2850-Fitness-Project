from flask import Flask
from routes.auth import auth

# Create the Flask app
app = Flask(__name__)

# Secret key is needed for sessions to work
# This is like a password that encrypts the session cookie
app.secret_key = "fittrack-secret-2025"

# Register the auth routes so Flask knows about /login /signup /logout
app.register_blueprint(auth)

# Home page - just shows two buttons for now
@app.route("/")
def home():
    return """
        <h1>FitTrack</h1>
        <a href='/login'>Login</a>
        <a href='/signup'>Sign Up</a>
    """

# Start the server on port 8080
if __name__ == "__main__":
    app.run(debug=True, port=8080)