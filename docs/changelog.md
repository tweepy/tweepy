Changelog
=========

These changelogs are also at <https://github.com/tweepy/tweepy/releases> as release notes.

Version 4.14.0 (2023-04-24)
---------------------------

### New Features / Improvements
- Add constants for potential model object fields ([f3f73bc](https://github.com/tweepy/tweepy/commit/f3f73bc1cf0a7f19ebfe7df0a2f6b08fb7c4cd9c))
  - `DIRECT_MESSAGE_EVENT_FIELDS`
  - `DM_EVENT_FIELDS`
  - `LIST_FIELDS`
  - `MEDIA_FIELDS`
  - `PLACE_FIELDS`
  - `POLL_FIELDS`
  - `PUBLIC_SPACE_FIELDS`
  - `SPACE_FIELDS`
  - `PUBLIC_TWEET_FIELDS`
  - `TWEET_FIELDS`
  - `USER_FIELDS`
- Add `creator_id` field for `Space` ([a13726a](https://github.com/tweepy/tweepy/commit/a13726a1c0114f72e0037bad4292b4a2a6693b65))

### Twitter API Backwards-Incompatible Changes
- Remove support for streaming with Twitter API v1.1 status/filter endpoint ([c8a02eb](https://github.com/tweepy/tweepy/commit/c8a02eb61b36ac710010b67ff0ed7b8374ef9375))
  - `Stream`
  - `AsyncStream`
- Remove support for deprecated Premium v1.1 Search APIs ([a955f30](https://github.com/tweepy/tweepy/commit/a955f3000c57c134f51d55b42c0e98ff56e17311))
  - `API.search_30_day`
  - `API.search_full_archive`

### Misc
- Overhaul Getting Started documentation ([addb9f7](https://github.com/tweepy/tweepy/commit/addb9f7a78de70c1b1e4b6a34e5324776f55cd0f))
- Remove no longer valid Twitter API version badges in README ([880e7bf](https://github.com/tweepy/tweepy/commit/880e7bf98075a1e1c1cd817971581d4f229ea1fb))
- Update and improve various documentation

Version 4.13.0 (2023-03-09)
---------------------------

### New Features / Improvements
- Add `verified_type` field for `User` ([9f7afae](https://github.com/tweepy/tweepy/commit/9f7afaefa680da6a4f7864db99e12dd72a51cafa))

### Twitter API Backwards-Incompatible Changes
- Remove streaming methods using retired Twitter API v1.1 features ([0cd96b1](https://github.com/tweepy/tweepy/commit/0cd96b1918e5e920eb9f8fe4ba303ab5ec899c65))
  - Twitter API v1.1 statuses/sample endpoint
    - `Stream.sample`
    - `AsyncStream.sample`
  - Compliance messages on the Twitter API v1.1 statuses/filter endpoint
    - `Stream.on_delete`, `Stream.on_scrub_geo`, `Stream.on_status_withheld`, `Stream.on_user_withheld`
    - `AsyncStream.on_delete`, `AsyncStream.on_scrub_geo`, `AsyncStream.on_status_withheld`, `AsyncStream.on_user_withheld`

### Twitter API Deprecations
- Deprecate streaming with Twitter API v1.1 statuses/filter endpoint ([8b9c547](https://github.com/tweepy/tweepy/commit/8b9c547b7e443344ba78ee435ec60a407d92f902))
  - `Stream`
  - `AsyncStream`

### Bug Fixes
- Return base class method values in `StreamingClient._process_data` and `AsyncStreamingClient._process_data` methods ([2744073](https://github.com/tweepy/tweepy/commit/274407346aa2db1b751f5e5fe11ab0d8bbe9314c))
- Handle empty payloads in `JSONParser.parse` ([e854138](https://github.com/tweepy/tweepy/commit/e854138dcecc223fac1038704ec0d9266037217b), [#2051](https://github.com/tweepy/tweepy/issues/2051))

#### Twitter API Bug Handling
- Handle incorrect processing state for errored chunked uploads ([a68ce86](https://github.com/tweepy/tweepy/commit/a68ce8658ab0908227dc486e73d02060e21174f8))

### Misc
- Support async-lru v2 ([f98b345](https://github.com/tweepy/tweepy/commit/f98b34573a50fdc870111e17052d385b0917e3c3))
- Document specific expansions available for each type of payload ([7df6453](https://github.com/tweepy/tweepy/commit/7df645328bdf26e5c4c569392d5d2252b1527477))
- Add documentation for Direct Message events ([c689548](https://github.com/tweepy/tweepy/commit/c689548cb1b4b9c2f69249d67534a735b931b9b5))
- Update documentation for `dm_event_fields` parameter ([e2fb467](https://github.com/tweepy/tweepy/commit/e2fb467b52659e87de592ff80b03edb9324c0189))
- Add section in documentation about `dm_event_fields` parameter ([4b0fa90](https://github.com/tweepy/tweepy/commit/4b0fa90e91eb2b67dfd33f0d27b148e95ea05f65))
- Add expansions documentation for Direct Message conversation events ([#2009](https://github.com/tweepy/tweepy/pull/2009))
- Add note in documentation about removal of `Tweet` `source` field ([5d22a01](https://github.com/tweepy/tweepy/commit/5d22a01a2f48feaed6817e0ab7c27a990735a3d8))
- Add SECURITY.md ([b79a1db](https://github.com/tweepy/tweepy/commit/b79a1db0962d7091de17f6ad93f42699d68e76f6), [3d3d58e](https://github.com/tweepy/tweepy/commit/3d3d58e1e8627788fe88684a515ef888038f3e3c))
- Update copyright years to include 2023 ([ccc9526](https://github.com/tweepy/tweepy/commit/ccc95269c1071f6c1f65698bf73c851472defba9))

Version 4.12.1 (2022-11-06)
---------------------------

### Bug Fixes
- Add 1 second buffer to API v2 streaming timeout ([51a5d61](https://github.com/tweepy/tweepy/commit/51a5d61bfd6699ab844449698b34befd6a170857))
  - The keep-alive is often received after marginally longer than 20 seconds, causing unnecessary timeouts and reconnects with a timeout of exactly 20 seconds
- Default `AsyncBaseStream` to abort closed SSL transports ([#1904](https://github.com/tweepy/tweepy/issues/1904))
- Warn when Tweet data is missing default `edit_history_tweet_ids` field ([3dea0df](https://github.com/tweepy/tweepy/commit/3dea0df2b8ee797264de67afc9f2d670e68aa634), [#1994](https://github.com/tweepy/tweepy/issues/1994))
- Change initial `network_error_wait` to 0 for streaming ([b18c1a6](https://github.com/tweepy/tweepy/commit/b18c1a6239e81cb5744fa99d392ec539de787e5c))
  - Attempt to reconnect immediately when established streaming connection drops

### Misc
- Document `limit` and `pagination_token` parameters for `Paginator` and `AsyncPaginator` ([e98ab02](https://github.com/tweepy/tweepy/commit/e98ab0211e488c734d1c01c0bf2a2cf4d87c4762), [bb934fc](https://github.com/tweepy/tweepy/commit/bb934fc247892d83ce69511311c07bed2b170412))
- Use separate method to construct `Response` in `Client` and `AsyncClient` ([#1997](https://github.com/tweepy/tweepy/pull/1997), [9983735](https://github.com/tweepy/tweepy/commit/9983735313c10906479348621f835bbbc38e5619))
- Log streaming connection error exceptions ([b7f02c6](https://github.com/tweepy/tweepy/commit/b7f02c60b252b747e16d84ccfedb275d85720439))
- Add CITATION.cff ([2547b44](https://github.com/tweepy/tweepy/commit/2547b44ac8ea1250b5eb6747db5bce7e425bc5ba))
- Add DOI badge to README ([72a33c9](https://github.com/tweepy/tweepy/commit/72a33c9df96cd5f537999d9a4f2a1ad2d82d8f60))
- Replace docs/requirements.txt with docs extra ([0ccfe86](https://github.com/tweepy/tweepy/commit/0ccfe86175d83ea89b20ff00ef6f420423fde347))
- Fix Intersphinx link to `namedtuple` in documentation for `Response` ([352c74a](https://github.com/tweepy/tweepy/commit/352c74ac1e1eb3a87a70bc707f35256d20001494))
- Improve format of badges in README ([d41c813](https://github.com/tweepy/tweepy/commit/d41c8135f2876cb91299bb70fb4b95d06039ce05))

Version 4.12.0 (2022-10-27)
---------------------------

### New Features / Improvements
- Add support for Direct Messages with Twitter API v2 ([#1995](https://github.com/tweepy/tweepy/issues/1995))
  - Add `DirectMessageEvent` model
  - Add `Client.get_direct_message_events`, `Client.create_direct_message`, and `Client.create_direct_message_conversation`
  - Add `AsyncClient.get_direct_message_events`, `AsyncClient.create_direct_message`, and `AsyncClient.create_direct_message_conversation`
- Add support for Python 3.11 ([a391c66](https://github.com/tweepy/tweepy/commit/a391c66daae3f217585b5da9a9556cb86abe34bd))
- Add support for `variants` `Media` field ([#1910](https://github.com/tweepy/tweepy/pull/1910), [e31be15](https://github.com/tweepy/tweepy/commit/e31be1519269d5225e28dad8a77b58412b7fe435))

### Bug Fixes
- Handle different method return types in API v2 pagination ([#1843](https://github.com/tweepy/tweepy/issues/1843), [#1861](https://github.com/tweepy/tweepy/pull/1861), [381bf91](https://github.com/tweepy/tweepy/commit/381bf9182700fa0c51df00b5b0f3e19c3d04dac0), [3874579](https://github.com/tweepy/tweepy/commit/3874579bac22a6648e774995478cb597689d89bc))
- Add missing angle bracket to string representation of `ReferencedTweet` ([d4df069](https://github.com/tweepy/tweepy/commit/d4df0691b4686161cc4bda0c85f29b75f207e0c2))

### Misc
- Add documentation for `edit_history_tweet_ids` and `edit_controls` `Tweet` fields ([2b1e159](https://github.com/tweepy/tweepy/commit/2b1e159f4525df74e7cf9f2c531392966f306a82))
  - This documentation was previously missing from Twitter's API documentation
- Fix class references in notes in documentation for `AsyncClient` methods ([f737b87](https://github.com/tweepy/tweepy/commit/f737b87fbcf15fda070898189578ca60dcb38614))
- Fix signature of `Client.get_quote_tweets` in documentation ([6f7de39](https://github.com/tweepy/tweepy/commit/6f7de39b65d43eb5e52e9353b9830ab49a388a03))
- Update actions/setup-python from v2 to v4 ([f16b3dc](https://github.com/tweepy/tweepy/commit/f16b3dc3afdeeba124b661734d53a3af1d504192), [0148be7](https://github.com/tweepy/tweepy/commit/0148be7edc460fcb9dae5fd1b38361cab6098da2))

Version 4.11.0 (2022-10-24)
---------------------------

### New Features / Improvements
- Add support for retrieving edited Tweet metadata
  - Add support for `include_ext_edit_control` parameter for `API` methods ([e122f35](https://github.com/tweepy/tweepy/commit/e122f351a0b9a0e461a5c13ba0a94a47bd8a446e), [e736770](https://github.com/tweepy/tweepy/commit/e736770b038e7c08d2ec37ac4827d5e03475bc7c))
  - Add support for `edit_history_tweet_ids` and `edit_controls` `Tweet` fields ([#1979](https://github.com/tweepy/tweepy/issues/1979), [a1c104f](https://github.com/tweepy/tweepy/commit/a1c104f2f9fa46371ae585b3603b761b91904612))
- Add `asynchronous.AsyncPaginator` for pagination for `AsyncClient` ([33e444a](https://github.com/tweepy/tweepy/commit/33e444a9d13d53ea024ddb3c9da30158a39ea4f6))
- Add support for `exclude` parameter for `get_quote_tweets` ([4f28bd8](https://github.com/tweepy/tweepy/commit/4f28bd85d85adf0fb735a3e24b45e7804c534aa7), [17e02b7](https://github.com/tweepy/tweepy/commit/17e02b78b9b4c5e6bf2d94e658e9d9790cd4c9a9), [48ebdb7](https://github.com/tweepy/tweepy/commit/48ebdb7face9188a352bfa82c616b20c6de12475))

### Bug Fixes
- Handle 429 HTTP errors for streaming ([#1982](https://github.com/tweepy/tweepy/issues/1982), [#1986](https://github.com/tweepy/tweepy/issues/1986))
- Lower API v2 streaming timeout to 20 seconds ([#1986](https://github.com/tweepy/tweepy/issues/1986))
- Regenerate Authorization header prior to any reconnection requests for `AsyncStream` ([29bbb7b](https://github.com/tweepy/tweepy/commit/29bbb7be378fef8347858c9825f0b48e2c380c90), [a4c6325](https://github.com/tweepy/tweepy/commit/a4c632530e6783a6a899947c7ec32d78b55fc3c6), [5ade386](https://github.com/tweepy/tweepy/commit/5ade386f0c700c6ddf785bd991851acea9b848a8))
- Use tuple for `endpoint_parameters` argument in `API.indicate_direct_message_typing` ([396ab84](https://github.com/tweepy/tweepy/commit/396ab841b73771ef6f91088fb8937a252560cf34))
- Update `models.List` methods to pass keyword arguments to `API` methods ([#1987](https://github.com/tweepy/tweepy/issues/1987))
- Update `models.List` methods to use list ID instead of slug ([73f6308](https://github.com/tweepy/tweepy/commit/73f630804a8e49d666e96b85c8d8f0780cb1ff91))

### Misc
- Log text of HTTP response when handling request error in `AsyncBaseStream` ([51c3762](https://github.com/tweepy/tweepy/commit/51c37626b76b40693cc033fec7c71d56090f7135))
- Update signature for `get_list_tweets` in documentation ([86577b1](https://github.com/tweepy/tweepy/commit/86577b1b0cbc0d8f89cf1ff33112741d48071cbb))
  - Add `media_fields`, `place_fields`, and `poll_fields` parameters
- Add version changed directive to documentation for `get_list_tweets` ([5cb2616](https://github.com/tweepy/tweepy/commit/5cb26164473b4527eccd7e05efbf903abccc1f3b))
- Improve documentation for `wait_on_rate_limit` parameter for streaming ([#1986](https://github.com/tweepy/tweepy/issues/1986))
- Add release dates to changelog ([f665ce6](https://github.com/tweepy/tweepy/commit/f665ce63c3a87dfa6ee1e3008f01c765d4a0a397), [eafa665](https://github.com/tweepy/tweepy/commit/eafa66595490f95175c89ee58eaa79d86133aaf4), [3f0cc76](https://github.com/tweepy/tweepy/commit/3f0cc760ac7e9dd9125c0f9fc63b20119e6d17e4))
- Add sections for old and previously missing versions to changelog ([6aa1b77](https://github.com/tweepy/tweepy/commit/6aa1b77a7b0adb48982979c2bc98fe98563d6696))
- Update cassettes for testing methods that return Tweet objects ([872b33e](https://github.com/tweepy/tweepy/commit/872b33ec59127dd91db291f27c61a3860eab8fac))

Version 4.10.1 (2022-08-22)
---------------------------

### Bug Fixes
- Fix `AsyncBaseClient` rate limit handling ([#1902](https://github.com/tweepy/tweepy/pull/1902))
- Fix handling of `StreamRule` when passed in list to `StreamingClient.delete_rules` or `AsyncStreamingClient.delete_rules` ([#1942](https://github.com/tweepy/tweepy/issues/1942))
- Add support for `media_fields`, `place_fields`, and `poll_fields` parameters for `Client.get_list_tweets` and `AsyncClient.get_list_tweets` ([#1931](https://github.com/tweepy/tweepy/issues/1931))
- Ignore `AsyncClient` method parameters explicitly passed as `None` ([#1944](https://github.com/tweepy/tweepy/issues/1944))

### Misc
- Log text of HTTP response when handling request error in `BaseStream` ([598ea64](https://github.com/tweepy/tweepy/commit/598ea64d68ab3c27861e0f6dcf9bbce864dc3748))
- Update Requests documentation URL for Intersphinx linking ([2c7213d](https://github.com/tweepy/tweepy/commit/2c7213d71c8df9bddac00985d411750f1eb62a56))
- Correct typo in documentation for `StreamingClient` and `AsyncStreamingClient` `add_rules` and `delete_rules` methods ([#1937](https://github.com/tweepy/tweepy/issues/1937))

Version 4.10.0 (2022-05-20)
---------------------------

### New Features / Improvements
- Add asynchronous interfaces for Twitter API v2
  - Add `asynchronous.AsyncClient` ([0aadd53](https://github.com/tweepy/tweepy/commit/0aadd5327b8e14fd6921ffb10153145cc9c58061))
    - Add `async_lru` as requirement for `async` extra
  - Add `asynchronous.AsyncStreamingClient` ([9051ba6](https://github.com/tweepy/tweepy/commit/9051ba64bc0610c9e0027e53f6e32a72de67d1e2))
- Add support for reverse chronological home timeline with Twitter API v2 ([#1900](https://github.com/tweepy/tweepy/issues/1900))
  - Add `Client.get_home_timeline` and `AsyncClient.get_home_timeline`
- Update the User-Agent header based on `AsyncStream.user_agent` even if `AsyncStream.session` is already initialized/set ([096a62c](https://github.com/tweepy/tweepy/commit/096a62c737218c4b51682c1127ab2a876547ad73))

### Twitter API Deprecations
- Deprecate `AsyncStream.sample` and note deprecation of compliance messages for `AsyncStream.filter` ([e043074](https://github.com/tweepy/tweepy/commit/e0430748b311cfc0d284897351ae589db0b85ada), [1b77007](https://github.com/tweepy/tweepy/commit/1b77007aee7b491a7878996b060a102984e84edd))

### Misc
- Update and improve various documentation and tests

Version 4.9.0 (2022-05-05)
--------------------------

### New Features / Improvements
- Add support for Direct Message typing indicator and read receipts ([#1856](https://github.com/tweepy/tweepy/issues/1856))
  - Add `API.indicate_direct_message_typing` and `API.mark_direct_message_read`
- Fallback to `"detail"` response value for `HTTPException` message ([b6b8241](https://github.com/tweepy/tweepy/commit/b6b8241d8df408a427a38d3b9a44837f07cfab32))
- Handle `"error"` key of response being a string in `HTTPException` ([2da4452](https://github.com/tweepy/tweepy/commit/2da4452870093f930fb8808861bcec809a2d4ccf))

### Twitter API Deprecations
- Deprecate `Stream.sample` and note deprecation of compliance messages for `Stream.filter` ([#1876](https://github.com/tweepy/tweepy/issues/1876))

### Misc
- Use setup.cfg for coverage.py configuration ([e24bb2f](https://github.com/tweepy/tweepy/commit/e24bb2f0febe6662552a95eb7fbd5da0f3314a24))
  - Explicitly specify coverage >= 4.4.2 requirement for dev extra ([b5bd35e](https://github.com/tweepy/tweepy/commit/b5bd35eb607b07ef7268f45df2c22e4af67adf96))
- Use setup.cfg for tox configuration ([e24bb2f](https://github.com/tweepy/tweepy/commit/e24bb2f0febe6662552a95eb7fbd5da0f3314a24))
  - Update lower bound for dev extra tox requirement to >= 3.21.0 ([ba6e6b1](https://github.com/tweepy/tweepy/commit/ba6e6b17f4c22d05ee67c11d91c25424ec61dc57))
- Remove `tests_require` from setup.py ([2870031](https://github.com/tweepy/tweepy/commit/2870031844dfc28919763d5c05c1d1bc6db8f4f1))
- Stop creating universal wheels ([9d93ec8](https://github.com/tweepy/tweepy/commit/9d93ec8ddd0f202e06e0a9393b3397d4d29e85fa))
- Update and improve various documentation and tests

Version 4.8.0 (2022-03-24)
--------------------------

### New Features / Improvements
- Add support for Bookmarks with Twitter API v2 ([#1848](https://github.com/tweepy/tweepy/issues/1848))
  - Add `Client.remove_bookmark`, `Client.get_bookmarks`, `Client.bookmark`
- Add support for using OAuth 2.0 Authorization Code Flow with `Client` methods that require the authenticating user's ID ([0157d0b](https://github.com/tweepy/tweepy/commit/0157d0b2abcfe40e4e5b77c3d8f733f67ebef9d9))
  - Raise `TypeError` for those methods when the access token isn't set
- Raise `NotFound` rather than `HTTPException` when encountering 404 response status codes in `BaseClient.request` ([b6b8219](https://github.com/tweepy/tweepy/commit/b6b82196d3f0821c184901de985e2cedb56a9db2))

Version 4.7.0 (2022-03-17)
--------------------------

### New Features / Improvements
- Add support for Quote Tweets lookup with Twitter API v2 ([#1844](https://github.com/tweepy/tweepy/issues/1844))
  - Add `Client.get_quote_tweets`

### Python Backwards-Incompatible Changes
- Drop support for Python 3.6, which has reached end-of-life status ([#1788](https://github.com/tweepy/tweepy/issues/1788))

### Bug Fixes
- Fix `Client.follow` to return response from `Client.follow_user` rather than `None` ([0742f54](https://github.com/tweepy/tweepy/commit/0742f549fae6118dd7b154ea9244077d124751a2))
- Fix `Client.unfollow` to return response from `Client.unfollow_user` rather than `None` ([c1787f0](https://github.com/tweepy/tweepy/commit/c1787f0a3ca478d1610015ce5ffa8553873a8efc))

### Misc
- Organize documentation arrangement and improve index / table of contents categorization ([c5310d1](https://github.com/tweepy/tweepy/commit/c5310d11cd62ea2aeb69bb546d0d3682dd4bc739))
- Add documentation for API v2 models
  - Add documentation for `List` ([360594b](https://github.com/tweepy/tweepy/commit/360594b9044a4b75c9cb1d0e47462e155ef75c12))
  - Add documentation for `Media` ([c2dacc8](https://github.com/tweepy/tweepy/commit/c2dacc8e53ddda3cb37cef04ba2bb629955b6938))
  - Add documentation for `Place` ([e3fa223](https://github.com/tweepy/tweepy/commit/e3fa2238819b9678cabfc2b8068cd35a11747b0a))
  - Add documentation for `Poll` ([61ed5d7](https://github.com/tweepy/tweepy/commit/61ed5d7be1bb023b43ed5522da345223a04f1ea4))
  - Add documentation for `Space` ([1a7ea1f](https://github.com/tweepy/tweepy/commit/1a7ea1f5d5580133ac478cf89921454bef71d6c5))
  - Add documentation for `Tweet` ([b9cef72](https://github.com/tweepy/tweepy/commit/b9cef72a514f64840c1583ca9fb0aaad228ef1de))
  - Add documentation for `ReferencedTweet` ([9a995b5](https://github.com/tweepy/tweepy/commit/9a995b524eab52e49428b26aca51b51a04a84278))
  - Add documentation for `User` ([aa3658e](https://github.com/tweepy/tweepy/commit/aa3658e41008e1e71cbf12ccff2b67314823ecac))
- Use Read the Docs Sphinx search extension for documentation ([72c7e01](https://github.com/tweepy/tweepy/commit/72c7e01bb87fd2834a12d8a68ddbde85da7ea8d1))
- Add and improve API v2 examples ([#1835](https://github.com/tweepy/tweepy/pull/1835), [6a6ef98](https://github.com/tweepy/tweepy/commit/6a6ef98efa58e13147220cde1b475bfc6fac3116))
- Use dash instead of underscore for requests-oauthlib requirement ([2c94758](https://github.com/tweepy/tweepy/commit/2c947583a0e3a691de2e0e9251d99e66437291f7))
- Optimize `Tweet.referenced_tweets` initialization ([3299881](https://github.com/tweepy/tweepy/commit/3299881b5e6766cc812181a107f50d3b65ae76b7))
- Update and improve various documentation

Version 4.6.0 (2022-02-24)
--------------------------
This will be the last minor version to support Python 3.6 ([#1788](https://github.com/tweepy/tweepy/issues/1788)).

### New Features / Improvements
- Add support for streaming with Twitter API v2 ([86244c1](https://github.com/tweepy/tweepy/commit/86244c1a82a1852d04f3695b03201363f5d5eafd))
  - Refactor `Client` and `Stream` to inherit from new `BaseClient` and `BaseStream` classes and add `StreamingClient`, `StreamResponse`, and `StreamRule`
- Add support for new `max_results` and `pagination_token` parameters for `Client.get_liking_users` ([bdd6b55](https://github.com/tweepy/tweepy/commit/bdd6b55d7cb075fc2e4c7cb56a061c552ca106fe))
- Add support for new `max_results` and `pagination_token` parameters for `Client.get_retweeters` ([3479e56](https://github.com/tweepy/tweepy/commit/3479e56a0fff02594ab6e77ca8227e65b51b46f7))
- Add support for new `sort_order` parameter for `Client.search_all_tweets` ([bd202e5](https://github.com/tweepy/tweepy/commit/bd202e5be19670116ebe98329d388b4821d5f3eb))
- Add support for new `sort_order` parameter for `Client.search_recent_tweets` ([8b47170](https://github.com/tweepy/tweepy/commit/8b47170e7c20127add3e67190890d2a4cef92266))
- Add `Client.get_space_tweets` ([c8d5d9a](https://github.com/tweepy/tweepy/commit/c8d5d9ad2c2b3c6b58b987286726cad467ce888f))
- Add `Space.subscriber_count` ([1ffc8cd](https://github.com/tweepy/tweepy/commit/1ffc8cda6d2b9670b86610859f21ac05d726eaf9))
- Use `repr` of text in `Tweet.__repr__` ([4e2997e](https://github.com/tweepy/tweepy/commit/4e2997e11a6e40b7e7ece508ef87be17cf493b04))
  - This avoids including inconstant newlines, rather than escaped newlines, in the string representation of the Tweet object, making it more consistent
- Override `Mapping.__contains__` in `DataMapping` ([9f10a58](https://github.com/tweepy/tweepy/commit/9f10a58e6a9fa8726fa033008f203ff577e1fc03))
  - This allows membership tests to check for existence within data in Twitter API v2 models, rather than existence of the attribute at all
- Initialize `Stream.session` within `Stream.__init__` ([80adf5b](https://github.com/tweepy/tweepy/commit/80adf5b2cc861ab6837ae03052378719e694bebc))
  - Update the user agent based on `Stream.user_agent` even if `Stream.session` is already initialized
- Use oauthlib to create code challenge and verifier for PKCE ([eb22416](https://github.com/tweepy/tweepy/commit/eb22416676ea4798340290f1a0dca1c131e8b1d5))
  - Explicitly specify oauthlib dependency requirement as >= 3.2.0 ([fc0d967](https://github.com/tweepy/tweepy/commit/fc0d96718eb37f5ce6609e1c950fd3d11c6cae79))
    - Update requests_oauthlib dependency requirement to >= 1.2.0 ([dd7e2c9](https://github.com/tweepy/tweepy/commit/dd7e2c9003983bb6c012a103e045b669063bc14b))

### Bug Fixes
- Fix datetime endpoint parameter formatting in `Client._make_request` ([#1793](https://github.com/tweepy/tweepy/pull/1793))

### Misc
- Remove undocumented `debug` function ([a702325](https://github.com/tweepy/tweepy/commit/a702325c3b1cac98e6ea7c5b19bbdd56f8745cc2))
- Add logging documentation ([7701506](https://github.com/tweepy/tweepy/commit/77015065f63022747eb10f6ed081b39dbc75c4a3))
- Update and improve various documentation

Version 4.5.0 (2022-01-24)
--------------------------

### New Features / Improvements
- Revamp authentication interface
  - Add support for OAuth 2.0 Authorization Code Flow with PKCE
    - Add `OAuth2UserHandler` ([2b83507](https://github.com/tweepy/tweepy/commit/2b835073cb193ca6f2849c8cb6ef4322e5b16f24), [16763e2](https://github.com/tweepy/tweepy/commit/16763e2ff6913653077512f069864ad720d44ad7))
    - Add `user_auth` parameters to `Client` methods ([8f38429](https://github.com/tweepy/tweepy/commit/8f384294405c6d14507441a5d1a7040d927b3fc2), [e88b074](https://github.com/tweepy/tweepy/commit/e88b07465fbcf6013be89cf938eae718391cc1df), [0d6b68a](https://github.com/tweepy/tweepy/commit/0d6b68aeb3ed36e8d0e3d400b99351ed628ba1e0))
  - Rename `OAuthHandler` to `OAuth1UserHandler` ([fb6eb7d](https://github.com/tweepy/tweepy/commit/fb6eb7d53d78bcaca997586f95270a43753a9ae6))
    - `OAuthHandler` is kept as a deprecated alias ([cba7317](https://github.com/tweepy/tweepy/commit/cba7317a4aa298a65eda7825589eb40a01a370f6))
  - Rename `AppAuthHandler` to `Oauth2AppHandler` ([529d793](https://github.com/tweepy/tweepy/commit/529d7936201f05f4167225be3bbcaf38eafadb8c))
    - `AppAuthHandler` is kept as a deprecated alias ([d4ceb1a](https://github.com/tweepy/tweepy/commit/d4ceb1aedba5380d95c8efee7d21f5e478715fe6))
  - Rename `OAuth2Bearer` to `OAuth2BearerHandler` ([0781fde](https://github.com/tweepy/tweepy/commit/0781fde83c31cef45e0d7d8b2155a2624fb93b77))
  - Allow passing access token and secret directly to `OAuth1UserHandler.__init__` ([99f3583](https://github.com/tweepy/tweepy/commit/99f3583d99ac9a0003273318e7628235bba707f0))
    - Note, this changes the `callback` parameter to be the fifth argument, positionally
  - Allow `OAuth2BearerHandler` to be used as `auth` parameter for `API` ([5a2a3fc](https://github.com/tweepy/tweepy/commit/5a2a3fc6020b6fe91141a753a2e293976addf48e))
  - Remove `AuthHandler` ([d600c4c](https://github.com/tweepy/tweepy/commit/d600c4cf6ad2755aa0a959ee57c12d86cddce973))
  - Remove `OAuth1UserHandler.get_xauth_access_token` ([8e2de9f](https://github.com/tweepy/tweepy/commit/8e2de9f590031bf6d6ade8946e7371366c4caa58))
  - Update and improve authentication documentation ([f9a722b](https://github.com/tweepy/tweepy/commit/f9a722bae8cce368b9f8fd447c418e1034c32178))
  - Other improvements and optimizations
- Add `Client.get_me` ([c49cbdf](https://github.com/tweepy/tweepy/commit/c49cbdfcbda48295591d731446cd03b2eb2332ae), [62b5b58](https://github.com/tweepy/tweepy/commit/62b5b586e75a850427eabdf31448d73a9e564f66), [f6895d3](https://github.com/tweepy/tweepy/commit/f6895d36eee68adc41d0951ce6b3ee1d7b179995), [bb87b26](https://github.com/tweepy/tweepy/commit/bb87b269efa2e0ba019a0e67fa1a7489838b9684))
- Add support for `Media.url` ([#1722](https://github.com/tweepy/tweepy/issues/1722))
- Use requests exception to handle `JSONDecodeError` ([b492b0a](https://github.com/tweepy/tweepy/commit/b492b0a9fd4a0fedbc03cc2cc1927c45e866cb4e))
  - Update requests dependency requirement to >= 2.27.0 ([ed66e8e](https://github.com/tweepy/tweepy/commit/ed66e8e98ea489eabe0e6ef607bb0c8c715b19d6))

### Bug Fixes
- Fix `Response.includes["polls"]` not being `Poll` objects ([#1733](https://github.com/tweepy/tweepy/pull/1733))
- Fix `Paginator` handling of `Client.get_all_tweets_count` ([#1761](https://github.com/tweepy/tweepy/pull/1761))

### Misc
- Improve and optimize `Model.__getstate__` ([#1707](https://github.com/tweepy/tweepy/issues/1707))
- Add API v2 examples to documentation ([bbdbb7b](https://github.com/tweepy/tweepy/commit/bbdbb7bbd7f3eb0d3c46d970aa14098d37857053))
- Update and improve various documentation

Version 4.4.0 (2021-11-17)
--------------------------
### New Features / Improvements
- Add support for List lookup with Twitter API v2 ([0aa2366](https://github.com/tweepy/tweepy/commit/0aa2366a875464756507abf42709a3db676f4cee))
- Add `Client.get_space_buyers` ([8bf58ca](https://github.com/tweepy/tweepy/commit/8bf58ca5754f72292d1d86367a02778af7a44f20))
- Add `Space.ended_at` and `Space.topic_ids` ([c89a233](https://github.com/tweepy/tweepy/commit/c89a233a96142ce01ecd5e1372c3fdce45c6601f))

### Bug Fixes
- Remove erroneous `Space.__str__` ([ebb4bfd](https://github.com/tweepy/tweepy/commit/ebb4bfdd4033e9a8ee257ab244381e1a8fdb2984))

Version 4.3.0 (2021-11-03)
--------------------------
### New Features / Improvements
- Add support for managing Tweets with Twitter API v2 ([7884e3a](https://github.com/tweepy/tweepy/commit/7884e3a7253d9a821ff46160ec0d3811f299327f))

### Misc
- Document `HTTPException` attributes ([c62c31a](https://github.com/tweepy/tweepy/commit/c62c31a0f3574e04b6e2f5996b90b5c1b5917485))
- Add table to documentation mapping `Client` methods to Twitter API v2 endpoints ([0572b03](https://github.com/tweepy/tweepy/commit/0572b03b7fe1a2384951ebc2c0002f9d8bd6b68a))
- Add and improve examples
- Revamp examples page in documentation
- Update and improve various documentation and tests

Version 4.2.0 (2021-10-29)
--------------------------
### New Features / Improvements
- Add support for managing lists with Twitter API v2 ([b1342bf](https://github.com/tweepy/tweepy/commit/b1342bfc998bee334437f2b7a8d2aef4df7c3838))
- Rename `Client.follow` and `Client.unfollow` to `Client.follow_user` and `Client.unfollow_user`, respectively ([8f8de15](https://github.com/tweepy/tweepy/commit/8f8de15e13f11d042a521d2adae24d0c09fa2098))
  - `Client.follow` and `Client.unfollow` are kept as deprecated aliases
- Add FAQ section in documentation
- Update and improve various documentation and tests

#### Twitter API Changes
- Change `state` to optional parameter for `Client.search_spaces` ([e61d5d6](https://github.com/tweepy/tweepy/commit/e61d5d6f017db7f28871331b515fcfd87666f352))

### Bug Fixes
- Fix parsing of datetime strings for API v2 models with Python 3.6 ([5bf2446](https://github.com/tweepy/tweepy/commit/5bf24464b00257a9fa5f66047a2f7815c1e4f8fb))
- Fix models missing an `API` instance attribute when using `Cursor` with pagination by ID ([451e921](https://github.com/tweepy/tweepy/commit/451e921210677ee0a618849f189bdfeea497a00c))

Version 4.1.0 (2021-10-07)
--------------------------
### New Features / Improvements
- Add support for Python 3.10 ([229b738](https://github.com/tweepy/tweepy/commit/229b73858c93bd5997385445f522816c374d41ea))
  - Update minimum dev requirement version for tox to 3.14.0
- Add support for Spaces ([5c68892](https://github.com/tweepy/tweepy/commit/5c688922cf0f8e89d401ea5108b06aaa8c12d71b))
  - Add `Space` model
  - Add `Client.search_spaces`, `Client.get_spaces`, and `Client.get_space`
- Add support for batch compliance ([6ca75e1](https://github.com/tweepy/tweepy/commit/6ca75e1b69a1085ac43215b30fc8269b91faa790))
  - Add `Client.get_compliance_jobs`, `Client.get_compliance_job`, and `Client.create_compliance_job`
- Add `Client.get_muted` ([00cdab8](https://github.com/tweepy/tweepy/commit/00cdab8a86b98c6b02636fd511700fc73653e006))
- Minor documentation corrections

Version 4.0.1 (2021-10-01)
--------------------------
### Bug Fixes
- Fix handling of strings passed as fields parameters for `Client` methods ([d61a5d9](https://github.com/tweepy/tweepy/commit/d61a5d9f52a9d9ee3f40d23515d6ffd1f2a02e14))
- Include unexpected parameters passed to `Client` methods in Twitter API request ([618d1c2](https://github.com/tweepy/tweepy/commit/618d1c25c7743443686f27006f558f4d78972da3))
  - This future-proofs for new endpoint parameters
- Stop checking parameter names when converting parameters passed to `Client` methods from datetimes to strings ([1320a37](https://github.com/tweepy/tweepy/commit/1320a3709b1683cb32b69abdaa9e7e120b6ed59c))
  - This future-proofs for new endpoint parameters besides `start_time` and `end_time` that accept datetimes
- Handle simplejson being installed when handling `JSONDecodeError` in `HTTPException` ([586c162](https://github.com/tweepy/tweepy/commit/586c1621f71c9569c17b6bdbee99a7c238bb301d))

### Misc
- Update documentation requirements ([3fa38b6](https://github.com/tweepy/tweepy/commit/3fa38b6b949fb85c434f4aec9c54327d80027c12), [388e2f6](https://github.com/tweepy/tweepy/commit/388e2f6c5167cd9fd6669d05d2e15ea00cdea805), [4315ab0](https://github.com/tweepy/tweepy/commit/4315ab07c382c92e177cde7232085dfd4828b50e))
- Remove nose usage from tests ([b4c06a4](https://github.com/tweepy/tweepy/commit/b4c06a4bb7800026809cfabf69565845dbc00923))
- Remove mock and nose from tests extra and requirements ([0f071fd](https://github.com/tweepy/tweepy/commit/0f071fd2dbbbb5eb7efccc16a8121eb22ebabf12), [b4c06a4](https://github.com/tweepy/tweepy/commit/b4c06a4bb7800026809cfabf69565845dbc00923))
- Update and improve various documentation and tests

Version 4.0.0 (2021-09-25)
--------------------------

### Major New Features / Improvements
- Support Twitter API v2 ([#1472](https://github.com/tweepy/tweepy/issues/1472), [#1535](https://github.com/tweepy/tweepy/pull/1535))
  - Replace API v1.1 models in package namespace

- Rework media uploading ([#640](https://github.com/tweepy/tweepy/issues/640), [#1486](https://github.com/tweepy/tweepy/pull/1486), [#1501](https://github.com/tweepy/tweepy/issues/1501))

- Support asynchronous streaming ([#732](https://github.com/tweepy/tweepy/issues/732), [#1491](https://github.com/tweepy/tweepy/pull/1491))

- Rework `API`
  - Replace `bind_api` and `APIMethod` with `API.request`
    - Stop using property decorators for `API` methods
    - Use `pagination` decorator
  - Add `requests.Session` instance as `API.session` attribute ([2f28757](https://github.com/tweepy/tweepy/commit/2f28757fc3f060d14ce4e42a8ca441cd172fd8e5))
    - Initialize a single `requests.Session` instance per `API` instance, rather than for each request
  - Log warning when API.request is passed an unexpected keyword argument that isn't an endpoint parameter ([c82d7ac](https://github.com/tweepy/tweepy/commit/c82d7ac1789ee9f3f1bdc2b0743376f518cdb0de))
  - Rename allowed parameters (`allowed_param`) to endpoint parameters (`endpoint_parameters`) ([b4fc6a0](https://github.com/tweepy/tweepy/commit/b4fc6a09a1f8942f000d97a182368ba1e9b8f7f5))
  - Rename methods and method parameters (see Backwards-Incompatible Changes section)
  - Require parameters for methods (see Backwards-Incompatible Changes section)
  - Stop allowing arbitrary positional arguments for methods (see Backwards-Incompatible Changes section)
  - Remove unnecessary attributes and parameters (see Backwards-Incompatible Changes section)
  - Improve, optimize, and simplify `API.request` and other `API` methods

- Rework streaming
  - `StreamListener` has been merged into `Stream` (see Backwards-Incompatible Changes section)
  - `Stream` data/event handling methods (i.e. those starting with `on_`) now log by default and disregard return values
  - Allow the stream to disconnect when any line of data is received, including keep-alive signals ([#773](https://github.com/tweepy/tweepy/issues/773), [#897](https://github.com/tweepy/tweepy/issues/897))
  - Remove, rename, and replace attributes, methods, and parameters (see Backwards-Incompatible Changes section)
  - Improve, optimize, and simplify `Stream`

- Rework documentation
  - Automatically use docstrings for documentation
  - Use NumPy style docstrings
  - Use Intersphinx linking
  - Add tooltips for cross references using sphinx-hoverxref
  - Document `Stream` ([18a6059](https://github.com/tweepy/tweepy/commit/18a6059e7980de7759be126ffe39836494cc4f23))
  - Document models ([0724060](https://github.com/tweepy/tweepy/commit/07240603b2fc64c6433d8fbe9e1e8db47a9f1cfe), [78a0c22](https://github.com/tweepy/tweepy/commit/78a0c22fb67ca3d190e9dd95baab142aa2960ff9))
  - Document pagination ([695d531](https://github.com/tweepy/tweepy/commit/695d531064277978d44f78387a3edb3d29fb6f25), [652fece](https://github.com/tweepy/tweepy/commit/652fece7f78f90ea11f206b4a045a2450db42cc9))
  - Add table for `API` documentation ([6db8e4c](https://github.com/tweepy/tweepy/commit/6db8e4c06d20f6ad7bdfade7b44b13ac45dd51c0))
  - Separate documentation for exceptions ([8a831b1](https://github.com/tweepy/tweepy/commit/8a831b16f1bd1288781bc924fe82397decd93b3d))
  - Move changelog to documentation ([fc98629](https://github.com/tweepy/tweepy/commit/fc9862963702eb02f33106ca13110b369ee86e47))
  - Update, improve, and organize documentation

- Rework exceptions
  - Replace `TweepError` with `TweepyException` ([5c39cd1](https://github.com/tweepy/tweepy/commit/5c39cd159ef761500f3cb0292a3da40d5e250417)) and `HTTPException` ([#599](https://github.com/tweepy/tweepy/issues/599))
  - Replace `RateLimitError` with `TooManyRequests` ([cd5f696](https://github.com/tweepy/tweepy/commit/cd5f696d09530f86ac0edf1ec0fe0a02578a3920))
  - Remove `Parser.parse_error` ([cd5f696](https://github.com/tweepy/tweepy/commit/cd5f696d09530f86ac0edf1ec0fe0a02578a3920))
  - Add `NotFound` ([2d84b27](https://github.com/tweepy/tweepy/commit/2d84b270408944e784b32199faa09fb553f6250d))
  - Add `Unauthorized` ([3ffec76](https://github.com/tweepy/tweepy/commit/3ffec76039a9552b1b90a11d3774ccc90793c33d))
  - Add `Forbidden` ([4a9bc58](https://github.com/tweepy/tweepy/commit/4a9bc58f1006c1b2b1310d4a6cd821e23d9c8c79))
  - Add `BadRequest` ([3da5ede](https://github.com/tweepy/tweepy/commit/3da5edeffcab5796949c0c346b0bc187f69a6874))
  - Add `TwitterServerError` ([b443557](https://github.com/tweepy/tweepy/commit/b443557e79258ab99239cc4b910bac176a0d9b60))

### Backwards-Incompatible Changes
- Drop support for Python 2 ([#1253](https://github.com/tweepy/tweepy/issues/1253), [#1482](https://github.com/tweepy/tweepy/pull/1482))
- Drop support for Python 3.5 ([#1487](https://github.com/tweepy/tweepy/pull/1487))

#### `API`
- Rename `API` and `models` methods
  - `API.blocks` -> `API.get_blocks` ([9541794](https://github.com/tweepy/tweepy/commit/9541794b5dd9a3617247c0cd5efdcd082b5e7275))
  - `API.blocks_ids` -> `API.get_blocked_ids` ([e241ca4](https://github.com/tweepy/tweepy/commit/e241ca4bb44acc0def9db390ddf10cf7f9fc37e6))
  - `API.destroy_direct_message` -> `API.delete_direct_message` ([2731fc9](https://github.com/tweepy/tweepy/commit/2731fc98fc7298425d8208d0184a60418af02ca9))
    - `DirectMessage.destroy` -> `DirectMessage.delete` ([2731fc9](https://github.com/tweepy/tweepy/commit/2731fc98fc7298425d8208d0184a60418af02ca9))
  - `API.favorites` -> `API.get_favorites` ([3c467da](https://github.com/tweepy/tweepy/commit/3c467da810f8ffdf5d7d05244d586897ed1ed547))
  - `API.followers` -> `API.get_followers` ([ce768d9](https://github.com/tweepy/tweepy/commit/ce768d974ae7c4b907aeff580728b1045c2d85d2))
  - `API.followers_ids` -> `API.get_follower_ids` ([fa5e7c4](https://github.com/tweepy/tweepy/commit/fa5e7c4bb08b775e21e52da4e7e65b61eb7bc038))
    - `models.User.followers_ids` -> `models.User.follower_ids` ([fa5e7c4](https://github.com/tweepy/tweepy/commit/fa5e7c4bb08b775e21e52da4e7e65b61eb7bc038))
  - `API.friends` -> `API.get_friends` ([6f3fccb](https://github.com/tweepy/tweepy/commit/6f3fccb95917535586efa660f9cf9c851e3e4e02))
  - `API.friends_ids` -> `API.get_friend_ids` ([bab3e5e](https://github.com/tweepy/tweepy/commit/bab3e5e9eee57583298fe64ab1ab0e37edf12344))
  - `API.friendships_incoming` -> `API.incoming_friendships` ([007bd07](https://github.com/tweepy/tweepy/commit/007bd07536d1e0dfd5a5b5967943acffb77f24f4))
  - `API.friendships_outgoing` -> `API.outgoing_friendships` ([1400065](https://github.com/tweepy/tweepy/commit/1400065bb4980ec1b3934f68173e63acffc970e2))
  - `API.geo_search` -> `API.search_geo` ([6f4fb39](https://github.com/tweepy/tweepy/commit/6f4fb39b1c88cc019e7e5d66f1c29b781568c622))
  - `API.list_direct_messages` -> `API.get_direct_messages` ([ff1186f](https://github.com/tweepy/tweepy/commit/ff1186f80b2dbb7f5e4ed3669d90db300e8de36d))
  - `API.list_members` -> `API.get_list_members` ([5845f02](https://github.com/tweepy/tweepy/commit/5845f023b74b309aa12c50844bdd586bd3e30dde))
  - `API.list_subscribers` -> `API.get_list_subscribers` ([a05b630](https://github.com/tweepy/tweepy/commit/a05b630973d4ac7e642f827f03ce01bc8e5b9ef8))
  - `API.lists_all` -> `API.get_lists` ([458e0e8](https://github.com/tweepy/tweepy/commit/458e0e8275693bb557f2a21e1f75be92adae0d00))
  - `API.lists_memberships` -> `API.get_list_memberships` ([9dddc12](https://github.com/tweepy/tweepy/commit/9dddc1262d9d043df9201ddda39002d111d035fe))
    - `models.User.lists_memberships` -> `models.User.list_memberships` ([9dddc12](https://github.com/tweepy/tweepy/commit/9dddc1262d9d043df9201ddda39002d111d035fe))
  - `API.lists_subscriptions` -> `API.get_list_subscriptions` ([51945a7](https://github.com/tweepy/tweepy/commit/51945a7124e6ce68b294c97340a6ec803cd02da9))
    - `models.User.lists_subscriptions` -> `models.User.list_subscriptions` ([51945a7](https://github.com/tweepy/tweepy/commit/51945a7124e6ce68b294c97340a6ec803cd02da9))
  - `API.mutes` -> `API.get_mutes` ([744edc2](https://github.com/tweepy/tweepy/commit/744edc245f856e3fc69401db8185b820c0219f6f))
  - `API.mutes_ids` -> `API.get_muted_ids` ([ea26a29](https://github.com/tweepy/tweepy/commit/ea26a296639e7a42d81b9f84a236a82e4915d434))
  - `API.retweeters` -> `API.get_retweeter_ids` ([588c342](https://github.com/tweepy/tweepy/commit/588c34243fe2b12d72f66f0d31312c7452610ec8))
  - `API.retweets` -> `API.get_retweets` ([3b3ba24](https://github.com/tweepy/tweepy/commit/3b3ba2494743b894a44539247fd7e5b7839c90aa))
  - `API.retweets_of_me` -> `API.get_retweets_of_me` ([737bd0b](https://github.com/tweepy/tweepy/commit/737bd0b725e5d33009e63eb040b5cb369214d7f0))
  - `API.saved_searches` -> `API.get_saved_searches` ([8b39f74](https://github.com/tweepy/tweepy/commit/8b39f748c91e3363cd35c3313563d43f1da25939))
  - `API.search` -> `API.search_tweets` ([7fac253](https://github.com/tweepy/tweepy/commit/7fac25379d51174408f0a361c22d8649437a0255))
  - `API.show_friendship` -> `API.get_friendship` ([ee9ea2e](https://github.com/tweepy/tweepy/commit/ee9ea2e4513db4d1d627a8815008cb8c71769949))
  - `API.show_list_member` -> `API.get_list_member` ([431ab15](https://github.com/tweepy/tweepy/commit/431ab15b846706dbd30387412aa601ba9f3810ab))
  - `API.show_list_subscriber` -> `API.get_list_subscriber` ([bf26301](https://github.com/tweepy/tweepy/commit/bf26301bb5fa22cc6d52ebb41ed7fe63c5a33768))
  - `API.statuses_lookup` -> `API.lookup_statuses` ([#477](https://github.com/tweepy/tweepy/issues/477))
  - `API.trends_available` -> `API.available_trends` ([68b33d7](https://github.com/tweepy/tweepy/commit/68b33d7ea70bb9c2f7efc384482b3eb6af0807fa))
  - `API.trends_closest` -> `API.closest_trends` ([2e18162](https://github.com/tweepy/tweepy/commit/2e181628ba97ec1252039439d1daccb9df93e565))
  - `API.trends_place` -> `API.get_place_trends` ([4912a7c](https://github.com/tweepy/tweepy/commit/4912a7c33420099663015325a0b758926892eb8a))
  - `API.update_with_media` -> `API.update_status_with_media` ([0a5e533](https://github.com/tweepy/tweepy/commit/0a5e533a10c87163e847a0086358a6b0224da7ff))
- Rename `API` method parameters
  - `API.geo_id`: `id` -> `place_id` ([78051e8](https://github.com/tweepy/tweepy/commit/78051e8a67b50cec5cacf53e0f9b315a53e16c4c))
  - `API.lookup_friendships`: `screen_names` -> `screen_name` ([4573b35](https://github.com/tweepy/tweepy/commit/4573b35611c8d8391373d579ccb0fe2eb6e3800b)), `user_ids` -> `user_id` ([3bcccf8](https://github.com/tweepy/tweepy/commit/3bcccf8a1f03e7e35ed05cd4f0ef8f43b6e51b33))
  - `API.lookup_statuses`: `id_` -> `id` ([f13a34b](https://github.com/tweepy/tweepy/commit/f13a34bf2309c3696fb050b8f3bac9fe1fa0b6cc))
  - `API.lookup_users`: `screen_names` -> `screen_name` ([17a2e7c](https://github.com/tweepy/tweepy/commit/17a2e7cdbbea19b8630870267a92e08e9365e29d)), `user_ids` -> `user_id` ([e7d9e55](https://github.com/tweepy/tweepy/commit/e7d9e557f2611065cfed50dbd2fcf529f9146d65))
  - `API.search_30_day`: `environment_name` -> `label` ([6c66c60](https://github.com/tweepy/tweepy/commit/6c66c603c42c609b00f923ea2ce72c1e975c5462))
  - `API.search_full_archive`: `environment_name` -> `label` ([295bfe4](https://github.com/tweepy/tweepy/commit/295bfe45ed056e94fc7055eb83aea9fcac5dddcb))
  - `API.update_profile_image`: `file_` -> `file` ([69f6c1d](https://github.com/tweepy/tweepy/commit/69f6c1d1302f0d5118ce2d288f76e7d8ffdac8c0))
- Require `API` method parameters
  - `API.closest_trends`: `lat`, `long` ([75b9616](https://github.com/tweepy/tweepy/commit/75b9616d3206967b71902e491d662b6eea5d6fe2))
  - `API.create_favorite`: `id` ([d3d2abe](https://github.com/tweepy/tweepy/commit/d3d2abec91f678d660f53af259fe9ebce7ff5a11))
  - `API.create_list`: `name` ([5e7385a](https://github.com/tweepy/tweepy/commit/5e7385a02e67178bb62c914998d8e0b7cb40714a))
  - `API.create_saved_search`: `query` ([c57a4be](https://github.com/tweepy/tweepy/commit/c57a4bef48a41165196dcbc0e2013d5718ee52a1))
  - `API.delete_direct_message`: `id` ([bcb56ab](https://github.com/tweepy/tweepy/commit/bcb56abce37d4252080fca6df796b7fc3dd2ae76))
  - `API.destroy_favorite`: `id` ([a9d41b6](https://github.com/tweepy/tweepy/commit/a9d41b6e499a07dfbcb4146ba98b44d77796efa8))
  - `API.get_direct_message`: `id` ([f5775ee](https://github.com/tweepy/tweepy/commit/f5775ee4436e3c8ba040882803d1b3ea261313be))
  - `API.get_oembed`: `url` ([af0cc51](https://github.com/tweepy/tweepy/commit/af0cc51b1f41a37d6b325596d0fa2c738a29efcf))
  - `API.get_place_trends`: `id` ([c50f540](https://github.com/tweepy/tweepy/commit/c50f5405abf8161c88e13395c61b6b188540f6f9))
  - `API.get_retweeter_ids`: `id` ([66f6704](https://github.com/tweepy/tweepy/commit/66f6704472eba01321fdb36d8991e3497967ad89))
  - `API.get_status`: `id` ([bac73c3](https://github.com/tweepy/tweepy/commit/bac73c3f1418ad3ce15524c4a9024c57ec70d12b))
  - `API.reverse_geocode`: `lat`, `long` ([87d8646](https://github.com/tweepy/tweepy/commit/87d86462b112b35e9741c9452bf956aaa16fb47c))
  - `API.search_30_day`: `query` ([52874b7](https://github.com/tweepy/tweepy/commit/52874b72cd16e3984ce99710824d07608c329024))
  - `API.search_full_archive`: `query` ([801f15d](https://github.com/tweepy/tweepy/commit/801f15de892771a5d1d683facb409c54459676b9))
  - `API.search_tweets`: `q` ([9377e7e](https://github.com/tweepy/tweepy/commit/9377e7e844f9a87e6fc8e53eb5ca0cd4d758d548))
  - `API.search_users`: `q` ([21802f9](https://github.com/tweepy/tweepy/commit/21802f9856fe8847c481f51c73d5c661b531bfc0))
  - `API.update_status`: `status` ([f64c076](https://github.com/tweepy/tweepy/commit/f64c076503e13411719faa3042267f27e96126ea))
  - `API.update_status_with_media`: `status` ([0726263](https://github.com/tweepy/tweepy/commit/0726263b33be8db7b675c0f970944bd8dccd81f1))
- Stop allowing positional arguments for `API` methods (change to be keyword-only arguments):
  - `API.add_list_member` ([ae18ee5](https://github.com/tweepy/tweepy/commit/ae18ee50c122d7cbe714ded3851eed3a765ff0c5))
  - `API.add_list_members ` ([8eb900f](https://github.com/tweepy/tweepy/commit/8eb900f12e62a21dad9314d0caf9035471baf840))
  - `API.available_trends` ([7a74863](https://github.com/tweepy/tweepy/commit/7a74863b66aeffdcd1157d8abf07df5f907cb0be))
  - `API.closest_trends`, besides `lat` and `long` ([7946490](https://github.com/tweepy/tweepy/commit/794649099b915bd44954aef2844e64dc394a4f6f))
  - `API.create_block` ([caa34c6](https://github.com/tweepy/tweepy/commit/caa34c6f790f5fa1820a52ed7dc3ebc3dd38e055))
  - `API.create_favorite`, besides `id` ([0b83984](https://github.com/tweepy/tweepy/commit/0b839841c985e1c549a63b5306ac3ea9363ded7f))
  - `API.create_friendship` ([82cd798](https://github.com/tweepy/tweepy/commit/82cd7983d70d5260c1fa9290c1552227b70af00a))
  - `API.create_list`, besides `name` ([25cb01e](https://github.com/tweepy/tweepy/commit/25cb01ec734d2e6bf913be0a5d8ef76da3ebca24))
  - `API.create_mute ` ([4aae710](https://github.com/tweepy/tweepy/commit/4aae710e05d0ed8906b3cb5bc2fabc8b8f253b44))
  - `API.create_saved_search`, besides `query` ([76be2d9](https://github.com/tweepy/tweepy/commit/76be2d9cfb2c8437627531ea7cb30047fbfd8355))
  - `API.delete_direct_message`, besides `id` ([53ca00f](https://github.com/tweepy/tweepy/commit/53ca00ffe5681deff1f80ddfe3f822d7be1ba14f))
  - `API.destroy_block` ([c49cfb2](https://github.com/tweepy/tweepy/commit/c49cfb272f15ff11ef7cc0f27a6a6ed91ac6c755))
  - `API.destroy_favorite`, besides `id` ([8afee87](https://github.com/tweepy/tweepy/commit/8afee87ee2e3f8e612082c693bab3fa6ce60cb69))
  - `API.destroy_friendship` ([b2d44fe](https://github.com/tweepy/tweepy/commit/b2d44fed587132b866401dcd0c02cb9bc0b3a130))
  - `API.destroy_list` ([4b2cfc4](https://github.com/tweepy/tweepy/commit/4b2cfc486836faa749248af1fd6dd0200202c62e))
  - `API.destroy_mute ` ([009b54e](https://github.com/tweepy/tweepy/commit/009b54e43230827264eb34141d6436b935f76084))
  - `API.destroy_saved_search`, besides `id` ([b7afca2](https://github.com/tweepy/tweepy/commit/b7afca2ad8f8721b267fd159bc7a2a91d012b15e))
  - `API.destroy_status`, besides `id` ([876c8ca](https://github.com/tweepy/tweepy/commit/876c8cad4a9574d25ac4969e554b7a5739fb75a7))
  - `API.geo_id`, besides `place_id` ([a0cff22](https://github.com/tweepy/tweepy/commit/a0cff22d0402386ffe576327b17a2a4240e51148))
  - `API.get_blocked_ids` ([ff38b70](https://github.com/tweepy/tweepy/commit/ff38b7026403eb9c952e1d1ac00a1a11c6b40f61))
  - `API.get_blocks` ([dc81854](https://github.com/tweepy/tweepy/commit/dc8185429815deeea51fad06995e64fb58c07009))
  - `API.get_direct_message`, besides `id` ([4ae0ec8](https://github.com/tweepy/tweepy/commit/4ae0ec83daef681877d7d5f3dadf41652a66051c))
  - `API.get_direct_messages` ([8e0507d](https://github.com/tweepy/tweepy/commit/8e0507dd1456a42e8c4258bed37295e1116c1bd9))
  - `API.get_favorites` ([e80b49a](https://github.com/tweepy/tweepy/commit/e80b49aded75b9cf75e168760c095a6d1a5f70ac))
  - `API.get_follower_ids` ([7d42597](https://github.com/tweepy/tweepy/commit/7d425979312dd71a8151c7463a2592bb2f57a2f9))
  - `API.get_followers` ([c6ab5a0](https://github.com/tweepy/tweepy/commit/c6ab5a0882651802a8a2fcf8c9f8300321415455))
  - `API.get_friend_ids` ([c65641b](https://github.com/tweepy/tweepy/commit/c65641b48df0320bad6046798d789e38b3cd8ec8))
  - `API.get_friends` ([e6965fa](https://github.com/tweepy/tweepy/commit/e6965fa7847782ca5e4073a21cc3cd30752eeafb))
  - `API.get_friendship` ([6dea7de](https://github.com/tweepy/tweepy/commit/6dea7de36bd4daefd33f25a76fc0712318f9735b))
  - `API.get_list` ([92dc37f](https://github.com/tweepy/tweepy/commit/92dc37f1c45b1420c1cdcef0c16843ffffc15aa4))
  - `API.get_list_member` ([0af06db](https://github.com/tweepy/tweepy/commit/0af06db70a3f41db048d2f5e866a39c48cfcdd98))
  - `API.get_list_members` ([7c8be8d](https://github.com/tweepy/tweepy/commit/7c8be8de2c9c099b61ec59078a62a2aa3fba8a8e))
  - `API.get_list_memberships` ([ec7601f](https://github.com/tweepy/tweepy/commit/ec7601ff86b8198d80242718cfea898c3d35b0ee))
  - `API.get_list_subscriber` ([a175cdd](https://github.com/tweepy/tweepy/commit/a175cdd690f577cd56e1affb7c6d42a69a5c9427))
  - `API.get_list_subscribers` ([3ee84ef](https://github.com/tweepy/tweepy/commit/3ee84ef24094eae62be706108309a5a561095be1))
  - `API.get_list_subscriptions` ([178d719](https://github.com/tweepy/tweepy/commit/178d7193c08452f4218aa8a1e0b069b6b72f23e3))
  - `API.get_lists` ([3cd0058](https://github.com/tweepy/tweepy/commit/3cd00587cf7a3b92fb64375e0311e03a4c410595))
  - `API.get_muted_ids` ([2967104](https://github.com/tweepy/tweepy/commit/2967104c1e6f2398aaf52f19c9a7627dbcdd7651))
  - `API.get_mutes` ([9e9d370](https://github.com/tweepy/tweepy/commit/9e9d370c440b0c5dd26131382a96306b681385a9))
  - `API.get_oembed`, besides `url` ([d13d853](https://github.com/tweepy/tweepy/commit/d13d8535862b12f8cd0b4ca60a4f3c4be6f3122f))
  - `API.get_place_trends`, besides `id` ([548810c](https://github.com/tweepy/tweepy/commit/548810c081508965972bbdfcec227ebcba3a350d))
  - `API.get_retweeter_ids`, besides `id` ([9907c25](https://github.com/tweepy/tweepy/commit/9907c25c8873876ff56fd2575aaa6e1994715313))
  - `API.get_retweets`, besides `id` ([0bd0292](https://github.com/tweepy/tweepy/commit/0bd0292fbe7cdd7b1b6f7a43906ac59ffb97ed72))
  - `API.get_retweets_of_me` ([2b2ed0a](https://github.com/tweepy/tweepy/commit/2b2ed0a45bfe2077dd1e0b3c0e91de2557aa4a36))
  - `API.get_saved_search`, besides `id` ([1d3d3ae](https://github.com/tweepy/tweepy/commit/1d3d3ae2f5600173771d51b193d5c3675c905167))
  - `API.get_saved_searches` ([c5f5b4b](https://github.com/tweepy/tweepy/commit/c5f5b4b552fbdff75cd4d46585cefa97a82abee7))
  - `API.get_settings` ([2c2f0ec](https://github.com/tweepy/tweepy/commit/2c2f0ecbfb4bc9b262f2320589f2ce3cf99bdc9c))
  - `API.get_status`, besides `id` ([30af3ac](https://github.com/tweepy/tweepy/commit/30af3ac8dcbd385fec6cef372550e0afb43b2612))
  - `API.get_user` ([6b761ce](https://github.com/tweepy/tweepy/commit/6b761ce7f42ad348e9d0dade6657e020f326f88d))
  - `API.home_timeline` ([b91be22](https://github.com/tweepy/tweepy/commit/b91be220928d1cb2996a5c71ef16a13c58375d4a))
  - `API.incoming_friendships` ([6d3b7f2](https://github.com/tweepy/tweepy/commit/6d3b7f259bb547eef47d6212fe4b3379b1a96586))
  - `API.list_timeline` ([e3ec5c1](https://github.com/tweepy/tweepy/commit/e3ec5c11f3f7ebac43747b8a7b0d07530ec34fea))
  - `API.lookup_friendships` ([0eff951](https://github.com/tweepy/tweepy/commit/0eff9515797dad95728f44b7c2b21fd88e5f6312))
  - `API.lookup_statuses`, besides `id` ([cf9845d](https://github.com/tweepy/tweepy/commit/cf9845d18c42600f890e5a40b313e77079ca9a5b))
  - `API.lookup_users` ([7317109](https://github.com/tweepy/tweepy/commit/731710944c07c82a7a2b52e5a73f0d20ec77b9ae))
  - `API.media_upload`, besides `filename` ([ec2498f](https://github.com/tweepy/tweepy/commit/ec2498f0d2c14702b69dbdba463e07ce8709b8d5))
  - `API.mentions_timeline` ([3614ce4](https://github.com/tweepy/tweepy/commit/3614ce42483711b1aea65c16a235b4ec4d0c8242))
  - `API.outgoing_friendships` ([09f8504](https://github.com/tweepy/tweepy/commit/09f85045945331e9b0ace417be20df0fa1ec7a79))
  - `API.rate_limit_status` ([b4b91c1](https://github.com/tweepy/tweepy/commit/b4b91c116921045eb18790330771460c28f9662a))
  - `API.remove_list_member` ([e7fa800](https://github.com/tweepy/tweepy/commit/e7fa800bf0cbe699201c7f3e26ad2e27b4193b6d))
  - `API.remove_list_members` ([593ef1c](https://github.com/tweepy/tweepy/commit/593ef1cf6a59656e3c7208ef6907009b2e95089b))
  - `API.report_spam` ([f55efcf](https://github.com/tweepy/tweepy/commit/f55efcfc86ba10c3fd133a84290a9c50a1f64a9d))
  - `API.retweet`, besides `id` ([4f7be88](https://github.com/tweepy/tweepy/commit/4f7be886e806c3f61eaaff48827c5c8d1e517fe8))
  - `API.reverse_geocode`: besides `lat` and `long` ([b209c48](https://github.com/tweepy/tweepy/commit/b209c484f1dd4458d455b4faa41971c6429dae3b))
  - `API.search_30_day`, besides `label` and `query` ([434fd35](https://github.com/tweepy/tweepy/commit/434fd35d76481f0281d62cd83b8da2bd47353e56))
  - `API.search_full_archive`, besides `label` and `query` ([44391bc](https://github.com/tweepy/tweepy/commit/44391bcf55da7fb50cf077510ee94e849599b6cd))
  - `API.search_geo` ([0a6bec9](https://github.com/tweepy/tweepy/commit/0a6bec9906b41983067315954ac533556ae85176))
  - `API.search_tweets`, besides `q` ([445da4e](https://github.com/tweepy/tweepy/commit/445da4ec69cdaf1199ac025e63d7ffc80dd9f27f))
  - `API.search_users`, besides `q` ([76ca416](https://github.com/tweepy/tweepy/commit/76ca4169f38759d7eb7deb5cd984ef615fe2b628))
  - `API.send_direct_message`, besides `recipient_id` and `text` ([7d1a549](https://github.com/tweepy/tweepy/commit/7d1a5498325cbc93c7c177a96f5642c5c5683eac))
  - `API.set_settings` ([bf1d928](https://github.com/tweepy/tweepy/commit/bf1d928cec2b9ada5d161b479f9140d80e254e81))
  - `API.supported_languages` ([2034efc](https://github.com/tweepy/tweepy/commit/2034efc450d6bf29a481fc7eca35f125dd66e9d4))
  - `API.subscribe_list` ([ee3b718](https://github.com/tweepy/tweepy/commit/ee3b718339e5ff8719cf8fc7ada5fc7930e41c13))
  - `API.unretweet`, besides `id` ([4626c42](https://github.com/tweepy/tweepy/commit/4626c424aaca20b4fcb87bbd590cdb33abed9fb0))
  - `API.unsubscribe_list` ([2df2311](https://github.com/tweepy/tweepy/commit/2df231158d08e05ccb2f08a020dea154681e2609))
  - `API.update_list` ([8b3b4fb](https://github.com/tweepy/tweepy/commit/8b3b4fbab2c9150ff3ce1f15f1f4a0f8bc5edde1))
  - `API.update_profile` ([99cd815](https://github.com/tweepy/tweepy/commit/99cd815b0e730a8f1bc2bd0737fcb83749a483c7))
  - `API.update_profile_banner`, besides `filename` ([1ca22be](https://github.com/tweepy/tweepy/commit/1ca22be0cbb0a4f3aba00b37263ac92149eceb1c))
  - `API.update_profile_image`, besides `filename` ([3539fa2](https://github.com/tweepy/tweepy/commit/3539fa2129f22af80e68adfb9d216c2176dc0181))
  - `API.update_status`, besides `status` ([761cbfe](https://github.com/tweepy/tweepy/commit/761cbfe05e866e60edf7c4e58b9ecf356507c6f2))
  - `API.update_status_with_media`, besides `filename` and `status` ([0ac4e83](https://github.com/tweepy/tweepy/commit/0ac4e83531993187df16c05a886654e13574f136))
  - `API.user_timeline` ([0ef964f](https://github.com/tweepy/tweepy/commit/0ef964f454a0e9111c1933aca13ec55c2bcbe2c3))
- Reorder `API.update_status_with_media` parameters ([87abdcd](https://github.com/tweepy/tweepy/commit/87abdcd40c89da6be3ddc3911fadd4e31fcf5986))
- Rename `API` initialization parameter: `auth_handler` -> `auth` ([ee313bd](https://github.com/tweepy/tweepy/commit/ee313bd96e9c2ecf317792a024712e98b5c33c25))
- Stop allowing positional arguments besides `auth` for `API` initialization ([da2f276](https://github.com/tweepy/tweepy/commit/da2f2767abb1b565b6902ecf7eead3dfcf651ec1))
- Remove `API.api_root` and `API.upload_root` ([e757919](https://github.com/tweepy/tweepy/commit/e7579194edd367a5fea6e50dc1cd0d82f3ae643d))
- Remove `API.compression` ([4590c7a](https://github.com/tweepy/tweepy/commit/4590c7adebc5bb540429dd9f432f16155c4bf0b5))
- Remove `API.me`, `AuthHandler.get_username`, and `OAuthHandler.get_username` ([807f937](https://github.com/tweepy/tweepy/commit/807f9371b6f0a796fea6093497401a1d10b5e183))
- Remove `API.search_host` and `API.search_root` ([92db0cf](https://github.com/tweepy/tweepy/commit/92db0cf87666229098809973554d20d35b2971a0))
- Remove `API.wait_on_rate_limit_notify` ([f325738](https://github.com/tweepy/tweepy/commit/f3257389ed566029e7eec0598597afeef6900d35))
  - Always log warning when rate limit reached
- Remove `map_` keyword argument aliasing for `API.lookup_statuses` ([0a404c3](https://github.com/tweepy/tweepy/commit/0a404c3fc66399271b1a1d769fc18665d1a7a37a))

#### `Stream`
- Remove and replace `StreamListener` by merging it into `Stream` ([39abff4](https://github.com/tweepy/tweepy/commit/39abff4520e291180425ac2219d1d8597ac5da96))
  - `StreamListener.keep_alive` -> `Stream.on_keep_alive` ([abf4d5d](https://github.com/tweepy/tweepy/commit/abf4d5d4dfa117b39bfcdc992895574df7e5ee8b))
  - `StreamListener.on_connect` -> `Stream.on_connect`
  - `StreamListener.on_data` -> `Stream.on_data`
  - `StreamListener.on_delete` -> `Stream.on_delete`
  - `StreamListener.on_disconnect` -> `Stream.on_disconnect_message` ([6c3b997](https://github.com/tweepy/tweepy/commit/6c3b997df0070b6ab7ead9cd0482cb66088ef229))
  - `StreamListener.on_error` -> `Stream.on_request_error` ([fe3bb8b](https://github.com/tweepy/tweepy/commit/fe3bb8bbbea880b4629206a7d542f71a96991e30))
  - `StreamListener.on_exception` -> `Stream.on_exception`
  - `StreamListener.on_limit` -> `Stream.on_limit`
  - `StreamListener.on_scrub_geo` -> `Stream.on_scrub_geo`
  - `StreamListener.on_status` -> `Stream.on_status`
  - `StreamListener.on_status_withheld` -> `Stream.on_status_withheld`
  - `StreamListener.on_timeout` -> `Stream.on_connection_error` ([8f62297](https://github.com/tweepy/tweepy/commit/8f622971f2a36f49ad54b70cf4f98464487a4716))
  - `StreamListener.on_user_withheld` -> `Stream.on_user_withheld`
  - `StreamListener.on_warning` -> `Stream.on_warning`
- Remove `Stream.api` ([21a9db2](https://github.com/tweepy/tweepy/commit/21a9db282a9ee981d5d767066634a0fb551bbcde))
- Remove `Stream.body` ([3e40193](https://github.com/tweepy/tweepy/commit/3e40193ee1bcecd470e28f6e1bd90e9090694213))
- Remove `Stream.headers` ([d07af4e](https://github.com/tweepy/tweepy/commit/d07af4ec865be12fc09ebf99afe2b99041e16b45))
- Remove `Stream.host` ([9cf8518](https://github.com/tweepy/tweepy/commit/9cf8518350113c1bc89aa978d7a89ffcae2f1832))
- Remove `Stream.new_session` ([26518ab](https://github.com/tweepy/tweepy/commit/26518abe993b3cf7729e9d55be571b4cc89f50ab))
- Remove `Stream.timeout` ([a2f79f1](https://github.com/tweepy/tweepy/commit/a2f79f1b6e4406672895764b044d18b33dc527fd))
- Remove `Stream.url` ([48cbf97](https://github.com/tweepy/tweepy/commit/48cbf97fbcdb9543be3bb6729e9bc4327d8993bf))
- Remove Stream parameters and attributes for reconnect wait times ([24059d4](https://github.com/tweepy/tweepy/commit/24059d41c13084003d88a8e62de081c7869db8ca))
  - Remove `Stream.retry_time_start`, `Stream.retry_420_start`, `Stream.retry_time_cap`, `Stream.snooze_time_step`, `Stream.snooze_time_cap`, `Stream.retry_time`, and `Stream.snooze_time`
- Rename `Stream.retry_count` to `Stream.max_retries` ([3585f13](https://github.com/tweepy/tweepy/commit/3585f134ecfc5e1c25d37cb6d5bd21fd2d913aa9))
- Replace `Stream.auth` with parameters and attributes for each credential ([c9f59e6](https://github.com/tweepy/tweepy/commit/c9f59e680f17412522206d0999bf9f5ac7788f2f))
  - Replace `Stream.auth` with `Stream.consumer_key`, `Stream.consumer_secret`, `Stream.access_token`, and `Stream.access_token_secret`
- Replace `Stream` parameter, `proxies`, with `proxy` ([#1272](https://github.com/tweepy/tweepy/issues/1272))
- Remove `Stream.filter` parameter: `encoding` ([b3f2db2](https://github.com/tweepy/tweepy/commit/b3f2db2baa024ea1aae7acf53948b60e02c1ed18))
- Rename `Stream.filter` and `Stream.sample` parameters: `is_async` -> `threaded` ([6c96c15](https://github.com/tweepy/tweepy/commit/6c96c156cac4ede3855222f0c4705bc08829b308))
- Stop allowing positional arguments for `Stream.filter` ([0629d5f](https://github.com/tweepy/tweepy/commit/0629d5ff17d5491d70da67b674f2e933c50f1262))
- Stop allowing positional arguments for `Stream.sample` ([b170720](https://github.com/tweepy/tweepy/commit/b170720b9af085fc024d364980f7ecde5d19de4d))

#### Twitter API Backwards-Incompatible Changes
- Remove `API.configuration` ([#1614](https://github.com/tweepy/tweepy/issues/1614))
- Remove `API.geo_similar_places` ([c6cfd97](https://github.com/tweepy/tweepy/commit/c6cfd9720b78c6261f4e7ab0f7da7802fc495d2e))
- Remove `API.related_results` ([068273b](https://github.com/tweepy/tweepy/commit/068273bb2b159af904a154bc4d0720711c671bbc))
  - Remove `Relation` model ([cc4479a](https://github.com/tweepy/tweepy/commit/cc4479a4d5331cec57880d3bc82f283a8bc8bbc5))
- Remove `id` endpoint parameter for `API.create_block` ([e4eaa4b](https://github.com/tweepy/tweepy/commit/e4eaa4bd8a85f401035f1a0f56debd9eff25c610))
- Remove `id` endpoint parameter for `API.create_friendship` ([6a3c1ab](https://github.com/tweepy/tweepy/commit/6a3c1abae29e04b52ae4e881c337bb735e72a038))
- Remove `id` endpoint parameter for `API.create_mute` ([bb25d69](https://github.com/tweepy/tweepy/commit/bb25d691d2498456a6cd05f7a9f0dc8621a9ece4))
- Remove `id` endpoint parameter for `API.destroy_block` ([1a9b52d](https://github.com/tweepy/tweepy/commit/1a9b52d121d6d00cdb8a8a9863170b748b02574e))
- Remove `id` endpoint parameter for `API.destroy_friendship` ([66f1612](https://github.com/tweepy/tweepy/commit/66f16122addb06fe244f75c44ffd7adb01e57c7f))
- Remove `id` endpoint parameter for `API.destroy_mute` ([8c444c5](https://github.com/tweepy/tweepy/commit/8c444c5b9d135bf39850bbcd757c8471e16d4202))
- Remove `id` endpoint parameter for `API.get_follower_ids` ([5cddd12](https://github.com/tweepy/tweepy/commit/5cddd12d26d22f691039de3cb792da3e9e25e0e8))
- Remove `id` endpoint parameter for `API.get_followers` ([a3fb959](https://github.com/tweepy/tweepy/commit/a3fb9594b4bcc884eb29feb11028509b73328f2a))
- Remove `id` endpoint parameter for `API.get_friend_ids`([7cbf818](https://github.com/tweepy/tweepy/commit/7cbf818e2093a5d866ab72469194df0d1d0d4696))
- Remove `id` endpoint parameter for `API.get_friends` ([6875e15](https://github.com/tweepy/tweepy/commit/6875e1517d4d81b9f5bfb5e7b5d4e076cd3a7bea))
- Remove `id` endpoint parameter for `API.get_user` ([a2681ed](https://github.com/tweepy/tweepy/commit/a2681ed376246677b48156fac66c75d05afdc3ff))
- Remove `accuracy` and `contained_within` endpoint parameters for `API.search_geo` ([d37a409](https://github.com/tweepy/tweepy/commit/d37a409e96553d86621a6caa125c5581cac0b3f7))
- Remove `allow_contributor_request` endpoint parameter for `API.set_settings` ([1cc33b2](https://github.com/tweepy/tweepy/commit/1cc33b209f181d1c729d7931c1b541947423dd4d))
- Update `API.update_profile_banner` endpoint parameters: `offset_right` -> `offset_top` ([83f9b79](https://github.com/tweepy/tweepy/commit/83f9b79f5744dc7327a8e1c7d5720742c3d370f1))
- Remove `enable_dmcommands` and `fail_dmcommands` parameters for `API.update_status` ([fe5b3ef](https://github.com/tweepy/tweepy/commit/fe5b3efd77713d00a7ca516ec20afa54903cba8c))
- Remove `in_reply_to_status_id_str` and `auto_populate_reply_metadata` endpoint parameters for `API.update_status_with_media` ([c3c9d29](https://github.com/tweepy/tweepy/commit/c3c9d29ecfffc75976b6d20b1efcfb084adfafaf))
- Remove `id` endpoint parameter for `API.user_timeline` ([#1484](https://github.com/tweepy/tweepy/pull/1484))
- Remove `Stream.firehose` ([ad50cdc](https://github.com/tweepy/tweepy/commit/ad50cdca6091c9781689634afb817f3ccd5c7e0d))
- Remove `Stream.retweet`([6b1944b](https://github.com/tweepy/tweepy/commit/6b1944b23aeb93166964f96d71f408cd21ef64be))
- Remove `Stream.sitestream` and `Stream.userstream` ([96f7e63](https://github.com/tweepy/tweepy/commit/96f7e63e1019639496bd983fd8443e49be45524f))
  - Remove `StreamListener.on_direct_message` and `StreamListener.on_friends` ([ab2479b](https://github.com/tweepy/tweepy/commit/ab2479b15da04c28144c3f4384b7aac71eaa0250))
  - Remove `StreamListener.on_event` ([20b5afb](https://github.com/tweepy/tweepy/commit/20b5afba81e451f3e7a97d97f11eb423fa2b1723))

#### Other
- Datetime objects for `models.List.created_at`, `models.SavedSearch.created_at`, `models.Status.created_at`, and `models.User.created_at` are now aware ([59d4d92](https://github.com/tweepy/tweepy/commit/59d4d920dd4470b52f329d850366721cb52ea0eb))
- Change `return_cursors` parameter for `JSONParser.parse` and `ModelParser.parse` to be keyword-only argument ([56b8e31](https://github.com/tweepy/tweepy/commit/56b8e319a874f6d4cfae7dc9f7c33f32ceea83f4))
- Remove `method` parameter from `parse` method for `Parser` and its subclasses ([dda2ec6](https://github.com/tweepy/tweepy/commit/dda2ec6ccd9b5df44daf7b8574d183ac0c2503fa))
- Remove handling of 401 HTTP status code in `API.verify_credentials` ([7e4d2a4](https://github.com/tweepy/tweepy/commit/7e4d2a4b3bc9b73501d833af349fc8b8986a5197))
- Remove `models.List.is_member` and `models.List.is_subscribed` ([b765aee](https://github.com/tweepy/tweepy/commit/b765aee92ed9a482983c8a7900cbb62a238abb60))

### New Features / Improvements

#### New Methods And Parameters / Attributes
- Add `API.get_list_ownerships` ([#1282](https://github.com/tweepy/tweepy/pull/1282), [#1498](https://github.com/tweepy/tweepy/issues/1498))
  - Add `models.User.list_ownerships` ([#1282](https://github.com/tweepy/tweepy/pull/1282))
- Add `API.get_profile_banner` ([58ac8bb](https://github.com/tweepy/tweepy/commit/58ac8bb8083044f37c1999b61ecb763918d7a703))
- Add `API.no_retweets_friendships` ([496a399](https://github.com/tweepy/tweepy/commit/496a3993ae6f6048059c3e9ee2a6f08a27f654b9))
- Add `API.remove_profile_banner` ([f0e53c6](https://github.com/tweepy/tweepy/commit/f0e53c6d6a21595cefc797b66ab8bbc027a2d425))
- Add `API.update_friendship` ([ddd24a4](https://github.com/tweepy/tweepy/commit/ddd24a474305d2a9916d92e64b2821a27a6ef450))
- Add `API.user_agent` ([bbec64b](https://github.com/tweepy/tweepy/commit/bbec64bda79350e9691951f61e9663a51696d07f))
- Add endpoint parameters for `API` methods:
  - `API.create_block`: `include_entities`, `skip_status` ([5e694b2](https://github.com/tweepy/tweepy/commit/5e694b289a8543014ed5bd04f667142ededeac04))
  - `API.create_favorite`: `include_entities` ([65c7ce7](https://github.com/tweepy/tweepy/commit/65c7ce71d09a570e14723b51fcef894093a21bae))
  - `API.destroy_block`: `include_entities`, `skip_status` ([7299362](https://github.com/tweepy/tweepy/commit/7299362474563b7082f934c56b150d3f14366e26))
  - `API.destroy_favorite`: `include_entities` ([ecd19f0](https://github.com/tweepy/tweepy/commit/ecd19f071b385cc9649a699e502cc215b441e071))
  - `API.destroy_status`: `trim_user` ([ed363e6](https://github.com/tweepy/tweepy/commit/ed363e6141ba467f27a312bca92fafd8b303db4c))
  - `API.get_blocked_ids`: `stringify_ids` ([316b4cc](https://github.com/tweepy/tweepy/commit/316b4cc73393e21075dd0fe1985777ba876bedcb))
  - `API.get_blocks`: `include_entities`, `skip_status` ([7ef1e85](https://github.com/tweepy/tweepy/commit/7ef1e8540d38e33d3082795ebf9561e24f1e42ae))
  - `API.get_favorites`: `include_entities` ([2b91edc](https://github.com/tweepy/tweepy/commit/2b91edc94c20d88467f9883fa0b16e4e35b8226f))
  - `API.get_follower_ids`: `stringify_ids ` ([c490027](https://github.com/tweepy/tweepy/commit/c490027e936c3a0a1a62cfa3cb321358414b3b93))
  - `API.get_friend_ids`: `stringify_ids`, `count` ([aba327e](https://github.com/tweepy/tweepy/commit/aba327e2aaec8ac5b63c84bdb2ece0bf7e84103f))
  - `API.get_list_member`: `include_entities`, `skip_status` ([e959787](https://github.com/tweepy/tweepy/commit/e9597879d653fec0b999ec5e48995e7c5bad298f))
  - `API.get_list_members`: `count`, `include_entities`, `skip_status` ([232fa29](https://github.com/tweepy/tweepy/commit/232fa2982fd7a92c9d8458ca63482ee8d55d06f7))
  - `API.get_list_subscriber`: `include_entities`, `skip_status` ([783941a](https://github.com/tweepy/tweepy/commit/783941a28384aaa99d7998c69df2c873636f9922))
  - `API.get_muted_ids`: `stringify_ids` ([8b04108](https://github.com/tweepy/tweepy/commit/8b04108163f130f6492534ea26baa7b460031a7c))
  - `API.get_retweeter_ids`: `count` ([71ca488](https://github.com/tweepy/tweepy/commit/71ca488c6201552647fe73a030533de03ab0dbd4))
  - `API.get_retweets`: `trim_user` ([e377188](https://github.com/tweepy/tweepy/commit/e377188c0cca0863c617f2ae7f97d51c865273e8))
  - `API.get_retweets_of_me`: `trim_user`, `include_entities`, `include_user_entities` ([589d97d](https://github.com/tweepy/tweepy/commit/589d97d400ac343b84a7b4b1911c1fb87d6e0ef6))
  - `API.get_user`: `include_entities` ([485691d](https://github.com/tweepy/tweepy/commit/485691d5686402af00938d672a102da57c195d1b))
  - `API.incoming_friendships`: `stringify_ids` ([ffb7c0e](https://github.com/tweepy/tweepy/commit/ffb7c0eb7582b1bd568c4d0c7f1ee7b4ae893ef1))
  - `API.media_upload`: `media_category`, `additional_owners` ([#1486](https://github.com/tweepy/tweepy/pull/1486))
  - `API.mentions_timeline`: `trim_user`, `include_entities` ([eb7c8f6](https://github.com/tweepy/tweepy/commit/eb7c8f6e668bf4fe00cdd2f58cc8b7c3fd9c6ed4))
  - `API.outgoing_friendships`: `stringify_ids` ([7ed0762](https://github.com/tweepy/tweepy/commit/7ed0762883e03c4479980b62b123baf1e854d316))
  - `API.retweet`: `trim_user` ([70d9665](https://github.com/tweepy/tweepy/commit/70d96657a9e2897e59dc43f789256ea709ea3857))
  - `API.search_users`: `include_entities` ([8d64b61](https://github.com/tweepy/tweepy/commit/8d64b617b974f4924df7b85e3d2ec3accb4365d1))
  - `API.unretweet`: `trim_user` ([6d93f3b](https://github.com/tweepy/tweepy/commit/6d93f3b8a082aca6dc522bfabf7d284f4476e756))
  - `API.update_profile`: `include_entities`, `skip_status` ([9715c4a](https://github.com/tweepy/tweepy/commit/9715c4a3fd1d367e4a163c9c61d0c8377a8c3c36))
- Add `Stream.on_disconnect` method ([#277](https://github.com/tweepy/tweepy/issues/277))
- Expose `Stream.thread` ([9c2419d](https://github.com/tweepy/tweepy/commit/9c2419d09c2b5af101a730917308d89dced0861a))

#### New Functionality
- Allow sending Quick Reply Options with Direct Messages ([#1280](https://github.com/tweepy/tweepy/issues/1280))
  - Replace `API.send_direct_message` parameter, `quick_reply_type`, with `quick_reply_options`
- Allow sending Call-To-Action buttons with Direct Messages in `API.send_direct_message` ([#1311](https://github.com/tweepy/tweepy/issues/1311))

#### Documentation For Existing Methods
- Document `API.get_settings` ([cbac800](https://github.com/tweepy/tweepy/commit/cbac800b752c7ac063b44e120f9699fd969718de))
- Document `API.incoming_friendships` ([09dbe0e](https://github.com/tweepy/tweepy/commit/09dbe0e8d0975531b559f18caf702152353c0fff))
- Document `API.outgoing_friendships` ([8ff5f22](https://github.com/tweepy/tweepy/commit/8ff5f22c6655002ff7ec230d2200d6833af5ff0a))
- Document `API.search_geo` ([a51a097](https://github.com/tweepy/tweepy/commit/a51a097c13b31a5ce290749b280455cb93f970cb))
- Document `API.set_settings` ([4703da3](https://github.com/tweepy/tweepy/commit/4703da38090292fb48d4d6853eb67883a5c282b8))
- Document `API.supported_languages` ([9bb8446](https://github.com/tweepy/tweepy/commit/9bb8446837562424093d4c65b6c389d2f1228c62))
- Document `API.update_profile_banner` ([a5df615](https://github.com/tweepy/tweepy/commit/a5df61561f2f40be88bc0e52bb6e50ce7b6a6052))

#### Dependencies
- Update requests_oauthlib dependency requirement to >= 1.0.0 ([bf629e5](https://github.com/tweepy/tweepy/commit/bf629e53abfada2ce58496fe775d81f47a13494e))
- Remove requests socks extra from setup.py `install_requires` ([38b6de6](https://github.com/tweepy/tweepy/commit/38b6de6c464897684cc18638f1b9348f2a7584f2))
  - Add socks extra requiring requests socks extra

#### Other
- Check consumer key and secret type when initializing `OAuthHandler` ([#1489](https://github.com/tweepy/tweepy/issues/1489))
- Make `models.User` hashable ([#1306](https://github.com/tweepy/tweepy/pull/1306))
- Reduce extra sleep time for rate limit handling for `API` ([#1049](https://github.com/tweepy/tweepy/issues/1049))
- Handle keyword arguments for `API.update_profile_image` ([ab96f2f](https://github.com/tweepy/tweepy/commit/ab96f2fca9ab6300b2f2be0472bb8458d94dbcac))
- Handle keyword arguments for `API.update_profile_banner` ([88c3fa1](https://github.com/tweepy/tweepy/commit/88c3fa1624af2a9eaaf0b85870ae01115ce0f952))
- Treat all 2xx HTTP status codes as successful responses ([a0f6984](https://github.com/tweepy/tweepy/commit/a0f69848540fceae68de1be2e4dbd3fc6c7794ec))
- Support gevent for streaming ([#651](https://github.com/tweepy/tweepy/issues/651))
- Return thread when using threaded `Stream.filter` and `Stream.sample` ([2e957b6](https://github.com/tweepy/tweepy/commit/2e957b654ed54f7d7c2b92166517f4d15deee240))
- Use specific user agent for `Stream` ([5994c4b](https://github.com/tweepy/tweepy/commit/5994c4b4005f5f909609ff04765b784fcbe9479c))

#### Misc
- Update and improve various documentation and tests
- Various other optimizations and improvements

### Bug Fixes
- Handle connection errors when streaming ([#237](https://github.com/tweepy/tweepy/issues/237), [#448](https://github.com/tweepy/tweepy/issues/448), [#750](https://github.com/tweepy/tweepy/issues/750), [#1024](https://github.com/tweepy/tweepy/issues/1024), [#1113](https://github.com/tweepy/tweepy/issues/1113), [#1416](https://github.com/tweepy/tweepy/issues/1416))
- Remove dependence on string length delimitation in `Stream` ([#892](https://github.com/tweepy/tweepy/issues/892))
- Stop reraising exceptions in `Stream._connect` ([#1072](https://github.com/tweepy/tweepy/issues/1072))
- Change `Stream.sample` method to use GET HTTP method ([1b0e869](https://github.com/tweepy/tweepy/commit/1b0e86968db9702ca258b3df93911952fc934f86))
- Default to `models.User` model in `models.Status.parse` more broadly for `user` attribute to handle parsers without `model_factory` attribute or model factories without `user` attribute ([#538](https://github.com/tweepy/tweepy/issues/538))
- Default to `models.Status` model in `models.SearchResults.parse` more broadly for results to handle parsers without `model_factory` attribute or model factories without `status` attribute ([71c031b](https://github.com/tweepy/tweepy/commit/71c031b64a397c54c8d5f64ead161df63ea1c99c))
- Start on page 1 for `PageIterator` ([#958](https://github.com/tweepy/tweepy/issues/958))
- Handle Twitter API issue with duplicate pages for `API.search_users` ([#958](https://github.com/tweepy/tweepy/issues/958), [#1465](https://github.com/tweepy/tweepy/issues/1465))
- Allow integer IDs for `Stream.filter` ([#829](https://github.com/tweepy/tweepy/issues/829), [#830](https://github.com/tweepy/tweepy/pull/830))
- Handle `ChunkedEncodingError` during streaming ([e8fcc4d](https://github.com/tweepy/tweepy/commit/e8fcc4da695abe15e8da371c1127f548aa8889ad))
- Handle Twitter API errors with successful HTTP status codes ([#1427](https://github.com/tweepy/tweepy/issues/1427))
- Handle initial negative or zero limits in `Cursor` iterators ([c1457b7](https://github.com/tweepy/tweepy/commit/c1457b7785764d736b0b1d60a15deb95581b783f))

Version 3.10.0 (2020-12-25)
---------------------------
This will be the last major and minor version to support Python 2.7 ([#1253](https://github.com/tweepy/tweepy/issues/1253)) and Python 3.5.  
The next non-patch release should be version 4.0.0.

### New Features / Improvements
- Add `API.search_30_day` and `API.search_full_archive` ([#1175](https://github.com/tweepy/tweepy/issues/1175), [#1294](https://github.com/tweepy/tweepy/pull/1294))
- Update allowed parameters for `API.home_timeline` ([#1410](https://github.com/tweepy/tweepy/issues/1410), [#1458](https://github.com/tweepy/tweepy/pull/1458))
  - Add `trim_user`, `exclude_replies`, `include_entities`
  - Remove `page` as erroneously documented parameter
  - Reorder `count` to be the first parameter
- Update allowed parameters for `API.get_oembed`
  - Add `hide_thread`, `theme`, `link_color`, `widget_type`, `dnt`
  - Remove `id`
- Remove `API.update_profile_background_image` ([#1466](https://github.com/tweepy/tweepy/issues/1466))
- Add support for Python 3.9
- Switch from Travis CI to GitHub Actions to run tests and deploy releases ([#1402](https://github.com/tweepy/tweepy/pull/1402))
- Update and improve various documentation

### Bug Fixes
- Use `mimetypes.guess_type` as fallback for determining image file type ([#1411](https://github.com/tweepy/tweepy/issues/1411))
- Use proper MIME type in Content-Type header for uploaded images
- Allow `file` parameter to be used again for `API.media_upload` ([#1412](https://github.com/tweepy/tweepy/issues/1412), [#1413](https://github.com/tweepy/tweepy/pull/1413))
- Allow `file` parameter to be used again for `API.update_profile_banner`, `API.update_profile_image`, and `API.update_with_media` ([#1475](https://github.com/tweepy/tweepy/pull/1475))
- Fix `User.lists`, `User.lists_memberships`, and `User.lists_subscriptions` to retrieve information about the user in question rather than the authenticating user ([#1443](https://github.com/tweepy/tweepy/issues/1443), [#1444](https://github.com/tweepy/tweepy/pull/1444))

Version 3.9.0 (2020-07-11)
--------------------------
### New Features / Improvements
- Add `API.create_media_metadata` ([#716](https://github.com/tweepy/tweepy/issues/716))
- Update allowed parameters for `API.update_status` ([#1101](https://github.com/tweepy/tweepy/issues/1101))
  - Add `exclude_reply_user_ids`, `attachment_url`, `possibly_sensitive`, `trim_user`, `enable_dmcommands`, `fail_dmcommands`, `card_uri`
  - Remove `in_reply_to_status_id_str`, `source`
- Add allowed parameters to `API.get_status`
  - `trim_user`, `include_my_retweet`, `include_entities`, `include_ext_alt_text`, `include_card_uri`
- Add allowed parameters to `API.statuses_lookup`
  - `include_ext_alt_text`, `include_card_uri`
- Improve `API.lookup_users` ([#706](https://github.com/tweepy/tweepy/issues/706))
- Improve and optimize `API.statuses_lookup`, `API.create_media_metadata`, `API.update_status`
- Add `reverse` as allowed parameter for `API.lists_all`
- Add `count` as allowed parameter for `API.lists_memberships`
- Add `count` as allowed parameter for `API.lists_subscriptions`
- Add `include_entities` as allowed parameter for `API.list_timeline`
- Add allowed parameters to `API.list_subscribers`
  - `count`, `include_entities`, `skip_status`
- Add support for Python 3.8
- Update and improve setup.py
- Use requests socks extra instead of requiring PySocks directly
- Allow uploading of images with file names without extensions ([#1060](https://github.com/tweepy/tweepy/issues/1060), [#1086](https://github.com/tweepy/tweepy/pull/1086))
- Support uploading WebP images ([#1298](https://github.com/tweepy/tweepy/issues/1298))
- Add missing attributes to `Relationship` model ([#1375](https://github.com/tweepy/tweepy/pull/1375))
- Update max allowed size for uploaded GIFs ([#1336](https://github.com/tweepy/tweepy/issues/1336), [#1338](https://github.com/tweepy/tweepy/pull/1338))
- Add `_json` attribute to `DirectMessage` model ([#1342](https://github.com/tweepy/tweepy/pull/1342))
- Update and improve tests ([#1217](https://github.com/tweepy/tweepy/issues/1217))
- Add documentation for extended Tweets
- Document `API.lookup_users` ([#539](https://github.com/tweepy/tweepy/issues/539))
- Add documentation for running tests ([#681](https://github.com/tweepy/tweepy/issues/681))
- Add Korean translation of documentation ([#1296](https://github.com/tweepy/tweepy/pull/1296))
- Add Polish translation of documentation ([#1316](https://github.com/tweepy/tweepy/pull/1316))
- Document `API.lookup_friendships` ([#1375](https://github.com/tweepy/tweepy/pull/1375))
- Update and improve various documentation

### Bug Fixes
- Fix handling of invalid credentials for `API.verify_credentials`
- Handle boolean value for `API.verify_credentials` include_email parameter ([#890](https://github.com/tweepy/tweepy/issues/890))
- Allow `Cursor` to be used with `API.list_direct_messages` by adding DMCursorIterator ([#1261](https://github.com/tweepy/tweepy/issues/1261), [#1262](https://github.com/tweepy/tweepy/pull/1262))

Version 3.8.0 (2019-07-14)
--------------------------
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

Version 3.7.0 (2018-11-27)
--------------------------
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

Version 3.6.0 (2015-03-02)
--------------------------
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

Version 3.5.0 (2015-11-19)
--------------------------
### Features / Improvements
- Allow 'full_text' param when getting direct messages ( #664 )
- Explicitly return api code when parsing error ( #666 )
- Remove deprecated function and clean up codes ( #583 )

### Bug Fixes
- update_status: first positional argument should be 'status' ( #578 )
- Fix "TypeError: Can't convert 'bytes' object to str implicitly" ( #615 #658 #635 )
- Fix duplicate raise in auth.py ( #667 )

Version 3.4.0 (2015-08-13)
--------------------------
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

Version 3.3.0 (2015-02-21)
--------------------------
  - Loosen our dependency requirements for Requests (>= 2.4.3)
  - Fix issue with streams freezing up on Python 3 (Issue #556)
  - Add keep_alive() callback to StreamListener when keep alive messages arrive
  - Fix issue with stream session headers not being used when restarting connection
  - Fix issue with streams getting stuck in a loop when connection dies. (PR #561)

Version 3.2.0 (2015-01-28)
--------------------------
  - Remove deprecated trends methods.
  - Fix tweepy.debug() to work in Python 3.
  - Fixed issue #529 - StreamListener language filter stopped working.
  - Add Documentation Page for streaming.
  - Add media/upload endpoint.
  - Add media_ids parameter to update_status().

Version 3.1.0 (2014-12-01)
--------------------------
  - Allow specifying your own ssl certificates for streaming client.
  - Distribute Python Wheels instead of dumb binaries.
  - Fix cursor invocation, passing args to underlying method. (https://github.com/tweepy/tweepy/issues/515)
  - Upgrade to Request 2.4.3

Version 3.0 (2014-11-30)
------------------------
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

Version 2.3.0 (2014-04-26)
--------------------------
<https://github.com/tweepy/tweepy/compare/2.2...v2.3.0>

Version 2.2 (2014-01-20)
------------------------
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

Version 2.1 (2013-06-16)
------------------------
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

Version 2.0 (2013-02-10)
------------------------
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

Version 1.13 (2013-01-17)
-------------------------
<https://github.com/tweepy/tweepy/compare/1.12...1.13>

Version 1.12 (2012-11-08)
-------------------------
<https://github.com/tweepy/tweepy/compare/1.11...1.12>

Version 1.11 (2012-08-14)
-------------------------
<https://github.com/tweepy/tweepy/compare/1.10...1.11>

Version 1.10 (2012-07-08)
-------------------------
<https://github.com/tweepy/tweepy/compare/1.9...1.10>

Version 1.9 (2012-03-17)
------------------------
<https://github.com/tweepy/tweepy/compare/1.8...1.9>

Version 1.8 (2011-10-31)
------------------------
<https://github.com/tweepy/tweepy/compare/1.7.1...1.8>

Version 1.7.1 (2010-05-25)
--------------------------
<https://github.com/tweepy/tweepy/compare/1.7...1.7.1>

Version 1.7 (2010-05-23)
------------------------
<https://github.com/tweepy/tweepy/compare/1.6...1.7>

Version 1.6 (2010-03-18)
------------------------
<https://github.com/tweepy/tweepy/compare/1.5...1.6>

Version 1.5 (2010-01-12)
------------------------
+ Models
    - Added some new helper methods to List model
    - User model
        - Added lists_memberships, lists_subscriptions, and lists helpers
        - Added followers_ids helper
    - Added ModelFactory to replace 'models' dict in tweepy.models.
        Extend this factory to plugin customized models then pass into API().
+ API
    - lists(), lists_memberships(), and lists_subscriptions() now
        take an "user" parameter for specifying which user to query.
+ OAuthHandler
    - You may now pass in an optional 'secure' boolean to the
        constructor which will use https for OAuth requests.
        Ex: auth = OAuthHandler(token,secret,secure=True)
    - Fallback to using 'twitter.com' instead of 'api.twitter.com'
        for OAuth until issue #8 is resolved.

Version 1.4 (2009-12-10)
------------------------
+ Added people search API method. API.search_users()
+ Streaming API
    - Moved parameters into POST body to prevent "head too big" errors.
    - Stream can be run either asynchronously (threaded) or synchronously (blocks main thread).
      By default Stream will run in sync. mode. To change this pass into the stream
      method 'async=True'. Example:
          s = Stream('test', 'password', MyListener())
          s.sample(async=True)  # threaded mode
          s.filter(track=['pizza']) # synch./blocking mode
    - Listener now has a "on_data" method which can be overridden to manually handle the
        raw stream data.
+ tweepyshell
    - allow using getpass for more secure password collection
      new usage: tweepyshell <username> [password] <-- optional now
    - enable debug mode with '-d' flag
+ API
	- retweet() method now works correctly
    - Added local trends method: trends_available() and trends_location()
	- send_direct_message() now accepts either a user/screen_name/user_id for recipient of DM
    - update_status() added 'source' parameter for Identi.ca
    - create_list() and update_list() added 'description' parameter
+ tweepy.debug() enables httplib debug mode
+ New Sphinx documentation (Thanks Kumar!) in doc/
+ User model
    - Fix timeline() to return correct timeline
    - Remove mentions() method

Version 1.3 (2009-11-13)
------------------------
+ Lists API methods added
+ API.verify_credentials() now returns an User object if credentials
    are valid. Otherwise false will be returned.
+ API.new() removed
+ Removed model validation. Prone to breakage due to API changes.
+ Moved documentation out of api.py and into wiki.
+ Removed 'email' parameter from API.update_profile. No longer supported.
+ API.auth_handler -> API.auth
+ Moved memcache implementation to tweepy-more repository.
+ Tweepy now uses the versioned API and the new api.twitter.com subdomain
+ Updated retweet parsing for new payload format

Version 1.2 (2009-10-16)
------------------------
+ API
    + Added automatic request re-try feature
        Example: API.friends(retry_count=5, retry_delay=10)
                Retry up to 5 times with a delay of 10 seconds between each attempt.
        See tutorial/t4.py for more an example.
    + Added cursor parameter to API.friends and API.followers methods.
      Note: page parameter is being deprecated by twitter on 10/26
    + Update parsing to handle cursor responses.
        When using 'cursor' parameter, the API method will return
        a tuple with this format: (data, next_cursor, prev_cursor)
        Calls not using the 'cursor' parameter are not changed in the way they return.
    + API.friends_ids and API.followers_ids now return a list of integers.
      Parser updated to handle cursor responses. See above.
    + Fix Status.source_url parsing
    + Fix search result 'source' parsing to properly unescape html and extract source
    + Added report_spam method

+ Cursor
    Added the Cursor object to help with pagination within the API.
    Please see the pagination tutorial for more details (tutorial/t6).
    This is the recommended way for using the 'page' and 'cursor' parameters.

+ Models
    + Status: added retweet, favorite and retweets methods
      (NOTE: retweet API not live yet on twitter)

+ Python 2.4 support

+ Update OAuth bundled library.

- Logging removed. Having our own mini-logging system just feels like overkill.
  Turns out it was not really needed that much. Simply just exposing the last
  HTTPResponse object should be good enough for most debugging.

Version 1.1 (2009-09-24)
------------------------
+ Fixes
    + Google App Engine fixes (thanks Thomas Bohmbach, Jr)
+ API
    + Added Retweet API methods
    + Added Retweet Streaming method
    + New model: Retweet
    + Updated statuses parser to handle retweet_details
    + Added new parameters for statuses/update; lat & long
    + friends_ids() & followers_ids() parameter changed page -> cursor
    + search() added "locale" parameter
    + expose last httplib.HTTPResponse object received as API.last_response
+ OAuthHandler
    + Added set_request_token() method
    + Added support for "sign in with twitter".
      get_authorization_url() now takes a boolean that when
      true uses the "sign in with twitter" flow.
      See http://apiwiki.twitter.com/Sign-in-with-Twitter
+ Logging
    + Added TweepyLogger interface which allows applications
      to collect log messages from Tweepy for debugging purposes.
    + Dummy, console, and file loggers available
+ Examples
    + Appengine demo (oauth)
+ Documentation of each method in api.py

Version 1.0.1 (2009-09-13)
--------------------------
+ Status.user --> Status.author
+ User:
    + follow()
    + unfollow()
+ API:
    + __init__() signature change; no longer accepts 'username' parameter
      which is now autodetected.
    + added new() method. shortcut for setting up new API instances
      example: API.new(auth='basic', username='testuser', password='testpass')
    + update_profile_image() and update_profile_background_image() method added.
    + Added search API methods: 
        trends, trends_current, trends_daily, and trends_weekly
+ Streaming:
    + Update to new streaming API methods
    + New StreamListener class replacing callback function
+ Fixes
    + User.following is now set to False instead of None
      when user is not followed.
    + python 2.5 import syntax error fixed
    + python 2.5 timeout support for streaming API
    + win32 failed import of fcntl in cache.py
+ Changed indents from 2 to 4 spaces

Version 1.0 (2009-08-13)
------------------------
<https://github.com/tweepy/tweepy/commits/e62f8c18977fd755c9d24a0abebd3b8087c75b45>
