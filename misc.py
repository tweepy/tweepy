"""
Only allow method to be called with authentication.
"""
def require_auth(func):
  def wrapper(instance, *args, **kargs):
    if instance.username and instance.password:
      func(instance, *args, **kargs)
    else:
      print 'require auth'
  return wrapper

"""
Tweepy exception
"""
class TweepError(Exception):

  def __init__(self, reason):
    self.reason = reason

  def __str__(self):
    return self.reason
