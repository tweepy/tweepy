""" script to parse the url of bindings and find if the page exists or not """
import pprint
import re
import os
import requests

__author__ = 'jordiriera'

url_root = 'https://dev.twitter.com'
reference_line = re.compile(':reference: ({}.*) "'.format(url_root))


def parse(filename):
    dead_links = []
    with open(filename, 'r') as file_:
        for line in file_.readlines():
            res = reference_line.search(line)
            if res:
                if not exists(res.group(1)):
                    dead_links.append(res.group(1))

    return dead_links


def exists(path):
    r = requests.head(path)
    return r.status_code == requests.codes.ok


if __name__ == '__main__':
    root = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(root, 'tweepy', 'api.py')
    pprint.pprint(parse(filename))
