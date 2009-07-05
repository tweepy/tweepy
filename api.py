import urllib
import urllib2

from misc import *
from models import *
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
    self.username = username
    self.host = host
    if secure:
      self._schema = 'https'
    else:
      self._schema = 'http'

    # Setup headers
    self._headers = {
      'User-Agent': user_agent
    }

    self._opener = self._build_opener(username, password)

  def public_timeline(self):
    return self._fetch('statuses/public_timelinee.json') 

  @require_auth
  def friends_timeline(self, since_id=None, max_id=None, count=None, page=None):
    raise NotImplementedError

  def _build_opener(self, username, password):
    if username and password:
      bauth = urllib2.HTTPBasicAuthHandler()
      bauth.add_password(None, self.host, username, password)
      return urllib2.build_opener(bauth)
    else:
      return urllib2.build_opener()

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
      return self._opener.open(req)
    except urllib2.HTTPError, e:
      raise TweepError(parse_error(e.read()))
