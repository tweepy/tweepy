import tweepy

# === Basic Authentication ===
#
# *Note: Basic Authentication is deprecated and no longer supported on Twitter.
#      It is still provided for use in services like Status.net which still suppports it.*
#
# This mode of authentication requires the user provide their username and plain text password.
# These credentials will then be provided for each request to the API for authentication.

# You would normally fetch this in your application
# by asking the user or loading from some dark place.
username = ""
password = ""

# Create an authentication handler passing it the username and password.
# We will use this object later on when creating our API object.
auth = tweepy.auth.BasicAuthHandler(username, password)

# Create the API object providing it the authentication handler to use.
# Each request will then be authenticated using this handler.
api = tweepy.API(auth)

api.update_status('Updating using basic authentication via Tweepy!')

