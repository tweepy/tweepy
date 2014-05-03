import unittest2 as unittest
import random
from time import sleep
import os

from nose import SkipTest

from tweepy import Friendship, MemoryCache, FileCache, API
from tweepy.parsers import Parser
from config import TweepyTestCase, username, use_replay

test_tweet_id = '266367358078169089'
tweet_text = 'testing 1000'

"""Unit tests"""

class TweepyErrorTests(unittest.TestCase):

    def testpickle(self):
        """Verify exceptions can be pickled and unpickled."""
        import pickle
        from tweepy.error import TweepError

        e = TweepError('no reason', {'status': 200})
        e2 = pickle.loads(pickle.dumps(e))

        self.assertEqual(e.reason, e2.reason)
        self.assertEqual(e.response, e2.response)

class TweepyAPITests(TweepyTestCase):

    # TODO: Actually have some sort of better assertion
    def testgetoembed(self):
        data = self.api.get_oembed(test_tweet_id)
        self.assertEqual(data['author_name'], "Twitter")

    def testparserargumenthastobeaparserinstance(self):
        """ Testing the issue https://github.com/tweepy/tweepy/issues/421"""
        self.assertRaises(TypeError, API, self.auth, parser=Parser)

    def testhometimeline(self):
        self.api.home_timeline()

    def testusertimeline(self):
        self.api.user_timeline()
        self.api.user_timeline('twitter')

    def testmentionstimeline(self):
        self.api.mentions_timeline()

    def testretweetsofme(self):
        self.api.retweets_of_me()

    def testretweet(self):
        # TODO(josh): Need a way to get random tweets to retweet.
        raise SkipTest()

    def testretweets(self):
        self.api.retweets(test_tweet_id)

    def testretweeters(self):
        self.api.retweeters(test_tweet_id)

    def testgetstatus(self):
        self.api.get_status(id=test_tweet_id)

    def testupdateanddestroystatus(self):
        # test update
        text = tweet_text if use_replay else 'testing %i' % random.randint(0, 1000)
        update = self.api.update_status(status=text)
        self.assertEqual(update.text, text)

        # test destroy
        deleted = self.api.destroy_status(id=update.id)
        self.assertEqual(deleted.id, update.id)

    def testupdatestatuswithmedia(self):
        update = self.api.update_with_media('examples/banner.png', status=tweet_text)
        self.assertIn(tweet_text + ' http://t.co', update.text)

    def testgetuser(self):
        u = self.api.get_user('twitter')
        self.assertEqual(u.screen_name, 'twitter')

        u = self.api.get_user(783214)
        self.assertEqual(u.screen_name, 'twitter')

    def testlookupusers(self):
        def check(users):
            self.assertEqual(len(users), 2)
        check(self.api.lookup_users(user_ids=[6844292, 6253282]))
        check(self.api.lookup_users(screen_names=['twitterapi', 'twitter']))

    def testsearchusers(self):
        self.api.search_users('twitter')

    def testsuggestedcategories(self):
        self.api.suggested_categories()

    def testsuggestedusers(self):
        categories = self.api.suggested_categories()
        if len(categories) != 0:
            self.api.suggested_users(categories[0].slug)

    def testsuggesteduserstweets(self):
        categories = self.api.suggested_categories()
        if len(categories) != 0:
            self.api.suggested_users_tweets(categories[0].slug)

    def testme(self):
        me = self.api.me()
        self.assertEqual(me.screen_name, username)

    def testdirectmessages(self):
        self.api.direct_messages()

    def testsentdirectmessages(self):
        self.api.sent_direct_messages()

    def testsendanddestroydirectmessage(self):
        # send
        sent_dm = self.api.send_direct_message(username, text='test message')
        self.assertEqual(sent_dm.text, 'test message')
        self.assertEqual(sent_dm.sender.screen_name, username)
        self.assertEqual(sent_dm.recipient.screen_name, username)

        # destroy
        destroyed_dm = self.api.destroy_direct_message(sent_dm.id)
        self.assertEqual(destroyed_dm.text, sent_dm.text)
        self.assertEqual(destroyed_dm.id, sent_dm.id)
        self.assertEqual(destroyed_dm.sender.screen_name, username)
        self.assertEqual(destroyed_dm.recipient.screen_name, username)

    def testcreatedestroyfriendship(self):
        enemy = self.api.destroy_friendship('twitter')
        self.assertEqual(enemy.screen_name, 'twitter')

        # Wait 5 seconds to allow Twitter time
        # to process the friendship destroy request.
        sleep(5)

        friend = self.api.create_friendship('twitter')
        self.assertEqual(friend.screen_name, 'twitter')

    def testshowfriendship(self):
        source, target = self.api.show_friendship(target_screen_name='twitter')
        self.assert_(isinstance(source, Friendship))
        self.assert_(isinstance(target, Friendship))

    def testfriendsids(self):
        self.api.friends_ids(username)

    def testfollowersids(self):
        self.api.followers_ids(username)

    def testfriends(self):
        self.api.friends(username)

    def testfollowers(self):
        self.api.followers(username)

    def testverifycredentials(self):
        self.assertNotEqual(self.api.verify_credentials(), False)

        # make sure that `me.status.entities` is not an empty dict
        me = self.api.verify_credentials(include_entities=True)
        self.assertTrue(me.status.entities)

        # `status` shouldn't be included
        me = self.api.verify_credentials(skip_status=True)
        self.assertFalse(hasattr(me, 'status'))

    def testratelimitstatus(self):
        self.api.rate_limit_status()

    """ TODO(josh): Remove once this deprecated API is gone.
    def testsetdeliverydevice(self):
        self.api.set_delivery_device('im')
        self.api.set_delivery_device('none')
    """

    def testupdateprofilecolors(self):
        original = self.api.me()
        updated = self.api.update_profile_colors('000', '000', '000', '000', '000')

        # restore colors
        self.api.update_profile_colors(
            original.profile_background_color,
            original.profile_text_color,
            original.profile_link_color,
            original.profile_sidebar_fill_color,
            original.profile_sidebar_border_color
        )

        self.assertEqual(updated.profile_background_color, '000000')
        self.assertEqual(updated.profile_text_color, '000000')
        self.assertEqual(updated.profile_link_color, '000000')
        self.assertEqual(updated.profile_sidebar_fill_color, '000000')
        self.assertEqual(updated.profile_sidebar_border_color, '000000')

    """
    def testupateprofileimage(self):
        self.api.update_profile_image('examples/profile.png')

    def testupdateprofilebg(self):
        self.api.update_profile_background_image('examples/bg.png')
    """

    def testupdateprofilebannerimage(self):
        self.api.update_profile_banner('examples/banner.png')

    def testupdateprofile(self):
        original = self.api.me()
        profile = {
            'name': 'Tweepy test 123',
            'location': 'pytopia',
            'description': 'just testing things out'
        }
        updated = self.api.update_profile(**profile)
        self.api.update_profile(
            name = original.name, url = original.url,
            location = original.location, description = original.description
        )

        for k,v in profile.items():
            if k == 'email': continue
            self.assertEqual(getattr(updated, k), v)

    def testfavorites(self):
        self.api.favorites()

    def testcreatedestroyfavorite(self):
        self.api.create_favorite(4901062372)
        self.api.destroy_favorite(4901062372)

    def testcreatedestroyblock(self):
        self.api.create_block('twitter')
        self.api.destroy_block('twitter')
        self.api.create_friendship('twitter') # restore

    def testblocks(self):
        self.api.blocks()

    def testblocksids(self):
        self.api.blocks_ids()

    # TODO: Rewrite test to be less brittle. It fails way too often.
    # def testcreateupdatedestroylist(self):
    #     params = {
    #         'owner_screen_name': username,
    #         'slug': 'tweeps'
    #     }
    #     l = self.api.create_list(name=params['slug'], **params)
    #     l = self.api.update_list(list_id=l.id, description='updated!')
    #     self.assertEqual(l.description, 'updated!')
    #     self.api.destroy_list(list_id=l.id)

    def testlistsall(self):
        self.api.lists_all()

    def testlistsmemberships(self):
        self.api.lists_memberships()

    def testlistssubscriptions(self):
        self.api.lists_subscriptions()

    def testlisttimeline(self):
        self.api.list_timeline('applepie', 'stars')

    def testgetlist(self):
        self.api.get_list(owner_screen_name='applepie', slug='stars')

    def testaddremovelistmember(self):
        params = {
            'slug': 'test',
            'owner_screen_name': username,
            'screen_name': 'twitter'
        }

        def assert_list(l):
            self.assertEqual(l.name, params['slug'])

        assert_list(self.api.add_list_member(**params))
        sleep(3)
        assert_list(self.api.remove_list_member(**params))

    def testaddremovelistmembers(self):
        params = {
            'slug': 'test',
            'owner_screen_name': username,
            'screen_name': ['twitterapi', 'twittermobile']
        }

        def assert_list(l):
            self.assertEqual(l.name, params['slug'])

        assert_list(self.api.add_list_members(**params))
        assert_list(self.api.remove_list_members(**params))

    def testlistmembers(self):
        self.api.list_members('applepie', 'stars')

    def testshowlistmember(self):
        self.assertTrue(self.api.show_list_member(owner_screen_name='applepie', slug='stars', screen_name='NathanFillion'))

    def testsubscribeunsubscribelist(self):
        params = {
            'owner_screen_name': 'applepie',
            'slug': 'stars'
        }
        self.api.subscribe_list(**params)
        self.api.unsubscribe_list(**params)

    def testlistsubscribers(self):
        self.api.list_subscribers('applepie', 'stars')

    def testshowlistsubscriber(self):
        self.assertTrue(self.api.show_list_subscriber('tweepytest', 'test', 'applepie'))

    def testsavedsearches(self):
        s = self.api.create_saved_search('test')
        self.api.saved_searches()
        self.assertEqual(self.api.get_saved_search(s.id).query, 'test')
        self.api.destroy_saved_search(s.id)

    def testsearch(self):
        self.api.search('tweepy')

    def testgeoapis(self):
        def place_name_in_list(place_name, place_list):
            """Return True if a given place_name is in place_list."""
            return any([x.full_name.lower() == place_name.lower() for x in place_list])

        twitter_hq = self.api.geo_similar_places(lat=37, long= -122, name='Twitter HQ')
        # Assumes that twitter_hq is first Place returned...
        self.assertEqual(twitter_hq[0].id, '3bdf30ed8b201f31')
        # Test various API functions using Austin, TX, USA
        self.assertEqual(self.api.geo_id(id='c3f37afa9efcf94b').full_name, 'Austin, TX')
        self.assertTrue(place_name_in_list('Austin, TX',
            self.api.reverse_geocode(lat=30.267370168467806, long= -97.74261474609375))) # Austin, TX, USA

    def testsupportedlanguages(self):
        languages = self.api.supported_languages()
        expected_dict = {
            "name": "English",
            "code": "en",
            "status": "production"
        }
        self.assertTrue(expected_dict in languages)

    def testcachedresult(self):
        self.api.cache = MemoryCache()
        self.api.home_timeline()
        self.assertFalse(self.api.cached_result)
        self.api.home_timeline()
        self.assertTrue(self.api.cached_result)

class TweepyCacheTests(unittest.TestCase):

    timeout = 2.0
    memcache_servers = ['127.0.0.1:11211']  # must be running for test to pass

    def _run_tests(self, do_cleanup=True):
        # test store and get
        self.cache.store('testkey', 'testvalue')
        self.assertEqual(self.cache.get('testkey'), 'testvalue',
            'Stored value does not match retrieved value')

        # test timeout
        sleep(self.timeout)
        self.assertEqual(self.cache.get('testkey'), None,
            'Cache entry should have expired')

        # test cleanup
        if do_cleanup:
            self.cache.store('testkey', 'testvalue')
            sleep(self.timeout)
            self.cache.cleanup()
            self.assertEqual(self.cache.count(), 0, 'Cache cleanup failed')

        # test count
        for i in range(0, 20):
            self.cache.store('testkey%i' % i, 'testvalue')
        self.assertEqual(self.cache.count(), 20, 'Count is wrong')

        # test flush
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
