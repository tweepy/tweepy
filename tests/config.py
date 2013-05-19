import os

from tweepy.auth import OAuthHandler

username = os.environ.get('TWITTER_USERNAME', '')
oauth_consumer_key = os.environ.get('CONSUMER_KEY', '')
oauth_consumer_secret = os.environ.get('CONSUMER_SECRET', '')
oauth_token = os.environ.get('ACCESS_KEY', '')
oauth_token_secret = os.environ.get('ACCESS_SECRET', '')

def create_auth():
    auth = OAuthHandler(oauth_consumer_key, oauth_consumer_secret)
    auth.set_access_token(oauth_token, oauth_token_secret)
    return auth

