try:
  import json
except ImportError:
  import simplejson as json

def parse_error(jsondata):

  return json.loads(jsondata)['error']
