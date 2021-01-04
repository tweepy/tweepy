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
from tweepy.error import TweepError
from tweepy.models import Status

log = logging.getLogger(__name__)


class AsyncStream:
    """Stream realtime Tweets asynchronously

    Parameters
    ----------
    consumer_key: :class:`str`
        Consumer key
    consumer_secret: :class:`str`
        Consuemr secret
    access_token: :class:`str`
        Access token
    access_token_secret: :class:`str`
        Access token secret
    max_retry: Optional[:class:`int`]
        Number of times to attempt to (re)connect the stream.
        Defaults to infinite.
    proxy: Optional[:class:`str`]
        Proxy URL
    """

    def __init__(self, consumer_key, consumer_secret, access_token,
                 access_token_secret, max_retry=inf, proxy=None):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.max_retry = max_retry
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
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={"User-Agent": self.user_agent},
                # Override default 5 min. total timeout
                timeout=aiohttp.ClientTimeout()
            )

        url = f"https://stream.twitter.com/1.1/{endpoint}.json"
        url = str(URL(url).with_query(sorted(params.items())))

        oauth_client = OAuthClient(self.consumer_key, self.consumer_secret,
                                   self.access_token, self.access_token_secret)

        error_count = 0
        # https://developer.twitter.com/en/docs/twitter-api/v1/tweets/filter-realtime/guides/connecting
        stall_timeout = 90
        network_error_wait = network_error_step = 0.25
        network_error_max = 16
        http_error_wait = http_error_start = 5
        http_error_max = 320
        http_420_error_start = 60

        try:
            while error_count <= self.max_retry:
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
                            http_error_wait = http_error_start
                            network_error_wait = network_error_step

                            await self.on_connect()

                            while not resp.content.at_eof():
                                line = await asyncio.wait_for(
                                    resp.content.readline(),
                                    timeout=stall_timeout
                                )
                                line = line.strip()
                                if line:
                                    await self.on_data(line)
                                else:
                                    await self.on_keep_alive()

                            await self.on_closed(resp)
                        else:
                            await self.on_http_error(resp.status)

                            error_count += 1

                            if resp.status == 420:
                                if http_error_wait < http_420_error_start:
                                    http_error_wait = http_420_error_start

                            await asyncio.sleep(http_error_wait)

                            http_error_wait *= 2
                            if resp.status != 420:
                                if http_error_wait > http_error_max:
                                    http_error_wait = http_error_max
                except (aiohttp.ClientConnectionError,
                        aiohttp.ClientPayloadError,
                        asyncio.TimeoutError) as e:
                    await self.on_connection_error()

                    await asyncio.sleep(network_error_wait)

                    network_error_wait += network_error_step
                    if network_error_wait > network_error_max:
                        network_error_wait = network_error_max
        except asyncio.CancelledError:
            return
        except Exception as e:
            await self.on_exception(e)
            raise
        finally:
            await self.session.close()

    async def filter(self, follow=None, track=None, locations=None,
                     stall_warnings=False):
        """This method is a coroutine.

        Filter realtime Tweets
        https://developer.twitter.com/en/docs/twitter-api/v1/tweets/filter-realtime/api-reference/post-statuses-filter

        Parameters
        ----------
        follow: Optional[List[Union[:class:`int`, :class:`str`]]]
            A list of user IDs, indicating the users to return statuses for in
            the stream. See https://developer.twitter.com/en/docs/twitter-api/v1/tweets/filter-realtime/guides/basic-stream-parameters
            for more information.
        track: Optional[List[:class:`str`]]
            Keywords to track. Phrases of keywords are specified by a list. See
            https://developer.twitter.com/en/docs/tweets/filter-realtime/guides/basic-stream-parameters
            for more information.
        locations: Optional[List[:class:`float`]]
            Specifies a set of bounding boxes to track. See
            https://developer.twitter.com/en/docs/tweets/filter-realtime/guides/basic-stream-parameters
            for more information.
        stall_warnings: Optional[:class:`bool`]
            Specifies whether stall warnings should be delivered. See
            https://developer.twitter.com/en/docs/tweets/filter-realtime/guides/basic-stream-parameters
            for more information. Defaults to False.

        Returns :class:`asyncio.Task`
        """
        if self.task is not None:
            raise TweepError('Stream is already connected')

        endpoint = "statuses/filter"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        body = {}
        if follow is not None:
            body["follow"] = ','.join(map(str, follow))
        if track is not None:
            body["track"] = ','.join(map(str, track))
        if locations is not None:
            if len(locations) % 4:
                raise TweepError(
                    "Number of location coordinates should be a multiple of 4"
                )
            body["locations"] = ','.join(
                f"{location:.4f}" for location in locations
            )
        if stall_warnings:
            body["stall_warnings"] = "true"

        self.task = await asyncio.create_task(
            self._connect("POST", endpoint, headers=headers, body=body or None)
        )
        return self.task

    async def sample(self, stall_warnings=False):
        """This method is a coroutine.

        Sample realtime Tweets
        https://developer.twitter.com/en/docs/twitter-api/v1/tweets/sample-realtime/api-reference/get-statuses-sample

        Parameters
        ----------
        stall_warnings: Optional[:class:`bool`]
            Specifies whether stall warnings should be delivered. See
            https://developer.twitter.com/en/docs/tweets/filter-realtime/guides/basic-stream-parameters
            for more information. Defaults to False.

        Returns :class:`asyncio.Task`
        """
        if self.task is not None:
            raise TweepError("Stream is already connected")

        endpoint = "statuses/sample"

        params = {}
        if stall_warnings:
            params["stall_warnings"] = "true"

        self.task = await asyncio.create_task(
            self._connect("GET", endpoint, params=params)
        )
        return self.task

    def disconnect(self):
        """Disconnect the stream"""
        if self.task is not None:
            self.task.cancel()

    async def on_closed(self, resp):
        """This method is a coroutine.

        This is called when the stream has been closed by Twitter.
        """
        log.error("Stream connection closed by Twitter")

    async def on_connect(self):
        """This method is a coroutine.

        This is called after successfully coneccting to the streaming API.
        """
        log.info("Stream connected")

    async def on_connection_error(self):
        """This method is a coroutine.

        This is called when the stream connection errors or times out.
        """
        log.error("Stream connection has errored or timed out")

    async def on_exception(self, exception):
        """This method is a coroutine.

        This is called when an unhandled exception occurs.
        """
        log.exception("Stream encountered an exception")

    async def on_http_error(self, status_code):
        """This method is a coroutine.

        This is called when a non-200 HTTP status code is encountered.
        """
        log.error(f"Stream encountered HTTP Error: {status_code}")

    async def on_keep_alive(self):
        """This method is a coroutine.

        This is called when a keep-alive message is received.
        """
        log.debug("Received keep-alive message")

    async def on_data(self, raw_data):
        """This method is a coroutine.

        This is called when raw data is received from the stream.
        This method handles sending the data to other methods, depending on the
        message type.

        https://developer.twitter.com/en/docs/twitter-api/v1/tweets/filter-realtime/guides/streaming-message-types
        """
        data = json.loads(raw_data)

        if "in_reply_to_status_id" in data:
            status = Status.parse(None, data)
            return await self.on_status(status)
        if "delete" in data:
            delete = data["delete"]["status"]
            return await self.on_delete(delete["id"], delete["user_id"])
        if "limit" in data:
            return await self.on_limit(data["limit"]["track"])
        for message_type in ("disconnect", "scrub_geo", "status_withheld",
                             "user_withheld", "warning"):
            if message_type in data:
                method = getattr(self, "on_" + message_type)
                return await method(data[message_type])

        log.warning(f"Received unknown message type: {raw_data}")

    async def on_status(self, status):
        """This method is a coroutine.

        This is called when a status is received.
        """
        log.debug(f"Received status: {status.id}")

    async def on_delete(self, status_id, user_id):
        """This method is a coroutine.

        This is called when a status deletion notice is received.
        """
        log.debug(f"Received status deletion notice: {status_id}")

    async def on_disconnect(self, notice):
        """This method is a coroutine.

        This is called when a disconnect notice is received.
        """
        log.warning(f"Received disconnect message: {notice}")

    async def on_limit(self, track):
        """This method is a coroutine.

        This is called when a limit notice is received.
        """
        log.debug(f"Received limit notice: {track}")

    async def on_scrub_geo(self, notice):
        """This method is a coroutine.

        This is called when a location deletion notice is received.
        """
        log.debug(f"Received location deletion notice: {notice}")

    async def on_status_withheld(self, notice):
        """This method is a coroutine.

        This is called when a status withheld content notice is received.
        """
        log.debug(f"Received status withheld content notice: {notice}")

    async def on_user_withheld(self, notice):
        """This method is a coroutine.

        This is called when a user withheld content notice is received.
        """
        log.debug(f"Received user withheld content notice: {notice}")

    async def on_warning(self, notice):
        """This method is a coroutine.

        This is called when a stall warning message is received.
        """
        log.warning(f"Received stall warning: {notice}")
