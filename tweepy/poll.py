# Tweepy
# Copyright 2009-2022 Joshua Roesslein
# See LICENSE for details.

from tweepy.mixins import DataMapping, HashableID
from tweepy.utils import parse_datetime


class Poll(HashableID, DataMapping):
    """A poll included in a Tweet is not a primary object on any endpoint, but
    can be found and expanded in the Tweet object. 

    The object is available for expansion with
    ``?expansions=attachments.poll_ids`` to get the condensed object with only
    default fields. Use the expansion with the field parameter: ``poll.fields``
    when requesting additional fields to complete the object.

    .. versionadded:: 4.0

    Attributes
    ----------
    data : dict
        The JSON data representing the poll.
    id : str
        Unique identifier of the expanded poll.
    options : list
        Contains objects describing each choice in the referenced poll.
    duration_minutes : int | None
        Specifies the total duration of this poll.
    end_datetime : datetime.datetime | None
        Specifies the end date and time for this poll.
    voting_status : str | None
        Indicates if this poll is still active and can receive votes, or if the
        voting is now closed.

    References
    ----------
    https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/poll
    """

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
            self.end_datetime = parse_datetime(self.end_datetime)

        self.voting_status = data.get("voting_status")

    def __iter__(self):
        return iter(self.options)

    def __len__(self):
        return len(self.options)

    def __repr__(self):
        return f"<Poll id={self.id} options={self.options}>"
