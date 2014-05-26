from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import configparser # for reading the configuration file
import os
import sys
import json # For converting string into json object

# add your details
consumer_key=""
consumer_secret=""
access_token=""
access_token_secret=""

class StdOutListener(StreamListener):
    """ A listener handles tweets are the received from the stream.
    This is a basic listener that just prints received tweets to stdout.

    """
    def on_data(self, data):
        print data
        return True

    def on_error(self, status):
        print status

class FileWriterListener(StreamListener):
    """
    A listener handles tweets are the received from the stream, writing them to a file
    """

    def on_data(self, raw_data):

        # Call the parent (StreamReader) function which does some error checking, returning False if
        # this isn't a tweet
        # if super(StreamListener, self).on_data(raw_data) == False:
        #    print "This doesn't look like a tweet"
        #    return False

        # 1 - use json library to create a python dictionary object from the raw data (a 
        # json-formatter string). This can be then be interrogated to find info. about the tweet.

        data = json.loads(raw_data)

        # 2 - get the id (e.g. data['id'] )

        tweetid = str(data['id'])
        print "read tweet",tweetid

        # 3 - write to a file (with filename of tweet id)
        f = open('data/tweets.json','a')
        try:
            f.write(raw_data) # 
        finally:
            f.close()

        # P.S. this is a nicer way to write to files using 'with' syntax:
        #with open('data/'+tweetid,'w') as f:
        #    f.write(str(data))

        return True

    def on_error(self, status):
        print status

if __name__ == '__main__':
    # Read the twitter authentication stuff from the configuration file (see README for details).
    try:
        if not os.path.isfile('~/Desktop/credentials.ini'):
            print "Error, there is no credentials.ini file. See the README for details."
            sys.exit()

        config = configparser.ConfigParser()
        config.read('~/Desktop/credentials.ini')

        consumer_key=str(config['CREDENTIALS']['consumer_key'])
        consumer_secret=str(config['CREDENTIALS']['consumer_secret'])
        access_token=str(config['CREDENTIALS']['access_token'])
        access_token_secret=str(config['CREDENTIALS']['access_token_secret'])

    except:
        print "Error reading credentials from credentials.ini"

    #l = StdOutListener()
    l = FileWriterListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    stream = Stream(auth, l)
    stream.filter(locations=[-2.17,53.52,-1.20,53.96])
