import time
from getpass import getpass

import tweepy

def callback(status):

  print status.text   

username = raw_input('Twitter username: ')
password = getpass('Twitter password: ')
stream = tweepy.Stream('spritzer', username, password)
stream.connect(callback)

while True:

  try:
    if not stream.running:
      print 'Stream stopped!'
      break

    time.sleep(1)

  except KeyboardInterrupt:
    break

stream.disconnect()
