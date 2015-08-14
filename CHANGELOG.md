See https://github.com/tweepy/tweepy/releases for change logs.

Version 3.3.0
-------------
  - Loosen our dependency requirements for Requests (>= 2.4.3)
  - Fix issue with streams freezing up on Python 3 (Issue #556)
  - Add keep_alive() callback to StreamListener when keep alive messages arrive
  - Fix issue with stream session headers not being used when restarting connection
  - Fix issue with streams getting stuck in a loop when connection dies. (PR #561)

Version 3.2.0
-------------
  - Remove deprecated trends methods.
  - Fix tweepy.debug() to work in Python 3.
  - Fixed issue #529 - StreamListener language filter stopped working.
  - Add Documentation Page for streaming.
  - Add media/upload endpoint.
  - Add media_ids parameter to update_status().

Version 3.1.0
-------------
  - Allow specifying your own ssl certificates for streaming client.
  - Distribute Python Wheels instead of dumb binaries.
  - Fix cursor invocation, passing args to underlying method. (https://github.com/tweepy/tweepy/issues/515)
  - Upgrade to Request 2.4.3

Version 3.0
-----------
  - Added multiple list members operation api methods (add_list_members, remove_list_members).
  - Added sitestream endpoint.
  - Switch to using Requests instead of httplib.
  - Fully removed support for non-secure HTTP.
  - Proxy support.
  - Add API method for /statuses/lookup.json
  - Add missing 'count' parameter to followers_ids
  - Added allowed_param to update_profile_image
  - Comparison between Status objects
  - Extend on_data method by including a conditional to process warning messages and add the definition of the method to manage those warning messages
  - Better Python 3 support.

Version 2.2
-----------
  - Added update_profile_banner endpoint.
  - Don't treat HTTP status codes in 200 range as errors.
  - Tests no longer packaged into egg releases.
  - Improve test stability and enable CI testing on pull requests.
  - Removed Basic Auth.
  - Use built-in timeout feature of httplib to fix appengine.
  - Added retweeters() endpoint.
  - Removed deprecated retweeted_by and retweeted_by_ids.
  - Improved datetime parsing. Should be more thread safe.
  - Enable coverage reporting. Upload reports to Coveralls.
    - https://coveralls.io/r/tweepy/tweepy
  - Removed deprecated test() endpoint.
  - New stream listeners callback on_disconnect(). Called whenever
"disconnect" messages arrive from Twitter before connection is killed.
    - https://dev.twitter.com/docs/streaming-apis/messages#Disconnect_messages_disconnect
  - [Compare View](https://github.com/tweepy/tweepy/compare/2.1...2.2)
  - Use HTTPS by default.
  - Support setting the starting cursor postion (ex: Ex:
    Cursor(api.friends_ids, cursor=123456))
  - Added API.cached_result instance flag that is "True" when cached result is returned.
  - New Streaming client callbacks
    - on_event(status): called when new events arrive
    - on_direct_message(status): called when a new direct message
      arrives.
  - Improvements to streaming client re-connection behavior /
    configuration.
(https://github.com/tweepy/tweepy/commit/447f69cd3de67b0d241b9d4f669ecc9b9c0cdb54)

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
  - [Compare View](https://github.com/tweepy/tweepy/compare/2.0...2.1)

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
