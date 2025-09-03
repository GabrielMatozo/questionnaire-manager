from flask_bcrypt import Bcrypt

from app.models import User


def test_change_password(client, auth_headers):
    resp = client.post(
        "/admin/change_password", data={"new_password": "nova123"}, follow_redirects=True
    )
    assert resp.status_code == 200
    bcrypt = Bcrypt()
    # The fixture creates user, then login, then password change
    user2 = User.query.first()
    assert bcrypt.check_password_hash(user2.password_hash, "nova123")


def test_admin_delete_unauthorized(client):
    resp = client.post("/admin/delete_all_questions", follow_redirects=True)
    assert resp.status_code == 200
    assert b"Login" in resp.data
