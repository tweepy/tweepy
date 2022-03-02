import tweepy


# Replace bearer token value with your own
bearer_token = ""

# Initializing the Tweepy client
client = tweepy.Client(bearer_token)

# Replace User ID
id = 2244994945

# By default the Tweet ID and text are returned. If you want additional fields,
# request them using the tweet_fields parameter
tweets = client.get_liked_tweets(id, tweet_fields=["created_at"])

# Print the Tweet id and the time the Tweet was created
for tweet in tweets.data:
    print(tweet.id)
    print(tweet.created_at)
    