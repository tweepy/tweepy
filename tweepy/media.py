# Tweepy
# Copyright 2009-2022 Joshua Roesslein
# See LICENSE for details.

from tweepy.mixins import DataMapping


class Media(DataMapping):
    """Media refers to any image, GIF, or video attached to a Tweet. The media
    object is not a primary object on any endpoint, but can be found and
    expanded in the Tweet object. 

    The object is available for expansion with
    ``?expansions=attachments.media_keys`` to get the condensed object with
    only default fields. Use the expansion with the field parameter:
    ``media.fields`` when requesting additional fields to complete the object..

    .. versionadded:: 4.0

    .. versionchanged:: 4.5
        Added ``url`` field

    .. versionchanged:: 4.12
        Added ``variants`` field

    Attributes
    ----------
    data : dict
        The JSON data representing the media.
    media_key : str
        Unique identifier of the expanded media content.
    type : str
        Type of content (animated_gif, photo, video).
    url : str | None
        A direct URL to the media file on Twitter.
    duration_ms : int | None
        Available when type is video. Duration in milliseconds of the video.
    height : int | None
        Height of this content in pixels.
    non_public_metrics : dict | None
        Non-public engagement metrics for the media content at the time of the
        request. 

        Requires user context authentication.
    organic_metrics: dict | None
        Engagement metrics for the media content, tracked in an organic
        context, at the time of the request. 

        Requires user context authentication.
    preview_image_url : str | None
        URL to the static placeholder preview of this content.
    promoted_metrics : dict | None
        Engagement metrics for the media content, tracked in a promoted
        context, at the time of the request. 

        Requires user context authentication.
    public_metrics : dict | None
        Public engagement metrics for the media content at the time of the
        request.
    width : int | None
        Width of this content in pixels.
    alt_text : str | None
        A description of an image to enable and support accessibility. Can be
        up to 1000 characters long. Alt text can only be added to images at the
        moment.
    variants: list[dict] | None
        Each media object may have multiple display or playback variants,
        with different resolutions or formats

    References
    ----------
    https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/media
    """

    __slots__ = (
        "data", "media_key", "url", "type", "duration_ms", "height",
        "non_public_metrics", "organic_metrics", "preview_image_url",
        "promoted_metrics", "public_metrics", "width", "alt_text",
        "variants"
    )

    def __init__(self, data):
        self.data = data
        self.media_key = data["media_key"]
        self.type = data["type"]

        self.url = data.get("url")
        self.duration_ms = data.get("duration_ms")
        self.height = data.get("height")
        self.non_public_metrics = data.get("non_public_metrics")
        self.organic_metrics = data.get("organic_metrics")
        self.preview_image_url = data.get("preview_image_url")
        self.promoted_metrics = data.get("promoted_metrics")
        self.public_metrics = data.get("public_metrics")
        self.width = data.get("width")
        self.alt_text = data.get("alt_text")
        self.variants = data.get("variants")

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.media_key == other.media_key

        return NotImplemented

    def __hash__(self):
        return hash(self.media_key)

    def __repr__(self):
        return f"<Media media_key={self.media_key} type={self.type}>"
