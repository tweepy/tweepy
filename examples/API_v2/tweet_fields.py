import tweepy


bearer_token = ""

client = tweepy.Client(bearer_token)

# You can specify additional Tweet fields to retrieve using tweet_fields
response = client.search_recent_tweets(
    "Tweepy", tweet_fields=["created_at", "lang"]
)
tweets = response.data

# You can then access those fields as attributes of the Tweet objects
for tweet in tweets:
    print(tweet.id, tweet.lang)

# Alternatively, you can also access fields as keys, like a dictionary
for tweet in tweets:
    print(tweet["id"], tweet["lang"])

# There’s also a data attribute/key that provides the entire data dictionary
for tweet in tweets:
    print(tweet.data)
