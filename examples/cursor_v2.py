import tweepy

bearer_token = ""
client = tweepy.Client(bearer_token)


# the app can only retrieve fixed number of objects per
# request, with pagination it could be solved and more than 
# that amount can be gathered

for tweet in tweepy.Paginator(client.search_recent_tweets, "search query here",
                              max_results=100).flatten(limit=250):
    print(tweet)
