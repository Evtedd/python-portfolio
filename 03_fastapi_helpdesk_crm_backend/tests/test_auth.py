def test_register_and_login(client):
    response = client.post(
        "/auth/register",
        json={"email": "dev@example.com", "password": "password123"},
    )
    assert response.status_code == 201

    login = client.post(
        "/auth/login",
        json={"email": "dev@example.com", "password": "password123"},
    )

    assert login.status_code == 200
    assert login.json()["token_type"] == "bearer"


def test_duplicate_email_is_rejected(client):
    payload = {"email": "dev@example.com", "password": "password123"}

    assert client.post("/auth/register", json=payload).status_code == 201
    assert client.post("/auth/register", json=payload).status_code == 409
