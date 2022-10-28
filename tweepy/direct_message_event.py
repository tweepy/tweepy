# Tweepy
# Copyright 2009-2022 Joshua Roesslein
# See LICENSE for details.

from tweepy.mixins import DataMapping, HashableID
from tweepy.tweet import ReferencedTweet
from tweepy.utils import parse_datetime


class DirectMessageEvent(HashableID, DataMapping):
    """.. versionadded:: 4.12

    Attributes
    ----------
    data : dict
        The JSON data representing the Direct Message event.
    id : int
    event_type : str
    attachments : dict | None
    created_at : datetime.datetime | None
    dm_conversation_id : str | None
    participant_ids : list[int] | None
    referenced_tweets : list[ReferencedTweet] | None
    sender_id : int | None
    text : str | None
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

        self.attachments = data.get("attachments")

        self.created_at = data.get("created_at")
        if self.created_at is not None:
            self.created_at = parse_datetime(self.created_at)

        self.dm_conversation_id = data.get("dm_conversation_id")

        self.participant_ids = data.get("participant_ids")
        if self.participant_ids is not None:
            self.participant_ids = list(map(int, self.participant_ids))

        self.referenced_tweets = data.get("referenced_tweets")
        if self.referenced_tweets is not None:
            self.referenced_tweets = [
                ReferencedTweet(referenced_tweet)
                for referenced_tweet in self.referenced_tweets
            ]

        self.sender_id = data.get("sender_id")
        if self.sender_id is not None:
            self.sender_id = int(self.sender_id)

        self.text = data.get("text")

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
