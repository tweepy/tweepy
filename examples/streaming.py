from __future__ import absolute_import, print_function

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API


# Override tweepy.StreamListener to add logic
# both default methods on_status and on_error 
# are overridden with added logic
class MyStreamListener(StreamListener):
    # A listener handles tweets that are received from the stream.
    # This is a basic listener that just prints received tweets to stdout.
    def on_status(self, status):
        print(status.text)

    def on_error(self, status):
        print(status)


# Go to http://apps.twitter.com and create an app.
# The consumer key and secret will be generated for you after
consumer_key = ""
consumer_secret = ""

# After the step above, you will be redirected to your app's page.
# Create an access token under the the "Your access token" section
access_token = ""
access_token_secret = ""

# Basic OAuth handling
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = API(auth)

if __name__ == '__main__':
    # Makes a MyStreamListener instance
    myStreamListener = MyStreamListener()
    myStream = Stream(auth = api.auth, listener = myStreamListener)

    # In this example we will use filter to stream all tweets containing the word
    # python. The track parameter is an array of search terms to stream.
    myStream.filter(track = ['python'])
