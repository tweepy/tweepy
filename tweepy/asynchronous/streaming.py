# Tweepy
# Copyright 2009-2023 Joshua Roesslein
# See LICENSE for details.

import asyncio
import json
import logging
from math import inf
from platform import python_version
import traceback

import aiohttp

import tweepy
from tweepy.asynchronous.client import AsyncBaseClient
from tweepy.client import Response
from tweepy.errors import TweepyException
from tweepy.streaming import StreamResponse, StreamRule
from tweepy.tweet import Tweet

log = logging.getLogger(__name__)


class AsyncBaseStream:

    def __init__(self, *, max_retries=inf, proxy=None):
        self.max_retries = max_retries
        self.proxy = proxy

        self.session = None
        self.task = None
        self.user_agent = (
            f"Python/{python_version()} "
            f"aiohttp/{aiohttp.__version__} "
            f"Tweepy/{tweepy.__version__}"
        )

    async def _connect(
        self, method, url, params=None, headers=None, body=None,
        oauth_client=None, timeout=21
    ):
        error_count = 0
        # https://developer.twitter.com/en/docs/twitter-api/v1/tweets/filter-realtime/guides/connecting
        # https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/integrate/handling-disconnections
        # https://developer.twitter.com/en/docs/twitter-api/tweets/volume-streams/integrate/handling-disconnections
        network_error_wait = 0
        network_error_wait_step = 0.25
        network_error_wait_max = 16
        http_error_wait = http_error_wait_start = 5
        http_error_wait_max = 320
        http_429_error_wait_start = 60

        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(enable_cleanup_closed=True),
                timeout=aiohttp.ClientTimeout(sock_read=timeout)
            )
        self.session.headers["User-Agent"] = self.user_agent

        try:
            while error_count <= self.max_retries:
                try:
                    if oauth_client is not None:
                        url, headers, body = oauth_client.sign(
                            url, http_method=method, headers=headers, body=body
                        )
                    async with self.session.request(
                        method, url, params=params, headers=headers, data=body,
                        proxy=self.proxy
                    ) as resp:
                        if resp.status == 200:
                            error_count = 0
                            http_error_wait = http_error_wait_start
                            network_error_wait = 0

                            await self.on_connect()

                            async for line in resp.content:
                                line = line.strip()
                                if line:
                                    await self.on_data(line)
                                else:
                                    await self.on_keep_alive()

                            await self.on_closed(resp)
                        else:
                            await self.on_request_error(resp.status)
                            # The error text is logged here instead of in
                            # on_request_error to keep on_request_error
                            # backwards-compatible. In a future version, the
                            # ClientResponse should be passed to
                            # on_request_error.
                            response_text = await resp.text()
                            log.error(
                                "HTTP error response text: %s", response_text
                            )

                            error_count += 1

                            if resp.status in (420, 429):
                                if http_error_wait < http_429_error_wait_start:
                                    http_error_wait = http_429_error_wait_start

                            await asyncio.sleep(http_error_wait)

                            http_error_wait *= 2
                            if resp.status != 420:
                                if http_error_wait > http_error_wait_max:
                                    http_error_wait = http_error_wait_max
                except (aiohttp.ClientConnectionError,
                        aiohttp.ClientPayloadError) as e:
                    await self.on_connection_error()
                    # The error text is logged here instead of in
                    # on_connection_error to keep on_connection_error
                    # backwards-compatible. In a future version, the error
                    # should be passed to on_connection_error.
                    log.error(
                        "Connection error: %s",
                        "".join(
                            traceback.format_exception_only(type(e), e)
                        ).rstrip()
                    )

                    await asyncio.sleep(network_error_wait)

                    network_error_wait += network_error_wait_step
                    if network_error_wait > network_error_wait_max:
                        network_error_wait = network_error_wait_max
        except asyncio.CancelledError:
            return
        except Exception as e:
            await self.on_exception(e)
        finally:
            await self.session.close()
            await self.on_disconnect()

    def disconnect(self):
        """Disconnect the stream"""
        if self.task is not None:
            self.task.cancel()

    async def on_closed(self, resp):
        """|coroutine|

        This is called when the stream has been closed by Twitter.

        Parameters
        ----------
        response : aiohttp.ClientResponse
            The response from Twitter
        """
        log.error("Stream connection closed by Twitter")

    async def on_connect(self):
        """|coroutine|

        This is called after successfully connecting to the streaming API.
        """
        log.info("Stream connected")

    async def on_connection_error(self):
        """|coroutine|

        This is called when the stream connection errors or times out.
        """
        log.error("Stream connection has errored or timed out")

    async def on_disconnect(self):
        """|coroutine|

        This is called when the stream has disconnected.
        """
        log.info("Stream disconnected")

    async def on_exception(self, exception):
        """|coroutine|

        This is called when an unhandled exception occurs.

        Parameters
        ----------
        exception : Exception
            The unhandled exception
        """
        log.exception("Stream encountered an exception")

    async def on_keep_alive(self):
        """|coroutine|

        This is called when a keep-alive signal is received.
        """
        log.debug("Received keep-alive signal")

    async def on_request_error(self, status_code):
        """|coroutine|

        This is called when a non-200 HTTP status code is encountered.

        Parameters
        ----------
        status_code : int
            The HTTP status code encountered
        """
        log.error("Stream encountered HTTP Error: %d", status_code)


class AsyncStreamingClient(AsyncBaseClient, AsyncBaseStream):
    """Stream realtime Tweets asynchronously with Twitter API v2

    .. versionadded:: 4.10

    Parameters
    ----------
    bearer_token : str
        Twitter API Bearer Token
    return_type : type[dict | requests.Response | Response]
        Type to return from requests to the API
    wait_on_rate_limit : bool
        Whether or not to wait before retrying when a rate limit is
        encountered. This applies to requests besides those that connect to a
        stream (see ``max_retries``).
    max_retries: int | None
        Number of times to attempt to (re)connect the stream.
    proxy : str | None
        URL of the proxy to use when connecting to the stream

    Attributes
    ----------
    session : aiohttp.ClientSession | None
        Aiohttp client session used to connect to the API
    task : asyncio.Task | None
        The task running the stream
    user_agent : str
        User agent used when connecting to the API
    """

    def __init__(self, bearer_token, *, return_type=Response,
                 wait_on_rate_limit=False, **kwargs):
        """__init__( \
            bearer_token, *, return_type=Response, wait_on_rate_limit=False, \
            max_retries=inf, proxy=None \
        )
        """
        AsyncBaseClient.__init__(self, bearer_token, return_type=return_type,
                                 wait_on_rate_limit=wait_on_rate_limit)
        AsyncBaseStream.__init__(self, **kwargs)

    async def _connect(self, method, endpoint, **kwargs):
        url = f"https://api.twitter.com/2/tweets/{endpoint}/stream"
        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        await super()._connect(method, url, headers=headers, **kwargs)

    def _process_data(self, data, data_type=None):
        if data_type is StreamRule:
            if isinstance(data, list):
                rules = []
                for rule in data:
                    if "tag" in rule:
                        rules.append(StreamRule(
                            value=rule["value"], id=rule["id"], tag=rule["tag"]
                        ))
                    else:
                        rules.append(StreamRule(value=rule["value"],
                                                id=rule["id"]))
                return rules
            elif data is not None:
                if "tag" in data:
                    return StreamRule(value=data["value"], id=data["id"],
                                      tag=data["tag"])
                else:
                    return StreamRule(value=data["value"], id=data["id"])
        else:
            return super()._process_data(data, data_type=data_type)

    async def add_rules(self, add, **params):
        """add_rules(add, *, dry_run)

        |coroutine|

        Add rules to filtered stream.

        Parameters
        ----------
        add : list[StreamRule] | StreamRule
            Specifies the operation you want to perform on the rules.
        dry_run : bool
            Set to true to test the syntax of your rule without submitting it.
            This is useful if you want to check the syntax of a rule before
            removing one or more of your existing rules.

        Returns
        -------
        dict | requests.Response | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/api-reference/post-tweets-search-stream-rules
        """
        json = {"add": []}
        if isinstance(add, StreamRule):
            add = (add,)
        for rule in add:
            if rule.tag is not None:
                json["add"].append({"value": rule.value, "tag": rule.tag})
            else:
                json["add"].append({"value": rule.value})

        return await self._make_request(
            "POST", f"/2/tweets/search/stream/rules", params=params,
            endpoint_parameters=("dry_run",), json=json, data_type=StreamRule
        )

    async def delete_rules(self, ids, **params):
        """delete_rules(ids, *, dry_run)

        |coroutine|

        Delete rules from filtered stream.

        Parameters
        ----------
        ids : int | str | list[int | str | StreamRule] | StreamRule
            Array of rule IDs, each one representing a rule already active in
            your stream. IDs must be submitted as strings.
        dry_run : bool
            Set to true to test the syntax of your rule without submitting it.
            This is useful if you want to check the syntax of a rule before
            removing one or more of your existing rules.

        Returns
        -------
        dict | requests.Response | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/api-reference/post-tweets-search-stream-rules
        """
        json = {"delete": {"ids": []}}
        if isinstance(ids, (int, str, StreamRule)):
            ids = (ids,)
        for id in ids:
            if isinstance(id, StreamRule):
                json["delete"]["ids"].append(str(id.id))
            else:
                json["delete"]["ids"].append(str(id))

        return await self._make_request(
            "POST", f"/2/tweets/search/stream/rules", params=params,
            endpoint_parameters=("dry_run",), json=json, data_type=StreamRule
        )

    def filter(self, **params):
        """filter( \
            *, backfill_minutes=None, expansions=None, media_fields=None, \
            place_fields=None, poll_fields=None, tweet_fields=None, \
            user_fields=None \
        )

        Streams Tweets in real-time based on a specific set of filter rules.

        If you are using the academic research product track, you can connect
        up to two `redundant connections <filter redundant connections_>`_ to
        maximize your streaming up-time.

        The Tweets returned by this endpoint count towards the Project-level
        `Tweet cap`_.

        Parameters
        ----------
        backfill_minutes : int | None
            By passing this parameter, you can request up to five (5) minutes
            worth of streaming data that you might have missed during a
            disconnection to be delivered to you upon reconnection. The
            backfilled Tweets will automatically flow through the reconnected
            stream, with older Tweets generally being delivered before any
            newly matching Tweets. You must include a whole number between 1
            and 5 as the value to this parameter.

            This feature will deliver duplicate Tweets, meaning that if you
            were disconnected for 90 seconds, and you requested two minutes of
            backfill, you will receive 30 seconds worth of duplicate Tweets.
            Due to this, you should make sure your system is tolerant of
            duplicate data.

            This feature is currently only available to the Academic Research
            product track.
        expansions : list[str] | str
            :ref:`expansions_parameter`
        media_fields : list[str] | str
            :ref:`media_fields_parameter`
        place_fields : list[str] | str
            :ref:`place_fields_parameter`
        poll_fields : list[str] | str
            :ref:`poll_fields_parameter`
        tweet_fields : list[str] | str
            :ref:`tweet_fields_parameter`
        user_fields : list[str] | str
            :ref:`user_fields_parameter`

        Raises
        ------
        TweepyException
            When the stream is already connected

        Returns
        -------
        asyncio.Task
            The task running the stream

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/api-reference/get-tweets-search-stream

        .. _filter redundant connections: https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/integrate/recovery-and-redundancy-features
        .. _Tweet cap: https://developer.twitter.com/en/docs/twitter-api/tweet-caps
        """
        if self.task is not None and not self.task.done():
            raise TweepyException("Stream is already connected")

        endpoint = "search"

        params = self._process_params(
            params, endpoint_parameters=(
                "backfill_minutes", "expansions", "media.fields",
                "place.fields", "poll.fields", "tweet.fields", "user.fields"
            )
        )

        self.task = asyncio.create_task(
            self._connect("GET", endpoint, params=params)
        )
        # Use name parameter when support for Python 3.7 is dropped
        return self.task

    async def get_rules(self, **params):
        """get_rules(*, ids)

        |coroutine|

        Return a list of rules currently active on the streaming endpoint,
        either as a list or individually.

        Parameters
        ----------
        ids : list[str] | str
            Comma-separated list of rule IDs. If omitted, all rules are
            returned.

        Returns
        -------
        dict | requests.Response | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/api-reference/get-tweets-search-stream-rules
        """
        return await self._make_request(
            "GET", f"/2/tweets/search/stream/rules", params=params,
            endpoint_parameters=("ids",), data_type=StreamRule
        )

    def sample(self, **params):
        """sample( \
            *, backfill_minutes=None, expansions=None, media_fields=None, \
            place_fields=None, poll_fields=None, tweet_fields=None, \
            user_fields=None \
        )

        Streams about 1% of all Tweets in real-time.

        If you are using the academic research product track, you can connect
        up to two `redundant connections <sample redundant connections_>`_ to
        maximize your streaming up-time.

        Parameters
        ----------
        backfill_minutes : int | None
            By passing this parameter, you can request up to five (5) minutes
            worth of streaming data that you might have missed during a
            disconnection to be delivered to you upon reconnection. The
            backfilled Tweets will automatically flow through the reconnected
            stream, with older Tweets generally being delivered before any
            newly matching Tweets. You must include a whole number between 1
            and 5 as the value to this parameter.

            This feature will deliver duplicate Tweets, meaning that if you
            were disconnected for 90 seconds, and you requested two minutes of
            backfill, you will receive 30 seconds worth of duplicate Tweets.
            Due to this, you should make sure your system is tolerant of
            duplicate data.

            This feature is currently only available to the Academic Research
            product track.
        expansions : list[str] | str
            :ref:`expansions_parameter`
        media_fields : list[str] | str
            :ref:`media_fields_parameter`
        place_fields : list[str] | str
            :ref:`place_fields_parameter`
        poll_fields : list[str] | str
            :ref:`poll_fields_parameter`
        tweet_fields : list[str] | str
            :ref:`tweet_fields_parameter`
        user_fields : list[str] | str
            :ref:`user_fields_parameter`

        Raises
        ------
        TweepyException
            When the stream is already connected

        Returns
        -------
        asyncio.Task
            The task running the stream

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/volume-streams/api-reference/get-tweets-sample-stream

        .. _sample redundant connections: https://developer.twitter.com/en/docs/twitter-api/tweets/volume-streams/integrate/recovery-and-redundancy-features
        """
        if self.task is not None and not self.task.done():
            raise TweepyException("Stream is already connected")

        endpoint = "sample"

        params = self._process_params(
            params, endpoint_parameters=(
                "backfill_minutes", "expansions", "media.fields",
                "place.fields", "poll.fields", "tweet.fields", "user.fields"
            )
        )

        self.task = asyncio.create_task(
            self._connect("GET", endpoint, params=params)
        )
        # Use name parameter when support for Python 3.7 is dropped
        return self.task

    async def on_data(self, raw_data):
        """|coroutine|

        This is called when raw data is received from the stream.
        This method handles sending the data to other methods.

        Parameters
        ----------
        raw_data : JSON
            The raw data from the stream

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/integrate/consuming-streaming-data
        """
        data = json.loads(raw_data)

        tweet = None
        includes = {}
        errors = []
        matching_rules = []

        if "data" in data:
            tweet = Tweet(data["data"])
            await self.on_tweet(tweet)
        if "includes" in data:
            includes = self._process_includes(data["includes"])
            await self.on_includes(includes)
        if "errors" in data:
            errors = data["errors"]
            await self.on_errors(errors)
        if "matching_rules" in data:
            matching_rules = [
                StreamRule(id=rule["id"], tag=rule["tag"])
                for rule in data["matching_rules"]
            ]
            await self.on_matching_rules(matching_rules)

        await self.on_response(
            StreamResponse(tweet, includes, errors, matching_rules)
        )

    async def on_tweet(self, tweet):
        """|coroutine|

        This is called when a Tweet is received.

        Parameters
        ----------
        tweet : Tweet
            The Tweet received
        """
        pass

    async def on_includes(self, includes):
        """|coroutine|

        This is called when includes are received.

        Parameters
        ----------
        includes : dict
            The includes received
        """
        pass

    async def on_errors(self, errors):
        """|coroutine|

        This is called when errors are received.

        Parameters
        ----------
        errors : dict
            The errors received
        """
        log.error("Received errors: %s", errors)

    async def on_matching_rules(self, matching_rules):
        """|coroutine|

        This is called when matching rules are received.

        Parameters
        ----------
        matching_rules : list[StreamRule]
            The matching rules received
        """
        pass

    async def on_response(self, response):
        """|coroutine|

        This is called when a response is received.

        Parameters
        ----------
        response : StreamResponse
            The response received
        """
        log.debug("Received response: %s", response)
