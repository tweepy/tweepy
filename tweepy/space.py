# Tweepy
# Copyright 2009-2021 Joshua Roesslein
# See LICENSE for details.

import datetime

from tweepy.mixins import DataMapping, HashableID


class Space(HashableID, DataMapping):

    __slots__ = (
        "data", "id", "state", "created_at", "host_ids", "lang", "is_ticketed",
        "invited_user_ids", "participant_count", "scheduled_start",
        "speaker_ids", "started_at", "title", "updated_at"
    )

    def __init__(self, data):
        self.data = data
        self.id = data["id"]
        self.state = data["state"]

        self.created_at = data.get("created_at")
        if self.created_at is not None:
            self.created_at = datetime.datetime.strptime(
                self.created_at, "%Y-%m-%dT%H:%M:%S.%f%z"
            )

        self.host_ids = data.get("host_ids", [])
        self.lang = data.get("lang")
        self.is_ticketed = data.get("is_ticketed")
        self.invited_user_ids = data.get("invited_user_ids", [])
        self.participant_count = data.get("participant_count")

        self.scheduled_start = data.get("scheduled_start")
        if self.scheduled_start is not None:
            self.scheduled_start = datetime.datetime.strptime(
                self.scheduled_start, "%Y-%m-%dT%H:%M:%S.%f%z"
            )

        self.speaker_ids = data.get("speaker_ids", [])

        self.started_at = data.get("started_at")
        if self.started_at is not None:
            self.started_at = datetime.datetime.strptime(
                self.started_at, "%Y-%m-%dT%H:%M:%S.%f%z"
            )

        self.title = data.get("title")

        self.updated_at = data.get("updated_at")
        if self.updated_at is not None:
            self.updated_at = datetime.datetime.strptime(
                self.updated_at, "%Y-%m-%dT%H:%M:%S.%f%z"
            )

    def __repr__(self):
        return f"<Space id={self.id} state={self.state}>"

    def __str__(self):
        return self.full_name
