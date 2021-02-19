import flask_login
from flask import (
    Blueprint,
    render_template,
    render_template_string,
    session, request, jsonify,
)
from flask_login import current_user
from flask_user import roles_required, login_required
from flask_wtf import FlaskForm
from wtforms import validators, ValidationError
from wtforms import HiddenField, StringField, SubmitField, RadioField, SelectField

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


@main.route('/profile')
@flask_login.login_required
def profile():
    return render_template('profile.html')


@main.route('/profile/update', methods=['GET', 'POST',])
@flask_login.login_required
def profile_update():
    if request.method == 'POST':
        return jsonify(dict(request.form))
    form = ProfileUpdateForm()

    return render_template('profile-update.html', form=form)


class ProfileUpdateForm(FlaskForm):
    language = SelectField(
        '언어',
        choices=[
            ('', '미입력'),
            ('ko', '한글'),
            ('en', '영어'),
        ],
        validators=[
            validators.DataRequired('언어 설정은 필수 입력입니다.')
        ])
    country = SelectField(
        '국가',
        choices=[
            ('', '미입력'),
            ('kr', '한국'),
            ('us', '미국'),
            ('vn', '베트남'),
        ],
        validators=[
            validators.DataRequired('국가 설정은 필수 입력입니다.')
        ])
    gender = RadioField(
        '성별',
        choices=[
            ('M', '남성'),
            ('F', '여성'),
            ('U', '공개 안함')
        ],

        validators=[
            validators.DataRequired('성별 설정은 필수 입력입니다.')
        ])
    # next = HiddenField()        # for login_or_register.html
    # reg_next = HiddenField()    # for register.html
    #
    # username = StringField(_('Username'), validators=[
    #     validators.DataRequired(_('Username is required')),
    #     username_validator,
    #     unique_username_validator])
    # email = StringField(_('Email'), validators=[
    #     validators.DataRequired(_('Email is required')),
    #     validators.Email(_('Invalid Email')),
    #     unique_email_validator])
    # password = PasswordField(_('Password'), validators=[
    #     validators.DataRequired(_('Password is required')),
    #     password_validator])
    # retype_password = PasswordField(_('Retype Password'), validators=[
    #     validators.EqualTo('password', message=_('Password and Retype Password did not match'))])
    # invite_token = HiddenField(_('Token'))

    submit = SubmitField("업데이트")

    def validate(self):
        # remove certain form fields depending on user manager config
        # user_manager =  current_app.user_manager
        # if not user_manager.USER_ENABLE_USERNAME:
        #     delattr(self, 'username')
        # if not user_manager.USER_ENABLE_EMAIL:
        #     delattr(self, 'email')
        # if not user_manager.USER_REQUIRE_RETYPE_PASSWORD:
        #     delattr(self, 'retype_password')
        # if not super(ProfileUpdateForm, self).validate():
        #     return False
        # All is well
        return True
