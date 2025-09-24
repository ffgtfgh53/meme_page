from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user, login_required, login_user

from .models import Users, Posts, Bookmarks
from .extensions import db

admin = Blueprint('admin', __name__)

admin_usernames = ['admin']

#To check admin:
#if current_user.username not in admin_usernames: return "Unauthorised", 401
#idk how to make decorator functions work like @login_required

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

def get_record(table: str, record_id: str|tuple[str,str], template: str):
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
    return render_template(template, 
                table=table, id=record_id, data=data.items())        

@admin.route('/adminconsole', methods=['POST'])
@login_required
def adminconsole_post():
    if current_user.username not in admin_usernames: return "Unauthorised", 401
    action = request.form.get('action', '', type=str)
    table = request.form.get('table', '', type=str).lower()
    record_id = request.form.get('id', '', type=str).lower()
    if action == 'view':
        return redirect(f"/adminconsole/view/{table}")
    elif action == 'edit':
        return get_record(table, record_id, 
            template='admin/editrecord.html.jinja')
    elif action == 'login':
        user = Users.query.filter_by(id=record_id).first()
        if not user:
            return f"Error: no user with ID {record_id} found"
        login_user(user)
        return redirect(url_for('account.profile'))
    else:
        return f"invalid action '{action}'"

@admin.route('/adminconsole', methods=['GET'])
@login_required
def adminconsole_get():
    if current_user.username not in admin_usernames: return "Unauthorised", 401
    return render_template('admin/console.html.jinja')

@admin.route('/adminconsole/view/<table>')
@login_required
def view(table):
    if current_user.username not in admin_usernames: return "Unauthorised", 401
    return view_table(table)

@admin.route('/adminconsole/edit', methods=['POST'])
@login_required
def edit():
    if current_user.username not in admin_usernames: return "Unauthorised", 401
    data = dict(request.form)
    print(data)
    table = data.pop('table', '')
    record_id = data.pop('id', '')
    if not table or not record_id:
        return "Bad data", 400
    #Users and Posts both contain 'nsfw' which is bool
    data_nsfw = data['nsfw'].lower()
    if data_nsfw == 'false' or data_nsfw == '0':
        nsfw = False
    elif data_nsfw == 'true' or data_nsfw == '1':
        nsfw = True
    else:
        return 'bad data: nsfw must be true or false', 400
    if table == 'users':
        db.session.query(Users).filter(Users.id == record_id).update({
                Users.username: data['username'],
                Users.nsfw: nsfw,
                Users.password: data['password']}, 
            synchronize_session="fetch")
        #basically almost a sql statement
        db.session.commit()
        return 'edit success'
    elif table == 'posts':
        db.session.query(Posts).filter(Posts.id == record_id).update({
                Posts.subreddit: data['subreddit'],
                Posts.nsfw: nsfw}, 
            synchronize_session="fetch")
        db.session.commit()
        return 'edit success'
    else:
        return 'bad data: table not specified', 400
    #errors will result in Error 500: Internal server error

@admin.route('/adminconsole/delete', methods=['GET'])
@login_required
def confirm_delete():
    if current_user.username not in admin_usernames: return "Unauthorised", 401
    userid = request.args.get('user_id', '', int)
    postid = request.args.get('post_id', '', str)
    if userid and postid:
        table = 'Bookmarks'
        bookmark = Bookmarks.query.filter_by(postid=postid, userid=userid).first()
        if not bookmark:
            return f"Error: no bookmark with UserID {userid} and PostID {postid} found", 400
        data={'UserID': userid, 'PostID': postid}
    elif userid and not postid:
        table = 'Users'
        user = Users.query.filter_by(id=userid).first()
        if not user:
            return f"Error: no user with id {userid} found"
        data = {'ID': userid, 'username': user.username, 
                'nsfw': user.nsfw, 'password': user.password}
    elif not userid and postid:
        table = 'Posts'
        post = Posts.query.filter_by(id=postid).first()
        if not post:
            return f"Error: no post with id {postid} found"
        data = {'ID': postid, 'subreddit': post.subreddit, 'nsfw': post.nsfw}
    else:
        return "Error: no userid and postid specified"
    return render_template('admin/deleterecord.html.jinja', 
        data=data.items(), table=table, user_id=userid, post_id=postid)

@admin.route('/adminconsole/delete', methods=['POST'])
@login_required
def delete():
    if current_user.username not in admin_usernames: return "Unauthorised", 401
    userid = request.form.get('user_id', '', str)
    postid = request.form.get('post_id', '', str)
    print(userid, postid)
    if userid and postid:
        bookmark = Bookmarks.query.filter_by(postid=postid, userid=userid)
        if not bookmark.first():
            return "Error: no bookmark found", 400
        try:
            bookmark.delete()
            db.session.commit()
            return "Bookmark deleted successfully"
        except Exception as e:
            return str(e), 500
    elif userid and not postid:
        user = Users.query.filter_by(id=userid)
        if not user.first():
            return f"Error: no user with id {userid} found"
        try:
            Bookmarks.query.filter_by(userid=userid).delete()
            user.delete()
            db.session.commit()
            return "User and related bookmarks deleted successfully"
        except Exception as e:
            return str(e), 500
    elif not userid and postid:
        post = Posts.query.filter_by(id=postid)
        if not post.first():
            return f"Error: no post with id {postid} found"
        try:
            Bookmarks.query.filter_by(postid=postid).delete()
            post.delete()
            db.session.commit()
            return "Post and related bookmarks deleted successfully"
        except Exception as e:
            return str(e), 500
    else:
        return "Error: no userid and postid specified"
