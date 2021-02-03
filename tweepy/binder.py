# Tweepy
# Copyright 2009-2021 Joshua Roesslein
# See LICENSE for details.


def pagination(mode):
    def decorator(method):
        method.pagination_mode = mode
        return method
    return decorator


def payload(payload_type, **payload_kwargs):
    payload_list = payload_kwargs.get('list', False)
    def decorator(method):
        def wrapper(*args, **kwargs):
            kwargs['payload_list'] = payload_list
            kwargs['payload_type'] = payload_type
            return method(*args, **kwargs)
        wrapper.payload_list = payload_list
        wrapper.payload_type = payload_type
        return wrapper
    return decorator
