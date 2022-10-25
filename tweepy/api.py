# Tweepy
# Copyright 2009-2022 Joshua Roesslein
# See LICENSE for details.

import contextlib
import functools
import imghdr
import logging
import mimetypes
from platform import python_version
import sys
import time
from urllib.parse import urlencode

import requests

import tweepy
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
    """Twitter API v1.1 Interface

    .. versionchanged:: 4.11
        Added support for ``include_ext_edit_control`` endpoint/method
        parameter

    Parameters
    ----------
    auth
        The authentication handler to be used
    cache
        The cache to query if a GET method is used
    host
        The general REST API host server URL
    parser
        The Parser instance to use for parsing the response from Twitter;
        defaults to an instance of ModelParser
    proxy
        The full url to an HTTPS proxy to use for connecting to Twitter
    retry_count
        Number of retries to attempt when an error occurs
    retry_delay
        Number of seconds to wait between retries
    retry_errors
        Which HTTP status codes to retry
    timeout
        The maximum amount of time to wait for a response from Twitter
    upload_host
        The URL of the upload server
    wait_on_rate_limit
        Whether or not to automatically wait for rate limits to replenish

    Raises
    ------
    TypeError
        If the given parser is not a Parser instance

    References
    ----------
    https://developer.twitter.com/en/docs/api-reference-index
    """

    def __init__(
        self, auth=None, *, cache=None, host='api.twitter.com', parser=None,
        proxy=None, retry_count=0, retry_delay=0, retry_errors=None,
        timeout=60, upload_host='upload.twitter.com', user_agent=None,
        wait_on_rate_limit=False
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

        if user_agent is None:
            user_agent = (
                f"Python/{python_version()} "
                f"Requests/{requests.__version__} "
                f"Tweepy/{tweepy.__version__}"
            )
        self.user_agent = user_agent

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

        if headers is None:
            headers = {}
        headers["User-Agent"] = self.user_agent

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
            if k not in endpoint_parameters + (
                "include_ext_edit_control", "tweet_mode"
            ):
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

    # Premium Search APIs

    @pagination(mode='next')
    @payload('status', list=True)
    def search_30_day(self, label, query, **kwargs):
        """search_30_day(label, query, *, tag, fromDate, toDate, maxResults, \
                         next)

        Premium search that provides Tweets posted within the last 30 days.

        Parameters
        ----------
        label
            The (case-sensitive) label associated with your search developer
            environment, as displayed at
            https://developer.twitter.com/en/account/environments.
        query
            The equivalent of one premium rule/filter, with up to 1,024
            characters (256 with Sandbox dev environments).

            This parameter should include ALL portions of the rule/filter,
            including all operators, and portions of the rule should not be
            separated into other parameters of the query.
        tag
            Tags can be used to segregate rules and their matching data into
            different logical groups. If a rule tag is provided, the rule tag
            is included in the 'matching_rules' attribute.

            It is recommended to assign rule-specific UUIDs to rule tags and
            maintain desired mappings on the client side.
        fromDate
            The oldest UTC timestamp (from most recent 30 days) from which the
            Tweets will be provided. Timestamp is in minute granularity and is
            inclusive (i.e. 12:00 includes the 00 minute).

            Specified: Using only the fromDate with no toDate parameter will
            deliver results for the query going back in time from now( ) until
            the fromDate.

            Not Specified: If a fromDate is not specified, the API will deliver
            all of the results for 30 days prior to now( ) or the toDate (if
            specified).

            If neither the fromDate or toDate parameter is used, the API will
            deliver all results for the most recent 30 days, starting at the
            time of the request, going backwards.
        toDate
            The latest, most recent UTC timestamp to which the Tweets will be
            provided. Timestamp is in minute granularity and is not inclusive
            (i.e. 11:59 does not include the 59th minute of the hour).

            Specified: Using only the toDate with no fromDate parameter will
            deliver the most recent 30 days of data prior to the toDate.

            Not Specified: If a toDate is not specified, the API will deliver
            all of the results from now( ) for the query going back in time to
            the fromDate.

            If neither the fromDate or toDate parameter is used, the API will
            deliver all results for the entire 30-day index, starting at the
            time of the request, going backwards.
        maxResults
            The maximum number of search results to be returned by a request. A
            number between 10 and the system limit (currently 500, 100 for
            Sandbox environments). By default, a request response will return
            100 results.
        next
            This parameter is used to get the next 'page' of results. The value
            used with the parameter is pulled directly from the response
            provided by the API, and should not be modified.

        Returns
        -------
        :py:class:`List`\[:class:`~tweepy.models.Status`]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/premium/search-api/api-reference/premium-search
        """
        return self.request(
            'GET', f'tweets/search/30day/{label}', endpoint_parameters=(
                'query', 'tag', 'fromDate', 'toDate', 'maxResults', 'next'
            ), query=query, **kwargs
        )

    @pagination(mode='next')
    @payload('status', list=True)
    def search_full_archive(self, label, query, **kwargs):
        """search_full_archive(label, query, *, tag, fromDate, toDate, \
                               maxResults, next)

        Premium search that provides Tweets from as early as 2006, starting
        with the first Tweet posted in March 2006.

        Parameters
        ----------
        label
            The (case-sensitive) label associated with your search developer
            environment, as displayed at
            https://developer.twitter.com/en/account/environments.
        query
            The equivalent of one premium rule/filter, with up to 1,024
            characters (256 with Sandbox dev environments).

            This parameter should include ALL portions of the rule/filter,
            including all operators, and portions of the rule should not be
            separated into other parameters of the query.
        tag
            Tags can be used to segregate rules and their matching data into
            different logical groups. If a rule tag is provided, the rule tag
            is included in the 'matching_rules' attribute.

            It is recommended to assign rule-specific UUIDs to rule tags and
            maintain desired mappings on the client side.
        fromDate
            The oldest UTC timestamp (from most recent 30 days) from which the
            Tweets will be provided. Timestamp is in minute granularity and is
            inclusive (i.e. 12:00 includes the 00 minute).

            Specified: Using only the fromDate with no toDate parameter will
            deliver results for the query going back in time from now( ) until
            the fromDate.

            Not Specified: If a fromDate is not specified, the API will deliver
            all of the results for 30 days prior to now( ) or the toDate (if
            specified).

            If neither the fromDate or toDate parameter is used, the API will
            deliver all results for the most recent 30 days, starting at the
            time of the request, going backwards.
        toDate
            The latest, most recent UTC timestamp to which the Tweets will be
            provided. Timestamp is in minute granularity and is not inclusive
            (i.e. 11:59 does not include the 59th minute of the hour).

            Specified: Using only the toDate with no fromDate parameter will
            deliver the most recent 30 days of data prior to the toDate.

            Not Specified: If a toDate is not specified, the API will deliver
            all of the results from now( ) for the query going back in time to
            the fromDate.

            If neither the fromDate or toDate parameter is used, the API will
            deliver all results for the entire 30-day index, starting at the
            time of the request, going backwards.
        maxResults
            The maximum number of search results to be returned by a request. A
            number between 10 and the system limit (currently 500, 100 for
            Sandbox environments). By default, a request response will return
            100 results.
        next
            This parameter is used to get the next 'page' of results. The value
            used with the parameter is pulled directly from the response
            provided by the API, and should not be modified.

        Returns
        -------
        :py:class:`List`\[:class:`~tweepy.models.Status`]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/premium/search-api/api-reference/premium-search
        """
        return self.request(
            'GET', f'tweets/search/fullarchive/{label}', endpoint_parameters=(
                'query', 'tag', 'fromDate', 'toDate', 'maxResults', 'next'
            ), query=query, **kwargs
        )

    # Get Tweet timelines

    @pagination(mode='id')
    @payload('status', list=True)
    def home_timeline(self, **kwargs):
        """home_timeline(*, count, since_id, max_id, trim_user, \
                         exclude_replies, include_entities)

        Returns the 20 most recent statuses, including retweets, posted by
        the authenticating user and that user's friends. This is the equivalent
        of /timeline/home on the Web.

        Parameters
        ----------
        count
            |count|
        since_id
            |since_id|
        max_id
            |max_id|
        trim_user
            |trim_user|
        exclude_replies
            |exclude_replies|
        include_entities
            |include_entities|

        Returns
        -------
        :py:class:`List`\[:class:`~tweepy.models.Status`]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/tweets/timelines/api-reference/get-statuses-home_timeline
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

        Parameters
        ----------
        count
            |count|
        since_id
            |since_id|
        max_id
            |max_id|
        trim_user
            |trim_user|
        include_entities
            |include_entities|

        Returns
        -------
        :py:class:`List`\[:class:`~tweepy.models.Status`]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/tweets/timelines/api-reference/get-statuses-mentions_timeline
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

        Parameters
        ----------
        user_id
            |user_id|
        screen_name
            |screen_name|
        since_id
            |since_id|
        count
            |count|
        max_id
            |max_id|
        trim_user
            |trim_user|
        exclude_replies
            |exclude_replies|
        include_rts
            When set to ``false``, the timeline will strip any native retweets
            (though they will still count toward both the maximal length of the
            timeline and the slice selected by the count parameter). Note: If
            you're using the trim_user parameter in conjunction with
            include_rts, the retweets will still contain a full user object.

        Returns
        -------
        :py:class:`List`\[:class:`~tweepy.models.Status`]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/tweets/timelines/api-reference/get-statuses-user_timeline
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
    def get_favorites(self, **kwargs):
        """get_favorites(*, user_id, screen_name, count, since_id, max_id, \
                         include_entities)

        Returns the favorite statuses for the authenticating user or user
        specified by the ID parameter.

        .. versionchanged:: 4.0
            Renamed from ``API.favorites``

        Parameters
        ----------
        user_id
            |user_id|
        screen_name
            |screen_name|
        count
            |count|
        since_id
            |since_id|
        max_id
            |max_id|
        include_entities
            |include_entities|

        Returns
        -------
        :py:class:`List`\[:class:`~tweepy.models.Status`]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/get-favorites-list
        """
        return self.request(
            'GET', 'favorites/list', endpoint_parameters=(
                'user_id', 'screen_name', 'count', 'since_id', 'max_id',
                'include_entities'
            ), **kwargs
        )

    @payload('status', list=True)
    def lookup_statuses(self, id, **kwargs):
        """lookup_statuses(id, *, include_entities, trim_user, map, \
                           include_ext_alt_text, include_card_uri)

        Returns full Tweet objects for up to 100 Tweets per request, specified
        by the ``id`` parameter.

        .. versionchanged:: 4.0
            Renamed from ``API.statuses_lookup``

        Parameters
        ----------
        id
            A list of Tweet IDs to lookup, up to 100
        include_entities
            |include_entities|
        trim_user
            |trim_user|
        map
            A boolean indicating whether or not to include Tweets that cannot
            be shown. Defaults to False.
        include_ext_alt_text
            |include_ext_alt_text|
        include_card_uri
            |include_card_uri|

        Returns
        -------
        :py:class:`List`\[:class:`~tweepy.models.Status`]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/get-statuses-lookup
        """
        return self.request(
            'GET', 'statuses/lookup', endpoint_parameters=(
                'id', 'include_entities', 'trim_user', 'map',
                'include_ext_alt_text', 'include_card_uri'
            ), id=list_to_csv(id), **kwargs
        )

    @payload('json')
    def get_oembed(self, url, **kwargs):
        """get_oembed( \
            url, *, maxwidth, hide_media, hide_thread, omit_script, align, \
            related, lang, theme, link_color, widget_type, dnt \
        )

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

        Parameters
        ----------
        url
            The URL of the Tweet to be embedded
        maxwidth
            The maximum width of a rendered Tweet in whole pixels. A supplied
            value under or over the allowed range will be returned as the
            minimum or maximum supported width respectively; the reset width
            value will be reflected in the returned ``width`` property. Note
            that Twitter does not support the oEmbed ``maxheight`` parameter.
            Tweets are fundamentally text, and are therefore of unpredictable
            height that cannot be scaled like an image or video. Relatedly, the
            oEmbed response will not provide a value for ``height``.
            Implementations that need consistent heights for Tweets should
            refer to the ``hide_thread`` and ``hide_media`` parameters below.
        hide_media
            When set to ``true``, ``"t"``, or ``1``, links in a Tweet are not
            expanded to photo, video, or link previews.
        hide_thread
            When set to ``true``, ``"t"``, or ``1``, a collapsed version of the
            previous Tweet in a conversation thread will not be displayed when
            the requested Tweet is in reply to another Tweet.
        omit_script
            When set to ``true``, ``"t"``, or ``1``, the ``<script>``
            responsible for loading ``widgets.js`` will not be returned. Your
            webpages should include their own reference to ``widgets.js`` for
            use across all Twitter widgets including Embedded Tweets.
        align
            Specifies whether the embedded Tweet should be floated left, right,
            or center in the page relative to the parent element.
        related
            A comma-separated list of Twitter usernames related to your
            content. This value will be forwarded to Tweet action intents if a
            viewer chooses to reply, like, or retweet the embedded Tweet.
        lang
            Request returned HTML and a rendered Tweet in the specified Twitter
            language supported by embedded Tweets.
        theme
            When set to ``dark``, the Tweet is displayed with light text over a
            dark background.
        link_color
            Adjust the color of Tweet text links with a hexadecimal color
            value.
        widget_type
            Set to ``video`` to return a Twitter Video embed for the given
            Tweet.
        dnt
            When set to ``true``, the Tweet and its embedded page on your site
            are not used for purposes that include personalized suggestions and
            personalized ads.

        Returns
        -------
        :class:`dict`
            JSON

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/get-statuses-oembed
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
    def get_retweeter_ids(self, id, **kwargs):
        """get_retweeter_ids(id, *, count, cursor, stringify_ids)

        Returns up to 100 user IDs belonging to users who have retweeted the
        Tweet specified by the ``id`` parameter.

        .. versionchanged:: 4.0
            Renamed from ``API.retweeters``

        Parameters
        ----------
        id
            |sid|
        count
            |count|
        cursor
            |cursor|
        stringify_ids
            |stringify_ids|

        Returns
        -------
        :py:class:`List`\[:class:`int`]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/get-statuses-retweeters-ids
        """
        return self.request(
            'GET', 'statuses/retweeters/ids', endpoint_parameters=(
                'id', 'count', 'cursor', 'stringify_ids'
            ), id=id, **kwargs
        )

    @payload('status', list=True)
    def get_retweets(self, id, **kwargs):
        """get_retweets(id, *, count, trim_user)

        Returns up to 100 of the first Retweets of the given Tweet.

        .. versionchanged:: 4.0
            Renamed from ``API.retweets``

        Parameters
        ----------
        id
            |sid|
        count
            |count|
        trim_user
            |trim_user|

        Returns
        -------
        :py:class:`List`\[:class:`~tweepy.models.Status`]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/get-statuses-retweets-id
        """
        return self.request(
            'GET', f'statuses/retweets/{id}', endpoint_parameters=(
                'count', 'trim_user'
            ), **kwargs
        )

    @pagination(mode='id')
    @payload('status', list=True)
    def get_retweets_of_me(self, **kwargs):
        """get_retweets_of_me(*, count, since_id, max_id, trim_user, \
                              include_entities, include_user_entities)

        Returns the 20 most recent Tweets of the authenticated user that have
        been retweeted by others.

        .. versionchanged:: 4.0
            Renamed from ``API.retweets_of_me``

        Parameters
        ----------
        count
            |count|
        since_id
            |since_id|
        max_id
            |max_id|
        trim_user
            |trim_user|
        include_entities
            |include_entities|
        include_user_entities
            |include_user_entities|

        Returns
        -------
        :py:class:`List`\[:class:`~tweepy.models.Status`]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/get-statuses-retweets_of_me
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

        Parameters
        ----------
        id:
            |sid|
        trim_user
            |trim_user|
        include_my_retweet:
            A boolean indicating if any Tweets returned that have been
            retweeted by the authenticating user should include an additional
            current_user_retweet node, containing the ID of the source status
            for the retweet.
        include_entities
            |include_entities|
        include_ext_alt_text
            |include_ext_alt_text|
        include_card_uri
            |include_card_uri|

        Returns
        -------
        :class:`~tweepy.models.Status`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/get-statuses-show-id
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

        Parameters
        ----------
        id
            |sid|
        include_entities
            |include_entities|

        Returns
        -------
        :class:`~tweepy.models.Status`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/post-favorites-create
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

        Parameters
        ----------
        id
            |sid|
        include_entities
            |include_entities|

        Returns
        -------
        :class:`~tweepy.models.Status`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/post-favorites-destroy
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

        Parameters
        ----------
        id
            |sid|
        trim_user
            |trim_user|

        Returns
        -------
        :class:`~tweepy.models.Status`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/post-statuses-destroy-id
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

        Parameters
        ----------
        id
            |sid|
        trim_user
            |trim_user|

        Returns
        -------
        :class:`~tweepy.models.Status`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/post-statuses-retweet-id
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

        Parameters
        ----------
        id
            |sid|
        trim_user
            |trim_user|

        Returns
        -------
        :class:`~tweepy.models.Status`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/post-statuses-unretweet-id
        """
        return self.request(
            'POST', f'statuses/unretweet/{id}', endpoint_parameters=(
                'trim_user',
            ), **kwargs
        )

    @payload('status')
    def update_status(self, status, **kwargs):
        """update_status( \
            status, *, in_reply_to_status_id, auto_populate_reply_metadata, \
            exclude_reply_user_ids, attachment_url, media_ids, \
            possibly_sensitive, lat, long, place_id, display_coordinates, \
            trim_user, card_uri \
        )

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

        Parameters
        ----------
        status
            The text of your status update.
        in_reply_to_status_id
            The ID of an existing status that the update is in reply to. Note:
            This parameter will be ignored unless the author of the Tweet this
            parameter references is mentioned within the status text.
            Therefore, you must include @username, where username is the author
            of the referenced Tweet, within the update.
        auto_populate_reply_metadata
            If set to true and used with in_reply_to_status_id, leading
            @mentions will be looked up from the original Tweet, and added to
            the new Tweet from there. This wil append @mentions into the
            metadata of an extended Tweet as a reply chain grows, until the
            limit on @mentions is reached. In cases where the original Tweet
            has been deleted, the reply will fail.
        exclude_reply_user_ids
            When used with auto_populate_reply_metadata, a comma-separated list
            of user ids which will be removed from the server-generated
            @mentions prefix on an extended Tweet. Note that the leading
            @mention cannot be removed as it would break the
            in-reply-to-status-id semantics. Attempting to remove it will be
            silently ignored.
        attachment_url
            In order for a URL to not be counted in the status body of an
            extended Tweet, provide a URL as a Tweet attachment. This URL must
            be a Tweet permalink, or Direct Message deep link. Arbitrary,
            non-Twitter URLs must remain in the status text. URLs passed to the
            attachment_url parameter not matching either a Tweet permalink or
            Direct Message deep link will fail at Tweet creation and cause an
            exception.
        media_ids
            A list of media_ids to associate with the Tweet. You may include up
            to 4 photos or 1 animated GIF or 1 video in a Tweet.
        possibly_sensitive
            If you upload Tweet media that might be considered sensitive
            content such as nudity, or medical procedures, you must set this
            value to true.
        lat
            The latitude of the location this Tweet refers to. This parameter
            will be ignored unless it is inside the range -90.0 to +90.0 (North
            is positive) inclusive. It will also be ignored if there is no
            corresponding long parameter.
        long
            The longitude of the location this Tweet refers to. The valid
            ranges for longitude are -180.0 to +180.0 (East is positive)
            inclusive. This parameter will be ignored if outside that range, if
            it is not a number, if geo_enabled is disabled, or if there no
            corresponding lat parameter.
        place_id
            A place in the world.
        display_coordinates
            Whether or not to put a pin on the exact coordinates a Tweet has
            been sent from.
        trim_user
            |trim_user|
        card_uri
            Associate an ads card with the Tweet using the card_uri value from
            any ads card response.

        Returns
        -------
        :class:`~tweepy.models.Status`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/post-statuses-update
        """
        if 'media_ids' in kwargs:
            kwargs['media_ids'] = list_to_csv(kwargs['media_ids'])

        return self.request(
            'POST', 'statuses/update', endpoint_parameters=(
                'status', 'in_reply_to_status_id',
                'auto_populate_reply_metadata', 'exclude_reply_user_ids',
                'attachment_url', 'media_ids', 'possibly_sensitive', 'lat',
                'long', 'place_id', 'display_coordinates', 'trim_user',
                'card_uri'
            ), status=status, **kwargs
        )

    @payload('status')
    def update_status_with_media(self, status, filename, *, file=None,
                                 **kwargs):
        """update_status_with_media( \
            status, filename, *, file, possibly_sensitive, \
            in_reply_to_status_id, lat, long, place_id, display_coordinates \
        )

        Update the authenticated user's status. Statuses that are duplicates or
        too long will be silently ignored.

        .. deprecated:: 3.7.0
            Use :func:`API.media_upload` instead.

        .. versionchanged:: 4.0
            Renamed from ``API.update_with_media``

        Parameters
        ----------
        status
            The text of your status update.
        filename
            |filename|
        file
            |file|
        possibly_sensitive
            Set to true for content which may not be suitable for every
            audience.
        in_reply_to_status_id
            The ID of an existing status that the update is in reply to.
        lat
            The location's latitude that this tweet refers to.
        long
            The location's longitude that this tweet refers to.
        place_id
            Twitter ID of location which is listed in the Tweet if geolocation
            is enabled for the user.
        display_coordinates
            Whether or not to put a pin on the exact coordinates a Tweet has
            been sent from.

        Returns
        -------
        :class:`~tweepy.models.Status`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/post-statuses-update_with_media
        """
        with contextlib.ExitStack() as stack:
            if file is not None:
                files = {'media[]': (filename, file)}
            else:
                files = {'media[]': stack.enter_context(open(filename, 'rb'))}
            return self.request(
                'POST', 'statuses/update_with_media', endpoint_parameters=(
                    'status', 'possibly_sensitive', 'in_reply_to_status_id',
                    'lat', 'long', 'place_id', 'display_coordinates'
                ), status=status, files=files, **kwargs
            )

    # Search Tweets

    @pagination(mode='id')
    @payload('search_results')
    def search_tweets(self, q, **kwargs):
        """search_tweets(q, *, geocode, lang, locale, result_type, count, \
                         until, since_id, max_id, include_entities)

        Returns a collection of relevant Tweets matching a specified query.

        Please note that Twitter's search service and, by extension, the Search
        API is not meant to be an exhaustive source of Tweets. Not all Tweets
        will be indexed or made available via the search interface.

        .. note::

            Twitter's standard search API only "searches against a sampling of
            recent Tweets published in the past 7 days."

            If you're specifying an ID range beyond the past 7 days or there
            are no results from the past 7 days, then no results will be
            returned.

            See `Twitter's documentation on the standard search API`_ for more
            information.

        .. note::

            In API v1.1, the response format of the Search API has been
            improved to return Tweet objects more similar to the objects you’ll
            find across the REST API and platform. However, perspectival
            attributes (fields that pertain to the perspective of the
            authenticating user) are not currently supported on this endpoint.
            [#]_\ [#]_

        .. versionchanged:: 4.0
            Renamed from ``API.search``

        Parameters
        ----------
        q
            The search query string of 500 characters maximum, including
            operators. Queries may additionally be limited by complexity.
        geocode
            Returns tweets by users located within a given radius of the given
            latitude/longitude.  The location is preferentially taking from the
            Geotagging API, but will fall back to their Twitter profile. The
            parameter value is specified by "latitude,longitude,radius", where
            radius units must be specified as either "mi" (miles) or "km"
            (kilometers). Note that you cannot use the near operator via the
            API to geocode arbitrary locations; however you can use this
            geocode parameter to search near geocodes directly. A maximum of
            1,000 distinct "sub-regions" will be considered when using the
            radius modifier.
        lang
            Restricts tweets to the given language, given by an ISO 639-1 code.
            Language detection is best-effort.
        locale
            Specify the language of the query you are sending (only ja is
            currently effective). This is intended for language-specific
            consumers and the default should work in the majority of cases.
        result_type
            Specifies what type of search results you would prefer to receive.
            The current default is "mixed." Valid values include:

            * mixed : include both popular and real time results in the \
                      response
            * recent : return only the most recent results in the response
            * popular : return only the most popular results in the response
        count
            |count|
        until
            Returns tweets created before the given date. Date should be
            formatted as YYYY-MM-DD. Keep in mind that the search index has a
            7-day limit. In other words, no tweets will be found for a date
            older than one week.
        since_id
            |since_id| There are limits to the number of Tweets which can be
            accessed through the API. If the limit of Tweets has occurred since
            the since_id, the since_id will be forced to the oldest ID
            available.
        max_id
            |max_id|
        include_entities
            |include_entities|

        Returns
        -------
        :class:`SearchResults`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/tweets/search/api-reference/get-search-tweets

        .. _Twitter's documentation on the standard search API: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/search/overview
        """
        return self.request(
            'GET', 'search/tweets', endpoint_parameters=(
                'q', 'geocode', 'lang', 'locale', 'result_type', 'count',
                'until', 'since_id', 'max_id', 'include_entities'
            ), q=q, **kwargs
        )

    # Create and manage lists

    @payload('list', list=True)
    def get_lists(self, **kwargs):
        """get_lists(*, user_id, screen_name, reverse)

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

        .. versionchanged:: 4.0
            Renamed from ``API.lists_all``

        Parameters
        ----------
        user_id
            |user_id|
        screen_name
            |screen_name|
        reverse
            A boolean indicating if you would like owned lists to be returned
            first. See description above for information on how this parameter
            works.

        Returns
        -------
        :py:class:`List`\[:class:`~tweepy.models.List`]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/get-lists-list
        """
        return self.request(
            'GET', 'lists/list', endpoint_parameters=(
                'user_id', 'screen_name', 'reverse'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('user', list=True)
    def get_list_members(self, **kwargs):
        """get_list_members(*, list_id, slug, owner_screen_name, owner_id, \
                            count, cursor, include_entities, skip_status)

        Returns the members of the specified list.

        .. versionchanged:: 4.0
            Renamed from ``API.list_members``

        Parameters
        ----------
        list_id
            |list_id|
        slug
            |slug|
        owner_screen_name
            |owner_screen_name|
        owner_id
            |owner_id|
        count
            |count|
        cursor
            |cursor|
        include_entities
            |include_entities|
        skip_status
            |skip_status|

        Returns
        -------
        :py:class:`List`\[:class:`~tweepy.models.User`]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/get-lists-members
        """
        return self.request(
            'GET', 'lists/members', endpoint_parameters=(
                'list_id', 'slug', 'owner_screen_name', 'owner_id', 'count',
                'cursor', 'include_entities', 'skip_status'
            ), **kwargs
        )

    @payload('user')
    def get_list_member(self, **kwargs):
        """get_list_member( \
            *, list_id, slug, user_id, screen_name, owner_screen_name, \
            owner_id, include_entities, skip_status \
        )

        Check if the specified user is a member of the specified list.

        .. versionchanged:: 4.0
            Renamed from ``API.show_list_member``

        Parameters
        ----------
        list_id
            |list_id|
        slug
            |slug|
        user_id
            |user_id|
        screen_name
            |screen_name|
        owner_screen_name
            |owner_screen_name|
        owner_id
            |owner_id|
        include_entities
            |include_entities|
        skip_status
            |skip_status|

        Raises
        ------
        :class:`~tweepy.errors.NotFound`
            The user is not a member of the list.

        Returns
        -------
        :class:`~tweepy.models.User`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/get-lists-members-show
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
    def get_list_memberships(self, **kwargs):
        """get_list_memberships(*, user_id, screen_name, count, cursor, \
                                filter_to_owned_lists)

        Returns the lists the specified user has been added to. If ``user_id``
        or ``screen_name`` are not provided, the memberships for the
        authenticating user are returned.

        .. versionchanged:: 4.0
            Renamed from ``API.lists_memberships``

        Parameters
        ----------
        user_id
            |user_id|
        screen_name
            |screen_name|
        count
            |count|
        cursor
            |cursor|
        filter_to_owned_lists
            A boolean indicating whether to return just lists the
            authenticating user owns, and the user represented by ``user_id``
            or ``screen_name`` is a member of.

        Returns
        -------
        :py:class:`List`\[:class:`~tweepy.models.List`]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/get-lists-memberships
        """
        return self.request(
            'GET', 'lists/memberships', endpoint_parameters=(
                'user_id', 'screen_name', 'count', 'cursor',
                'filter_to_owned_lists'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('list', list=True)
    def get_list_ownerships(self, **kwargs):
        """get_list_ownerships(*, user_id, screen_name, count, cursor)

        Returns the lists owned by the specified user. Private lists will only
        be shown if the authenticated user is also the owner of the lists. If
        ``user_id`` and ``screen_name`` are not provided, the ownerships for
        the authenticating user are returned.

        Parameters
        ----------
        user_id
            |user_id|
        screen_name
            |screen_name|
        count
            |count|
        cursor
            |cursor|

        Returns
        -------
        :py:class:`List`\[:class:`~tweepy.models.List`]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/get-lists-ownerships
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

        Parameters
        ----------
        list_id
            |list_id|
        slug
            |slug|
        owner_screen_name
            |owner_screen_name|
        owner_id
            |owner_id|

        Returns
        -------
        :class:`~tweepy.models.List`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/get-lists-show
        """
        return self.request(
            'GET', 'lists/show', endpoint_parameters=(
                'list_id', 'slug', 'owner_screen_name', 'owner_id'
            ), **kwargs
        )

    @pagination(mode='id')
    @payload('status', list=True)
    def list_timeline(self, **kwargs):
        """list_timeline( \
            *, list_id, slug, owner_screen_name, owner_id, since_id, max_id, \
            count, include_entities, include_rts \
        )

        Returns a timeline of Tweets authored by members of the specified list.
        Retweets are included by default. Use the ``include_rts=false``
        parameter to omit retweets.

        Parameters
        ----------
        list_id
            |list_id|
        slug
            |slug|
        owner_screen_name
            |owner_screen_name|
        owner_id
            |owner_id|
        since_id
            |since_id|
        max_id
            |max_id|
        count
            |count|
        include_entities
            |include_entities|
        include_rts
            A boolean indicating whether the list timeline will contain native
            retweets (if they exist) in addition to the standard stream of
            Tweets. The output format of retweeted Tweets is identical to the
            representation you see in home_timeline.

        Returns
        -------
        :py:class:`List`\[:class:`~tweepy.models.Status`]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/get-lists-statuses
                """
        return self.request(
            'GET', 'lists/statuses', endpoint_parameters=(
                'list_id', 'slug', 'owner_screen_name', 'owner_id', 'since_id',
                'max_id', 'count', 'include_entities', 'include_rts'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('user', list=True)
    def get_list_subscribers(self, **kwargs):
        """get_list_subscribers( \
            *, list_id, slug, owner_screen_name, owner_id, count, cursor, \
            include_entities, skip_status \
        )

        Returns the subscribers of the specified list. Private list subscribers
        will only be shown if the authenticated user owns the specified list.

        .. versionchanged:: 4.0
            Renamed from ``API.list_subscribers``

        Parameters
        ----------
        list_id
            |list_id|
        slug
            |slug|
        owner_screen_name
            |owner_screen_name|
        owner_id
            |owner_id|
        count
            |count|
        cursor
            |cursor|
        include_entities
            |include_entities|
        skip_status
            |skip_status|

        Returns
        -------
        :py:class:`List`\[:class:`~tweepy.models.User`]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/get-lists-subscribers
        """
        return self.request(
            'GET', 'lists/subscribers', endpoint_parameters=(
                'list_id', 'slug', 'owner_screen_name', 'owner_id', 'count',
                'cursor', 'include_entities', 'skip_status'
            ), **kwargs
        )

    @payload('user')
    def get_list_subscriber(self, **kwargs):
        """get_list_subscriber( \
            *, owner_screen_name, owner_id, list_id, slug, user_id, \
            screen_name, include_entities, skip_status \
        )

        Check if the specified user is a subscriber of the specified list.

        .. versionchanged:: 4.0
            Renamed from ``API.show_list_subscriber``

        Parameters
        ----------
        owner_screen_name
            |owner_screen_name|
        owner_id
            |owner_id|
        list_id
            |list_id|
        slug
            |slug|
        user_id
            |user_id|
        screen_name
            |screen_name|
        include_entities
            |include_entities|
        skip_status
            |skip_status|

        Raises
        ------
        :class:`~tweepy.errors.NotFound`
            The user is not a subscriber of the list.

        Returns
        -------
        :class:`~tweepy.models.User`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/get-lists-subscribers-show
        """
        return self.request(
            'GET', 'lists/subscribers/show', endpoint_parameters=(
                'owner_screen_name', 'owner_id', 'list_id', 'slug', 'user_id',
                'screen_name', 'include_entities', 'skip_status'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('list', list=True)
    def get_list_subscriptions(self, **kwargs):
        """get_list_subscriptions(*, user_id, screen_name, count, cursor)

        Obtain a collection of the lists the specified user is subscribed to,
        20 lists per page by default. Does not include the user's own lists.

        .. versionchanged:: 4.0
            Renamed from ``API.lists_subscriptions``

        Parameters
        ----------
        user_id
            |user_id|
        screen_name
            |screen_name|
        count
            |count|
        cursor
            |cursor|

        Returns
        -------
        :py:class:`List`\[:class:`~tweepy.models.List`]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/get-lists-subscriptions
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

        Parameters
        ----------
        name
            The name of the new list.
        mode
            |list_mode|
        description
            The description of the list you are creating.

        Returns
        -------
        :class:`~tweepy.models.List`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/post-lists-create
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

        Parameters
        ----------
        owner_screen_name
            |owner_screen_name|
        owner_id
            |owner_id|
        list_id
            |list_id|
        slug
            |slug|

        Returns
        -------
        :class:`~tweepy.models.List`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/post-lists-destroy
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

        Parameters
        ----------
        list_id
            |list_id|
        slug
            |slug|
        user_id
            |user_id|
        screen_name
            |screen_name|
        owner_screen_name
            |owner_screen_name|
        owner_id
            |owner_id|

        Returns
        -------
        :class:`~tweepy.models.List`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/post-lists-members-create
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

        Parameters
        ----------
        list_id
            |list_id|
        slug
            |slug|
        user_id
            A comma separated list of user IDs, up to 100 are allowed in a
            single request
        screen_name
            A comma separated list of screen names, up to 100 are allowed in a
            single request
        owner_screen_name
            |owner_screen_name|
        owner_id
            |owner_id|

        Returns
        -------
        :class:`~tweepy.models.List`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/post-lists-members-create_all
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

        Parameters
        ----------
        list_id
            |list_id|
        slug
            |slug|
        user_id
            |user_id|
        screen_name
            |screen_name|
        owner_screen_name
            |owner_screen_name|
        owner_id
            |owner_id|

        Returns
        -------
        :class:`~tweepy.models.List`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/post-lists-members-destroy
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

        Parameters
        ----------
        list_id
            |list_id|
        slug
            |slug|
        user_id
            A comma separated list of user IDs, up to 100 are allowed in a
            single request
        screen_name
            A comma separated list of screen names, up to 100 are allowed in a
            single request
        owner_screen_name
            |owner_screen_name|
        owner_id
            |owner_id|

        Returns
        -------
        :class:`~tweepy.models.List`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/post-lists-members-destroy_all
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

        Parameters
        ----------
        owner_screen_name
            |owner_screen_name|
        owner_id
            |owner_id|
        list_id
            |list_id|
        slug
            |slug|

        Returns
        -------
        :class:`~tweepy.models.List`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/post-lists-subscribers-create
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

        Parameters
        ----------
        list_id
            |list_id|
        slug
            |slug|
        owner_screen_name
            |owner_screen_name|
        owner_id
            |owner_id|

        Returns
        -------
        :class:`~tweepy.models.List`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/post-lists-subscribers-destroy
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

        Parameters
        ----------
        list_id
            |list_id|
        slug
            |slug|
        name
            The name for the list.
        mode
            |list_mode|
        description
            The description to give the list.
        owner_screen_name
            |owner_screen_name|
        owner_id
            |owner_id|

        Returns
        -------
        :class:`~tweepy.models.List`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/create-manage-lists/api-reference/post-lists-update
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
    def get_follower_ids(self, **kwargs):
        """get_follower_ids(*, user_id, screen_name, cursor, stringify_ids, \
                            count)

        Returns an array containing the IDs of users following the specified
        user.

        .. versionchanged:: 4.0
            Renamed from ``API.followers_ids``

        Parameters
        ----------
        user_id
            |user_id|
        screen_name
            |screen_name|
        cursor
            |cursor|
        stringify_ids
            |stringify_ids|
        count
            |count|

        Returns
        -------
        :py:class:`List`\[:class:`int`]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-followers-ids
        """
        return self.request(
            'GET', 'followers/ids', endpoint_parameters=(
                'user_id', 'screen_name', 'cursor', 'stringify_ids', 'count'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('user', list=True)
    def get_followers(self, **kwargs):
        """get_followers(*, user_id, screen_name, cursor, count, skip_status, \
                         include_user_entities)

        Returns a user's followers ordered in which they were added. If no user
        is specified by id/screen name, it defaults to the authenticated user.

        .. versionchanged:: 4.0
            Renamed from ``API.followers``

        Parameters
        ----------
        user_id
            |user_id|
        screen_name
            |screen_name|
        cursor
            |cursor|
        count
            |count|
        skip_status
            |skip_status|
        include_user_entities
            |include_user_entities|

        Returns
        -------
        :py:class:`List`\[:class:`~tweepy.models.User`]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-followers-list
        """
        return self.request(
            'GET', 'followers/list', endpoint_parameters=(
                'user_id', 'screen_name', 'cursor', 'count', 'skip_status',
                'include_user_entities'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('ids')
    def get_friend_ids(self, **kwargs):
        """get_friend_ids(*, user_id, screen_name, cursor, stringify_ids, \
                          count)

        Returns an array containing the IDs of users being followed by the
        specified user.

        .. versionchanged:: 4.0
            Renamed from ``API.friends_ids``

        Parameters
        ----------
        user_id
            |user_id|
        screen_name
            |screen_name|
        cursor
            |cursor|
        stringify_ids
            |stringify_ids|
        count
            |count|

        Returns
        -------
        :py:class:`List`\[:class:`int`]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-friends-ids
        """
        return self.request(
            'GET', 'friends/ids', endpoint_parameters=(
                'user_id', 'screen_name', 'cursor', 'stringify_ids', 'count'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('user', list=True)
    def get_friends(self, **kwargs):
        """get_friends(*, user_id, screen_name, cursor, count, skip_status, \
                       include_user_entities)

        Returns a user's friends ordered in which they were added 100 at a
        time. If no user is specified it defaults to the authenticated user.

        .. versionchanged:: 4.0
            Renamed from ``API.friends``

        Parameters
        ----------
        user_id
            |user_id|
        screen_name
            |screen_name|
        cursor
            |cursor|
        count
            |count|
        skip_status
            |skip_status|
        include_user_entities
            |include_user_entities|

        Returns
        -------
        :py:class:`List`\[:class:`~tweepy.models.User`]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-friends-list
        """
        return self.request(
            'GET', 'friends/list', endpoint_parameters=(
                'user_id', 'screen_name', 'cursor', 'count', 'skip_status',
                'include_user_entities'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('ids')
    def incoming_friendships(self, **kwargs):
        """incoming_friendships(*, cursor, stringify_ids)

        Returns a collection of numeric IDs for every user who has a pending
        request to follow the authenticating user.

        .. versionchanged:: 4.0
            Renamed from ``API.friendships_incoming``

        Parameters
        ----------
        cursor
            |cursor|
        stringify_ids
            |stringify_ids|

        Returns
        -------
        :py:class:`List`\[:class:`int`]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-friendships-incoming
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

        Parameters
        ----------
        screen_name
            A list of screen names, up to 100 are allowed in a single request.
        user_id
            A list of user IDs, up to 100 are allowed in a single request.

        Returns
        -------
        :py:class:`List`\[:class:`~tweepy.models.Relationship`]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-friendships-lookup
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

        Parameters
        ----------
        stringify_ids
            |stringify_ids|

        Returns
        -------
        :py:class:`List`\[:class:`int`]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-friendships-no_retweets-ids
        """
        return self.request(
            'GET', 'friendships/no_retweets/ids', endpoint_parameters=(
                'stringify_ids',
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('ids')
    def outgoing_friendships(self, **kwargs):
        """outgoing_friendships(*, cursor, stringify_ids)

        Returns a collection of numeric IDs for every protected user for whom
        the authenticating user has a pending follow request.

        .. versionchanged:: 4.0
            Renamed from ``API.friendships_outgoing``

        Parameters
        ----------
        cursor
            |cursor|
        stringify_ids
            |stringify_ids|

        Returns
        -------
        :py:class:`List`\[:class:`int`]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-friendships-outgoing
        """
        return self.request(
            'GET', 'friendships/outgoing', endpoint_parameters=(
                'cursor', 'stringify_ids'
            ), **kwargs
        )

    @payload('friendship')
    def get_friendship(self, **kwargs):
        """get_friendship(*, source_id, source_screen_name, target_id, \
                          target_screen_name)

        Returns detailed information about the relationship between two users.

        .. versionchanged:: 4.0
            Renamed from ``API.show_friendship``

        Parameters
        ----------
        source_id
            The user_id of the subject user.
        source_screen_name
            The screen_name of the subject user.
        target_id
            The user_id of the target user.
        target_screen_name
            The screen_name of the target user.

        Returns
        -------
        :class:`~tweepy.models.Friendship`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-friendships-show
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

        Parameters
        ----------
        screen_name
            A list of screen names, up to 100 are allowed in a single request.
        user_id
            A list of user IDs, up to 100 are allowed in a single request.
        include_entities
            |include_entities|
        tweet_mode
            Valid request values are compat and extended, which give
            compatibility mode and extended mode, respectively for Tweets that
            contain over 140 characters.

        Returns
        -------
        :py:class:`List`\[:class:`~tweepy.models.User`]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-users-lookup
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

        Parameters
        ----------
        q
            The query to run against people search.
        page
            |page|
        count
            |count|
        include_entities
            |include_entities|

        Returns
        -------
        :py:class:`List`\[:class:`~tweepy.models.User`]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-users-search
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

        Parameters
        ----------
        user_id
            |user_id|
        screen_name
            |screen_name|
        include_entities
            |include_entities|

        Returns
        -------
        :class:`~tweepy.models.User`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-users-show
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

        Parameters
        ----------
        screen_name
            |screen_name|
        user_id
            |user_id|
        follow
            Enable notifications for the target user in addition to becoming
            friends.

        Returns
        -------
        :class:`~tweepy.models.User`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/post-friendships-create
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

        Parameters
        ----------
        screen_name
            |screen_name|
        user_id
            |user_id|

        Returns
        -------
        :class:`~tweepy.models.User`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/post-friendships-destroy
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

        Parameters
        ----------
        screen_name
            |screen_name|
        user_id
            |user_id|
        device
            Turn on/off device notifications from the target user.
        retweets
            Turn on/off Retweets from the target user.

        Returns
        -------
        :class:`~tweepy.models.Friendship`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/post-friendships-update
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

        Returns
        -------
        :class:`dict`
            JSON

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/get-account-settings
        """
        return self.request(
            'GET', 'account/settings', use_cache=False, **kwargs
        )

    @payload('user')
    def verify_credentials(self, **kwargs):
        """verify_credentials(*, include_entities, skip_status, include_email)

        Verify the supplied user credentials are valid.

        Parameters
        ----------
        include_entities
            |include_entities|
        skip_status
            |skip_status|
        include_email
            When set to true email will be returned in the user objects as a
            string.

        Raises
        ------
        :class:`~tweepy.errors.Unauthorized`
            Authentication unsuccessful

        Returns
        -------
        :class:`~tweepy.models.User`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/get-account-verify_credentials
        """
        if 'include_email' in kwargs:
            kwargs['include_email'] = str(kwargs['include_email']).lower()
        return self.request(
            'GET', 'account/verify_credentials', endpoint_parameters=(
                'include_entities', 'skip_status', 'include_email'
            ), **kwargs
        )

    @payload('saved_search', list=True)
    def get_saved_searches(self, **kwargs):
        """get_saved_searches()

        Returns the authenticated user's saved search queries.

        .. versionchanged:: 4.0
            Renamed from ``API.saved_searches``

        Returns
        -------
        :py:class:`List`\[:class:`~tweepy.models.SavedSearch`]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/get-saved_searches-list
        """
        return self.request('GET', 'saved_searches/list', **kwargs)

    @payload('saved_search')
    def get_saved_search(self, id, **kwargs):
        """get_saved_search(id)

        Retrieve the data for a saved search owned by the authenticating user
        specified by the given ID.

        Parameters
        ----------
        id
            The ID of the saved search to be retrieved.

        Returns
        -------
        :class:`~tweepy.models.SavedSearch`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/get-saved_searches-show-id
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

        Parameters
        ----------
        user_id
            |user_id|
        screen_name
            |screen_name|

        Returns
        -------
        :class:`dict`
            JSON

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/get-users-profile_banner
        """
        return self.request(
            'GET', 'users/profile_banner', endpoint_parameters=(
                'user_id', 'screen_name'
            ), **kwargs
        )

    def remove_profile_banner(self, **kwargs):
        """remove_profile_banner()

        Removes the uploaded profile banner for the authenticating user.

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/post-account-remove_profile_banner
        """
        return self.request('POST', 'account/remove_profile_banner', **kwargs)

    @payload('json')
    def set_settings(self, **kwargs):
        """set_settings(*, sleep_time_enabled, start_sleep_time, \
                        end_sleep_time, time_zone, trend_location_woeid, lang)

        Updates the authenticating user's settings.

        Parameters
        ----------
        sleep_time_enabled
            When set to ``true``, ``t`` or ``1`` , will enable sleep time for
            the user. Sleep time is the time when push or SMS notifications
            should not be sent to the user.
        start_sleep_time
            The hour that sleep time should begin if it is enabled. The value
            for this parameter should be provided in `ISO 8601`_ format (i.e.
            00-23). The time is considered to be in the same timezone as the
            user's ``time_zone`` setting.
        end_sleep_time
            The hour that sleep time should end if it is enabled. The value for
            this parameter should be provided in `ISO 8601`_ format (i.e.
            00-23). The time is considered to be in the same timezone as the
            user's ``time_zone`` setting.
        time_zone
            The timezone dates and times should be displayed in for the user.
            The timezone must be one of the `Rails TimeZone`_ names.
        trend_location_woeid
            The Yahoo! Where On Earth ID to use as the user's default trend
            location. Global information is available by using 1 as the WOEID.
        lang
            The language which Twitter should render in for this user. The
            language must be specified by the appropriate two letter ISO 639-1
            representation.

        Returns
        -------
        :class:`dict`
            JSON

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/post-account-settings

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

        Parameters
        ----------
        name
            Full name associated with the profile.
        url
            URL associated with the profile. Will be prepended with ``http://``
            if not present
        location
            The city or country describing where the user of the account is
            located. The contents are not normalized or geocoded in any way.
        description
            A description of the user owning the account.
        profile_link_color
            Sets a hex value that controls the color scheme of links used on
            the authenticating user's profile page on twitter.com. This must be
            a valid hexadecimal value, and may be either three or six
            characters (ex: F00 or FF0000).
        include_entities
            |include_entities|
        skip_status
            |skip_status|

        Returns
        -------
        :class:`~tweepy.models.User`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/post-account-update_profile
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

        Parameters
        ----------
        filename
            |filename|
        file:
            |file|
        width
            The width of the preferred section of the image being uploaded in
            pixels. Use with ``height``, ``offset_left``, and ``offset_top`` to
            select the desired region of the image to use.
        height
            The height of the preferred section of the image being uploaded in
            pixels. Use with ``width``, ``offset_left``, and ``offset_top`` to
            select the desired region of the image to use.
        offset_left
            The number of pixels by which to offset the uploaded image from the
            left. Use with ``height``, ``width``, and ``offset_top`` to select
            the desired region of the image to use.
        offset_top
            The number of pixels by which to offset the uploaded image from the
            top. Use with ``height``, ``width``, and ``offset_left`` to select
            the desired region of the image to use.

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/post-account-update_profile_banner
        """
        with contextlib.ExitStack() as stack:
            if file is not None:
                files = {'banner': (filename, file)}
            else:
                files = {'banner': stack.enter_context(open(filename, 'rb'))}
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

        Parameters
        ----------
        filename
            |filename|
        file
            |file|
        include_entities
            |include_entities|
        skip_status
            |skip_status|

        Returns
        -------
        :class:`~tweepy.models.User`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/post-account-update_profile_image
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

        Parameters
        ----------
        query
            The query of the search the user would like to save.

        Returns
        -------
        :class:`~tweepy.models.SavedSearch`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/post-saved_searches-create
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

        Parameters
        ----------
        id
            The ID of the saved search to be deleted.

        Returns
        -------
        :class:`~tweepy.models.SavedSearch`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/post-saved_searches-destroy-id
        """
        return self.request('POST', f'saved_searches/destroy/{id}', **kwargs)

    # Mute, block, and report users

    @pagination(mode='cursor')
    @payload('ids')
    def get_blocked_ids(self, **kwargs):
        """get_blocked_ids(*, stringify_ids, cursor)

        Returns an array of numeric user IDs the authenticating user is
        blocking.

        .. versionchanged:: 4.0
            Renamed from ``API.blocks_ids``

        Parameters
        ----------
        stringify_ids
            |stringify_ids|
        cursor
            |cursor|

        Returns
        -------
        :py:class:`List`\[:class:`int`]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/mute-block-report-users/api-reference/get-blocks-ids
        """
        return self.request(
            'GET', 'blocks/ids', endpoint_parameters=(
                'stringify_ids', 'cursor',
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('user', list=True)
    def get_blocks(self, **kwargs):
        """get_blocks(*, include_entities, skip_status, cursor)

        Returns an array of user objects that the authenticating user is
        blocking.

        .. versionchanged:: 4.0
            Renamed from ``API.blocks``

        Parameters
        ----------
        include_entities
            |include_entities|
        skip_status
            |skip_status|
        cursor
            |cursor|

        Returns
        -------
        :py:class:`List`\[:class:`~tweepy.models.User`]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/mute-block-report-users/api-reference/get-blocks-list
        """
        return self.request(
            'GET', 'blocks/list', endpoint_parameters=(
                'include_entities', 'skip_status', 'cursor'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('ids')
    def get_muted_ids(self, **kwargs):
        """get_muted_ids(*, stringify_ids, cursor)

        Returns an array of numeric user IDs the authenticating user has muted.

        .. versionchanged:: 4.0
            Renamed from ``API.mutes_ids``

        Parameters
        ----------
        stringify_ids
            |stringify_ids|
        cursor
            |cursor|

        Returns
        -------
        :py:class:`List`\[:class:`int`]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/mute-block-report-users/api-reference/get-mutes-users-ids
        """
        return self.request(
            'GET', 'mutes/users/ids', endpoint_parameters=(
                'stringify_ids', 'cursor'
            ), **kwargs
        )

    @pagination(mode='cursor')
    @payload('user', list=True)
    def get_mutes(self, **kwargs):
        """get_mutes(*, cursor, include_entities, skip_status)

        Returns an array of user objects the authenticating user has muted.

        .. versionchanged:: 4.0
            Renamed from ``API.mutes``

        Parameters
        ----------
        cursor
            |cursor|
        include_entities
            |include_entities|
        skip_status
            |skip_status|

        Returns
        -------
        :py:class:`List`\[:class:`~tweepy.models.User`]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/mute-block-report-users/api-reference/get-mutes-users-list
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

        Parameters
        ----------
        screen_name
            |screen_name|
        user_id
            |user_id|
        include_entities
            |include_entities|
        skip_status
            |skip_status|

        Returns
        -------
        :class:`~tweepy.models.User`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/mute-block-report-users/api-reference/post-blocks-create
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

        Parameters
        ----------
        screen_name
            |screen_name|
        user_id
            |user_id|
        include_entities
            |include_entities|
        skip_status
            |skip_status|

        Returns
        -------
        :class:`~tweepy.models.User`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/mute-block-report-users/api-reference/post-blocks-destroy
        """
        return self.request(
            'POST', 'blocks/destroy', endpoint_parameters=(
                'screen_name', 'user_id', 'include_entities', 'skip_status'
            ), **kwargs
        )

    @payload('user')
    def create_mute(self, **kwargs):
        """create_mute(*, screen_name, user_id)

        Mutes the user specified in the ID parameter for the authenticating
        user.

        Parameters
        ----------
        screen_name
            |screen_name|
        user_id
            |user_id|

        Returns
        -------
        :class:`~tweepy.models.User`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/mute-block-report-users/api-reference/post-mutes-users-create
        """
        return self.request(
            'POST', 'mutes/users/create', endpoint_parameters=(
                'screen_name', 'user_id'
            ), **kwargs
        )

    @payload('user')
    def destroy_mute(self, **kwargs):
        """destroy_mute(*, screen_name, user_id)

        Un-mutes the user specified in the ID parameter for the authenticating
        user.

        Parameters
        ----------
        screen_name
            |screen_name|
        user_id
            |user_id|

        Returns
        -------
        :class:`~tweepy.models.User`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/mute-block-report-users/api-reference/post-mutes-users-destroy
        """
        return self.request(
            'POST', 'mutes/users/destroy', endpoint_parameters=(
                'screen_name', 'user_id'
            ), **kwargs
        )

    @payload('user')
    def report_spam(self, **kwargs):
        """report_spam(*, screen_name, user_id, perform_block)

        Report the specified user as a spam account to Twitter.

        Parameters
        ----------
        screen_name
            |screen_name|
        user_id
            |user_id|
        perform_block
            A boolean indicating if the reported account should be blocked.
            Defaults to True.

        Returns
        -------
        :class:`~tweepy.models.User`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/mute-block-report-users/api-reference/post-users-report_spam
        """
        return self.request(
            'POST', 'users/report_spam', endpoint_parameters=(
                'screen_name', 'user_id', 'perform_block'
            ), **kwargs
        )

    # Sending and receiving events

    def delete_direct_message(self, id, **kwargs):
        """delete_direct_message(id)

        Deletes the direct message specified in the required ID parameter. The
        authenticating user must be the recipient of the specified direct
        message. Direct Messages are only removed from the interface of the
        user context provided. Other members of the conversation can still
        access the Direct Messages.

        .. versionchanged:: 4.0
            Renamed from ``API.destroy_direct_message``

        Parameters
        ----------
        id
            The ID of the Direct Message that should be deleted.

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/direct-messages/sending-and-receiving/api-reference/delete-message-event
        """
        return self.request(
            'DELETE', 'direct_messages/events/destroy', endpoint_parameters=(
                'id',
            ), id=id, **kwargs
        )

    @pagination(mode='dm_cursor')
    @payload('direct_message', list=True)
    def get_direct_messages(self, **kwargs):
        """get_direct_messages(*, count, cursor)

        Returns all Direct Message events (both sent and received) within the
        last 30 days. Sorted in reverse-chronological order.

        .. versionchanged:: 4.0
            Renamed from ``API.list_direct_messages``

        Parameters
        ----------
        count
            |count|
        cursor
            |cursor|

        Returns
        -------
        :py:class:`List`\[:class:`~tweepy.models.DirectMessage`]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/direct-messages/sending-and-receiving/api-reference/list-events
        """
        return self.request(
            'GET', 'direct_messages/events/list', endpoint_parameters=(
                'count', 'cursor'
            ), **kwargs
        )

    @payload('direct_message')
    def get_direct_message(self, id, **kwargs):
        """get_direct_message(id)

        Returns a specific direct message.

        Parameters
        ----------
        id
            The ID of the Direct Message event that should be returned.

        Returns
        -------
        :class:`~tweepy.models.DirectMessage`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/direct-messages/sending-and-receiving/api-reference/get-event
        """
        return self.request(
            'GET', 'direct_messages/events/show', endpoint_parameters=(
                'id',
            ), id=id, **kwargs
        )

    @payload('direct_message')
    def send_direct_message(
        self, recipient_id, text, *, quick_reply_options=None,
        attachment_type=None, attachment_media_id=None, ctas=None, **kwargs
    ):
        """send_direct_message(recipient_id, text, *, quick_reply_options, \
                               attachment_type, attachment_media_id, ctas)

        Sends a new direct message to the specified user from the
        authenticating user.

        Parameters
        ----------
        recipient_id
            The ID of the user who should receive the direct message.
        text
            The text of your Direct Message. Max length of 10,000 characters.
        quick_reply_options
            Array of Options objects (20 max).
        attachment_type
            The attachment type. Can be media or location.
        attachment_media_id
            A media id to associate with the message. A Direct Message may only
            reference a single media_id.
        ctas
            Array of 1-3 call-to-action (CTA) button objects

        Returns
        -------
        :class:`~tweepy.models.DirectMessage`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/direct-messages/sending-and-receiving/api-reference/new-event
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

    # Typing indicator and read receipts

    def indicate_direct_message_typing(self, recipient_id, **kwargs):
        """indicate_direct_message_typing(recipient_id)

        Displays a visual typing indicator in the recipient’s Direct Message
        conversation view with the sender. Each request triggers a typing
        indicator animation with a duration of ~3 seconds.

        .. versionadded:: 4.9

        Parameters
        ----------
        recipient_id
            The user ID of the user to receive the typing indicator.

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/direct-messages/typing-indicator-and-read-receipts/api-reference/new-typing-indicator
        """
        return self.request(
            'POST', 'direct_messages/indicate_typing', endpoint_parameters=(
                'recipient_id',
            ), recipient_id=recipient_id, **kwargs
        )

    def mark_direct_message_read(self, last_read_event_id, recipient_id,
                                 **kwargs):
        """mark_direct_message_read(last_read_event_id, recipient_id)

        Marks a message as read in the recipient’s Direct Message conversation
        view with the sender.

        .. versionadded:: 4.9

        Parameters
        ----------
        last_read_event_id
            The message ID of the most recent message to be marked read. All
            messages before it will be marked read as well.
        recipient_id
            The user ID of the user the message is from.

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/direct-messages/typing-indicator-and-read-receipts/api-reference/new-read-receipt
        """
        return self.request(
            'POST', 'direct_messages/mark_read', endpoint_parameters=(
                'last_read_event_id', 'recipient_id'
            ), last_read_event_id=last_read_event_id,
            recipient_id=recipient_id, **kwargs
        )

    # Upload media

    @payload('media')
    def get_media_upload_status(self, media_id, **kwargs):
        """get_media_upload_status(media_id)

        Check on the progress of a chunked media upload. If the upload has
        succeeded, it's safe to create a Tweet with this ``media_id``.

        Parameters
        ----------
        media_id
            The ID of the media to check.

        Returns
        -------
        :class:`~tweepy.models.Media`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/media/upload-media/api-reference/get-media-upload-status
        """
        return self.request(
            'GET', 'media/upload', endpoint_parameters=(
                'command', 'media_id'
            ), command='STATUS', media_id=media_id, upload_api=True, **kwargs
        )

    def create_media_metadata(self, media_id, alt_text, **kwargs):
        """create_media_metadata(media_id, alt_text)

        This endpoint can be used to provide additional information about the
        uploaded ``media_id``. This feature is currently only supported for
        images and GIFs. Call this endpoint to attach additional metadata such
        as image alt text.

        Parameters
        ----------
        media_id
            The ID of the media to add alt text to.
        alt_text
            The alt text to add to the image.

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/media/upload-media/api-reference/post-media-metadata-create
        """
        json_payload = {
            'media_id': media_id,
            'alt_text': {'text': alt_text}
        }

        return self.request(
            'POST', 'media/metadata/create', json_payload=json_payload,
            upload_api=True, **kwargs
        )

    def media_upload(self, filename, *, file=None, chunked=False,
                     media_category=None, additional_owners=None, **kwargs):
        """media_upload(filename, *, file, chunked, media_category, \
                        additional_owners)

        Use this to upload media to Twitter. This calls either
        :func:`API.simple_upload` or :func:`API.chunked_upload`. Chunked media
        upload is automatically used for videos. If ``chunked`` is set or the
        media is a video, ``wait_for_async_finalize`` can be specified as a
        keyword argument to be passed to :func:`API.chunked_upload`.

        Parameters
        ----------
        filename
            |filename|
        file
            |file|
        chunked
            Whether or not to use chunked media upload. Videos use chunked
            upload regardless of this parameter. Defaults to ``False``.
        media_category
            |media_category|
        additional_owners
            |additional_owners|

        Returns
        -------
        :class:`~tweepy.models.Media`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/media/upload-media/overview
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
        """simple_upload(filename, *, file, media_category, additional_owners)

        Use this endpoint to upload media to Twitter. This does not use the
        chunked upload endpoints.

        Parameters
        ----------
        filename
            |filename|
        file
            |file|
        media_category
            |media_category|
        additional_owners
            |additional_owners|

        Returns
        -------
        :class:`~tweepy.models.Media`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/media/upload-media/api-reference/post-media-upload
        """
        with contextlib.ExitStack() as stack:
            if file is not None:
                files = {'media': (filename, file)}
            else:
                files = {'media': stack.enter_context(open(filename, 'rb'))}

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
        """chunked_upload( \
            filename, *, file, file_type, wait_for_async_finalize, \
            media_category, additional_owners \
        )

        Use this to upload media to Twitter. This uses the chunked upload
        endpoints and calls :func:`API.chunked_upload_init`,
        :func:`API.chunked_upload_append`, and
        :func:`API.chunked_upload_finalize`. If ``wait_for_async_finalize`` is
        set, this calls :func:`API.get_media_upload_status` as well.

        Parameters
        ----------
        filename
            |filename|
        file
            |file|
        file_type
            The MIME type of the media being uploaded.
        wait_for_async_finalize
            Whether to wait for Twitter's API to finish processing the media.
            Defaults to ``True``.
        media_category
            |media_category|
        additional_owners
            |additional_owners|

        Returns
        -------
        :class:`~tweepy.models.Media`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/media/upload-media/uploading-media/chunked-media-upload
        """
        fp = file or open(filename, 'rb')

        start = fp.tell()
        fp.seek(0, 2)  # Seek to end of file
        file_size = fp.tell() - start
        fp.seek(start)

        min_chunk_size, remainder = divmod(file_size, 1000)
        min_chunk_size += bool(remainder)

        # Use 1 MiB as default chunk size
        chunk_size = kwargs.pop('chunk_size', 1024 * 1024)
        # Max chunk size is 5 MiB
        chunk_size = max(min(chunk_size, 5 * 1024 * 1024), min_chunk_size)

        segments, remainder = divmod(file_size, chunk_size)
        segments += bool(remainder)

        media_id = self.chunked_upload_init(
            file_size, file_type, media_category=media_category,
            additional_owners=additional_owners, **kwargs
        ).media_id

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

    def chunked_upload_append(self, media_id, media, segment_index, **kwargs):
        """chunked_upload_append(media_id, media, segment_index)

        Use this endpoint to upload a chunk (consecutive byte range) of the
        media file.

        Parameters
        ----------
        media_id
            The ``media_id`` returned from the initialization.
        media
            The raw binary file content being uploaded. It must be <= 5 MB.
        segment_index
            An ordered index of file chunk. It must be between 0-999 inclusive.
            The first segment has index 0, second segment has index 1, and so
            on.

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/media/upload-media/api-reference/post-media-upload-append
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
        """chunked_upload_finalize(media_id)

        Use this endpoint after the entire media file is uploaded via
        appending. If (and only if) the response contains a
        ``processing_info field``, it may also be necessary to check its status
        and wait for it to return success before proceeding to Tweet creation.

        Parameters
        ----------
        media_id
            The ``media_id`` returned from the initialization.

        Returns
        -------
        :class:`~tweepy.models.Media`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/media/upload-media/api-reference/post-media-upload-finalize
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

    @payload('media')
    def chunked_upload_init(self, total_bytes, media_type, *,
                            media_category=None, additional_owners=None,
                            **kwargs):
        """chunked_upload_init(total_bytes, media_type, *, media_category, \
                               additional_owners)

        Use this endpoint to initiate a chunked file upload session.

        Parameters
        ----------
        total_bytes
            The size of the media being uploaded in bytes.
        media_type
            The MIME type of the media being uploaded.
        media_category
            |media_category|
        additional_owners
            |additional_owners|

        Returns
        -------
        :class:`~tweepy.models.Media`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/media/upload-media/api-reference/post-media-upload-init
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

    # Get locations with trending topics

    @payload('json')
    def available_trends(self, **kwargs):
        """available_trends()

        Returns the locations that Twitter has trending topic information for.
        The response is an array of "locations" that encode the location's
        WOEID (a Yahoo! Where On Earth ID) and some other human-readable
        information such as a canonical name and country the location belongs
        in.

        .. versionchanged:: 4.0
            Renamed from ``API.trends_available``

        Returns
        -------
        :class:`dict`
            JSON

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/trends/locations-with-trending-topics/api-reference/get-trends-available
        """
        return self.request('GET', 'trends/available', **kwargs)

    @payload('json')
    def closest_trends(self, lat, long, **kwargs):
        """closest_trends(lat, long)

        Returns the locations that Twitter has trending topic information for,
        closest to a specified location.

        The response is an array of “locations” that encode the location’s
        WOEID and some other human-readable information such as a canonical
        name and country the location belongs in.

        A WOEID is a Yahoo! Where On Earth ID.

        .. versionchanged:: 4.0
            Renamed from ``API.trends_closest``

        Parameters
        ----------
        lat
            If provided with a long parameter the available trend locations
            will be sorted by distance, nearest to furthest, to the co-ordinate
            pair. The valid ranges for longitude is -180.0 to +180.0 (West is
            negative, East is positive) inclusive.
        long
            If provided with a lat parameter the available trend locations will
            be sorted by distance, nearest to furthest, to the co-ordinate
            pair. The valid ranges for longitude is -180.0 to +180.0 (West is
            negative, East is positive) inclusive.

        Returns
        -------
        :class:`dict`
            JSON

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/trends/locations-with-trending-topics/api-reference/get-trends-closest
        """
        return self.request(
            'GET', 'trends/closest', endpoint_parameters=(
                'lat', 'long'
            ), lat=lat, long=long, **kwargs
        )

    # Get trends near a location

    @payload('json')
    def get_place_trends(self, id, **kwargs):
        """get_place_trends(id *, exclude)

        Returns the top 50 trending topics for a specific WOEID, if trending
        information is available for it.

        The response is an array of “trend” objects that encode the name of the
        trending topic, the query parameter that can be used to search for the
        topic on Twitter Search, and the Twitter Search URL.

        This information is cached for 5 minutes. Requesting more frequently
        than that will not return any more data, and will count against your
        rate limit usage.

        The tweet_volume for the last 24 hours is also returned for many trends
        if this is available.

        .. versionchanged:: 4.0
            Renamed from ``API.trends_place``

        Parameters
        ----------
        id
            The Yahoo! Where On Earth ID of the location to return trending
            information for. Global information is available by using 1 as the
            WOEID.
        exclude
            Setting this equal to hashtags will remove all hashtags from the
            trends list.

        Returns
        -------
        :class:`dict`
            JSON

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/trends/trends-for-location/api-reference/get-trends-place
        """
        return self.request(
            'GET', 'trends/place', endpoint_parameters=(
                'id', 'exclude'
            ), id=id, **kwargs
        )

    # Get information about a place

    @payload('place')
    def geo_id(self, place_id, **kwargs):
        """geo_id(place_id)

        Given ``place_id``, provide more details about that place.

        Parameters
        ----------
        place_id
            Valid Twitter ID of a location.

        Returns
        -------
        :class:`~tweepy.models.Place`

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/geo/place-information/api-reference/get-geo-id-place_id
        """
        return self.request('GET', f'geo/id/{place_id}', **kwargs)

    # Get places near a location

    @payload('place', list=True)
    def reverse_geocode(self, lat, long, **kwargs):
        """reverse_geocode(lat, long, *, accuracy, granularity, max_results)

        Given a latitude and a longitude, searches for up to 20 places that can
        be used as a ``place_id`` when updating a status.

        This request is an informative call and will deliver generalized
        results about geography.

        Parameters
        ----------
        lat
            The location's latitude.
        long
            The location's longitude.
        accuracy
            Specify the "region" in which to search, such as a number (then
            this is a radius in meters, but it can also take a string that is
            suffixed with ft to specify feet). If this is not passed in, then
            it is assumed to be 0m
        granularity
            Assumed to be ``neighborhood`` by default; can also be ``city``.
        max_results
            A hint as to the maximum number of results to return. This is only
            a guideline, which may not be adhered to.

        Returns
        -------
        :py:class:`List`\[:class:`~tweepy.models.Place`]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/geo/places-near-location/api-reference/get-geo-reverse_geocode
        """
        return self.request(
            'GET', 'geo/reverse_geocode', endpoint_parameters=(
                'lat', 'long', 'accuracy', 'granularity', 'max_results'
            ), lat=lat, long=long, **kwargs
        )

    @payload('place', list=True)
    def search_geo(self, **kwargs):
        """search_geo(*, lat, long, query, ip, granularity, max_results)

        Search for places that can be attached to a Tweet via
        :func:`API.update_status`. Given a latitude and a longitude pair, an IP
        address, or a name, this request will return a list of all the valid
        places that can be used as the ``place_id`` when updating a status.

        Conceptually, a query can be made from the user's location, retrieve a
        list of places, have the user validate the location they are at, and
        then send the ID of this location with a call to
        :func:`API.update_status`.

        This is the recommended method to use find places that can be attached
        to :func:`API.update_status`. Unlike :func:`API.reverse_geocode` which
        provides raw data access, this endpoint can potentially re-order places
        with regards to the user who is authenticated. This approach is also
        preferred for interactive place matching with the user.

        Some parameters in this method are only required based on the existence
        of other parameters. For instance, ``lat`` is required if ``long`` is
        provided, and vice-versa.

        .. versionchanged:: 4.0
            Renamed from ``API.geo_search``

        Parameters
        ----------
        lat
            The latitude to search around. This parameter will be ignored
            unless it is inside the range -90.0 to +90.0 (North is positive)
            inclusive. It will also be ignored if there isn't a corresponding
            ``long`` parameter.
        long
            The longitude to search around. The valid ranges for longitude are
            -180.0 to +180.0 (East is positive) inclusive. This parameter will
            be ignored if outside that range, if it is not a number, if
            ``geo_enabled`` is turned off, or if there not a corresponding
            ``lat`` parameter.
        query
            Free-form text to match against while executing a geo-based query,
            best suited for finding nearby locations by name.
        ip
            An IP address. Used when attempting to fix geolocation based off of
            the user's IP address.
        granularity
            This is the minimal granularity of place types to return and must
            be one of: ``neighborhood``, ``city``, ``admin`` or ``country``.
            If no granularity is provided for the request ``neighborhood`` is
            assumed.

            Setting this to ``city``, for example, will find places which have
            a type of ``city``, ``admin`` or ``country``.
        max_results
            A hint as to the number of results to return. This does not
            guarantee that the number of results returned will equal
            ``max_results``, but instead informs how many "nearby" results to
            return. Ideally, only pass in the number of places you intend to
            display to the user here.

        Returns
        -------
        :py:class:`List`\[:class:`~tweepy.models.Place`]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/geo/places-near-location/api-reference/get-geo-search
        """
        return self.request(
            'GET', 'geo/search', endpoint_parameters=(
                'lat', 'long', 'query', 'ip', 'granularity', 'max_results'
            ), **kwargs
        )

    # Get Twitter supported languages

    @payload('json')
    def supported_languages(self, **kwargs):
        """supported_languages()

        Returns the list of languages supported by Twitter along with the
        language code supported by Twitter.

        The language code may be formatted as ISO 639-1 alpha-2 (``en``), ISO
        639-3 alpha-3 (``msa``), or ISO 639-1 alpha-2 combined with an ISO
        3166-1 alpha-2 localization (``zh-tw``).

        Returns
        -------
        :class:`dict`
            JSON

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/developer-utilities/supported-languages/api-reference/get-help-languages
        """
        return self.request('GET', 'help/languages', **kwargs)

    # Get app rate limit status

    @payload('json')
    def rate_limit_status(self, **kwargs):
        """rate_limit_status(*, resources)

        Returns the current rate limits for methods belonging to the specified
        resource families. When using application-only auth, this method's
        response indicates the application-only auth rate limiting context.

        Parameters
        ----------
        resources
            A comma-separated list of resource families you want to know the
            current rate limit disposition for.

        Returns
        -------
        :class:`dict`
            JSON

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/developer-utilities/rate-limit-status/api-reference/get-application-rate_limit_status
        """
        return self.request(
            'GET', 'application/rate_limit_status', endpoint_parameters=(
                'resources',
            ), use_cache=False, **kwargs
        )
