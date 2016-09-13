import tweepy

#   This example explains tweepy's Status & User Models, and demonstrates
#   parsing the info found in a single tweet ('Status')
#
# Author: Ran Levi, @ranlevi, ran@cmpod.net

#For this example, We use a particular tweet with the following ID:
#(IDs are part of a tweet's URL)

EXAMPLE_ID = '774173247390621696'

#OAuth authentication (see oauth.py in /examples for more info)
CONSUMER_KEY    = "rqqIsNzMCe948Abo3VAAXLMdY"
CONSUMER_SECRET = "d6lFCurrtEMBI7tSU5NylvIpYAOiX4ox2mNwzBP5zRmi1tCnyJ"

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET) #Application Keys, from Twitter

api = tweepy.API(auth) 

#statuses_lookup method returns a list. We grab the first 
#(and only, in this example) item - which is a Status object.
tweet = api.statuses_lookup([EXAMPLE_ID])[0] 

#The Status object follows the Tweets model, described in https://dev.twitter.com/overview/api/tweets.

status = {'created_at'                  : '',
          'Id'                          : '', 
          "id_str"                      : '', 
          "Text"                        : '',
            #(There are many more fields in the Tweet Model - check out the above Twitter document.

          #The User Model follows the model described in https://dev.twitter.com/overview/api/users 
          "user"    : { "id"                    : '',
                        "id_str"                : '', 
                        "contributors_enabled"  : '', 
                        "name"                  : '', 
                        "screen_name"           : '', 
                            #(Again, there are many more fields in the model, we won't cover them all.)
   
                        #Entities follow the model described in https://dev.twitter.com/overview/api/entities 
                        "entities" : {}
                     }, 
         }

# Here we retrive the actual Tweet values from the tweet object. 
# Note that Twitter recommends that applications should be able to handle any
# missing fields in the Tweet - so we use the getattr method to detect any non-existing
# attributes and replace them with a default value ('Does not Exist')

attributes = ['created_at', 'id', 'id_str', 'Text']

for attribute in attributes:
    status[attribute] = getattr(tweet, attribute, 'Does Not Exist')

user_attributes = ['id', 'id_str', 'contributors_enabled', 'name', 'screen_name']

for user_attribute in user_attributes:
    status['user'][user_attribute] = getattr(tweet.user, user_attribute, 'Does Not Exist')

status['user']['entities'] = getattr(tweet.user, 'entities', 'Does Not Exist')

#Go over the keys, print the value.
#if the value is a dict - recuse with it's keys. 

def recursive_printer(_dict):
    # This function travels down a dict object that may hold
    # other dict objects - and prints it's values recursivly.
   
    for key in sorted(_dict.keys()):

        if isinstance(_dict[key], dict): #Is the value a dict? if so, jump inside it.
            recursive_printer(_dict[key]) 
        else:
            print (key + ": " + str(_dict[key])) #It's not a dict, so just print it.
                                                 #Note that values can be Bol, Int, etc. 
                                                 #So we convert them to Str explicitly.
recursive_printer(status)


