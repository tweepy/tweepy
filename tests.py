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
    s = self.api.friends_timeline(count=1)
    self.assert_(len(s) == 1)
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

  def testfriends(self):
    friends = self.api.friends()
    self.assert_(len(friends) > 0)
    self.assert_(isinstance(friends[0], User))

  def testfollowers(self):
    followers = self.api.followers()
    self.assert_(len(followers) > 0)
    self.assert_(isinstance(followers[0], User))

  def testdirectmessages(self):
    dms = self.api.direct_messages()
    self.assert_(len(dms) > 0)
    self.assert_(isinstance(dms[0], DirectMessage))

  def testsendanddestroydirectmessage(self):
    # send
    sent_dm = self.api.send_direct_message(self.username, 'test message')
    self.assert_(isinstance(sent_dm, DirectMessage))
    self.assertEqual(sent_dm.text, 'test message')
    self.assertEqual(sent_dm.sender.screen_name, self.username)
    self.assertEqual(sent_dm.recipient.screen_name, self.username)

    # destroy
    destroyed_dm = self.api.destroy_direct_message(sent_dm.id)
    self.assert_(isinstance(destroyed_dm, DirectMessage))
    self.assertEqual(destroyed_dm.text, sent_dm.text)
    self.assertEqual(destroyed_dm.id, sent_dm.id)
    self.assertEqual(destroyed_dm.sender.screen_name, self.username)
    self.assertEqual(destroyed_dm.recipient.screen_name, self.username)

  def testcreatefriendship(self):
    friend = self.api.create_friendship('twitter')
    self.assert_(isinstance(friend, User))
    self.assertEqual(friend.screen_name, 'twitter')
    self.assertTrue(self.api.exists_friendship(self.username, 'twitter'))

  def testdestroyfriendship(self):
    enemy = self.api.destroy_friendship('twitter')
    self.assert_(isinstance(enemy, User))
    self.assertEqual(enemy.screen_name, 'twitter')
    self.assertFalse(self.api.exists_friendship(self.username, 'twitter'))

  def testshowfriendship(self):
    source, target = self.api.show_friendship(target_screen_name='twtiter')
    self.assert_(isinstance(source, Friendship))
    self.assert_(isinstance(target, Friendship))

if __name__ == '__main__':
  unittest.main()
    
