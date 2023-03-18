# Tweepy
# Copyright 2009-2023 Joshua Roesslein
# See LICENSE for details.

from tweepy.mixins import DataMapping, HashableID
from tweepy.tweet import ReferencedTweet
from tweepy.utils import parse_datetime


#: All the potential fields for :class:`DirectMessageEvent` objects
DIRECT_MESSAGE_EVENT_FIELDS = [
    "attachments",
    "created_at",
    "dm_conversation_id",
    "event_type",
    "id",
    "participant_ids",
    "referenced_tweets",
    "sender_id",
    "text",
]
#: Alias for :const:`DIRECT_MESSAGE_EVENT_FIELDS`
DM_EVENT_FIELDS = DIRECT_MESSAGE_EVENT_FIELDS


class DirectMessageEvent(HashableID, DataMapping):
    """Direct Message (DM) conversations are made up of events. The Twitter API
    v2 currently supports three event types: MessageCreate, ParticipantsJoin,
    and ParticipantsLeave.

    DM event objects are returned by the `Direct Message lookup`_ endpoints,
    and a MessageCreate event is created when Direct Messages are successfully
    created with the `Manage Direct Messages`_ endpoints.

    When requesting DM events, there are three default event object attributes,
    or fields, included: ``id``, ``event_type``, and ``text``. To receive
    additional event `fields`_, use the fields parameter ``dm_event.fields`` to
    select others. Other available event fields include the following:
    ``dm_conversation_id``, ``created_at``, ``sender_id`, ``attachments``,
    ``participant_ids``, and ``referenced_tweets``.

    Several of these fields provide the IDs of other Twitter objects related to
    the Direct Message event:

    * ``sender_id`` - The ID of the account that sent the message, or who
      invited a participant to a group conversation
    * ``partricipants_ids`` - An array of account IDs. For ParticipantsJoin and
      ParticipantsLeave events this array will contain a single ID of the
      account that created the event
    * ``attachments`` - Provides media IDs for content that has been uploaded
      to Twitter by the sender
    * ``referenced_tweets`` - If a Tweet URL is found in the text field, the ID
      of that Tweet is included in the response

    The ``sender_id``, ``participant_ids``, ``referenced_tweets.id``, and
    ``attachments.media_keys`` `expansions`_ are available to expand on these
    Twitter object IDs.

    .. versionadded:: 4.12

    Attributes
    ----------
    data : dict
        The JSON data representing the Direct Message event.
    id : int
        The unique identifier of the event.
    event_type : str
        Describes the type of event. Three types are currently supported:

        * MessageCreate
        * ParticipantsJoin
        * ParticipantsLeave
    text : str | None
        The actual UTF-8 text of the Direct Message. 
    sender_id : int | None
        ID of the User creating the event. To expand this object in the
        response, include ``sender_id`` as an expansion and use the
        ``user.fields`` query parameter to specify User object attributes of
        interest.
    participant_ids : list[int] | None
        IDs of the participants joining and leaving a group conversation. Also
        used when creating new group conversations. To expand this object in
        the response, include ``participant_ids`` as an expansion and use the
        ``user.fields`` query parameter to specify User object attributes of
        interest.
    dm_conversation_id : str | None
        The unique identifier of the conversation the event is apart of.
    created_at : datetime.datetime | None
        Creation time (UTC) of the Tweet.
    referenced_tweets : list[ReferencedTweet] | None
        ID for any Tweet mentioned in the Direct Message text. To expand this
        object in the response, include ``referenced_tweets.id`` as an
        expansion and use the ``tweet.fields`` query parameter to specify Tweet
        object attributes of interest.
    attachments : dict | None
        For Direct Messages with attached Media, provides the media key of the
        uploaded content (photo, video, or GIF. To expand this object in the
        response, include ``attachments.media_keys`` as an expansion and use
        the ``media.fields`` query parameter to specify media object attributes
        of interest. Currently, one attachment is supported. 

    References
    ----------
    https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/dm-events

    .. _Direct Message lookup: https://developer.twitter.com/en/docs/twitter-api/direct-messages/lookup/introduction
    .. _Manage Direct Messages: https://developer.twitter.com/en/docs/twitter-api/direct-messages/manage/introduction
    .. _fields: https://developer.twitter.com/en/docs/twitter-api/fields
    .. _expansions: https://developer.twitter.com/en/docs/twitter-api/expansions
    """

    __slots__ = (
        "data", "id", "event_type", "attachments", "created_at",
        "dm_conversation_id", "participant_ids", "referenced_tweets",
        "sender_id", "text"
    )

    def __init__(self, data):
        self.data = data
        self.id = int(data["id"])
        self.event_type = data["event_type"]

        self.text = data.get("text")

        self.sender_id = data.get("sender_id")
        if self.sender_id is not None:
            self.sender_id = int(self.sender_id)

        self.participant_ids = data.get("participant_ids")
        if self.participant_ids is not None:
            self.participant_ids = list(map(int, self.participant_ids))

        self.dm_conversation_id = data.get("dm_conversation_id")

        self.created_at = data.get("created_at")
        if self.created_at is not None:
            self.created_at = parse_datetime(self.created_at)

        self.referenced_tweets = data.get("referenced_tweets")
        if self.referenced_tweets is not None:
            self.referenced_tweets = [
                ReferencedTweet(referenced_tweet)
                for referenced_tweet in self.referenced_tweets
            ]

        self.attachments = data.get("attachments")

    def __repr__(self):
        representation = (
            f"<Direct Message Event id={self.id} event_type={self.event_type}"
        )
        if self.text is not None:
            representation += f" text={repr(self.text)}"
        representation += '>'
        return representation

    def __str__(self):
        return self.text or self.__repr__()
