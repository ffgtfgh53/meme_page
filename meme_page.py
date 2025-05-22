from flask import Flask, render_template, request
from requests import request as webrequest
from random import randint, choice
import json, praw
from pprint import pprint
from re import sub, Match

app = Flask(__name__)

reddit = praw.Reddit("main bot") #Requires praw.ini file which im not gonna share duh
def get_meme_v2(src:str=''):
    print(src)
    if src == '': src = choice(['memes','dankmemes','meirl']*9+['shitposting','196','meme'])
    print(src)
    print(src)
    subreddit = reddit.subreddit(src)
    magic_number = randint(0, 12)
    for i, submission in enumerate(subreddit.random_rising(limit=16)):
        if i != magic_number: 
            continue
        if submission.over_18:
            magic_number += 1
            continue #Will be at least 2 chances to get non NSFW post
        if submission.is_self: 
            return get_meme_v2(src)
            #self explanatory, we cant display selfposts
        elif hasattr(submission, 'is_gallery'):
            return get_meme_v2(src)
            #idk how to implement gallery that looks nice
            #besides gallery typically not memes
        elif submission.is_video:
            #idk why im using fallback but ok
            return render_template(
                'video.html', 
                meme=submission.media['reddit_video']['fallback_url'], 
                subreddit=src, 
                title=submission.title, 
                link='https://reddit.com' + submission.permalink
                )
        elif submission.media != None:
            if submission.media.get('oembed', False):
                def resize(match:Match):
                    if match.group(1) == "width": return 'width = "90%"'
                    else: return 'height = "70%"'
                return render_template(
                    'embed.html',
                    embed=sub(r'(width|height)=\"\d+\"',resize,submission.media['oembed']['html']),
                    subreddit=src,
                    title=submission.title,
                    link='https://reddit.com' + submission.permalink
            )
        else:
            #if is image
            return render_template(
                'index.html', 
                meme=submission.url, 
                subreddit=src, 
                title=submission.title, 
                link='https://reddit.com' + submission.permalink
                )
    print("ran out??")
    return get_meme_v2()
    

@app.route('/',methods=["GET"])
def index():
    print(request.args)
    return get_meme_v2(request.args.get("subreddit", ""))


if __name__ == "__main__":
    app.run(debug=True)