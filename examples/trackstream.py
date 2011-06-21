#!/usr/bin/env python

from tweepy.streaming import StreamListener, Stream

class Listener ( StreamListener ):
    def on_status( self, status ):
        print status.text, ' from ', status.place['full_name']
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
        print 'timeout'
        return True
 
def main():
 
    USERNAME = "username"
    PASSWORD = "password"
 
    listener = Listener()
    stream = Stream(
      USERNAME,
      PASSWORD,
      listener,
      timeout=None,
    )
 
    # filter messages from Tampa
    stream.filter(locations=['-82.846527','27.961656','-82.611694','28.13255','-82.855453','27.700552','-82.582855','27.964082'])

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print '\nGoodbye!'
