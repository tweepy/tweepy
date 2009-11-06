#!/usr/bin/env python

import sys

import code
import tweepy
from tweepy import API, BasicAuthHandler

"""Launch an interactive shell ready for Tweepy usage

This script is handy for debugging tweepy during development
or to just play around with the library.
It imports tweepy and creates an authenticated API instance (api)
using the credentials provided.
"""

if len(sys.argv) != 3:
    print 'Usage: tweepyshell <username> <password>'
    exit(1)

api = API(BasicAuthHandler(username=sys.argv[1], password=sys.argv[2]))

code.interact('<Tweepy shell>', local={'tweepy': tweepy, 'api': api})

