import base64

from binder import bind_api
from parsers import *
from models import User, Status

"""Twitter API"""
class API(object):

  def __init__(self, username=None, password=None, host='twitter.com', secure=False,
                classes={'user': User, 'status': Status}):
    if username and password:
      self._b64up = base64.b64encode('%s:%s' % (username, password))
    else:
      self._b64up = None
    self.host = host
    self.secure = secure
    self.classes = classes

  """Get public timeline"""
  public_timeline = bind_api(
      path = '/statuses/public_timeline.json',
      parser = parse_statuses,
      allowed_param = []
  )

  """Get friends timeline"""
  friends_timeline = bind_api(
      path = '/statuses/friends_timeline.json',
      parser = parse_statuses,
      allowed_param = ['since_id', 'max_id', 'count', 'page'],
      require_auth = True
  )

  """Get user timeline"""
  user_timeline = bind_api(
      path = '/statuses/user_timeline.json',
      parser = parse_statuses,
      allowed_param = ['id', 'user_id', 'screen_name', 'since_id',
                        'max_id', 'count', 'page']
  )

api = API('jitterapp', 'josh1987')
