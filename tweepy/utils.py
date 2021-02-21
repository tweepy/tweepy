# Tweepy
# Copyright 2010-2021 Joshua Roesslein
# See LICENSE for details.


def list_to_csv(item_list):
    if item_list:
        return ','.join(map(str, item_list))
