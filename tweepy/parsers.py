# Tweepy
# Copyright 2009 Joshua Roesslein
# See LICENSE

from tweepy.models import ModelFactory
from tweepy.utils import import_simplejson


class Parser(object):

    def parse(self, api, payload_type, payload_list, payload):
        """
        Parse the response payload and return the result.
        Returns a tuple that contains the result data and the cursors
        (or None if not present).
        """
        raise NotImplementedError


class JSONParser(Parser):

    payload_format = 'json'

    def __init__(self):
        self.json_lib = import_simplejson()

    def parse(self, api, payload_type, payload_list, payload):
        try:
            json = self.json_lib.loads(payload)
        except Exception, e:
            raise TweepError('Failed to parse JSON payload: %s' % e)

        if isinstance(json, dict) and 'previous_cursor' in json and 'next_cursor' in json:
            cursors = json['previous_cursor'], json['next_cursor']
            return json, cursors
        else:
            return json


class ModelParser(JSONParser):

    def __init__(self, model_factory=None):
        JSONParser.__init__(self)
        self.model_factory = model_factory or ModelFactory

    def parse(self, api, payload_type, payload_list, payload):
        try:
            if payload_type is None: return
            model = getattr(self.model_factory, payload_type)
        except AttributeError:
            raise TweepError('No model for this payload type: %s' % method.payload_type)

        json = JSONParser.parse(self, api, payload_type, payload_list, payload)
        if isinstance(json, tuple):
            json, cursors = json
        else:
            cursors = None

        if payload_list:
            result = model.parse_list(api, json)
        else:
            result = model.parse(api, json)

        if cursors:
            return result, cursors
        else:
            return result

