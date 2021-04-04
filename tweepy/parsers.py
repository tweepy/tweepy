# Tweepy
# Copyright 2009-2021 Joshua Roesslein
# See LICENSE for details.

import json as json_lib

from tweepy.errors import TweepyException
from tweepy.models import ModelFactory


class Parser:

    def parse(self, payload, *args, **kwargs):
        """
        Parse the response payload and return the result.
        Returns a tuple that contains the result data and the cursors
        (or None if not present).
        """
        raise NotImplementedError


class RawParser(Parser):

    def __init__(self):
        pass

    def parse(self, payload, *args, **kwargs):
        return payload


class JSONParser(Parser):

    payload_format = 'json'

    def parse(self, payload, *, return_cursors=False, **kwargs):
        try:
            json = json_lib.loads(payload)
        except Exception as e:
            raise TweepyException(f'Failed to parse JSON payload: {e}')

        if return_cursors and isinstance(json, dict):
            if 'next' in json:
                return json, json['next']
            elif 'next_cursor' in json:
                if 'previous_cursor' in json:
                    cursors = json['previous_cursor'], json['next_cursor']
                    return json, cursors
                else:
                    return json, json['next_cursor']
        return json


class ModelParser(JSONParser):

    def __init__(self, model_factory=None):
        JSONParser.__init__(self)
        self.model_factory = model_factory or ModelFactory

    def parse(self, payload, *, api=None, payload_list=False,
              payload_type=None, return_cursors=False):
        try:
            if payload_type is None:
                return
            model = getattr(self.model_factory, payload_type)
        except AttributeError:
            raise TweepyException(
                f'No model for this payload type: {payload_type}'
            )

        json = JSONParser.parse(self, payload, return_cursors=return_cursors)
        if isinstance(json, tuple):
            json, cursors = json
        else:
            cursors = None

        try:
            if payload_list:
                result = model.parse_list(api, json)
            else:
                result = model.parse(api, json)
        except KeyError:
            raise TweepyException(
                f"Unable to parse response payload: {json}"
            ) from None

        if cursors:
            return result, cursors
        else:
            return result
