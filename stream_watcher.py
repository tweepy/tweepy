import time

import tweepy

def callback(stream_object):

  if 'text' in stream_object:
    print stream_object['text']
    

stream = tweepy.Stream('spritzer', 'tweebly', 'omega1987twitter')
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
