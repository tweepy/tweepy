# Tweepy
# Copyright 2009-2021 Joshua Roesslein
# See LICENSE for details.

import asyncio
import json
import logging
from math import inf
from platform import python_version

import aiohttp
from oauthlib.oauth1 import Client as OAuthClient
from yarl import URL

import tweepy
from tweepy.errors import TweepyException
from tweepy.models import Status

log = logging.getLogger(__name__)


class AsyncStream:
    """Stream realtime Tweets asynchronously

    Parameters
    ----------
    consumer_key: str
        Twitter API Consumer Key
    consumer_secret: str
        Twitter API Consumer Secret
    access_token: str
        Twitter API Access Token
    access_token_secret: str
        Twitter API Access Token Secret
    max_retries: Optional[int]
        Number of times to attempt to (re)connect the stream.
    proxy: Optional[str]
        Proxy URL

    Attributes
    ----------
    session : Optional[aiohttp.ClientSession]
        Aiohttp client session used to connect to the API
    task : Optional[asyncio.Task]
        The task running the stream
    user_agent : str
        User agent used when connecting to the API
    """

    def __init__(self, consumer_key, consumer_secret, access_token,
                 access_token_secret, *, max_retries=inf, proxy=None):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.max_retries = max_retries
        self.proxy = proxy

        self.session = None
        self.task = None
        self.user_agent = (
            f"Python/{python_version()} "
            f"aiohttp/{aiohttp.__version__} "
            f"Tweepy/{tweepy.__version__}"
        )

    async def _connect(self, method, endpoint, params={}, headers=None,
                       body=None):
        error_count = 0
        # https://developer.twitter.com/en/docs/twitter-api/v1/tweets/filter-realtime/guides/connecting
        stall_timeout = 90
        network_error_wait = network_error_wait_step = 0.25
        network_error_wait_max = 16
        http_error_wait = http_error_wait_start = 5
        http_error_wait_max = 320
        http_420_error_wait_start = 60

        oauth_client = OAuthClient(self.consumer_key, self.consumer_secret,
                                   self.access_token, self.access_token_secret)

        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={"User-Agent": self.user_agent},
                timeout=aiohttp.ClientTimeout(sock_read=stall_timeout)
            )

        url = f"https://stream.twitter.com/1.1/{endpoint}.json"
        url = str(URL(url).with_query(sorted(params.items())))

        try:
            while error_count <= self.max_retries:
                request_url, request_headers, request_body = oauth_client.sign(
                    url, method, body, headers
                )
                try:
                    async with self.session.request(
                        method, request_url, headers=request_headers,
                        data=request_body, proxy=self.proxy
                    ) as resp:
                        if resp.status == 200:
                            error_count = 0
                            http_error_wait = http_error_wait_start
                            network_error_wait = network_error_wait_step

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

                            error_count += 1

                            if resp.status == 420:
                                if http_error_wait < http_420_error_wait_start:
                                    http_error_wait = http_420_error_wait_start

                            await asyncio.sleep(http_error_wait)

                            http_error_wait *= 2
                            if resp.status != 420:
                                if http_error_wait > http_error_wait_max:
                                    http_error_wait = http_error_wait_max
                except (aiohttp.ClientConnectionError,
                        aiohttp.ClientPayloadError) as e:
                    await self.on_connection_error()

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

    def filter(self, *, follow=None, track=None, locations=None,
               filter_level=None, languages=None, stall_warnings=False):
        """Filter realtime Tweets

        Parameters
        ----------
        follow: Optional[List[Union[int, str]]]
            A list of user IDs, indicating the users to return statuses for in
            the stream. See https://developer.twitter.com/en/docs/twitter-api/v1/tweets/filter-realtime/guides/basic-stream-parameters
            for more information.
        track: Optional[List[str]]
            Keywords to track. Phrases of keywords are specified by a list. See
            https://developer.twitter.com/en/docs/tweets/filter-realtime/guides/basic-stream-parameters
            for more information.
        locations: Optional[List[float]]
            Specifies a set of bounding boxes to track. See
            https://developer.twitter.com/en/docs/tweets/filter-realtime/guides/basic-stream-parameters
            for more information.
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
        stall_warnings: Optional[bool]
            Specifies whether stall warnings should be delivered. See
            https://developer.twitter.com/en/docs/tweets/filter-realtime/guides/basic-stream-parameters
            for more information.

        Raises
        ------
        TweepyException
            When the stream is already connected or when the number of location
            coordinates is not a multiple of 4

        Returns
        -------
        asyncio.Task
            The task running the stream

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/v1/tweets/filter-realtime/api-reference/post-statuses-filter

        .. _BCP 47: https://tools.ietf.org/html/bcp47
        .. _advanced search: https://twitter.com/search-advanced
        """
        if self.task is not None and not self.task.done():
            raise TweepyException("Stream is already connected")

        endpoint = "statuses/filter"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        body = {}
        if follow is not None:
            body["follow"] = ','.join(map(str, follow))
        if track is not None:
            body["track"] = ','.join(map(str, track))
        if locations is not None:
            if len(locations) % 4:
                raise TweepyException(
                    "Number of location coordinates should be a multiple of 4"
                )
            body["locations"] = ','.join(
                f"{location:.4f}" for location in locations
            )
        if filter_level is not None:
            body["filter_level"] = filter_level
        if languages is not None:
            body["language"] = ','.join(map(str, languages))
        if stall_warnings:
            body["stall_warnings"] = "true"

        self.task = asyncio.ensure_future(
            self._connect("POST", endpoint, headers=headers, body=body or None)
        )
        # Use create_task when support for Python 3.6 is dropped
        return self.task

    def sample(self, *, languages=None, stall_warnings=False):
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
        stall_warnings: Optional[bool]
            Specifies whether stall warnings should be delivered. See
            https://developer.twitter.com/en/docs/tweets/filter-realtime/guides/basic-stream-parameters
            for more information.

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
        https://developer.twitter.com/en/docs/twitter-api/v1/tweets/sample-realtime/api-reference/get-statuses-sample

        .. _BCP 47: https://tools.ietf.org/html/bcp47
        .. _advanced search: https://twitter.com/search-advanced
        """
        if self.task is not None and not self.task.done():
            raise TweepyException("Stream is already connected")

        endpoint = "statuses/sample"

        params = {}
        if languages is not None:
            params["language"] = ','.join(map(str, languages))
        if stall_warnings:
            params["stall_warnings"] = "true"

        self.task = asyncio.ensure_future(
            self._connect("GET", endpoint, params=params)
        )
        # Use create_task when support for Python 3.6 is dropped
        return self.task

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

    async def on_data(self, raw_data):
        """|coroutine|

        This is called when raw data is received from the stream.
        This method handles sending the data to other methods, depending on the
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
            return await self.on_status(status)
        if "delete" in data:
            delete = data["delete"]["status"]
            return await self.on_delete(delete["id"], delete["user_id"])
        if "disconnect" in data:
            return await self.on_disconnect_message(data["disconnect"])
        if "limit" in data:
            return await self.on_limit(data["limit"]["track"])
        if "scrub_geo" in data:
            return await self.on_scrub_geo(data["scrub_geo"])
        if "status_withheld" in data:
            return await self.on_status_withheld(data["status_withheld"])
        if "user_withheld" in data:
            return await self.on_user_withheld(data["user_withheld"])
        if "warning" in data:
            return await self.on_warning(data["warning"])

        log.warning("Received unknown message type: %s", raw_data)

    async def on_status(self, status):
        """|coroutine|

        This is called when a status is received.

        Parameters
        ----------
        status : Status
            The Status received
        """
        log.debug("Received status: %d", status.id)

    async def on_delete(self, status_id, user_id):
        """|coroutine|

        This is called when a status deletion notice is received.

        Parameters
        ----------
        status_id : int
            The ID of the deleted Tweet
        user_id : int
            The ID of the author of the Tweet
        """
        log.debug("Received status deletion notice: %d", status_id)

    async def on_disconnect_message(self, message):
        """|coroutine|

        This is called when a disconnect message is received.

        Parameters
        ----------
        message : JSON
            The disconnect message
        """
        log.warning("Received disconnect message: %s", message)

    async def on_limit(self, track):
        """|coroutine|

        This is called when a limit notice is received.

        Parameters
        ----------
        track : int
            Total count of the number of undelivered Tweets since the
            connection was opened
        """
        log.debug("Received limit notice: %d", track)

    async def on_scrub_geo(self, notice):
        """|coroutine|

        This is called when a location deletion notice is received.

        Parameters
        ----------
        notice : JSON
            The location deletion notice
        """
        log.debug("Received location deletion notice: %s", notice)

    async def on_status_withheld(self, notice):
        """|coroutine|

        This is called when a status withheld content notice is received.

        Parameters
        ----------
        notice : JSON
            The status withheld content notice
        """
        log.debug("Received status withheld content notice: %s", notice)

    async def on_user_withheld(self, notice):
        """|coroutine|

        This is called when a user withheld content notice is received.

        Parameters
        ----------
        notice : JSON
            The user withheld content notice
        """
        log.debug("Received user withheld content notice: %s", notice)

    async def on_warning(self, notice):
        """|coroutine|

        This is called when a stall warning message is received.

        Parameters
        ----------
        warning : JSON
            The stall warning
        """
        log.warning("Received stall warning: %s", notice)
