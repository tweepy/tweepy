import urllib
import urllib2
import base64

from misc import TweepError, require_auth
from models import Status, User
from parsers import *

"""
Twitter API Interface
"""
class API(object):

  def __init__(self, username=None, password=None, host='twitter.com',
                user_agent='tweepy', secure=False,
                user_class=User, status_class=Status):
    self._Status = status_class
    self._User = user_class
    self.host = host
    if secure:
      self._schema = 'https'
    else:
      self._schema = 'http'

    # Setup headers
    self._headers = {}
    self._headers['User-Agent'] = user_agent
    if username and password:
      self._auth = True
      self._headers['Authorization'] = \
          'Basic ' + base64.encodestring('%s:%s' % (username, password))[:-1]
    else:
      self._auth = False

  def public_timeline(self):
    return parse_list(self._Status, self._fetch('statuses/public_timeline.json'))

  @require_auth
  def friends_timeline(self, since_id=None, max_id=None, count=None, page=None):
    return self._fetch('statuses/friends_timeline.json')

  def _fetch(self, url, parameters=None, post_data=None):
    # Build the url
    if parameters:
      _url = '%s://%s/%s?%s' % (self._schema, self.host, urllib.urlencode(parameters))
    else:
      _url = '%s://%s/%s' % (self._schema, self.host, url)

    # Encode post data
    post = None
    if post_data:
      post = urllib.encode(post_data)

    # Build the request
    req = urllib2.Request(_url, post, self._headers)

    # Send request
    try:
      return urllib2.urlopen(req).read()
    except urllib2.HTTPError, e:
      raise TweepError(parse_error(e.read()))
