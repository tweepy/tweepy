import tweepy


# Replace bearer token value with your own
bearer_token = ""

# Initializing the Tweepy client
client = tweepy.Client(bearer_token)

# Replace Tweet IDs
ids = ['1409935014725177344', '1409931481552543749', '1441054496931541004']

# By default the Tweet ID and Tweet text are returned. If you want additional fields, use the appropriate
# fields and expansions
tweets = client.get_tweets(ids=ids, tweet_fields=['context_annotations','created_at','geo'])

for tweet in tweets.data:
    print(tweet)
    