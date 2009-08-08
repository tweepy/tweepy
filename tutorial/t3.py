import tweepy

""" Tutorial 3 -- Models

Tweepy uses a set of models to transfer data from the 
Twitter API to your python application. The following
models are used...

  Status, User, DirectMessage, Friendship,
  SavedSearch, SearchResult
"""

""" Custom Models
A nice feature of Tweepy is that you can extend or even provide
your own implementations of these models. Tweepy simply just sets
the attributes and returns back an instance of your model class.
This makes it easy to integrate your ORM into Tweepy.
"""

"""
First let's create our own implementation of Status.
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

""" Validation

Tweepy's models include a method validate() which can check to
make sure no data is missing from the model. By default the API class
will call this method before returning the models. If the model is 
invalid a TweepError exception will be raised. Validation is handy
to make sure data is present which your application depends on.
Here's a demo...
"""
try:
  u = tweepy.api.get_user('twitter')
except TweepError, e:
  # will be raised if user is invalid OR request failed
  print 'Failed to get user: %s' % e

"""
To disable auto validation...
"""
tweepy.api.validate = False

""" Shortcuts

Some of the models include shortcut functions for accessing
related data from the API.
In this next demo I will show you how to get a list of an user's
friends by using the User model friends() shortcut...
"""
u = tweepy.api.get_user('twitter')
friends = u.friends()
for friend in friends:
  print friend.screen_name

"""
To learn about all shortcuts check out the reference documentation.
"""

""" _api attribute

Shortcuts are possible due to the _api attribute. This is a
reference to the API instance that created the model. Normally you
can just ignore this, but if you plan to pickle or store your models
you must not store this reference. It will not be valid from one 
python instance to the next. When you restore your model from storage
you must re-link it to an API instance if you plan to use the shortcuts.
Example:

u = get_from_storage()
u._api = my_api_instance

"""

""" The End

This concludes the tutorial on models. You have learned how to
implement your own models, perform validation, and using shortcuts
to access related data.
"""

