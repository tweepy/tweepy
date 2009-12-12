# Tweepy
# Copyright 2009 Joshua Roesslein
# See LICENSE

import htmlentitydefs
import re
from datetime import datetime
import time

from tweepy.models import models

def _parse_cursor(obj):

    return obj['next_cursor'], obj['prev_cursor']

def parse_json(obj, api):

    return obj


def parse_return_true(obj, api):

    return True


def parse_none(obj, api):

    return None


def parse_error(obj):

    return obj['error']


def _parse_datetime(str):

    # We must parse datetime this way to work in python 2.4
    return datetime(*(time.strptime(str, '%a %b %d %H:%M:%S +0000 %Y')[0:6]))


def _parse_search_datetime(str):

    # python 2.4
    return datetime(*(time.strptime(str, '%a, %d %b %Y %H:%M:%S +0000')[0:6]))


def unescape_html(text):
    """Created by Fredrik Lundh (http://effbot.org/zone/re-sub.htm#unescape-html)"""
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)


def _parse_html_value(html):

    return html[html.find('>')+1:html.rfind('<')]


def _parse_a_href(atag):

    start = atag.find('"') + 1
    end = atag.find('"', start)
    return atag[start:end]


def parse_user(obj, api):

    user = models['user']()
    user._api = api
    for k, v in obj.items():
        if k == 'created_at':
            setattr(user, k, _parse_datetime(v))
        elif k == 'status':
            setattr(user, k, parse_status(v, api))
        elif k == 'following':
            # twitter sets this to null if it is false
            if v is True:
                setattr(user, k, True)
            else:
                setattr(user, k, False)
        else:
            setattr(user, k, v)
    return user


def parse_users(obj, api):

    if isinstance(obj, list) is False:
        item_list = obj['users']
    else:
        item_list = obj

    users = []
    for item in item_list:
        if item is None: break  # sometimes an empty list with a null in it
        users.append(parse_user(item, api))
    return users


def parse_status(obj, api):

    status = models['status']()
    status._api = api
    for k, v in obj.items():
        if k == 'user':
            user = parse_user(v, api)
            setattr(status, 'author', user)
            setattr(status, 'user', user)  # DEPRECIATED
        elif k == 'created_at':
            setattr(status, k, _parse_datetime(v))
        elif k == 'source':
            if '<' in v:
                setattr(status, k, _parse_html_value(v))
                setattr(status, 'source_url', _parse_a_href(v))
            else:
                setattr(status, k, v)
        elif k == 'retweeted_status':
            setattr(status, k, parse_status(v, api))
        else:
            setattr(status, k, v)
    return status


def parse_statuses(obj, api):

    statuses = []
    for item in obj:
        statuses.append(parse_status(item, api))
    return statuses


def parse_dm(obj, api):

    dm = models['direct_message']()
    dm._api = api
    for k, v in obj.items():
        if k == 'sender' or k == 'recipient':
            setattr(dm, k, parse_user(v, api))
        elif k == 'created_at':
            setattr(dm, k, _parse_datetime(v))
        else:
            setattr(dm, k, v)
    return dm


def parse_directmessages(obj, api):

    directmessages = []
    for item in obj:
        directmessages.append(parse_dm(item, api))
    return directmessages


def parse_friendship(obj, api):

    relationship = obj['relationship']

    # parse source
    source = models['friendship']()
    for k, v in relationship['source'].items():
        setattr(source, k, v)

    # parse target
    target = models['friendship']()
    for k, v in relationship['target'].items():
        setattr(target, k, v)

    return source, target


def parse_ids(obj, api):

    if isinstance(obj, list) is False:
        return obj['ids']
    else:
        return obj

def parse_saved_search(obj, api):

    ss = models['saved_search']()
    ss._api = api
    for k, v in obj.items():
        if k == 'created_at':
            setattr(ss, k, _parse_datetime(v))
        else:
            setattr(ss, k, v)
    return ss


def parse_saved_searches(obj, api):

    saved_searches = []
    saved_search = models['saved_search']()
    for item in obj:
        saved_searches.append(parse_saved_search(item, api))
    return saved_searches


def parse_search_result(obj, api):

    result = models['search_result']()
    for k, v in obj.items():
        if k == 'created_at':
            setattr(result, k, _parse_search_datetime(v))
        elif k == 'source':
            setattr(result, k, _parse_html_value(unescape_html(v)))
        else:
            setattr(result, k, v)
    return result


def parse_search_results(obj, api):

    results = obj['results']
    result_objects = []
    for item in results:
        result_objects.append(parse_search_result(item, api))
    return result_objects


def parse_list(obj, api):

    lst = models['list']()
    lst._api = api
    for k,v in obj.items():
        if k == 'user':
            setattr(lst, k, parse_user(v, api))
        else:
            setattr(lst, k, v)
    return lst

def parse_lists(obj, api):

    lists = []
    for item in obj['lists']:
        lists.append(parse_list(item, api))
    return lists

