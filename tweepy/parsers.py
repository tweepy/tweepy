# Tweepy
# Copyright 2009 Joshua Roesslein
# See LICENSE

from tweepy.models import ModelFactory
from tweepy.utils import import_simplejson


class Parser(object):

    payload_format = 'json'

    def parse(self, api, payload_type, payload_list, payload):
        """Parse the response payload and return the result."""
        raise NotImplementedError


class ModelParser(Parser):

    def __init__(self, model_factory=None):
        self.model_factory = model_factory or ModelFactory
        self.json_lib = import_simplejson()

    def parse(self, api, payload_type, payload_list, payload):
        try:
            if payload_type is None: return
            model = getattr(self.model_factory, payload_type)
        except AttributeError:
            raise TweepError('No model for this payload type: %s' % method.payload_type)

        try:
            json = self.json_lib.loads(payload)
        except Exception, e:
            raise TweepError('Failed to parse JSON: %s' % e)

        if payload_list:
            return model.parse_list(api, json)
        else:
            return model.parse(api, json)

