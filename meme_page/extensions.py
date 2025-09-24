"Contains global db and reddit objects"
from flask_sqlalchemy import SQLAlchemy
from praw import Reddit

db = SQLAlchemy()

#Requires praw.ini file 
reddit = Reddit("main bot")
