#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

Quick example of using OAuth and the Streaming interface with a Geographic
bounding box and optionally an additional query filter.

"""

import tweepy

from tweepy.streaming import StreamListener, Stream

class Listener ( StreamListener ):
    def on_status( self, status ):
        try:
            print status.author.name, status.text, status.place['full_name']
        except:
            pass
        return
    def on_error(self, status_code):
        if status_code != 406:
            print 'An error has occured! Status code = %s' % status_code
        else:
            print 'Error: 406, It is possible that your bounding box is ' \
                  'not SouthWest longitude, SouthWest latitude, NorthEast ' \
                  'longitude, Northeast Latitude'
        return True
    def on_timeout(self):
        return True
 
def main():
    """
    Go to:

    https://dev.twitter.com/apps/new

    Create an app, agree to the terms, Create your access token (you may need
    to reload the page).

    Replace the CONSUMER KEY, CONSUMER SECRET, ACCESS TOKEN and ACCESS TOKEN
    SECRET with the values generated from the 
    https://dev.twitter.com/apps/xxxxxx/show page

    You don't need to give the app write privileges as it is only
    going to follow the stream and print the messages within the bounding
    box.

    """

    auth1 = tweepy.auth.OAuthHandler('CONSUMER KEY','CONSUMER SECRET')
    auth1.set_access_token('ACCESS TOKEN','ACCESS TOKEN SECRET')
    api = tweepy.API(auth1)
 
    listener = Listener()
    stream = Stream(auth=auth1, listener=listener, timeout=None,)
 
    # filter messages from Florida and part of Georgia using two bounding
    # boxes
    stream.filter(locations=[
         -87.528076,29.363027,-81.210937,30.836215,
         -82.825928,24.417142,-79.94751,29.363027,
    ])

    # filter messages with the text 'apple'
    #stream.filter(None,['apple'])

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print '\nGoodbye!'
