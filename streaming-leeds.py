from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import configparser # for reading the configuration file
import os
import sys
import json # For converting string into json object
import argparse # For parsing command-line arguments

# add your details
consumer_key=""
consumer_secret=""
access_token=""
access_token_secret=""

# Global variables

credentials_file = "./credentials.ini" # Assume in local directory

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
        # this isn't a tweet.
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



def check_locations(locs):
    """Checks that the locations input from the command line look OK. Exit if not."""
    # argparse will have turned the arguments into a 4-item list
    if locs[0] > locs[2]:
        print "Error with locations ({locs}), min x ({minx}) is greater than max x ({maxx})".format( \
                locs=locs, minx=locs[0], maxx=locs[2])
        sys.exit(1)
    if locs[1] > locs[3]:
        print "Error with locations ({locs}), min y ({miny}) is greater than max y ({maxy})".format( \
                locs=locs, miny=locs[1], maxy=locs[3])
        sys.exit(1)


if __name__ == '__main__':

    # Parse command-line options
    parser = argparse.ArgumentParser()
#    (description='Usage %prog -l <locations> [-c <credentials_file]')
    parser.add_argument('-l', nargs=4, dest='locs', type=float, required=True, \
            help='specify min/max coordinates of bounding box (minx miny maxx maxy)')
    parser.add_argument('-c', nargs=1, dest='cred', type=str, required=False, \
            help='specify location of credentials file', default=credentials_file)
    args = parser.parse_args()
    print args
    print args.cred
    print args.locs

    if not os.path.isfile(args.cred):
        print "Error",args.cred,"doesn't look like a file. See the README for details."
        sys.exit(1)
    credentials_file = args.cred

    locations = args.locs
    check_locations(locations)

    # Read the twitter authentication stuff from the configuration file (see README for details).
    try:
        config = configparser.ConfigParser()
        config.read(credentials_file)

        consumer_key=str(config['CREDENTIALS']['consumer_key'])
        consumer_secret=str(config['CREDENTIALS']['consumer_secret'])
        access_token=str(config['CREDENTIALS']['access_token'])
        access_token_secret=str(config['CREDENTIALS']['access_token_secret'])

    except:
        print "Error reading credentials from", credentials_file

    print "Starting listener on locations:",locations

    #l = StdOutListener()
    l = FileWriterListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    stream = Stream(auth, l)
    stream.filter(locations=locations)
