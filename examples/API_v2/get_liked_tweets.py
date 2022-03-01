import tweepy


# Replace bearer token value with your own
bearer_token = ""

# Initializing the Tweepy client
client = tweepy.Client(bearer_token)

# Replace User ID
id = '2244994945'

# By default the Tweet ID and Tweet text are returned. If you want additional fields, use the appropriate
# fields and expansions
tweets = client.get_liked_tweets(id=id, tweet_fields=['context_annotations','created_at'])

for tweet in tweets.data:
    print(tweet)
    