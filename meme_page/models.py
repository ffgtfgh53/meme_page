from .extensions import db
from flask_login import UserMixin

class Users(db.Model, UserMixin):
    __tablename__ = "USERS"
    id = db.Column("ID", db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    username = db.Column("USERNAME", db.String(100), unique=True)
    password = db.Column("PASSWORD", db.String(100), nullable=False)
    nsfw = db.Column("SHOW_NSFW", db.Integer)

class Posts(db.Model):
    __tablename__ = 'POSTS'
    id = db.Column("ID", db.Integer, primary_key=True)
    link = db.Column("LINK", db.String(200), unique=True, nullable=False)
    subreddit = db.Column("SUBREDDIT", db.String(50))
    nsfw = db.Column("NSFW", db.Integer)

class Bookmarks(db.Model):
    __tablename__ = "BOOKMARKS"
    userid = db.Column("USERID", db.ForeignKey('USERS.ID'), primary_key=True)
    postid = db.Column("POSTID", db.ForeignKey('POSTS.ID'), primary_key=True)
    

