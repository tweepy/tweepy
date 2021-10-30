import tweepy


consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

# Follow every follower of the authenticated user
for follower in tweepy.Cursor(api.get_followers).items():
    follower.follow()
