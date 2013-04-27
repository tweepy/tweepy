import tweepy

# Go to http://dev.twitter.com and create an app. 
# The consumer key and secret will be generated for you after
consumer_key=''
consumer_secret=''

# After the step above, you will be redirected to your app's page.
# Create an access token under the the "Your access token" section
access_token=''
access_token_secret=''

if __name__ == '__main__':
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    
    api = tweepy.API([auth])
    json_user_timeline = tweepy.binder.bind_api(
        path = '/statuses/user_timeline.json',
        payload_type = 'json', payload_list = True,
        allowed_param = ['id', 'user_id', 'screen_name', 'since_id', 'max_id', 'count', 'page', 'include_rts'])

    # iterate over 50 of tim oreilly's tweets
    for tweet in tweepy.Cursor(json_user_timeline, api, screen_name='timoreilly', count=20, include_rts=True).items(50):
        print tweet['text'].encode('utf-8')