import tweepy

""" Tutorial 3 -- Models

Tweepy uses a set of models to transfer data from the 
Twitter API to your python application. The following
models are used...

  Status, User, DirectMessage, Friendship,
  SavedSearch, SearchResult

A nice feature of Tweepy is that you can extend or even provide
your own implementations of these models. Tweepy simply just sets
the attributes and returns back an instance of your model class.
This makes it easy to intergrate your ORM into Tweepy.
"""

"""
First let's create our own implementaion of Status.
"""
class MyStatus(tweepy.Status):

  def length(self):
    """Return length of status text"""
    return len(self.text)

"""
We must now register our implementation of Status with tweepy.
"""
tweepy.models['status'] = MyStatus

"""
Now to test out our new status model...
"""
s = tweepy.api.get_status(123)
print 'Length of status 123: %i' % s.length()

"""
As you can see once you register your model with tweepy
it will be used for each API call. If you want to restore
the Status model to tweepy's implementation...
"""
tweepy.models['status'] = tweepy.Status

