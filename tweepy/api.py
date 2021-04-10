# Tweepy
# Copyright 2009-2021 Joshua Roesslein
# See LICENSE for details.

import functools
import imghdr
import logging
import mimetypes
import os
import sys
import time
from urllib.parse import urlencode

import requests

from tweepy.errors import (
    BadRequest, Forbidden, HTTPException, NotFound, TooManyRequests,
    TweepyException, TwitterServerError, Unauthorized
)
from tweepy.models import Model
from tweepy.parsers import ModelParser, Parser
from tweepy.utils import list_to_csv

log = logging.getLogger(__name__)


def pagination(mode):
    def decorator(method):
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            return method(*args, **kwargs)
        wrapper.pagination_mode = mode
        return wrapper
    return decorator


def payload(payload_type, **payload_kwargs):
    payload_list = payload_kwargs.get('list', False)
    def decorator(method):
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            kwargs['payload_list'] = payload_list
            kwargs['payload_type'] = payload_type
            return method(*args, **kwargs)
        wrapper.payload_list = payload_list
        wrapper.payload_type = payload_type
        return wrapper
    return decorator


class API:
    """This class provides a wrapper for the API as provided by Twitter.
    The functions provided in this class are listed below.

    :param auth: The authentication handler to be used
    :param cache: The cache to query if a GET method is used
    :param host: The general REST API host server URL
    :param parser: The Parser instance to use for parsing the response from
                   Twitter; defaults to an instance of ModelParser
    :param proxy: The full url to an HTTPS proxy to use for connecting to
                  Twitter
    :param retry_count: Number of retries to attempt when an error occurs
    :param retry_delay: Number of seconds to wait between retries
    :param retry_errors: Which HTTP status codes to retry
    :param timeout: The maximum amount of time to wait for a response from
                    Twitter
    :param upload_host: The URL of the upload server
    :param wait_on_rate_limit: Whether or not to automatically wait for rate
                               limits to replenish
    
    :raise TypeError: If the given parser is not a Parser instance

    :reference: https://developer.twitter.com/en/docs/api-reference-index
    """

    def __init__(
        self, auth=None, *, cache=None, host='api.twitter.com', parser=None,
        proxy=None, retry_count=0, retry_delay=0, retry_errors=None,
        timeout=60, upload_host='upload.twitter.com', wait_on_rate_limit=False
    ):
        self.auth = auth
        self.cache = cache
        self.host = host

        if parser is None:
            parser = ModelParser()
        self.parser = parser

        self.proxy = {}
        if proxy is not None:
            self.proxy['https'] = proxy

        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.retry_errors = retry_errors
        self.timeout = timeout
        self.upload_host = upload_host
        self.wait_on_rate_limit = wait_on_rate_limit

        # Attempt to explain more clearly the parser argument requirements
        # https://github.com/tweepy/tweepy/issues/421

        if not isinstance(self.parser, Parser):
            raise TypeError(
                "parser should be an instance of Parser, not " +
                str(type(self.parser))
            )

        self.session = requests.Session()

    def request(
        self, method, endpoint, *, endpoint_parameters=(), params=None,
        headers=None, json_payload=None, parser=None, payload_list=False,
        payload_type=None, post_data=None, files=None, require_auth=True,
        return_cursors=False, upload_api=False, use_cache=True, **kwargs
    ):
        # If authentication is required and no credentials
        # are provided, throw an error.
        if require_auth and not self.auth:
            raise TweepyException('Authentication required!')

        self.cached_result = False

        # Build the request URL
        path = f'/1.1/{endpoint}.json'
        if upload_api:
            url = 'https://' + self.upload_host + path
        else:
            url = 'https://' + self.host + path

        if params is None:
            params = {}
        for k, arg in kwargs.items():
            if arg is None:
                continue
            if k not in endpoint_parameters and k != "tweet_mode":
                log.warning(f'Unexpected parameter: {k}')
            params[k] = str(arg)
        log.debug("PARAMS: %r", params)

        # Query the cache if one is available
        # and this request uses a GET method.
        if use_cache and self.cache and method == 'GET':
            cache_result = self.cache.get(f'{path}?{urlencode(params)}')
            # if cache result found and not expired, return it
            if cache_result:
                # must restore api reference
                if isinstance(cache_result, list):
                    for result in cache_result:
                        if isinstance(result, Model):
                            result._api = self
                else:
                    if isinstance(cache_result, Model):
                        cache_result._api = self
                self.cached_result = True
                return cache_result

        # Monitoring rate limits
        remaining_calls = None
        reset_time = None

        if parser is None:
            parser = self.parser

        try:
            # Continue attempting request until successful
            # or maximum number of retries is reached.
            retries_performed = 0
            while retries_performed <= self.retry_count:
                if (self.wait_on_rate_limit and reset_time is not None
                    and remaining_calls is not None
                    and remaining_calls < 1):
                    # Handle running out of API calls
                    sleep_time = reset_time - int(time.time())
                    if sleep_time > 0:
                        log.warning(f"Rate limit reached. Sleeping for: {sleep_time}")
                        time.sleep(sleep_time + 1)  # Sleep for extra sec

                # Apply authentication
                auth = None
                if self.auth:
                    auth = self.auth.apply_auth()

                # Execute request
                try:
                    resp = self.session.request(
                        method, url, params=params, headers=headers,
                        data=post_data, files=files, json=json_payload,
                        timeout=self.timeout, auth=auth, proxies=self.proxy
                    )
                except Exception as e:
                    raise TweepyException(f'Failed to send request: {e}').with_traceback(sys.exc_info()[2])

                if 200 <= resp.status_code < 300:
                    break

                rem_calls = resp.headers.get('x-rate-limit-remaining')
                if rem_calls is not None:
                    remaining_calls = int(rem_calls)
                elif remaining_calls is not None:
                    remaining_calls -= 1

                reset_time = resp.headers.get('x-rate-limit-reset')
                if reset_time is not None:
                    reset_time = int(reset_time)

                retry_delay = self.retry_delay
                if resp.status_code in (420, 429) and self.wait_on_rate_limit:
                    if remaining_calls == 0:
                        # If ran out of calls before waiting switching retry last call
                        continue
                    if 'retry-after' in resp.headers:
                        retry_delay = float(resp.headers['retry-after'])
                elif self.retry_errors and resp.status_code not in self.retry_errors:
                    # Exit request loop if non-retry error code
                    break

                # Sleep before retrying request again
                time.sleep(retry_delay)
                retries_performed += 1

            # If an error was returned, throw an exception
            self.last_response = resp
            if resp.status_code == 400:
                raise BadRequest(resp)
            if resp.status_code == 401:
                raise Unauthorized(resp)
            if resp.status_code == 403:
                raise Forbidden(resp)
            if resp.status_code == 404:
                raise NotFound(resp)
            if resp.status_code == 429:
                raise TooManyRequests(resp)
            if resp.status_code >= 500:
                raise TwitterServerError(resp)
            if resp.status_code and not 200 <= resp.status_code < 300:
                raise HTTPException(resp)

            # Parse the response payload
            return_cursors = return_cursors or 'cursor' in params or 'next' in params
            result = parser.parse(
                resp.text, api=self, payload_list=payload_list,
                payload_type=payload_type, return_cursors=return_cursors
            )

            # Store result into cache if one is available.
            if use_cache and self.cache and method == 'GET' and result:
                self.cache.store(f'{path}?{urlencode(params)}', result)

            return result
        finally:
            self.session.close()

    # Get Tweet timelines

    @pagination(mode='id')
    @payload('status', list=True)
    def home_timeline(self, **kwargs):
        """home_timeline(*, count, since_id, max_id, trim_user, \
                         exclude_replies, include_entities)

        Returns the 20 most recent statuses, including retweets, posted by
        the authenticating user and that user's friends. This is the equivalent
        of /timeline/home on the Web.

        :param count: |count|
        :param since_id: |since_id|
        :param max_id: |max_id|
        :param trim_user: |trim_user|
        :param exclude_replies: |exclude_replies|
        :param include_entities: |include_entities|

        :rtype: list of :class:`Status` objects

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/timelines/api-reference/get-statuses-home_timeline
        """
        return self.request(
            'GET', 'statuses/home_timeline', endpoint_parameters=(
                'count', 'since_id', 'max_id', 'trim_user', 'exclude_replies',
                'include_entities'
            ), **kwargs
        )

    @pagination(mode='id')
    @payload('status', list=True)
    def mentions_timeline(self, **kwargs):
        """mentions_timeline(*, count, since_id, max_id, trim_user, \
                             include_entities)

        Returns the 20 most recent mentions, including retweets.

        :param count: |count|
        :param since_id: |since_id|
        :param max_id: |max_id|
        :param trim_user: |trim_user|
        :param include_entities: |include_entities|

        :rtype: list of :class:`Status` objects

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/timelines/api-reference/get-statuses-mentions_timeline
        """
        return self.request(
            'GET', 'statuses/mentions_timeline', endpoint_parameters=(
                'count', 'since_id', 'max_id', 'trim_user', 'include_entities'
            ), **kwargs
        )

    @pagination(mode='id')
    @payload('status', list=True)
    def user_timeline(self, **kwargs):
        """user_timeline(*, user_id, screen_name, since_id, count, max_id, \
                         trim_user, exclude_replies, include_rts)

        Returns the 20 most recent statuses posted from the authenticating user
        or the user specified. It's also possible to request another user's
        timeline via the id parameter.

        :param user_id: |user_id|
        :param screen_name: |screen_name|
        :param since_id: |since_id|
        :param count: |count|
        :param max_id: |max_id|
        :param trim_user: |trim_user|
        :param exclude_replies: |exclude_replies|
        :param include_rts: When set to ``false``, the timeline will strip any
            native retweets (though they will still count toward both the
            maximal length of the timeline and the slice selected by the count
            parameter). Note: If you're using the trim_user parameter in
            conjunction with include_rts, the retweets will still contain a
            full user object.

        :rtype: list of :class:`Status` objects

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/timelines/api-reference/get-statuses-user_timeline
        """
        return self.request(
            'GET', 'statuses/user_timeline', endpoint_parameters=(
                'user_id', 'screen_name', 'since_id', 'count', 'max_id',
                'trim_user', 'exclude_replies', 'include_rts'
            ), **kwargs
        )

    # Post, retrieve, and engage with Tweets

    @pagination(mode='id')
    @payload('status', list=True)
    def favorites(self, **kwargs):
        """favorites(*, user_id, screen_name, count, since_id, max_id, \
                     include_entities)

        Returns the favorite statuses for the authenticating user or user
        specified by the ID parameter.

        :param user_id: |user_id|
        :param screen_name: |screen_name|
        :param count: |count|
        :param since_id: |since_id|
        :param max_id: |max_id|
        :param include_entities: |include_entities|

        :rtype: list of :class:`Status` objects

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/get-favorites-list
        """
        return self.request(
            'GET', 'favorites/list', endpoint_parameters=(
                'user_id', 'screen_name', 'count', 'since_id', 'max_id',
                'include_entities'
            ), **kwargs
        )

    @payload('status', list=True)
    def statuses_lookup(self, id, **kwargs):
        """statuses_lookup(id, *, include_entities, trim_user, map, \
                           include_ext_alt_text, include_card_uri)

        Returns full Tweet objects for up to 100 Tweets per request, specified
        by the ``id`` parameter.

        :param id: A list of Tweet IDs to lookup, up to 100
        :param include_entities: |include_entities|
        :param trim_user: |trim_user|
        :param map: A boolean indicating whether or not to include Tweets
                    that cannot be shown. Defaults to False.
        :param include_ext_alt_text: |include_ext_alt_text|
        :param include_card_uri: |include_card_uri|

        :rtype: list of :class:`Status` objects

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/get-statuses-lookup
        """
        return self.request(
            'GET', 'statuses/lookup', endpoint_parameters=(
                'id', 'include_entities', 'trim_user', 'map',
                'include_ext_alt_text', 'include_card_uri'
            ), id=list_to_csv(id), **kwargs
        )

    @payload('json')
    def get_oembed(self, url, **kwargs):
        """get_oembed(url, *, maxwidth, hide_media, hide_thread, omit_script, \
                      align, related, lang, theme, link_color, widget_type, \
                      dnt)

        Returns a single Tweet, specified by either a Tweet web URL or the
        Tweet ID, in an oEmbed-compatible format. The returned HTML snippet will
        be automatically recognized as an Embedded Tweet when Twitter's widget
        JavaScript is included on the page.

        The oEmbed endpoint allows customization of the final appearance of an
        Embedded Tweet by setting the corresponding properties in HTML markup
        to be interpreted by Twitter's JavaScript bundled with the HTML
        response by default. The format of the returned markup may change over
        time as Twitter adds new features or adjusts its Tweet representation.

        The Tweet fallback markup is meant to be cached on your servers for up
        to the suggested cache lifetime specified in the ``cache_age``.

        :param url: The URL of the Tweet to be embedded
        :param maxwidth: The maximum width of a rendered Tweet in whole pixels.
            A supplied value under or over the allowed range will be returned
            as the minimum or maximum supported width respectively; the reset
            width value will be reflected in the returned ``width`` property.
            Note that Twitter does not support the oEmbed ``maxheight``
            parameter. Tweets are fundamentally text, and are therefore of
            unpredictable height that cannot be scaled like an image or video.
            Relatedly, the oEmbed response will not provide a value for
            ``height``. Implementations that need consistent heights for Tweets
            should refer to the ``hide_thread`` and ``hide_media`` parameters
            below.
        :param hide_media: When set to ``true``, ``"t"``, or ``1``, links in a
            Tweet are not expanded to photo, video, or link previews.
        :param hide_thread: When set to ``true``, ``"t"``, or ``1``, a
            collapsed version of the previous Tweet in a conversation thread
            will not be displayed when the requested Tweet is in reply to
            another Tweet.
        :param omit_script: When set to ``true``, ``"t"``, or ``1``, the
            ``<script>`` responsible for loading ``widgets.js`` will not be
            returned. Your webpages should include their own reference to
            ``widgets.js`` for use across all Twitter widgets including
            Embedded Tweets.
        :param align: Specifies whether the embedded Tweet should be floated
            left, right, or center in the page relative to the parent element.
        :param related: A comma-separated list of Twitter usernames related to
            your content. This value will be forwarded to Tweet action intents
            if a viewer chooses to reply, like, or retweet the embedded Tweet.
        :param lang: Request returned HTML and a rendered Tweet in the
                     specified Twitter language supported by embedded Tweets.
        :param theme: When set to ``dark``, the Tweet is displayed with light
                      text over a dark background.
        :param link_color: Adjust the color of Tweet text links with a
                           hexadecimal color value.
        :param widget_type: Set to ``video`` to return a Twitter Video embed
                            for the given Tweet.
        :param dnt: When set to ``true``, the Tweet and its embedded page on
            your site are not used for purposes that include personalized
            suggestions and personalized ads.

        :rtype: :class:`JSON` object

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/get-statuses-oembed
        """
        return self.request(
            'GET', 'statuses/oembed', endpoint_parameters=(
                'url', 'maxwidth', 'hide_media', 'hide_thread', 'omit_script',
                'align', 'related', 'lang', 'theme', 'link_color',
                'widget_type', 'dnt'
            ), url=url, require_auth=False, **kwargs
        )

    @pagination(mode='cursor')
    @payload('ids')
    def retweeters(self, id, **kwargs):
        """retweeters(id, *, count, cursor, stringify_ids)

        Returns up to 100 user IDs belonging to users who have retweeted the
        Tweet specified by the ``id`` parameter.

        :param id: |sid|
        :param count: |count|
        :param cursor: |cursor|
        :param stringify_ids: |stringify_ids|

        :rtype: list of :class:`int`

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/get-statuses-retweeters-ids
        """
        return self.request(
            'GET', 'statuses/retweeters/ids', endpoint_parameters=(
                'id', 'count', 'cursor', 'stringify_ids'
            ), id=id, **kwargs
        )

    @payload('status', list=True)
    def retweets(self, id, **kwargs):
        """retweets(id, *, count, trim_user)

        Returns up to 100 of the first Retweets of the given Tweet.

        :param id: |sid|
        :param count: |count|
        :param trim_user: |trim_user|

        :rtype: list of :class:`Status` objects

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/get-statuses-retweets-id
        """
        return self.request(
            'GET', f'statuses/retweets/{id}', endpoint_parameters=(
                'count', 'trim_user'
            ), **kwargs
        )

    @pagination(mode='id')
    @payload('status', list=True)
    def retweets_of_me(self, **kwargs):
        """retweets_of_me(*, count, since_id, max_id, trim_user, \
                          include_entities, include_user_entities)

        Returns the 20 most recent Tweets of the authenticated user that have
        been retweeted by others.

        :param count: |count|
        :param since_id: |since_id|
        :param max_id: |max_id|
        :param trim_user: |trim_user|
        :param include_entities: |include_entities|
        :param include_user_entities: |include_user_entities|

        :rtype: list of :class:`Status` objects

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/get-statuses-retweets_of_me
        """
        return self.request(
            'GET', 'statuses/retweets_of_me', endpoint_parameters=(
                'count', 'since_id', 'max_id', 'trim_user', 'include_entities',
                'include_user_entities'
            ), **kwargs
        )

    @payload('status')
    def get_status(self, id, **kwargs):
        """get_status(id, *, trim_user, include_my_retweet, include_entities, \
                      include_ext_alt_text, include_card_uri)

        Returns a single status specified by the ID parameter.

        :param id: |sid|
        :param trim_user: |trim_user|
        :param include_my_retweet: A boolean indicating if any Tweets returned
            that have been retweeted by the authenticating user should include
            an additional current_user_retweet node, containing the ID of the
            source status for the retweet.
        :param include_entities: |include_entities|
        :param include_ext_alt_text: |include_ext_alt_text|
        :param include_card_uri: |include_card_uri|

        :rtype: :class:`Status` object

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/get-statuses-show-id
        """
        return self.request(
            'GET', 'statuses/show', endpoint_parameters=(
                'id', 'trim_user', 'include_my_retweet', 'include_entities',
                'include_ext_alt_text', 'include_card_uri'
            ), id=id, **kwargs
        )

    @payload('status')
    def create_favorite(self, id, **kwargs):
        """create_favorite(id, *, include_entities)

        Favorites the status specified in the ``id`` parameter as the
        authenticating user.

        :param id: |sid|
        :param include_entities: |include_entities|

        :rtype: :class:`Status` object

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/post-favorites-create
        """
        return self.request(
            'POST', 'favorites/create', endpoint_parameters=(
                'id', 'include_entities'
            ), id=id, **kwargs
        )

    @payload('status')
    def destroy_favorite(self, id, **kwargs):
        """destroy_favorite(id, *, include_entities)

        Un-favorites the status specified in the ``id`` parameter as the
        authenticating user.

        :param id: |sid|
        :param include_entities: |include_entities|

        :rtype: :class:`Status` object

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/post-favorites-destroy
        """
        return self.request(
            'POST', 'favorites/destroy', endpoint_parameters=(
                'id', 'include_entities'
            ), id=id, **kwargs
        )

    @payload('status')
    def destroy_status(self, id, **kwargs):
        """destroy_status(id, *, trim_user)

        Destroy the status specified by the ``id`` parameter. The authenticated
        user must be the author of the status to destroy.

        :param id: |sid|
        :param trim_user: |trim_user|

        :rtype: :class:`Status` object

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/post-statuses-destroy-id
        """
        return self.request(
            'POST', f'statuses/destroy/{id}', endpoint_parameters=(
                'trim_user',
            ), **kwargs
        )

    @payload('status')
    def retweet(self, id, **kwargs):
        """retweet(id, *, trim_user)

        Retweets a Tweet. Requires the ID of the Tweet you are retweeting.

        :param id: |sid|
        :param trim_user: |trim_user|

        :rtype: :class:`Status` object

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/post-statuses-retweet-id
        """
        return self.request(
            'POST', f'statuses/retweet/{id}', endpoint_parameters=(
                'trim_user',
            ), **kwargs
        )

    @payload('status')
    def unretweet(self, id, **kwargs):
        """unretweet(id, *, trim_user)

        Untweets a retweeted status. Requires the ID of the retweet to
        unretweet.

        :param id: |sid|
        :param trim_user: |trim_user|

        :rtype: :class:`Status` object

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/post-statuses-unretweet-id
        """
        return self.request(
            'POST', f'statuses/unretweet/{id}', endpoint_parameters=(
                'trim_user',
            ), **kwargs
        )

    @payload('status')
    def update_status(self, status, **kwargs):
        """update_status(status, *, in_reply_to_status_id, \
                         auto_populate_reply_metadata, \
                         exclude_reply_user_ids, attachment_url, media_ids, \
                         possibly_sensitive, lat, long, place_id, \
                         display_coordinates, trim_user, enable_dmcommands, \
                         fail_dmcommands, card_uri)

        Updates the authenticating user's current status, also known as
        Tweeting.

        For each update attempt, the update text is compared with the
        authenticating user's recent Tweets. Any attempt that would result in
        duplication will be blocked, resulting in a 403 error. A user cannot
        submit the same status twice in a row.

        While not rate limited by the API, a user is limited in the number of
        Tweets they can create at a time. If the number of updates posted by
        the user reaches the current allowed limit this method will return an
        HTTP 403 error.

        :param status: The text of your status update.
        :param in_reply_to_status_id: The ID of an existing status that the
            update is in reply to. Note: This parameter will be ignored unless
            the author of the Tweet this parameter references is mentioned
            within the status text. Therefore, you must include @username,
            where username is the author of the referenced Tweet, within the
            update.
        :param auto_populate_reply_metadata: If set to true and used with
            in_reply_to_status_id, leading @mentions will be looked up from the
            original Tweet, and added to the new Tweet from there. This wil
            append @mentions into the metadata of an extended Tweet as a reply
            chain grows, until the limit on @mentions is reached. In cases
            where the original Tweet has been deleted, the reply will fail.
        :param exclude_reply_user_ids: When used with
            auto_populate_reply_metadata, a comma-separated list of user ids
            which will be removed from the server-generated @mentions prefix on
            an extended Tweet. Note that the leading @mention cannot be removed
            as it would break the in-reply-to-status-id semantics. Attempting
            to remove it will be silently ignored.
        :param attachment_url: In order for a URL to not be counted in the
            status body of an extended Tweet, provide a URL as a Tweet
            attachment. This URL must be a Tweet permalink, or Direct Message
            deep link. Arbitrary, non-Twitter URLs must remain in the status
            text. URLs passed to the attachment_url parameter not matching
            either a Tweet permalink or Direct Message deep link will fail at
            Tweet creation and cause an exception.
        :param media_ids: A list of media_ids to associate with the Tweet. You
            may include up to 4 photos or 1 animated GIF or 1 video in a Tweet.
        :param possibly_sensitive: If you upload Tweet media that might be
            considered sensitive content such as nudity, or medical procedures,
            you must set this value to true.
        :param lat: The latitude of the location this Tweet refers to. This
            parameter will be ignored unless it is inside the range -90.0 to
            +90.0 (North is positive) inclusive. It will also be ignored if
            there is no corresponding long parameter.
        :param long: The longitude of the location this Tweet refers to. The
            valid ranges for longitude are -180.0 to +180.0 (East is positive)
            inclusive. This parameter will be ignored if outside that range, if
            it is not a number, if geo_enabled is disabled, or if there no
            corresponding lat parameter.
        :param place_id: A place in the world.
        :param display_coordinates: Whether or not to put a pin on the exact
            coordinates a Tweet has been sent from.
        :param trim_user: |trim_user|
        :param enable_dmcommands: When set to true, enables shortcode commands
            for sending Direct Messages as part of the status text to send a
            Direct Message to a user. When set to false, disables this behavior
            and includes any leading characters in the status text that is
            posted
        :param fail_dmcommands: When set to true, causes any status text that
            starts with shortcode commands to return an API error. When set to
            false, allows shortcode commands to be sent in the status text and
            acted on by the API.
        :param card_uri: Associate an ads card with the Tweet using the
            card_uri value from any ads card response.

        :rtype: :class:`Status` object

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/post-statuses-update
        """
        if 'media_ids' in kwargs:
            kwargs['media_ids'] = list_to_csv(kwargs['media_ids'])

        return self.request(
            'POST', 'statuses/update', endpoint_parameters=(
                'status', 'in_reply_to_status_id',
                'auto_populate_reply_metadata', 'exclude_reply_user_ids',
                'attachment_url', 'media_ids', 'possibly_sensitive', 'lat',
                'long', 'place_id', 'display_coordinates', 'trim_user',
                'enable_dmcommands', 'fail_dmcommands', 'card_uri'
            ), status=status, **kwargs
        )

    @payload('status')
    def update_with_media(self, status, filename, *, file=None, **kwargs):
        """update_with_media(status, filename, *, file, possibly_sensitive, \
                             in_reply_to_status_id, lat, long, place_id, \
                             display_coordinates)

        .. deprecated:: 3.7.0
            Use :func:`API.media_upload` instead.
        
        Update the authenticated user's status. Statuses that are duplicates or
        too long will be silently ignored.

        :param status: The text of your status update.
        :param filename: |filename|
        :param file: |file|
        :param possibly_sensitive: Set to true for content which may not be
                                   suitable for every audience.
        :param in_reply_to_status_id: The ID of an existing status that the
                                      update is in reply to.
        :param lat: The location's latitude that this tweet refers to.
        :param long: The location's longitude that this tweet refers to.
        :param place_id: Twitter ID of location which is listed in the Tweet if
                         geolocation is enabled for the user.
        :param display_coordinates: Whether or not to put a pin on the exact
                                    coordinates a Tweet has been sent from.

        :rtype: :class:`Status` object

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/post-statuses-update_with_media
        """
        if file is not None:
            files = {'media[]': (filename, file)}
        else:
            files = {'media[]': open(filename, 'rb')}
        return self.request(
            'POST', 'statuses/update_with_media', endpoint_parameters=(
                'status', 'possibly_sensitive', 'in_reply_to_status_id',
                'lat', 'long', 'place_id', 'display_coordinates'
            ), status=status, files=files, **kwargs
        )

    # Search Tweets

    @pagination(mode='id')
    @payload('search_results')
    def search(self, q, **kwargs):
        """search(q, *, geocode, lang, locale, result_type, count, until, \
                  since_id, max_id, include_entities)

        Returns a collection of relevant Tweets matching a specified query.

        Please note that Twitter's search service and, by extension, the Search
        API is not meant to be an exhaustive source of Tweets. Not all Tweets
        will be indexed or made available via the search interface.

        In API v1.1, the response format of the Search API has been improved to
        return Tweet objects more similar to the objects you’ll find across the
        REST API and platform. However, perspectival attributes (fields that
        pertain to the perspective of the authenticating user) are not
        currently supported on this endpoint.\ [#]_\ [#]_

        :param q: the search query string of 500 characters maximum, including
            operators. Queries may additionally be limited by complexity.
        :param geocode: Returns tweets by users located within a given radius
            of the given latitude/longitude.  The location is preferentially
            taking from the Geotagging API, but will fall back to their Twitter
            profile. The parameter value is specified by
            "latitide,longitude,radius", where radius units must be specified
            as either "mi" (miles) or "km" (kilometers). Note that you cannot
            use the near operator via the API to geocode arbitrary locations;
            however you can use this geocode parameter to search near geocodes
            directly. A maximum of 1,000 distinct "sub-regions" will be
            considered when using the radius modifier.
        :param lang: Restricts tweets to the given language, given by an ISO
            639-1 code. Language detection is best-effort.
        :param locale: Specify the language of the query you are sending (only
            ja is currently effective). This is intended for language-specific
            consumers and the default should work in the majority of cases.
        :param result_type: Specifies what type of search results you would
            prefer to receive. The current default is "mixed." Valid values
            include:

            * mixed : include both popular and real time results in the \
                      response
            * recent : return only the most recent results in the response
            * popular : return only the most popular results in the response
        :param count: |count|
        :param until: Returns tweets created before the given date. Date should
            be formatted as YYYY-MM-DD. Keep in mind that the search index has
            a 7-day limit. In other words, no tweets will be found for a date
            older than one week.
        :param since_id: |since_id| There are limits to the number of Tweets
            which can be accessed through the API. If the limit of Tweets has
            occurred since the since_id, the since_id will be forced to the
            oldest ID available.
        :param max_id: |max_id|
        :param include_entities: |include_entities|

        :rtype: :class:`SearchResults` object

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/search/api-reference/get-search-tweets
        """
        return self.request(
            'GET', 'search/tweets', endpoint_parameters=(
                'q', 'geocode', 'lang', 'locale', 'result_type', 'count',
                'until', 'since_id', 'max_id', 'include_entities'
            ), q=q, **kwargs
        )

    # Create and manage lists

    @payload('list', list=True)
    def lists_all(self, **kwargs):
        """lists_all(*, user_id, screen_name, reverse)

        Returns all lists the authenticating or specified user subscribes to,
        including their own. The user is specified using the ``user_id`` or
        ``screen_name`` parameters. If no user is given, the authenticating
        user is used.

        A maximum of 100 results will be returned by this call. Subscribed
        lists are returned first, followed by owned lists. This means that if a
        user subscribes to 90 lists and owns 20 lists, this method returns 90
        subscriptions and 10 owned lists. The ``reverse`` method returns owned
        lists first, so with ``reverse=true``, 20 owned lists and 80
        subscriptions would be returned.

        :param user_id: |user_id|
        :param screen_name: |screen_name|
        :param reverse: A boolean indicating if you would like owned lists to
                        be returned first. See description above for
                        information on how this parameter works.

        :rtype: list of :class:`List` objects

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/get-lists-list
        """
        return self.request(
            'GET', 'lists/list', endpoint_parameters=(
                'user_id', 'screen_name', 'reverse'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('user', list=True)
    def list_members(self, **kwargs):
        """list_members(*, list_id, slug, owner_screen_name, owner_id, count, \
                        cursor, include_entities, skip_status)

        Returns the members of the specified list.

        :param list_id: |list_id|
        :param slug: |slug|
        :param owner_screen_name: |owner_screen_name|
        :param owner_id: |owner_id|
        :param count: |count|
        :param cursor: |cursor|
        :param include_entities: |include_entities|
        :param skip_status: |skip_status|

        :rtype: list of :class:`User` objects

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/get-lists-members
        """
        return self.request(
            'GET', 'lists/members', endpoint_parameters=(
                'list_id', 'slug', 'owner_screen_name', 'owner_id', 'count',
                'cursor', 'include_entities', 'skip_status'
            ), **kwargs
        )

    @payload('user')
    def show_list_member(self, **kwargs):
        """show_list_member(*, list_id, slug, user_id, screen_name, \
                            owner_screen_name, owner_id, include_entities, \
                            skip_status)

        Check if the specified user is a member of the specified list.

        :param list_id: |list_id|
        :param slug: |slug|
        :param user_id: |user_id|
        :param screen_name: |screen_name|
        :param owner_screen_name: |owner_screen_name|
        :param owner_id: |owner_id|
        :param include_entities: |include_entities|
        :param skip_status: |skip_status|

        :rtype: :class:`User` object if user is a member of list

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/get-lists-members-show
        """
        return self.request(
            'GET', 'lists/members/show', endpoint_parameters=(
                'list_id', 'slug', 'user_id', 'screen_name',
                'owner_screen_name', 'owner_id', 'include_entities',
                'skip_status'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('list', list=True)
    def lists_memberships(self, **kwargs):
        """lists_memberships(*, user_id, screen_name, count, cursor, \
                             filter_to_owned_lists)

        Returns the lists the specified user has been added to. If ``user_id``
        or ``screen_name`` are not provided, the memberships for the
        authenticating user are returned.

        :param user_id: |user_id|
        :param screen_name: |screen_name|
        :param count: |count|
        :param cursor: |cursor|
        :param filter_to_owned_lists: A boolean indicating whether to return
            just lists the authenticating user owns, and the user represented
            by ``user_id`` or ``screen_name`` is a member of.

        :rtype: list of :class:`List` objects

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/get-lists-memberships
        """
        return self.request(
            'GET', 'lists/memberships', endpoint_parameters=(
                'user_id', 'screen_name', 'count', 'cursor',
                'filter_to_owned_lists'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('list', list=True)
    def lists_ownerships(self, **kwargs):
        """lists_ownerships(*, user_id, screen_name, count, cursor)

        Returns the lists owned by the specified user. Private lists will only
        be shown if the authenticated user is also the owner of the lists. If
        ``user_id`` and ``screen_name`` are not provided, the ownerships for
        the authenticating user are returned.

        :param user_id: |user_id|
        :param screen_name: |screen_name|
        :param count: |count|
        :param cursor: |cursor|

        :rtype: list of :class:`List` objects

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/get-lists-ownerships
        """
        return self.request(
            'GET', 'lists/ownerships', endpoint_parameters=(
                'user_id', 'screen_name', 'count', 'cursor'
            ), **kwargs
        )

    @payload('list')
    def get_list(self, **kwargs):
        """get_list(*, list_id, slug, owner_screen_name, owner_id)

        Returns the specified list. Private lists will only be shown if the
        authenticated user owns the specified list.

        :param list_id: |list_id|
        :param slug: |slug|
        :param owner_screen_name: |owner_screen_name|
        :param owner_id: |owner_id|

        :rtype: :class:`List` object

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/get-lists-show
        """
        return self.request(
            'GET', 'lists/show', endpoint_parameters=(
                'list_id', 'slug', 'owner_screen_name', 'owner_id'
            ), **kwargs
        )

    @pagination(mode='id')
    @payload('status', list=True)
    def list_timeline(self, **kwargs):
        """list_timeline(*, list_id, slug, owner_screen_name, owner_id, \
                         since_id, max_id, count, include_entities, \
                         include_rts)

        Returns a timeline of Tweets authored by members of the specified list.
        Retweets are included by default. Use the ``include_rts=false``
        parameter to omit retweets.

        :param list_id: |list_id|
        :param slug: |slug|
        :param owner_screen_name: |owner_screen_name|
        :param owner_id: |owner_id|
        :param since_id: |since_id|
        :param max_id: |max_id|
        :param count: |count|
        :param include_entities: |include_entities|
        :param include_rts: A boolean indicating whether the list timeline will
            contain native retweets (if they exist) in addition to the standard
            stream of Tweets. The output format of retweeted Tweets is
            identical to the representation you see in home_timeline.

        :rtype: list of :class:`Status` objects

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/get-lists-statuses
                """
        return self.request(
            'GET', 'lists/statuses', endpoint_parameters=(
                'list_id', 'slug', 'owner_screen_name', 'owner_id', 'since_id',
                'max_id', 'count', 'include_entities', 'include_rts'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('user', list=True)
    def list_subscribers(self, **kwargs):
        """list_subscribers(*, list_id, slug, owner_screen_name, owner_id, \
                            count, cursor, include_entities, skip_status)

        Returns the subscribers of the specified list. Private list subscribers
        will only be shown if the authenticated user owns the specified list.

        :param list_id: |list_id|
        :param slug: |slug|
        :param owner_screen_name: |owner_screen_name|
        :param owner_id: |owner_id|
        :param count: |count|
        :param cursor: |cursor|
        :param include_entities: |include_entities|
        :param skip_status: |skip_status|

        :rtype: list of :class:`User` objects

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/get-lists-subscribers
        """
        return self.request(
            'GET', 'lists/subscribers', endpoint_parameters=(
                'list_id', 'slug', 'owner_screen_name', 'owner_id', 'count',
                'cursor', 'include_entities', 'skip_status'
            ), **kwargs
        )

    @payload('user')
    def show_list_subscriber(self, **kwargs):
        """show_list_subscriber(*, owner_screen_name, owner_id, list_id, \
                                slug, user_id, screen_name, include_entities \
                                skip_status)

        Check if the specified user is a subscriber of the specified list.

        :param owner_screen_name: |owner_screen_name|
        :param owner_id: |owner_id|
        :param list_id: |list_id|
        :param slug: |slug|
        :param user_id: |user_id|
        :param screen_name: |screen_name|
        :param include_entities: |include_entities|
        :param skip_status: |skip_status|

        :rtype: :class:`User` object if user is subscribed to list

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/get-lists-subscribers-show
        """
        return self.request(
            'GET', 'lists/subscribers/show', endpoint_parameters=(
                'owner_screen_name', 'owner_id', 'list_id', 'slug', 'user_id',
                'screen_name', 'include_entities', 'skip_status'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('list', list=True)
    def lists_subscriptions(self, **kwargs):
        """lists_subscriptions(*, user_id, screen_name, count, cursor)

        Obtain a collection of the lists the specified user is subscribed to,
        20 lists per page by default. Does not include the user's own lists.

        :param user_id: |user_id|
        :param screen_name: |screen_name|
        :param count: |count|
        :param cursor: |cursor|

        :rtype: list of :class:`List` objects

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/get-lists-subscriptions
        """
        return self.request(
            'GET', 'lists/subscriptions', endpoint_parameters=(
                'user_id', 'screen_name', 'count', 'cursor'
            ), **kwargs
        )

    @payload('list')
    def create_list(self, name, **kwargs):
        """create_list(name, *, mode, description)

        Creates a new list for the authenticated user.
        Note that you can create up to 1000 lists per account.

        :param name: The name of the new list.
        :param mode: |list_mode|
        :param description: The description of the list you are creating.

        :rtype: :class:`List` object

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/post-lists-create
        """
        return self.request(
            'POST', 'lists/create', endpoint_parameters=(
                'name', 'mode', 'description'
            ), name=name, **kwargs
        )

    @payload('list')
    def destroy_list(self, **kwargs):
        """destroy_list(*, owner_screen_name, owner_id, list_id, slug)

        Deletes the specified list.
        The authenticated user must own the list to be able to destroy it.

        :param owner_screen_name: |owner_screen_name|
        :param owner_id: |owner_id|
        :param list_id: |list_id|
        :param slug: |slug|

        :rtype: :class:`List` object

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/post-lists-destroy
        """
        return self.request(
            'POST', 'lists/destroy', endpoint_parameters=(
                'owner_screen_name', 'owner_id', 'list_id', 'slug'
            ), **kwargs
        )

    @payload('list')
    def add_list_member(self, **kwargs):
        """add_list_member(*, list_id, slug, user_id, screen_name, \
                           owner_screen_name, owner_id)

        Add a member to a list. The authenticated user must own the list to be
        able to add members to it. Lists are limited to 5,000 members.

        :param list_id: |list_id|
        :param slug: |slug|
        :param user_id: |user_id|
        :param screen_name: |screen_name|
        :param owner_screen_name: |owner_screen_name|
        :param owner_id: |owner_id|

        :rtype: :class:`List` object

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/post-lists-members-create
        """
        return self.request(
            'POST', 'lists/members/create', endpoint_parameters=(
                'list_id', 'slug', 'user_id', 'screen_name',
                'owner_screen_name', 'owner_id'
            ), **kwargs
        )

    @payload('list')
    def add_list_members(self, **kwargs):
        """add_list_members(*, list_id, slug, user_id, screen_name, \
                            owner_screen_name, owner_id)

        Add up to 100 members to a list. The authenticated user must own the
        list to be able to add members to it. Lists are limited to 5,000
        members.

        :param list_id: |list_id|
        :param slug: |slug|
        :param user_id: A comma separated list of user IDs, up to 100 are
                        allowed in a single request
        :param screen_name: A comma separated list of screen names, up to 100
                            are allowed in a single request
        :param owner_screen_name: |owner_screen_name|
        :param owner_id: |owner_id|

        :rtype: :class:`List` object

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/post-lists-members-create_all
        """
        if 'user_id' in kwargs:
            kwargs['user_id'] = list_to_csv(kwargs['user_id'])
        if 'screen_name' in kwargs:
            kwargs['screen_name'] = list_to_csv(kwargs['screen_name'])
        return self.request(
            'POST', 'lists/members/create_all', endpoint_parameters=(
                'list_id', 'slug', 'user_id', 'screen_name',
                'owner_screen_name', 'owner_id'
            ), **kwargs
        )

    @payload('list')
    def remove_list_member(self, **kwargs):
        """remove_list_member(*, list_id, slug, user_id, screen_name, \
                              owner_screen_name, owner_id)

        Removes the specified member from the list. The authenticated user must
        be the list's owner to remove members from the list.

        :param list_id: |list_id|
        :param slug: |slug|
        :param user_id: |user_id|
        :param screen_name: |screen_name|
        :param owner_screen_name: |owner_screen_name|
        :param owner_id: |owner_id|

        :rtype: :class:`List` object

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/post-lists-members-destroy
        """
        return self.request(
            'POST', 'lists/members/destroy', endpoint_parameters=(
                'list_id', 'slug', 'user_id', 'screen_name',
                'owner_screen_name', 'owner_id'
            ), **kwargs
        )

    @payload('list')
    def remove_list_members(self, **kwargs):
        """remove_list_members(*, list_id, slug, user_id, screen_name, \
                               owner_screen_name, owner_id)

        Remove up to 100 members from a list. The authenticated user must own
        the list to be able to remove members from it. Lists are limited to
        5,000 members.

        :param list_id: |list_id|
        :param slug: |slug|
        :param user_id: A comma separated list of user IDs, up to 100 are
                        allowed in a single request
        :param screen_name: A comma separated list of screen names, up to 100
                            are allowed in a single request
        :param owner_screen_name: |owner_screen_name|
        :param owner_id: |owner_id|

        :rtype: :class:`List` object

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/post-lists-members-destroy_all
        """
        if 'user_id' in kwargs:
            kwargs['user_id'] = list_to_csv(kwargs['user_id'])
        if 'screen_name' in kwargs:
            kwargs['screen_name'] = list_to_csv(kwargs['screen_name'])
        return self.request(
            'POST', 'lists/members/destroy_all', endpoint_parameters=(
                'list_id', 'slug', 'user_id', 'screen_name',
                'owner_screen_name', 'owner_id'
            ), **kwargs
        )

    @payload('list')
    def subscribe_list(self, **kwargs):
        """subscribe_list(*, owner_screen_name, owner_id, list_id, slug)

        Subscribes the authenticated user to the specified list.

        :param owner_screen_name: |owner_screen_name|
        :param owner_id: |owner_id|
        :param list_id: |list_id|
        :param slug: |slug|

        :rtype: :class:`List` object

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/post-lists-subscribers-create
        """
        return self.request(
            'POST', 'lists/subscribers/create', endpoint_parameters=(
                'owner_screen_name', 'owner_id', 'list_id', 'slug'
            ), **kwargs
        )

    @payload('list')
    def unsubscribe_list(self, **kwargs):
        """unsubscribe_list(*, list_id, slug, owner_screen_name, owner_id)

        Unsubscribes the authenticated user from the specified list.

        :param list_id: |list_id|
        :param slug: |slug|
        :param owner_screen_name: |owner_screen_name|
        :param owner_id: |owner_id|

        :rtype: :class:`List` object

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/post-lists-subscribers-destroy
        """
        return self.request(
            'POST', 'lists/subscribers/destroy', endpoint_parameters=(
                'list_id', 'slug', 'owner_screen_name', 'owner_id'
            ), **kwargs
        )

    @payload('list')
    def update_list(self, **kwargs):
        """update_list(*, list_id, slug, name, mode, description, \
                       owner_screen_name, owner_id)

        Updates the specified list.
        The authenticated user must own the list to be able to update it.

        :param list_id: |list_id|
        :param slug: |slug|
        :param name: The name for the list.
        :param mode: |list_mode|
        :param description: The description to give the list.
        :param owner_screen_name: |owner_screen_name|
        :param owner_id: |owner_id|

        :rtype: :class:`List` object

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/post-lists-update
        """
        return self.request(
            'POST', 'lists/update', endpoint_parameters=(
                'list_id', 'slug', 'name', 'mode', 'description',
                'owner_screen_name', 'owner_id'
            ), **kwargs
        )

    # Follow, search, and get users

    @pagination(mode='cursor')
    @payload('ids')
    def followers_ids(self, **kwargs):
        """followers_ids(*, user_id, screen_name, cursor, stringify_ids, count)

        Returns an array containing the IDs of users following the specified
        user.

        :param user_id: |user_id|
        :param screen_name: |screen_name|
        :param cursor: |cursor|
        :param stringify_ids: |stringify_ids|
        :param count: |count|

        :rtype: list of :class:`int`

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-followers-ids
        """
        return self.request(
            'GET', 'followers/ids', endpoint_parameters=(
                'user_id', 'screen_name', 'cursor', 'stringify_ids', 'count'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('user', list=True)
    def followers(self, **kwargs):
        """followers(*, user_id, screen_name, cursor, count, skip_status, \
                     include_user_entities)

        Returns a user's followers ordered in which they were added. If no user
        is specified by id/screen name, it defaults to the authenticated user.

        :param user_id: |user_id|
        :param screen_name: |screen_name|
        :param cursor: |cursor|
        :param count: |count|
        :param skip_status: |skip_status|
        :param include_user_entities: |include_user_entities|

        :rtype: list of :class:`User` objects

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-followers-list
        """
        return self.request(
            'GET', 'followers/list', endpoint_parameters=(
                'user_id', 'screen_name', 'cursor', 'count', 'skip_status',
                'include_user_entities'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('ids')
    def friends_ids(self, **kwargs):
        """friends_ids(*, user_id, screen_name, cursor, stringify_ids, count)

        Returns an array containing the IDs of users being followed by the
        specified user.

        :param user_id: |user_id|
        :param screen_name: |screen_name|
        :param cursor: |cursor|
        :param stringify_ids: |stringify_ids|
        :param count: |count|

        :rtype: list of :class:`int`

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-friends-ids
        """
        return self.request(
            'GET', 'friends/ids', endpoint_parameters=(
                'user_id', 'screen_name', 'cursor', 'stringify_ids', 'count'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('user', list=True)
    def friends(self, **kwargs):
        """friends(*, user_id, screen_name, cursor, count, skip_status, \
                   include_user_entities)

        Returns a user's friends ordered in which they were added 100 at a
        time. If no user is specified it defaults to the authenticated user.

        :param user_id: |user_id|
        :param screen_name: |screen_name|
        :param cursor: |cursor|
        :param count: |count|
        :param skip_status: |skip_status|
        :param include_user_entities: |include_user_entities|

        :rtype: list of :class:`User` objects

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-friends-list
        """
        return self.request(
            'GET', 'friends/list', endpoint_parameters=(
                'user_id', 'screen_name', 'cursor', 'count', 'skip_status',
                'include_user_entities'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('ids')
    def friendships_incoming(self, **kwargs):
        """friendships_incoming(*, cursor, stringify_ids)

        Returns a collection of numeric IDs for every user who has a pending
        request to follow the authenticating user.

        :param cursor: |cursor|
        :param stringify_ids: |stringify_ids|

        :rtype: list of :class:`int`

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-friendships-incoming
        """
        return self.request(
            'GET', 'friendships/incoming', endpoint_parameters=(
                'cursor', 'stringify_ids'
            ), **kwargs
        )

    @payload('relationship', list=True)
    def lookup_friendships(self, *, screen_name=None, user_id=None, **kwargs):
        """lookup_friendships(*, screen_name, user_id)

        Returns the relationships of the authenticated user to the list of up
        to 100 screen_name or user_id provided.

        :param screen_name: A list of screen names, up to 100 are allowed in a
                            single request.
        :param user_id: A list of user IDs, up to 100 are allowed in a single
                        request.

        :rtype: list of :class:`Relationship` objects

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-friendships-lookup
        """
        return self.request(
            'GET', 'friendships/lookup', endpoint_parameters=(
                'screen_name', 'user_id'
            ), screen_name=list_to_csv(screen_name),
            user_id=list_to_csv(user_id), **kwargs
        )

    @payload('ids')
    def no_retweets_friendships(self, **kwargs):
        """no_retweets_friendships(*, stringify_ids)

        Returns a collection of user_ids that the currently authenticated user
        does not want to receive retweets from.

        :param stringify_ids: |stringify_ids|

        :rtype: list of :class:`int`

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-friendships-no_retweets-ids
        """
        return self.request(
            'GET', 'friendships/no_retweets/ids', endpoint_parameters=(
                'stringify_ids',
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('ids')
    def friendships_outgoing(self, **kwargs):
        """friendships_outgoing(*, cursor, stringify_ids)

        Returns a collection of numeric IDs for every protected user for whom
        the authenticating user has a pending follow request.

        :param cursor: |cursor|
        :param stringify_ids: |stringify_ids|

        :rtype: list of :class:`int`

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-friendships-outgoing
        """
        return self.request(
            'GET', 'friendships/outgoing', endpoint_parameters=(
                'cursor', 'stringify_ids'
            ), **kwargs
        )

    @payload('friendship')
    def show_friendship(self, **kwargs):
        """show_friendship(*, source_id, source_screen_name, target_id, \
                           target_screen_name)

        Returns detailed information about the relationship between two users.

        :param source_id: The user_id of the subject user.
        :param source_screen_name: The screen_name of the subject user.
        :param target_id: The user_id of the target user.
        :param target_screen_name: The screen_name of the target user.

        :rtype: :class:`Friendship` object

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-friendships-show
        """
        return self.request(
            'GET', 'friendships/show', endpoint_parameters=(
                'source_id', 'source_screen_name', 'target_id',
                'target_screen_name'
            ), **kwargs
        )

    @payload('user', list=True)
    def lookup_users(self, *, screen_name=None, user_id=None, **kwargs):
        """lookup_users(*, screen_name, user_id, include_entities, tweet_mode)

        Returns fully-hydrated user objects for up to 100 users per request.

        There are a few things to note when using this method.

        * You must be following a protected user to be able to see their most \
            recent status update. If you don't follow a protected user their \
            status will be removed.
        * The order of user IDs or screen names may not match the order of \
            users in the returned array.
        * If a requested user is unknown, suspended, or deleted, then that \
            user will not be returned in the results list.
        * If none of your lookup criteria can be satisfied by returning a \
            user object, a HTTP 404 will be thrown.

        :param screen_name: A list of screen names, up to 100 are allowed in a
                            single request.
        :param user_id: A list of user IDs, up to 100 are allowed in a single
                        request.
        :param include_entities: |include_entities|
        :param tweet_mode: Valid request values are compat and extended, which
                           give compatibility mode and extended mode,
                           respectively for Tweets that contain over 140
                           characters.

        :rtype: list of :class:`User` objects

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-users-lookup
        """
        return self.request(
            'POST', 'users/lookup', endpoint_parameters=(
                'screen_name', 'user_id', 'include_entities', 'tweet_mode'
            ), screen_name=list_to_csv(screen_name),
            user_id=list_to_csv(user_id), **kwargs
        )

    @pagination(mode='page')
    @payload('user', list=True)
    def search_users(self, q, **kwargs):
        """search_users(q, *, page, count, include_entities)

        Run a search for users similar to Find People button on Twitter.com;
        the same results returned by people search on Twitter.com will be
        returned by using this API (about being listed in the People Search).
        It is only possible to retrieve the first 1000 matches from this API.

        :param q: The query to run against people search.
        :param page: |page|
        :param count: |count|
        :param include_entities: |include_entities|

        :rtype: list of :class:`User` objects

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-users-search
        """
        return self.request(
            'GET', 'users/search', endpoint_parameters=(
                'q', 'page', 'count', 'include_entities'
            ), q=q, **kwargs
        )

    @payload('user')
    def get_user(self, **kwargs):
        """get_user(*, user_id, screen_name, include_entities)

        Returns information about the specified user.

        :param user_id: |user_id|
        :param screen_name: |screen_name|
        :param include_entities: |include_entities|

        :rtype: :class:`User` object

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-users-show
        """
        return self.request(
            'GET', 'users/show', endpoint_parameters=(
                'user_id', 'screen_name', 'include_entities'
            ), **kwargs
        )

    @payload('user')
    def create_friendship(self, **kwargs):
        """create_friendship(*, screen_name, user_id, follow)

        Create a new friendship with the specified user (aka follow).

        :param screen_name: |screen_name|
        :param user_id: |user_id|
        :param follow: Enable notifications for the target user in addition to
                       becoming friends.

        :rtype: :class:`User` object

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/post-friendships-create
        """
        return self.request(
            'POST', 'friendships/create', endpoint_parameters=(
                'screen_name', 'user_id', 'follow'
            ), **kwargs
        )

    @payload('user')
    def destroy_friendship(self, **kwargs):
        """destroy_friendship(*, screen_name, user_id)

        Destroy a friendship with the specified user (aka unfollow).

        :param screen_name: |screen_name|
        :param user_id: |user_id|

        :rtype: :class:`User` object

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/post-friendships-destroy
        """
        return self.request(
            'POST', 'friendships/destroy', endpoint_parameters=(
                'screen_name', 'user_id'
            ), **kwargs
        )

    @payload('friendship')
    def update_friendship(self, **kwargs):
        """update_friendship(*, screen_name, user_id, device, retweets)

        Turn on/off Retweets and device notifications from the specified user.

        :param screen_name: |screen_name|
        :param user_id: |user_id|
        :param device: Turn on/off device notifications from the target user.
        :param retweets: Turn on/off Retweets from the target user.

        :rtype: :class:`Friendship` object

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/post-friendships-update
        """
        return self.request(
            'POST', 'friendships/update', endpoint_parameters=(
                'screen_name', 'user_id', 'device', 'retweets'
            ), **kwargs
        )

    # Manage account settings and profile

    @payload('json')
    def get_settings(self, **kwargs):
        """get_settings()

        Returns settings (including current trend, geo and sleep time
        information) for the authenticating user.

        :rtype: :class:`JSON` object

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/get-account-settings
        """
        return self.request(
            'GET', 'account/settings', use_cache=False, **kwargs
        )

    @payload('user')
    def verify_credentials(self, **kwargs):
        """verify_credentials(*, include_entities, skip_status, include_email)

        Verify the supplied user credentials are valid.

        :param include_entities: |include_entities|
        :param skip_status: |skip_status|
        :param include_email: When set to true email will be returned in the
                              user objects as a string.

        :rtype: :class:`User` object if credentials are valid, otherwise False

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/get-account-verify_credentials
        """
        if 'include_email' in kwargs:
            kwargs['include_email'] = str(kwargs['include_email']).lower()
        return self.request(
            'GET', 'account/verify_credentials', endpoint_parameters=(
                'include_entities', 'skip_status', 'include_email'
            ), **kwargs
        )

    @payload('saved_search', list=True)
    def saved_searches(self, **kwargs):
        """saved_searches()

        Returns the authenticated user's saved search queries.

        :rtype: list of :class:`SavedSearch` objects

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/get-saved_searches-list
        """
        return self.request('GET', 'saved_searches/list', **kwargs)

    @payload('saved_search')
    def get_saved_search(self, id, **kwargs):
        """get_saved_search(id)

        Retrieve the data for a saved search owned by the authenticating user
        specified by the given ID.

        :param id: The ID of the saved search to be retrieved.

        :rtype: :class:`SavedSearch` object

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/get-saved_searches-show-id
        """
        return self.request('GET', f'saved_searches/show/{id}', **kwargs)

    @payload('json')
    def get_profile_banner(self, **kwargs):
        """get_profile_banner(*, user_id, screen_name)

        Returns a map of the available size variations of the specified user's
        profile banner. If the user has not uploaded a profile banner, a HTTP
        404 will be served instead.

        The profile banner data available at each size variant's URL is in PNG
        format.

        :param user_id: |user_id|
        :param screen_name: |screen_name|

        :rtype: :class:`JSON` object

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/get-users-profile_banner
        """
        return self.request(
            'GET', 'users/profile_banner', endpoint_parameters=(
                'user_id', 'screen_name'
            ), **kwargs
        )

    def remove_profile_banner(self, **kwargs):
        """remove_profile_banner()

        Removes the uploaded profile banner for the authenticating user.

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/post-account-remove_profile_banner
        """
        return self.request('POST', 'account/remove_profile_banner', **kwargs)

    @payload('json')
    def set_settings(self, **kwargs):
        """set_settings(*, sleep_time_enabled, start_sleep_time, \
                        end_sleep_time, time_zone, trend_location_woeid, lang)
        
        Updates the authenticating user's settings.

        :param sleep_time_enabled: When set to ``true``, ``t`` or ``1`` , will
            enable sleep time for the user. Sleep time is the time when push or
            SMS notifications should not be sent to the user.
        :param start_sleep_time: The hour that sleep time should begin if it is
            enabled. The value for this parameter should be provided in
            `ISO 8601`_ format (i.e. 00-23). The time is considered to be in
            the same timezone as the user's ``time_zone`` setting.
        :param end_sleep_time: The hour that sleep time should end if it is
            enabled. The value for this parameter should be provided in
            `ISO 8601`_ format (i.e. 00-23). The time is considered to be in
            the same timezone as the user's ``time_zone`` setting.
        :param time_zone: The timezone dates and times should be displayed in
            for the user. The timezone must be one of the `Rails TimeZone`_
            names.
        :param trend_location_woeid: The Yahoo! Where On Earth ID to use as the
            user's default trend location. Global information is available by
            using 1 as the WOEID.
        :param lang: The language which Twitter should render in for this user.
            The language must be specified by the appropriate two letter ISO
            639-1 representation.

        :rtype: :class:`JSON` object

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/post-account-settings

        .. _ISO 8601: https://en.wikipedia.org/wiki/ISO_8601
        .. _Rails TimeZone: https://api.rubyonrails.org/classes/ActiveSupport/TimeZone.html
        """
        return self.request(
            'POST', 'account/settings', endpoint_parameters=(
                'sleep_time_enabled', 'start_sleep_time', 'end_sleep_time',
                'time_zone', 'trend_location_woeid', 'lang'
            ), use_cache=False, **kwargs
        )

    @payload('user')
    def update_profile(self, **kwargs):
        """update_profile(*, name, url, location, description, \
                          profile_link_color, include_entities, skip_status)

        Sets values that users are able to set under the "Account" tab of their
        settings page.

        :param name: Full name associated with the profile.
        :param url: URL associated with the profile. Will be prepended with
                    ``http://`` if not present
        :param location: The city or country describing where the user of the
            account is located. The contents are not normalized or geocoded in
            any way.
        :param description: A description of the user owning the account.
        :param profile_link_color: Sets a hex value that controls the color
            scheme of links used on the authenticating user's profile page on
            twitter.com. This must be a valid hexadecimal value, and may be
            either three or six characters (ex: F00 or FF0000).
        :param include_entities: |include_entities|
        :param skip_status: |skip_status|

        :rtype: :class:`User` object

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/post-account-update_profile
        """
        return self.request(
            'POST', 'account/update_profile', endpoint_parameters=(
                'name', 'url', 'location', 'description', 'profile_link_color',
                'include_entities', 'skip_status'
            ), **kwargs
        )

    def update_profile_banner(self, filename, *, file=None, **kwargs):
        """update_profile_banner(filename, *, file, width, height, \
                                 offset_left, offset_top)

        Uploads a profile banner on behalf of the authenticating user.

        :param filename: |filename|
        :param file: |file|
        :param width: The width of the preferred section of the image being
            uploaded in pixels. Use with ``height``, ``offset_left``, and
            ``offset_top`` to select the desired region of the image to use.
        :param height: The height of the preferred section of the image being
            uploaded in pixels. Use with ``width``, ``offset_left``, and
            ``offset_top`` to select the desired region of the image to use.
        :param offset_left: The number of pixels by which to offset the
            uploaded image from the left. Use with ``height``, ``width``, and
            ``offset_top`` to select the desired region of the image to use.
        :param offset_top: The number of pixels by which to offset the uploaded
            image from the top. Use with ``height``, ``width``, and
            ``offset_left`` to select the desired region of the image to use.

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/post-account-update_profile_banner
        """
        if file is not None:
            files = {'banner': (filename, file)}
        else:
            files = {'banner': open(filename, 'rb')}
        return self.request(
            'POST', 'account/update_profile_banner', endpoint_parameters=(
                'width', 'height', 'offset_left', 'offset_top'
            ), files=files, **kwargs
        )

    @payload('user')
    def update_profile_image(self, filename, *, file=None, **kwargs):
        """update_profile_image(filename, *, file, include_entities, \
                                skip_status)

        Update the authenticating user's profile image. Valid formats: GIF,
        JPG, or PNG

        :param filename: |filename|
        :param file: |file|
        :param include_entities: |include_entities|
        :param skip_status: |skip_status|

        :rtype: :class:`User` object

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/post-account-update_profile_image
        """
        if file is not None:
            files = {'image': (filename, file)}
        else:
            files = {'image': open(filename, 'rb')}
        return self.request(
            'POST', 'account/update_profile_image', endpoint_parameters=(
                'include_entities', 'skip_status'
            ), files=files, **kwargs
        )

    @payload('saved_search')
    def create_saved_search(self, query, **kwargs):
        """create_saved_search(query)

        Creates a saved search for the authenticated user.

        :param query: The query of the search the user would like to save.

        :rtype: :class:`SavedSearch` object

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/post-saved_searches-create
        """
        return self.request(
            'POST', 'saved_searches/create', endpoint_parameters=(
                'query',
            ), query=query, **kwargs
        )

    @payload('saved_search')
    def destroy_saved_search(self, id, **kwargs):
        """destroy_saved_search(id)

        Destroys a saved search for the authenticated user. The search
        specified by ID must be owned by the authenticating user.

        :param id: The ID of the saved search to be deleted.

        :rtype: :class:`SavedSearch` object

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/post-saved_searches-destroy-id
        """
        return self.request('POST', f'saved_searches/destroy/{id}', **kwargs)

    # Mute, block, and report users

    @pagination(mode='cursor')
    @payload('ids')
    def blocks_ids(self, **kwargs):
        """blocks_ids(*, stringify_ids, cursor)

        Returns an array of numeric user IDs the authenticating user is
        blocking.

        :param stringify_ids: |stringify_ids|
        :param cursor: |cursor|

        :rtype: list of :class:`int`

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/mute-block-report-users/api-reference/get-blocks-ids
        """
        return self.request(
            'GET', 'blocks/ids', endpoint_parameters=(
                'stringify_ids', 'cursor',
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('user', list=True)
    def blocks(self, **kwargs):
        """blocks(*, include_entities, skip_status, cursor)

        Returns an array of user objects that the authenticating user is
        blocking.

        :param include_entities: |include_entities|
        :param skip_status: |skip_status|
        :param cursor: |cursor|

        :rtype: list of :class:`User` objects

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/mute-block-report-users/api-reference/get-blocks-list
        """
        return self.request(
            'GET', 'blocks/list', endpoint_parameters=(
                'include_entities', 'skip_status', 'cursor'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('ids')
    def mutes_ids(self, **kwargs):
        """mutes_ids(*, stringify_ids, cursor)

        Returns an array of numeric user IDs the authenticating user has muted.

        :param stringify_ids: |stringify_ids|
        :param cursor: |cursor|

        :rtype: list of :class:`int`

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/mute-block-report-users/api-reference/get-mutes-users-ids
        """
        return self.request(
            'GET', 'mutes/users/ids', endpoint_parameters=(
                'stringify_ids', 'cursor'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('user', list=True)
    def mutes(self, **kwargs):
        """mutes(*, cursor, include_entities, skip_status)

        Returns an array of user objects the authenticating user has muted.

        :param cursor: |cursor|
        :param include_entities: |include_entities|
        :param skip_status: |skip_status|

        :rtype: list of :class:`User` objects

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/mute-block-report-users/api-reference/get-mutes-users-list
        """
        return self.request(
            'GET', 'mutes/users/list', endpoint_parameters=(
                'cursor', 'include_entities', 'skip_status'
            ), **kwargs
        )

    @payload('user')
    def create_block(self, **kwargs):
        """create_block(*, screen_name, user_id, include_entities, skip_status)

        Blocks the specified user from following the authenticating user. In
        addition the blocked user will not show in the authenticating users
        mentions or timeline (unless retweeted by another user). If a follow or
        friend relationship exists it is destroyed.

        :param screen_name: |screen_name|
        :param user_id: |user_id|
        :param include_entities: |include_entities|
        :param skip_status: |skip_status|

        :rtype: :class:`User` object

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/mute-block-report-users/api-reference/post-blocks-create
        """
        return self.request(
            'POST', 'blocks/create', endpoint_parameters=(
                'screen_name', 'user_id', 'include_entities', 'skip_status'
            ), **kwargs
        )

    @payload('user')
    def destroy_block(self, **kwargs):
        """destroy_block(*, screen_name, user_id, include_entities, \
                         skip_status)

        Un-blocks the user specified in the ID parameter for the authenticating
        user.

        :param screen_name: |screen_name|
        :param user_id: |user_id|
        :param include_entities: |include_entities|
        :param skip_status: |skip_status|

        :rtype: :class:`User` object

        :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/mute-block-report-users/api-reference/post-blocks-destroy
        """
        return self.request(
            'POST', 'blocks/destroy', endpoint_parameters=(
                'screen_name', 'user_id', 'include_entities', 'skip_status'
            ), **kwargs
        )

    def media_upload(self, filename, *, file=None, chunked=False,
                     media_category=None, additional_owners=None, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/media/upload-media/overview
        """
        h = None
        if file is not None:
            location = file.tell()
            h = file.read(32)
            file.seek(location)
        file_type = imghdr.what(filename, h=h)
        if file_type is not None:
            file_type = 'image/' + file_type
        else:
            file_type = mimetypes.guess_type(filename)[0]

        if chunked or file_type.startswith('video/'):
            return self.chunked_upload(
                filename, file=file, file_type=file_type,
                media_category=media_category,
                additional_owners=additional_owners, **kwargs
            )
        else:
            return self.simple_upload(
                filename, file=file, media_category=media_category,
                additional_owners=additional_owners, **kwargs
            )

    @payload('media')
    def simple_upload(self, filename, *, file=None, media_category=None,
                      additional_owners=None, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/media/upload-media/api-reference/post-media-upload
        """
        if file is not None:
            files = {'media': (filename, file)}
        else:
            files = {'media': open(filename, 'rb')}

        post_data = {}
        if media_category is not None:
            post_data['media_category'] = media_category
        if additional_owners is not None:
            post_data['additional_owners'] = additional_owners

        return self.request(
            'POST', 'media/upload', post_data=post_data, files=files,
            upload_api=True, **kwargs
        )

    def chunked_upload(self, filename, *, file=None, file_type=None,
                       wait_for_async_finalize=True, media_category=None,
                       additional_owners=None, **kwargs):
        """ :reference https://developer.twitter.com/en/docs/twitter-api/v1/media/upload-media/uploading-media/chunked-media-upload
        """
        fp = file or open(filename, 'rb')

        start = fp.tell()
        fp.seek(0, 2)  # Seek to end of file
        file_size = fp.tell() - start
        fp.seek(start)

        media_id = self.chunked_upload_init(
            file_size, file_type, media_category=media_category,
            additional_owners=additional_owners, **kwargs
        ).media_id

        min_chunk_size, remainder = divmod(file_size, 1000)
        min_chunk_size += bool(remainder)

        # Use 1 MiB as default chunk size
        chunk_size = kwargs.pop('chunk_size', 1024 * 1024)
        # Max chunk size is 5 MiB
        chunk_size = max(min(chunk_size, 5 * 1024 * 1024), min_chunk_size)

        segments, remainder = divmod(file_size, chunk_size)
        segments += bool(remainder)

        for segment_index in range(segments):
            # The APPEND command returns an empty response body
            self.chunked_upload_append(
                media_id, (filename, fp.read(chunk_size)), segment_index,
                **kwargs
            )

        fp.close()
        media =  self.chunked_upload_finalize(media_id, **kwargs)

        if wait_for_async_finalize and hasattr(media, 'processing_info'):
            while media.processing_info['state'] in ('pending', 'in_progress'):
                time.sleep(media.processing_info['check_after_secs'])
                media = self.get_media_upload_status(media.media_id, **kwargs)

        return media

    @payload('media')
    def chunked_upload_init(self, total_bytes, media_type, *,
                            media_category=None, additional_owners=None,
                            **kwargs):
        """ :reference https://developer.twitter.com/en/docs/twitter-api/v1/media/upload-media/api-reference/post-media-upload-init
        """
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        post_data = {
            'command': 'INIT',
            'total_bytes': total_bytes,
            'media_type': media_type,
        }
        if media_category is not None:
            post_data['media_category'] = media_category
        if additional_owners is not None:
            post_data['additional_owners'] = list_to_csv(additional_owners)

        return self.request(
            'POST', 'media/upload', headers=headers, post_data=post_data,
            upload_api=True, **kwargs
        )

    def chunked_upload_append(self, media_id, media, segment_index, **kwargs):
        """ :reference https://developer.twitter.com/en/docs/twitter-api/v1/media/upload-media/api-reference/post-media-upload-append
        """
        post_data = {
            'command': 'APPEND',
            'media_id': media_id,
            'segment_index': segment_index
        }
        files = {'media': media}
        return self.request(
            'POST', 'media/upload', post_data=post_data, files=files,
            upload_api=True, **kwargs
        )

    @payload('media')
    def chunked_upload_finalize(self, media_id, **kwargs):
        """ :reference https://developer.twitter.com/en/docs/twitter-api/v1/media/upload-media/api-reference/post-media-upload-finalize
        """
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        post_data = {
            'command': 'FINALIZE',
            'media_id': media_id
        }
        return self.request(
            'POST', 'media/upload', headers=headers, post_data=post_data,
            upload_api=True, **kwargs
        )

    def create_media_metadata(self, media_id, alt_text, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/media/upload-media/api-reference/post-media-metadata-create
        """
        json_payload = {
            'media_id': media_id,
            'alt_text': {'text': alt_text}
        }

        return self.request(
            'POST', 'media/metadata/create', json_payload=json_payload,
            upload_api=True, **kwargs
        )

    @payload('media')
    def get_media_upload_status(self, media_id, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/media/upload-media/api-reference/get-media-upload-status
        """
        return self.request(
            'GET', 'media/upload', endpoint_parameters=(
                'command', 'media_id'
            ), command='STATUS', media_id=media_id, upload_api=True, **kwargs
        )

    @payload('direct_message')
    def get_direct_message(self, id, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/direct-messages/sending-and-receiving/api-reference/get-event
        """
        return self.request(
            'GET', 'direct_messages/events/show', endpoint_parameters=(
                'id',
            ), id=id, **kwargs
        )

    @pagination(mode='dm_cursor')
    @payload('direct_message', list=True)
    def list_direct_messages(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/direct-messages/sending-and-receiving/api-reference/list-events
        """
        return self.request(
            'GET', 'direct_messages/events/list', endpoint_parameters=(
                'count', 'cursor'
            ), **kwargs
        )

    @payload('direct_message')
    def send_direct_message(self, recipient_id, text, *, quick_reply_options=None,
                            attachment_type=None, attachment_media_id=None,
                            ctas=None, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/direct-messages/sending-and-receiving/api-reference/new-event
        """
        json_payload = {
            'event': {'type': 'message_create',
                      'message_create': {
                          'target': {'recipient_id': recipient_id},
                          'message_data': {'text': text}
                      }
            }
        }
        message_data = json_payload['event']['message_create']['message_data']
        if quick_reply_options is not None:
            message_data['quick_reply'] = {
                'type': 'options',
                'options': quick_reply_options
            }
        if attachment_type is not None and attachment_media_id is not None:
            message_data['attachment'] = {
                'type': attachment_type,
                'media': {'id': attachment_media_id}
            }
        if ctas is not None:
            message_data['ctas'] = ctas
        return self.request(
            'POST', 'direct_messages/events/new',
            json_payload=json_payload, **kwargs
        )

    def destroy_direct_message(self, id, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/direct-messages/sending-and-receiving/api-reference/delete-message-event
        """
        return self.request(
            'DELETE', 'direct_messages/events/destroy', endpoint_parameters=(
                'id',
            ), id=id, **kwargs
        )

    @payload('json')
    def rate_limit_status(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/developer-utilities/rate-limit-status/api-reference/get-application-rate_limit_status
        """
        return self.request(
            'GET', 'application/rate_limit_status', endpoint_parameters=(
                'resources',
            ), use_cache=False, **kwargs
        )

    @payload('user')
    def create_mute(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/mute-block-report-users/api-reference/post-mutes-users-create
        """
        return self.request(
            'POST', 'mutes/users/create', endpoint_parameters=(
                'screen_name', 'user_id'
            ), **kwargs
        )

    @payload('user')
    def destroy_mute(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/mute-block-report-users/api-reference/post-mutes-users-destroy
        """
        return self.request(
            'POST', 'mutes/users/destroy', endpoint_parameters=(
                'screen_name', 'user_id'
            ), **kwargs
        )

    @payload('user')
    def report_spam(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/mute-block-report-users/api-reference/post-users-report_spam
        """
        return self.request(
            'POST', 'users/report_spam', endpoint_parameters=(
                'screen_name', 'user_id', 'perform_block'
            ), **kwargs
        )

    @payload('json')
    def trends_available(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/trends/locations-with-trending-topics/api-reference/get-trends-available
        """
        return self.request('GET', 'trends/available', **kwargs)

    @payload('json')
    def trends_place(self, id, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/trends/trends-for-location/api-reference/get-trends-place
        """
        return self.request(
            'GET', 'trends/place', endpoint_parameters=(
                'id', 'exclude'
            ), id=id, **kwargs
        )

    @payload('json')
    def trends_closest(self, lat, long, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/trends/locations-with-trending-topics/api-reference/get-trends-closest
        """
        return self.request(
            'GET', 'trends/closest', endpoint_parameters=(
                'lat', 'long'
            ), lat=lat, long=long, **kwargs
        )

    @pagination(mode='next')
    @payload('status', list=True)
    def search_30_day(self, label, query, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/premium/search-api/api-reference/premium-search
        """
        return self.request(
            'GET', f'tweets/search/30day/{label}', endpoint_parameters=(
                'query', 'tag', 'fromDate', 'toDate', 'maxResults', 'next'
            ), query=query, **kwargs
        )

    @pagination(mode='next')
    @payload('status', list=True)
    def search_full_archive(self, label, query, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/premium/search-api/api-reference/premium-search
        """
        return self.request(
            'GET', f'tweets/search/fullarchive/{label}', endpoint_parameters=(
                'query', 'tag', 'fromDate', 'toDate', 'maxResults', 'next'
            ), query=query, **kwargs
        )

    @payload('place', list=True)
    def reverse_geocode(self, lat, long, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/geo/places-near-location/api-reference/get-geo-reverse_geocode
        """
        return self.request(
            'GET', 'geo/reverse_geocode', endpoint_parameters=(
                'lat', 'long', 'accuracy', 'granularity', 'max_results'
            ), lat=lat, long=long, **kwargs
        )

    @payload('place')
    def geo_id(self, place_id, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/geo/place-information/api-reference/get-geo-id-place_id
        """
        return self.request('GET', f'geo/id/{place_id}', **kwargs)

    @payload('place', list=True)
    def geo_search(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/geo/places-near-location/api-reference/get-geo-search
        """
        return self.request(
            'GET', 'geo/search', endpoint_parameters=(
                'lat', 'long', 'query', 'ip', 'granularity', 'max_results'
            ), **kwargs
        )

    @payload('json')
    def supported_languages(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/developer-utilities/supported-languages/api-reference/get-help-languages
        """
        return self.request('GET', 'help/languages', **kwargs)

    @payload('json')
    def configuration(self, **kwargs):
        """ :reference: https://developer.twitter.com/en/docs/twitter-api/v1/developer-utilities/configuration/api-reference/get-help-configuration
        """
        return self.request('GET', 'help/configuration', **kwargs)
