import tweepy

# The app's API/consumer key and secret can be found under the Consumer Keys
# section of the Keys and Tokens tab of your app, under the
# Twitter Developer Portal Projects & Apps page at
# https://developer.twitter.com/en/portal/projects-and-apps
consumer_key = ""
consumer_secret = ""

# The app's access token and secret can be found under the 
# Authentication Tokens section of the  Keys and Tokens tab of your app, 
# under the Twitter Developer Portal Projects & Apps page at
# https://developer.twitter.com/en/portal/projects-and-apps
access_token = ""
access_token_secret = ""

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

# If the authentication was successful, this should print the
# screen name / username of the account
print(api.verify_credentials().screen_name)
