# Tweepy
# Copyright 2009-2022 Joshua Roesslein
# See LICENSE for details.

from math import inf

from tweepy.errors import TweepyException
from tweepy.parsers import ModelParser, RawParser


class Cursor:
    """:class:`Cursor` can be used to paginate for any :class:`API` methods that
    support pagination

    Parameters
    ----------
    method
        :class:`API` method to paginate for
    args
        Positional arguments to pass to ``method``
    kwargs
        Keyword arguments to pass to ``method``
    """

    def __init__(self, method, *args, **kwargs):
        if hasattr(method, 'pagination_mode'):
            if method.pagination_mode == 'cursor':
                self.iterator = CursorIterator(method, *args, **kwargs)
            elif method.pagination_mode == 'dm_cursor':
                self.iterator = DMCursorIterator(method, *args, **kwargs)
            elif method.pagination_mode == 'id':
                self.iterator = IdIterator(method, *args, **kwargs)
            elif method.pagination_mode == "next":
                self.iterator = NextIterator(method, *args, **kwargs)
            elif method.pagination_mode == 'page':
                self.iterator = PageIterator(method, *args, **kwargs)
            else:
                raise TweepyException('Invalid pagination mode.')
        else:
            raise TweepyException('This method does not perform pagination')

    def pages(self, limit=inf):
        """Retrieve the page for each request

        Parameters
        ----------
        limit
            Maximum number of pages to iterate over

        Returns
        -------
        CursorIterator or DMCursorIterator or IdIterator or NextIterator or \
        PageIterator
            Iterator to iterate through pages
        """
        self.iterator.limit = limit
        return self.iterator

    def items(self, limit=inf):
        """Retrieve the items in each page/request

        Parameters
        ----------
        limit
            Maximum number of items to iterate over

        Returns
        -------
        ItemIterator
            Iterator to iterate through items
        """
        iterator = ItemIterator(self.iterator)
        iterator.limit = limit
        return iterator


class BaseIterator:

    def __init__(self, method, *args, **kwargs):
        self.method = method
        self.args = args
        self.kwargs = kwargs
        self.limit = inf

    def __next__(self):
        return self.next()

    def next(self):
        raise NotImplementedError

    def prev(self):
        raise NotImplementedError

    def __iter__(self):
        return self


class CursorIterator(BaseIterator):

    def __init__(self, method, *args, **kwargs):
        BaseIterator.__init__(self, method, *args, **kwargs)
        start_cursor = self.kwargs.pop('cursor', None)
        self.next_cursor = start_cursor or -1
        self.prev_cursor = start_cursor or 0
        self.num_tweets = 0

    def next(self):
        if self.next_cursor == 0 or self.num_tweets >= self.limit:
            raise StopIteration
        data, cursors = self.method(cursor=self.next_cursor,
                                    *self.args,
                                    **self.kwargs)
        self.prev_cursor, self.next_cursor = cursors
        if len(data) == 0:
            raise StopIteration
        self.num_tweets += 1
        return data

    def prev(self):
        if self.prev_cursor == 0:
            raise TweepyException('Can not page back more, at first page')
        data, self.next_cursor, self.prev_cursor = self.method(cursor=self.prev_cursor,
                                                               *self.args,
                                                               **self.kwargs)
        self.num_tweets -= 1
        return data


class DMCursorIterator(BaseIterator):

    def __init__(self, method, *args, **kwargs):
        BaseIterator.__init__(self, method, *args, **kwargs)
        self.next_cursor = self.kwargs.pop('cursor', None)
        self.page_count = 0

    def next(self):
        if self.next_cursor == -1 or self.page_count >= self.limit:
            raise StopIteration
        data = self.method(cursor=self.next_cursor, return_cursors=True, *self.args, **self.kwargs)
        self.page_count += 1
        if isinstance(data, tuple):
            data, self.next_cursor = data
        else:
            self.next_cursor = -1
        return data

    def prev(self):
        raise TweepyException('This method does not allow backwards pagination')


class IdIterator(BaseIterator):

    def __init__(self, method, *args, **kwargs):
        BaseIterator.__init__(self, method, *args, **kwargs)
        self.max_id = self.kwargs.pop('max_id', None)
        self.num_tweets = 0
        self.results = []
        self.model_results = []
        self.index = 0

    def next(self):
        """Fetch a set of items with IDs less than current set."""
        if self.num_tweets >= self.limit:
            raise StopIteration

        if self.index >= len(self.results) - 1:
            data = self.method(max_id=self.max_id, parser=RawParser(), *self.args, **self.kwargs)

            model = ModelParser().parse(
                data, api = self.method.__self__,
                payload_list=self.method.payload_list,
                payload_type=self.method.payload_type
            )
            result = self.method.__self__.parser.parse(
                data, api = self.method.__self__,
                payload_list=self.method.payload_list,
                payload_type=self.method.payload_type
            )

            if len(self.results) != 0:
                self.index += 1
            self.results.append(result)
            self.model_results.append(model)
        else:
            self.index += 1
            result = self.results[self.index]
            model = self.model_results[self.index]

        if len(result) == 0:
            raise StopIteration
        # TODO: Make this not dependant on the parser making max_id and
        # since_id available
        self.max_id = model.max_id
        self.num_tweets += 1
        return result

    def prev(self):
        """Fetch a set of items with IDs greater than current set."""
        if self.num_tweets >= self.limit:
            raise StopIteration

        self.index -= 1
        if self.index < 0:
            # There's no way to fetch a set of tweets directly 'above' the
            # current set
            raise StopIteration

        data = self.results[self.index]
        self.max_id = self.model_results[self.index].max_id
        self.num_tweets += 1
        return data


class PageIterator(BaseIterator):

    def __init__(self, method, *args, **kwargs):
        BaseIterator.__init__(self, method, *args, **kwargs)
        self.current_page = 1
        # Keep track of previous page of items to handle Twitter API issue with
        # duplicate pages
        # https://twittercommunity.com/t/odd-pagination-behavior-with-get-users-search/148502
        # https://github.com/tweepy/tweepy/issues/1465
        # https://github.com/tweepy/tweepy/issues/958
        self.previous_items = []

    def next(self):
        if self.current_page > self.limit:
            raise StopIteration

        items = self.method(page=self.current_page, *self.args, **self.kwargs)

        if len(items) == 0:
            raise StopIteration

        for item in items:
            if item in self.previous_items:
                raise StopIteration

        self.current_page += 1
        self.previous_items = items
        return items

    def prev(self):
        if self.current_page == 1:
            raise TweepyException('Can not page back more, at first page')
        self.current_page -= 1
        return self.method(page=self.current_page, *self.args, **self.kwargs)


class NextIterator(BaseIterator):

    def __init__(self, method, *args, **kwargs):
        BaseIterator.__init__(self, method, *args, **kwargs)
        self.next_token = self.kwargs.pop('next', None)
        self.page_count = 0

    def next(self):
        if self.next_token == -1 or self.page_count >= self.limit:
            raise StopIteration
        data = self.method(next=self.next_token, return_cursors=True, *self.args, **self.kwargs)
        self.page_count += 1
        if isinstance(data, tuple):
            data, self.next_token = data
        else:
            self.next_token = -1
        return data

    def prev(self):
        raise TweepyException('This method does not allow backwards pagination')


class ItemIterator(BaseIterator):

    def __init__(self, page_iterator):
        self.page_iterator = page_iterator
        self.limit = inf
        self.current_page = None
        self.page_index = -1
        self.num_tweets = 0

    def next(self):
        if self.num_tweets >= self.limit:
            raise StopIteration
        if self.current_page is None or self.page_index == len(self.current_page) - 1:
            # Reached end of current page, get the next page...
            self.current_page = next(self.page_iterator)
            while len(self.current_page) == 0:
                self.current_page = next(self.page_iterator)
            self.page_index = -1
        self.page_index += 1
        self.num_tweets += 1
        return self.current_page[self.page_index]

    def prev(self):
        if self.current_page is None:
            raise TweepyException('Can not go back more, at first page')
        if self.page_index == 0:
            # At the beginning of the current page, move to next...
            self.current_page = self.page_iterator.prev()
            self.page_index = len(self.current_page)
            if self.page_index == 0:
                raise TweepyException('No more items')
        self.page_index -= 1
        self.num_tweets -= 1
        return self.current_page[self.page_index]
