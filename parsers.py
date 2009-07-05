try:
  import json
except ImportError:
  import simplejson as json

def parse_error(data):

  return json.loads(data)['error']

def parse_item(type, data):
  t = type()
  for k,v in json.loads(data).items():
    setattr(t, k, v)
  return t

def parse_list(type, data):
  types = []

  for obj in json.loads(data):
    t = type()
    for k,v in obj.items():
      setattr(t, k, v)
    types.append(t)

  return types
