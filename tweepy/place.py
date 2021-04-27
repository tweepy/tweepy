# Tweepy
# Copyright 2009-2021 Joshua Roesslein
# See LICENSE for details.

from tweepy.mixins import DataMapping, HashableID


class Place(HashableID, DataMapping):

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
