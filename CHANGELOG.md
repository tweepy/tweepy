Version 2.1
-----------
  - Added get_oembed().
  - friends() and followers() are back and updated to v1.1.
  - Fixed report_spam() endpoint.
  - Added "languages" parameter to streaming filter() method.
  - Added "timeout" support for API object. Ex: API(timeout=1000).
  - Python 2.5 no longer supported.
  - Added compression support. Ex: API(compression=True).
  - Added on_connect() callback to StreamListener.
  - Switched API search() to v1.1 endpoint. Some breaking changes.
  - Drop "page" based cursors and use "ID" based ones instead.
  - [Compare
    2.0...master](https://github.com/tweepy/tweepy/compare/2.0...master)

Version 2.0
-----------
  _Dedicated in memory of Aaron Swartz_

  - Twitter API 1.1 support.
  - Basic Authentication deprecated.
  - friends_timeline() removed.
  - mentions() removed and replaced by mentions_timeline().
  - retweeted_by_user() removed.
  - retweeted_by_me() removed.
  - retweeted_to_me() removed.
  - retweeted_by_user() removed.
  - friends() removed.
  - followers() removed.
  - enable_notifications() removed.
  - disable_notifications() removed.
  - exists_block() removed.
  - lists() removed and replaced by lists_all().
  - is_list_member() removed.
  - show_list_member added.
  - is_subscribed_list() removed.
  - show_list_subscriber() added.
  - trends_location() removed.
  - nearby_places() removed.
