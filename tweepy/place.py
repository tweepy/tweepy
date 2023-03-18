# Tweepy
# Copyright 2009-2023 Joshua Roesslein
# See LICENSE for details.

from tweepy.mixins import DataMapping, HashableID


#: All the potential fields for :class:`Place` objects
PLACE_FIELDS = [
    "contained_within",
    "country",
    "country_code",
    "full_name",
    "geo",
    "id",
    "name",
    "place_type",
]


class Place(HashableID, DataMapping):
    """The place tagged in a Tweet is not a primary object on any endpoint, but
    can be found and expanded in the Tweet resource. 

    The object is available for expansion with ``?expansions=geo.place_id`` to
    get the condensed object with only default fields. Use the expansion with
    the field parameter: ``place.fields`` when requesting additional fields to
    complete the object.

    .. versionadded:: 4.0

    Attributes
    ----------
    data : dict
        The JSON data representing the place.
    full_name : str
        A longer-form detailed place name.
    id : str
        The unique identifier of the expanded place, if this is a point of
        interest tagged in the Tweet.
    contained_within : list
        Returns the identifiers of known places that contain the referenced
        place.
    country : str | None
        The full-length name of the country this place belongs to.
    country_code : str | None
        The ISO Alpha-2 country code this place belongs to.
    geo : dict | None
        Contains place details in GeoJSON format.
    name : str | None
        The short name of this place.
    place_type : str | None
        Specified the particular type of information represented by this place
        information, such as a city name, or a point of interest.

    References
    ----------
    https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/place
    """

    __slots__ = (
        "data", "full_name", "id", "contained_within", "country",
        "country_code", "geo", "name", "place_type"
    )

    def __init__(self, data):
        self.data = data
        self.full_name = data["full_name"]
        self.id = data["id"]

        self.contained_within = data.get("contained_within", [])
        self.country = data.get("country")
        self.country_code = data.get("country_code")
        self.geo = data.get("geo")
        self.name = data.get("name")
        self.place_type = data.get("place_type")

    def __repr__(self):
        return f"<Place id={self.id} full_name={self.full_name}>"

    def __str__(self):
        return self.full_name
