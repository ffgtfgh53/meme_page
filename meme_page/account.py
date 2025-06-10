"""For the routes associated with the user
E.g. /account and /bookmarks"""

from typing import Iterable

from flask import Blueprint, render_template, request, jsonify, url_for, abort
from flask_login import current_user, login_required
import praw

from .extensions import db, reddit
from .models import Posts, Bookmarks, Users

account = Blueprint('account', __name__)

@account.route('/profile')
@login_required
def profile():
    return render_template('account/profile.html.jinja')

@account.route('/bookmarks')
@login_required
def bookmark_page():
    def bookmark_from_url(bookmark: Posts):
        post = reddit.submission(url=bookmark.link)
        from praw.models import Submission
        try:
            thumbnail = post.thumbnail #may return '' or error
        except:
            thumbnail = ''
        if not thumbnail: thumbnail = 'default' #If thumbnail is ''
        if thumbnail in ['default', 'self', 'nsfw']:
            thumbnail = url_for('static', 
                                filename=f'thumbnails/{thumbnail}.png')
        return {
            'subreddit': bookmark.subreddit, 
            'thumbnail': thumbnail,
            'title': post.title, 
            'nsfw': bookmark.nsfw, 
            'link': bookmark.link}
    bookmarks = [bookmark_from_url(bookmark) for bookmark in current_user.bookmarks]
    return render_template('account/bookmarks.html.jinja', bookmarks=bookmarks)
    #TODO

@account.route('/bookmarks', methods=["POST"])
@login_required
def create_bookmark():
    link = request.form.get('link')
    if not link: 
        return jsonify({'error': 'No link specified'})
    post = Posts.query.filter_by(link=link).first()
    if not post: #Post not in table yet
        reddit_post = reddit.submission(url=link)
        subreddit = reddit_post.subreddit.display_name
        nsfw = reddit_post.over_18
        parameters = {'link': link, 
                      'subreddit': subreddit,
                      'nsfw': nsfw,
                      }
        new_post = Posts(**parameters)
        db.session.add(new_post)
        db.session.commit()
        post_id = new_post.id
    else:
        post_id = post.id
    #Post is now in database
    new_bookmark = Bookmarks(userid=current_user.id, postid=post_id)
    try:
        db.session.add(new_bookmark)
        db.session.commit()
    except:
        return jsonify({'error': 'Bookmark already exists'})
    print('ok')
    return jsonify({'error': False, })
    
@account.route('/banana')
def banana():
    return jsonify(True)