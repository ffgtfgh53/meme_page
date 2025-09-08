from flask import Blueprint, render_template, request, redirect, url_for, current_app
from flask_login import current_user, login_required

from .models import *
from .extensions import db

admin = Blueprint('admin', __name__)

#To check admin: 
#if current_user.username != 'admin': return "Unauthorised", 401

def view_table(table: str):
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
        return "Invalid table", 400
    return render_template('admin/viewtable.html.jinja', 
                data=data, header=header, title=f'table {table}')

def edit_table(table: str, record_id:str):
    if not record_id: 
        return "error: id unspecified", 400
    if table == 'users':
        data = Users.query.filter_by(id=record_id).first()
    elif table == 'posts':
        data = Posts.query.filter_by(id=record_id).first()
    else:
        return f"invalid table '{table}'", 400
    if data is None:
        return f"no record with id '{record_id}' found in table '{table}'", 400
    data = data.__dict__
    data.pop('_sa_instance_state', False)
    data.pop('id')
    return render_template('admin/edittable.html.jinja', 
                table=table, id=record_id, data=data.items())

@admin.route('/adminconsole', methods=['POST'])
def adminconsole_post():
    if current_user.username != 'admin': return "Unauthorised", 401
    action = request.form.get('action', '', type=str)
    table = request.form.get('table', '', type=str).lower()
    record_id = request.form.get('id', '', type=str).lower()
    if action == 'view':
        return redirect(f"/adminconsole/view/{table}")
    elif action == 'edit':
        return edit_table(table, record_id)
    else:
        return f"invalid action '{action}'"

@admin.route('/adminconsole', methods=['GET'])
def adminconsole_get():
    if current_user.username != 'admin': return "Unauthorised", 401
    return render_template('admin/console.html.jinja')

@admin.route('/adminconsole/view/<table>')
def view(table):
    if current_user.username != 'admin': return "Unauthorised", 401
    return view_table(table)

@admin.route('/adminconsole/edit', methods=["POST"])
def edit():
    if current_user.username != 'admin': return "Unauthorised", 401
    data = dict(request.form)
    print(data)
    table = data.pop('table', '')
    record_id = data.pop('id', '')
    if not table or not record_id:
        return "Bad data", 400
    nsfw = data['nsfw'].lower()
    if nsfw == 'false':
        data['nsfw'] = False
    elif nsfw == 'true':
        data['nsfw'] = True
    else:
        return 'bad data: nsfw must be true or false', 400
        #Users and Posts both contain 'nsfw' which is bool
    session = db.session()
    if table == 'users':
        session.query(Users).filter(Users.id == record_id).update({
            Users.username: data['username'],
            Users.nsfw: data['nsfw'],
            Users.password: data['password'],
        }, synchronize_session="fetch")
        #basically almost a sql statement
        return 'success'
    elif table == 'posts':
        session.query(Posts).filter(Posts.id == record_id).update({
            Posts.subreddit: data['subreddit'],
            Posts.nsfw: data['nsfw'],}, synchronize_session="fetch")
        session.commit()
        return 'sucess'
