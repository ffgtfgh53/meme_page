from re import sub
from flask import Flask, render_template, request, session
from random import choice#, randint
import praw

from pprint import pprint

app = Flask(__name__)

app.config.from_pyfile('config.py')

def init():
    session['src'] = ''
    session['return_selfpost'] = False
    session['nsfw'] = False
    session['init'] = True

reddit = praw.Reddit("main bot") #Requires praw.ini file which im not gonna share duh

def get_meme_v2(failed:int=0):
    #Ensures not empty subreddit field
    if session['src'] == '' or failed > 6: src = (['memes','dankmemes','meirl','wholesomememes'] * 12
                                + ['historymemes', 'angryupvote', 'artmemes', 'programmerhumor', 'cursedcomments', 'meowirl', 'prequelmemes', 'unexpected'] * 6
                                + ['shitposting','196','meme','youseecomrade']) #For a total of 100 options
    elif type(session['src']) == str : src = session['src'].split('+')
    #At this stage session['src'] will be a list of possible subreddits
    subreddit_display_name = choice(src)
    print(subreddit_display_name)
    for submission in reddit.subreddit(subreddit_display_name).random_rising(limit=1):

        if submission.over_18 and not session['nsfw']:
            print("\nNSFW\n")
            return get_meme_v2(failed=failed+1)


        elif submission.is_self and not session['return_selfpost']: 
            print("\nisself\n")
            return get_meme_v2(failed=failed+1)


        elif hasattr(submission, 'is_gallery'):
            print("\nisgallery\n")
            return get_meme_v2()
            #idk how to implement gallery
            #Arrow keys???
            #besides gallery typically not memes

        common_kwargs = { #For unpacking in render_template
                'subreddit':subreddit_display_name, 
                'title':submission.title, 
                'link':'https://reddit.com' + submission.permalink}
                

        if submission.is_video:
            #idk why im using fallback url but ok
            return render_template(
                'media/video.html', 
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
                    'media/embed.html',
                    embed=sub(r'(width|height)=\"\d+\"',resize,submission.media['oembed']['html']),
                    **common_kwargs)

        elif submission.is_self:
            return render_template(
                "media/embed.html",
                embed=submission.selftext_html,
                **common_kwargs
            )
        else:
            #if is image
            return render_template(
                'media/index.html', 
                meme=submission.preview['images'][0]['resolutions'][-1]['url'], 
                **common_kwargs
                )
    


@app.route('/',methods=["GET"])
def index():
    if 'init' not in session: init()
    passed = 0
    try: session['src'] = request.args['subreddit']
    except: passed += 1
    try: session['return_selfpost'] = True if request.args["return_selfpost"].lower() == "true" else False
    except: passed += 1
    try: session['nsfw'] = True if request.args["plsplsplsimdesperateshowmensfw"].lower() == "true" else False
    except: passed += 1
    if passed < 3: app.redirect('/')
    return get_meme_v2()

@app.route('/',methods=["POST"])
def settings():
    return render_template('settings/settings')

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8080, debug=True)