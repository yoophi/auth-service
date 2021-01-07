import flask
import flask_login
from flask import Blueprint, render_template, url_for, request, session, redirect, current_app

from auth_service import user_service

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/login', methods=['GET', 'POST', ])
def login():
    if flask.request.method == 'GET':
        return render_template(
            'auth/login.html',
            login_redirect=request.args.get('next'),
        )

    email = request.form['email']
    password_ = request.form['password']
    login_redirect = request.form.get('login_redirect')

    user = user_service.authenticate_and_get_user(email, password_)

    if user:
        flask_login.login_user(user)

        if login_redirect and not login_redirect.startswith(url_for('main.login')):
            return redirect(login_redirect)

        return redirect(flask.url_for('main.protected'))

    return 'Bad login'


@main.route('/protected')
@flask_login.login_required
def protected():
    return render_template('protected.html')


@main.route('/logout')
def logout():
    flask_login.logout_user()
    return flask.redirect(url_for('main.index'))
