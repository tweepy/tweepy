import tweepy


bearer_token = ""

client = tweepy.Client(bearer_token)

# Get Tweets

# This endpoint/method returns a variety of information about the Tweet(s)
# specified by the requested ID or list of IDs

tweet_ids = [1460323737035677698, 1293593516040269825, 1293595870563381249]

# By default, only the ID and text fields of each Tweet will be returned
# Additional fields can be retrieved using the tweet_fields parameter
response = client.get_tweets(tweet_ids, tweet_fields=["created_at"])

for tweet in response.data:
    print(tweet.id, tweet.created_at)
