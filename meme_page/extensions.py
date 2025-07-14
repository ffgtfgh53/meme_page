"Contains global db and reddit objects"
from flask_sqlalchemy import SQLAlchemy
from praw import Reddit

db = SQLAlchemy()

reddit = Reddit("main bot")  
#Requires praw.ini file 