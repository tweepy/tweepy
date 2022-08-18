# Tweepy
# Copyright 2009-2022 Joshua Roesslein
# See LICENSE for details.

# Appengine users: https://developers.google.com/appengine/docs/python/sockets/#making_httplib_use_sockets

from collections import namedtuple
import json
import logging
from math import inf
from platform import python_version
import ssl
from threading import Thread
from time import sleep
from typing import NamedTuple

import requests
from requests_oauthlib import OAuth1
import urllib3

import tweepy
from tweepy.client import BaseClient, Response
from tweepy.errors import TweepyException
from tweepy.models import Status
from tweepy.tweet import Tweet

log = logging.getLogger(__name__)

StreamResponse = namedtuple(
    "StreamResponse", ("data", "includes", "errors", "matching_rules")
)


class BaseStream:

    def __init__(self, *, chunk_size=512, daemon=False, max_retries=inf,
                 proxy=None, verify=True):
        self.chunk_size = chunk_size
        self.daemon = daemon
        self.max_retries = max_retries
        self.proxies = {"https": proxy} if proxy else {}
        self.verify = verify

        self.running = False
        self.session = requests.Session()
        self.thread = None
        self.user_agent = (
            f"Python/{python_version()} "
            f"Requests/{requests.__version__} "
            f"Tweepy/{tweepy.__version__}"
        )

    def _connect(self, method, url, auth=None, params=None, headers=None,
                 body=None):
        self.running = True

        error_count = 0
        # https://developer.twitter.com/en/docs/twitter-api/v1/tweets/filter-realtime/guides/connecting
        # https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/integrate/handling-disconnections
        # https://developer.twitter.com/en/docs/twitter-api/tweets/volume-streams/integrate/handling-disconnections
        stall_timeout = 90
        network_error_wait = network_error_wait_step = 0.25
        network_error_wait_max = 16
        http_error_wait = http_error_wait_start = 5
        http_error_wait_max = 320
        http_420_error_wait_start = 60

        self.session.headers["User-Agent"] = self.user_agent

        try:
            while self.running and error_count <= self.max_retries:
                try:
                    with self.session.request(
                        method, url, params=params, headers=headers, data=body,
                        timeout=stall_timeout, stream=True, auth=auth,
                        verify=self.verify, proxies=self.proxies
                    ) as resp:
                        if resp.status_code == 200:
                            error_count = 0
                            http_error_wait = http_error_wait_start
                            network_error_wait = network_error_wait_step

                            self.on_connect()
                            if not self.running:
                                break

                            for line in resp.iter_lines(
                                chunk_size=self.chunk_size
                            ):
                                if line:
                                    self.on_data(line)
                                else:
                                    self.on_keep_alive()
                                if not self.running:
                                    break

                            if resp.raw.closed:
                                self.on_closed(resp)
                        else:
                            self.on_request_error(resp.status_code)
                            if not self.running:
                                break
                            # The error text is logged here instead of in
                            # on_request_error to keep on_request_error
                            # backwards-compatible. In a future version, the
                            # Response should be passed to on_request_error.
                            log.error(
                                "HTTP error response text: %s", resp.text
                            )

                            error_count += 1

                            if resp.status_code == 420:
                                if http_error_wait < http_420_error_wait_start:
                                    http_error_wait = http_420_error_wait_start

                            sleep(http_error_wait)

                            http_error_wait *= 2
                            if http_error_wait > http_error_wait_max:
                                http_error_wait = http_error_wait_max
                except (requests.ConnectionError, requests.Timeout,
                        requests.exceptions.ChunkedEncodingError,
                        ssl.SSLError, urllib3.exceptions.ReadTimeoutError,
                        urllib3.exceptions.ProtocolError) as exc:
                    # This is still necessary, as a SSLError can actually be
                    # thrown when using Requests
                    # If it's not time out treat it like any other exception
                    if isinstance(exc, ssl.SSLError):
                        if not (exc.args and "timed out" in str(exc.args[0])):
                            raise

                    self.on_connection_error()
                    if not self.running:
                        break

                    sleep(network_error_wait)

                    network_error_wait += network_error_wait_step
                    if network_error_wait > network_error_wait_max:
                        network_error_wait = network_error_wait_max
        except Exception as exc:
            self.on_exception(exc)
        finally:
            self.session.close()
            self.running = False
            self.on_disconnect()

    def _threaded_connect(self, *args, **kwargs):
        self.thread = Thread(target=self._connect, name="Tweepy Stream",
                             args=args, kwargs=kwargs, daemon=self.daemon)
        self.thread.start()
        return self.thread

    def disconnect(self):
        """Disconnect the stream"""
        self.running = False

    def on_closed(self, response):
        """This is called when the stream has been closed by Twitter.

        Parameters
        ----------
        response : requests.Response
            The Response from Twitter
        """
        log.error("Stream connection closed by Twitter")

    def on_connect(self):
        """This is called after successfully connecting to the streaming API.
        """
        log.info("Stream connected")

    def on_connection_error(self):
        """This is called when the stream connection errors or times out."""
        log.error("Stream connection has errored or timed out")

    def on_disconnect(self):
        """This is called when the stream has disconnected."""
        log.info("Stream disconnected")

    def on_exception(self, exception):
        """This is called when an unhandled exception occurs.

        Parameters
        ----------
        exception : Exception
            The unhandled exception
        """
        log.exception("Stream encountered an exception")

    def on_keep_alive(self):
        """This is called when a keep-alive signal is received."""
        log.debug("Received keep-alive signal")

    def on_request_error(self, status_code):
        """This is called when a non-200 HTTP status code is encountered.

        Parameters
        ----------
        status_code : int
            The HTTP status code encountered
        """
        log.error("Stream encountered HTTP error: %d", status_code)


class Stream(BaseStream):
    """Filter and sample realtime Tweets with Twitter API v1.1

    .. note::

        New Twitter Developer Apps created on or after April 29, 2022 `will not
        be able to gain access to v1.1 statuses/sample and v1.1
        statuses/filter`_, the Twitter API v1.1 endpoints that :class:`Stream`
        uses. Twitter API v2 can be used instead with :class:`StreamingClient`.

    Parameters
    ----------
    consumer_key : str
        Twitter API Consumer Key
    consumer_secret : str
        Twitter API Consumer Secret
    access_token: str
        Twitter API Access Token
    access_token_secret : str
        Twitter API Access Token Secret
    chunk_size : int
        The default socket.read size. Default to 512, less than half the size
        of a Tweet so that it reads Tweets with the minimal latency of 2 reads
        per Tweet. Values higher than ~1kb will increase latency by waiting for
        more data to arrive but may also increase throughput by doing fewer
        socket read calls.
    daemon : bool
        Whether or not to use a daemon thread when using a thread to run the
        stream
    max_retries : int
        Max number of times to retry connecting the stream
    proxy : str | None
        URL of the proxy to use when connecting to the stream
    verify : bool | str
        Either a boolean, in which case it controls whether to verify the
        server’s TLS certificate, or a string, in which case it must be a path
        to a CA bundle to use.

    Attributes
    ----------
    running : bool
        Whether there's currently a stream running
    session : :class:`requests.Session`
        Requests Session used to connect to the stream
    thread : :class:`threading.Thread` | None
        Thread used to run the stream
    user_agent : str
        User agent used when connecting to the stream


    .. _will not be able to gain access to v1.1 statuses/sample and v1.1
        statuses/filter: https://twittercommunity.com/t/deprecation-announcement-removing-compliance-messages-from-statuses-filter-and-retiring-statuses-sample-from-the-twitter-api-v1-1/170500
    """

    def __init__(self, consumer_key, consumer_secret, access_token,
                 access_token_secret, **kwargs):
        """__init__( \
            consumer_key, consumer_secret, access_token, access_token_secret, \
            chunk_size=512, daemon=False, max_retries=inf, proxy=None, \
            verify=True \
        )
        """
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        super().__init__(**kwargs)

    def _connect(self, method, endpoint, **kwargs):
        auth = OAuth1(self.consumer_key, self.consumer_secret,
                      self.access_token, self.access_token_secret)
        url = f"https://stream.twitter.com/1.1/{endpoint}.json"
        super()._connect(method, url, auth=auth, **kwargs)

    def filter(self, *, follow=None, track=None, locations=None,
               filter_level=None, languages=None, stall_warnings=False,
               threaded=False):
        """Filter realtime Tweets

        .. deprecated:: 4.9
            `The delivery of compliance messages through the Twitter API v1.1
            endpoint this method uses has been deprecated, and they will stop
            being delivered beginning October 29, 2022.`_ Twitter API v2 can be
            used instead with :meth:`StreamingClient.filter` and/or
            :class:`Client` :ref:`batch compliance <Batch compliance>` methods.

        Parameters
        ----------
        follow : list[int | str] | None
            User IDs, indicating the users to return statuses for in the stream
        track : list[str] | None
            Keywords to track
        locations : list[float] | None
            Specifies a set of bounding boxes to track
        filter_level : str | None
            Setting this parameter to one of none, low, or medium will set the
            minimum value of the filter_level Tweet attribute required to be
            included in the stream. The default value is none, which includes
            all available Tweets.

            When displaying a stream of Tweets to end users (dashboards or live
            feeds at a presentation or conference, for example) it is suggested
            that you set this value to medium.
        languages : list[str] | None
            Setting this parameter to a comma-separated list of `BCP 47`_
            language identifiers corresponding to any of the languages listed
            on Twitter’s `advanced search`_ page will only return Tweets that
            have been detected as being written in the specified languages. For
            example, connecting with language=en will only stream Tweets
            detected to be in the English language.
        stall_warnings : bool
            Specifies whether stall warnings should be delivered
        threaded : bool
            Whether or not to use a thread to run the stream

        Raises
        ------
        TweepyException
            When the stream is already connected or when the number of location
            coordinates is not a multiple of 4

        Returns
        -------
        threading.Thread | None
            The thread if ``threaded`` is set to ``True``, else ``None``

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/tweets/filter-realtime/api-reference/post-statuses-filter

        .. _BCP 47: https://tools.ietf.org/html/bcp47
        .. _advanced search: https://twitter.com/search-advanced
        .. _The delivery of compliance messages through the Twitter API v1.1
            endpoint this method uses has been deprecated, and they will stop
            being delivered beginning October 29, 2022.: https://twittercommunity.com/t/deprecation-announcement-removing-compliance-messages-from-statuses-filter-and-retiring-statuses-sample-from-the-twitter-api-v1-1/170500
        """
        if self.running:
            raise TweepyException("Stream is already connected")

        method = "POST"
        endpoint = "statuses/filter"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        body = {}
        if follow:
            body["follow"] = ','.join(map(str, follow))
        if track:
            body["track"] = ','.join(map(str, track))
        if locations and len(locations) > 0:
            if len(locations) % 4:
                raise TweepyException(
                    "Number of location coordinates should be a multiple of 4"
                )
            body["locations"] = ','.join(f"{l:.4f}" for l in locations)
        if filter_level:
            body["filter_level"] = filter_level
        if languages:
            body["language"] = ','.join(map(str, languages))
        if stall_warnings:
            body["stall_warnings"] = stall_warnings

        if threaded:
            return self._threaded_connect(method, endpoint, headers=headers,
                                          body=body)
        else:
            self._connect(method, endpoint, headers=headers, body=body)

    def sample(self, *, languages=None, stall_warnings=False, threaded=False):
        """Sample realtime Tweets

        .. deprecated:: 4.9
            `The Twitter API v1.1 endpoint this method uses is now deprecated
            and will be retired on October 29, 2022.`_ Twitter API v2 can be
            used instead with :meth:`StreamingClient.sample`.

        Parameters
        ----------
        languages : list[str] | None
            Setting this parameter to a comma-separated list of `BCP 47`_
            language identifiers corresponding to any of the languages listed
            on Twitter’s `advanced search`_ page will only return Tweets that
            have been detected as being written in the specified languages. For
            example, connecting with language=en will only stream Tweets
            detected to be in the English language.
        stall_warnings : bool
            Specifies whether stall warnings should be delivered
        threaded : bool
            Whether or not to use a thread to run the stream

        Raises
        ------
        TweepyException
            When the stream is already connected

        Returns
        -------
        threading.Thread | None
            The thread if ``threaded`` is set to ``True``, else ``None``

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/tweets/sample-realtime/api-reference/get-statuses-sample

        .. _BCP 47: https://tools.ietf.org/html/bcp47
        .. _advanced search: https://twitter.com/search-advanced
        .. _The Twitter API v1.1 endpoint this method uses is now deprecated
            and will be retired on October 29, 2022.: https://twittercommunity.com/t/deprecation-announcement-removing-compliance-messages-from-statuses-filter-and-retiring-statuses-sample-from-the-twitter-api-v1-1/170500
        """
        if self.running:
            raise TweepyException("Stream is already connected")

        method = "GET"
        endpoint = "statuses/sample"

        params = {}
        if languages:
            params["language"] = ','.join(map(str, languages))
        if stall_warnings:
            params["stall_warnings"] = "true"

        if threaded:
            return self._threaded_connect(method, endpoint, params=params)
        else:
            self._connect(method, endpoint, params=params)

    def on_data(self, raw_data):
        """This is called when raw data is received from the stream.
        This method handles sending the data to other methods based on the
        message type.

        Parameters
        ----------
        raw_data : JSON
            The raw data from the stream

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/tweets/filter-realtime/guides/streaming-message-types
        """
        data = json.loads(raw_data)

        if "in_reply_to_status_id" in data:
            status = Status.parse(None, data)
            return self.on_status(status)
        if "delete" in data:
            delete = data["delete"]["status"]
            return self.on_delete(delete["id"], delete["user_id"])
        if "disconnect" in data:
            return self.on_disconnect_message(data["disconnect"])
        if "limit" in data:
            return self.on_limit(data["limit"]["track"])
        if "scrub_geo" in data:
            return self.on_scrub_geo(data["scrub_geo"])
        if "status_withheld" in data:
            return self.on_status_withheld(data["status_withheld"])
        if "user_withheld" in data:
            return self.on_user_withheld(data["user_withheld"])
        if "warning" in data:
            return self.on_warning(data["warning"])

        log.error("Received unknown message type: %s", raw_data)

    def on_status(self, status):
        """This is called when a status is received.

        Parameters
        ----------
        status : Status
            The Status received
        """
        log.debug("Received status: %d", status.id)

    def on_delete(self, status_id, user_id):
        """This is called when a status deletion notice is received.

        Parameters
        ----------
        status_id : int
            The ID of the deleted Tweet
        user_id : int
            The ID of the author of the Tweet
        """
        log.debug("Received status deletion notice: %d", status_id)

    def on_disconnect_message(self, message):
        """This is called when a disconnect message is received.

        Parameters
        ----------
        message : JSON
            The disconnect message
        """
        log.warning("Received disconnect message: %s", message)

    def on_limit(self, track):
        """This is called when a limit notice is received.

        Parameters
        ----------
        track : int
            Total count of the number of undelivered Tweets since the
            connection was opened
        """
        log.debug("Received limit notice: %d", track)

    def on_scrub_geo(self, notice):
        """This is called when a location deletion notice is received.

        Parameters
        ----------
        notice : JSON
            The location deletion notice
        """
        log.debug("Received location deletion notice: %s", notice)

    def on_status_withheld(self, notice):
        """This is called when a status withheld content notice is received.

        Parameters
        ----------
        notice : JSON
            The status withheld content notice
        """
        log.debug("Received status withheld content notice: %s", notice)

    def on_user_withheld(self, notice):
        """This is called when a user withheld content notice is received.

        Parameters
        ----------
        notice : JSON
            The user withheld content notice
        """
        log.debug("Received user withheld content notice: %s", notice)

    def on_warning(self, warning):
        """This is called when a stall warning message is received.

        Parameters
        ----------
        warning : JSON
            The stall warning
        """
        log.warning("Received stall warning: %s", warning)


class StreamingClient(BaseClient, BaseStream):
    """Filter and sample realtime Tweets with Twitter API v2

    .. versionadded:: 4.6

    Parameters
    ----------
    bearer_token : str
        Twitter API Bearer Token
    return_type : type[dict | requests.Response | Response]
        Type to return from requests to the API
    wait_on_rate_limit : bool
        Whether to wait when rate limit is reached
    chunk_size : int
        The default socket.read size. Default to 512, less than half the size
        of a Tweet so that it reads Tweets with the minimal latency of 2 reads
        per Tweet. Values higher than ~1kb will increase latency by waiting for
        more data to arrive but may also increase throughput by doing fewer
        socket read calls.
    daemon : bool
        Whether or not to use a daemon thread when using a thread to run the
        stream
    max_retries : int
        Max number of times to retry connecting the stream
    proxy : str | None
        URL of the proxy to use when connecting to the stream
    verify : bool | str
        Either a boolean, in which case it controls whether to verify the
        server’s TLS certificate, or a string, in which case it must be a path
        to a CA bundle to use.

    Attributes
    ----------
    running : bool
        Whether there's currently a stream running
    session : :class:`requests.Session`
        Requests Session used to connect to the stream
    thread : :class:`threading.Thread` | None
        Thread used to run the stream
    user_agent : str
        User agent used when connecting to the stream
    """

    def __init__(self, bearer_token, *, return_type=Response,
                 wait_on_rate_limit=False, **kwargs):
        """__init__( \
            bearer_token, *, return_type=Response, wait_on_rate_limit=False, \
            chunk_size=512, daemon=False, max_retries=inf, proxy=None, \
            verify=True \
        )
        """
        BaseClient.__init__(self, bearer_token, return_type=return_type,
                            wait_on_rate_limit=wait_on_rate_limit)
        BaseStream.__init__(self, **kwargs)

    def _connect(self, method, endpoint, **kwargs):
        self.session.headers["Authorization"] = f"Bearer {self.bearer_token}"
        url = f"https://api.twitter.com/2/tweets/{endpoint}/stream"
        super()._connect(method, url, **kwargs)

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
            super()._process_data(data, data_type=data_type)

    def add_rules(self, add, **params):
        """add_rules(add, *, dry_run)

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

        return self._make_request(
            "POST", f"/2/tweets/search/stream/rules", params=params,
            endpoint_parameters=("dry_run",), json=json, data_type=StreamRule
        )

    def delete_rules(self, ids, **params):
        """delete_rules(ids, *, dry_run)

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

        return self._make_request(
            "POST", f"/2/tweets/search/stream/rules", params=params,
            endpoint_parameters=("dry_run",), json=json, data_type=StreamRule
        )

    def filter(self, *, threaded=False, **params):
        """filter( \
            *, backfill_minutes=None, expansions=None, media_fields=None, \
            place_fields=None, poll_fields=None, tweet_fields=None, \
            user_fields=None, threaded=False \
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
        threaded : bool
            Whether or not to use a thread to run the stream

        Raises
        ------
        TweepyException
            When the stream is already connected

        Returns
        -------
        threading.Thread | None
            The thread if ``threaded`` is set to ``True``, else ``None``

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/api-reference/get-tweets-search-stream

        .. _filter redundant connections: https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/integrate/recovery-and-redundancy-features
        .. _Tweet cap: https://developer.twitter.com/en/docs/twitter-api/tweet-caps
        """
        if self.running:
            raise TweepyException("Stream is already connected")

        method = "GET"
        endpoint = "search"

        params = self._process_params(
            params, endpoint_parameters=(
                "backfill_minutes", "expansions", "media.fields",
                "place.fields", "poll.fields", "tweet.fields", "user.fields"
            )
        )

        if threaded:
            return self._threaded_connect(method, endpoint, params=params)
        else:
            self._connect(method, endpoint, params=params)

    def get_rules(self, **params):
        """get_rules(*, ids)

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
        return self._make_request(
            "GET", f"/2/tweets/search/stream/rules", params=params,
            endpoint_parameters=("ids",), data_type=StreamRule
        )

    def sample(self, *, threaded=False, **params):
        """sample( \
            *, backfill_minutes=None, expansions=None, media_fields=None, \
            place_fields=None, poll_fields=None, tweet_fields=None, \
            user_fields=None, threaded=False \
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
        threaded : bool
            Whether or not to use a thread to run the stream

        Raises
        ------
        TweepyException
            When the stream is already connected

        Returns
        -------
        threading.Thread | None
            The thread if ``threaded`` is set to ``True``, else ``None``

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/volume-streams/api-reference/get-tweets-sample-stream

        .. _sample redundant connections: https://developer.twitter.com/en/docs/twitter-api/tweets/volume-streams/integrate/recovery-and-redundancy-features
        """
        if self.running:
            raise TweepyException("Stream is already connected")

        method = "GET"
        endpoint = "sample"

        params = self._process_params(
            params, endpoint_parameters=(
                "backfill_minutes", "expansions", "media.fields",
                "place.fields", "poll.fields", "tweet.fields", "user.fields"
            )
        )

        if threaded:
            return self._threaded_connect(method, endpoint, params=params)
        else:
            self._connect(method, endpoint, params=params)

    def on_data(self, raw_data):
        """This is called when raw data is received from the stream.
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
            self.on_tweet(tweet)
        if "includes" in data:
            includes = self._process_includes(data["includes"])
            self.on_includes(includes)
        if "errors" in data:
            errors = data["errors"]
            self.on_errors(errors)
        if "matching_rules" in data:
            matching_rules = [
                StreamRule(id=rule["id"], tag=rule["tag"])
                for rule in data["matching_rules"]
            ]
            self.on_matching_rules(matching_rules)

        self.on_response(
            StreamResponse(tweet, includes, errors, matching_rules)
        )

    def on_tweet(self, tweet):
        """This is called when a Tweet is received.

        Parameters
        ----------
        tweet : Tweet
            The Tweet received
        """
        pass

    def on_includes(self, includes):
        """This is called when includes are received.

        Parameters
        ----------
        includes : dict
            The includes received
        """
        pass

    def on_errors(self, errors):
        """This is called when errors are received.

        Parameters
        ----------
        errors : dict
            The errors received
        """
        log.error("Received errors: %s", errors)

    def on_matching_rules(self, matching_rules):
        """This is called when matching rules are received.

        Parameters
        ----------
        matching_rules : list[StreamRule]
            The matching rules received
        """
        pass

    def on_response(self, response):
        """This is called when a response is received.

        Parameters
        ----------
        response : StreamResponse
            The response received
        """
        log.debug("Received response: %s", response)


class StreamRule(NamedTuple):
    """Rule for filtered stream

    .. versionadded:: 4.6

    Parameters
    ----------
    value : str | None
        The rule text. If you are using a `Standard Project`_ at the Basic
        `access level`_, you can use the basic set of `operators`_, can submit
        up to 25 concurrent rules, and can submit rules up to 512 characters
        long. If you are using an `Academic Research Project`_ at the Basic
        access level, you can use all available operators, can submit up to
        1,000 concurrent rules, and can submit rules up to 1,024 characters
        long.
    tag : str | None
        The tag label. This is a free-form text you can use to identify the
        rules that matched a specific Tweet in the streaming response. Tags can
        be the same across rules.
    id : str | None
        Unique identifier of this rule. This is returned as a string.


    .. _Standard Project: https://developer.twitter.com/en/docs/projects
    .. _access level: https://developer.twitter.com/en/products/twitter-api/early-access/guide#na_1
    .. _operators: https://developer.twitter.com/en/docs/twitter-api/tweets/search/integrate/build-a-query
    .. _Academic Research Project: https://developer.twitter.com/en/docs/projects
    """
    value: str = None
    tag: str = None
    id: str = None
