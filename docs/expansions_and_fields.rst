.. _expansions_and_fields:

*********************
Expansions and Fields
*********************

.. _expansions_parameter:

``expansions`` Parameter
========================
`Expansions`_ enable you to request additional data objects that relate to the
originally returned List, Space, Tweets, Users, or Direct Message conversation
events. Submit a list of desired expansions in a comma-separated list without
spaces. The ID(s) that represent(s) the expanded data object(s) will be
included directly in the List, Space, Tweet, user, or event data object, but
the expanded object metadata will be returned within the ``includes`` response
object, and will also include the ID so that you can match this data object to
the original Space, Tweet, User or Direct Message conversation event object.

Available expansions for Tweet payloads
---------------------------------------

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

.. table::
    :align: center

    +------------------------------------+-----------------------------------------------------------------------------------------------------+
    | Expansion                          | Description                                                                                         |
    +====================================+=====================================================================================================+
    | ``author_id``                      | Returns a user object representing the Tweet’s author                                               |
    +------------------------------------+-----------------------------------------------------------------------------------------------------+
    | ``referenced_tweets.id``           | Returns a Tweet object that this Tweet is referencing (either as a Retweet, Quoted Tweet, or reply) |
    +------------------------------------+-----------------------------------------------------------------------------------------------------+
    | ``edit_history_tweet_ids``         | Returns Tweet objects that are part of a Tweet's edit history                                       |
    +------------------------------------+-----------------------------------------------------------------------------------------------------+
    | ``in_reply_to_user_id``            | Returns a user object representing the Tweet author this requested Tweet is a reply of              |
    +------------------------------------+-----------------------------------------------------------------------------------------------------+
    | ``attachments.media_keys``         | Returns a media object representing the images, videos, GIFs included in the Tweet                  |
    +------------------------------------+-----------------------------------------------------------------------------------------------------+
    | ``attachments.poll_ids``           | Returns a poll object containing metadata for the poll included in the Tweet                        |
    +------------------------------------+-----------------------------------------------------------------------------------------------------+
    | ``geo.place_id``                   | Returns a place object containing metadata for the location tagged in the Tweet                     |
    +------------------------------------+-----------------------------------------------------------------------------------------------------+
    | ``entities.mentions.username``     | Returns a user object for the user mentioned in the Tweet                                           |
    +------------------------------------+-----------------------------------------------------------------------------------------------------+
    | ``referenced_tweets.id.author_id`` | Returns a user object for the author of the referenced Tweet                                        |
    +------------------------------------+-----------------------------------------------------------------------------------------------------+

Available expansion for User payloads
-------------------------------------

At this time, the only expansion available to endpoints that primarily return
user objects is ``expansions=pinned_tweet_id``. You will find the expanded
Tweet data object living in the ``includes`` response object.

.. table::
    :align: center

    +---------------------+---------------------------------------------------------------------------------------+
    | Expansion           | Description                                                                           |
    +=====================+=======================================================================================+
    | ``pinned_tweet_id`` | Returns a Tweet object representing the Tweet pinned to the top of the user’s profile |
    +---------------------+---------------------------------------------------------------------------------------+

Available expansions for Direct Message event payloads
------------------------------------------------------

For methods that returns Direct Message conversation events, the following data
objects can be expanded using this parameter:

* The user object for the message sender.
* Attached media's object.
* Any referenced Tweet's object.
* The user object for who is joining or leaving group conversations.

.. table::
    :align: center

    +----------------------------+------------------------------------------------------------------------------------------------------------------------+
    | Expansion                  | Description                                                                                                            |
    +============================+========================================================================================================================+
    | ``attachments.media_keys`` | Returns a Media object that was attached to a Direct Message                                                           |
    +----------------------------+------------------------------------------------------------------------------------------------------------------------+
    | ``referenced_tweets.id``   | Returns a Tweet object that was referenced in a Direct Message                                                         |
    +----------------------------+------------------------------------------------------------------------------------------------------------------------+
    | ``sender_id``              | Returns a User object representing the author of a Direct Message and who invited a participant to join a conversation |
    +----------------------------+------------------------------------------------------------------------------------------------------------------------+
    | ``participant_ids``        | Returns a User object representing a participant that joined or left a conversation                                    |
    +----------------------------+------------------------------------------------------------------------------------------------------------------------+

Available expansions for Spaces payloads
----------------------------------------

For methods that return Spaces, the following data objects can be expanded
using this parameter:

* The Spaces creator's user object
* The user objects of any Space co-host
* Any mentioned users’ object
* Any speaker's user object

.. table::
    :align: center

    +----------------------+----------------------------------------------------------------------+
    | Expansion            | Description                                                          |
    +======================+======================================================================+
    | ``invited_user_ids`` | Returns User objects representing what accounts were invited         |
    +----------------------+----------------------------------------------------------------------+
    | ``speaker_ids``      | Returns User objects representing what accounts spoke during a Space |
    +----------------------+----------------------------------------------------------------------+
    | ``creator_id``       | Returns a User object representing what account created the Space    |
    +----------------------+----------------------------------------------------------------------+
    | ``host_ids``         | Returns User objects representing what accounts were set up as hosts |
    +----------------------+----------------------------------------------------------------------+
    | ``topics_ids``       | Returns topic descriptions that were set up by the creator           |
    +----------------------+----------------------------------------------------------------------+

Available expansion for Lists payloads
--------------------------------------

At this time, the only expansion available to endpoints that primarily return
List objects is ``expansions=owner_id``. You will find the expanded user data
object living in the ``includes`` response object.

.. table::
    :align: center

    +--------------+--------------------------------------------------------------------------------+
    | Expansion    | Description                                                                    |
    +==============+================================================================================+
    | ``owner_id`` | Returns a User object representing what account created and maintains the List |
    +--------------+--------------------------------------------------------------------------------+

`Fields`_ Parameters
====================

.. _dm_event_fields_parameter:

``dm_event_fields``
-------------------

Extra fields to include in the event payload. ``id`` and ``event_type`` are
returned by default. The ``text`` value isn't included for ``ParticipantsJoin``
and ``ParticipantsLeave`` events.

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

Constants
=========

These constants are available directly in the :mod:`tweepy` module, which means
each file itself does not need to be imported. For example,
:const:`tweepy.user.USER_FIELDS` is available as :const:`tweepy.USER_FIELDS`.

.. autodata:: tweepy.direct_message_event.DIRECT_MESSAGE_EVENT_FIELDS

.. autodata:: tweepy.direct_message_event.DM_EVENT_FIELDS

.. autodata:: tweepy.list.LIST_FIELDS

.. autodata:: tweepy.media.MEDIA_FIELDS

.. autodata:: tweepy.place.PLACE_FIELDS

.. autodata:: tweepy.poll.POLL_FIELDS

.. autodata:: tweepy.space.PUBLIC_SPACE_FIELDS

.. autodata:: tweepy.space.SPACE_FIELDS

.. autodata:: tweepy.tweet.PUBLIC_TWEET_FIELDS

.. autodata:: tweepy.tweet.TWEET_FIELDS

.. autodata:: tweepy.user.USER_FIELDS
