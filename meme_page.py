from flask import Flask, render_template
from requests import request
import json

app = Flask(__name__)

def get_meme(src:str="") -> tuple[str, str, str, str]:
    url = "https://meme-api.com/gimme/" + src + '20'
    response = json.loads(request("GET", url).text)
    if response.get("code") != -1 : 
        return "", "", f"Error {response["code"]}, {response[message]}"
    if response["nsfw"]:
        return get_meme()
    else: 
        return response["preview"][-2], response["subreddit"], response["title"], response["postLink"]

@app.route('/<hmm>')
def subreddit(hmm):
    meme, subreddit, title, link = get_meme(hmm)
    return render_template('index.html', meme=meme, subreddit=subreddit, title=title, link=link)

@app.route('/')
def index():
    meme, subreddit, title, link = get_meme()
    return render_template('index.html', meme=meme, subreddit=subreddit, title=title, link=link)


if __name__ == "__main__":
    app.run(debug=True)