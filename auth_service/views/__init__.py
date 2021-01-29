import flask_login
from flask import (
    Blueprint,
    render_template,
    render_template_string, session,
)
from flask_login import current_user
from flask_user import roles_required, login_required

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/protected")
@flask_login.login_required
def protected():
    return render_template("protected.html")


# The Members page is only accessible to authenticated users
@main.route("/members")
@login_required  # Use of @login_required decorator
def member_page():
    return render_template_string(
        """
            {% extends "layouts/bootstrap-contents.html" %}
            {% block main %}
                <h2>{%trans%}Members page{%endtrans%}</h2>
                <p><a href={{ url_for('user.register') }}>{%trans%}Register{%endtrans%}</a></p>
                <p><a href={{ url_for('user.login') }}>{%trans%}Sign in{%endtrans%}</a></p>
                <p><a href={{ url_for('main.index') }}>{%trans%}Home Page{%endtrans%}</a> (accessible to anyone)</p>
                <p><a href={{ url_for('main.member_page') }}>{%trans%}Member Page{%endtrans%}</a> (login_required: member@example.com / Password1)</p>
                <p><a href={{ url_for('main.admin_page') }}>{%trans%}Admin Page{%endtrans%}</a> (role_required: admin@example.com / Password1')</p>
                <p><a href={{ url_for('user.logout') }}>{%trans%}Sign out{%endtrans%}</a></p>
            {% endblock %}
            """
    )


# The Admin page requires an 'Admin' role.
@main.route("/admin")
@roles_required("Admin")  # Use of @roles_required decorator
def admin_page():
    return render_template_string(
        """
            {% extends "layouts/bootstrap-contents.html" %}
            {% block main %}
                <h2>{%trans%}Admin Page{%endtrans%}</h2>
                <p><a href={{ url_for('user.register') }}>{%trans%}Register{%endtrans%}</a></p>
                <p><a href={{ url_for('user.login') }}>{%trans%}Sign in{%endtrans%}</a></p>
                <p><a href={{ url_for('main.index') }}>{%trans%}Home Page{%endtrans%}</a> (accessible to anyone)</p>
                <p><a href={{ url_for('main.member_page') }}>{%trans%}Member Page{%endtrans%}</a> (login_required: member@example.com / Password1)</p>
                <p><a href={{ url_for('main.admin_page') }}>{%trans%}Admin Page{%endtrans%}</a> (role_required: admin@example.com / Password1')</p>
                <p><a href={{ url_for('user.logout') }}>{%trans%}Sign out{%endtrans%}</a></p>
            {% endblock %}
            """
    )
