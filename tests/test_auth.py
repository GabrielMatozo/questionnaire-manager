def test_register_page_loads(client):
    resp = client.get("/auth/register")
    assert resp.status_code == 200


def test_login_page_loads(client):
    resp = client.get("/auth/login")
    assert resp.status_code == 200


def test_register_and_login(client, db):
    from app.models import User

    resp = client.post(
        "/auth/register",
        data={"username": "admin", "password": "secret"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert User.query.count() == 1

    resp = client.post(
        "/auth/login",
        data={"username": "admin", "password": "secret"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"Painel" in resp.data or b"Admin" in resp.data


def test_login_invalid(client):
    resp = client.post(
        "/auth/login",
        data={"username": "admin", "password": "wrongpass"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"incorretos" in resp.data or b"usu" in resp.data or b"erro" in resp.data


def test_logout(client, auth_headers):
    resp = client.get("/auth/logout", follow_redirects=True)
    assert resp.status_code == 200


def test_admin_requires_login(client):
    resp = client.get("/admin", follow_redirects=True)
    assert resp.status_code == 200
    assert b"Login" in resp.data
