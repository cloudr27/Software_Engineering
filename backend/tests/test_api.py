TICKET = {
    "title": "Не работает принтер",
    "description": "Принтер в кабинете 12 не печатает",
    "author_id": 1,
    "priority_id": 3,
}


def related_id(body, name):
    """id связанного объекта: поддерживает и плоское поле (status_id),
    и вложенный объект (status: {"id": ...})."""
    if f"{name}_id" in body:
        return body[f"{name}_id"]
    value = body.get(name)
    if isinstance(value, dict):
        return value.get("id")
    return value


def test_dictionaries(client):
    assert len(client.get("/api/dictionaries/statuses").json()) == 4
    assert len(client.get("/api/dictionaries/priorities").json()) == 4
    assert len(client.get("/api/dictionaries/roles").json()) == 3


def test_create_user(client):
    r = client.post("/api/users", json={
        "username": "ivan", "email": "ivan@example.com",
        "password": "secret123", "role_id": 2,
    })
    assert r.status_code == 201
    assert r.json()["email"] == "ivan@example.com"


def test_create_user_duplicate_email(client):
    payload = {"username": "other", "email": "user@example.com",
               "password": "secret123", "role_id": 1}
    r = client.post("/api/users", json=payload)
    assert r.status_code == 400


def test_create_ticket_gets_open_status(client):
    r = client.post("/api/tickets", json=TICKET)
    assert r.status_code == 201
    body = r.json()
    assert related_id(body, "status") == 1, f"Ответ API: {body}"


def test_list_and_get_ticket(client):
    created = client.post("/api/tickets", json=TICKET).json()
    assert len(client.get("/api/tickets").json()) == 1
    r = client.get(f"/api/tickets/{created['id']}")
    assert r.status_code == 200
    assert r.json()["title"] == TICKET["title"]


def test_get_ticket_not_found(client):
    assert client.get("/api/tickets/999").status_code == 404


def test_resolve_ticket_sets_resolved_at(client):
    t = client.post("/api/tickets", json=TICKET).json()
    r = client.patch(f"/api/tickets/{t['id']}", json={"status_id": 3, "assignee_id": 1})
    assert r.status_code == 200
    body = r.json()
    assert related_id(body, "status") == 3, f"Ответ API: {body}"
    assert related_id(body, "assignee") == 1, f"Ответ API: {body}"
    assert body.get("resolved_at") is not None, f"Ответ API: {body}"


def test_add_and_list_comments(client):
    t = client.post("/api/tickets", json=TICKET).json()
    r = client.post(f"/api/tickets/{t['id']}/comments",
                    json={"author_id": 1, "text": "Принял в работу"})
    assert r.status_code == 201
    comments = client.get(f"/api/tickets/{t['id']}/comments").json()
    assert len(comments) == 1
    assert comments[0]["text"] == "Принял в работу"


def test_comment_on_missing_ticket(client):
    r = client.post("/api/tickets/999/comments", json={"author_id": 1, "text": "x"})
    assert r.status_code == 404
