from tweepy import *
import json

from twitter_credentials import consumer_key, consumer_secret, access_token, access_token_secret # Calling authorization variables from an external "file.py" 

users_list = ['44196397']
#             @elonmusk
  
class listener(Stream):
    """
    Class to manage pull of data 
    """
    
    def on_data(self, data):
        # Overwrite this method to change your data pull behavior  
        tweets = json.loads(data)
        print(tweets, end='\n\n')
        return tweets
        
    def on_connect(self):
        """Notify when user connected to twitter"""
        print("Connected to Twitter API!")

    def on_error(self, status_code):
        """Handle error codes"""
        if status_code == 420:
            print('Connection issues!')
            return False # Return False if stream disconnects

    def on_status(self, status): 
        """Manage tweet object passing the attributes on status"""
        return status 


def main():
    stream = listener(consumer_key, consumer_secret, access_token, access_token_secret)
    stream.filter(follow=users_list) 
# In this example, through the "follow" statement, the streamer will pull all the tweets that has to do with the username given as input (could even be a list of ids, not only one)

main()
