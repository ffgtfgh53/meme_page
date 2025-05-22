from flask import Flask, render_template, request
from random import choice#, randint
import praw
from re import sub

app = Flask(__name__)

reddit = praw.Reddit("main bot") #Requires praw.ini file which im not gonna share duh
def get_meme_v2(src:str=''):
    #Ensures not empty subreddit field
    if src == '': src = choice(['memes','dankmemes','meirl','wholesomememes'] * 12
                                + ['historymemes', 'angryupvote', 'artmemes', 'programmerhumor', 'cursedcomments', 'meowirl', 'prequelmemes', 'unexpected'] * 6
                                + ['shitposting','196','meme','youseecomrade']) #For a total of 100 options
    subreddit = reddit.subreddit(src)
    #magic_number = randint(0, 12)
    for i, submission in enumerate(subreddit.random()):

        if submission.over_18:
            return get_meme_v2()
            #No error message?

        common_kwargs = { #For unpacking in render_template
                'subreddit':src, 
                'title':submission.title, 
                'link':'https://reddit.com' + submission.permalink}
                
        if submission.is_self: 
            return get_meme_v2(src)
            #self explanatory, we cant display selfposts

        elif hasattr(submission, 'is_gallery'):
            return get_meme_v2(src)
            #idk how to implement gallery
            #Arrow keys???
            #besides gallery typically not memes

        elif submission.is_video:
            #idk why im using fallback url but ok
            return render_template(
                'video.html', 
                meme=submission.media['reddit_video']['fallback_url'], 
                **common_kwargs)

        elif submission.media != None:
            if submission.media.get('oembed', False):
                #Is embed :cry:
                def resize(match):
                    "used for re.sub() to change width and height of embed"
                    if match.group(1) == "width": return 'width = "90%"'
                    else: return 'height = "70%"'
                return render_template(
                    'embed.html',
                    embed=sub(r'(width|height)=\"\d+\"',resize,submission.media['oembed']['html']),
                    **common_kwargs)

        else:
            #if is image
            return render_template(
                'index.html', 
                meme=submission.url, 
                **common_kwargs
                )
    return get_meme_v2()
    

@app.route('/',methods=["GET"])
def index():
    return get_meme_v2(request.args.get("subreddit", ""))


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8080)