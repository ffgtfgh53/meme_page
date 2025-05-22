# Meme page

Grabs a random post from the specified subreddit and shows it to the user in a web browser.

Subreddit can be specified using GET.

(i.e. when running on `http://localhost:8080/` use `http://localhost:8080/?subreddit=SUBREDDIT`)

Supported post types:
- Images (including GIFs)
- Videos
- YouTube Embeds

Unsupported post types:
- Self-post/text only (Could theoretically add support)
- Gallery/image carousell (Not sure how to implement)
- Other types? (e.g. polls)


Requires internet connection (obviously).

*Does not show NSFW posts*.

# How to use

To use the project, you must first have a Reddit client ID and client secret.

[praw.ini](./praw.ini) requires `client_id`, `client_secret` and `user_agent`

To read more on `client_id`, `client_secret` and `user_agent`, read [Reddit's API wiki page](https://github.com/reddit-archive/reddit/wiki/API)
# Dependencies
Dependencies are listed in [requirements.txt](./requirements.txt)

To install dependencies simply run `pip install -r requirements.txt` or `pip install flask praw`
