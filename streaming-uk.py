from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import configparser # for reading the configuration file
import os
import sys

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

    def on_data(self, data):

        # DATA IS A STRING, NEEDS TO BE CONVERTED INTO A PYTHON DICTIONARY BEFORE BEING INTERROGATED

        # 1 - use json library to create a json object

        # 2 - get the id (e.g. data['id'] )

        # 3 - write to a file (with filename of tweet id)

        print "read tweet"
        return True

    def on_error(self, status):
        print status




if __name__ == '__main__':
    # Read the twitter authentication stuff from the configuration file (see README for details).
    try:
        if not os.path.isfile('credentials.ini'):
            print "Error, there is no credentials.ini file. See the README for details."
            sys.exit()

        config = configparser.ConfigParser()
        config.read('/home/robin/Dropbox/configs/credentials.ini')

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
    #stream.filter(locations=[-2.17,53.52,-1.20,53.96])
    stream.filter(locations=[-10,50,2,60])
