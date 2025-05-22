from flask import Flask, render_template, request
from random import choice#, randint
import praw
from re import sub
from pprint import pprint

app = Flask(__name__)

reddit = praw.Reddit("main bot") #Requires praw.ini file which im not gonna share duh
def get_meme_v2(src:str='',failed:int=0):
    #Ensures not empty subreddit field
    if src == '' or failed > 6: src = choice(['memes','dankmemes','meirl','wholesomememes'] * 12
                                + ['historymemes', 'angryupvote', 'artmemes', 'programmerhumor', 'cursedcomments', 'meowirl', 'prequelmemes', 'unexpected'] * 6
                                + ['shitposting','196','meme','youseecomrade']) #For a total of 100 options
    for submission in reddit.subreddit(src).random_rising(limit=1):

        if submission.over_18:
            print("\n\n\nNSFW\n\n\n")
            return get_meme_v2(src, failed=failed+1)
            #No error message?

        elif submission.is_self: 
            print("\n\n\nisself\n\n\n")
            return get_meme_v2(src, failed=failed+1)
            #self explanatory, we cant display selfposts

        elif hasattr(submission, 'is_gallery'):
            print("\n\n\nisgallery\n\n\n")
            return get_meme_v2(src)
            #idk how to implement gallery
            #Arrow keys???
            #besides gallery typically not memes

        common_kwargs = { #For unpacking in render_template
                'subreddit':src, 
                'title':submission.title, 
                'link':'https://reddit.com' + submission.permalink}
                

        if submission.is_video:
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
                    if match.group(1) == "width": return 'width = "70%"'
                    else: return 'height = "70%"'
                return render_template(
                    'embed.html',
                    embed=sub(r'(width|height)=\"\d+\"',resize,submission.media['oembed']['html']),
                    **common_kwargs)

        else:
            #if is image
            return render_template(
                'index.html', 
                meme=submission.preview['images'][0]['resolutions'][-1]['url'], 
                **common_kwargs
                )
    

@app.route('/',methods=["GET"])
def index():
    return get_meme_v2(request.args.get("subreddit", ""))


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8080, debug=True)