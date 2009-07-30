# Tweepy
# Copyright 2009 Joshua Roesslein
# See LICENSE

import unittest
import random

from tweepy import *

"""Unit tests"""

# API tests
class TweepyAPITests(unittest.TestCase):

  # Must supply twitter account credentials for tests
  username = ''
  password = ''

  def setUp(self):
    self.api = API(BasicAuthHandler(self.username, self.password), self.username)

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

  def testupdateanddestroystatus(self):
    # test update
    text = 'testing %i' % random.randint(0,1000)
    update = self.api.update_status(status=text)
    self.assert_(isinstance(update,Status))
    self.assertEqual(update.text, text)

    # test destroy
    deleted = self.api.destroy_status(id=update.id)
    self.assert_(isinstance(deleted,Status))
    self.assertEqual(deleted.id, update.id)

  def testgetuser(self):
    u = self.api.get_user(screen_name='twitter')
    self.assert_(isinstance(u,User))
    self.assertEqual(u.screen_name, 'twitter')

  def testme(self):
    me = self.api.me()
    self.assert_(isinstance(me,User))
    self.assertEqual(me.screen_name, self.username)

if __name__ == '__main__':
  unittest.main()
    
