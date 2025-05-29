import sqlite3 as sql
import hashlib

import praw
from flask import flash



def encode(password:str):
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(username: str, password:str):
    """Adds username and password to databease.
    Password will be hashed in thin function."""
    sql_query = """INSERT INTO USERS(USERNAME, PASSWORD)
             VALUES(?,?)"""
    with sql.connect('database.db') as cx:
        cur = cx.cursor()
        cur.execute(sql_query, (username, encode(password)))
        cx.commit()
        return cur.lastrowid


def add_bookmark(reddit:praw.Reddit, username: str, link: str):
    """Adds bookmark to the user"""
    with sql.connect('database.db') as cx:
        cur = cx.cursor()
        userID = cur.execute("SELECT ID FROM USERS WHERE USERNAME=?", 
                             (username,)).fetchone()[0]
        try:
            postID = cur.execute("SELECT ID FROM POSTS WHERE LINK=?", 
                                 (link,)).fetchone()[0]
        except TypeError: #Nonetype object is not subscriptable
            post = reddit.submission(url=link)
            subreddit = post.subreddit
            cur.execute("""INSERT INTO POSTS(LINK, SUBREDDIT) VALUES(?,?)""",
                        (link, subreddit.display_name))
            postID = cur.lastrowid    
        cur.execute("""INSERT INTO BOOKMARKS(USERID, POSTID) VALUES(?, ?)""",
                    (userID, postID))
        cx.commit()
    print("Bookmark added successfully")



def get_bookmark(username: str) -> list:
    with sql.connect('database.db') as cx:
        cur = cx.cursor()
        try:
            userID = cur.execute("SELECT ID FROM USERS WHERE USERNAME=?", 
                                 (username,)).fetchone()[0]
        except TypeError: #Nonetype object is not subscriptable
            raise NotImplementedError(f"User '{username}' does not exist.")
    return cur.execute("""SELECT POSTS.LINK, POSTS.SUBREDDIT 
                       FROM BOOKMARKS, POSTS 
                       WHERE BOOKMARKS.USERID = ? 
                       AND POSTS.ID=BOOKMARKS.POSTID""", 
                       (userID,)).fetchall()

def check_password(username: str, password: str, encoded: bool = False):
    with sql.connect('database.db') as cx:
        cur = cx.cursor()
        print(username)
        try:
            true_pass = cur.execute("""SELECT PASSWORD FROM USERS 
                                    WHERE USERNAME=?""", 
                                    (username,)).fetchone()[0]
        except TypeError: #Nonetype object is not subscriptable
            flash("Username not found.", category='error')
            return False
    if not encoded: password = encode(password)
    if password == true_pass:
        return True
    flash("Incorrect password",category='error')
    return False





sql_statements = [
    """CREATE TABLE IF NOT EXISTS USERS (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        USERNAME TEXT NOT NULL UNIQUE,
        PASSWORD TEXT NOT NULL,
        SHOW_NSFW INTEGER)
    """,
    """CREATE TABLE IF NOT EXISTS POSTS (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        LINK TEXT NOT NULL UNIQUE,
        SUBREDDIT TEXT)
    """,
    """CREATE TABLE IF NOT EXISTS BOOKMARKS (
        USERID INTEGER NOT NULL,
        POSTID INTEGER NOT NULL,
        FOREIGN KEY(USERID) REFERENCES USERS (ID),
        FOREIGN KEY(POSTID) REFERENCES POSTS (ID),
        PRIMARY KEY(USERID, POSTID))
    """
]



# cursor = cx.cursor()
# for statement in sql_statements:
#     cursor.execute(statement)
# #add_user(cx, 'notadmin','notadminpass')
# #add_bookmark(cx, praw.Reddit("main bot"),"notadmin", "https://reddit.com/r/meme/comments/1kwhjn9/skill_issues/")
# #add_user(cx, "admin", "adminpass")
# #add_bookmark(cx, praw.Reddit("main bot"),"admin","https://reddit.com/r/dankmemes/comments/1kvuprd/i_can_see_the_hidden_camera_now/")
# #add_bookmark(cx, praw.Reddit("main bot"), "admin", "https://reddit.com/r/meirl/comments/1kx2c3z/meirl/")
# #print(get_bookmark(cx, username="notadmin"))
# print(check_password(cx, 'noadmin','pass'))
    