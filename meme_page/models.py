from flask_login import UserMixin

from .extensions import db

class Users(db.Model, UserMixin):
    __tablename__ = "USERS"
    id = db.Column("ID", db.Integer, primary_key=True) 
    username = db.Column("USERNAME", db.String(100), unique=True)
    #Password hash is exactly 162 chars in length
    password = db.Column("PASSWORD", db.String(162), nullable=False)
    nsfw = db.Column("SHOW_NSFW", db.Boolean)
    bookmarks = db.relationship("Posts", secondary="BOOKMARKS", 
                                back_populates='users')
    def __repr__(self):
        return f"<Users {self.id=} {self.username=}>"
    
    def __iter__(self):
        return (self.id, self.username, self.password, self.nsfw).__iter__()

class Posts(db.Model):
    __tablename__ = 'POSTS'
    id = db.Column("ID", db.String, primary_key=True)
    # link = 'https://redd.it/' + id
    subreddit = db.Column("SUBREDDIT", db.String(50))
    nsfw = db.Column("NSFW", db.Boolean)
    users = db.relationship("Users", secondary="BOOKMARKS", 
                            back_populates='bookmarks')
    def __repr__(self):
        return f"<Posts {self.id=} {self.link=}>"
    
    def __iter__(self):
        return (self.id, self.subreddit, self.nsfw).__iter__()

class Bookmarks(db.Model):
    __tablename__ = "BOOKMARKS"
    userid = db.Column("USERID", db.ForeignKey('USERS.ID'), 
                       primary_key=True, index=True)
    postid = db.Column("POSTID", db.ForeignKey('POSTS.ID'),
                       primary_key=True, index=True)
    def __repr__(self):
        return f"<Bookmarks {self.userid=} {self.postid=}"
    
    def __iter__(self):
        return (self.userid, self.postid).__iter__()



