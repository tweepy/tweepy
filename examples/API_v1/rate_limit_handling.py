import tweepy


consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""

auth = tweepy.OAuth1UserHandler(
    consumer_key, consumer_secret, access_token, access_token_secret
)

# Setting wait_on_rate_limit to True when initializing API will initialize an
# instance, called api here, that will automatically wait, using time.sleep,
# for the appropriate amount of time when a rate limit is encountered
api = tweepy.API(auth, wait_on_rate_limit=True)

# This will search for Tweets with the query "Twitter", returning up to the
# maximum of 100 Tweets per request to the Twitter API

# Once the rate limit is reached, it will automatically wait / sleep before
# continuing

for tweet in tweepy.Cursor(api.search_tweets, "Twitter", count=100).items():
    print(tweet.id)
