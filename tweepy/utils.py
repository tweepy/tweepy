# Tweepy
# Copyright 2010-2023 Joshua Roesslein
# See LICENSE for details.

import datetime


def list_to_csv(item_list):
    if item_list:
        return ','.join(map(str, item_list))


def parse_datetime(datetime_string):
    return datetime.datetime.strptime(
        datetime_string, "%Y-%m-%dT%H:%M:%S.%f%z"
    ).replace(tzinfo=datetime.timezone.utc)
