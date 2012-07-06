from tweepy.streaming import StreamListener
from tweepy.auth import BasicAuthHandler
from tweepy import Stream

TWITTER_USERNAME = ''
TWITTER_PASSWORD = ''

class StdOutListener(StreamListener):
	def on_data(self, data):
		print data
		return True

	def on_error(self, status):
		print status

if __name__ == '__main__':
	l = StdOutListener()
	stream = Stream(BasicAuthHandler(TWITTER_USERNAME, TWITTER_PASSWORD), l)
	stream.filter(track=['basketball'])
