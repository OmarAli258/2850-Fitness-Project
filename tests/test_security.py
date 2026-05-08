from werkzeug.security import generate_password_hash


class TestRouteProtection:
    # unauthenticated user trying to access dashboard gets redirected to login
    def test_unauthenticated_user_cannot_access_dashboard(self, client):
        response = client.get("/dashboard", follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.location

    # unauthenticated user trying to access activities page gets redirected to login
    def test_unauthenticated_user_cannot_access_activities(self, client):
        response = client.get("/activities", follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.location

    # unauthenticated user trying to access activity form gets redirected to login
    def test_unauthenticated_user_cannot_access_activity_form(self, client):
        response = client.get("/activities/new", follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.location

    # unauthenticated user trying to delete activity gets redirected to login
    def test_unauthenticated_user_cannot_delete_activity(self, client):
        response = client.post("/activities/some-id/delete", follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.location


class TestSQLInjection:
    # trying to bypass login using sql injection in the email field
    def test_sql_injection_in_login_email_field_fails_safely(
        self, client, db_connection
    ):
        cursor = db_connection.cursor()
        cursor.execute(
            "INSERT INTO users (id, name, email, password) VALUES (?, ?, ?, ?)",
            (
                "sql-test-user",
                "SQL Test",
                "sqlinjection@test.com",
                generate_password_hash("realpassword"),
            ),
        )
        db_connection.commit()

        response = client.post(
            "/login",
            data={"email": "' OR '1'='1", "password": "anything"},
            follow_redirects=True,
        )

        assert b"Invalid email or password" in response.data

    # trying to bypass login using sql injection in the password field
    def test_sql_injection_in_login_password_field_fails_safely(
        self, client, db_connection
    ):
        cursor = db_connection.cursor()
        cursor.execute(
            "INSERT INTO users (id, name, email, password) VALUES (?, ?, ?, ?)",
            (
                "sql-test-user-2",
                "SQL Test 2",
                "sqlinjection2@test.com",
                generate_password_hash("realpassword"),
            ),
        )
        db_connection.commit()

        response = client.post(
            "/login",
            data={"email": "sqlinjection2@test.com", "password": "' OR '1'='1"},
            follow_redirects=True,
        )

        assert b"Invalid email or password" in response.data

    # trying a more complex sql injection attack with union select
    def test_sql_injection_multiple_conditions_fails_safely(
        self, client, db_connection
    ):
        cursor = db_connection.cursor()
        cursor.execute(
            "INSERT INTO users (id, name, email, password) VALUES (?, ?, ?, ?)",
            (
                "sql-test-user-3",
                "SQL Test 3",
                "sqlinjection3@test.com",
                generate_password_hash("realpassword"),
            ),
        )
        db_connection.commit()

        response = client.post(
            "/login",
            data={
                "email": "test@test.com' UNION SELECT 1,2,3,4--",
                "password": "anything",
            },
            follow_redirects=True,
        )

        assert b"Invalid email or password" in response.data


class TestInputValidation:
    # submitting negative duration should be rejected with error
    def test_negative_duration_rejected(self, authenticated_client):
        response = authenticated_client.post(
            "/activities/new",
            data={
                "activity_type": "Running",
                "date": "2025-05-01",
                "duration": "-10",
                "duration_unit": "minutes",
                "distance": "5.0",
                "notes": "Test",
                "visibility": "private",
            },
            follow_redirects=True,
        )

        assert b"Duration must be more than 0" in response.data

    # submitting negative distance should be rejected with error
    def test_negative_distance_rejected(self, authenticated_client):
        response = authenticated_client.post(
            "/activities/new",
            data={
                "activity_type": "Running",
                "date": "2025-05-01",
                "duration": "30",
                "duration_unit": "minutes",
                "distance": "-5.0",
                "notes": "Test",
                "visibility": "private",
            },
            follow_redirects=True,
        )

        assert b"Distance cannot be negative" in response.data

    # submitting zero duration should be rejected with error
    def test_zero_duration_rejected(self, authenticated_client):
        response = authenticated_client.post(
            "/activities/new",
            data={
                "activity_type": "Running",
                "date": "2025-05-01",
                "duration": "0",
                "duration_unit": "minutes",
                "distance": "5.0",
                "notes": "Test",
                "visibility": "private",
            },
            follow_redirects=True,
        )

        assert b"Duration must be more than 0" in response.data

    # submitting completely empty form should be rejected
    def test_empty_form_rejected(self, authenticated_client):
        response = authenticated_client.post(
            "/activities/new",
            data={
                "activity_type": "",
                "date": "",
                "duration": "",
                "duration_unit": "minutes",
                "distance": "",
                "notes": "",
                "visibility": "private",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert (
            b"Please choose an activity type" in response.data
            or b"required" in response.data.lower()
        )

    # submitting without selecting activity type should be rejected
    def test_missing_activity_type_rejected(self, authenticated_client):
        response = authenticated_client.post(
            "/activities/new",
            data={
                "activity_type": "",
                "date": "2025-05-01",
                "duration": "30",
                "duration_unit": "minutes",
                "distance": "5.0",
                "notes": "Test",
                "visibility": "private",
            },
            follow_redirects=True,
        )

        assert b"Please choose an activity type" in response.data

    # submitting unrealistically high duration should be rejected
    def test_excessive_duration_rejected(self, authenticated_client):
        response = authenticated_client.post(
            "/activities/new",
            data={
                "activity_type": "Running",
                "date": "2025-05-01",
                "duration": "500",
                "duration_unit": "minutes",
                "distance": "50.0",
                "notes": "Test",
                "visibility": "private",
            },
            follow_redirects=True,
        )

        assert b"Duration cannot exceed 8 hours" in response.data
