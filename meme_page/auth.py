from re import compile, match

from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from .models import Users
from .extensions import db


auth = Blueprint('auth', __name__)

userRegExp = compile(r"^\w+$") #test validity of username

@auth.route('/login')
def login_page():
    return render_template('auth/login.html.jinja')

@auth.route('/login',methods=["POST"])
def login():
    # login code goes here
    username = request.form.get('user', '', str)
    password = request.form.get('pass', '', str)
    remember = bool(request.form.get('remember'))

    user = Users.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password, password):
        flash('Incorrect login details: username or password incorrect', 
              category='error')
        return redirect(url_for('auth.login')) 

    # User has correct login
    login_user(user, remember=remember)
    flash("Logged in successfully!", category="success")
    return redirect(url_for('account.profile'))


@auth.route('/signup')
def signup_page():
    return render_template('/auth/signup.html.jinja')

@auth.route('/signup', methods=["POST"])
def signup():
        # code to validate and add user to database goes here
    username = request.form.get('user', '', str)
    password = request.form.get('pass', '', str)
    if not (username or password): #username/password is null or GET request
        return render_template('auth/login.html.jinja')
    #following tests should have been verified client-side
    if len(username) < 4:
        flash("Error: Username must be at least 4 characters", category="error")
        return redirect(url_for('auth.signup'))
    elif match(userRegExp, username) is None:
        flash("Username must only contain letters and numbers",category="error")
        return redirect(url_for('auth.signup'))
    elif len(password) < 8:
        flash("Password must be at least 8 characters", category="error")
        return redirect(url_for('auth.signup'))

    user = Users.query.filter_by(username=username).first() 
    # if this returns a user, then the user already exists in database
    if user:
        # if user found, redirect back to signup page
        flash("Error: User already exists", category="error")
        return redirect(url_for('auth.signup'))

    new_user = Users(username=username, 
                     password=generate_password_hash(password),
                     nsfw=False)

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()
    
    flash('Signed up successfuly! Please login using your new account', 
          category='success')
    return redirect(url_for('auth.login'))

@auth.route('/logout')
def logout():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    logout_user()
    flash("Logged out successfully", category='success')
    return redirect('/')

#const
nsfw_test_questions: dict[str, list[tuple[str, str, str]]] = {
    'Animals': 
        [
            ('What does the ','fox', ' say'),
            ("Beep beep I'm a ", 'sheep', ''),
            ("RIP ", 'Harambe', " (1999–2016)"),
        ],
    'Songs':
        [
            ('Welcome to the ', 'Hotel', ' California'),
            ('House of the ', 'Rising', ' Sun'),
            ("They're ", 'Taking the Hobbits', ' to Isengard'),
        ],
    #If you're here just for the answers you deserve it atp
    'Books':
        [
            ('Famous book by George Orwell: ', 'Animal', ' Farm'),
        ],
    'Memes':
        [
            ("Sir they've hit the ", 'second', ' tower'),
            ("Rainbow Dash ", "cum jar", " incident")
        ]
    #TODO?
}

@auth.route('/nsfwtest', methods=["GET"])
def nsfwtest():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    return render_template('auth/nsfwtest.html.jinja')


    