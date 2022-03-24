# Tweepy
# Copyright 2009-2022 Joshua Roesslein
# See LICENSE for details.

from tweepy.mixins import DataMapping, HashableID
from tweepy.utils import parse_datetime


class User(HashableID, DataMapping):
    """The user object contains Twitter user account metadata describing the
    referenced user. The user object is the primary object returned in the
    `users lookup`_ endpoint. When requesting additional user fields on this
    endpoint, simply use the fields parameter ``user.fields``.

    The user object can also be found as a child object and expanded in the
    Tweet object. The object is available for expansion with
    ``?expansions=author_id`` or ``?expansions=in_reply_to_user_id`` to get the
    condensed object with only default fields. Use the expansion with the field
    parameter: ``user.fields`` when requesting additional fields to complete
    the object.

    .. versionadded:: 4.0

    Attributes
    ----------
    data : dict
        The JSON data representing the user.
    id : int
        The unique identifier of this user.
    name : str
        The name of the user, as they’ve defined it on their profile. Not
        necessarily a person’s name. Typically capped at 50 characters, but
        subject to change.
    username : str
        The Twitter screen name, handle, or alias that this user identifies
        themselves with. Usernames are unique but subject to change. Typically
        a maximum of 15 characters long, but some historical accounts may exist
        with longer names.
    created_at : datetime.datetime | None
        The UTC datetime that the user account was created on Twitter.
    description : str | None
        The text of this user's profile description (also known as bio), if the
        user provided one.
    entities : dict | None
        Contains details about text that has a special meaning in the user's
        description.
    location : str | None
        The location specified in the user's profile, if the user provided one.
        As this is a freeform value, it may not indicate a valid location, but
        it may be fuzzily evaluated when performing searches with location
        queries.
    pinned_tweet_id : int | None
        Unique identifier of this user's pinned Tweet.
    profile_image_url : str | None
        The URL to the profile image for this user, as shown on the user's
        profile.
    protected : bool | None
        Indicates if this user has chosen to protect their Tweets (in other
        words, if this user's Tweets are private).
    public_metrics : dict | None
        Contains details about activity for this user.
    url : str | None
        The URL specified in the user's profile, if present.
    verified : bool | None
        Indicates if this user is a verified Twitter User.
    withheld : dict | None
        Contains withholding details for `withheld content`_, if applicable.

    References
    ----------
    https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/user

    .. _users lookup: https://developer.twitter.com/en/docs/twitter-api/users/lookup/introduction.html
    .. _withheld content: https://help.twitter.com/en/rules-and-policies/tweet-withheld-by-country
    """

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
