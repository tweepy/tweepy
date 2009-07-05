try:
  import json
except ImportError:
  import simplejson as json

def parse_error(data):

  return json.loads(data)['error']

def _parse_item(type, jsondata):
  t = type()
  for k,v in jsondata.items():
    if k == 'user':
      setattr(t,k, _parse_item(type._User, v))
    else:
      setattr(t,k,v)
  return t

def parse_item(type, data):
  jsondata = json.loads(data)
  return _parse_item(type, jsondata)

def parse_list(type, data):
  types = []

  for obj in json.loads(data):
    types.append(_parse_item(type, obj))

  return types
