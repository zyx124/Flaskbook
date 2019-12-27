from flask import Blueprint, render_template
from user.forms import RegisterForm
from user.models import User
import bcrypt

user_app = Blueprint('user_app', __name__)

@user_app.route('/login')
def login():
    return "User login"

@user_app.route('/register', methods=("GET", "POST"))
def register():
    form  = RegisterForm()
    if form.validate_on_submit():
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(form.password.data, salt)
        user = User(
            username = form.username.data,
            password = hashed_password,
            email = form.email.data,
            first_name = form.first_name.data,
            last_name = form.last_name.data,

        )

        user.save()
        return "User registered"
    return render_template('user/register.html', form=form)