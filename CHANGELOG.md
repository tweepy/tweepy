Also see https://github.com/tweepy/tweepy/releases for changelogs.

Version 3.8.0
-------------
### New Features / Improvements
- Allow streams to use daemon threads ([#1126](https://github.com/tweepy/tweepy/pull/1126))
- Remove `API.set_delivery_device` ([#1203](https://github.com/tweepy/tweepy/issues/1203))
- Remove simplejson import and usage ([#832](https://github.com/tweepy/tweepy/pull/832))
- Allow `cursor` parameter for `API.blocks_ids` and `API.mutes_ids` ([#1208](https://github.com/tweepy/tweepy/pull/1208))
- Drop support for Python 3.4
- Allow `perform_block` parameter for `API.report_spam` ([#1090](https://github.com/tweepy/tweepy/pull/1090))
- Add `API.mutes` ([#1197](https://github.com/tweepy/tweepy/issues/1197), [#1215](https://github.com/tweepy/tweepy/pull/1215))
- Allow `count` parameter for `API.friends` ([#577](https://github.com/tweepy/tweepy/issues/577))
- Remove `since`, `from`, `to`, and `source` as allowed parameters for `API.search`
- Handle location deletion and withheld content notices for streams ([#886](https://github.com/tweepy/tweepy/pull/886))
- Allow usage of equality and difference operators with `User` objects ([#939](https://github.com/tweepy/tweepy/pull/939))
- Add `_json` attribute to `Category`, `Friendship`, and `List` models ([#590](https://github.com/tweepy/tweepy/issues/590), [#1169](https://github.com/tweepy/tweepy/pull/1169))
- Remove `API.suggested_categories`, `API.suggested_users`, and `API.suggested_users_tweets`
- Update and improve tests and cassettes ([#1242](https://github.com/tweepy/tweepy/pull/1242))
- Update `DirectMessage` model ([#1081](https://github.com/tweepy/tweepy/issues/1081), [#1228](https://github.com/tweepy/tweepy/pull/1228))
- Replace `API.direct_messages` and `API.sent_direct_messages` with `API.list_direct_messages` ([#1081](https://github.com/tweepy/tweepy/issues/1081), [#1228](https://github.com/tweepy/tweepy/pull/1228))
- Update `API.get_direct_message`, `API.send_direct_message`, and `API.destroy_direct_message` ([#1081](https://github.com/tweepy/tweepy/issues/1081), [#1228](https://github.com/tweepy/tweepy/pull/1228))
- Update and improve various documentation

### Bug Fixes
- Exclude examples during installation ([#1141](https://github.com/tweepy/tweepy/issues/1141), [#1164](https://github.com/tweepy/tweepy/pull/1164))
- Properly initialize `OAuthHandler.request_token` ([#1149](https://github.com/tweepy/tweepy/pull/1149))
- Properly handle `map_` parameter for `API.statuses_lookup` ([#598](https://github.com/tweepy/tweepy/issues/598))
- Support cursor pagination for `API.blocks_ids` and `API.mutes_ids` ([#930](https://github.com/tweepy/tweepy/issues/930), [#931](https://github.com/tweepy/tweepy/pull/931))
- Return values for `API.update_profile_background_image` and `API.update_profile_banner` ([#904](https://github.com/tweepy/tweepy/pull/904))
- Replace usage of root logger
- Close Requests sessions ([#810](https://github.com/tweepy/tweepy/issues/810), [#1093](https://github.com/tweepy/tweepy/issues/1093), [#1237](https://github.com/tweepy/tweepy/issues/1237))

Version 3.7.0
-------------
### New Features / Improvements
- Allow `trim_user` and `exclude_replies` as parameters for `API.user_timeline` ([#909](https://github.com/tweepy/tweepy/pull/909))
- Allow `tweet_mode` parameter for `API.statuses_lookup` ([#840](https://github.com/tweepy/tweepy/issues/840), [#926](https://github.com/tweepy/tweepy/pull/926))
- Drop support for Python 2.6 and 3.3
- [Discord Server](https://discord.gg/bJvqnhg)
- Add proxy support for streams ([#1033](https://github.com/tweepy/tweepy/pull/1033))
- Add `API.create_mute`, `API.destroy_mute`, and `API.mutes_ids` ([#1055](https://github.com/tweepy/tweepy/pull/1055))
- Allow `tweet_mode` parameter for `API.lookup_users` ([#1130](https://github.com/tweepy/tweepy/pull/1130))

### Bug Fixes
- Fix `AttributeError` during streaming ([#1026](https://github.com/tweepy/tweepy/issues/1026), [#1027](https://github.com/tweepy/tweepy/pull/1027))
- Update how requirements are specified ([#1029](https://github.com/tweepy/tweepy/issues/1029), [#1030](https://github.com/tweepy/tweepy/pull/1030))
- Fix compatibility issue with Python 3.7 ([#1017](https://github.com/tweepy/tweepy/issues/1017), [#1042](https://github.com/tweepy/tweepy/pull/1042))

Version 3.6.0
-------------
### New Features / Improvements
- Parse `Status.quoted_status` as a `Status` object ([#633](https://github.com/tweepy/tweepy/pull/633))
- Allow `in_reply_to_status_id_str` as a parameter for `API.update_status` and `API.update_with_media` ([#693](https://github.com/tweepy/tweepy/pull/693))
- Add `stall_warnings` parameter to `Stream.sample` ([#701](https://github.com/tweepy/tweepy/pull/701))
- Add `API.unretweet` ([#735](https://github.com/tweepy/tweepy/issues/735), [#736](https://github.com/tweepy/tweepy/pull/736))
- Allow `auto_populate_reply_metadata` as a parameter for `API.update_status` and `API.update_with_media` ([#761](https://github.com/tweepy/tweepy/pull/761))
- Allow `profile_link_color` as a parameter for `API.update_profile`
- Add support for Python 3.6 ([#831](https://github.com/tweepy/tweepy/pull/831), [#884](https://github.com/tweepy/tweepy/pull/884))

### Bug Fixes
- Update file size limit for `API.media_upload` ([#717](https://github.com/tweepy/tweepy/pull/717))
- Fix `JSONParser.parse` returning `None` in certain cases ([#765](https://github.com/tweepy/tweepy/issues/765), [#766](https://github.com/tweepy/tweepy/pull/766))
- Include URL parameters when accessing cache ([#777](https://github.com/tweepy/tweepy/pull/777))
- Properly re-raise exceptions during streaming
- Fix `AttributeError` and `TypeError` during streaming ([#698](https://github.com/tweepy/tweepy/issues/698))
- Properly encode `filter_level` for `Stream.filter` ([#782](https://github.com/tweepy/tweepy/issues/782))

Version 3.5.0
-------------
### Features / Improvements
- Allow 'full_text' param when getting direct messages ( #664 )
- Explicitly return api code when parsing error ( #666 )
- Remove deprecated function and clean up codes ( #583 )

### Bug Fixes
- update_status: first positional argument should be 'status' ( #578 )
- Fix "TypeError: Can't convert 'bytes' object to str implicitly" ( #615 #658 #635 )
- Fix duplicate raise in auth.py ( #667 )

Version 3.4.0
-------------
### New Features
- Add API for account/settings (PR #596)
- Added RateLimitError for easily working with the rate limit. (Issue #600, PR #611) @obskyr 
- Allow include_email param for verify_credentials API (PR #623)
- Added support for the "filter_level" parameter for the streaming API (PR #619)

### Bug Fixes
- Streaming: don't decode stream bytes until json.decode (PR #606)
- Typo fix on _add_list_members, _remove_list_members properties. (PR #593)
- Fixes issue #570 - add "exception" when raising one
- Change raise in streaming.py to raise exception (PR #621)

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
