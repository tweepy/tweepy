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
    
    api = tweepy.API([auth], # support for multiple authentication handlers    
                     retry_count=3, retry_delay=5, retry_errors=set([401, 404, 500, 503]), # retry 3 times with 5 seconds delay when getting these error codes. For more details see https://dev.twitter.com/docs/error-codes-responses   
                     monitor_rate_limit=True, wait_on_rate_limit=True # monitor remaining calls and block until replenished
                    )
    
    query = 'cupcake OR donut'
    page_count = 0
    for tweets in tweepy.Cursor(api.search, q=query, count=100, result_type="recent", include_entities=True).pages():
        page_count += 1
        # print just the first tweet out of every page of 100 tweets
        print tweets[0].text.encode('utf-8')
        # stop after retrieving 200 pages
        if page_count >= 200: 
            break