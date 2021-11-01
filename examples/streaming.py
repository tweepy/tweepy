import tweepy


consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""

# Subclass Stream to print IDs of Tweets received
class IDPrinter(tweepy.Stream):

    def on_status(self, status):
        print(status.id)

# Initialize instance of the subclass
printer = IDPrinter(
  consumer_key, consumer_secret,
  access_token, access_token_secret
)

# Filter realtime Tweets by keyword
printer.filter(track=["Twitter"])
