"""
Only allow method to be called with authentication.
"""
def require_auth(func):
  def wrapper(instance, *args, **kargs):
    if instance._auth:
      return func(instance, **kargs)
    else:
      print 'require auth'
  return wrapper

"""
Process parameters. Perform validation. Build parameter list.
"""
def process_param(allowed_param):
  def decorator(func):
    def wrapper(instance, **kargs):
      if len(kargs):
        instance._parameters = {}
        for k,v in kargs.items():
          if k in allowed_param:
            instance._parameters[k] = v
      return func(instance, **kargs)
    return wrapper
  return decorator

"""
Tweepy exception
"""
class TweepError(Exception):

  def __init__(self, reason):
    self.reason = reason

  def __str__(self):
    return self.reason
