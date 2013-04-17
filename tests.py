import unittest
import random
from time import sleep
import os, sys

from nose import SkipTest

from tweepy import (API, OAuthHandler, Friendship, Cursor,
                    MemoryCache, FileCache)
from tweepy.error import TweepError

"""Configurations"""
# Must supply twitter account credentials for tests
username = os.environ.get('TWITTER_USERNAME', '')
oauth_keys = eval(os.environ.get('OAUTH_KEYS', '[]'))
if len(oauth_keys) > 0:
    oauth_consumer_key, oauth_consumer_secret, oauth_token, oauth_token_secret = oauth_keys[0]
else:
    oauth_consumer_key = os.environ.get('CONSUMER_KEY', '')
    oauth_consumer_secret = os.environ.get('CONSUMER_SECRET', '')
    oauth_token = os.environ.get('ACCESS_KEY', '')
    oauth_token_secret = os.environ.get('ACCESS_SECRET', '')
    oauth_keys.append((oauth_consumer_key, oauth_consumer_secret, oauth_token, oauth_token_secret))

test_tweet_id = '266367358078169089'

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

class TweepyAPITests(unittest.TestCase):

    def setUp(self):
        auths = []
        for consumer_key, consumer_secret, access_key, access_secret in oauth_keys:
            auth = OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_key, access_secret)
            auths.append(auth)

        self.api = API(auths)
        self.api.retry_count = 2
        self.api.retry_delay = 5

    # TODO: Actually have some sort of better assertion
    def testgetoembed(self):
        data = self.api.get_oembed(test_tweet_id)
        self.assertEqual(data['author_name'], "Twitter")


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

    def testgetstatus(self):
        self.api.get_status(id=test_tweet_id)

    def testupdateanddestroystatus(self):
        # test update
        text = 'testing %i' % random.randint(0, 1000)
        update = self.api.update_status(status=text)
        self.assertEqual(update.text, text)

        # test destroy
        deleted = self.api.destroy_status(id=update.id)
        self.assertEqual(deleted.id, update.id)

    def testgetuser(self):
        u = self.api.get_user('twitter')
        self.assertEqual(u.screen_name, 'twitter')

        u = self.api.get_user(783214)
        self.assertEqual(u.screen_name, 'twitter')

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
        source, target = self.api.show_friendship(target_screen_name='twtiter')
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

    def testupdateprofile(self):
        original = self.api.me()
        profile = {
            'name': 'Tweepy test 123',
            'url': 'http://www.example.com',
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

    def testcreateupdatedestroylist(self):
        params = {
            'owner_screen_name': username,
            'slug': 'tweeps'
        }
        l = self.api.create_list(name=params['slug'], **params)
        l = self.api.update_list(list_id=l.id, description='updated!')
        self.assertEqual(l.description, 'updated!')
        self.api.destroy_list(list_id=l.id)

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
        assert_list(self.api.remove_list_member(**params))

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
        self.assertTrue(self.api.show_list_subscriber('applepie', 'stars', username))

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

@unittest.skipIf(not 'testratelimit' in sys.argv, "skipping rate limiting test since testratelimit is not specified")
class TweepyRateLimitTests(unittest.TestCase):

    def setUp(self):
        auths = []
        for consumer_key, consumer_secret, access_key, access_secret in oauth_keys:
            auth = OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_key, access_secret)
            auths.append(auth)

        self.api = API(auths)
        self.api.retry_count = 2
        self.api.retry_delay = 5
        self.api.retry_errors = set([401, 404, 503])
        self.api.monitor_rate_limit = True
        self.api.wait_on_rate_limit = True
                
    def testratelimit(self):
        # len(test_userids) = 180 * 2 + 10
        # should cause the api to sleep 
        test_user_ids = [123796151, 263168076, 990027860, 901955678, 214630268, 18305040, 36126818, 312483939, 426975332, 469837158, 1104126054, 1342066705, 281632872, 608977002, 242901099, 846643308, 1166401645, 153886833, 95314037, 314458230, 149856382, 287916159, 472506496, 267180736, 251764866, 351035524, 997113991, 445915272, 57335947, 251043981, 95051918, 200761489, 48341139, 972660884, 422330517, 326429297, 864927896, 94183577, 95887514, 220807325, 194330782, 58796741, 1039212709, 1017192614, 625828008, 66539548, 320566383, 309829806, 571383983, 382694863, 439140530, 93977882, 277651636, 19984414, 502004733, 1093673143, 60014776, 469849460, 937107642, 155516395, 1272979644, 617433802, 102212981, 301228831, 805784562, 427799926, 322298054, 162197537, 554001783, 89252046, 536789199, 177807568, 805044434, 495541739, 392904916, 154656981, 291266775, 865454102, 475846642, 56910044, 55834550, 177389790, 339841061, 319614526, 954529597, 595960038, 501301480, 15679722, 938090731, 495829228, 325034224, 1041031410, 18882803, 161080540, 456245496, 636854521, 811974907, 222085372, 222306563, 422846724, 281616645, 223641862, 705786134, 1038901512, 174211339, 426795277, 370259272, 34759594, 366410456, 320577812, 757211413, 483238166, 222624369, 29425605, 456455726, 408723740, 1274608346, 295837985, 273490210, 232497444, 726843685, 465232166, 18850087, 22503721, 259629354, 414250375, 1259941938, 777167150, 1080552157, 1271036282, 1000551816, 109443357, 345781858, 45113654, 406536508, 253801866, 98836799, 395469120, 252920129, 604660035, 69124420, 283459909, 482261729, 377767308, 565240139, 191788429, 102048080, 330054371, 527868245, 177044049, 1250978114, 424042840, 15810905, 389030234, 69324415, 15638877, 159080798, 378708319, 549183840, 1034658145, 629924195, 969130340, 1143593845, 188129639, 535863656, 552452458, 1325277547, 756236624, 48421608, 178495858, 566206836, 378519925, 22678249, 377659768, 102326650, 76783997, 440716178, 49062271, 26296705, 1328036587, 289644932, 305767830, 437305735, 124821901, 591735533, 155140501, 1099612568, 631398810, 469295515, 131350941, 325804447, 529801632, 977197808, 232613818, 614777251, 229261732, 255533478, 256942503, 169583016, 237860252, 29257799, 276668845, 871571886, 398162507, 451954078, 526016951, 285655480, 1281827257, 340042172, 146653629, 61055423, 33407417, 95582321, 237420995, 310960580, 1222064886, 16490950, 60924360, 81928649, 374424010, 45703629, 817455571, 336077264, 400268024, 1203200467, 457105876, 232309205, 45838026, 91972056, 226927065, 82125276, 760131962, 1032274398, 562552291, 155155166, 146464315, 864864355, 128655844, 589747622, 293290470, 192004584, 19100402, 133931498, 19775979, 446374381, 1175241198, 20128240, 332395944, 74575955, 247407092, 427794934, 329823657, 405742072, 497475320, 997384698, 147718652, 757768705, 96757163, 289874437, 29892071, 568541704, 297039276, 356590090, 502055438, 291826323, 238944785, 71483924, 50031538, 863355416, 120273668, 224403994, 14880858, 1241506364, 848962080, 57898416, 599695908, 1222132262, 54045447, 907207212, 851412402, 454418991, 231844616, 618447410, 602997300, 447685173, 19681556, 22233657, 509901138, 184705596, 307624714, 553017923, 1249878596, 33727045, 419873350, 789307489, 287531592, 399163977, 1069425228, 920789582, 136891149, 134857296, 358558478, 436855382, 963011161, 195764827, 548872797, 1058980446, 442376799, 578216544, 527147110, 122077799, 1004773993, 420332138, 514994279, 61530732, 133462802, 19513966, 1286972018, 786121332, 265863798, 221258362, 42656382, 43631231, 198264256, 944382595, 37387030, 260948614, 314406408, 296512982, 92830743, 24519306, 21070476, 454107789, 331006606, 939713168, 256197265, 30065299, 74774188, 1332842606, 289424023, 526992024, 429933209, 116384410, 762143389, 308093598, 421208736, 454943394, 66026267, 158851748, 257550092, 70697073, 903627432, 290669225, 121168557, 92994330, 67642033, 635183794, 499303091, 421205146, 1252648171, 375268025, 16281866, 211960508, 267179466, 129016511, 157172416, 373370004, 167781059, 43624522]
        for user_id in test_user_ids:
            try:
                self.api.user_timeline(user_id=user_id, count=1, include_rts=True)
            except TweepError, e:
                # continue if we're not autherized to access the user's timeline or she doesn't exist anymore
                if e.response is not None and e.response.status in set([401, 404]): 
                    continue
                raise e

class TweepyCursorTests(unittest.TestCase):

    def setUp(self):
        auth = OAuthHandler(oauth_consumer_key, oauth_consumer_secret)
        auth.set_access_token(oauth_token, oauth_token_secret)
        self.api = API(auth)
        self.api.retry_count = 2
        self.api.retry_delay = 5

    def testpagecursoritems(self):
        items = list(Cursor(self.api.user_timeline).items())
        self.assert_(len(items) > 0)

        items = list(Cursor(self.api.user_timeline, 'twitter').items(30))
        self.assert_(len(items) == 30)

    def testpagecursorpages(self):
        pages = list(Cursor(self.api.user_timeline).pages())
        self.assert_(len(pages) > 0)

        pages = list(Cursor(self.api.user_timeline, 'twitter').pages(5))
        self.assert_(len(pages) == 5)

    def testsearchcursorpages(self):
        pages = list(Cursor(self.api.search, q='the', rpp=100).pages(20))
        self.assert_(len(pages) == 20, "Search did not return the expected number of pages")
        
        tweet_ids = []
        for page in pages:
            tweet_ids.extend([t.id for t in page])
        self.assert_(len(tweet_ids)==len(frozenset(tweet_ids)), "Search returned pages containing %d duplicates" % (len(tweet_ids)-len(frozenset(tweet_ids))))    
            
        items = list(Cursor(self.api.search, q='the', rpp=100).items(2000))
        self.assert_(len(items) == 2000, "Search did not return the expected number of items")
        item_ids = [t.id for t in items]
        self.assert_(len(items)==len(frozenset(item_ids)), "Search returned items containing duplicates")
        
        
    def testcursorcursoritems(self):
        items = list(Cursor(self.api.friends_ids).items())
        self.assert_(len(items) > 0)

        items = list(Cursor(self.api.followers_ids, 'twitter').items(30))
        self.assert_(len(items) == 30)

    def testcursorcursorpages(self):
        pages = list(Cursor(self.api.friends_ids).pages())
        self.assert_(len(pages) > 0)

        pages = list(Cursor(self.api.followers_ids, 'twitter').pages(5))
        self.assert_(len(pages) == 5)

class TweepyAuthTests(unittest.TestCase):

    def testoauth(self):
        auth = OAuthHandler(oauth_consumer_key, oauth_consumer_secret)

        # test getting access token
        auth_url = auth.get_authorization_url()
        print 'Please authorize: ' + auth_url
        verifier = raw_input('PIN: ').strip()
        self.assert_(len(verifier) > 0)
        access_token = auth.get_access_token(verifier)
        self.assert_(access_token is not None)

        # build api object test using oauth
        api = API(auth)
        s = api.update_status('test %i' % random.randint(0, 1000))
        api.destroy_status(s.id)


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
    if 'testratelimit' in sys.argv:
        unittest.TextTestRunner().run(unittest.loader.makeSuite(TweepyRateLimitTests))
    else:
        unittest.main()
