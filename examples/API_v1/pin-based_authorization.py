import tweepy

# PIN-based OAuth
# https://developer.twitter.com/en/docs/authentication/oauth-1-0a/pin-based-oauth

# Your app's API/consumer key and secret can be found under the Consumer Keys
# section of the Keys and Tokens tab of your app, under the
# Twitter Developer Portal Projects & Apps page at
# https://developer.twitter.com/en/portal/projects-and-apps
consumer_key = ""
consumer_secret = ""

auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret)

# This prints a URL that can be used to authorize your app
# After granting access to the app, a PIN to complete the authorization process
# will be displayed
print(auth.get_authorization_url())
# Enter that PIN to continue
verifier = input("PIN: ")

auth.get_access_token(verifier)

api = tweepy.API(auth)

# If the authentication was successful, this should print the
# screen name / username of the account
print(api.verify_credentials().screen_name)
