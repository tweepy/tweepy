import tweepy


# Replace bearer token value with your own
bearer_token = ""

# Initializing the Tweepy client
client = tweepy.Client(bearer_token)

# Replace User IDs
ids = [2244994945, 6253282]

# By default the user ID, name and username are returned. user_fields can be 
# used to specify the additional user data that you want returned for each user
# e.g. profile_image_url
users = client.get_users(ids, user_fields=["profile_image_url"])

# Print the username and the user's profile image url
for user in users.data:
    print(user.username)
    print(user.profile_image_url)
    