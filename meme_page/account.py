"""For the routes associated with the user
E.g. /account and /bookmarks"""

from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user, login_required
import praw

from .extensions import db, reddit
from .models import Posts, Bookmarks

account = Blueprint('account', __name__)

@account.route('/profile')
@login_required
def profile():
    return render_template('account/profile.html')

@account.route('/bookmarks')
@login_required
def bookmarks():
    return 'bookmarks'
    #TODO

@account.route('/bookmarks', methods=["POST"])
@login_required
def create_bookmark():
    link = request.form.get('link')
    if not link: raise Exception("Link of post not specified")
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
    db.session.add(new_bookmark)
    db.session.commit()
    return jsonify(True)
    
@account.route('/banana')
def banana():
    return jsonify(True)