.. _api_reference:

.. currentmodule:: tweepy

.. include:: parameters.rst

************
:class:`API`
************

.. autoclass:: API

.. table::
    :align: center

    +------------------------------------------+--------------------------------------------+
    | Twitter API v1.1 Endpoint                | :class:`API` Method                        |
    +==========================================+============================================+
    | .. centered:: :ref:`Tweets`                                                           |
    +---------------------------------------------------------------------------------------+
    | .. centered:: |Get Tweet timelines|_                                                  |
    +------------------------------------------+--------------------------------------------+
    | `GET statuses/home_timeline`_            | :meth:`API.home_timeline`                  |
    +------------------------------------------+--------------------------------------------+
    | `GET statuses/mentions_timeline`_        | :meth:`API.mentions_timeline`              |
    +------------------------------------------+--------------------------------------------+
    | `GET statuses/user_timeline`_            | :meth:`API.user_timeline`                  |
    +------------------------------------------+--------------------------------------------+
    | .. centered:: |Post, retrieve, and engage with Tweets|_                               |
    +------------------------------------------+--------------------------------------------+
    | `GET favorites/list`_                    | :meth:`API.get_favorites`                  |
    +------------------------------------------+--------------------------------------------+
    | `GET statuses/lookup`_                   | :meth:`API.lookup_statuses`                |
    +------------------------------------------+--------------------------------------------+
    | `GET statuses/oembed`_                   | :meth:`API.get_oembed`                     |
    +------------------------------------------+--------------------------------------------+
    | `GET statuses/retweeters/ids`_           | :meth:`API.get_retweeter_ids`              |
    +------------------------------------------+--------------------------------------------+
    | `GET statuses/retweets/:id`_             | :meth:`API.get_retweets`                   |
    +------------------------------------------+--------------------------------------------+
    | `GET statuses/retweets_of_me`_           | :meth:`API.get_retweets_of_me`             |
    +------------------------------------------+--------------------------------------------+
    | `GET statuses/show/:id`_                 | :meth:`API.get_status`                     |
    +------------------------------------------+--------------------------------------------+
    | `POST favorites/create`_                 | :meth:`API.create_favorite`                |
    +------------------------------------------+--------------------------------------------+
    | `POST favorites/destroy`_                | :meth:`API.destroy_favorite`               |
    +------------------------------------------+--------------------------------------------+
    | `POST statuses/destroy/:id`_             | :meth:`API.destroy_status`                 |
    +------------------------------------------+--------------------------------------------+
    | `POST statuses/retweet/:id`_             | :meth:`API.retweet`                        |
    +------------------------------------------+--------------------------------------------+
    | `POST statuses/unretweet/:id`_           | :meth:`API.unretweet`                      |
    +------------------------------------------+--------------------------------------------+
    | `POST statuses/update`_                  | :meth:`API.update_status`                  |
    +------------------------------------------+--------------------------------------------+
    | `POST statuses/update_with_media`_       | :meth:`API.update_status_with_media`       |
    +------------------------------------------+--------------------------------------------+
    | .. centered:: |Search Tweets|_                                                        |
    +------------------------------------------+--------------------------------------------+
    | `GET search/tweets`_                     | :meth:`API.search_tweets`                  |
    +------------------------------------------+--------------------------------------------+
    | .. centered:: :ref:`Accounts and users`                                               |
    +---------------------------------------------------------------------------------------+
    | .. centered:: |Create and manage lists|_                                              |
    +------------------------------------------+--------------------------------------------+
    | `GET lists/list`_                        | :meth:`API.get_lists`                      |
    +------------------------------------------+--------------------------------------------+
    | `GET lists/members`_                     | :meth:`API.get_list_members`               |
    +------------------------------------------+--------------------------------------------+
    | `GET lists/members/show`_                | :meth:`API.get_list_member`                |
    +------------------------------------------+--------------------------------------------+
    | `GET lists/memberships`_                 | :meth:`API.get_list_memberships`           |
    +------------------------------------------+--------------------------------------------+
    | `GET lists/ownerships`_                  | :meth:`API.get_list_ownerships`            |
    +------------------------------------------+--------------------------------------------+
    | `GET lists/show`_                        | :meth:`API.get_list`                       |
    +------------------------------------------+--------------------------------------------+
    | `GET lists/statuses`_                    | :meth:`API.list_timeline`                  |
    +------------------------------------------+--------------------------------------------+
    | `GET lists/subscribers`_                 | :meth:`API.get_list_subscribers`           |
    +------------------------------------------+--------------------------------------------+
    | `GET lists/subscribers/show`_            | :meth:`API.get_list_subscriber`            |
    +------------------------------------------+--------------------------------------------+
    | `GET lists/subscriptions`_               | :meth:`API.get_list_subscriptions`         |
    +------------------------------------------+--------------------------------------------+
    | `POST lists/create`_                     | :meth:`API.create_list`                    |
    +------------------------------------------+--------------------------------------------+
    | `POST lists/destroy`_                    | :meth:`API.destroy_list`                   |
    +------------------------------------------+--------------------------------------------+
    | `POST lists/members/create`_             | :meth:`API.add_list_member`                |
    +------------------------------------------+--------------------------------------------+
    | `POST lists/members/create_all`_         | :meth:`API.add_list_members`               |
    +------------------------------------------+--------------------------------------------+
    | `POST lists/members/destroy`_            | :meth:`API.remove_list_member`             |
    +------------------------------------------+--------------------------------------------+
    | `POST lists/members/destroy_all`_        | :meth:`API.remove_list_members`            |
    +------------------------------------------+--------------------------------------------+
    | `POST lists/subscribers/create`_         | :meth:`API.subscribe_list`                 |
    +------------------------------------------+--------------------------------------------+
    | `POST lists/subscribers/destroy`_        | :meth:`API.unsubscribe_list`               |
    +------------------------------------------+--------------------------------------------+
    | `POST lists/update`_                     | :meth:`API.update_list`                    |
    +------------------------------------------+--------------------------------------------+
    | .. centered:: |Follow, search, and get users|_                                        |
    +------------------------------------------+--------------------------------------------+
    | `GET followers/ids`_                     | :meth:`API.get_follower_ids`               |
    +------------------------------------------+--------------------------------------------+
    | `GET followers/list`_                    | :meth:`API.get_followers`                  |
    +------------------------------------------+--------------------------------------------+
    | `GET friends/ids`_                       | :meth:`API.get_friend_ids`                 |
    +------------------------------------------+--------------------------------------------+
    | `GET friends/list`_                      | :meth:`API.get_friends`                    |
    +------------------------------------------+--------------------------------------------+
    | `GET friendships/incoming`_              | :meth:`API.incoming_friendships`           |
    +------------------------------------------+--------------------------------------------+
    | `GET friendships/lookup`_                | :meth:`API.lookup_friendships`             |
    +------------------------------------------+--------------------------------------------+
    | `GET friendships/no_retweets/ids`_       | :meth:`API.no_retweets_friendships`        |
    +------------------------------------------+--------------------------------------------+
    | `GET friendships/outgoing`_              | :meth:`API.outgoing_friendships`           |
    +------------------------------------------+--------------------------------------------+
    | `GET friendships/show`_                  | :meth:`API.get_friendship`                 |
    +------------------------------------------+--------------------------------------------+
    | `GET users/lookup`_                      | :meth:`API.lookup_users`                   |
    +------------------------------------------+--------------------------------------------+
    | `GET users/search`_                      | :meth:`API.search_users`                   |
    +------------------------------------------+--------------------------------------------+
    | `GET users/show`_                        | :meth:`API.get_user`                       |
    +------------------------------------------+--------------------------------------------+
    | `POST friendships/create`_               | :meth:`API.create_friendship`              |
    +------------------------------------------+--------------------------------------------+
    | `POST friendships/destroy`_              | :meth:`API.destroy_friendship`             |
    +------------------------------------------+--------------------------------------------+
    | `POST friendships/update`_               | :meth:`API.update_friendship`              |
    +------------------------------------------+--------------------------------------------+
    | .. centered:: |Manage account settings and profile|_                                  |
    +------------------------------------------+--------------------------------------------+
    | `GET account/settings`_                  | :meth:`API.get_settings`                   |
    +------------------------------------------+--------------------------------------------+
    | `GET account/verify_credentials`_        | :meth:`API.verify_credentials`             |
    +------------------------------------------+--------------------------------------------+
    | `GET saved_searches/list`_               | :meth:`API.get_saved_searches`             |
    +------------------------------------------+--------------------------------------------+
    | `GET saved_searches/show/:id`_           | :meth:`API.get_saved_search`               |
    +------------------------------------------+--------------------------------------------+
    | `GET users/profile_banner`_              | :meth:`API.get_profile_banner`             |
    +------------------------------------------+--------------------------------------------+
    | `POST account/remove_profile_banner`_    | :meth:`API.remove_profile_banner`          |
    +------------------------------------------+--------------------------------------------+
    | `POST account/settings`_                 | :meth:`API.set_settings`                   |
    +------------------------------------------+--------------------------------------------+
    | `POST account/update_profile`_           | :meth:`API.update_profile`                 |
    +------------------------------------------+--------------------------------------------+
    | `POST account/update_profile_banner`_    | :meth:`API.update_profile_banner`          |
    +------------------------------------------+--------------------------------------------+
    | `POST account/update_profile_image`_     | :meth:`API.update_profile_image`           |
    +------------------------------------------+--------------------------------------------+
    | `POST saved_searches/create`_            | :meth:`API.create_saved_search`            |
    +------------------------------------------+--------------------------------------------+
    | `POST saved_searches/destroy/:id`_       | :meth:`API.destroy_saved_search`           |
    +------------------------------------------+--------------------------------------------+
    | .. centered:: |Mute, block, and report users|_                                        |
    +------------------------------------------+--------------------------------------------+
    | `GET blocks/ids`_                        | :meth:`API.get_blocked_ids`                |
    +------------------------------------------+--------------------------------------------+
    | `GET blocks/list`_                       | :meth:`API.get_blocks`                     |
    +------------------------------------------+--------------------------------------------+
    | `GET mutes/users/ids`_                   | :meth:`API.get_muted_ids`                  |
    +------------------------------------------+--------------------------------------------+
    | `GET mutes/users/list`_                  | :meth:`API.get_mutes`                      |
    +------------------------------------------+--------------------------------------------+
    | `POST blocks/create`_                    | :meth:`API.create_block`                   |
    +------------------------------------------+--------------------------------------------+
    | `POST blocks/destroy`_                   | :meth:`API.destroy_block`                  |
    +------------------------------------------+--------------------------------------------+
    | `POST mutes/users/create`_               | :meth:`API.create_mute`                    |
    +------------------------------------------+--------------------------------------------+
    | `POST mutes/users/destroy`_              | :meth:`API.destroy_mute`                   |
    +------------------------------------------+--------------------------------------------+
    | `POST users/report_spam`_                | :meth:`API.report_spam`                    |
    +------------------------------------------+--------------------------------------------+
    | .. centered:: :ref:`Direct Messages`                                                  |
    +---------------------------------------------------------------------------------------+
    | .. centered:: |Sending and receiving events|_                                         |
    +------------------------------------------+--------------------------------------------+
    | `DELETE direct_messages/events/destroy`_ | :meth:`API.delete_direct_message`          |
    +------------------------------------------+--------------------------------------------+
    | `GET direct_messages/events/list`_       | :meth:`API.get_direct_messages`            |
    +------------------------------------------+--------------------------------------------+
    | `GET direct_messages/events/show`_       | :meth:`API.get_direct_message`             |
    +------------------------------------------+--------------------------------------------+
    | `POST direct_messages/events/new`_       | :meth:`API.send_direct_message`            |
    +------------------------------------------+--------------------------------------------+
    | .. centered:: |Typing indicator and read receipts|_                                   |
    +------------------------------------------+--------------------------------------------+
    | `POST direct_messages/indicate_typing`_  | :meth:`API.indicate_direct_message_typing` |
    +------------------------------------------+--------------------------------------------+
    | `POST direct_messages/mark_read`_        | :meth:`API.mark_direct_message_read`       |
    +------------------------------------------+--------------------------------------------+
    | .. centered:: :ref:`Media`                                                            |
    +---------------------------------------------------------------------------------------+
    | .. centered:: |Upload media|_                                                         |
    +------------------------------------------+--------------------------------------------+
    | `GET media/upload`_                      | :meth:`API.get_media_upload_status`        |
    +------------------------------------------+--------------------------------------------+
    | `POST media/metadata/create`_            | :meth:`API.create_media_metadata`          |
    +------------------------------------------+--------------------------------------------+
    |                                          | :meth:`API.media_upload`                   |
    +------------------------------------------+--------------------------------------------+
    | `POST media/upload`_                     | :meth:`API.simple_upload`                  |
    +------------------------------------------+--------------------------------------------+
    |                                          | :meth:`API.chunked_upload`                 |
    +------------------------------------------+--------------------------------------------+
    | `POST media/upload (APPEND)`_            | :meth:`API.chunked_upload_append`          |
    +------------------------------------------+--------------------------------------------+
    | `POST media/upload (FINALIZE)`_          | :meth:`API.chunked_upload_finalize`        |
    +------------------------------------------+--------------------------------------------+
    | `POST media/upload (INIT)`_              | :meth:`API.chunked_upload_init`            |
    +------------------------------------------+--------------------------------------------+
    | .. centered:: :ref:`Trends`                                                           |
    +---------------------------------------------------------------------------------------+
    | .. centered:: |Get locations with trending topics|_                                   |
    +------------------------------------------+--------------------------------------------+
    | `GET trends/available`_                  | :meth:`API.available_trends`               |
    +------------------------------------------+--------------------------------------------+
    | `GET trends/closest`_                    | :meth:`API.closest_trends`                 |
    +------------------------------------------+--------------------------------------------+
    | .. centered::  |Get trends near a location|_                                          |
    +------------------------------------------+--------------------------------------------+
    | `GET trends/place`_                      | :meth:`API.get_place_trends`               |
    +------------------------------------------+--------------------------------------------+
    | .. centered:: :ref:`Geo`                                                              |
    +---------------------------------------------------------------------------------------+
    | .. centered:: |Get information about a place|_                                        |
    +------------------------------------------+--------------------------------------------+
    | `GET geo/id/:place_id`_                  | :meth:`API.geo_id`                         |
    +------------------------------------------+--------------------------------------------+
    | .. centered::  |Get places near a location|_                                          |
    +------------------------------------------+--------------------------------------------+
    | `GET geo/reverse_geocode`_               | :meth:`API.reverse_geocode`                |
    +------------------------------------------+--------------------------------------------+
    | `GET geo/search`_                        | :meth:`API.search_geo`                     |
    +------------------------------------------+--------------------------------------------+
    | .. centered:: :ref:`Developer utilities`                                              |
    +---------------------------------------------------------------------------------------+
    | .. centered:: |Get Twitter supported languages|_                                      |
    +------------------------------------------+--------------------------------------------+
    | `GET help/languages`_                    | :meth:`API.supported_languages`            |
    +------------------------------------------+--------------------------------------------+
    | .. centered:: |Get app rate limit status|_                                            |
    +------------------------------------------+--------------------------------------------+
    | `GET application/rate_limit_status`_     | :meth:`API.rate_limit_status`              |
    +------------------------------------------+--------------------------------------------+

.. |Get Tweet timelines| replace:: *Get Tweet timelines*
.. _GET statuses/home_timeline: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/timelines/api-reference/get-statuses-home_timeline
.. _GET statuses/mentions_timeline: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/timelines/api-reference/get-statuses-mentions_timeline
.. _GET statuses/user_timeline: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/timelines/api-reference/get-statuses-user_timeline
.. |Post, retrieve, and engage with Tweets| replace:: *Post, retrieve, and engage with Tweets*
.. _GET favorites/list: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/get-favorites-list
.. _GET statuses/lookup: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/get-statuses-lookup
.. _GET statuses/oembed: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/get-statuses-oembed
.. _GET statuses/retweeters/ids: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/get-statuses-retweeters-ids
.. _GET statuses/retweets/:id: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/get-statuses-retweets-id
.. _GET statuses/retweets_of_me: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/get-statuses-retweets_of_me
.. _GET statuses/show/:id: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/get-statuses-show-id
.. _POST favorites/create: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/post-favorites-create
.. _POST favorites/destroy: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/post-favorites-destroy
.. _POST statuses/destroy/:id: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/post-statuses-destroy-id
.. _POST statuses/retweet/:id: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/post-statuses-retweet-id
.. _POST statuses/unretweet/:id: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/post-statuses-unretweet-id
.. _POST statuses/update: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/post-statuses-update
.. _POST statuses/update_with_media: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/post-statuses-update_with_media
.. |Search Tweets| replace:: *Search Tweets*
.. _GET search/tweets: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/search/api-reference/get-search-tweets
.. |Create and manage lists| replace:: *Create and manage lists*
.. _GET lists/list: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/get-lists-list
.. _GET lists/members: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/get-lists-members
.. _GET lists/members/show: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/get-lists-members-show
.. _GET lists/memberships: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/get-lists-memberships
.. _GET lists/ownerships: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/get-lists-ownerships
.. _GET lists/show: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/get-lists-show
.. _GET lists/statuses: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/get-lists-statuses
.. _GET lists/subscribers: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/get-lists-subscribers
.. _GET lists/subscribers/show: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/get-lists-subscribers-show
.. _GET lists/subscriptions: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/get-lists-subscriptions
.. _POST lists/create: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/post-lists-create
.. _POST lists/destroy: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/post-lists-destroy
.. _POST lists/members/create: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/post-lists-members-create
.. _POST lists/members/create_all: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/post-lists-members-create_all
.. _POST lists/members/destroy: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/post-lists-members-destroy
.. _POST lists/members/destroy_all: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/post-lists-members-destroy_all
.. _POST lists/subscribers/create: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/post-lists-subscribers-create
.. _POST lists/subscribers/destroy: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/post-lists-subscribers-destroy
.. _POST lists/update: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/post-lists-update
.. |Follow, search, and get users| replace:: *Follow, search, and get users*
.. _GET followers/ids: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-followers-ids
.. _GET followers/list: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-followers-list
.. _GET friends/ids: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-friends-ids
.. _GET friends/list: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-friends-list
.. _GET friendships/incoming: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-friendships-incoming
.. _GET friendships/lookup: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-friendships-lookup
.. _GET friendships/no_retweets/ids: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-friendships-no_retweets-ids
.. _GET friendships/outgoing: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-friendships-outgoing
.. _GET friendships/show: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-friendships-show
.. _GET users/lookup: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-users-lookup
.. _GET users/search: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-users-search
.. _GET users/show: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-users-show
.. _POST friendships/create: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/post-friendships-create
.. _POST friendships/destroy: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/post-friendships-destroy
.. _POST friendships/update: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/post-friendships-update
.. |Manage account settings and profile| replace:: *Manage account settings and profile*
.. _GET account/settings: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/get-account-settings
.. _GET account/verify_credentials: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/get-account-verify_credentials
.. _GET saved_searches/list: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/get-saved_searches-list
.. _GET saved_searches/show/:id: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/get-saved_searches-show-id
.. _GET users/profile_banner: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/get-users-profile_banner
.. _POST account/remove_profile_banner: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/post-account-remove_profile_banner
.. _POST account/settings: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/post-account-settings
.. _POST account/update_profile: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/post-account-update_profile
.. _POST account/update_profile_banner: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/post-account-update_profile_banner
.. _POST account/update_profile_image: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/post-account-update_profile_image
.. _POST saved_searches/create: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/post-saved_searches-create
.. _POST saved_searches/destroy/:id: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/post-saved_searches-destroy-id
.. |Mute, block, and report users| replace:: *Mute, block, and report users*
.. _GET blocks/ids: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/mute-block-report-users/api-reference/get-blocks-ids
.. _GET blocks/list: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/mute-block-report-users/api-reference/get-blocks-list
.. _GET mutes/users/ids: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/mute-block-report-users/api-reference/get-mutes-users-ids
.. _GET mutes/users/list: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/mute-block-report-users/api-reference/get-mutes-users-list
.. _POST blocks/create: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/mute-block-report-users/api-reference/post-blocks-create
.. _POST blocks/destroy: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/mute-block-report-users/api-reference/post-blocks-destroy
.. _POST mutes/users/create: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/mute-block-report-users/api-reference/post-mutes-users-create
.. _POST mutes/users/destroy: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/mute-block-report-users/api-reference/post-mutes-users-destroy
.. _POST users/report_spam: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/mute-block-report-users/api-reference/post-users-report_spam
.. |Sending and receiving events| replace:: *Sending and receiving events*
.. _DELETE direct_messages/events/destroy: https://developer.twitter.com/en/docs/twitter-api/v1/direct-messages/sending-and-receiving/api-reference/delete-message-event
.. _GET direct_messages/events/list: https://developer.twitter.com/en/docs/twitter-api/v1/direct-messages/sending-and-receiving/api-reference/list-events
.. _GET direct_messages/events/show: https://developer.twitter.com/en/docs/twitter-api/v1/direct-messages/sending-and-receiving/api-reference/get-event
.. _POST direct_messages/events/new: https://developer.twitter.com/en/docs/twitter-api/v1/direct-messages/sending-and-receiving/api-reference/new-event
.. |Typing indicator and read receipts| replace:: *Typing indicator and read receipts*
.. _POST direct_messages/indicate_typing: https://developer.twitter.com/en/docs/twitter-api/v1/direct-messages/typing-indicator-and-read-receipts/api-reference/new-typing-indicator
.. _POST direct_messages/mark_read: https://developer.twitter.com/en/docs/twitter-api/v1/direct-messages/typing-indicator-and-read-receipts/api-reference/new-read-receipt
.. |Upload media| replace:: *Upload media*
.. _GET media/upload: https://developer.twitter.com/en/docs/twitter-api/v1/media/upload-media/api-reference/get-media-upload-status
.. _POST media/metadata/create: https://developer.twitter.com/en/docs/twitter-api/v1/media/upload-media/api-reference/post-media-metadata-create
.. _POST media/upload: https://developer.twitter.com/en/docs/twitter-api/v1/media/upload-media/api-reference/post-media-upload
.. _POST media/upload (APPEND): https://developer.twitter.com/en/docs/twitter-api/v1/media/upload-media/api-reference/post-media-upload-append
.. _POST media/upload (FINALIZE): https://developer.twitter.com/en/docs/twitter-api/v1/media/upload-media/api-reference/post-media-upload-finalize
.. _POST media/upload (INIT): https://developer.twitter.com/en/docs/twitter-api/v1/media/upload-media/api-reference/post-media-upload-init
.. |Get locations with trending topics| replace:: *Get locations with trending topics*
.. _GET trends/available: https://developer.twitter.com/en/docs/twitter-api/v1/trends/locations-with-trending-topics/api-reference/get-trends-available
.. _GET trends/closest: https://developer.twitter.com/en/docs/twitter-api/v1/trends/locations-with-trending-topics/api-reference/get-trends-closest
.. |Get trends near a location| replace:: *Get trends near a location*
.. _GET trends/place: https://developer.twitter.com/en/docs/twitter-api/v1/trends/trends-for-location/api-reference/get-trends-place
.. |Get information about a place| replace:: *Get information about a place*
.. _GET geo/id/:place_id: https://developer.twitter.com/en/docs/twitter-api/v1/geo/place-information/api-reference/get-geo-id-place_id
.. |Get places near a location| replace:: *Get places near a location*
.. _GET geo/reverse_geocode: https://developer.twitter.com/en/docs/twitter-api/v1/geo/places-near-location/api-reference/get-geo-reverse_geocode
.. _GET geo/search: https://developer.twitter.com/en/docs/twitter-api/v1/geo/places-near-location/api-reference/get-geo-search
.. |Get Twitter supported languages| replace:: *Get Twitter supported languages*
.. _GET help/languages: https://developer.twitter.com/en/docs/twitter-api/v1/developer-utilities/supported-languages/api-reference/get-help-languages
.. |Get app rate limit status| replace:: *Get app rate limit status*
.. _GET application/rate_limit_status: https://developer.twitter.com/en/docs/twitter-api/v1/developer-utilities/rate-limit-status/api-reference/get-application-rate_limit_status

Tweets
======

Get Tweet timelines
-------------------

.. automethod:: API.home_timeline

.. automethod:: API.mentions_timeline

.. automethod:: API.user_timeline

Post, retrieve, and engage with Tweets
--------------------------------------

.. automethod:: API.get_favorites

.. automethod:: API.lookup_statuses

.. automethod:: API.get_oembed

.. automethod:: API.get_retweeter_ids

.. automethod:: API.get_retweets

.. automethod:: API.get_retweets_of_me

.. automethod:: API.get_status

.. automethod:: API.create_favorite

.. automethod:: API.destroy_favorite

.. automethod:: API.destroy_status

.. automethod:: API.retweet

.. automethod:: API.unretweet

.. automethod:: API.update_status

.. automethod:: API.update_status_with_media

Search Tweets
-------------

.. automethod:: API.search_tweets

Accounts and users
==================

Create and manage lists
-----------------------

.. automethod:: API.get_lists

.. automethod:: API.get_list_members

.. automethod:: API.get_list_member

.. automethod:: API.get_list_memberships

.. automethod:: API.get_list_ownerships

.. automethod:: API.get_list

.. automethod:: API.list_timeline

.. automethod:: API.get_list_subscribers

.. automethod:: API.get_list_subscriber

.. automethod:: API.get_list_subscriptions

.. automethod:: API.create_list

.. automethod:: API.destroy_list

.. automethod:: API.add_list_member

.. automethod:: API.add_list_members

.. automethod:: API.remove_list_member

.. automethod:: API.remove_list_members

.. automethod:: API.subscribe_list

.. automethod:: API.unsubscribe_list

.. automethod:: API.update_list

Follow, search, and get users
-----------------------------

.. automethod:: API.get_follower_ids

.. automethod:: API.get_followers

.. automethod:: API.get_friend_ids

.. automethod:: API.get_friends

.. automethod:: API.incoming_friendships

.. automethod:: API.lookup_friendships

.. automethod:: API.no_retweets_friendships

.. automethod:: API.outgoing_friendships

.. automethod:: API.get_friendship

.. automethod:: API.lookup_users

.. automethod:: API.search_users

.. automethod:: API.get_user

.. automethod:: API.create_friendship

.. automethod:: API.destroy_friendship

.. automethod:: API.update_friendship

Manage account settings and profile
-----------------------------------

.. automethod:: API.get_settings

.. automethod:: API.verify_credentials

.. automethod:: API.get_saved_searches

.. automethod:: API.get_saved_search

.. automethod:: API.get_profile_banner

.. automethod:: API.remove_profile_banner

.. automethod:: API.set_settings

.. automethod:: API.update_profile

.. automethod:: API.update_profile_banner

.. automethod:: API.update_profile_image

.. automethod:: API.create_saved_search

.. automethod:: API.destroy_saved_search

Mute, block, and report users
-----------------------------

.. automethod:: API.get_blocked_ids

.. automethod:: API.get_blocks

.. automethod:: API.get_muted_ids

.. automethod:: API.get_mutes

.. automethod:: API.create_block

.. automethod:: API.destroy_block

.. automethod:: API.create_mute

.. automethod:: API.destroy_mute

.. automethod:: API.report_spam

Direct Messages
===============

Sending and receiving events
----------------------------

.. automethod:: API.delete_direct_message

.. automethod:: API.get_direct_messages

.. automethod:: API.get_direct_message

.. automethod:: API.send_direct_message

Typing indicator and read receipts
----------------------------------

.. automethod:: API.indicate_direct_message_typing

.. automethod:: API.mark_direct_message_read

Media
=====

Upload media
------------

.. automethod:: API.get_media_upload_status

.. automethod:: API.create_media_metadata

.. automethod:: API.media_upload

.. automethod:: API.simple_upload

.. automethod:: API.chunked_upload

.. automethod:: API.chunked_upload_append

.. automethod:: API.chunked_upload_finalize

.. automethod:: API.chunked_upload_init

Trends
======

Get locations with trending topics
----------------------------------

.. automethod:: API.available_trends

.. automethod:: API.closest_trends

Get trends near a location
--------------------------

.. automethod:: API.get_place_trends

Geo
===

Get information about a place
-----------------------------

.. automethod:: API.geo_id

Get places near a location
--------------------------

.. automethod:: API.reverse_geocode

.. automethod:: API.search_geo

Developer utilities
===================

Get Twitter supported languages
-------------------------------

.. automethod:: API.supported_languages

Get app rate limit status
-------------------------

.. automethod:: API.rate_limit_status


.. rubric:: Footnotes

.. [#] https://web.archive.org/web/20170829051949/https://dev.twitter.com/rest/reference/get/search/tweets
.. [#] https://twittercommunity.com/t/favorited-reports-as-false-even-if-status-is-already-favorited-by-the-user/11145
