import tweepy


bearer_token = ""

client = tweepy.Client(bearer_token)

# Get User's Tweets

# This endpoint/method returns Tweets composed by a single user, specified by
# the requested user ID

user_id = 2244994945

response = client.get_users_tweets(user_id)

# By default, only the ID and text fields of each Tweet will be returned
for tweet in response.data:
    print(tweet.id)
    print(tweet.text)

# By default, the 10 most recent Tweets will be returned
# You can retrieve up to 100 Tweets by specifying max_results
response = client.get_users_tweets(user_id, max_results=100)
