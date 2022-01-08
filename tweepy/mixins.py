# Tweepy
# Copyright 2009-2022 Joshua Roesslein
# See LICENSE for details.

# pytype: skip-file

from collections.abc import Mapping


class EqualityComparableID:
    __slots__ = ()

    def __eq__(self, other: "EqualityComparableID"):
        if isinstance(other, self.__class__):
            return self.id == other.id

        return NotImplemented


class HashableID(EqualityComparableID):
    __slots__ = ()

    def __hash__(self):
        return self.id


class DataMapping(Mapping):
    __slots__ = ()

    def __getattr__(self, name: str):
        try:
            return self.data[name]
        except KeyError:
            raise AttributeError from None

    def __getitem__(self, key: str):
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError from None
    
    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)
