def test_bootstrap_and_login_flow(client):
    bootstrap_payload = {
        "username": "admin",
        "email": "admin@example.com",
        "password": "secret123",
        "privileges": ["super_admin"],
    }
    bootstrap_response = client.post("/auth/bootstrap-admin", json=bootstrap_payload)
    assert bootstrap_response.status_code == 201

    login_response = client.post(
        "/auth/token",
        data={"username": "admin", "password": "secret123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    assert token

    list_admins_response = client.get(
        "/admins",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_admins_response.status_code == 200
    admins = list_admins_response.json()
    assert len(admins) == 1
    assert admins[0]["username"] == "admin"


def test_login_with_wrong_password_returns_401(client):
    client.post(
        "/auth/bootstrap-admin",
        json={
            "username": "admin",
            "email": "admin@example.com",
            "password": "secret123",
            "privileges": ["super_admin"],
        },
    )

    bad_login_response = client.post(
        "/auth/token",
        data={"username": "admin", "password": "wrong-password"},
    )
    assert bad_login_response.status_code == 401


def test_second_bootstrap_admin_returns_400(client):
    payload = {
        "username": "admin",
        "email": "admin@example.com",
        "password": "secret123",
        "privileges": ["super_admin"],
    }
    first_bootstrap = client.post("/auth/bootstrap-admin", json=payload)
    assert first_bootstrap.status_code == 201

    second_bootstrap = client.post(
        "/auth/bootstrap-admin",
        json={
            "username": "admin2",
            "email": "admin2@example.com",
            "password": "secret456",
            "privileges": ["manage_admins"],
        },
    )
    assert second_bootstrap.status_code == 400
