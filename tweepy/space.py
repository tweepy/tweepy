# Tweepy
# Copyright 2009-2021 Joshua Roesslein
# See LICENSE for details.

from tweepy.mixins import DataMapping, HashableID
from tweepy.utils import parse_datetime


class Space(HashableID, DataMapping):

    __slots__ = (
        "data", "id", "state", "created_at", "ended_at", "host_ids", "lang",
        "is_ticketed", "invited_user_ids", "participant_count",
        "scheduled_start", "speaker_ids", "started_at", "title", "topic_ids",
        "updated_at"
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

    def __repr__(self):
        return f"<Space id={self.id} state={self.state}>"
