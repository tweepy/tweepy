from parsers import parse_error

def bind_api(path, parser, allowed_param=None, method='GET'):

  def _call(api, **kargs):
    # Filter out unallowed parameters
    if len(kargs) == 0:
      parameters = None
    elif allowed_param:
      parameters = dict((k,v) for k,v in kargs.items() if k in allowed_param)
    else:
      parameters = kargs

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
    if api.username and api.b64pass:
      headers['Authorization'] = 'Basic %s' % api.b64pass

    # Build request
    conn.request(method, url, headers=headers)

    # Get response
    resp = conn.getresponse()

    # If an error was returned, throw an exception
    if resp.status != 200:
      raise TweepError(parse_error(resp.read()))

    # Pass returned body into parser and return parser output
    return parser(resp.read())

  return _call
