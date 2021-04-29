# Tweepy
# Copyright 2009-2021 Joshua Roesslein
# See LICENSE for details.

# Appengine users: https://developers.google.com/appengine/docs/python/sockets/#making_httplib_use_sockets

import json
import logging
from math import inf
from platform import python_version
import ssl
from threading import Thread
from time import sleep

import requests
from requests_oauthlib import OAuth1
import urllib3

import tweepy
from tweepy.errors import TweepyException
from tweepy.models import Status

log = logging.getLogger(__name__)


class Stream:
    """Filter and sample realtime Tweets

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
    proxy : Optional[str]
        URL of the proxy to use when connecting to the stream
    verify : Union[bool, str]
        Either a boolean, in which case it controls whether to verify the
        server’s TLS certificate, or a string, in which case it must be a path
        to a CA bundle to use.

    Attributes
    ----------
    running : bool
        Whether there's currently a stream running
    session : Optional[:class:`requests.Session`]
        Requests Session used to connect to the stream
    thread : Optional[:class:`threading.Thread`]
        Thread used to run the stream
    user_agent : str
        User agent used when connecting to the stream
    """

    def __init__(self, consumer_key, consumer_secret, access_token,
                 access_token_secret, *, chunk_size=512, daemon=False,
                 max_retries=inf, proxy=None, verify=True):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.chunk_size = chunk_size
        self.daemon = daemon
        self.max_retries = max_retries
        self.proxies = {"https": proxy} if proxy else {}
        self.verify = verify

        self.running = False
        self.session = None
        self.thread = None
        self.user_agent = (
            f"Python/{python_version()} "
            f"Requests/{requests.__version__} "
            f"Tweepy/{tweepy.__version__}"
        )

    def _connect(self, method, endpoint, params=None, headers=None, body=None):
        self.running = True

        error_count = 0
        # https://developer.twitter.com/en/docs/twitter-api/v1/tweets/filter-realtime/guides/connecting
        stall_timeout = 90
        network_error_wait = network_error_wait_step = 0.25
        network_error_wait_max = 16
        http_error_wait = http_error_wait_start = 5
        http_error_wait_max = 320
        http_420_error_wait_start = 60

        auth = OAuth1(self.consumer_key, self.consumer_secret,
                      self.access_token, self.access_token_secret)

        if self.session is None:
            self.session = requests.Session()
            self.session.headers["User-Agent"] = self.user_agent

        url = f"https://stream.twitter.com/1.1/{endpoint}.json"

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

    def filter(self, *, follow=None, track=None, locations=None,
               filter_level=None, languages=None, stall_warnings=False,
               threaded=False):
        """Filter realtime Tweets

        Parameters
        ----------
        follow : Optional[List[Union[int, str]]]
            User IDs, indicating the users to return statuses for in the stream
        track : Optional[List[str]]
            Keywords to track
        locations : Optional[List[float]]
            Specifies a set of bounding boxes to track
        filter_level : Optional[str]
            Setting this parameter to one of none, low, or medium will set the
            minimum value of the filter_level Tweet attribute required to be
            included in the stream. The default value is none, which includes
            all available Tweets.

            When displaying a stream of Tweets to end users (dashboards or live
            feeds at a presentation or conference, for example) it is suggested
            that you set this value to medium.
        languages : Optional[List[str]]
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
            When number of location coordinates is not a multiple of 4

        Returns
        -------
        Optional[threading.Thread]
            The thread if ``threaded`` is set to ``True``, else ``None``

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/tweets/filter-realtime/api-reference/post-statuses-filter

        .. _BCP 47: https://tools.ietf.org/html/bcp47
        .. _advanced search: https://twitter.com/search-advanced
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

        Parameters
        ----------
        languages : Optional[List[str]]
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

        Returns
        -------
        Optional[threading.Thread]
            The thread if ``threaded`` is set to ``True``, else ``None``

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/tweets/sample-realtime/api-reference/get-statuses-sample

        .. _BCP 47: https://tools.ietf.org/html/bcp47
        .. _advanced search: https://twitter.com/search-advanced
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
