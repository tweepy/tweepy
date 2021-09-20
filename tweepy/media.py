# Tweepy
# Copyright 2009-2021 Joshua Roesslein
# See LICENSE for details.

from tweepy.mixins import DataMapping


class Media(DataMapping):

    __slots__ = (
        "data", "media_key", "type", "duration_ms", "height",
        "non_public_metrics", "organic_metrics", "preview_image_url",
        "promoted_metrics", "public_metrics", "width", "alt_text"
    )

    def __init__(self, data):
        self.data = data
        self.media_key = data["media_key"]
        self.type = data["type"]

        self.duration_ms = data.get("duration_ms")
        self.height = data.get("height")
        self.non_public_metrics = data.get("non_public_metrics")
        self.organic_metrics = data.get("organic_metrics")
        self.preview_image_url = data.get("preview_image_url")
        self.promoted_metrics = data.get("promoted_metrics")
        self.public_metrics = data.get("public_metrics")
        self.width = data.get("width")
        self.alt_text = data.get("alt_text")

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.media_key == other.media_key

        return NotImplemented

    def __hash__(self):
        return hash(self.media_key)

    def __repr__(self):
        return f"<Media media_key={self.media_key} type={self.type}>"
