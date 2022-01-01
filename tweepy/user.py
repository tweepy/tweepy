# Tweepy
# Copyright 2009-2022 Joshua Roesslein
# See LICENSE for details.

from tweepy.mixins import DataMapping, HashableID
from tweepy.utils import parse_datetime


class User(HashableID, DataMapping):

    __slots__ = (
        "data", "id", "name", "username", "created_at", "description",
        "entities", "location", "pinned_tweet_id", "profile_image_url",
        "protected", "public_metrics", "url", "verified", "withheld"
    )

    def __init__(self, data):
        self.data = data
        self.id = int(data["id"])
        self.name = data["name"]
        self.username = data["username"]

        self.created_at = data.get("created_at")
        if self.created_at is not None:
            self.created_at = parse_datetime(self.created_at)

        self.description = data.get("description")
        self.entities = data.get("entities")
        self.location = data.get("location")

        self.pinned_tweet_id = data.get("pinned_tweet_id")
        if self.pinned_tweet_id is not None:
            self.pinned_tweet_id = int(self.pinned_tweet_id)

        self.profile_image_url = data.get("profile_image_url")
        self.protected = data.get("protected")
        self.public_metrics = data.get("public_metrics")
        self.url = data.get("url")
        self.verified = data.get("verified")
        self.withheld = data.get("withheld")

    def __repr__(self):
        return f"<User id={self.id} name={self.name} username={self.username}>"

    def __str__(self):
        return self.username
