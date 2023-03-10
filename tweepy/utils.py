# Tweepy
# Copyright 2010-2023 Joshua Roesslein
# See LICENSE for details.

from __future__ import annotations

from collections.abc import Iterable
import datetime


def list_to_csv(item_list: Iterable[int | str] | None) -> str | None:
    if item_list is None:
        return None
    else:
        return ','.join(map(str, item_list))


def parse_datetime(datetime_string: str) -> datetime.datetime:
    return datetime.datetime.strptime(
        datetime_string, "%Y-%m-%dT%H:%M:%S.%f%z"
    ).replace(tzinfo=datetime.timezone.utc)
