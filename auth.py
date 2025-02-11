"""Authentication routes for login, signup, and logout."""

import os

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.wrappers import Response

from __init__ import db
from models import User

auth = Blueprint("auth", __name__)
authtoken = os.getenv("AUTHTOKEN", "")
downloadtoken = os.getenv("DOWNLOADTOKEN", "")


@auth.route("/login")
def login() -> str:
    """Render the login page."""
    return render_template("login.html")


@auth.route("/login", methods=["POST"])
def login_post() -> Response:
    """Handle login form submission."""
    email = request.form.get("email")
    password = request.form.get("password")
    remember = bool(request.form.get("remember"))

    user = User.query.filter_by(email=email).first()

    # check if user exists and password matches
    if not user or not check_password_hash(user.password, password):
        flash("Please check your login details and try again.")
        # if user doesn't exist or password is wrong, reload the page
        return redirect(url_for("auth.login"))

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for("main.courses"))


@auth.route("/signup")
def signup() -> str:
    """Render the signup page."""
    return render_template("signup.html")


@auth.route("/signup", methods=["POST"])
def signup_post() -> Response:
    """Handle signup form submission."""
    email = request.form.get("email")
    username = request.form.get("username")
    password = request.form.get("password")
    authtoken_fromreq = request.form.get("authtoken")
    downloadtoken_fromreq = request.form.get("downloadtoken")

    # if this returns a user, then the email already exists in database
    user = (
        User.query.filter_by(email=email).first()
        or User.query.filter_by(username=username).first()
    )

    if user:  # user exists, redirect back to signup
        flash("Email or Username address already exists")
        return redirect(url_for("auth.signup"))
    if authtoken and authtoken != authtoken_fromreq:
        flash("Invalid Auth Token")
        return redirect(url_for("auth.signup"))

    # create new user with hashed password
    new_user = User(
        email=email,
        username=username,
        password=generate_password_hash(password, method="pbkdf2:sha256"),
        downloadaccess=downloadtoken_fromreq == downloadtoken,
    )

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for("auth.login"))


@auth.route("/logout")
@login_required
def logout() -> Response:
    """Log out the current user."""
    logout_user()
    return redirect(url_for("main.index"))
