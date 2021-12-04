import tweepy

consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

# the app can only retrieve fixed number of objects per
# request, with pagination it could be solved and more than 
# that amount can be gathered

for status in tweepy.Cursor(api.search_tweets, "search query here",
                            count=100).items(200):
    print(status.text)

for page in tweepy.Cursor(api.get_followers, screen_name="user name here",
                          count=100).pages(3):
    print(len(page))
