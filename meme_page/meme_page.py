from re import sub, compile
from random import choice

from flask import Blueprint, render_template, request, session, redirect, flash
from flask_login import LoginManager, current_user
import praw

app = Blueprint('app', __name__)

default_subreddits = (
    ['memes','dankmemes','meirl'] * 2
  + ['historymemes', 'angryupvote', 'wholesomememes', 'programmerhumor', 
     'cursedcomments', 'meowirl', 'prequelmemes', 'unexpected', 'artmemes']
  ) #For a total of 15 options

def init_session_vars():
    session['src'] = ' '.join(default_subreddits)
    session['return_selfpost'] = False
    session['nsfw'] = False
    session['init_session_vars'] = True

def set_args(request):
    if request.method == 'GET': 
        args = request.args
    else: 
        args = request.form
    if 'init_session_vars' not in session: init_session_vars()

    if 'subreddit' in args: session['src'] = args['subreddit']

    if 'change_selfpost_state' in args: session['return_selfpost'] = False
    if 'return_selfpost' in args: 
        session['return_selfpost'] = (args["return_selfpost"].lower() == "true")
        #true, True, TRUE, trUE and tRuE all return True

    if 'change_nsfw_state' in args: session['nsfw'] = False
    if 'plsplsplsimdesperateshowmensfw' in args:
        session['nsfw'] = args["plsplsplsimdesperateshowmensfw"].lower() == "true" 
    
#Requires praw.ini file which im not gonna share duh
reddit = praw.Reddit("main bot") 

#Regex pattern compilation
embed_dimensions_pattern = compile(r'(width|height)=\"\d+\"')
whitespace = compile(r' +')

def get_meme(failed:int=0):

    global default_subreddits

    if failed > 6: 
        error_msg = (
            r"Error: Valid post cannot be found in the specified subreddit(s).\n"
            + "Please enter valid subreddit(s) that contain valid posts"
        )
        flash(error_msg, category='error')
        src = default_subreddits

    else:
        if session['src'] == '': 
            session['src'] = ' '.join(default_subreddits)  

        src = sub(whitespace, ' ', session['src']).split(' ')
    #At this stage session['src'] will be a list of possible subreddits
    subreddit_display_name = choice(src)
    for submission in reddit.subreddit(subreddit_display_name).random_rising(limit=1):
    
        if submission.over_18 and not session['nsfw']:
            print("\nNSFW\n")
            return get_meme(failed=failed+1)


        elif submission.is_self and not session['return_selfpost']: 
            print("\nisself\n")
            return get_meme(failed=failed+1)


        elif hasattr(submission, 'is_gallery'):
            print("\nisgallery\n")
            return get_meme()
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
                #Submission is embed :cry:
                def resize(match):
                    "used for re.sub() to change width and height of embed"
                    if match.group(1) == "width": return 'width = "100%"'
                    else: return 'height = "70%"'
                return render_template(
                    'media/embed.html',
                    embed=sub(embed_dimensions_pattern, resize,
                              submission.media['oembed']['html']),
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
                meme=submission.url, 
                **common_kwargs
                )


@app.route('/',methods=["GET", "POST"])
def index():
    set_args(request)
    if request.form != {}:
        return redirect(request.path)
        #When reloading page from browser will not resend post request
    return get_meme()

@app.route('/settings',methods=["GET","POST"])
def settings():
    set_args(request)
    return render_template('settings/settings.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8080, debug=True)