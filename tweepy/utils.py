# Tweepy
# Copyright 2010-2022 Joshua Roesslein
# See LICENSE for details.

import datetime


def list_to_csv(item_list):
    if item_list:
        return ','.join(map(str, item_list))


def parse_datetime(datetime_string):
    return datetime.datetime.strptime(
        datetime_string, "%Y-%m-%dT%H:%M:%S.%fZ"
    ).replace(tzinfo=datetime.timezone.utc)
    # Use %z when support for Python 3.6 is dropped
