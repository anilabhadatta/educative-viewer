from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from .models import User
from . import db

auth = Blueprint('auth', __name__)


@auth.route('/edu-viewer/login')
def login():
    return render_template('login.html')


@auth.route('/edu-viewer/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # check if user actually exists
    # take the user supplied password, hash it, and compare it to the hashed password in database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        # if user doesn't exist or password is wrong, reload the page
        return redirect(url_for('auth.login'))

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('main.courses'))


@auth.route('/edu-viewer/signup')
def signup():
    return render_template('signup.html')


@auth.route('/edu-viewer/signup', methods=['POST'])
def signup_post():

    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')

    # if this returns a user, then the email already exists in database
    user = User.query.filter_by(email=email).first(
    ) or User.query.filter_by(username=username).first()

    if user:  # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email or Username address already exists')
        return redirect(url_for('auth.signup'))

    # create new user with the form data. Hash the password so plaintext version isn't saved.
    new_user = User(email=email, username=username,
                    password=generate_password_hash(password, method='pbkdf2:sha256'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('auth.login'))


@auth.route('/edu-viewer/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
