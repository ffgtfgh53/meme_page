from random import choice
from re import sub, compile

from flask import Blueprint, flash, redirect, render_template, request, session
from praw.models import Submission

from .extensions import reddit

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
    if 'init_session_vars' not in session: 
        init_session_vars()
    if 'subreddit' in args: 
        if args['subreddit'] == '':
            session['src'] = ' '.join(default_subreddits)
        else:
            session['src'] = args['subreddit']
    if 'change_selfpost_state' in args: 
        session['return_selfpost'] = False
    if 'return_selfpost' in args: 
        session['return_selfpost'] = (args["return_selfpost"].lower() == "true")
        #true, True, TRUE, trUE and tRuE all return True
    if 'change_nsfw_state' in args: 
        session['nsfw'] = False
    if 'plsplsplsimdesperateshowmensfw' in args:
        session['nsfw'] = args["plsplsplsimdesperateshowmensfw"].lower() == "true" 
    

#Regex pattern compilation
embed_dimensions_pattern = compile(r'(width|height)=\"\d+\"')
whitespace = compile(r' +')

def render_meme(submission: Submission, 
                parent: str='index.html.jinja',
                post_type: str='Random', 
                subreddit: str=''):
    """Return a rendered template using the submission.

    parent determines which template it extends.

    type determines the title used when rendering.

    DOES NOT WORK WITH GALLERY!
    
    """
    try:
        if submission.is_gallery: 
            raise NotImplementedError('Cannot render gallery')
    except AttributeError:
        pass
    if subreddit == '':
        subreddit = submission.subreddit.display_name
    common_kwargs = { #For unpacking in render_template
                    'subreddit':subreddit, 
                    'title':submission.title, 
                    'id': submission.id,
                    'post_type': post_type.capitalize(),
                    'parent': parent,}
    if submission.media:
        if submission.is_video:
            #idk why im using fallback url but ok
            return render_template(
                'media/video.html.jinja', 
                meme=submission.media['reddit_video']['fallback_url'], 
                **common_kwargs)
        elif submission.media.get('oembed', False):
            #Submission is embed :cry:
            def resize(match):
                return ('width = "100%"' if (match.group(1) == "width")
                        else 'height = "70%"')
            return render_template(
                'media/embed.html.jinja',
                embed=sub(embed_dimensions_pattern, 
                            resize,
                            submission.media['oembed']['html']),
                **common_kwargs)
    elif submission.is_self:
        return render_template(
            "media/embed.html.jinja",
            embed=submission.selftext_html,
            **common_kwargs)
    else:
        #if is image
        return render_template(
            'media/image.html.jinja', 
            meme=submission.url, 
            **common_kwargs)

def get_meme(failed:int=0):
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
    submission = next(reddit.subreddit(subreddit_display_name).random_rising(limit=1))
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
    return render_meme(submission=submission, 
                        post_type='Random', 
                        subreddit=subreddit_display_name,
                        parent='index.html.jinja')

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
    return render_template('settings/settings.html.jinja')

# if __name__ == "__main__":
#     app.run(host='0.0.0.0',port=8080, debug=True)