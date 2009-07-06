class Status(object):

  pass

class User(object):

  def timeline(self, **kargs):
    return self._api.user_timeline(**kargs)
  def mentions(self, **kargs):
    return self._api.mentions(**kargs)
  def friends(self, **kargs):
    return self._api.friends(id=self.id, **kargs)
  def followers(self, **kargs):
    return self._api.followers(id=self.id, **kargs)
