def test_register_login_and_me_flow(client):
    register_payload = {
        "email": "alice@example.com",
        "username": "alice",
        "password": "supersecret",
    }

    register_response = client.post("/api/auth/register", json=register_payload)
    assert register_response.status_code == 200
    assert register_response.json()["email"] == register_payload["email"]

    duplicate_email = {
        "email": "alice@example.com",
        "username": "another",
        "password": "supersecret",
    }
    duplicate_response = client.post("/api/auth/register", json=duplicate_email)
    assert duplicate_response.status_code == 400

    login_response = client.post(
        "/api/auth/login",
        json={"email": register_payload["email"], "password": register_payload["password"]},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    assert token

    me_response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["email"] == register_payload["email"]
    assert me_data["username"] == register_payload["username"]
