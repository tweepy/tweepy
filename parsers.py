try:
  import json
except ImportError:
  import simplejson as json

def parse_error(data):

  return json.loads(data)['error']

def _parse_user(obj, classes):

  user = classes['user']()
  for k,v in obj.items():
    setattr(user, k, v)
  return user

def parse_users(data, classes):

  users = []
  for obj in json.loads(data):
    users.append(_parse_user(obj, classes))
  return users

def _parse_status(obj, classes):

  status = classes['status']()
  for k,v in obj.items():
    if k == 'user':
      setattr(status, k, _parse_user(v, classes))
    else:
      setattr(status, k, v)
  return status

def parse_statuses(data, classes):

  statuses = []
  for obj in json.loads(data):
    statuses.append(_parse_status(obj, classes))
  return statuses
