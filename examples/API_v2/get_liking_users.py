import tweepy


# Replace bearer token value with your own
bearer_token = ""

# Initializing the Tweepy client
client = tweepy.Client(bearer_token)

# Replace Tweet ID
id = '1441054496931541004'

# By default the user ID, name and username are returned. user_fields can be used 
# to specify the additional user data that you want returned for each user e.g. profile_image_url
users = client.get_liking_users(id=id, user_fields=['profile_image_url'])

for user in users.data:
    print(user)
    