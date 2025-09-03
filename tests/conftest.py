import pytest

from app import create_app
from app.models import Option, Question, User
from app.models import db as _db


@pytest.fixture
def app():
    app = create_app()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["RATELIMIT_ENABLED"] = False

    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    return _db


@pytest.fixture
def auth_headers(client):
    with client.application.app_context():
        from flask_bcrypt import Bcrypt

        bcrypt = Bcrypt()
        pw = bcrypt.generate_password_hash("test123").decode("utf-8")
        user = User(username="admin", password_hash=pw)
        _db.session.add(user)
        _db.session.commit()

    client.post("/auth/login", data={"username": "admin", "password": "test123"})
    return {}


@pytest.fixture
def sample_question(db):
    q = Question(text="Qual sua cor favorita?", order=1)
    db.session.add(q)
    db.session.flush()
    o1 = Option(text="Azul", weight=1.0, question_id=q.id)
    o2 = Option(text="Vermelho", weight=0.5, question_id=q.id)
    db.session.add_all([o1, o2])
    db.session.commit()
    return q
