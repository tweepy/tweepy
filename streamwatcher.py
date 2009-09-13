#!/usr/bin/env python

import time
from getpass import getpass

import tweepy


class StreamWatcherListener(tweepy.StreamListener):

    def on_status(self, status):
        print status.text

    def on_error(self, status_code):
        print 'An error has occured! Status code = %s' % status_code
        return True  # keep stream alive

    def on_timeout(self):
        print 'Snoozing Zzzzzz'

# Prompt for login credentials and setup stream object
username = raw_input('Twitter username: ')
password = getpass('Twitter password: ')
stream = tweepy.Stream(username, password, StreamWatcherListener())

# Prompt for mode of streaming and connect
while True:
    mode = raw_input('Mode? [sample/filter] ')
    if mode == 'sample':
        stream.sample()
        break
    elif mode == 'filter':
        follow_list = raw_input('Users to follow (comma separated): ').strip()
        track_list = raw_input('Keywords to track (comma seperated): ').strip()
        if follow_list:
            follow_list = [u for u in follow_list.split(',')]
        else:
            follow_list = None
        if track_list:
            track_list = [k for k in track_list.split(',')]
        else:
            track_list = None
        stream.filter(follow_list, track_list)
        break
    else:
        print 'Invalid choice! Try again.'

# Run in a loop until termination
while True:
    try:
        if stream.running is False:
            print 'Stream stopped!'
            break
        time.sleep(1)
    except KeyboardInterrupt:
        break

# Shutdown connection
stream.disconnect()
print 'Bye!'

