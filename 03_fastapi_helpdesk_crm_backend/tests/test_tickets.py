def create_ticket(client, headers, title="Printer is down"):
    response = client.post(
        "/tickets",
        json={"title": title, "description": "Second floor printer fails."},
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def test_create_ticket(client, user_headers):
    ticket = create_ticket(client, user_headers)

    assert ticket["title"] == "Printer is down"
    assert ticket["status"] == "open"


def test_user_cannot_see_other_users_ticket(client, user_headers):
    ticket = create_ticket(client, user_headers)
    client.post(
        "/auth/register",
        json={"email": "other@example.com", "password": "password123"},
    )
    login = client.post(
        "/auth/login",
        json={"email": "other@example.com", "password": "password123"},
    )
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = client.get(f"/tickets/{ticket['id']}", headers=other_headers)

    assert response.status_code == 404


def test_admin_can_change_status(client, user_headers, admin_headers):
    ticket = create_ticket(client, user_headers)

    response = client.patch(
        f"/tickets/{ticket['id']}",
        json={"status": "in_progress"},
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"


def test_pagination(client, user_headers):
    create_ticket(client, user_headers, title="First issue")
    create_ticket(client, user_headers, title="Second issue")

    response = client.get("/tickets?limit=1&offset=1", headers=user_headers)

    assert response.status_code == 200
    assert len(response.json()) == 1
