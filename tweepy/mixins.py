# Tweepy
# Copyright 2009-2023 Joshua Roesslein
# See LICENSE for details.

from collections.abc import Mapping


class EqualityComparableID:
    __slots__ = ()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id == other.id

        return NotImplemented


class HashableID(EqualityComparableID):
    __slots__ = ()

    def __hash__(self):
        return self.id


class DataMapping(Mapping):
    __slots__ = ()

    def __contains__(self, item):
        data = DataMapping.__getattribute__(self, "data")
        return item in data

    def __getattr__(self, name):
        data = DataMapping.__getattribute__(self, "data")
        if name == "data":
            return data
        try:
            return data[name]
        except KeyError:
            raise AttributeError from None

    def __getitem__(self, key):
        try:
            return DataMapping.__getattribute__(self, key)
        except AttributeError:
            raise KeyError from None
    
    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)
