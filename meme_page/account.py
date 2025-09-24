"""For the routes associated with the user
E.g. /account and /bookmarks"""

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db, reddit
from .models import Posts, Bookmarks
from .meme_page import render_meme

account = Blueprint('account', __name__)

@account.route('/profile')
@login_required
def profile():
    return render_template('account/profile.html.jinja')

@account.route('/bookmarks')
@login_required
def bookmark_page():
    def data_from_bookmark(bookmark: Posts) -> dict:
        post = reddit.submission(id=bookmark.id)
        try:
            thumbnail = post.thumbnail #may return '' or error
        except:
            thumbnail = ''
        if not thumbnail:
            thumbnail = 'default' #If thumbnail is ''
        if thumbnail in ['default', 'self', 'nsfw']:
            thumbnail = url_for('static',
                                filename=f'thumbnails/{thumbnail}.png')
        return {
            'subreddit': bookmark.subreddit, 
            'thumbnail': thumbnail,
            'title': post.title, 
            'nsfw': bookmark.nsfw, 
            'id': bookmark.id}
    bookmarks = []
    for bookmark in current_user.bookmarks:
        try:
            bookmarks.append(data_from_bookmark(bookmark))
        except:
            continue #graceful handling of errors
    return render_template('account/bookmarks.html.jinja', bookmarks=bookmarks)

@account.route('/bookmarks', methods=["POST"])
@login_required
def create_bookmark():
    post_id = request.form.get('id')
    if not post_id:
        return jsonify({'error': 'No id specified'})
    post = Posts.query.filter_by(id=post_id).first()
    if not post: #Post not in table yet
        reddit_post = reddit.submission(id=post_id)
        parameters = {'id': post_id,
                      'subreddit': reddit_post.subreddit.display_name,
                      'nsfw': reddit_post.over_18,
                      }
        new_post = Posts(**parameters)
        db.session.add(new_post)
        db.session.commit()
        post_id = new_post.id
        #Post is now in database
    new_bookmark = Bookmarks(userid=current_user.id, postid=post_id)
    try:
        db.session.add(new_bookmark)
        db.session.commit()
    except:
        return jsonify({'error': 'Bookmark already exists'})
    return jsonify({'error': False, })

@account.route('/deletebookmark', methods=["POST"])
def delete_bookmark():
    post_id = request.form.get('id')
    if not post_id:
        return jsonify({'error': 'No id specified'})
    bookmark = Bookmarks.query.filter_by(postid=post_id,
                    userid=current_user.id)
    if bookmark.first() is None:
        return jsonify({'error': 'Bookmark does not exist'})
    bookmark.delete()
    db.session.commit()
    return jsonify({'error': False, })
    

@account.route('/bookmarks/<post_id>')
def render_bookmark(post_id: str):
    return render_meme(reddit.submission(id=post_id),
                       post_type='Bookmarked',
                       parent='account/bookmark.html.jinja')

@account.route('/banana')
def banana():
    "Happy Easter"
    return jsonify({'exists': True, 'egg_type': 'Easter',})

@account.route('/account')
@login_required
def acc_settings():
    return render_template('account/account.html.jinja')

@account.route('/account', methods=["POST"])
@login_required
def update_acc_settings():
    old_pass = request.form.get('old_password', '', str)
    new_pass = request.form.get('new_password', '', str)
    if not old_pass or not new_pass:
        flash('Please fill in all password fields')
    elif check_password_hash(current_user.password, old_pass):
        current_user.password = generate_password_hash(password=new_pass)
        db.session.commit()
        flash('Password updated successfully', category='success')
    else:
        flash('Current password does not match', category='error')
    return redirect(url_for('account.acc_settings'))
