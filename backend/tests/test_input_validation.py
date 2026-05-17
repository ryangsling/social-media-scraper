def _register_and_login(client, email, username):
    register_response = client.post(
        "/api/auth/register",
        json={"email": email, "username": username, "password": "supersecret"},
    )
    assert register_response.status_code == 200

    login_response = client.post(
        "/api/auth/login",
        json={"email": email, "password": "supersecret"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_register_validates_short_password(client):
    response = client.post(
        "/api/auth/register",
        json={"email": "shortpass@example.com", "username": "shortpass", "password": "12345"},
    )
    assert response.status_code == 422


def test_register_validates_short_username(client):
    response = client.post(
        "/api/auth/register",
        json={"email": "shortuser@example.com", "username": "ab", "password": "supersecret"},
    )
    assert response.status_code == 422


def test_start_scrape_rejects_invalid_max_results(client):
    headers = _register_and_login(client, "maxresults@example.com", "maxresults")
    response = client.post(
        "/api/scraping/start",
        json={
            "platform": "twitter",
            "job_type": "profile",
            "target": "openai",
            "use_apify": False,
            "max_results": 1000,
        },
        headers=headers,
    )
    assert response.status_code == 422


def test_start_scrape_rejects_blank_target(client):
    headers = _register_and_login(client, "blanktarget@example.com", "blanktarget")
    response = client.post(
        "/api/scraping/start",
        json={
            "platform": "twitter",
            "job_type": "profile",
            "target": "   ",
            "use_apify": False,
            "max_results": 50,
        },
        headers=headers,
    )
    assert response.status_code == 422
