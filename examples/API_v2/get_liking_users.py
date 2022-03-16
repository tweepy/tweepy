import tweepy


bearer_token = ""

client = tweepy.Client(bearer_token)

# Get Tweet's Liking Users

# This endpoint/method allows you to get information about a Tweet’s liking
# users

tweet_id = 1460323737035677698

# By default, only the ID, name, and username fields of each user will be
# returned
# Additional fields can be retrieved using the user_fields parameter
response = client.get_liking_users(tweet_id, user_fields=["profile_image_url"])

for user in response.data:
    print(user.username, user.profile_image_url)
