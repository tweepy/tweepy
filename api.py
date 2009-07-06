import base64

from binder import bind_api
from parsers import *
from models import User, Status, DirectMessage, Friendship

"""Twitter API"""
class API(object):

  def __init__(self, username=None, password=None, host='twitter.com', secure=False,
                classes={'user': User, 'status': Status,
                'direct_message': DirectMessage, 'friendship': Friendship}):
    if username and password:
      self._b64up = base64.b64encode('%s:%s' % (username, password))
    else:
      self._b64up = None
    self.host = host
    self.secure = secure
    self.classes = classes
    self.username = username

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

  """Get mentions"""
  mentions = bind_api(
      path = '/statuses/mentions.json',
      parser = parse_statuses,
      allowed_param = ['since_id', 'max_id', 'count', 'page'],
      require_auth = True
  )

  """Show status"""
  get_status = bind_api(
      path = '/statuses/show.json',
      parser = parse_status,
      allowed_param = ['id']
  )

  """Update status"""
  update_status = bind_api(
      path = '/statuses/update.json',
      method = 'POST',
      parser = parse_status,
      allowed_param = ['status', 'in_reply_to_status_id'],
      require_auth = True
  )

  """Destroy status"""
  destroy_status = bind_api(
      path = '/statuses/destroy.json',
      method = 'DELETE',
      parser = parse_status,
      allowed_param = ['id'],
      require_auth = True
  )

  """Show user"""
  get_user = bind_api(
      path = '/users/show.json',
      parser = parse_user,
      allowed_param = ['id', 'user_id', 'screen_name']
  )

  """Get authenticated user"""
  def me(self):
    if self.username:
      return self.get_user(screen_name=self.username)
    else:
      return None

  """Show friends"""
  friends = bind_api(
      path = '/statuses/friends.json',
      parser = parse_users,
      allowed_param = ['id', 'user_id', 'screen_name', 'page']
  )

  """Show followers"""
  followers = bind_api(
      path = '/statuses/followers.json',
      parser = parse_users,
      allowed_param = ['id', 'user_id', 'screen_name', 'page'],
      require_auth = True
  )

  """Get direct messages"""
  direct_messages = bind_api(
      path = '/direct_messages.json',
      parser = parse_directmessages,
      allowed_param = ['since_id', 'max_id', 'count', 'page'],
      require_auth = True
  )

  """Sent direct messages"""
  sent_direct_messages = bind_api(
      path = '/direct_messages/sent.json',
      parser = parse_directmessages,
      allowed_param = ['since_id', 'max_id', 'count', 'page'],
      require_auth = True
  )

  """Send direct message"""
  send_direct_message = bind_api(
      path = '/direct_messages/new.json',
      method = 'POST',
      parser = parse_dm,
      allowed_param = ['user', 'text'],
      require_auth = True
  )

  """Destroy direct message"""
  destroy_direct_message = bind_api(
      path = '/direct_messages/destroy.json',
      method = 'DELETE',
      parser = parse_dm,
      allowed_param = ['id'],
      require_auth = True
  )

  """Create friendship"""
  create_friendship = bind_api(
      path = '/friendships/create.json',
      method = 'POST',
      parser = parse_user,
      allowed_param = ['id', 'user_id', 'screen_name', 'follow'],
      require_auth = True
  )

  """Destroy friendship"""
  destroy_friendship = bind_api(
      path = '/friendships/destroy.json',
      method = 'DELETE',
      parser = parse_user,
      allowed_param = ['id', 'user_id', 'screen_name'],
      require_auth = True
  )

  """Check if friendship exists"""
  exists_friendship = bind_api(
      path = '/friendships/exists.json',
      parser = parse_bool,
      allowed_param = ['user_a', 'user_b']
  )

  """Show friendship details"""
  show_friendship = bind_api(
      path = '/friendships/show.json',
      parser = parse_friendship,
      allowed_param = ['source_id', 'source_screen_name',
                        'target_id', 'target_screen_name']
  )

  """Get list of IDs of users the specified user is following"""
  friends_ids = bind_api(
      path = '/friends/ids.json',
      parser = parse_ids,
      allowed_param = ['id', 'user_id', 'screen_name', 'page']
  )

  """Get list of IDs of users following the specified user"""
  followers_ids = bind_api(
      path = '/followers/ids.json',
      parser = parse_ids,
      allowed_param = ['id', 'user_id', 'screen_name', 'page']
  )

  """Verify credentials"""
  verify_credentials = bind_api(
      path = '/account/verify_credentials.json',
      parser = parse_verify_credentials,
      require_auth = True
  )

  """Rate limit status"""
  rate_limit_status = bind_api(
      path = '/account/rate_limit_status.json',
      parser = parse_rate_limit
  )

  """Update delivery device"""
  set_delivery_device = bind_api(
      path = '/account/update_delivery_device.json',
      method = 'POST',
      allowed_param = ['device'],
      parser = parse_user,
      require_auth = True
  )

  """Update profile colors"""
  update_profile_colors = bind_api(
      path = '/account/update_profile_colors.json',
      method = 'POST',
      parser = parse_user,
      allowed_param = ['profile_background_color', 'profile_text_color',
                        'profile_link_color', 'profile_sidebar_fill_color',
                        'profile_sidebar_border_color'],
      require_auth = True
  )

  # todo: add support for changing profile and background images

  """Update profile"""
  update_profile = bind_api(
      path = '/account/update_profile.json',
      method = 'POST',
      parser = parse_user,
      allowed_param = ['name', 'email', 'url', 'location', 'description'],
      require_auth = True
  )

api = API('jitterapp', 'josh1987')
