import tweepy


bearer_token = ""

client = tweepy.Client(bearer_token)

# Get Users

# This endpoint/method returns a variety of information about one or more users
# specified by the requested IDs or usernames

user_ids = [2244994945, 6253282]

# By default, only the ID, name, and username fields of each user will be
# returned
# Additional fields can be retrieved using the user_fields parameter
response = client.get_users(ids=user_ids, user_fields=["profile_image_url"])

for user in response.data:
    print(user.username, user.profile_image_url)
