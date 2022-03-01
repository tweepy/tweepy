import tweepy


# Replace bearer token value with your own
bearer_token = ""

# Initializing the Tweepy client
client = tweepy.Client(bearer_token)

# Replace Tweet IDs
ids = ["1409935014725177344", "1409931481552543749", "1441054496931541004"]

# By default the Tweet ID and Tweet text are returned. If you want additional 
# Tweet fields, specify those in tweet_fields
tweets = client.get_tweets(ids, tweet_fields=["created_at"])

# Print the Tweet text and the time the Tweet was created
for tweet in tweets.data:
    print(tweet)
    print(tweet.created_at)
    