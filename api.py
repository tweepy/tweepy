import base64

from binder import bind_api
from parsers import *

"""Twitter API"""
class API(object):

  def __init__(self, username=None, password=None):
    if username and password:
      self._b64up = base64.encode('%s:%s' % (username, password))

  """Twitter API endpoint bindings"""

  """
  Returns the 20 most recent statuses from non-protected users who have
  set a custom icon. The public timeline is cached for 60 seconds
  so requesting it more often than that is a waste of resources.

  Requires Authentication: false
  API Rate limited: true
  Response: list of statuses
  """
  public_timeline = bind_api(
      path = '/statuses/public_timeline.json',
      parser = parse_test,
      allowed_param = []) 
