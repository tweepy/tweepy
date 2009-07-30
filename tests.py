# Tweepy
# Copyright 2009 Joshua Roesslein
# See LICENSE

import unittest
import random

from api import API
from models import *

"""Unit tests"""

# API tests
class TweepyAPITests(unittest.TestCase):

  # Must supply twitter account credentials for tests
  username = 'jitterapp'
  password = 'omega123'

  def setUp(self):
    self.api = API(self.username, self.password)
    self.update_status_id = None

  def testsetcredentials(self):
    testapi = API()
    testapi.set_credentials('test', 'donttellanyone')
    self.assert_(testapi._b64up)
    self.assertEqual(testapi.username, 'test')

  def testpublictimeline(self):
    s = self.api.public_timeline()
    self.assert_(len(s) == 20)
    self.assert_(isinstance(s[0],Status))

  def testfriendstimeline(self):
    s = self.api.friends_timeline(count=5)
    self.assert_(len(s) == 5)
    self.assert_(isinstance(s[0],Status))

  def testusertimeline(self):
    s = self.api.user_timeline(screen_name='twitter')
    self.assert_(len(s) > 0)
    self.assert_(isinstance(s[0],Status))
    self.assertEqual(s[0].user.screen_name, 'twitter')

  def testmentions(self):
    s = self.api.mentions()
    self.assert_(len(s) > 0)
    self.assert_(isinstance(s[0],Status))

  def testgetstatus(self):
    s = self.api.get_status(id=123)
    self.assert_(isinstance(s,Status))
    self.assertEqual(s.user.id, 17)

  def testupdatestatus(self):
    text = 'testing %i' % random.randint(0,1000)
    update = self.api.update_status('status'=text)
    self.assert_(isinstance(update,Status))
    self.assertEqual(update.text, text)
    self.update_status_id = update.id

  def testdestroystatus(self):
    self.assert_(self.update_status_id)
    deleted = self.api.destroy_status(id=self.update_status_id)
    self.assert_(isinstance(deleted,Status))
    self.assertEqual(deleted.id, self.update_status_id)

  def testshowuser(self):
    u = self.api.show_user(screen_name='twitter')
    self.assert_(isinstance(u,User))
    self.assertEqual(u.screen_name, 'twitter')

  def testme(self):
    me = self.api.me()
    self.assert_(isinstance(me,User))
    self.assertEqual(me.screen_name, self.username)

if __name__ == '__main__':
  unittest.main()
    
