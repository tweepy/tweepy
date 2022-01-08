# Tweepy
# Copyright 2010-2022 Joshua Roesslein
# See LICENSE for details.

import datetime
from typing import Sequence, Optional, Union


def list_to_csv(item_list: Optional[Sequence[Union[str, int]]]) -> Optional[str]:
    if item_list:
        return ','.join(map(str, item_list))


def parse_datetime(datetime_string: str) -> datetime.datetime:
    return datetime.datetime.strptime(
        datetime_string, "%Y-%m-%dT%H:%M:%S.%fZ"
    ).replace(tzinfo=datetime.timezone.utc)
    # Use %z when support for Python 3.6 is dropped
