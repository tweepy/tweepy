import os
import shutil
import time
import unittest
from ast import literal_eval

from config import tape, TweepyTestCase, username
from tweepy import API, FileCache, MemoryCache
from tweepy.models import Friendship
from tweepy.parsers import Parser

test_tweet_id = '266367358078169089'
tweet_text = 'testing 1000'

"""Unit tests"""


class TweepyAPITests(TweepyTestCase):

    #@tape.use_cassette('testfailure.json')
    #def testapierror(self):
    #    from tweepy.errors import TweepyException
    #
    #    with self.assertRaises(TweepyException) as cm:
    #        self.api.direct_messages()
    #
    #    reason, = literal_eval(cm.exception.reason)
    #    self.assertEqual(reason['message'], 'Bad Authentication data.')
    #    self.assertEqual(reason['code'], 215)
    #    self.assertEqual(cm.exception.api_code, 215)

    # TODO: Actually have some sort of better assertion
    @tape.use_cassette('testgetoembed.json', serializer='json')
    def testgetoembed(self):
        data = self.api.get_oembed("https://twitter.com/Twitter/status/" + test_tweet_id)
        self.assertEqual(data['author_name'], "Twitter")

    @tape.use_cassette('testparserargumenthastobeaparserinstance.json',
                       serializer='json')
    def testparserargumenthastobeaparserinstance(self):
        """ Testing the issue https://github.com/tweepy/tweepy/issues/421"""
        self.assertRaises(TypeError, API, self.auth, parser=Parser)

    @tape.use_cassette('testhometimeline.json', serializer='json')
    def testhometimeline(self):
        self.api.home_timeline()

    @tape.use_cassette('testusertimeline.json', serializer='json')
    def testusertimeline(self):
        self.api.user_timeline()
        self.api.user_timeline(screen_name='Twitter')

    @tape.use_cassette('testmentionstimeline.json', serializer='json')
    def testmentionstimeline(self):
        self.api.mentions_timeline()

    @tape.use_cassette('testgetretweetsofme.json', serializer='json')
    def testgetretweetsofme(self):
        self.api.get_retweets_of_me()

    @tape.use_cassette('testretweetandunretweet.json', serializer='json')
    def testretweetandunretweet(self):
        self.api.retweet(test_tweet_id)
        self.api.unretweet(test_tweet_id)

    @tape.use_cassette('testgetretweets.json', serializer='json')
    def testgetretweets(self):
        self.api.get_retweets(test_tweet_id)

    @tape.use_cassette('testgetretweeterids.json', serializer='json')
    def testgetretweeterids(self):
        self.api.get_retweeter_ids(test_tweet_id)

    @tape.use_cassette('testgetstatus.json', serializer='json')
    def testgetstatus(self):
        self.api.get_status(id=test_tweet_id)

    @tape.use_cassette('testupdateanddestroystatus.json', serializer='json')
    def testupdateanddestroystatus(self):
        # test update
        update = self.api.update_status(status=tweet_text)
        self.assertEqual(update.text, tweet_text)

        # test destroy
        deleted = self.api.destroy_status(id=update.id)
        self.assertEqual(deleted.id, update.id)

    @tape.use_cassette('testupdateanddestroystatus.json', serializer='json')
    def testupdateanddestroystatuswithoutkwarg(self):
        # test update, passing text as a positional argument (#554)
        update = self.api.update_status(tweet_text)
        self.assertEqual(update.text, tweet_text)

        # test destroy
        deleted = self.api.destroy_status(id=update.id)
        self.assertEqual(deleted.id, update.id)

    @tape.use_cassette('testupdatestatuswithmedia.yaml')
    def testupdatestatuswithmedia(self):
        update = self.api.update_status_with_media(tweet_text, 'assets/banner.png')
        self.assertIn(tweet_text + ' https://t.co', update.text)

    @tape.use_cassette('testmediauploadpng.yaml')
    def testmediauploadpng(self):
        self.api.media_upload('assets/banner.png')

    @tape.use_cassette('testmediauploadgif.yaml')
    def testmediauploadgif(self):
        self.api.media_upload('assets/animated.gif')

    @tape.use_cassette('testmediauploadmp4.yaml')
    def testmediauploadmp4(self):
        self.api.media_upload('assets/video.mp4')

    @tape.use_cassette('testgetuser.yaml')
    def testgetuser(self):
        u = self.api.get_user(screen_name='Twitter')
        self.assertEqual(u.screen_name, 'Twitter')

        u = self.api.get_user(user_id=783214)
        self.assertEqual(u.screen_name, 'Twitter')

    @tape.use_cassette('testlookupusers.json', serializer='json')
    def testlookupusers(self):
        def check(users):
            self.assertEqual(len(users), 2)
        check(self.api.lookup_users(user_id=[6844292, 6253282]))
        check(self.api.lookup_users(screen_name=['twitterapi', 'twitter']))

    @tape.use_cassette('testsearchusers.json', serializer='json')
    def testsearchusers(self):
        self.api.search_users('twitter')

    @tape.use_cassette('testgetdirectmessages.json', serializer='json')
    def testgetdirectmessages(self):
        self.api.get_direct_messages()

    @tape.use_cassette('testsendanddeletedirectmessage.json',
                       serializer='json')
    def testsendanddeletedirectmessage(self):
        me = self.api.verify_credentials()

        # send
        sent_dm = self.api.send_direct_message(me.id, text='test message')
        self.assertEqual(sent_dm.message_create['message_data']['text'], 'test message')
        self.assertEqual(int(sent_dm.message_create['sender_id']), me.id)
        self.assertEqual(int(sent_dm.message_create['target']['recipient_id']), me.id)

        # destroy
        self.api.delete_direct_message(sent_dm.id)

    @tape.use_cassette('test_api_indicate_direct_message_typing.yaml')
    def test_indicate_direct_message_typing(self):
        me = self.api.verify_credentials()

        self.api.indicate_direct_message_typing(me.id)

    # TODO: Test API.mark_direct_message_read

    @tape.use_cassette('testcreatedestroyfriendship.yaml')
    def testcreatedestroyfriendship(self):
        enemy = self.api.destroy_friendship(screen_name='Twitter')
        self.assertEqual(enemy.screen_name, 'Twitter')

        friend = self.api.create_friendship(screen_name='Twitter')
        self.assertEqual(friend.screen_name, 'Twitter')

    @tape.use_cassette('testgetfriendship.json', serializer='json')
    def testgetfriendship(self):
        source, target = self.api.get_friendship(target_screen_name='twitter')
        self.assertTrue(isinstance(source, Friendship))
        self.assertTrue(isinstance(target, Friendship))

    @tape.use_cassette('testgetfriendids.yaml')
    def testgetfriendids(self):
        self.api.get_friend_ids(screen_name=username)

    @tape.use_cassette('testgetfollowerids.yaml')
    def testgetfollowerids(self):
        self.api.get_follower_ids(screen_name=username)

    @tape.use_cassette('testgetfriends.yaml')
    def testgetfriends(self):
        self.api.get_friends(screen_name=username)

    @tape.use_cassette('testgetfollowers.yaml')
    def testgetfollowers(self):
        self.api.get_followers(screen_name=username)

    @tape.use_cassette('testverifycredentials.json', serializer='json')
    def testverifycredentials(self):
        self.api.verify_credentials()

        # make sure that `me.status.entities` is not an empty dict
        me = self.api.verify_credentials(include_entities=True)
        self.assertTrue(me.status.entities)

        # `status` shouldn't be included
        me = self.api.verify_credentials(skip_status=True)
        self.assertFalse(hasattr(me, 'status'))

    @tape.use_cassette('testratelimitstatus.json', serializer='json')
    def testratelimitstatus(self):
        self.api.rate_limit_status()

    @tape.use_cassette('testupdateprofilecolors.json', serializer='json')
    def testupdateprofilecolors(self):
        original = self.api.verify_credentials()
        updated = self.api.update_profile(profile_link_color='D0F900')

        # restore colors
        self.api.update_profile(
            profile_link_color=original.profile_link_color,
        )

        self.assertEqual(updated.profile_background_color, '000000')
        self.assertEqual(updated.profile_text_color, '000000')
        self.assertEqual(updated.profile_link_color, 'D0F900')
        self.assertEqual(updated.profile_sidebar_fill_color, '000000')
        self.assertEqual(updated.profile_sidebar_border_color, '000000')

    """
    def testupateprofileimage(self):
        self.api.update_profile_image('examples/profile.png')
    """
    # TODO: Use logo

    @tape.use_cassette('testupdateprofilebannerimage.yaml')
    def testupdateprofilebannerimage(self):
        self.api.update_profile_banner('assets/banner.png')

    @tape.use_cassette('testupdateprofile.json', serializer='json')
    def testupdateprofile(self):
        original = self.api.verify_credentials()
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

    @tape.use_cassette('testgetfavorites.json', serializer='json')
    def testgetfavorites(self):
        self.api.get_favorites()

    @tape.use_cassette('testcreatedestroyfavorite.json', serializer='json')
    def testcreatedestroyfavorite(self):
        self.api.create_favorite(145344012)
        self.api.destroy_favorite(145344012)

    @tape.use_cassette('testcreatedestroyblock.yaml')
    def testcreatedestroyblock(self):
        self.api.create_block(screen_name='twitter')
        self.api.destroy_block(screen_name='twitter')
        self.api.create_friendship(screen_name='twitter')  # restore

    @tape.use_cassette('testgetblocks.json', serializer='json')
    def testgetblocks(self):
        self.api.get_blocks()

    @tape.use_cassette('testgetblockedids.json', serializer='json')
    def testgetblockedids(self):
        self.api.get_blocked_ids()

    @tape.use_cassette('testcreateupdatedestroylist.yaml')
    def testcreateupdatedestroylist(self):
        l = self.api.create_list(name="tweeps")
        l = self.api.update_list(list_id=l.id, description='updated!')
        self.assertEqual(l.description, 'updated!')
        self.api.destroy_list(list_id=l.id)

    @tape.use_cassette('testgetlists.json', serializer='json')
    def testgetlists(self):
        self.api.get_lists()

    @tape.use_cassette('testgetlistmemberships.json', serializer='json')
    def testgetlistmemberships(self):
        self.api.get_list_memberships()

    @tape.use_cassette('testgetlistownerships.json', serializer='json')
    def testgetlistownerships(self):
        self.api.get_list_ownerships()

    @tape.use_cassette('testgetlistsubscriptions.json', serializer='json')
    def testgetlistsubscriptions(self):
        self.api.get_list_subscriptions()

    @tape.use_cassette('testlisttimeline.json', serializer='json')
    def testlisttimeline(self):
        self.api.list_timeline(owner_screen_name='Twitter', slug='Official-Twitter-Accounts')

    @tape.use_cassette('testgetlist.json', serializer='json')
    def testgetlist(self):
        self.api.get_list(owner_screen_name='Twitter', slug='Official-Twitter-Accounts')

    @tape.use_cassette('testaddremovelistmember.json', serializer='json')
    def testaddremovelistmember(self):
        params = {
            'slug': 'test',
            'owner_screen_name': username,
            'screen_name': 'twitter'
        }

        def assert_list(l):
            self.assertEqual(l.name, params['slug'])

        assert_list(self.api.add_list_member(**params))
        assert_list(self.api.remove_list_member(**params))

    @tape.use_cassette('testaddremovelistmembers.json', serializer='json')
    def testaddremovelistmembers(self):
        params = {
            'slug': 'test',
            'owner_screen_name': username,
            'screen_name': ['Twitter', 'TwitterAPI']
        }

        def assert_list(l):
            self.assertEqual(l.name, params['slug'])

        assert_list(self.api.add_list_members(**params))
        assert_list(self.api.remove_list_members(**params))

    @tape.use_cassette('testgetlistmembers.json', serializer='json')
    def testgetlistmembers(self):
        self.api.get_list_members(owner_screen_name='Twitter', slug='Official-Twitter-Accounts')

    @tape.use_cassette('testgetlistmember.json', serializer='json')
    def testgetlistmember(self):
        self.assertTrue(self.api.get_list_member(owner_screen_name='Twitter', slug='Official-Twitter-Accounts', screen_name='TwitterAPI'))

    @tape.use_cassette('testsubscribeunsubscribelist.json', serializer='json')
    def testsubscribeunsubscribelist(self):
        params = {
            'owner_screen_name': 'Twitter',
            'slug': 'Official-Twitter-Accounts'
        }
        self.api.subscribe_list(**params)
        self.api.unsubscribe_list(**params)

    @tape.use_cassette('testgetlistsubscribers.json', serializer='json')
    def testgetlistsubscribers(self):
        self.api.get_list_subscribers(owner_screen_name='Twitter', slug='Official-Twitter-Accounts')

    @tape.use_cassette('testgetlistsubscriber.json', serializer='json')
    def testgetlistsubscriber(self):
        self.assertTrue(self.api.get_list_subscriber(owner_screen_name='Twitter', slug='Official-Twitter-Accounts', screen_name='TwitterMktg'))

    @tape.use_cassette('testsavedsearches.json', serializer='json')
    def testsavedsearches(self):
        s = self.api.create_saved_search('test')
        self.api.get_saved_searches()
        self.assertEqual(self.api.get_saved_search(s.id).query, 'test')
        self.api.destroy_saved_search(s.id)

    @tape.use_cassette('testsearchtweets.json', serializer='json')
    def testsearchtweets(self):
        self.api.search_tweets('tweepy')

    @tape.use_cassette('testgeoapis.json', serializer='json')
    def testgeoapis(self):
        def place_name_in_list(place_name, place_list):
            """Return True if a given place_name is in place_list."""
            return any(x.full_name.lower() == place_name.lower() for x in place_list)

        # Test various API functions using Austin, TX, USA
        self.assertEqual(self.api.geo_id(place_id='1ffd3558f2e98349').full_name, 'Dogpatch, San Francisco')
        self.assertTrue(place_name_in_list('Austin, TX',
            self.api.reverse_geocode(lat=30.2673701685, long= -97.7426147461)))  # Austin, TX, USA

    @tape.use_cassette('testsupportedlanguages.json', serializer='json')
    def testsupportedlanguages(self):
        languages = self.api.supported_languages()
        expected_dict = {
            "code": "en",
            "debug": False,
            "local_name": "English",
            "name": "English",
            "status": "production"
        }
        self.assertTrue(expected_dict in languages)

    @tape.use_cassette('testcachedresult.yaml')
    def testcachedresult(self):
        self.api.cache = MemoryCache()
        self.api.home_timeline()
        self.assertFalse(self.api.cached_result)
        self.api.home_timeline()
        self.assertTrue(self.api.cached_result)

    @tape.use_cassette('testcachedresult.yaml')
    def testcachedifferentqueryparameters(self):
        self.api.cache = MemoryCache()

        user1 = self.api.get_user(screen_name='TweepyDev')
        self.assertFalse(self.api.cached_result)
        self.assertEqual('TweepyDev', user1.screen_name)

        user2 = self.api.get_user(screen_name='Twitter')
        self.assertEqual('Twitter', user2.screen_name)
        self.assertFalse(self.api.cached_result)


class TweepyCacheTests(unittest.TestCase):
    timeout = 0.5
    memcache_servers = ['127.0.0.1:11211']  # must be running for test to pass

    def _run_tests(self, do_cleanup=True):
        # test store and get
        self.cache.store('testkey', 'testvalue')
        self.assertEqual(self.cache.get('testkey'), 'testvalue',
            'Stored value does not match retrieved value')

        # test timeout
        time.sleep(self.timeout)
        self.assertEqual(self.cache.get('testkey'), None,
            'Cache entry should have expired')

        # test cleanup
        if do_cleanup:
            self.cache.store('testkey', 'testvalue')
            time.sleep(self.timeout)
            self.cache.cleanup()
            self.assertEqual(self.cache.count(), 0, 'Cache cleanup failed')

        # test count
        for i in range(20):
            self.cache.store(f'testkey{i}', 'testvalue')
        self.assertEqual(self.cache.count(), 20, 'Count is wrong')

        # test flush
        self.cache.flush()
        self.assertEqual(self.cache.count(), 0, 'Cache failed to flush')

    def testmemorycache(self):
        self.cache = MemoryCache(timeout=self.timeout)
        self._run_tests()

    def testfilecache(self):
        os.mkdir('cache_test_dir')
        try:
            self.cache = FileCache('cache_test_dir', self.timeout)
            self._run_tests()
            self.cache.flush()
        finally:
            if os.path.exists('cache_test_dir'):
                shutil.rmtree('cache_test_dir')


if __name__ == '__main__':
    unittest.main()
