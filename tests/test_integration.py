from werkzeug.security import generate_password_hash


class TestAuthenticationFlow:
    # register with valid details redirects to dashboard
    def test_register_success_redirects_to_dashboard(self, client, db_connection):
        response = client.post(
            "/signup",
            data={
                "name": "New User",
                "email": "newuser@example.com",
                "password": "password123",
                "confirm": "password123",
            },
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert "/dashboard" in response.location

    # confirms user actually gets saved in the database after signup
    def test_register_creates_user_in_database(self, client, db_connection):
        client.post(
            "/signup",
            data={
                "name": "DB Test User",
                "email": "dbtest@example.com",
                "password": "password123",
                "confirm": "password123",
            },
        )

        cursor = db_connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", ("dbtest@example.com",))
        user = cursor.fetchone()

        assert user is not None
        assert user["name"] == "DB Test User"
        assert user["email"] == "dbtest@example.com"

    # login with correct credentials redirects to dashboard
    def test_login_success_redirects_to_dashboard(self, client, db_connection):
        cursor = db_connection.cursor()
        cursor.execute(
            "INSERT INTO users (id, name, email, password) VALUES (?, ?, ?, ?)",
            (
                "user-login-id",
                "Login User",
                "login@example.com",
                generate_password_hash("secret123"),
            ),
        )
        db_connection.commit()

        response = client.post(
            "/login",
            data={"email": "login@example.com", "password": "secret123"},
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert "/dashboard" in response.location

    # login with wrong password shows error message
    def test_login_invalid_credentials_shows_error(self, client, db_connection):
        cursor = db_connection.cursor()
        cursor.execute(
            "INSERT INTO users (id, name, email, password) VALUES (?, ?, ?, ?)",
            (
                "existing-user",
                "Existing",
                "existing@example.com",
                generate_password_hash("correctpassword"),
            ),
        )
        db_connection.commit()

        response = client.post(
            "/login",
            data={"email": "existing@example.com", "password": "wrongpassword"},
            follow_redirects=True,
        )

        assert b"Invalid email or password" in response.data

    # login with email that doesnt exist shows error message
    def test_login_nonexistent_user_shows_error(self, client):
        response = client.post(
            "/login",
            data={"email": "nobody@example.com", "password": "anypassword"},
            follow_redirects=True,
        )

        assert b"Invalid email or password" in response.data


class TestActivityCRUD:
    # creating an activity saves it to the database
    def test_create_activity_appears_in_database(
        self, authenticated_client, db_connection
    ):
        response = authenticated_client.post(
            "/activities/new",
            data={
                "activity_type": "Running",
                "date": "2025-05-01",
                "duration": "30",
                "duration_unit": "minutes",
                "distance": "5.0",
                "notes": "Morning run",
                "visibility": "private",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200

        cursor = db_connection.cursor()
        cursor.execute("SELECT * FROM activities WHERE user_id = ?", ("test-user-id",))
        activity = cursor.fetchone()

        assert activity is not None
        assert activity["type"] == "Running"
        assert activity["duration"] == 30
        assert activity["distance"] == "5.0"
        assert activity["notes"] == "Morning run"

    # creating an activity redirects to the activities list page
    def test_create_activity_redirects_to_activities_list(self, authenticated_client):
        response = authenticated_client.post(
            "/activities/new",
            data={
                "activity_type": "Cycling",
                "date": "2025-05-02",
                "duration": "60",
                "duration_unit": "minutes",
                "distance": "15.0",
                "notes": "Bike ride",
                "visibility": "private",
            },
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert "/activities" in response.location

    # viewing the activities page shows the created activity
    def test_view_activities_shows_created_activity(self, authenticated_client):
        authenticated_client.post(
            "/activities/new",
            data={
                "activity_type": "Swimming",
                "date": "2025-05-03",
                "duration": "45",
                "duration_unit": "minutes",
                "distance": "1.5",
                "notes": "Pool session",
                "visibility": "private",
            },
        )

        response = authenticated_client.get("/activities", follow_redirects=True)
        assert response.status_code == 200
        assert b"Swimming" in response.data
        assert b"45" in response.data

    # deleting an activity removes it from the database
    def test_delete_activity_removes_from_database(
        self, authenticated_client, db_connection
    ):
        cursor = db_connection.cursor()
        cursor.execute(
            "INSERT INTO activities (id, user_id, type, date, duration, distance, notes, is_public) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                "activity-to-delete",
                "test-user-id",
                "Running",
                "2025-05-04",
                30,
                "5.0",
                "To be deleted",
                0,
            ),
        )
        db_connection.commit()

        response = authenticated_client.post(
            "/activities/activity-to-delete/delete", follow_redirects=True
        )
        assert response.status_code == 200

        cursor.execute("SELECT * FROM activities WHERE id = ?", ("activity-to-delete",))
        activity = cursor.fetchone()
        assert activity is None

    # deleting an activity redirects back to activities list
    def test_delete_activity_redirects_to_activities_list(
        self, authenticated_client, db_connection
    ):
        cursor = db_connection.cursor()
        cursor.execute(
            "INSERT INTO activities (id, user_id, type, date, duration, distance, notes, is_public) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                "activity-delete-redirect",
                "test-user-id",
                "Walking",
                "2025-05-05",
                20,
                "2.0",
                "Test redirect",
                0,
            ),
        )
        db_connection.commit()

        response = authenticated_client.post(
            "/activities/activity-delete-redirect/delete", follow_redirects=False
        )
        assert response.status_code == 302
        assert "/activities" in response.location
