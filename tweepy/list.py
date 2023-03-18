# Tweepy
# Copyright 2009-2023 Joshua Roesslein
# See LICENSE for details.

from tweepy.mixins import DataMapping, HashableID
from tweepy.utils import parse_datetime


#: All the potential fields for :class:`List` objects
LIST_FIELDS = [
    "created_at",
    "description",
    "follower_count",
    "id",
    "member_count",
    "name",
    "owner_id",
    "private",
]


class List(HashableID, DataMapping):
    """The list object contains `Twitter Lists`_ metadata describing the
    referenced List. The List object is the primary object returned in the List
    lookup endpoint. When requesting additional List fields on this endpoint,
    simply use the fields parameter ``list.fields``.

    At the moment, the List object cannot be found as a child object from any
    other data object. However, user objects can be found and expanded in the
    user resource. These objects are available for expansion by adding
    ``owner_id`` to the ``expansions`` query parameter. Use the expansion with
    the field parameter: ``list.fields`` when requesting additional fields to
    complete the primary List object and ``user.fields`` to complete the
    expansion object.

    .. versionadded:: 4.4

    Attributes
    ----------
    data : dict
        The JSON data representing the List.
    id : str
        The unique identifier of this List.
    name : str
        The name of the List, as defined when creating the List.
    created_at : datetime.datetime | None
        The UTC datetime that the List was created on Twitter.
    description : str | None
        A brief description to let users know about the List.
    follower_count : int | None
        Shows how many users follow this List,
    member_count : int | None
        Shows how many members are part of this List.
    private : bool | None
        Indicates if the List is private.
    owner_id : str | None
        Unique identifier of this List's owner.

    References
    ----------
    https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/lists

    .. _Twitter Lists: https://help.twitter.com/en/using-twitter/twitter-lists
    """

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
