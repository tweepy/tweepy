# Tweepy
# Copyright 2009-2010 Joshua Roesslein
# See LICENSE for details.

from tweepy.error import TweepError

class Cursor(object):
    """Pagination helper class"""

    def __init__(self, method, *args, **kargs):
        if hasattr(method, 'pagination_mode'):
            if method.pagination_mode == 'cursor':
                self.iterator = CursorIterator(method, args, kargs)
            elif method.pagination_mode == 'id':
                self.iterator = IdIterator(method, args, kargs)
            elif method.pagination_mode == 'page':
                self.iterator = PageIterator(method, args, kargs)
            else:
                raise TweepError('Invalid pagination mode.')
        else:
            raise TweepError('This method does not perform pagination')

    def pages(self, limit=0):
        """Return iterator for pages"""
        if limit > 0:
            self.iterator.limit = limit
        return self.iterator

    def items(self, limit=0):
        """Return iterator for items in each page"""
        i = ItemIterator(self.iterator)
        i.limit = limit
        return i

class BaseIterator(object):

    def __init__(self, method, args, kargs):
        self.method = method
        self.args = args
        self.kargs = kargs
        self.limit = 0

    def next(self):
        raise NotImplementedError

    def prev(self):
        raise NotImplementedError

    def __iter__(self):
        return self

class CursorIterator(BaseIterator):

    def __init__(self, method, args, kargs):
        BaseIterator.__init__(self, method, args, kargs)
        self.next_cursor = -1
        self.prev_cursor = 0
        self.count = 0

    def next(self):
        if self.next_cursor == 0 or (self.limit and self.count == self.limit):
            raise StopIteration
        data, cursors = self.method(
                cursor=self.next_cursor, *self.args, **self.kargs
        )
        self.prev_cursor, self.next_cursor = cursors
        if len(data) == 0:
            raise StopIteration
        self.count += 1
        return data

    def prev(self):
        if self.prev_cursor == 0:
            raise TweepError('Can not page back more, at first page')
        data, self.next_cursor, self.prev_cursor = self.method(
                cursor=self.prev_cursor, *self.args, **self.kargs
        )
        self.count -= 1
        return data

class IdIterator(BaseIterator):

    def __init__(self, method, args, kargs):
        BaseIterator.__init__(self, method, args, kargs)
        self.max_id = kargs.get('max_id')
        self.since_id = kargs.get('since_id')
        self.count = 0

    def next(self):
        """Fetch a set of items with IDs less than current set."""
        if self.limit and self.limit == self.count:
            raise StopIteration

        # max_id is inclusive so decrement by one
        # to avoid requesting duplicate items.
        max_id = self.since_id - 1 if self.max_id else None
        data = self.method(max_id = max_id, *self.args, **self.kargs)
        if len(data) == 0:
            raise StopIteration
        self.max_id = data.max_id
        self.since_id = data.since_id
        self.count += 1
        return data

    def prev(self):
        """Fetch a set of items with IDs greater than current set."""
        if self.limit and self.limit == self.count:
            raise StopIteration

        since_id = self.max_id
        data = self.method(since_id = since_id, *self.args, **self.kargs)
        if len(data) == 0:
            raise StopIteration
        self.max_id = data.max_id
        self.since_id = data.since_id
        self.count += 1
        return data

class PageIterator(BaseIterator):

    def __init__(self, method, args, kargs):
        BaseIterator.__init__(self, method, args, kargs)
        self.current_page = 0

    def next(self):
        self.current_page += 1
        items = self.method(page=self.current_page, *self.args, **self.kargs)
        if len(items) == 0 or (self.limit > 0 and self.current_page > self.limit):
            raise StopIteration
        return items

    def prev(self):
        if (self.current_page == 1):
            raise TweepError('Can not page back more, at first page')
        self.current_page -= 1
        return self.method(page=self.current_page, *self.args, **self.kargs)

class ItemIterator(BaseIterator):

    def __init__(self, page_iterator):
        self.page_iterator = page_iterator
        self.limit = 0
        self.current_page = None
        self.page_index = -1
        self.count = 0

    def next(self):
        if self.limit > 0 and self.count == self.limit:
            raise StopIteration
        if self.current_page is None or self.page_index == len(self.current_page) - 1:
            # Reached end of current page, get the next page...
            self.current_page = self.page_iterator.next()
            self.page_index = -1
        self.page_index += 1
        self.count += 1
        return self.current_page[self.page_index]

    def prev(self):
        if self.current_page is None:
            raise TweepError('Can not go back more, at first page')
        if self.page_index == 0:
            # At the beginning of the current page, move to next...
            self.current_page = self.page_iterator.prev()
            self.page_index = len(self.current_page)
            if self.page_index == 0:
                raise TweepError('No more items')
        self.page_index -= 1
        self.count -= 1
        return self.current_page[self.page_index]

