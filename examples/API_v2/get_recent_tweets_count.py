import tweepy


bearer_token = ""

client = tweepy.Client(bearer_token)

# Get Recent Tweets Count

# This endpoint/method returns count of Tweets from the last seven days that
# match a search query

query = "Tweepy -is:retweet"

# Granularity is what you want the timeseries count data to be grouped by
# You can request minute, hour, or day granularity
# The default granularity, if not specified is hour
response = client.get_recent_tweets_count(query, granularity="day")

for count in response.data:
    print(count)
