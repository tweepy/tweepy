.. _expansions_and_fields:

Expansions and Fields
=====================

.. _expansions_parameter:

``expansions``
--------------
`Expansions`_ enable you to request additional data objects that relate to the
originally returned List, Space, Tweets, or users. Submit a list of desired
expansions in a comma-separated list without spaces. The ID that represents the
expanded data object will be included directly in the List, Space, Tweet, or
user data object, but the expanded object metadata will be returned within the
``includes`` response object, and will also include the ID so that you can
match this data object to the original Space, Tweet, or user object.

At this time, the only expansion available to endpoints that primarily return
List objects is ``expansions=owner_id``. You will find the expanded user data
object living in the ``includes`` response object.

For methods that return Spaces, the following data objects can be expanded
using this parameter:

* The Spaces creator's user object
* The user objects of any Space co-host
* Any mentioned users’ object
* Any speaker's user object

For methods that return Tweets, the following data objects can be expanded
using this parameter:

* The Tweet author's user object
* The user object of the Tweet’s author that the
  original Tweet is responding to
* Any mentioned users’ object
* Any referenced Tweets’ author’s user object
* Attached media’s object
* Attached poll’s object
* Attached place’s object
* Any referenced Tweets’ object

At this time, the only expansion available to endpoints that primarily return
user objects is ``expansions=pinned_tweet_id``. You will find the expanded
Tweet data object living in the ``includes`` response object.

.. _list_fields_parameter:

``list_fields``
---------------
This `fields`_ parameter enables you to select which specific `List fields`_
will deliver with each returned List objects. Specify the desired fields in a
comma-separated list without spaces between commas and fields. These specified
List fields will display directly in the List data objects.

.. _media_fields_parameter:

``media_fields``
----------------
This `fields`_ parameter enables you to select which specific `media fields`_
will deliver in each returned Tweet. Specify the desired fields in a
comma-separated list without spaces between commas and fields. The Tweet will
only return media fields if the Tweet contains media and if you've also
included the ``expansions=attachments.media_keys`` query parameter in your
request. While the media ID will be located in the Tweet object, you will find
this ID and all additional media fields in the ``includes`` data object.

.. _place_fields_parameter:

``place_fields``
----------------
This `fields`_ parameter enables you to select which specific `place fields`_
will deliver in each returned Tweet. Specify the desired fields in a
comma-separated list without spaces between commas and fields. The Tweet will
only return place fields if the Tweet contains a place and if you've also
included the ``expansions=geo.place_id`` query parameter in your request. While
the place ID will be located in the Tweet object, you will find this ID and all
additional place fields in the ``includes`` data object.

.. _poll_fields_parameter:

``poll_fields``
---------------

This `fields`_ parameter enables you to select which specific `poll fields`_
will deliver in each returned Tweet. Specify the desired fields in a
comma-separated list without spaces between commas and fields. The Tweet will
only return poll fields if the Tweet contains a poll and if you've also
included the ``expansions=attachments.poll_ids`` query parameter in your
request. While the poll ID will be located in the Tweet object, you will find
this ID and all additional poll fields in the ``includes`` data object.

.. _space_fields_parameter:

``space_fields``
----------------

This `fields`_ parameter enables you to select which specific `Space fields`_
will deliver in each returned Space. Specify the desired fields in a
comma-separated list.

.. _tweet_fields_parameter:

``tweet_fields``
----------------

For methods that return Tweets, this `fields`_ parameter enables you to select
which specific `Tweet fields`_ will deliver in each returned Tweet object.
Specify the desired fields in a comma-separated list without spaces between
commas and fields. You can also pass the ``expansions=referenced_tweets.id``
expansion to return the specified fields for both the original Tweet and any
included referenced Tweets. The requested Tweet fields will display in both the
original Tweet data object, as well as in the referenced Tweet expanded data
object that will be located in the ``includes`` data object.

For methods that return users, this `fields`_ parameter enables you to select
which specific `Tweet fields`_ will deliver in each returned pinned Tweet.
Specify the desired fields in a comma-separated list without spaces between
commas and fields. The Tweet fields will only return if the user has a pinned
Tweet and if you've also included the ``expansions=pinned_tweet_id`` query
parameter in your request. While the referenced Tweet ID will be located in the
original Tweet object, you will find this ID and all additional Tweet fields in
the ``includes`` data object.

.. _user_fields_parameter:

``user_fields``
---------------

For methods that return Spaces or Tweets, this `fields`_ parameter enables you
to select which specific `user fields`_ will deliver in each returned Space or
Tweet. Specify the desired fields in a comma-separated list without spaces
between commas and fields. While the user ID will be located in the original
Tweet object, you will find this ID and all additional user fields in the
``includes`` data object.

You must also pass one of the user expansions to return the desired user
fields:

* ``expansions=author_id``
* ``expansions=entities.mentions.username``
* ``expansions=in_reply_to_user_id``
* ``expansions=referenced_tweets.id.author_id``

For methods that return users, this `fields`_ parameter enables you to select
which specific `user fields`_ will deliver with each returned users objects.
Specify the desired fields in a comma-separated list without spaces between
commas and fields. These specified user fields will display directly in the
user data objects.

.. _Expansions: https://developer.twitter.com/en/docs/twitter-api/expansions
.. _fields: https://developer.twitter.com/en/docs/twitter-api/fields
.. _list fields: https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/lists
.. _media fields: https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/media
.. _place fields: https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/place
.. _poll fields: https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/poll
.. _Space fields: https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/space
.. _Tweet fields: https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/tweet
.. _user fields: https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/user
