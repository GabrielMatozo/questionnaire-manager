from datetime import datetime

from flask import flash, redirect, render_template, request, url_for
from flask_bcrypt import Bcrypt
from flask_login import login_required, login_user, logout_user
from marshmallow import ValidationError

from ..models import User, db
from ..schemas import login_schema, register_schema
from . import auth_bp

bcrypt = Bcrypt()


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if User.query.first():
        flash("Já existe um usuário cadastrado!")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        data = {
            "username": request.form.get("username"),
            "password": request.form.get("password"),
        }

        try:
            register_schema.load(data)
        except ValidationError as e:
            flash(f"Erro de validação: {e.messages}")
            return render_template("register.html")

        username = data["username"]
        password = data["password"]

        if not username or not password:
            flash("Preencha todos os campos!")
            return render_template("register.html")

        password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        user = User(username=username, password_hash=password_hash)

        db.session.add(user)
        db.session.commit()

        flash("Usuário cadastrado com sucesso!", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = {
            "username": request.form.get("username"),
            "password": request.form.get("password"),
        }

        try:
            login_schema.load(data)
        except ValidationError as e:
            flash(f"Erro de validação: {e.messages}")
            return render_template("login.html")

        username = data["username"]
        password = data["password"]

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            user.last_active = datetime.utcnow()
            db.session.commit()
            return redirect(url_for("main.admin"))
        else:
            flash("Usuário ou senha incorretos!", "error")

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))
