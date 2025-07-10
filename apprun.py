from meme_page import create_app

with open('./praw.ini') as f:
    lines = f.readlines()[1]
if lines[1] == "client_id=CLIENTID":
    raise NotImplementedError('Please add client ID')
if lines[2] == "client_secret=CLIENTSECRET":
    raise NotImplementedError('Please add client secret')
if lines[3] == "user_agent=USERAGENT":
    raise NotImplementedError('Please add appropiate user agent')

if __name__ == "__main__":
    create_app().run(port=8080)
