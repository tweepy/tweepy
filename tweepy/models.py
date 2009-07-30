# Tweepy
# Copyright 2009 Joshua Roesslein
# See LICENSE

class Model(object):

  def __getstate__(self):
    # pickle
    pickle = {}
    for k,v in self.__dict__.items():
      if k == '_api': continue # do not pickle the api reference
      pickle[k] = v
    return pickle

class Status(Model):

  def destroy(self):
    return self._api.destroy_status(id=self.id)

class User(Model):

  def timeline(self, **kargs):
    return self._api.user_timeline(**kargs)
  def mentions(self, **kargs):
    return self._api.mentions(**kargs)
  def friends(self, **kargs):
    return self._api.friends(id=self.id, **kargs)
  def followers(self, **kargs):
    return self._api.followers(id=self.id, **kargs)

class DirectMessage(Model):

  def destroy(self):
    return self._api.destroy_direct_message(id=self.id)

class Friendship(Model):

  pass

class SavedSearch(Model):

  pass

class SearchResult(Model):

  pass
