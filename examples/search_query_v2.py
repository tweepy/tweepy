import tweepy

bearer_token = ""
client = tweepy.Client(bearer_token)

for tweet in client.search_recent_tweets(query = "search query here",max_results=100)[0]:
  print(tweet)
