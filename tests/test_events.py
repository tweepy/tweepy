from __future__ import absolute_import, print_function

import six
if six.PY3:
    import unittest
    from unittest.case import skip
else:
    import unittest2 as unittest
    from unittest2.case import skip

from tweepy import api
from tweepy.utils import import_simplejson
from tweepy.models import Status, Event, User

json = import_simplejson()


class TweepyEventTests(unittest.TestCase):
    def test_quoted_tweet(self):
        e = Event.parse(api, json.loads(quoted_tweet_event_json))
        self.assertIsInstance(e, Event)
        self.assertIsInstance(e.source, User)
        self.assertIsInstance(e.target, User)
        self.assertIsInstance(e.target_object, Status)


quoted_tweet_event_json = r'''
{
 "source": {
  "lang": "en", 
  "utc_offset": null, 
  "id_str": "1597840026", 
  "statuses_count": 29, 
  "follow_request_sent": null, 
  "friends_count": 1, 
  "profile_use_background_image": true, 
  "contributors_enabled": false, 
  "profile_link_color": "0084B4", 
  "profile_image_url": "http://pbs.twimg.com/profile_images/721798985808289792/j5S5NV_y_normal.jpg", 
  "default_profile_image": false, 
  "following": null, 
  "favourites_count": 0, 
  "geo_enabled": false, 
  "profile_background_color": "C0DEED", 
  "profile_banner_url": "https://pbs.twimg.com/profile_banners/1597840026/1460925298", 
  "profile_background_image_url_https": "https://abs.twimg.com/images/themes/theme1/bg.png", 
  "profile_background_image_url": "http://abs.twimg.com/images/themes/theme1/bg.png", 
  "description": "A possible new home for @resiak unless @wjjt can be reclaimed.", 
  "is_translation_enabled": false, 
  "profile_background_tile": false, 
  "profile_sidebar_border_color": "C0DEED", 
  "verified": false, 
  "screen_name": "wjjjjt", 
  "notifications": null, 
  "url": null, 
  "name": "Will Thompson", 
  "profile_image_url_https": "https://pbs.twimg.com/profile_images/721798985808289792/j5S5NV_y_normal.jpg", 
  "profile_sidebar_fill_color": "DDEEF6", 
  "time_zone": null, 
  "id": 1597840026, 
  "profile_text_color": "333333", 
  "followers_count": 1, 
  "protected": false, 
  "location": null, 
  "default_profile": true, 
  "is_translator": false, 
  "created_at": "Tue Jul 16 08:19:17 +0000 2013", 
  "listed_count": 0
 }, 
 "created_at": "Mon Apr 18 08:56:32 +0000 2016", 
 "event": "quoted_tweet", 
 "target_object": {
  "contributors": null, 
  "quoted_status_id": 690153391398457345, 
  "text": "quotey mcquoteface https://t.co/iuoPa9MmKM", 
  "is_quote_status": true, 
  "in_reply_to_status_id": null, 
  "id": 721985754826715136, 
  "favorite_count": 0, 
  "entities": {
   "symbols": [], 
   "user_mentions": [], 
   "hashtags": [], 
   "urls": [
    {
     "url": "https://t.co/iuoPa9MmKM", 
     "indices": [
      19, 
      42
     ], 
     "expanded_url": "https://twitter.com/fewerror/status/690153391398457345", 
     "display_url": "twitter.com/fewerror/statu\u2026"
    }
   ]
  }, 
  "truncated": false, 
  "retweeted": false, 
  "coordinates": null, 
  "quoted_status": {
   "contributors": null, 
   "truncated": false, 
   "text": "@resiak I think you mean \u201cfewer sorrow-inducing\u201d.", 
   "is_quote_status": false, 
   "in_reply_to_status_id": 690153385421574145, 
   "id": 690153391398457345, 
   "favorite_count": 0, 
   "entities": {
    "symbols": [], 
    "user_mentions": [
     {
      "indices": [
       0, 
       7
      ], 
      "id": 786920, 
      "screen_name": "resiak", 
      "name": "will thompson", 
      "id_str": "786920"
     }
    ], 
    "hashtags": [], 
    "urls": []
   }, 
   "retweeted": false, 
   "coordinates": null, 
   "source": "<a href=\"https://github.com/wjt/fewerror\" rel=\"nofollow\">Fewerror</a>", 
   "in_reply_to_screen_name": "resiak", 
   "id_str": "690153391398457345", 
   "retweet_count": 0, 
   "in_reply_to_user_id": 786920, 
   "favorited": false, 
   "user": {
    "lang": "en", 
    "utc_offset": null, 
    "id_str": "1932168457", 
    "statuses_count": 2190, 
    "follow_request_sent": null, 
    "friends_count": 670, 
    "profile_use_background_image": true, 
    "contributors_enabled": false, 
    "profile_link_color": "E65825", 
    "profile_image_url": "http://pbs.twimg.com/profile_images/684672957327761408/QzOFGpB7_normal.jpg", 
    "default_profile_image": false, 
    "following": null, 
    "favourites_count": 27, 
    "geo_enabled": false, 
    "profile_background_color": "C0DEED", 
    "profile_banner_url": "https://pbs.twimg.com/profile_banners/1932168457/1408642383", 
    "profile_background_image_url_https": "https://abs.twimg.com/images/themes/theme1/bg.png", 
    "profile_background_image_url": "http://abs.twimg.com/images/themes/theme1/bg.png", 
    "description": "Follow me, and I'll let you know when you use \u201cless\u201d when you mean \u201cfewer\u201d. I'm pretty sure I always get it right. Unfollow to stop getting corrections.", 
    "is_translation_enabled": false, 
    "profile_background_tile": false, 
    "profile_sidebar_border_color": "C0DEED", 
    "verified": false, 
    "screen_name": "fewerror", 
    "notifications": null, 
    "url": "https://github.com/wjt/fewerror", 
    "name": "Fewer Errors", 
    "profile_image_url_https": "https://pbs.twimg.com/profile_images/684672957327761408/QzOFGpB7_normal.jpg", 
    "profile_sidebar_fill_color": "DDEEF6", 
    "time_zone": null, 
    "id": 1932168457, 
    "profile_text_color": "333333", 
    "followers_count": 529, 
    "protected": false, 
    "location": "@resiak's private cloud", 
    "default_profile": false, 
    "is_translator": false, 
    "created_at": "Thu Oct 03 21:38:29 +0000 2013", 
    "listed_count": 10
   }, 
   "geo": null, 
   "in_reply_to_user_id_str": "786920", 
   "lang": "en", 
   "created_at": "Thu Jan 21 12:46:05 +0000 2016", 
   "in_reply_to_status_id_str": "690153385421574145", 
   "place": null
  }, 
  "source": "<a href=\"https://about.twitter.com/products/tweetdeck\" rel=\"nofollow\">TweetDeck</a>", 
  "in_reply_to_screen_name": null, 
  "in_reply_to_user_id": null, 
  "retweet_count": 0, 
  "id_str": "721985754826715136", 
  "favorited": false, 
  "user": {
   "lang": "en", 
   "utc_offset": null, 
   "id_str": "1597840026", 
   "statuses_count": 29, 
   "follow_request_sent": null, 
   "friends_count": 1, 
   "profile_use_background_image": true, 
   "contributors_enabled": false, 
   "profile_link_color": "0084B4", 
   "profile_image_url": "http://pbs.twimg.com/profile_images/721798985808289792/j5S5NV_y_normal.jpg", 
   "default_profile_image": false, 
   "following": null, 
   "favourites_count": 0, 
   "geo_enabled": false, 
   "profile_background_color": "C0DEED", 
   "profile_banner_url": "https://pbs.twimg.com/profile_banners/1597840026/1460925298", 
   "profile_background_image_url_https": "https://abs.twimg.com/images/themes/theme1/bg.png", 
   "profile_background_image_url": "http://abs.twimg.com/images/themes/theme1/bg.png", 
   "description": "A possible new home for @resiak unless @wjjt can be reclaimed.", 
   "is_translation_enabled": false, 
   "profile_background_tile": false, 
   "profile_sidebar_border_color": "C0DEED", 
   "verified": false, 
   "screen_name": "wjjjjt", 
   "notifications": null, 
   "url": null, 
   "name": "Will Thompson", 
   "profile_image_url_https": "https://pbs.twimg.com/profile_images/721798985808289792/j5S5NV_y_normal.jpg", 
   "profile_sidebar_fill_color": "DDEEF6", 
   "time_zone": null, 
   "id": 1597840026, 
   "profile_text_color": "333333", 
   "followers_count": 1, 
   "protected": false, 
   "location": null, 
   "default_profile": true, 
   "is_translator": false, 
   "created_at": "Tue Jul 16 08:19:17 +0000 2013", 
   "listed_count": 0
  }, 
  "geo": null, 
  "in_reply_to_user_id_str": null, 
  "possibly_sensitive": false, 
  "lang": "en", 
  "created_at": "Mon Apr 18 08:56:32 +0000 2016", 
  "quoted_status_id_str": "690153391398457345", 
  "in_reply_to_status_id_str": null, 
  "place": null
 }, 
 "target": {
  "lang": "en", 
  "utc_offset": null, 
  "id_str": "1932168457", 
  "statuses_count": 2190, 
  "follow_request_sent": null, 
  "friends_count": 670, 
  "profile_use_background_image": true, 
  "contributors_enabled": false, 
  "profile_link_color": "E65825", 
  "profile_image_url": "http://pbs.twimg.com/profile_images/684672957327761408/QzOFGpB7_normal.jpg", 
  "default_profile_image": false, 
  "following": null, 
  "favourites_count": 27, 
  "geo_enabled": false, 
  "profile_background_color": "C0DEED", 
  "profile_banner_url": "https://pbs.twimg.com/profile_banners/1932168457/1408642383", 
  "profile_background_image_url_https": "https://abs.twimg.com/images/themes/theme1/bg.png", 
  "profile_background_image_url": "http://abs.twimg.com/images/themes/theme1/bg.png", 
  "description": "Follow me, and I'll let you know when you use \u201cless\u201d when you mean \u201cfewer\u201d. I'm pretty sure I always get it right. Unfollow to stop getting corrections.", 
  "is_translation_enabled": false, 
  "profile_background_tile": false, 
  "profile_sidebar_border_color": "C0DEED", 
  "verified": false, 
  "screen_name": "fewerror", 
  "notifications": null, 
  "url": "https://github.com/wjt/fewerror", 
  "name": "Fewer Errors", 
  "profile_image_url_https": "https://pbs.twimg.com/profile_images/684672957327761408/QzOFGpB7_normal.jpg", 
  "profile_sidebar_fill_color": "DDEEF6", 
  "time_zone": null, 
  "id": 1932168457, 
  "profile_text_color": "333333", 
  "followers_count": 529, 
  "protected": false, 
  "location": "@resiak's private cloud", 
  "default_profile": false, 
  "is_translator": false, 
  "created_at": "Thu Oct 03 21:38:29 +0000 2013", 
  "listed_count": 10
 }
}
'''
