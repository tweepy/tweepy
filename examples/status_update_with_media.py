#!/usr/bin/env python

import os
import tweepy

from token_secret import (
    CONSUMER, CONSUMER_SECRET,
    ACCESS_TOKEN, ACCESS_TOKEN_SECRET
)


def setup_api():
    auth = tweepy.OAuthHandler(CONSUMER, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    return tweepy.API(auth)

    
if __name__ == '__main__':
    api = setup_api()
    dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(dir, 'data', 'sample.png')
    status = 'Test Media Upload'
    api.status_update_with_media(file_path, status=status)

