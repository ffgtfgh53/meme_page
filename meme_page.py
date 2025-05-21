from flask import Flask, render_template
from requests import request
import json

app = Flask(__name__)

def get_meme(src:str="") -> tuple[str]:
    url = "https://meme-api.com/gimme/" + src
    response = json.loads(request("GET", url).text)
    if response.get("code") != None : 
        return "", "", f"Error {response["code"]}, {response["message"]}", ""
    if response["nsfw"]:
        return *get_meme(), "(Random meme/image from subreddit contained nsfw, returning random meme)"
    else: 
        return response["preview"][-2], response["subreddit"], response["title"], response["postLink"]

@app.route('/<hmm>')
def subreddit(hmm):
    meme, subreddit, title, link, *extra = get_meme(hmm)
    return render_template('index.html', meme=meme, subreddit=subreddit, title=title, link=link, extra=extra)

@app.route('/')
def index():
    meme, subreddit, title, link = get_meme()
    return render_template('index.html', meme=meme, subreddit=subreddit, title=title, link=link)


if __name__ == "__main__":
    app.run(debug=True)