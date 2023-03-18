# Tweepy
# Copyright 2009-2023 Joshua Roesslein
# See LICENSE for details.

from tweepy.mixins import DataMapping, HashableID
from tweepy.utils import parse_datetime


#: All the potential publically-available fields for :class:`Space` objects
PUBLIC_SPACE_FIELDS = [
    "created_at",
    "creator_id",
    "ended_at",
    "host_ids",
    "id",
    "invited_user_ids",
    "is_ticketed",
    "lang",
    "participant_count",
    "scheduled_start",
    "speaker_ids",
    "started_at",
    "state",
    "title",
    "topic_ids",
    "updated_at",
]

#: All the potential fields for :class:`Space` objects
SPACE_FIELDS = PUBLIC_SPACE_FIELDS + [
    "subscriber_count",
]


class Space(HashableID, DataMapping):
    """Spaces allow expression and interaction via live audio conversations.
    The Space data dictionary contains relevant metadata about a Space; all the
    details are updated in real time.

    User objects can found and expanded in the user resource. These objects are
    available for expansion by adding at least one of ``host_ids``,
    ``creator_id``, ``speaker_ids``, ``mentioned_user_ids`` to the
    ``expansions`` query parameter.

    Unlike Tweets, Spaces are ephemeral and become unavailable after they end
    or when they are canceled by their creator. When your app handles Spaces
    data, you are responsible for returning the most up-to-date information,
    and must remove data that is no longer available from the platform. The
    `Spaces lookup endpoints`_ can help you ensure you respect the users’
    expectations and intent.

    .. versionadded:: 4.1

    .. versionchanged:: 4.4
        Added ``ended_at`` and ``topic_ids`` fields

    .. versionchanged:: 4.6
        Added ``subscriber_count`` field

    .. versionchanged:: 4.14
        Added ``creator_id`` field

    Attributes
    ----------
    data : dict
        The JSON data representing the Space.
    id : str
        The unique identifier of the requested Space.
    state : str
        Indicates if the Space has started or will start in the future, or if
        it has ended.
    created_at : datetime.datetime | None
        Creation time of this Space.
    ended_at : datetime.datetime | None
        Time when the Space was ended. Only available for ended Spaces. 
    host_ids : list
        The unique identifier of the users who are hosting this Space.
    lang : str | None
        Language of the Space, if detected by Twitter. Returned as a BCP47
        language tag.
    is_ticketed : bool | None
        Indicates is this is a ticketed Space.
    invited_user_ids : list
        The list of user IDs that were invited to join as speakers. Usually,
        users in this list are invited to speak via the Invite user option.
    participant_count : int | None
        The current number of users in the Space, including Hosts and Speakers.
    subscriber_count : int | None
        The number of people who set a reminder to a Space.
    scheduled_start : datetime.datetime | None
        Indicates the start time of a scheduled Space, as set by the creator of
        the Space. This field is returned only if the Space has been scheduled;
        in other words, if the field is returned, it means the Space is a
        scheduled Space.
    speaker_ids : list
        The list of users who were speaking at any point during the Space. This
        list contains all the users in ``invited_user_ids`` in addition to any
        user who requested to speak and was allowed via the Add speaker option.
    started_at : datetime.datetime | None
        Indicates the actual start time of a Space.
    title : str | None
        The title of the Space as specified by the creator.
    topic_ids : list
        A list of IDs of the topics selected by the creator of the Space.
    updated_at : datetime.datetime | None
        Specifies the date and time of the last update to any of the Space's
        metadata, such as its title or scheduled time.
    creator_id : int | None

    References
    ----------
    https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/space

    .. _Spaces lookup endpoints: https://developer.twitter.com/en/docs/twitter-api/spaces/lookup/introduction
    """

    __slots__ = (
        "data", "id", "state", "created_at", "ended_at", "host_ids", "lang",
        "is_ticketed", "invited_user_ids", "participant_count",
        "subscriber_count", "scheduled_start", "speaker_ids", "started_at",
        "title", "topic_ids", "updated_at", "creator_id"
    )

    def __init__(self, data):
        self.data = data
        self.id = data["id"]
        self.state = data["state"]

        self.created_at = data.get("created_at")
        if self.created_at is not None:
            self.created_at = parse_datetime(self.created_at)

        self.ended_at = data.get("ended_at")
        if self.ended_at is not None:
            self.ended_at = parse_datetime(self.ended_at)

        self.host_ids = data.get("host_ids", [])
        self.lang = data.get("lang")
        self.is_ticketed = data.get("is_ticketed")
        self.invited_user_ids = data.get("invited_user_ids", [])
        self.participant_count = data.get("participant_count")
        self.subscriber_count = data.get("subscriber_count")

        self.scheduled_start = data.get("scheduled_start")
        if self.scheduled_start is not None:
            self.scheduled_start = parse_datetime(self.scheduled_start)

        self.speaker_ids = data.get("speaker_ids", [])

        self.started_at = data.get("started_at")
        if self.started_at is not None:
            self.started_at = parse_datetime(self.started_at)

        self.title = data.get("title")

        self.topic_ids = data.get("topic_ids", [])

        self.updated_at = data.get("updated_at")
        if self.updated_at is not None:
            self.updated_at = parse_datetime(self.updated_at)

        self.creator_id = data.get("creator_id")
        if self.creator_id is not None:
            self.creator_id = int(self.creator_id)

    def __repr__(self):
        return f"<Space id={self.id} state={self.state}>"
