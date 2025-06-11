from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from .models import Users
from .extensions import db


auth = Blueprint('auth', __name__)

@auth.route('/login')
def login_page():
    return render_template('auth/login.html.jinja')

@auth.route('/login',methods=["POST"])
def login():
    # login code goes here
    username = request.form.get('user', False, str)
    password = request.form.get('pass', False, str)
    remember = True if request.form.get('remember') else False

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
    username = request.form.get('user',False,str)
    password = request.form.get('pass', False, str)
    if not (username or password): #username/password is null or GET request
        return render_template('auth/login.html.jinja')

    user = Users.query.filter_by(username=username).first() 
    # if this returns a user, then the user already exists in database

    if user:
        # if user found, redirect back to signup page
        flash("Error: User already exists", category="error")
        return redirect(url_for('auth.signup'))

    new_user = Users(username=username, 
                     password=generate_password_hash(password))

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
    
    