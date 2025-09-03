from flask import Blueprint, render_template, request
from flask_login import current_user, login_required

from .models import *
from .extensions import db

admin = Blueprint('admin', __name__)

@admin.route('/adminconsole', methods=['GET'])
@login_required
def console():
    if current_user.username != 'admin':
        return redirect(url_for('auth.login')) 
    return render_template('admin/console.html.jinja')

@admin.route('/adminconsole', methods=['POST'])
def database():
    action = request.form.get('action', False, type=str).lower()
    table = request.form.get('table', False, type=str).lower()
    if action == 'view':
        if table == 'users':
            data = Users.query.all()
            header = ['id','username','password_hash','show_nsfw?']
        elif table == 'posts':
            data = Posts.query.all()
            header = ['id', 'subreddit', 'nsfw?']
        elif table == 'bookmarks':
            data = Bookmarks.query.all()
            header = ['userid', 'postid']
        else:
            data = []
            header = [f'error occured: no table {table} found']
        return render_template('admin/tabledata.html.jinja', 
                    data=data, header=header, title=f'table {table}')


