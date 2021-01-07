import flask
import flask_login
from flask import Blueprint, render_template, url_for

from auth_service import user_service

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/login', methods=['GET', 'POST', ])
def login():
    if flask.request.method == 'GET':
        return render_template('auth/login.html')

    email = flask.request.form['email']
    password_ = flask.request.form['password']

    user = user_service.authenticate_and_get_user(email, password_)

    if user:
        flask_login.login_user(user)
        return flask.redirect(flask.url_for('main.protected'))

    return 'Bad login'


@main.route('/protected')
@flask_login.login_required
def protected():
    return render_template('protected.html')
    # return f'Logged in as: {flask_login.current_user.id}, {flask_login.current_user.username}'


@main.route('/logout')
def logout():
    flask_login.logout_user()
    return flask.redirect(url_for('main.index'))
