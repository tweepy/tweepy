import tweepy

consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

user=api.get_user(screen_name= "username here")
recipient_id=user.id
api.send_direct_messege(recepient_id = recipient_id ,text = "hello this messege is send with tweepy!")
