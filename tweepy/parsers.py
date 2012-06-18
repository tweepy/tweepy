# Tweepy
# Copyright 2009-2010 Joshua Roesslein
# See LICENSE for details.

from .models import ModelFactory
from .utils import import_simplejson
from .error import TweepError

import sys
PY_MAJOR_VERSION = sys.version_info.major


class Parser(object):

    def parse(self, method, payload):
        """
        Parse the response payload and return the result.
        Returns a tuple that contains the result data and the cursors
        (or None if not present).
        """
        raise NotImplementedError

    def parse_error(self, payload):
        """
        Parse the error message from payload.
        If unable to parse the message, throw an exception
        and default error message will be used.
        """
        raise NotImplementedError


class RawParser(Parser):

    def __init__(self):
        pass

    def parse(self, method, payload):
        return payload

    def parse_error(self, payload):
        return payload


class JSONParser(Parser):

    payload_format = 'json'

    def __init__(self):
        self.json_lib = import_simplejson()

    def parse(self, method, payload):
        try:
            if PY_MAJOR_VERSION == 2 :
                payload = payload.read()
                json = self.json_lib.loads(payload)
            else :
                encoding = payload.headers.get_content_charset()
                body = payload.readall().decode(encoding)
                json = self.json_lib.loads(body)

        except Exception as e:
            raise TweepError('Failed to parse JSON payload: %s' % e)

        if PY_MAJOR_VERSION == 2 :
            needsCursors = method.parameters.has_key('cursor')
        else :
            needsCursors = 'cursor' in method.parameters
        if needsCursors and isinstance(json, dict) and 'previous_cursor' in json and 'next_cursor' in json:
            cursors = json['previous_cursor'], json['next_cursor']
            return json, cursors
        else:
            return json

    def parse_error(self, payload):
        error = self.json_lib.loads(payload)
        if PY_MAJOR_VERSION == 2 :
            if error.has_key('error'):
                return error['error']
            else:
                return error['errors']
        else :
            if 'error' in error:
                return error['error']
            else:
                return error['errors']


class ModelParser(JSONParser):

    def __init__(self, model_factory=None):
        JSONParser.__init__(self)
        self.model_factory = model_factory or ModelFactory

    def parse(self, method, payload):
        try:
            if method.payload_type is None: return
            model = getattr(self.model_factory, method.payload_type)
        except AttributeError:
            raise TweepError('No model for this payload type: %s' % method.payload_type)

        json = JSONParser.parse(self, method, payload)
        if isinstance(json, tuple):
            json, cursors = json
        else:
            cursors = None

        if method.payload_list:
            result = model.parse_list(method.api, json)
        else:
            result = model.parse(method.api, json)

        if cursors:
            return result, cursors
        else:
            return result

