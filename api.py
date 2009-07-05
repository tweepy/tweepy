import urllib
import httplib
import base64

from misc import TweepError, require_auth, process_param
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
    self._Status._User = self._User
    self._parameters = None
    self._post_data = None

    # Setup headers
    self._headers = {}
    self._headers['User-Agent'] = user_agent
    if username and password:
      self._auth = True
      self._headers['Authorization'] = \
          'Basic ' + base64.encodestring('%s:%s' % (username, password))[:-1]
    else:
      self._auth = False

    if secure:
      self._http = httplib.HTTPSConnection(host)
    else:
      self._http = httplib.HTTPConnection(host)

  def public_timeline(self):
    return parse_list(self._Status, self._fetch('/statuses/public_timeline.json'))

  @require_auth
  @process_param(['since_id'])
  def friends_timeline(self, **kargs):
    if self._parameters:
      for k,v in self._parameters.items():
        print k,v
    #return parse_list(self._Status, self._fetch('/statuses/friends_timeline.json'))

  def _fetch(self, url, method='GET'):
    # Build the url
    if self._parameters:
      _url = '%s?%s' % (url, urllib.urlencode(parameters))
    else:
      _url = url

    # Encode post data
    post = None
    if self._post_data:
      post = urllib.encode(post_data)

    # Send request
    self._http.request(method, _url, body=post, headers=self._headers)
    resp = self._http.getresponse()
    if resp.status != 200:
      raise TweepError(parse_error(resp.read()))
    return resp.read()
