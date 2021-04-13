# Tweepy
# Copyright 2009-2021 Joshua Roesslein
# See LICENSE for details.

from math import inf


class Paginator:
    """:class:`Paginator` can be used to paginate for any :class:`Client`
    methods that support pagination

    Parameters
    ----------
    method
        :class:`Client` method to paginate for
    args
        Positional arguments to pass to ``method``
    kwargs
        Keyword arguments to pass to ``method``
    """

    def __init__(self, method, *args, **kwargs):
        self.method = method
        self.args = args
        self.kwargs = kwargs

    def __iter__(self):
        return PaginationIterator(self.method, *self.args, **self.kwargs)

    def __reversed__(self):
        return PaginationIterator(self.method, *self.args, reverse=True,
                                  **self.kwargs)

    def flatten(self, limit=inf):
        """Flatten paginated data

        Parameters
        ----------
        limit
            Maximum number of results to yield
        """
        if limit <= 0:
            return

        count = 0
        for response in PaginationIterator(self.method, *self.args,
                                           **self.kwargs):
            if response.data is not None:
                for data in response.data:
                    yield data
                    count += 1
                    if count == limit:
                        return


class PaginationIterator:

    def __init__(self, method, *args, limit=inf, pagination_token=None,
                 reverse=False, **kwargs):
        self.method = method
        self.args = args
        self.limit = limit
        self.kwargs = kwargs
        self.reverse = reverse

        if reverse:
            self.previous_token = pagination_token
            self.next_token = None
        else:
            self.previous_token = None
            self.next_token = pagination_token

        self.count = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.reverse:
            pagination_token = self.previous_token
        else:
            pagination_token = self.next_token

        if self.count >= self.limit or self.count and pagination_token is None:
            raise StopIteration

        # https://twittercommunity.com/t/why-does-timeline-use-pagination-token-while-search-uses-next-token/150963
        if self.method.__name__ in ("search_all_tweets",
                                    "search_recent_tweets"):
            self.kwargs["next_token"] = pagination_token
        else:
            self.kwargs["pagination_token"] = pagination_token

        response = self.method(*self.args, **self.kwargs)

        self.previous_token = response.meta.get("previous_token")
        self.next_token = response.meta.get("next_token")
        self.count += 1

        return response
