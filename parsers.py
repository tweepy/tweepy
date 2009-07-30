from datetime import datetime

try:
  import json
except ImportError:
  import simplejson as json

def parse_error(data):

  return json.loads(data)['error']

def _parse_datetime(str):

  return datetime.strptime(str, '%a %b %d %H:%M:%S +0000 %Y')

def _parse_user(obj, api):

  user = api.classes['user']()
  user._api = api
  for k,v in obj.items():
    if k == 'created_at':
      setattr(user, k, _parse_datetime(v))
    elif k == 'status':
      setattr(user, k, _parse_status(v, api))
    else:
      setattr(user, k, v)
  return user

def parse_user(data, api):

  return _parse_user(json.loads(data), api)

def parse_users(data, api):

  users = []
  for obj in json.loads(data):
    users.append(_parse_user(obj, api))
  return users

def _parse_status(obj, api):

  status = api.classes['status']()
  status._api = api
  for k,v in obj.items():
    if k == 'user':
      setattr(status, k, _parse_user(v, api))
    elif k == 'created_at':
      setattr(status, k, _parse_datetime(v))
    else:
      setattr(status, k, v)
  return status

def parse_status(data, api):

  return _parse_status(json.loads(data), api)

def parse_statuses(data, api):

  statuses = []
  for obj in json.loads(data):
    statuses.append(_parse_status(obj, api))
  return statuses

def _parse_dm(obj, api):

  dm = api.classes['direct_message']()
  dm._api = api
  for k,v in obj.items():
    if k == 'sender':
      setattr(dm, k, _parse_user(v, api))
    elif k == 'created_at':
      setattr(dm, k, _parse_datetime(v))
    else:
      setattr(dm, k, v)
  return dm

def parse_dm(data, api):

  return _parse_dm(json.loads(data), api)

def parse_directmessages(data, api):

  directmessages = []
  for obj in json.loads(data):
    directmessages.append(_parse_dm(obj, api))
  return directmessages

def parse_friendship(data, api):

  relationship = json.loads(data)['relationship']

  # parse source
  source = api.classes['friendship']()
  for k,v in relationship['source'].items():
    setattr(source, k, v)

  # parse target
  target = api.classes['friendship']()
  for k,v in relationship['target'].items():
    setattr(target, k, v)

  return source, target

def _parse_saved_search(obj, api):

  ss = api.classes['saved_search']()
  ss._api = api
  for k,v in obj.items():
    if k == 'created_at':
      setattr(ss, k, _parse_datetime(v))
    else:
      setattr(ss, k, v)
  return ss

def parse_saved_search(data, api):

  return _parse_saved_search(json.loads(data), api)

def parse_saved_searches(data, api):

  saved_searches = []
  saved_search = api.classes['saved_search']()
  for obj in json.loads(data):
    saved_searches.append(_parse_saved_search(obj, api))
  return saved_searches

def parse_json(data, api):

  return json.loads(data)

def parse_return_true(data, api):

  return True

def parse_none(data, api):

  return None
