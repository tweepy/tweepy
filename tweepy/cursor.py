# Tweepy
# Copyright 2009 Joshua Roesslein
# See LICENSE

class Cursor(object):
    """Pagination helper class"""

    def __init__(self, method, *args, **kargs):
        if 'cursor' in method.allowed_param:
            self.iterator = CursorIterator(method, args, kargs)
        elif 'page' in method.allowed_param:
            self.iterator = PageIterator(method, args, kargs)
        else:
            raise TweepError('This method does not perform pagination')

    def pages(self, limit=0):
        """Return iterator for pages"""
        if limit > 0:
            self.iterator.limit = limit
        return self.iterator

    def items(self, limit=0):
        """Return iterator for items in each page"""
        items_yielded = 0
        for page in self.iterator:
            for item in page:
                if limit > 0 and items_yielded == limit:
                    raise StopIteration
                items_yielded += 1
                yield item

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

    def next(self):
        return

    def prev(self):
        return

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
        if (self.current_page == 0):
            raise TweepError('Can not page back more, at first page')
        self.current_page -= 1
        return self.method(page=self.current_page, *self.args, **self.kargs)

