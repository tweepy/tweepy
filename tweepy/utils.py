# Tweepy
# Copyright 2010-2021 Joshua Roesslein
# See LICENSE for details.


def parse_html_value(html):
    return html[html.find('>')+1:html.rfind('<')]


def parse_a_href(atag):
    start = atag.find('"') + 1
    end = atag.find('"', start)
    return atag[start:end]


def list_to_csv(item_list):
    if item_list:
        return ','.join(map(str, item_list))
