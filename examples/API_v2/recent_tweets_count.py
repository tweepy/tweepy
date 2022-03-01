import tweepy


# Replace bearer token value with your own
bearer_token = ""

# Initializing the Tweepy client
client = tweepy.Client(bearer_token)

# Replace with your own search query
query = "tweepy -is:retweet"

# Granularity can be day, hour or minute
counts = client.get_recent_tweets_count(query, granularity="day")

# Print the daily count of Tweets for your query
for count in counts.data:
    print(count)
    