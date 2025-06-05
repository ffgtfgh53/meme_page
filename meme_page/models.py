from typing import Optional

from flask_login import UserMixin

from .extensions import db


class Users(db.Model, UserMixin):
    __tablename__ = "USERS"
    id = db.Column("ID", db.Integer, primary_key=True) 
    username = db.Column("USERNAME", db.String(100), unique=True)
    password = db.Column("PASSWORD", db.String(200), nullable=False)
    nsfw = db.Column("SHOW_NSFW", db.Boolean)
    bookmarks = db.relationship("Posts", secondary="BOOKMARKS", 
                                back_populates='users')
    
    def __repr__(self):
        return f"<User {self.id=} {self.username=}>"

class Posts(db.Model):
    __tablename__ = 'POSTS'
    id = db.Column("ID", db.Integer, primary_key=True)
    link = db.Column("LINK", db.String(162), unique=True, nullable=False)
    subreddit = db.Column("SUBREDDIT", db.String(50))
    nsfw = db.Column("NSFW", db.Boolean)
    users = db.relationship("Users", secondary="BOOKMARKS", 
                            back_populates='bookmarks')

class Bookmarks(db.Model):
    __tablename__ = "BOOKMARKS"
    userid = db.Column("USERID", db.ForeignKey('USERS.ID'), 
                       primary_key=True, index=True)
    postid = db.Column("POSTID", db.ForeignKey('POSTS.ID'),
                       primary_key=True, index=True)



