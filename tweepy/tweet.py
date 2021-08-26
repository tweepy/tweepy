# Tweepy
# Copyright 2009-2021 Joshua Roesslein
# See LICENSE for details.

import datetime

from tweepy.mixins import DataMapping, HashableID


class Tweet(HashableID, DataMapping):

    __slots__ = (
        "data", "id", "text", "attachments", "author_id",
        "context_annotations", "conversation_id", "created_at", "entities",
        "geo", "in_reply_to_user_id", "lang", "non_public_metrics",
        "organic_metrics", "possibly_sensitive", "promoted_metrics",
        "public_metrics", "referenced_tweets", "reply_settings", "source",
        "withheld"
    )

    def __init__(self, data):
        self.data = data
        self.id = int(data["id"])
        self.text = data["text"]

        self.attachments = data.get("attachments")

        self.author_id = data.get("author_id")
        if self.author_id is not None:
            self.author_id = int(self.author_id)

        self.context_annotations = data.get("context_annotations", [])

        self.conversation_id = data.get("conversation_id")
        if self.conversation_id is not None:
            self.conversation_id = int(self.conversation_id)

        self.created_at = data.get("created_at")
        if self.created_at is not None:
            self.created_at = datetime.datetime.strptime(
                self.created_at, "%Y-%m-%dT%H:%M:%S.%f%z"
            )

        self.entities = data.get("entities")
        self.geo = data.get("geo")

        self.in_reply_to_user_id = data.get("in_reply_to_user_id")
        if self.in_reply_to_user_id is not None:
            self.in_reply_to_user_id = int(self.in_reply_to_user_id)

        self.lang = data.get("lang")
        self.non_public_metrics = data.get("non_public_metrics")
        self.organic_metrics = data.get("organic_metrics")
        self.possibly_sensitive = data.get("possibly_sensitive")
        self.promoted_metrics = data.get("promoted_metrics")
        self.public_metrics = data.get("public_metrics")

        self.referenced_tweets = None
        if "referenced_tweets" in data:
            self.referenced_tweets = [
                ReferencedTweet(referenced_tweet)
                for referenced_tweet in data["referenced_tweets"]
            ]

        self.reply_settings = data.get("reply_settings")
        self.source = data.get("source")
        self.withheld = data.get("withheld")

    def __len__(self):
        return len(self.text)

    def __repr__(self):
        return f"<Tweet id={self.id} text={self.text}>"

    def __str__(self):
        return self.text


class ReferencedTweet(HashableID, DataMapping):

    __slots__ = ("data", "id", "type")

    def __init__(self, data):
        self.data = data
        self.id = int(data["id"])
        self.type = data["type"]

    def __repr__(self):
        return f"<ReferencedTweet id={self.id} type={self.type}"
