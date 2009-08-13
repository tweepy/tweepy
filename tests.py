# Tweepy
# Copyright 2009 Joshua Roesslein
# See LICENSE

import unittest
import random
from time import sleep

from tweepy import *

"""Configurations"""
# Must supply twitter account credentials for tests
username = ''
password = ''

"""Unit tests"""

# API tests
class TweepyAPITests(unittest.TestCase):

  def setUp(self):
    self.api = API(BasicAuthHandler(username, password), username)

  def testpublictimeline(self):
    self.assertEqual(len(self.api.public_timeline()), 20)

  def testfriendstimeline(self):
    self.assert_(len(self.api.friends_timeline()) > 0)

  def testusertimeline(self):
    s = self.api.user_timeline(screen_name='twitter')
    self.assert_(len(s) > 0)
    self.assertEqual(s[0].user.screen_name, 'twitter')

  def testmentions(self):
    s = self.api.mentions()
    self.assert_(len(s) > 0)
    self.assert_(s[0].text.find(username) >= 0)

  def testgetstatus(self):
    s = self.api.get_status(id=123)
    self.assertEqual(s.user.id, 17)

  def testupdateanddestroystatus(self):
    # test update
    text = 'testing %i' % random.randint(0,1000)
    update = self.api.update_status(status=text)
    self.assertEqual(update.text, text)

    # test destroy
    deleted = self.api.destroy_status(id=update.id)
    self.assertEqual(deleted.id, update.id)

  def testgetuser(self):
    u = self.api.get_user(screen_name='twitter')
    self.assertEqual(u.screen_name, 'twitter')

  def testme(self):
    me = self.api.me()
    self.assertEqual(me.screen_name, username)

  def testfriends(self):
    friends = self.api.friends()
    self.assert_(len(friends) > 0)

  def testfollowers(self):
    followers = self.api.followers()
    self.assert_(len(followers) > 0)

  def testdirectmessages(self):
    dms = self.api.direct_messages()
    self.assert_(len(dms) > 0)

  def testsendanddestroydirectmessage(self):
    # send
    sent_dm = self.api.send_direct_message(username, 'test message')
    self.assertEqual(sent_dm.text, 'test message')
    self.assertEqual(sent_dm.sender.screen_name, username)
    self.assertEqual(sent_dm.recipient.screen_name, username)

    # destroy
    destroyed_dm = self.api.destroy_direct_message(sent_dm.id)
    self.assertEqual(destroyed_dm.text, sent_dm.text)
    self.assertEqual(destroyed_dm.id, sent_dm.id)
    self.assertEqual(destroyed_dm.sender.screen_name, username)
    self.assertEqual(destroyed_dm.recipient.screen_name, username)

  def testcreatefriendship(self):
    friend = self.api.create_friendship('twitter')
    self.assertEqual(friend.screen_name, 'twitter')
    self.assertTrue(self.api.exists_friendship(username, 'twitter'))

  def testdestroyfriendship(self):
    enemy = self.api.destroy_friendship('twitter')
    self.assertEqual(enemy.screen_name, 'twitter')
    self.assertFalse(self.api.exists_friendship(username, 'twitter'))

  def testshowfriendship(self):
    source, target = self.api.show_friendship(target_screen_name='twtiter')
    self.assert_(isinstance(source, Friendship))
    self.assert_(isinstance(target, Friendship))

# Authentication tests
class TweepyAuthTests(unittest.TestCase):

  consumer_key = 'ZbzSsdQj7t68VYlqIFvdcA'
  consumer_secret = '4yDWgrBiRs2WIx3bfvF9UWCRmtQ2YKpKJKBahtZcU'

  def testoauth(self):
    auth = OAuthHandler(self.consumer_key, self.consumer_secret)   

    # test getting access token
    auth_url = auth.get_authorization_url()
    self.assert_(auth_url.startswith('http://twitter.com/oauth/authorize?'))
    print 'Please authorize: ' + auth_url
    verifier = raw_input('PIN: ').strip()
    self.assert_(len(verifier) > 0)
    access_token = auth.get_access_token(verifier)
    self.assert_(access_token is not None)

    # build api object test using oauth
    api = API(auth)
    api.update_status('test %i' % random.randint(0,1000))

  def testbasicauth(self):
    auth = BasicAuthHandler(username, password)

    # test accessing twitter API
    api = API(auth)
    api.update_status('test %i' % random.randint(1,1000))


# Cache tests
class TweepyCacheTests(unittest.TestCase):

  timeout = 2.0

  def _run_tests(self):
    # test store and get
    self.cache.store('testkey', 'testvalue')
    self.assertEqual(self.cache.count(), 1, 'Count is wrong')
    self.assertEqual(self.cache.get('testkey'), 'testvalue', 'Stored value does not match retrieved value')

    # test timeout
    sleep(self.timeout)
    self.assertEqual(self.cache.get('testkey'), None, 'Cache entry should have expired')

    # test cleanup
    self.cache.store('testkey', 'testvalue')
    sleep(self.timeout)
    self.cache.cleanup()
    self.assertEqual(self.cache.count(), 0, 'Cache cleanup failed')

    # test flush
    for i in range(0,10):
      self.cache.store('testkey%i' % i, 'testvalue')
    self.cache.flush()
    self.assertEqual(self.cache.count(), 0, 'Cache failed to flush')
    
  def testmemorycache(self):
    self.cache = MemoryCache(timeout=self.timeout)
    self._run_tests()

  def testfilecache(self):
    os.mkdir('cache_test_dir')
    self.cache = FileCache('cache_test_dir', self.timeout)
    self._run_tests()
    self.cache.flush()
    os.rmdir('cache_test_dir')
    

if __name__ == '__main__':
  unittest.main()
    
