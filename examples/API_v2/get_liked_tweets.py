import tweepy


bearer_token = ""

client = tweepy.Client(bearer_token)

# Get User's Liked Tweets

# This endpoint/method allows you to get information about a user’s liked 
# Tweets

user_id = 2244994945

# By default, only the ID and text fields of each Tweet will be returned
# Additional fields can be retrieved using the tweet_fields parameter
response = client.get_liked_tweets(user_id, tweet_fields=["created_at"])

for tweet in response.data:
    print(tweet.id, tweet.created_at)
