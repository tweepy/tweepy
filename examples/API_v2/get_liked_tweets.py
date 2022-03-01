import tweepy


# Replace bearer token value with your own
bearer_token = ""

# Initializing the Tweepy client
client = tweepy.Client(bearer_token)

# Replace User ID
id = '2244994945'

# By default the Tweet ID and text are returned. If you want additional fields,
# request them using the tweet_fields parameter
tweets = client.get_liked_tweets(id=id, tweet_fields=['context_annotations','created_at'])

for tweet in tweets.data:
    print(tweet)
    