import pickle
from google.appengine.ext.webapp import RequestHandler, template
from google.appengine.ext import db
import tweepy

from oauth_example.models import OAuthToken

CONSUMER_KEY = 'e9n31I0z64dagq3WbErGvA'
CONSUMER_SECRET = '9hwCupdAKV8EixeNdN3xrxL9RG3X3JTXI0Q520Oyolo'
CALLBACK = 'http://127.0.0.1:8080/oauth/callback'

# Main page handler  (/oauth/)
class MainPage(RequestHandler):

    def get(self):
        # Build a new oauth handler and display authorization url to user.
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK)
        try:
            print template.render('oauth_example/main.html', {
                    "authurl": auth.get_authorization_url(),
                    "request_token": auth.request_token
            })
        except tweepy.TweepError, e:
            # Failed to get a request token
            print template.render('error.html', {'message': e})
            return

        # We must store the request token for later use in the callback page.
        request_token = OAuthToken(
                token_key = auth.request_token.key,
                token_secret = auth.request_token.secret
        )
        request_token.put()

# Callback page (/oauth/callback)
class CallbackPage(RequestHandler):

    def get(self):
        oauth_token = self.request.get("oauth_token", None)
        oauth_verifier = self.request.get("oauth_verifier", None)
        if oauth_token is None:
            # Invalid request!
            print template.render('error.html', {
                    'message': 'Missing required parameters!'
            })
            return

        # Lookup the request token
        request_token = OAuthToken.gql("WHERE token_key=:key", key=oauth_token).get()
        if request_token is None:
            # We do not seem to have this request token, show an error.
            print template.render('error.html', {'message': 'Invalid token!'})
            return

        # Rebuild the auth handler
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_request_token(request_token.token_key, request_token.token_secret)

        # Fetch the access token
        try:
            auth.get_access_token(oauth_verifier)
        except tweepy.TweepError, e:
            # Failed to get access token
            print template.render('error.html', {'message': e})
            return

        # So now we could use this auth handler.
        # Here we will just display the access token key&secret
        print template.render('oauth_example/callback.html', {
            'access_token': auth.access_token
        })

