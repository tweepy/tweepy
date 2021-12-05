import tweepy

# The app's API/consumer key and secret can be found under the Consumer Keys
# section of the Keys and Tokens tab of your app, under the
# Twitter Developer Portal Projects & Apps page at
# https://developer.twitter.com/en/portal/projects-and-apps
consumer_key = ""
consumer_secret = ""

# The app's access token, secret and Bearer token can be found under the 
# Authentication Tokens section of the  Keys and Tokens tab of your app, 
# under the Twitter Developer Portal Projects & Apps page at
# https://developer.twitter.com/en/portal/projects-and-apps
bearer_token = ""
access_token = ""
access_token_secret = ""

client = tweepy.Client(bearer_token, consumer_key, consumer_secret,
                       access_token, access_token_secret)

# If the authentication was successful, this should tweet the
# given text in the account
client.create_tweet(text = "This Tweet was Tweeted using Tweepy!")
