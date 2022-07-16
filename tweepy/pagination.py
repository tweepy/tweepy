# Tweepy
# Copyright 2009-2022 Joshua Roesslein
# See LICENSE for details.
import time
from math import inf


class Paginator:
    """:class:`Paginator` can be used to paginate for any :class:`Client`
    methods that support pagination

    .. versionadded:: 4.0

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
        t0: float = time.time()

        if self.reverse:
            pagination_token = self.previous_token
        else:
            pagination_token = self.next_token

        if self.count >= self.limit or self.count and pagination_token is None:
            raise StopIteration

        # https://twittercommunity.com/t/why-does-timeline-use-pagination-token-while-search-uses-next-token/150963
        if self.method.__name__ in (
                "search_all_tweets",
                "search_recent_tweets",
                "get_all_tweets_count"
        ):
            self.kwargs["next_token"] = pagination_token
        else:
            self.kwargs["pagination_token"] = pagination_token

        response = self.method(*self.args, **self.kwargs)

        self.previous_token = response.meta.get("previous_token")
        self.next_token = response.meta.get("next_token")
        self.count += 1

        if self.method.__name__ == "search_all_tweets" and self.method.__self__.bearer_token:
            # It is required by Twitter that one request per second is made during an archive search
            # with OAuth 2.0 Bearer Token. cf. https://developer.twitter.com/en/docs/twitter-api/tweets/search/migrate.
            # The minimum is 1 request per second, the maximum for optimal throughput is 300 requests per 900 seconds.
            time.sleep(1 - ((time.time() - t0) % 1))

        return response
