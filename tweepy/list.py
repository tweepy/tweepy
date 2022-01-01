# Tweepy
# Copyright 2009-2022 Joshua Roesslein
# See LICENSE for details.

from tweepy.mixins import DataMapping, HashableID
from tweepy.utils import parse_datetime


class List(HashableID, DataMapping):

    __slots__ = (
        "data", "id", "name", "created_at", "description", "follower_count",
        "member_count", "private", "owner_id"
    )

    def __init__(self, data):
        self.data = data
        self.id = data["id"]
        self.name = data["name"]

        self.created_at = data.get("created_at")
        if self.created_at is not None:
            self.created_at = parse_datetime(self.created_at)

        self.description = data.get("description")
        self.follower_count = data.get("follower_count")
        self.member_count = data.get("member_count")
        self.private = data.get("private")
        self.owner_id = data.get("owner_id")

    def __repr__(self):
        return f"<List id={self.id} name={self.name}>"

    def __str__(self):
        return self.name
