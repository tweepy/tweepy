# Tweepy
# Copyright 2009-2021 Joshua Roesslein
# See LICENSE for details.

import datetime

from tweepy.mixins import DataMapping, HashableID


class Poll(HashableID, DataMapping):

    __slots__ = (
        "data", "id", "options", "duration_minutes", "end_datetime",
        "voting_status"
    )

    def __init__(self, data):
        self.data = data
        self.id = data["id"]
        self.options = data["options"]

        self.duration_minutes = data.get("duration_minutes")

        self.end_datetime = data.get("end_datetime")
        if self.end_datetime is not None:
            self.end_datetime = datetime.datetime.strptime(
                self.end_datetime, "%Y-%m-%dT%H:%M:%S.%f%z"
            )
        
        self.voting_status = data.get("voting_status")

    def __iter__(self):
        return iter(self.options)

    def __len__(self):
        return len(self.options)

    def __repr__(self):
        return f"<Poll id={self.id} options={self.options}>"
