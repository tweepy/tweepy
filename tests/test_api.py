import os
import shutil
import time
import unittest

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
    @tape.use_cassette('testgetoembed.json')
    def testgetoembed(self):
        data = self.api.get_oembed("https://twitter.com/Twitter/status/" + test_tweet_id)
        self.assertEqual(type(data).__name__, 'dict')
        self.assertEqual(data['author_name'], "Twitter")

    @tape.use_cassette('testparserargumenthastobeaparserinstance.json')
    def testparserargumenthastobeaparserinstance(self):
        """ Testing the issue https://github.com/tweepy/tweepy/issues/421"""
        self.assertRaises(TypeError, API, self.auth, parser=Parser)

    @tape.use_cassette('testhometimeline.json')
    def testhometimeline(self):
        response = self.api.home_timeline()
        self.assertEqual(type(response).__name__, 'ResultSet')

    @tape.use_cassette('testusertimeline.json')
    def testusertimeline(self):
        response = self.api.user_timeline()
        self.assertEqual(type(response).__name__, 'ResultSet')
        self.api.user_timeline(screen_name='Twitter')

    @tape.use_cassette('testmentionstimeline.json')
    def testmentionstimeline(self):
        response = self.api.mentions_timeline()
        self.assertEqual(type(response).__name__, 'ResultSet')

    @tape.use_cassette('testgetretweetsofme.json')
    def testgetretweetsofme(self):
        response = self.api.get_retweets_of_me()
        self.assertEqual(type(response).__name__, 'ResultSet')

    @tape.use_cassette('testretweetandunretweet.json')
    def testretweetandunretweet(self):
        response = self.api.retweet(test_tweet_id)
        self.assertEqual(type(response).__name__, 'Status')
        response = self.api.unretweet(test_tweet_id)
        self.assertEqual(type(response).__name__, 'Status')

    @tape.use_cassette('testgetretweets.json')
    def testgetretweets(self):
        response = self.api.get_retweets(test_tweet_id)
        self.assertEqual(type(response).__name__, 'ResultSet')

    @tape.use_cassette('testgetretweeterids.json')
    def testgetretweeterids(self):
        response = self.api.get_retweeter_ids(test_tweet_id)
        self.assertEqual(type(response).__name__, 'list')
        self.assertEqual(response[0], 2390428970)

    @tape.use_cassette('testgetstatus.json')
    def testgetstatus(self):
        response = self.api.get_status(id=test_tweet_id)
        self.assertEqual(type(response).__name__, 'Status')

    @tape.use_cassette('testupdateanddestroystatus.json')
    def testupdateanddestroystatus(self):
        # test update
        update = self.api.update_status(status=tweet_text)
        self.assertEqual(type(update).__name__, 'Status')
        self.assertEqual(update.text, tweet_text)

        # test destroy
        deleted = self.api.destroy_status(id=update.id)
        self.assertEqual(type(deleted).__name__, 'Status')
        self.assertEqual(deleted.id, update.id)

    @tape.use_cassette('testupdateanddestroystatus.json')
    def testupdateanddestroystatuswithoutkwarg(self):
        # test update, passing text as a positional argument (#554)
        update = self.api.update_status(tweet_text)
        self.assertEqual(type(update).__name__, 'Status')
        self.assertEqual(update.text, tweet_text)

        # test destroy
        deleted = self.api.destroy_status(id=update.id)
        self.assertEqual(type(deleted).__name__, 'Status')
        self.assertEqual(deleted.id, update.id)

    @tape.use_cassette('testupdatestatuswithmedia.yaml', serializer='yaml')
    def testupdatestatuswithmedia(self):
        update = self.api.update_status_with_media(tweet_text, 'assets/banner.png')
        self.assertEqual(type(update).__name__, 'Status')
        self.assertIn(tweet_text + ' https://t.co', update.text)

    @tape.use_cassette('testmediauploadpng.yaml', serializer='yaml')
    def testmediauploadpng(self):
        response = self.api.media_upload('assets/banner.png')
        self.assertEqual(type(response).__name__, 'Media')

    @tape.use_cassette('testmediauploadgif.yaml', serializer='yaml')
    def testmediauploadgif(self):
        response = self.api.media_upload('assets/animated.gif')
        self.assertEqual(type(response).__name__, 'Media')

    @tape.use_cassette('testmediauploadmp4.yaml', serializer='yaml')
    def testmediauploadmp4(self):
        response = self.api.media_upload('assets/video.mp4')
        self.assertEqual(type(response).__name__, 'Media')

    @tape.use_cassette('testgetuser.yaml', serializer='yaml')
    def testgetuser(self):
        u = self.api.get_user(screen_name='Twitter')
        self.assertEqual(type(u).__name__, 'User')
        self.assertEqual(u.screen_name, 'Twitter')

        u = self.api.get_user(user_id=783214)
        self.assertEqual(type(u).__name__, 'User')
        self.assertEqual(u.screen_name, 'Twitter')

    @tape.use_cassette('testlookupusers.json')
    def testlookupusers(self):
        def check(users):
            self.assertEqual(len(users), 2)

        response = self.api.lookup_users(user_id=[6844292, 6253282])
        self.assertEqual(type(response).__name__, 'ResultSet')
        check(response)
        check(self.api.lookup_users(screen_name=['twitterapi', 'twitter']))

    @tape.use_cassette('testsearchusers.json')
    def testsearchusers(self):
        response = self.api.search_users('twitter')
        self.assertEqual(type(response).__name__, 'ResultSet')

    @tape.use_cassette('testgetdirectmessages.json')
    def testgetdirectmessages(self):
        response = self.api.get_direct_messages()
        self.assertEqual(type(response).__name__, 'ResultSet')

    @tape.use_cassette('testsendanddeletedirectmessage.json')
    def testsendanddeletedirectmessage(self):
        me = self.api.verify_credentials()
        self.assertEqual(type(me).__name__, 'User')

        # send
        sent_dm = self.api.send_direct_message(me.id, text='test message')
        self.assertEqual(type(sent_dm).__name__, 'DirectMessage')

        self.assertEqual(sent_dm.message_create['message_data']['text'], 'test message')
        self.assertEqual(int(sent_dm.message_create['sender_id']), me.id)
        self.assertEqual(int(sent_dm.message_create['target']['recipient_id']), me.id)

        # destroy
        deletion = self.api.delete_direct_message(sent_dm.id)
        self.assertIsNone(deletion)

    @tape.use_cassette('testcreatedestroyfriendship.yaml', serializer='yaml')
    def testcreatedestroyfriendship(self):
        enemy = self.api.destroy_friendship(screen_name='Twitter')
        self.assertEqual(type(enemy).__name__, 'User')
        self.assertEqual(enemy.screen_name, 'Twitter')

        friend = self.api.create_friendship(screen_name='Twitter')
        self.assertEqual(type(friend).__name__, 'User')
        self.assertEqual(friend.screen_name, 'Twitter')

    @tape.use_cassette('testgetfriendship.json')
    def testgetfriendship(self):
        response = self.api.get_friendship(target_screen_name='twitter')
        self.assertEqual(type(response).__name__, 'tuple')
        (source, target) = response
        self.assertTrue(isinstance(source, Friendship))
        self.assertTrue(isinstance(target, Friendship))

    @tape.use_cassette('testgetfriendids.yaml', serializer='yaml')
    def testgetfriendids(self):
        response = self.api.get_friend_ids(screen_name=username)
        self.assertEqual(type(response).__name__, 'list')
        self.assertEqual(response[0], 857699969263964161)

    @tape.use_cassette('testgetfollowerids.yaml', serializer='yaml')
    def testgetfollowerids(self):
        response = self.api.get_follower_ids(screen_name=username)
        self.assertEqual(type(response).__name__, 'list')
        self.assertEqual(response[0], 15772978)

    @tape.use_cassette('testgetfriends.yaml', serializer='yaml')
    def testgetfriends(self):
        response = self.api.get_friends(screen_name=username)
        self.assertEqual(type(response).__name__, 'ResultSet')

    @tape.use_cassette('testgetfollowers.yaml', serializer='yaml')
    def testgetfollowers(self):
        response = self.api.get_followers(screen_name=username)
        self.assertEqual(type(response).__name__, 'ResultSet')

    @tape.use_cassette('testverifycredentials.json')
    def testverifycredentials(self):
        response = self.api.verify_credentials()
        self.assertEqual(type(response).__name__, 'User')

        # make sure that `me.status.entities` is not an empty dict
        me = self.api.verify_credentials(include_entities=True)
        self.assertTrue(me.status.entities)

        # `status` shouldn't be included
        me = self.api.verify_credentials(skip_status=True)
        self.assertFalse(hasattr(me, 'status'))

    @tape.use_cassette('testratelimitstatus.json')
    def testratelimitstatus(self):
        response = self.api.rate_limit_status()
        self.assertEqual(type(response).__name__, 'dict')

    @tape.use_cassette('testupdateprofilecolors.json')
    def testupdateprofilecolors(self):
        original = self.api.verify_credentials()
        updated = self.api.update_profile(profile_link_color='D0F900')
        self.assertEqual(type(updated).__name__, 'User')

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

    @tape.use_cassette('testupdateprofilebannerimage.yaml', serializer='yaml')
    def testupdateprofilebannerimage(self):
        response = self.api.update_profile_banner('assets/banner.png')
        self.assertIsNone(response)

    @tape.use_cassette('testupdateprofile.json')
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

    @tape.use_cassette('testgetfavorites.json')
    def testgetfavorites(self):
        response = self.api.get_favorites()
        self.assertEqual(type(response).__name__, 'ResultSet')

    @tape.use_cassette('testcreatedestroyfavorite.json')
    def testcreatedestroyfavorite(self):
        response = self.api.create_favorite(145344012)
        self.assertEqual(type(response).__name__, 'Status')

        response = self.api.destroy_favorite(145344012)
        self.assertEqual(type(response).__name__, 'Status')

    @tape.use_cassette('testcreatedestroyblock.yaml', serializer='yaml')
    def testcreatedestroyblock(self):
        response = self.api.create_block(screen_name='twitter')
        self.assertEqual(type(response).__name__, 'User')

        response = self.api.destroy_block(screen_name='twitter')
        self.assertEqual(type(response).__name__, 'User')

        response = self.api.create_friendship(screen_name='twitter')  # restore
        self.assertEqual(type(response).__name__, 'User')

    @tape.use_cassette('testgetblocks.json')
    def testgetblocks(self):
        response = self.api.get_blocks()
        self.assertEqual(type(response).__name__, 'ResultSet')

    @tape.use_cassette('testgetblockedids.json')
    def testgetblockedids(self):
        response = self.api.get_blocked_ids()
        self.assertEqual(type(response).__name__, 'list')

    @tape.use_cassette('testcreateupdatedestroylist.yaml', serializer='yaml')
    def testcreateupdatedestroylist(self):
        l = self.api.create_list(name="tweeps")
        self.assertEqual(type(l).__name__, 'List')

        l = self.api.update_list(list_id=l.id, description='updated!')
        self.assertEqual(type(l).__name__, 'List')
        self.assertEqual(l.description, 'updated!')

        response = self.api.destroy_list(list_id=l.id)
        self.assertEqual(type(response).__name__, 'List')

    @tape.use_cassette('testgetlists.json')
    def testgetlists(self):
        response = self.api.get_lists()
        self.assertEqual(type(response).__name__, 'ResultSet')

    @tape.use_cassette('testgetlistmemberships.json')
    def testgetlistmemberships(self):
        response = self.api.get_list_memberships()
        self.assertEqual(type(response).__name__, 'ResultSet')

    @tape.use_cassette('testgetlistownerships.json')
    def testgetlistownerships(self):
        response = self.api.get_list_ownerships()
        self.assertEqual(type(response).__name__, 'ResultSet')

    @tape.use_cassette('testgetlistsubscriptions.json')
    def testgetlistsubscriptions(self):
        response = self.api.get_list_subscriptions()
        self.assertEqual(type(response).__name__, 'ResultSet')

    @tape.use_cassette('testlisttimeline.json')
    def testlisttimeline(self):
        response = self.api.list_timeline(owner_screen_name='Twitter', slug='Official-Twitter-Accounts')
        self.assertEqual(type(response).__name__, 'ResultSet')

    @tape.use_cassette('testgetlist.json')
    def testgetlist(self):
        response = self.api.get_list(owner_screen_name='Twitter', slug='Official-Twitter-Accounts')
        self.assertEqual(type(response).__name__, 'List')

    @tape.use_cassette('testaddremovelistmember.json')
    def testaddremovelistmember(self):
        params = {
            'slug': 'test',
            'owner_screen_name': username,
            'screen_name': 'twitter'
        }

        def assert_list(l):
            self.assertEqual(type(l).__name__, 'List')
            self.assertEqual(l.name, params['slug'])

        assert_list(self.api.add_list_member(**params))
        assert_list(self.api.remove_list_member(**params))

    @tape.use_cassette('testaddremovelistmembers.json')
    def testaddremovelistmembers(self):
        params = {
            'slug': 'test',
            'owner_screen_name': username,
            'screen_name': ['Twitter', 'TwitterAPI']
        }

        def assert_list(l):
            self.assertEqual(type(l).__name__, 'List')
            self.assertEqual(l.name, params['slug'])

        assert_list(self.api.add_list_members(**params))
        assert_list(self.api.remove_list_members(**params))

    @tape.use_cassette('testgetlistmembers.json')
    def testgetlistmembers(self):
        response = self.api.get_list_members(owner_screen_name='Twitter', slug='Official-Twitter-Accounts')
        self.assertEqual(type(response).__name__, 'ResultSet')

    @tape.use_cassette('testgetlistmember.json')
    def testgetlistmember(self):
        self.assertTrue(self.api.get_list_member(owner_screen_name='Twitter', slug='Official-Twitter-Accounts', screen_name='TwitterAPI'))

    @tape.use_cassette('testsubscribeunsubscribelist.json')
    def testsubscribeunsubscribelist(self):
        params = {
            'owner_screen_name': 'Twitter',
            'slug': 'Official-Twitter-Accounts'
        }
        response = self.api.subscribe_list(**params)
        self.assertEqual(type(response).__name__, 'List')

        response = self.api.unsubscribe_list(**params)
        self.assertEqual(type(response).__name__, 'List')

    @tape.use_cassette('testgetlistsubscribers.json')
    def testgetlistsubscribers(self):
        response = self.api.get_list_subscribers(owner_screen_name='Twitter', slug='Official-Twitter-Accounts')
        self.assertEqual(type(response).__name__, 'ResultSet')

    @tape.use_cassette('testgetlistsubscriber.json')
    def testgetlistsubscriber(self):
        self.assertTrue(self.api.get_list_subscriber(owner_screen_name='Twitter', slug='Official-Twitter-Accounts', screen_name='TwitterMktg'))

    @tape.use_cassette('testsavedsearches.json')
    def testsavedsearches(self):
        s = self.api.create_saved_search('test')
        self.assertEqual(type(s).__name__, 'SavedSearch')

        response = self.api.get_saved_searches()
        self.assertEqual(type(response).__name__, 'ResultSet')

        search = self.api.get_saved_search(s.id)
        self.assertEqual(type(search).__name__, 'SavedSearch')
        self.assertEqual(search.query, 'test')

        deletion = self.api.destroy_saved_search(s.id)
        self.assertEqual(type(deletion).__name__, 'SavedSearch')

    @tape.use_cassette('testsearchtweets.json')
    def testsearchtweets(self):
        response = self.api.search_tweets('tweepy')
        self.assertEqual(type(response).__name__, 'SearchResults')

    @tape.use_cassette('testgeoapis.json')
    def testgeoapis(self):
        def place_name_in_list(place_name, place_list):
            """Return True if a given place_name is in place_list."""
            return any(x.full_name.lower() == place_name.lower() for x in place_list)

        # Test various API functions using Austin, TX, USA
        geo_result = self.api.geo_id(place_id='1ffd3558f2e98349')
        self.assertEqual(type(geo_result).__name__, 'Place')
        self.assertEqual(geo_result.full_name, 'Dogpatch, San Francisco')

        reverse_result = self.api.reverse_geocode(lat=30.2673701685, long=-97.7426147461)
        self.assertEqual(type(reverse_result).__name__, 'ResultSet')
        self.assertTrue(place_name_in_list('Austin, TX', reverse_result))  # Austin, TX, USA

    @tape.use_cassette('testsupportedlanguages.json')
    def testsupportedlanguages(self):
        languages = self.api.supported_languages()
        self.assertEqual(type(languages).__name__, 'list')
        self.assertEqual(type(languages[0]).__name__, 'dict')

        expected_dict = {
            "code": "en",
            "debug": False,
            "local_name": "English",
            "name": "English",
            "status": "production"
        }
        self.assertTrue(expected_dict in languages)

    @tape.use_cassette('testcachedresult.yaml', serializer='yaml')
    def testcachedresult(self):
        self.api.cache = MemoryCache()
        response = self.api.home_timeline()
        self.assertEqual(type(response).__name__, 'ResultSet')
        self.assertEqual(type(response[0]).__name__, 'Status')
        self.assertFalse(self.api.cached_result)

        self.api.home_timeline()
        self.assertTrue(self.api.cached_result)

    @tape.use_cassette('testcachedresult.yaml', serializer='yaml')
    def testcachedifferentqueryparameters(self):
        self.api.cache = MemoryCache()

        user1 = self.api.get_user(screen_name='TweepyDev')
        self.assertFalse(self.api.cached_result)
        self.assertEqual('TweepyDev', user1.screen_name)
        self.assertEqual(type(user1).__name__, 'User')

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
