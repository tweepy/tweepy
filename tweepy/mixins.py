# Tweepy
# Copyright 2009-2021 Joshua Roesslein
# See LICENSE for details.

class EqualityComparable:
    __slots__ = ()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id == other.id

        return NotImplemented


class Hashable(EqualityComparable):
    __slots__ = ()

    def __hash__(self):
        return self.id
