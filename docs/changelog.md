Changelog
=========

These changelogs are also at <https://github.com/tweepy/tweepy/releases> as release notes.

Version 4.1.0
-------------
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

Version 4.0.1
-------------
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

Version 4.0.0
-------------

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
  - Rename methods and method parameters (see Breaking Changes section)
  - Require parameters for methods (see Breaking Changes section)
  - Stop allowing arbitrary positional arguments for methods (see Breaking Changes section)
  - Remove unnecessary attributes and parameters (see Breaking Changes section)
  - Improve, optimize, and simplify `API.request` and other `API` methods

- Rework streaming
  - `StreamListener` has been merged into `Stream` (see Breaking Changes section)
  - `Stream` data/event handling methods (i.e. those starting with `on_`) now log by default and disregard return values
  - Allow the stream to disconnect when any line of data is received, including keep-alive signals ([#773](https://github.com/tweepy/tweepy/issues/773), [#897](https://github.com/tweepy/tweepy/issues/897))
  - Remove, rename, and replace attributes, methods, and parameters (see Breaking Changes section)
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

### Breaking Changes
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

#### Twitter API Breaking Changes
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

Version 3.10.0
--------------
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

Version 3.9.0
-------------
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
