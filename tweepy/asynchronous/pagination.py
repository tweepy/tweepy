# Tweepy
# Copyright 2009-2022 Joshua Roesslein
# See LICENSE for details.

from math import inf

import aiohttp

from tweepy.client import Response


class AsyncPaginator:
    """AsyncPaginator( \
        self, method, *args, limit=inf, pagination_token=None, **kwargs \
    )

    :class:`AsyncPaginator` can be used to paginate for any
    :class:`AsyncClient` methods that support pagination

    .. note::

        When the returned response from the method being passed is of type
        :class:`aiohttp.ClientResponse`, it will be deserialized in order to
        parse the pagination tokens, likely negating any potential performance
        benefits from using a :class:`aiohttp.ClientResponse` return type.

    .. versionadded:: 4.11

    Parameters
    ----------
    method
        :class:`AsyncClient` method to paginate for
    args
        Positional arguments to pass to ``method``
    limit
        Maximum number of requests to make to the API
    pagination_token
        Pagination token to start pagination with
    kwargs
        Keyword arguments to pass to ``method``
    """

    def __init__(self, method, *args, **kwargs):
        self.method = method
        self.args = args
        self.kwargs = kwargs

    def __aiter__(self):
        return AsyncPaginationIterator(self.method, *self.args, **self.kwargs)

    def __reversed__(self):
        return AsyncPaginationIterator(
            self.method, *self.args, reverse=True, **self.kwargs
        )

    async def flatten(self, limit=inf):
        """Flatten paginated data

        Parameters
        ----------
        limit
            Maximum number of results to yield
        """
        if limit <= 0:
            return

        count = 0
        async for response in AsyncPaginationIterator(
            self.method, *self.args, **self.kwargs
        ):
            if isinstance(response, Response):
                response_data = response.data or []
            elif isinstance(response, dict):
                response_data = response.get("data", [])
            else:
                raise RuntimeError(
                    "AsyncPaginator.flatten does not support the "
                    f"{type(response)} return type for "
                    f"{self.method.__qualname__}"
                )
            for data in response_data:
                yield data
                count += 1
                if count == limit:
                    return


class AsyncPaginationIterator:

    def __init__(
        self, method, *args, limit=inf, pagination_token=None, reverse=False,
        **kwargs
    ):
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

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.reverse:
            pagination_token = self.previous_token
        else:
            pagination_token = self.next_token

        if self.count >= self.limit or self.count and pagination_token is None:
            raise StopAsyncIteration

        # https://twittercommunity.com/t/why-does-timeline-use-pagination-token-while-search-uses-next-token/150963
        if self.method.__name__ in (
            "search_all_tweets", "search_recent_tweets",
            "get_all_tweets_count"
        ):
            self.kwargs["next_token"] = pagination_token
        else:
            self.kwargs["pagination_token"] = pagination_token

        response = await self.method(*self.args, **self.kwargs)

        if isinstance(response, Response):
            meta = response.meta
        elif isinstance(response, dict):
            meta = response.get("meta", {})
        elif isinstance(response, aiohttp.ClientResponse):
            meta = (await response.json()).get("meta", {})
        else:
            raise RuntimeError(
                f"Unknown {type(response)} return type for "
                f"{self.method.__qualname__}"
            )

        self.previous_token = meta.get("previous_token")
        self.next_token = meta.get("next_token")
        self.count += 1

        return response
