# Tweepy
# Copyright 2010 Joshua Roesslein
# See LICENSE for details.

from datetime import datetime
import time
import re
import locale

try:
    from urllib.parse import quote
except ImportError:  # Python < 3
    from urllib import quote
import sys
if sys.version_info > (3, ):
    text_type, binary_type = str, bytes
else:
    text_type, binary_type = unicode, str
string_types = (text_type, binary_type)

from email.utils import parsedate

def parse_datetime(string):
    return datetime(*(parsedate(string)[:6]))


def parse_html_value(html):

    return html[html.find('>')+1:html.rfind('<')]


def parse_a_href(atag):

    start = atag.find('"') + 1
    end = atag.find('"', start)
    return atag[start:end]


def convert_to_utf8_str(arg):
    # written by Michael Norton (http://docondev.blogspot.com/)
    if not isinstance(arg, string_types):
        arg = str(arg)
    if isinstance(arg, text_type):
        arg = arg.encode('utf-8')
    return arg



def import_simplejson():
    try:
        import simplejson as json
    except ImportError:
        try:
            import json  # Python 2.6+
        except ImportError:
            try:
                from django.utils import simplejson as json  # Google App Engine
            except ImportError:
                raise ImportError("Can't load a json library")

    return json

def list_to_csv(item_list):
    if item_list:
        return ','.join([str(i) for i in item_list])

def urlencode_noplus(query):
    return '&'.join(['%s=%s' % (quote(str(k), ''), quote(str(v), '')) \
        for k, v in query.iteritems()])
