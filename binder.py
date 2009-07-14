import httplib
import urllib

from parsers import parse_error
from error import TweepError

def bind_api(path, parser, allowed_param=None, method='GET', require_auth=False):

  def _call(api, *args, **kargs):
    # If require auth, throw exception if credentials not provided
    if require_auth and not api._b64up:
      raise TweepError('Authentication required!')

    # Filter out unallowed parameters
    if allowed_param:
      parameters = dict((k,v) for k,v in kargs.items() if k in allowed_param)
    else:
      parameters = None

    # Open connection
    if api.secure:
      conn = httplib.HTTPSConnection(api.host)
    else:
      conn = httplib.HTTPConnection(api.host)

    # Build url with parameters
    if parameters:
      url = '%s?%s' % (path, urllib.urlencode(parameters))
    else:
      url = path

    # Assemble headers
    headers = {
      'User-Agent': 'tweepy'
    }
    if api._b64up:
      headers['Authorization'] = 'Basic %s' % api._b64up

    # Build request
    conn.request(method, url, headers=headers)

    # Get response
    resp = conn.getresponse()

    # If an error was returned, throw an exception
    if resp.status != 200:
      raise TweepError(parse_error(resp.read()))

    # Pass returned body into parser and return parser output
    out =  parser(resp.read(), api)

    # close connection and return data
    conn.close()
    return out

  return _call
