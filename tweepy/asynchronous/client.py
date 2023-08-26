# Tweepy
# Copyright 2009-2023 Joshua Roesslein
# See LICENSE for details.

try:
    from functools import cache
except ImportError:  # Remove when support for Python 3.8 is dropped
    from functools import lru_cache
    cache = lru_cache(maxsize=None)

import asyncio
import logging
from platform import python_version
import time

import aiohttp
from async_lru import alru_cache
from oauthlib.oauth1 import Client as OAuthClient
from yarl import URL

import tweepy
from tweepy.client import BaseClient, Response
from tweepy.direct_message_event import DirectMessageEvent
from tweepy.errors import (
    BadRequest, Forbidden, HTTPException, NotFound, TooManyRequests,
    TwitterServerError, Unauthorized
)
from tweepy.list import List
from tweepy.space import Space
from tweepy.tweet import Tweet
from tweepy.user import User

async_cache = alru_cache(maxsize=None)

log = logging.getLogger(__name__)


class AsyncBaseClient(BaseClient):

    def __init__(
        self, bearer_token=None, consumer_key=None, consumer_secret=None,
        access_token=None, access_token_secret=None, *, return_type=Response,
        wait_on_rate_limit=False
    ):
        self.bearer_token = bearer_token
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret

        self.return_type = return_type
        self.wait_on_rate_limit = wait_on_rate_limit

        self.session = None
        self.user_agent = (
            f"Python/{python_version()} "
            f"aiohttp/{aiohttp.__version__} "
            f"Tweepy/{tweepy.__version__}"
        )

    async def request(
        self, method, route, params=None, json=None, user_auth=False
    ):
        session = self.session or aiohttp.ClientSession()
        url = "https://api.twitter.com" + route
        headers = {"User-Agent": self.user_agent}
        if json is not None:
            headers["Content-Type"] = "application/json"

        if user_auth:
            oauth_client = OAuthClient(
                self.consumer_key, self.consumer_secret,
                self.access_token, self.access_token_secret
            )
            url = str(URL(url).with_query(sorted(params.items())))
            url, headers, body = oauth_client.sign(
                url, method, headers=headers
            )
            # oauthlib.oauth1.Client (OAuthClient) expects colons in query 
            # values (e.g. in timestamps) to be percent-encoded, while
            # aiohttp.ClientSession does not automatically encode them
            before_query, question_mark, query = url.partition('?')
            url = URL(
                f"{before_query}?{query.replace(':', '%3A')}",
                encoded = True
            )
            params = None
        else:
            headers["Authorization"] = f"Bearer {self.bearer_token}"

        log.debug(
            f"Making API request: {method} {url}\n"
            f"Parameters: {params}\n"
            f"Headers: {headers}\n"
            f"JSON: {json}"
        )

        async with session.request(
            method, url, params=params, json=json, headers=headers
        ) as response:
            await response.read()

        log.debug(
            f"Received API response: {response.status} {response.reason}\n"
            f"Headers: {response.headers}"
        )

        if self.session is None:
            await session.close()

        if not 200 <= response.status < 300:
            response_json = await response.json()
        if response.status == 400:
            raise BadRequest(response, response_json=response_json)
        if response.status == 401:
            raise Unauthorized(response, response_json=response_json)
        if response.status == 403:
            raise Forbidden(response, response_json=response_json)
        if response.status == 404:
            raise NotFound(response, response_json=response_json)
        if response.status == 429:
            if self.wait_on_rate_limit:
                reset_time = int(response.headers["x-rate-limit-reset"])
                sleep_time = reset_time - int(time.time()) + 1
                if sleep_time > 0:
                    log.warning(
                        "Rate limit exceeded. "
                        f"Sleeping for {sleep_time} seconds."
                    )
                    await asyncio.sleep(sleep_time)
                return await self.request(method, route, params, json, user_auth)
            else:
                raise TooManyRequests(response, response_json=response_json)
        if response.status >= 500:
            raise TwitterServerError(response, response_json=response_json)
        if not 200 <= response.status < 300:
            raise HTTPException(response, response_json=response_json)

        return response

    async def _make_request(
        self, method, route, params={}, endpoint_parameters=(), json=None,
        data_type=None, user_auth=False
    ):
        request_params = self._process_params(params, endpoint_parameters)

        response = await self.request(method, route, params=request_params,
                                      json=json, user_auth=user_auth)

        if self.return_type is aiohttp.ClientResponse:
            return response

        response = await response.json()

        if self.return_type is dict:
            return response

        return self._construct_response(response, data_type=data_type)


class AsyncClient(AsyncBaseClient):
    """AsyncClient( \
        bearer_token=None, consumer_key=None, consumer_secret=None, \
        access_token=None, access_token_secret=None, *, return_type=Response, \
        wait_on_rate_limit=False \
    )

    Asynchronous Twitter API v2 Client

    .. versionadded:: 4.10

    .. versionchanged:: 4.15
        Removed ``block`` and ``unblock`` methods, as the endpoints they use
        have been removed

    Parameters
    ----------
    bearer_token : str | None
        Twitter API OAuth 2.0 Bearer Token / Access Token
    consumer_key : str | None
        Twitter API OAuth 1.0a Consumer Key
    consumer_secret : str | None
        Twitter API OAuth 1.0a Consumer Secret
    access_token : str | None
        Twitter API OAuth 1.0a Access Token
    access_token_secret : str | None
        Twitter API OAuth 1.0a Access Token Secret
    return_type : type[dict | aiohttp.ClientResponse | Response]
        Type to return from requests to the API
    wait_on_rate_limit : bool
        Whether to wait when rate limit is reached

    Attributes
    ----------
    session : aiohttp.ClientSession
        Aiohttp client session used to make requests to the API
    user_agent : str
        User agent used when making requests to the API
    """

    async def _get_authenticating_user_id(self, *, oauth_1=False):
        if oauth_1:
            if self.access_token is None:
                raise TypeError(
                    "Access Token must be provided for OAuth 1.0a User Context"
                )
            else:
                return self._get_oauth_1_authenticating_user_id(
                    self.access_token
                )
        else:
            if self.bearer_token is None:
                raise TypeError(
                    "Access Token must be provided for "
                    "OAuth 2.0 Authorization Code Flow with PKCE"
                )
            else:
                return await self._get_oauth_2_authenticating_user_id(
                    self.bearer_token
                )

    @cache
    def _get_oauth_1_authenticating_user_id(self, access_token):
        return access_token.partition('-')[0]

    @async_cache
    async def _get_oauth_2_authenticating_user_id(self, access_token):
        original_access_token = self.bearer_token
        original_return_type = self.return_type

        self.bearer_token = access_token
        self.return_type = dict
        user_id = (await self.get_me(user_auth=False))["data"]["id"]

        self.bearer_token = original_access_token
        self.return_type = original_return_type

        return user_id

    # Bookmarks

    async def remove_bookmark(self, tweet_id):
        """Allows a user or authenticated user ID to remove a Bookmark of a
        Tweet.

        .. note::

            A request is made beforehand to Twitter's API to determine the
            authenticating user's ID. This is cached and only done once per
            :class:`AsyncClient` instance for each access token used.

        Parameters
        ----------
        tweet_id : int | str
            The ID of the Tweet that you would like the ``id`` to remove a
            Bookmark of.

        Raises
        ------
        TypeError
            If the access token isn't set

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/bookmarks/api-reference/delete-users-id-bookmarks-tweet_id
        """
        id = await self._get_authenticating_user_id()
        route = f"/2/users/{id}/bookmarks/{tweet_id}"

        return await self._make_request(
            "DELETE", route
        )

    async def get_bookmarks(self, **params):
        """get_bookmarks( \
            *, expansions=None, max_results=None, media_fields=None, \
            pagination_token=None, place_fields=None, poll_fields=None, \
            tweet_fields=None, user_fields=None \
        )

        Allows you to get an authenticated user's 800 most recent bookmarked
        Tweets.

        .. note::

            A request is made beforehand to Twitter's API to determine the
            authenticating user's ID. This is cached and only done once per
            :class:`AsyncClient` instance for each access token used.

        Parameters
        ----------
        expansions : list[str] | str | None
            :ref:`expansions_parameter`
        max_results : int | None
            The maximum number of results to be returned per page. This can be
            a number between 1 and 100. By default, each page will return 100
            results.
        media_fields : list[str] | str | None
            :ref:`media_fields_parameter`
        pagination_token : str | None
            Used to request the next page of results if all results weren't
            returned with the latest request, or to go back to the previous
            page of results. To return the next page, pass the ``next_token``
            returned in your previous response. To go back one page, pass the
            ``previous_token`` returned in your previous response.
        place_fields : list[str] | str | None
            :ref:`place_fields_parameter`
        poll_fields : list[str] | str | None
            :ref:`poll_fields_parameter`
        tweet_fields : list[str] | str | None
            :ref:`tweet_fields_parameter`
        user_fields : list[str] | str | None
            :ref:`user_fields_parameter`

        Raises
        ------
        TypeError
            If the access token isn't set

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/bookmarks/api-reference/get-users-id-bookmarks
        """
        id = await self._get_authenticating_user_id()
        route = f"/2/users/{id}/bookmarks"

        return await self._make_request(
            "GET", route, params=params,
            endpoint_parameters=(
                "expansions", "max_results", "media.fields",
                "pagination_token", "place.fields", "poll.fields",
                "tweet.fields", "user.fields"
            ), data_type=Tweet
        )

    async def bookmark(self, tweet_id):
        """Causes the authenticating user to Bookmark the target Tweet provided
        in the request body.

        .. note::

            A request is made beforehand to Twitter's API to determine the
            authenticating user's ID. This is cached and only done once per
            :class:`AsyncClient` instance for each access token used.

        Parameters
        ----------
        tweet_id : int | str
            The ID of the Tweet that you would like the user ``id`` to
            Bookmark.

        Raises
        ------
        TypeError
            If the access token isn't set

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/bookmarks/api-reference/post-users-id-bookmarks
        """
        id = await self._get_authenticating_user_id()
        route = f"/2/users/{id}/bookmarks"

        return await self._make_request(
            "POST", route, json={"tweet_id": str(tweet_id)}
        )

    # Hide replies

    async def hide_reply(self, id, *, user_auth=True):
        """Hides a reply to a Tweet.

        Parameters
        ----------
        id : int | str
            Unique identifier of the Tweet to hide. The Tweet must belong to a
            conversation initiated by the authenticating user.
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/hide-replies/api-reference/put-tweets-id-hidden
        """
        return await self._make_request(
            "PUT", f"/2/tweets/{id}/hidden", json={"hidden": True},
            user_auth=user_auth
        )

    async def unhide_reply(self, id, *, user_auth=True):
        """Unhides a reply to a Tweet.

        Parameters
        ----------
        id : int | str
            Unique identifier of the Tweet to unhide. The Tweet must belong to
            a conversation initiated by the authenticating user.
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/hide-replies/api-reference/put-tweets-id-hidden
        """
        return await self._make_request(
            "PUT", f"/2/tweets/{id}/hidden", json={"hidden": False},
            user_auth=user_auth
        )

    # Likes

    async def unlike(self, tweet_id, *, user_auth=True):
        """Unlike a Tweet.

        The request succeeds with no action when the user sends a request to a
        user they're not liking the Tweet or have already unliked the Tweet.

        .. note::

            When using OAuth 2.0 Authorization Code Flow with PKCE with
            ``user_auth=False``, a request is made beforehand to Twitter's API
            to determine the authenticating user's ID. This is cached and only
            done once per :class:`AsyncClient` instance for each access token
            used.

        Parameters
        ----------
        tweet_id : int | str
            The ID of the Tweet that you would like to unlike.
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Raises
        ------
        TypeError
            If the access token isn't set

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/likes/api-reference/delete-users-id-likes-tweet_id
        """
        id = await self._get_authenticating_user_id(oauth_1=user_auth)
        route = f"/2/users/{id}/likes/{tweet_id}"

        return await self._make_request(
            "DELETE", route, user_auth=user_auth
        )

    async def get_liking_users(self, id, *, user_auth=False, **params):
        """get_liking_users( \
            id, *, expansions=None, max_results=None, media_fields=None, \
            pagination_token=None, place_fields=None, poll_fields=None, \
            tweet_fields=None, user_fields=None, user_auth=False \
        )

        Allows you to get information about a Tweet’s liking users.

        Parameters
        ----------
        id : int | str
            Tweet ID of the Tweet to request liking users of.
        expansions : list[str] | str | None
            :ref:`expansions_parameter`
        max_results : int | None
            The maximum number of results to be returned per page. This can be
            a number between 1 and 100. By default, each page will return 100
            results.
        media_fields : list[str] | str | None
            :ref:`media_fields_parameter`
        pagination_token : str | None
            Used to request the next page of results if all results weren't
            returned with the latest request, or to go back to the previous
            page of results. To return the next page, pass the ``next_token``
            returned in your previous response. To go back one page, pass the
            ``previous_token`` returned in your previous response.
        place_fields : list[str] | str | None
            :ref:`place_fields_parameter`
        poll_fields : list[str] | str | None
            :ref:`poll_fields_parameter`
        tweet_fields : list[str] | str | None
            :ref:`tweet_fields_parameter`
        user_fields : list[str] | str | None
            :ref:`user_fields_parameter`
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/likes/api-reference/get-tweets-id-liking_users
        """
        return await self._make_request(
            "GET", f"/2/tweets/{id}/liking_users", params=params,
            endpoint_parameters=(
                "expansions", "max_results", "media.fields",
                "pagination_token", "place.fields", "poll.fields",
                "tweet.fields", "user.fields"
            ), data_type=User, user_auth=user_auth
        )

    async def get_liked_tweets(self, id, *, user_auth=False, **params):
        """get_liked_tweets( \
            id, *, expansions=None, max_results=None, media_fields=None, \
            pagination_token=None, place_fields=None, poll_fields=None, \
            tweet_fields=None, user_fields=None, user_auth=False \
        )

        Allows you to get information about a user’s liked Tweets.

        The Tweets returned by this endpoint count towards the Project-level
        `Tweet cap`_.

        Parameters
        ----------
        id : int | str
            User ID of the user to request liked Tweets for.
        expansions : list[str] | str | None
            :ref:`expansions_parameter`
        max_results : int | None
            The maximum number of results to be returned per page. This can be
            a number between 5 and 100. By default, each page will return 100
            results.
        media_fields : list[str] | str | None
            :ref:`media_fields_parameter`
        pagination_token : str | None
            Used to request the next page of results if all results weren't
            returned with the latest request, or to go back to the previous
            page of results. To return the next page, pass the ``next_token``
            returned in your previous response. To go back one page, pass the
            ``previous_token`` returned in your previous response.
        place_fields : list[str] | str | None
            :ref:`place_fields_parameter`
        poll_fields : list[str] | str | None
            :ref:`poll_fields_parameter`
        tweet_fields : list[str] | str | None
            :ref:`tweet_fields_parameter`
        user_fields : list[str] | str | None
            :ref:`user_fields_parameter`
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/likes/api-reference/get-users-id-liked_tweets

        .. _Tweet cap: https://developer.twitter.com/en/docs/projects/overview#tweet-cap
        """
        return await self._make_request(
            "GET", f"/2/users/{id}/liked_tweets", params=params,
            endpoint_parameters=(
                "expansions", "max_results", "media.fields",
                "pagination_token", "place.fields", "poll.fields",
                "tweet.fields", "user.fields"
            ), data_type=Tweet, user_auth=user_auth
        )

    async def like(self, tweet_id, *, user_auth=True):
        """Like a Tweet.

        .. note::

            When using OAuth 2.0 Authorization Code Flow with PKCE with
            ``user_auth=False``, a request is made beforehand to Twitter's API
            to determine the authenticating user's ID. This is cached and only
            done once per :class:`AsyncClient` instance for each access token
            used.

        Parameters
        ----------
        tweet_id : int | str
            The ID of the Tweet that you would like to Like.
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Raises
        ------
        TypeError
            If the access token isn't set

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/likes/api-reference/post-users-id-likes
        """
        id = await self._get_authenticating_user_id(oauth_1=user_auth)
        route = f"/2/users/{id}/likes"

        return await self._make_request(
            "POST", route, json={"tweet_id": str(tweet_id)},
            user_auth=user_auth
        )

    # Manage Tweets

    async def delete_tweet(self, id, *, user_auth=True):
        """Allows an authenticated user ID to delete a Tweet.

        Parameters
        ----------
        id : int | str
            The Tweet ID you are deleting.
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/manage-tweets/api-reference/delete-tweets-id
        """
        return await self._make_request(
            "DELETE", f"/2/tweets/{id}", user_auth=user_auth
        )

    async def create_tweet(
        self, *, direct_message_deep_link=None, for_super_followers_only=None,
        place_id=None, media_ids=None, media_tagged_user_ids=None,
        poll_duration_minutes=None, poll_options=None, quote_tweet_id=None,
        exclude_reply_user_ids=None, in_reply_to_tweet_id=None,
        reply_settings=None, text=None, user_auth=True
    ):
        """Creates a Tweet on behalf of an authenticated user.

        Parameters
        ----------
        direct_message_deep_link : str | None
            `Tweets a link directly to a Direct Message conversation`_ with an
            account.
        for_super_followers_only : bool | None
            Allows you to Tweet exclusively for `Super Followers`_.
        place_id : str | None
            Place ID being attached to the Tweet for geo location.
        media_ids : list[int | str] | None
            A list of Media IDs being attached to the Tweet. This is only
            required if the request includes the ``tagged_user_ids``.
        media_tagged_user_ids : list[int | str] | None
            A list of User IDs being tagged in the Tweet with Media. If the
            user you're tagging doesn't have photo-tagging enabled, their names
            won't show up in the list of tagged users even though the Tweet is
            successfully created.
        poll_duration_minutes : int | None
            Duration of the poll in minutes for a Tweet with a poll. This is
            only required if the request includes ``poll.options``.
        poll_options : list[str] | None
            A list of poll options for a Tweet with a poll.
        quote_tweet_id : int | str | None
            Link to the Tweet being quoted.
        exclude_reply_user_ids : list[int | str] | None
            A list of User IDs to be excluded from the reply Tweet thus
            removing a user from a thread.
        in_reply_to_tweet_id : int | str | None
            Tweet ID of the Tweet being replied to. Please note that
            ``in_reply_to_tweet_id`` needs to be in the request if
            ``exclude_reply_user_ids`` is present.
        reply_settings : str | None
            `Settings`_ to indicate who can reply to the Tweet. Limited to
            "mentionedUsers" and "following". If the field isn’t specified, it
            will default to everyone.
        text : str | None
            Text of the Tweet being created. This field is required if
            ``media.media_ids`` is not present.
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/manage-tweets/api-reference/post-tweets

        .. _Tweets a link directly to a Direct Message conversation: https://business.twitter.com/en/help/campaign-editing-and-optimization/public-to-private-conversation.html
        .. _Super Followers: https://help.twitter.com/en/using-twitter/super-follows
        .. _Settings: https://blog.twitter.com/en_us/topics/product/2020/new-conversation-settings-coming-to-a-tweet-near-you
        """
        json = {}

        if direct_message_deep_link is not None:
            json["direct_message_deep_link"] = direct_message_deep_link

        if for_super_followers_only is not None:
            json["for_super_followers_only"] = for_super_followers_only

        if place_id is not None:
            json["geo"] = {"place_id": place_id}

        if media_ids is not None:
            json["media"] = {
                "media_ids": [str(media_id) for media_id in media_ids]
            }
            if media_tagged_user_ids is not None:
                json["media"]["tagged_user_ids"] = [
                    str(media_tagged_user_id)
                    for media_tagged_user_id in media_tagged_user_ids
                ]

        if poll_options is not None:
            json["poll"] = {"options": poll_options}
            if poll_duration_minutes is not None:
                json["poll"]["duration_minutes"] = poll_duration_minutes

        if quote_tweet_id is not None:
            json["quote_tweet_id"] = str(quote_tweet_id)

        if in_reply_to_tweet_id is not None:
            json["reply"] = {"in_reply_to_tweet_id": str(in_reply_to_tweet_id)}
            if exclude_reply_user_ids is not None:
                json["reply"]["exclude_reply_user_ids"] = [
                    str(exclude_reply_user_id)
                    for exclude_reply_user_id in exclude_reply_user_ids
                ]

        if reply_settings is not None:
            json["reply_settings"] = reply_settings

        if text is not None:
            json["text"] = text

        return await self._make_request(
            "POST", f"/2/tweets", json=json, user_auth=user_auth
        )

    # Quote Tweets

    async def get_quote_tweets(self, id, *, user_auth=False, **params):
        """get_quote_tweets( \
            id, *, exclude=None, expansions=None, max_results=None, \
            media_fields=None, pagination_token=None, place_fields=None, \
            poll_fields=None, tweet_fields=None, user_fields=None, \
            user_auth=False \
        )

        Returns Quote Tweets for a Tweet specified by the requested Tweet ID.

        The Tweets returned by this endpoint count towards the Project-level
        `Tweet cap`_.

        .. versionchanged:: 4.11
            Added ``exclude`` parameter

        Parameters
        ----------
        id : int | str
            Unique identifier of the Tweet to request.
        exclude : list[str] | str | None
            Comma-separated list of the types of Tweets to exclude from the
            response.
        expansions : list[str] | str | None
            :ref:`expansions_parameter`
        max_results : int | None
            Specifies the number of Tweets to try and retrieve, up to a maximum
            of 100 per distinct request. By default, 10 results are returned if
            this parameter is not supplied. The minimum permitted value is 10.
            It is possible to receive less than the ``max_results`` per request
            throughout the pagination process.
        media_fields : list[str] | str | None
            :ref:`media_fields_parameter`
        pagination_token : str | None
            This parameter is used to move forwards through 'pages' of results,
            based on the value of the ``next_token``. The value used with the
            parameter is pulled directly from the response provided by the API,
            and should not be modified.
        place_fields : list[str] | str | None
            :ref:`place_fields_parameter`
        poll_fields : list[str] | str | None
            :ref:`poll_fields_parameter`
        tweet_fields : list[str] | str | None
            :ref:`tweet_fields_parameter`
        user_fields : list[str] | str | None
            :ref:`user_fields_parameter`
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/quote-tweets/api-reference/get-tweets-id-quote_tweets

        .. _Tweet cap: https://developer.twitter.com/en/docs/projects/overview#tweet-cap
        """
        return await self._make_request(
            "GET", f"/2/tweets/{id}/quote_tweets", params=params,
            endpoint_parameters=(
                "exclude", "expansions", "max_results", "media.fields",
                "pagination_token", "place.fields", "poll.fields",
                "tweet.fields", "user.fields"
            ), data_type=Tweet, user_auth=user_auth
        )

    # Retweets

    async def unretweet(self, source_tweet_id, *, user_auth=True):
        """Allows an authenticated user ID to remove the Retweet of a Tweet.

        The request succeeds with no action when the user sends a request to a
        user they're not Retweeting the Tweet or have already removed the
        Retweet of.

        .. note::

            When using OAuth 2.0 Authorization Code Flow with PKCE with
            ``user_auth=False``, a request is made beforehand to Twitter's API
            to determine the authenticating user's ID. This is cached and only
            done once per :class:`AsyncClient` instance for each access token
            used.

        Parameters
        ----------
        source_tweet_id : int | str
            The ID of the Tweet that you would like to remove the Retweet of.
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Raises
        ------
        TypeError
            If the access token isn't set

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/retweets/api-reference/delete-users-id-retweets-tweet_id
        """
        id = await self._get_authenticating_user_id(oauth_1=user_auth)
        route = f"/2/users/{id}/retweets/{source_tweet_id}"

        return await self._make_request(
            "DELETE", route, user_auth=user_auth
        )

    async def get_retweeters(self, id, *, user_auth=False, **params):
        """get_retweeters( \
            id, *, expansions=None, max_results=None, media_fields=None, \
            pagination_token=None, place_fields=None, poll_fields=None, \
            tweet_fields=None, user_fields=None, user_auth=False \
        )

        Allows you to get information about who has Retweeted a Tweet.

        Parameters
        ----------
        id : int | str
            Tweet ID of the Tweet to request Retweeting users of.
        expansions : list[str] | str | None
            :ref:`expansions_parameter`
        max_results : int | None
            The maximum number of results to be returned per page. This can be
            a number between 1 and 100. By default, each page will return 100
            results.
        media_fields : list[str] | str | None
            :ref:`media_fields_parameter`
        pagination_token : str | None
            Used to request the next page of results if all results weren't
            returned with the latest request, or to go back to the previous
            page of results. To return the next page, pass the ``next_token``
            returned in your previous response. To go back one page, pass the
            ``previous_token`` returned in your previous response.
        place_fields : list[str] | str | None
            :ref:`place_fields_parameter`
        poll_fields : list[str] | str | None
            :ref:`poll_fields_parameter`
        tweet_fields : list[str] | str | None
            :ref:`tweet_fields_parameter`
        user_fields : list[str] | str | None
            :ref:`user_fields_parameter`
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/retweets/api-reference/get-tweets-id-retweeted_by
        """
        return await self._make_request(
            "GET", f"/2/tweets/{id}/retweeted_by", params=params,
            endpoint_parameters=(
                "expansions", "max_results", "media.fields",
                "pagination_token", "place.fields", "poll.fields",
                "tweet.fields", "user.fields"
            ), data_type=User, user_auth=user_auth
        )

    async def retweet(self, tweet_id, *, user_auth=True):
        """Causes the user ID to Retweet the target Tweet.

        .. note::

            When using OAuth 2.0 Authorization Code Flow with PKCE with
            ``user_auth=False``, a request is made beforehand to Twitter's API
            to determine the authenticating user's ID. This is cached and only
            done once per :class:`AsyncClient` instance for each access token
            used.

        Parameters
        ----------
        tweet_id : int | str
            The ID of the Tweet that you would like to Retweet.
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Raises
        ------
        TypeError
            If the access token isn't set

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/retweets/api-reference/post-users-id-retweets
        """
        id = await self._get_authenticating_user_id(oauth_1=user_auth)
        route = f"/2/users/{id}/retweets"

        return await self._make_request(
            "POST", route, json={"tweet_id": str(tweet_id)},
            user_auth=user_auth
        )

    # Search Tweets

    async def search_all_tweets(self, query, **params):
        """search_all_tweets( \
            query, *, end_time=None, expansions=None, max_results=None, \
            media_fields=None, next_token=None, place_fields=None, \
            poll_fields=None, since_id=None, sort_order=None, \
            start_time=None, tweet_fields=None, until_id=None, \
            user_fields=None \
        )

        This endpoint is only available to those users who have been approved
        for the `Academic Research product track`_.

        The full-archive search endpoint returns the complete history of public
        Tweets matching a search query; since the first Tweet was created March
        26, 2006.

        The Tweets returned by this endpoint count towards the Project-level
        `Tweet cap`_.

        .. note::

            By default, a request will return Tweets from up to 30 days ago if
            the ``start_time`` parameter is not provided.

        Parameters
        ----------
        query : str
            One query for matching Tweets. Up to 1024 characters.
        end_time : datetime.datetime | str | None
            YYYY-MM-DDTHH:mm:ssZ (ISO 8601/RFC 3339). Used with ``start_time``.
            The newest, most recent UTC timestamp to which the Tweets will be
            provided. Timestamp is in second granularity and is exclusive (for
            example, 12:00:01 excludes the first second of the minute). If used
            without ``start_time``, Tweets from 30 days before ``end_time``
            will be returned by default. If not specified, ``end_time`` will
            default to [now - 30 seconds].
        expansions : list[str] | str | None
            :ref:`expansions_parameter`
        max_results : int | None
            The maximum number of search results to be returned by a request. A
            number between 10 and the system limit (currently 500). By default,
            a request response will return 10 results.
        media_fields : list[str] | str | None
            :ref:`media_fields_parameter`
        next_token : str | None
            This parameter is used to get the next 'page' of results. The value
            used with the parameter is pulled directly from the response
            provided by the API, and should not be modified. You can learn more
            by visiting our page on `pagination`_.
        place_fields : list[str] | str | None
            :ref:`place_fields_parameter`
        poll_fields : list[str] | str | None
            :ref:`poll_fields_parameter`
        since_id : int | str | None
            Returns results with a Tweet ID greater than (for example, more
            recent than) the specified ID. The ID specified is exclusive and
            responses will not include it. If included with the same request as
            a ``start_time`` parameter, only ``since_id`` will be used.
        sort_order : str | None
            This parameter is used to specify the order in which you want the
            Tweets returned. By default, a request will return the most recent
            Tweets first (sorted by recency).
        start_time : datetime.datetime | str | None
            YYYY-MM-DDTHH:mm:ssZ (ISO 8601/RFC 3339). The oldest UTC timestamp
            from which the Tweets will be provided. Timestamp is in second
            granularity and is inclusive (for example, 12:00:01 includes the
            first second of the minute). By default, a request will return
            Tweets from up to 30 days ago if you do not include this parameter.
        tweet_fields : list[str] | str | None
            :ref:`tweet_fields_parameter`
        until_id : int | str | None
            Returns results with a Tweet ID less than (that is, older than) the
            specified ID. Used with ``since_id``. The ID specified is exclusive
            and responses will not include it.
        user_fields : list[str] | str | None
            :ref:`user_fields_parameter`

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-all

        .. _Academic Research product track: https://developer.twitter.com/en/docs/projects/overview#product-track
        .. _Tweet cap: https://developer.twitter.com/en/docs/projects/overview#tweet-cap
        .. _pagination: https://developer.twitter.com/en/docs/twitter-api/tweets/search/integrate/paginate
        """
        params["query"] = query
        return await self._make_request(
            "GET", "/2/tweets/search/all", params=params,
            endpoint_parameters=(
                "end_time", "expansions", "max_results", "media.fields",
                "next_token", "place.fields", "poll.fields", "query",
                "since_id", "sort_order", "start_time", "tweet.fields",
                "until_id", "user.fields"
            ), data_type=Tweet
        )

    async def search_recent_tweets(self, query, *, user_auth=False, **params):
        """search_recent_tweets( \
            query, *, end_time=None, expansions=None, max_results=None, \
            media_fields=None, next_token=None, place_fields=None, \
            poll_fields=None, since_id=None, sort_order=None, \
            start_time=None, tweet_fields=None, until_id=None, \
            user_fields=None, user_auth=False \
        )

        The recent search endpoint returns Tweets from the last seven days that
        match a search query.

        The Tweets returned by this endpoint count towards the Project-level
        `Tweet cap`_.

        Parameters
        ----------
        query : str
            One rule for matching Tweets. If you are using a
            `Standard Project`_ at the Basic `access level`_, you can use the
            basic set of `operators`_ and can make queries up to 512 characters
            long. If you are using an `Academic Research Project`_ at the Basic
            access level, you can use all available operators and can make
            queries up to 1,024 characters long.
        end_time : datetime.datetime | str | None
            YYYY-MM-DDTHH:mm:ssZ (ISO 8601/RFC 3339). The newest, most recent
            UTC timestamp to which the Tweets will be provided. Timestamp is in
            second granularity and is exclusive (for example, 12:00:01 excludes
            the first second of the minute). By default, a request will return
            Tweets from as recent as 30 seconds ago if you do not include this
            parameter.
        expansions : list[str] | str | None
            :ref:`expansions_parameter`
        max_results : int | None
            The maximum number of search results to be returned by a request. A
            number between 10 and 100. By default, a request response will
            return 10 results.
        media_fields : list[str] | str | None
            :ref:`media_fields_parameter`
        next_token : str | None
            This parameter is used to get the next 'page' of results. The value
            used with the parameter is pulled directly from the response
            provided by the API, and should not be modified.
        place_fields : list[str] | str | None
            :ref:`place_fields_parameter`
        poll_fields : list[str] | str | None
            :ref:`poll_fields_parameter`
        since_id : int | str | None
            Returns results with a Tweet ID greater than (that is, more recent
            than) the specified ID. The ID specified is exclusive and responses
            will not include it. If included with the same request as a
            ``start_time`` parameter, only ``since_id`` will be used.
        sort_order : str | None
            This parameter is used to specify the order in which you want the
            Tweets returned. By default, a request will return the most recent
            Tweets first (sorted by recency).
        start_time : datetime.datetime | str | None
            YYYY-MM-DDTHH:mm:ssZ (ISO 8601/RFC 3339). The oldest UTC timestamp
            (from most recent seven days) from which the Tweets will be
            provided. Timestamp is in second granularity and is inclusive (for
            example, 12:00:01 includes the first second of the minute). If
            included with the same request as a ``since_id`` parameter, only
            ``since_id`` will be used. By default, a request will return Tweets
            from up to seven days ago if you do not include this parameter.
        tweet_fields : list[str] | str | None
            :ref:`tweet_fields_parameter`
        until_id : int | str | None
            Returns results with a Tweet ID less than (that is, older than) the
            specified ID. The ID specified is exclusive and responses will not
            include it.
        user_fields : list[str] | str | None
            :ref:`user_fields_parameter`
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-recent

        .. _Tweet cap: https://developer.twitter.com/en/docs/projects/overview#tweet-cap
        .. _Standard Project: https://developer.twitter.com/en/docs/projects
        .. _access level: https://developer.twitter.com/en/products/twitter-api/early-access/guide.html#na_1
        .. _operators: https://developer.twitter.com/en/docs/twitter-api/tweets/search/integrate/build-a-query
        .. _Academic Research Project: https://developer.twitter.com/en/docs/projects
        """
        params["query"] = query
        return await self._make_request(
            "GET", "/2/tweets/search/recent", params=params,
            endpoint_parameters=(
                "end_time", "expansions", "max_results", "media.fields",
                "next_token", "place.fields", "poll.fields", "query",
                "since_id", "sort_order", "start_time", "tweet.fields",
                "until_id", "user.fields"
            ), data_type=Tweet, user_auth=user_auth
        )

    # Timelines

    async def get_users_mentions(self, id, *, user_auth=False, **params):
        """get_users_mentions( \
            id, *, end_time=None, expansions=None, max_results=None, \
            media_fields=None, pagination_token=None, place_fields=None, \
            poll_fields=None, since_id=None, start_time=None, \
            tweet_fields=None, until_id=None, user_fields=None, \
            user_auth=False \
        )

        Returns Tweets mentioning a single user specified by the requested user
        ID. By default, the most recent ten Tweets are returned per request.
        Using pagination, up to the most recent 800 Tweets can be retrieved.

        The Tweets returned by this endpoint count towards the Project-level
        `Tweet cap`_.

        Parameters
        ----------
        id : int | str
            Unique identifier of the user for whom to return Tweets mentioning
            the user. User ID can be referenced using the `user/lookup`_
            endpoint. More information on Twitter IDs is `here`_.
        end_time : datetime.datetime | str | None
            YYYY-MM-DDTHH:mm:ssZ (ISO 8601/RFC 3339). The new UTC timestamp
            from which the Tweets will be provided. Timestamp is in second
            granularity and is inclusive (for example, 12:00:01 includes the
            first second of the minute).

            Please note that this parameter does not support a millisecond
            value.
        expansions : list[str] | str | None
            :ref:`expansions_parameter`
        max_results : int | None
            Specifies the number of Tweets to try and retrieve, up to a maximum
            of 100 per distinct request. By default, 10 results are returned if
            this parameter is not supplied. The minimum permitted value is 5.
            It is possible to receive less than the ``max_results`` per request
            throughout the pagination process.
        media_fields : list[str] | str | None
            :ref:`media_fields_parameter`
        pagination_token : str | None
            This parameter is used to move forwards or backwards through
            'pages' of results, based on the value of the ``next_token`` or
            ``previous_token`` in the response. The value used with the
            parameter is pulled directly from the response provided by the API,
            and should not be modified.
        place_fields : list[str] | str | None
            :ref:`place_fields_parameter`
        poll_fields : list[str] | str | None
            :ref:`poll_fields_parameter`
        since_id : int | str | None
            Returns results with a Tweet ID greater than (that is, more recent
            than) the specified 'since' Tweet ID. There are limits to the
            number of Tweets that can be accessed through the API. If the limit
            of Tweets has occurred since the ``since_id``, the ``since_id``
            will be forced to the oldest ID available. More information on
            Twitter IDs is `here`_.
        start_time : datetime.datetime | str | None
            YYYY-MM-DDTHH:mm:ssZ (ISO 8601/RFC 3339). The oldest UTC timestamp
            from which the Tweets will be provided. Timestamp is in second
            granularity and is inclusive (for example, 12:00:01 includes the
            first second of the minute).

            Please note that this parameter does not support a millisecond
            value.
        tweet_fields : list[str] | str | None
            :ref:`tweet_fields_parameter`
        until_id : int | str | None
            Returns results with a Tweet ID less less than (that is, older
            than) the specified 'until' Tweet ID. There are limits to the
            number of Tweets that can be accessed through the API. If the limit
            of Tweets has occurred since the ``until_id``, the ``until_id``
            will be forced to the most recent ID available. More information on
            Twitter IDs is `here`_.
        user_fields : list[str] | str | None
            :ref:`user_fields_parameter`
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/timelines/api-reference/get-users-id-mentions

        .. _Tweet cap: https://developer.twitter.com/en/docs/projects/overview#tweet-cap
        .. _user/lookup: https://developer.twitter.com/en/docs/twitter-api/users/lookup/introduction
        .. _here: https://developer.twitter.com/en/docs/twitter-ids
        """
        return await self._make_request(
            "GET", f"/2/users/{id}/mentions", params=params,
            endpoint_parameters=(
                "end_time", "expansions", "max_results", "media.fields",
                "pagination_token", "place.fields", "poll.fields", "since_id",
                "start_time", "tweet.fields", "until_id", "user.fields"
            ), data_type=Tweet, user_auth=user_auth
        )

    async def get_home_timeline(self, *, user_auth=True, **params):
        """get_home_timeline( \
            *, end_time=None, exclude=None, expansions=None, \
            max_results=None, media_fields=None, pagination_token=None, \
            place_fields=None, poll_fields=None, since_id=None, \
            start_time=None, tweet_fields=None, until_id=None, \
            user_fields=None, user_auth=True \
        )

        Allows you to retrieve a collection of the most recent Tweets and
        Retweets posted by you and users you follow. This endpoint returns up
        to the last 3200 Tweets.

        .. note::

            When using OAuth 2.0 Authorization Code Flow with PKCE with
            ``user_auth=False``, a request is made beforehand to Twitter's API
            to determine the authenticating user's ID. This is cached and only
            done once per :class:`AsyncClient` instance for each access token
            used.

        Parameters
        ----------
        end_time : datetime.datetime | str | None
            YYYY-MM-DDTHH:mm:ssZ (ISO 8601/RFC 3339). The new UTC timestamp
            from which the Tweets will be provided. Timestamp is in second
            granularity and is inclusive (for example, 12:00:01 includes the
            first second of the minute).

            Please note that this parameter does not support a millisecond
            value.
        exclude : list[str] | str | None
            Comma-separated list of the types of Tweets to exclude from the
            response.
        expansions : list[str] | str | None
            :ref:`expansions_parameter`
        max_results : int | None
            Specifies the number of Tweets to try and retrieve, up to a maximum
            of 100 per distinct request. By default, 100 results are returned
            if this parameter is not supplied. The minimum permitted value is
            1. It is possible to receive less than the ``max_results`` per
            request throughout the pagination process.
        media_fields : list[str] | str | None
            :ref:`media_fields_parameter`
        pagination_token : str | None
            This parameter is used to move forwards or backwards through
            'pages' of results, based on the value of the ``next_token`` or
            ``previous_token`` in the response. The value used with the
            parameter is pulled directly from the response provided by the API,
            and should not be modified.
        place_fields : list[str] | str | None
            :ref:`place_fields_parameter`
        poll_fields : list[str] | str | None
            :ref:`poll_fields_parameter`
        since_id : int | str | None
            Returns results with a Tweet ID greater than (that is, more recent
            than) the specified 'since' Tweet ID. There are limits to the
            number of Tweets that can be accessed through the API. If the
            limit of Tweets has occurred since the ``since_id``, the
            ``since_id`` will be forced to the oldest ID available. More
            information on Twitter IDs is `here`_.
        start_time : datetime.datetime | str | None
            YYYY-MM-DDTHH:mm:ssZ (ISO 8601/RFC 3339). The oldest UTC timestamp
            from which the Tweets will be provided. Timestamp is in second
            granularity and is inclusive (for example, 12:00:01 includes the
            first second of the minute).

            Please note that this parameter does not support a millisecond
            value.
        tweet_fields : list[str] | str | None
            :ref:`tweet_fields_parameter`
        until_id : int | str | None
            Returns results with a Tweet ID less than (that is, older than) the
            specified 'until' Tweet ID. There are limits to the number of
            Tweets that can be accessed through the API. If the limit of Tweets
            has occurred since the ``until_id``, the ``until_id`` will be
            forced to the most recent ID available. More information on Twitter
            IDs is `here`_.
        user_fields : list[str] | str | None
            :ref:`user_fields_parameter`
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Returns
        -------
        dict | requests.Response | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/timelines/api-reference/get-users-id-reverse-chronological

        .. _here: https://developer.twitter.com/en/docs/twitter-ids
        """
        id = await self._get_authenticating_user_id(oauth_1=user_auth)
        route = f"/2/users/{id}/timelines/reverse_chronological"

        return await self._make_request(
            "GET", route, params=params,
            endpoint_parameters=(
                "end_time", "exclude", "expansions", "max_results",
                "media.fields", "pagination_token", "place.fields",
                "poll.fields", "since_id", "start_time", "tweet.fields",
                "until_id", "user.fields"
            ), data_type=Tweet, user_auth=user_auth
        )

    async def get_users_tweets(self, id, *, user_auth=False, **params):
        """get_users_tweets( \
            id, *, end_time=None, exclude=None, expansions=None, \
            max_results=None, media_fields=None, pagination_token=None, \
            place_fields=None, poll_fields=None, since_id=None, \
            start_time=None, tweet_fields=None, until_id=None, \
            user_fields=None, user_auth=False \
        )

        Returns Tweets composed by a single user, specified by the requested
        user ID. By default, the most recent ten Tweets are returned per
        request. Using pagination, the most recent 3,200 Tweets can be
        retrieved.

        The Tweets returned by this endpoint count towards the Project-level
        `Tweet cap`_.

        Parameters
        ----------
        id : int | str
            Unique identifier of the Twitter account (user ID) for whom to
            return results. User ID can be referenced using the `user/lookup`_
            endpoint. More information on Twitter IDs is `here`_.
        end_time : datetime.datetime | str | None
            YYYY-MM-DDTHH:mm:ssZ (ISO 8601/RFC 3339). The newest or most recent
            UTC timestamp from which the Tweets will be provided. Only the 3200
            most recent Tweets are available. Timestamp is in second
            granularity and is inclusive (for example, 12:00:01 includes the
            first second of the minute). Minimum allowable time is
            2010-11-06T00:00:01Z

            Please note that this parameter does not support a millisecond
            value.
        exclude : list[str] | str | None
            Comma-separated list of the types of Tweets to exclude from the
            response. When ``exclude=retweets`` is used, the maximum historical
            Tweets returned is still 3200. When the ``exclude=replies``
            parameter is used for any value, only the most recent 800 Tweets
            are available.
        expansions : list[str] | str | None
            :ref:`expansions_parameter`
        max_results : int | None
            Specifies the number of Tweets to try and retrieve, up to a maximum
            of 100 per distinct request. By default, 10 results are returned if
            this parameter is not supplied. The minimum permitted value is 5.
            It is possible to receive less than the ``max_results`` per request
            throughout the pagination process.
        media_fields : list[str] | str | None
            :ref:`media_fields_parameter`
        pagination_token : str | None
            This parameter is used to move forwards or backwards through
            'pages' of results, based on the value of the ``next_token`` or
            ``previous_token`` in the response. The value used with the
            parameter is pulled directly from the response provided by the API,
            and should not be modified.
        place_fields : list[str] | str | None
            :ref:`place_fields_parameter`
        poll_fields : list[str] | str | None
            :ref:`poll_fields_parameter`
        since_id : int | str | None
            Returns results with a Tweet ID greater than (that is, more recent
            than) the specified 'since' Tweet ID. Only the 3200 most recent
            Tweets are available. The result will exclude the ``since_id``. If
            the limit of Tweets has occurred since the ``since_id``, the
            ``since_id`` will be forced to the oldest ID available.
        start_time : datetime.datetime | str | None
            YYYY-MM-DDTHH:mm:ssZ (ISO 8601/RFC 3339). The oldest or earliest
            UTC timestamp from which the Tweets will be provided. Only the 3200
            most recent Tweets are available. Timestamp is in second
            granularity and is inclusive (for example, 12:00:01 includes the
            first second of the minute). Minimum allowable time is
            2010-11-06T00:00:00Z

            Please note that this parameter does not support a millisecond
            value.
        tweet_fields : list[str] | str | None
            :ref:`tweet_fields_parameter`
        until_id : int | str | None
            Returns results with a Tweet ID less less than (that is, older
            than) the specified 'until' Tweet ID. Only the 3200 most recent
            Tweets are available. The result will exclude the ``until_id``. If
            the limit of Tweets has occurred since the ``until_id``, the
            ``until_id`` will be forced to the most recent ID available.
        user_fields : list[str] | str | None
            :ref:`user_fields_parameter`
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/timelines/api-reference/get-users-id-tweets

        .. _Tweet cap: https://developer.twitter.com/en/docs/projects/overview#tweet-cap
        .. _user/lookup: https://developer.twitter.com/en/docs/twitter-api/users/lookup/introduction
        .. _here: https://developer.twitter.com/en/docs/twitter-ids
        """
        return await self._make_request(
            "GET", f"/2/users/{id}/tweets", params=params,
            endpoint_parameters=(
                "end_time", "exclude", "expansions", "max_results",
                "media.fields", "pagination_token", "place.fields",
                "poll.fields", "since_id", "start_time", "tweet.fields",
                "until_id", "user.fields"
            ), data_type=Tweet, user_auth=user_auth
        )

    # Tweet counts

    async def get_all_tweets_count(self, query, **params):
        """get_all_tweets_count( \
            query, *, end_time=None, granularity=None, next_token=None, \
            since_id=None, start_time=None, until_id=None \
        )

        This endpoint is only available to those users who have been approved
        for the `Academic Research product track`_.

        The full-archive search endpoint returns the complete history of public
        Tweets matching a search query; since the first Tweet was created March
        26, 2006.

        Parameters
        ----------
        query : str
            One query for matching Tweets. Up to 1024 characters.
        end_time : datetime.datetime | str | None
            YYYY-MM-DDTHH:mm:ssZ (ISO 8601/RFC 3339). Used with ``start_time``.
            The newest, most recent UTC timestamp to which the Tweets will be
            provided. Timestamp is in second granularity and is exclusive (for
            example, 12:00:01 excludes the first second of the minute). If used
            without ``start_time``, Tweets from 30 days before ``end_time``
            will be returned by default. If not specified, ``end_time`` will
            default to [now - 30 seconds].
        granularity : str | None
            This is the granularity that you want the timeseries count data to
            be grouped by. You can request ``minute``, ``hour``, or ``day``
            granularity. The default granularity, if not specified is ``hour``.
        next_token : str | None
            This parameter is used to get the next 'page' of results. The value
            used with the parameter is pulled directly from the response
            provided by the API, and should not be modified. You can learn more
            by visiting our page on `pagination`_.
        since_id : int | str | None
            Returns results with a Tweet ID greater than (for example, more
            recent than) the specified ID. The ID specified is exclusive and
            responses will not include it. If included with the same request as
            a ``start_time`` parameter, only ``since_id`` will be used.
        start_time : datetime.datetime | str | None
            YYYY-MM-DDTHH:mm:ssZ (ISO 8601/RFC 3339). The oldest UTC timestamp
            from which the Tweets will be provided. Timestamp is in second
            granularity and is inclusive (for example, 12:00:01 includes the
            first second of the minute). By default, a request will return
            Tweets from up to 30 days ago if you do not include this parameter.
        until_id : int | str | None
            Returns results with a Tweet ID less than (that is, older than) the
            specified ID. Used with ``since_id``. The ID specified is exclusive
            and responses will not include it.

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/counts/api-reference/get-tweets-counts-all

        .. _Academic Research product track: https://developer.twitter.com/en/docs/projects/overview#product-track
        .. _pagination: https://developer.twitter.com/en/docs/twitter-api/tweets/search/integrate/paginate
        """
        params["query"] = query
        return await self._make_request(
            "GET", "/2/tweets/counts/all", params=params,
            endpoint_parameters=(
                "end_time", "granularity", "next_token", "query", "since_id",
                "start_time", "until_id"
            )
        )

    async def get_recent_tweets_count(self, query, **params):
        """get_recent_tweets_count( \
            query, *, end_time=None, granularity=None, since_id=None, \
            start_time=None, until_id=None \
        )

        The recent Tweet counts endpoint returns count of Tweets from the last
        seven days that match a search query.

        Parameters
        ----------
        query : str
            One rule for matching Tweets. If you are using a
            `Standard Project`_ at the Basic `access level`_, you can use the
            basic set of `operators`_ and can make queries up to 512 characters
            long. If you are using an `Academic Research Project`_ at the Basic
            access level, you can use all available operators and can make
            queries up to 1,024 characters long.
        end_time : datetime.datetime | str | None
            YYYY-MM-DDTHH:mm:ssZ (ISO 8601/RFC 3339). The newest, most recent
            UTC timestamp to which the Tweets will be provided. Timestamp is in
            second granularity and is exclusive (for example, 12:00:01 excludes
            the first second of the minute). By default, a request will return
            Tweets from as recent as 30 seconds ago if you do not include this
            parameter.
        granularity : str | None
            This is the granularity that you want the timeseries count data to
            be grouped by. You can request ``minute``, ``hour``, or ``day``
            granularity. The default granularity, if not specified is ``hour``.
        since_id : int | str | None
            Returns results with a Tweet ID greater than (that is, more recent
            than) the specified ID. The ID specified is exclusive and responses
            will not include it. If included with the same request as a
            ``start_time`` parameter, only ``since_id`` will be used.
        start_time : datetime.datetime | str | None
            YYYY-MM-DDTHH:mm:ssZ (ISO 8601/RFC 3339). The oldest UTC timestamp
            (from most recent seven days) from which the Tweets will be
            provided. Timestamp is in second granularity and is inclusive (for
            example, 12:00:01 includes the first second of the minute). If
            included with the same request as a ``since_id`` parameter, only
            ``since_id`` will be used. By default, a request will return Tweets
            from up to seven days ago if you do not include this parameter.
        until_id : int | str | None
            Returns results with a Tweet ID less than (that is, older than) the
            specified ID. The ID specified is exclusive and responses will not
            include it.

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/counts/api-reference/get-tweets-counts-recent

        .. _Standard Project: https://developer.twitter.com/en/docs/projects
        .. _access level: https://developer.twitter.com/en/products/twitter-api/early-access/guide.html#na_1
        .. _operators: https://developer.twitter.com/en/docs/twitter-api/tweets/search/integrate/build-a-query
        .. _Academic Research Project: https://developer.twitter.com/en/docs/projects
        """
        params["query"] = query
        return await self._make_request(
            "GET", "/2/tweets/counts/recent", params=params,
            endpoint_parameters=(
                "end_time", "granularity", "query", "since_id", "start_time",
                "until_id"
            )
        )

    # Tweet lookup

    async def get_tweet(self, id, *, user_auth=False, **params):
        """get_tweet( \
            id, *, expansions=None, media_fields=None, place_fields=None, \
            poll_fields=None, tweet_fields=None, user_fields=None, \
            user_auth=False \
        )

        Returns a variety of information about a single Tweet specified by
        the requested ID.

        Parameters
        ----------
        id : int | str
            Unique identifier of the Tweet to request
        expansions : list[str] | str | None
            :ref:`expansions_parameter`
        media_fields : list[str] | str | None
            :ref:`media_fields_parameter`
        place_fields : list[str] | str | None
            :ref:`place_fields_parameter`
        poll_fields : list[str] | str | None
            :ref:`poll_fields_parameter`
        tweet_fields : list[str] | str | None
            :ref:`tweet_fields_parameter`
        user_fields : list[str] | str | None
            :ref:`user_fields_parameter`
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/lookup/api-reference/get-tweets-id
        """
        return await self._make_request(
            "GET", f"/2/tweets/{id}", params=params,
            endpoint_parameters=(
                "expansions", "media.fields", "place.fields", "poll.fields",
                "tweet.fields", "user.fields"
            ), data_type=Tweet, user_auth=user_auth
        )

    async def get_tweets(self, ids, *, user_auth=False, **params):
        """get_tweets( \
            ids, *, expansions=None, media_fields=None, place_fields=None, \
            poll_fields=None, tweet_fields=None, user_fields=None, \
            user_auth=False \
        )

        Returns a variety of information about the Tweet specified by the
        requested ID or list of IDs.

        Parameters
        ----------
        ids : list[int | str] | str
            A comma separated list of Tweet IDs. Up to 100 are allowed in a
            single request. Make sure to not include a space between commas and
            fields.
        expansions : list[str] | str | None
            :ref:`expansions_parameter`
        media_fields : list[str] | str | None
            :ref:`media_fields_parameter`
        place_fields : list[str] | str | None
            :ref:`place_fields_parameter`
        poll_fields : list[str] | str | None
            :ref:`poll_fields_parameter`
        tweet_fields : list[str] | str | None
            :ref:`tweet_fields_parameter`
        user_fields : list[str] | str | None
            :ref:`user_fields_parameter`
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/lookup/api-reference/get-tweets
        """
        params["ids"] = ids
        return await self._make_request(
            "GET", "/2/tweets", params=params,
            endpoint_parameters=(
                "ids", "expansions", "media.fields", "place.fields",
                "poll.fields", "tweet.fields", "user.fields"
            ), data_type=Tweet, user_auth=user_auth
        )

    # Blocks

    async def get_blocked(self, *, user_auth=True, **params):
        """get_blocked( \
            *, expansions=None, max_results=None, pagination_token=None, \
            tweet_fields=None, user_fields=None, user_auth=True \
        )

        Returns a list of users who are blocked by the authenticating user.

        .. note::

            When using OAuth 2.0 Authorization Code Flow with PKCE with
            ``user_auth=False``, a request is made beforehand to Twitter's API
            to determine the authenticating user's ID. This is cached and only
            done once per :class:`AsyncClient` instance for each access token
            used.

        Parameters
        ----------
        expansions : list[str] | str | None
            :ref:`expansions_parameter`
        max_results : int | None
            The maximum number of results to be returned per page. This can be
            a number between 1 and 1000. By default, each page will return 100
            results.
        pagination_token : str | None
            Used to request the next page of results if all results weren't
            returned with the latest request, or to go back to the previous
            page of results.
        tweet_fields : list[str] | str | None
            :ref:`tweet_fields_parameter`
        user_fields : list[str] | str | None
            :ref:`user_fields_parameter`
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Raises
        ------
        TypeError
            If the access token isn't set

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/users/blocks/api-reference/get-users-blocking
        """
        id = await self._get_authenticating_user_id(oauth_1=user_auth)
        route = f"/2/users/{id}/blocking"

        return await self._make_request(
            "GET", route, params=params,
            endpoint_parameters=(
                "expansions", "max_results", "pagination_token",
                "tweet.fields", "user.fields"
            ), data_type=User, user_auth=user_auth
        )

    # Follows

    async def unfollow_user(self, target_user_id, *, user_auth=True):
        """Allows a user ID to unfollow another user.

        The request succeeds with no action when the authenticated user sends a
        request to a user they're not following or have already unfollowed.

        .. note::

            When using OAuth 2.0 Authorization Code Flow with PKCE with
            ``user_auth=False``, a request is made beforehand to Twitter's API
            to determine the authenticating user's ID. This is cached and only
            done once per :class:`AsyncClient` instance for each access token
            used.

        Parameters
        ----------
        target_user_id : int | str
            The user ID of the user that you would like to unfollow.
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Raises
        ------
        TypeError
            If the access token isn't set

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/users/follows/api-reference/delete-users-source_id-following
        """
        source_user_id = await self._get_authenticating_user_id(
            oauth_1=user_auth
        )
        route = f"/2/users/{source_user_id}/following/{target_user_id}"

        return await self._make_request(
            "DELETE", route, user_auth=user_auth
        )

    async def get_users_followers(self, id, *, user_auth=False, **params):
        """get_users_followers( \
            id, *, expansions=None, max_results=None, pagination_token=None, \
            tweet_fields=None, user_fields=None, user_auth=False \
        )

        Returns a list of users who are followers of the specified user ID.

        .. note::

            The Twitter API endpoint that this method uses has been removed
            from the Basic and Pro tiers [#changelog]_.

        Parameters
        ----------
        id : int | str
            The user ID whose followers you would like to retrieve.
        expansions : list[str] | str | None
            :ref:`expansions_parameter`
        max_results : int | None
            The maximum number of results to be returned per page. This can be
            a number between 1 and the 1000. By default, each page will return
            100 results.
        pagination_token : str | None
            Used to request the next page of results if all results weren't
            returned with the latest request, or to go back to the previous
            page of results. To return the next page, pass the ``next_token``
            returned in your previous response. To go back one page, pass the
            ``previous_token`` returned in your previous response.
        tweet_fields : list[str] | str | None
            :ref:`tweet_fields_parameter`
        user_fields : list[str] | str | None
            :ref:`user_fields_parameter`
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/users/follows/api-reference/get-users-id-followers
        """
        return await self._make_request(
            "GET", f"/2/users/{id}/followers", params=params,
            endpoint_parameters=(
                "expansions", "max_results", "pagination_token",
                "tweet.fields", "user.fields"
            ),
            data_type=User, user_auth=user_auth
        )

    async def get_users_following(self, id, *, user_auth=False, **params):
        """get_users_following( \
            id, *, expansions=None, max_results=None, pagination_token=None, \
            tweet_fields=None, user_fields=None, user_auth=False \
        )

        Returns a list of users the specified user ID is following.

        .. note::

            The Twitter API endpoint that this method uses has been removed
            from the Basic and Pro tiers [#changelog]_.

        Parameters
        ----------
        id : int | str
            The user ID whose following you would like to retrieve.
        expansions : list[str] | str | None
            :ref:`expansions_parameter`
        max_results : int | None
            The maximum number of results to be returned per page. This can be
            a number between 1 and the 1000. By default, each page will return
            100 results.
        pagination_token : str | None
            Used to request the next page of results if all results weren't
            returned with the latest request, or to go back to the previous
            page of results. To return the next page, pass the ``next_token``
            returned in your previous response. To go back one page, pass the
            ``previous_token`` returned in your previous response.
        tweet_fields : list[str] | str | None
            :ref:`tweet_fields_parameter`
        user_fields : list[str] | str | None
            :ref:`user_fields_parameter`
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/users/follows/api-reference/get-users-id-following
        """
        return await self._make_request(
            "GET", f"/2/users/{id}/following", params=params,
            endpoint_parameters=(
                "expansions", "max_results", "pagination_token",
                "tweet.fields", "user.fields"
            ), data_type=User, user_auth=user_auth
        )

    async def follow_user(self, target_user_id, *, user_auth=True):
        """Allows a user ID to follow another user.

        If the target user does not have public Tweets, this endpoint will send
        a follow request.

        The request succeeds with no action when the authenticated user sends a
        request to a user they're already following, or if they're sending a
        follower request to a user that does not have public Tweets.

        .. note::

            When using OAuth 2.0 Authorization Code Flow with PKCE with
            ``user_auth=False``, a request is made beforehand to Twitter's API
            to determine the authenticating user's ID. This is cached and only
            done once per :class:`AsyncClient` instance for each access token
            used.

        Parameters
        ----------
        target_user_id : int | str
            The user ID of the user that you would like to follow.
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Raises
        ------
        TypeError
            If the access token isn't set

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/users/follows/api-reference/post-users-source_user_id-following
        """
        source_user_id = await self._get_authenticating_user_id(
            oauth_1=user_auth
        )
        route = f"/2/users/{source_user_id}/following"

        return await self._make_request(
            "POST", route, json={"target_user_id": str(target_user_id)},
            user_auth=user_auth
        )

    # Mutes

    async def unmute(self, target_user_id, *, user_auth=True):
        """Allows an authenticated user ID to unmute the target user.

        The request succeeds with no action when the user sends a request to a
        user they're not muting or have already unmuted.

        .. note::

            When using OAuth 2.0 Authorization Code Flow with PKCE with
            ``user_auth=False``, a request is made beforehand to Twitter's API
            to determine the authenticating user's ID. This is cached and only
            done once per :class:`AsyncClient` instance for each access token
            used.

        Parameters
        ----------
        target_user_id : int | str
            The user ID of the user that you would like to unmute.
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Raises
        ------
        TypeError
            If the access token isn't set

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/users/mutes/api-reference/delete-users-user_id-muting
        """
        source_user_id = await self._get_authenticating_user_id(
            oauth_1=user_auth
        )
        route = f"/2/users/{source_user_id}/muting/{target_user_id}"

        return await self._make_request(
            "DELETE", route, user_auth=user_auth
        )

    async def get_muted(self, *, user_auth=True, **params):
        """get_muted( \
            *, expansions=None, max_results=None, pagination_token=None, \
            tweet_fields=None, user_fields=None, user_auth=True \
        )

        Returns a list of users who are muted by the authenticating user.

        .. note::

            When using OAuth 2.0 Authorization Code Flow with PKCE with
            ``user_auth=False``, a request is made beforehand to Twitter's API
            to determine the authenticating user's ID. This is cached and only
            done once per :class:`AsyncClient` instance for each access token
            used.

        Parameters
        ----------
        expansions : list[str] | str | None
            :ref:`expansions_parameter`
        max_results : int | None
            The maximum number of results to be returned per page. This can be
            a number between 1 and 1000. By default, each page will return 100
            results.
        pagination_token : str | None
            Used to request the next page of results if all results weren't
            returned with the latest request, or to go back to the previous
            page of results.
        tweet_fields : list[str] | str | None
            :ref:`tweet_fields_parameter`
        user_fields : list[str] | str | None
            :ref:`user_fields_parameter`
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Raises
        ------
        TypeError
            If the access token isn't set

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/users/mutes/api-reference/get-users-muting
        """
        id = await self._get_authenticating_user_id(oauth_1=user_auth)
        route = f"/2/users/{id}/muting"

        return await self._make_request(
            "GET", route, params=params,
            endpoint_parameters=(
                "expansions", "max_results", "pagination_token",
                "tweet.fields", "user.fields"
            ), data_type=User, user_auth=user_auth
        )

    async def mute(self, target_user_id, *, user_auth=True):
        """Allows an authenticated user ID to mute the target user.

        .. note::

            When using OAuth 2.0 Authorization Code Flow with PKCE with
            ``user_auth=False``, a request is made beforehand to Twitter's API
            to determine the authenticating user's ID. This is cached and only
            done once per :class:`AsyncClient` instance for each access token
            used.

        Parameters
        ----------
        target_user_id : int | str
            The user ID of the user that you would like to mute.
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Raises
        ------
        TypeError
            If the access token isn't set

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/users/mutes/api-reference/post-users-user_id-muting
        """
        id = await self._get_authenticating_user_id(oauth_1=user_auth)
        route = f"/2/users/{id}/muting"

        return await self._make_request(
            "POST", route, json={"target_user_id": str(target_user_id)},
            user_auth=user_auth
        )

    # User lookup

    async def get_user(
        self, *, id=None, username=None, user_auth=False, **params
    ):
        """get_user(*, id=None, username=None, expansions=None, \
                    tweet_fields=None, user_fields=None, user_auth=False)

        Returns a variety of information about a single user specified by the
        requested ID or username.

        Parameters
        ----------
        id : int | str | None
            The ID of the user to lookup.
        username : str | None
            The Twitter username (handle) of the user.
        expansions : list[str] | str | None
            :ref:`expansions_parameter`
        tweet_fields : list[str] | str | None
            :ref:`tweet_fields_parameter`
        user_fields : list[str] | str | None
            :ref:`user_fields_parameter`
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Raises
        ------
        TypeError
            If ID and username are not passed or both are passed

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/users/lookup/api-reference/get-users-id
        https://developer.twitter.com/en/docs/twitter-api/users/lookup/api-reference/get-users-by-username-username
        """
        if id is not None and username is not None:
            raise TypeError("Expected ID or username, not both")

        route = "/2/users"

        if id is not None:
            route += f"/{id}"
        elif username is not None:
            route += f"/by/username/{username}"
        else:
            raise TypeError("ID or username is required")

        return await self._make_request(
            "GET", route, params=params,
            endpoint_parameters=("expansions", "tweet.fields", "user.fields"),
            data_type=User, user_auth=user_auth
        )

    async def get_users(self, *, ids=None, usernames=None, user_auth=False,
                        **params):
        """get_users(*, ids=None, usernames=None, expansions=None, \
                     tweet_fields=None, user_fields=None, user_auth=False)

        Returns a variety of information about one or more users specified by
        the requested IDs or usernames.

        Parameters
        ----------
        ids : list[int | str] | str | None
            A comma separated list of user IDs. Up to 100 are allowed in a
            single request. Make sure to not include a space between commas and
            fields.
        usernames : list[str] | str | None
            A comma separated list of Twitter usernames (handles). Up to 100
            are allowed in a single request. Make sure to not include a space
            between commas and fields.
        expansions : list[str] | str | None
            :ref:`expansions_parameter`
        tweet_fields : list[str] | str | None
            :ref:`tweet_fields_parameter`
        user_fields : list[str] | str | None
            :ref:`user_fields_parameter`
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Raises
        ------
        TypeError
            If IDs and usernames are not passed or both are passed

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/users/lookup/api-reference/get-users
        https://developer.twitter.com/en/docs/twitter-api/users/lookup/api-reference/get-users-by
        """
        if ids is not None and usernames is not None:
            raise TypeError("Expected IDs or usernames, not both")

        route = "/2/users"

        if ids is not None:
            params["ids"] = ids
        elif usernames is not None:
            route += "/by"
            params["usernames"] = usernames
        else:
            raise TypeError("IDs or usernames are required")

        return await self._make_request(
            "GET", route, params=params,
            endpoint_parameters=(
                "ids", "usernames", "expansions", "tweet.fields", "user.fields"
            ), data_type=User, user_auth=user_auth
        )

    async def get_me(self, *, user_auth=True, **params):
        """get_me(*, expansions=None, tweet_fields=None, user_fields=None, \
                  user_auth=True)

        Returns information about an authorized user.

        Parameters
        ----------
        expansions : list[str] | str | None
            :ref:`expansions_parameter`
        tweet_fields : list[str] | str | None
            :ref:`tweet_fields_parameter`
        user_fields : list[str] | str | None
            :ref:`user_fields_parameter`
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/users/lookup/api-reference/get-users-me
        """
        return await self._make_request(
            "GET", f"/2/users/me", params=params,
            endpoint_parameters=("expansions", "tweet.fields", "user.fields"),
            data_type=User, user_auth=user_auth
        )

    # Search Spaces

    async def search_spaces(self, query, **params):
        """search_spaces(query, *, expansions=None, max_results=None, \
                         space_fields=None, state=None, user_fields=None)

        Return live or scheduled Spaces matching your specified search terms

        Parameters
        ----------
        query : str
            Your search term. This can be any text (including mentions and
            Hashtags) present in the title of the Space.
        expansions : list[str] | str | None
            :ref:`expansions_parameter`
        max_results : int | None
            The maximum number of results to return in this request. Specify a
            value between 1 and 100.
        space_fields : list[str] | str | None
            :ref:`space_fields_parameter`
        state : str | None
            Determines the type of results to return. This endpoint returns all
            Spaces by default. Use ``live`` to only return live Spaces or
            ``scheduled`` to only return upcoming Spaces.
        user_fields : list[str] | str | None
            :ref:`user_fields_parameter`

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/spaces/search/api-reference/get-spaces-search
        """
        params["query"] = query
        return await self._make_request(
            "GET", "/2/spaces/search", params=params,
            endpoint_parameters=(
                "query", "expansions", "max_results", "space.fields", "state",
                "user.fields"
            ), data_type=Space
        )

    # Spaces lookup

    async def get_spaces(self, *, ids=None, user_ids=None, **params):
        """get_spaces(*, ids=None, user_ids=None, expansions=None, \
                      space_fields=None, user_fields=None)

        Returns details about multiple live or scheduled Spaces (created by the
        specified user IDs if specified). Up to 100 comma-separated Space or
        user IDs can be looked up using this endpoint.

        Parameters
        ----------
        ids : list[str] | str | None
            A comma separated list of Spaces (up to 100).
        user_ids : list[int | str] | str | None
            A comma separated list of user IDs (up to 100).
        expansions : list[str] | str | None
            :ref:`expansions_parameter`
        space_fields : list[str] | str | None
            :ref:`space_fields_parameter`
        user_fields : list[str] | str | None
            :ref:`user_fields_parameter`

        Raises
        ------
        TypeError
            If IDs and user IDs are not passed or both are passed

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/spaces/lookup/api-reference/get-spaces
        https://developer.twitter.com/en/docs/twitter-api/spaces/lookup/api-reference/get-spaces-by-creator-ids
        """
        if ids is not None and user_ids is not None:
            raise TypeError("Expected IDs or user IDs, not both")

        route = "/2/spaces"

        if ids is not None:
            params["ids"] = ids
        elif user_ids is not None:
            route += "/by/creator_ids"
            params["user_ids"] = user_ids
        else:
            raise TypeError("IDs or user IDs are required")

        return await self._make_request(
            "GET", route, params=params,
            endpoint_parameters=(
                "ids", "user_ids", "expansions", "space.fields", "user.fields"
            ), data_type=Space
        )

    async def get_space(self, id, **params):
        """get_space(id, *, expansions=None, space_fields=None, \
                     user_fields=None)

        Returns a variety of information about a single Space specified by the
        requested ID.

        Parameters
        ----------
        id : list[str] | str
            Unique identifier of the Space to request.
        expansions : list[str] | str | None
            :ref:`expansions_parameter`
        space_fields : list[str] | str | None
            :ref:`space_fields_parameter`
        user_fields : list[str] | str | None
            :ref:`user_fields_parameter`

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/spaces/lookup/api-reference/get-spaces-id
        """
        return await self._make_request(
            "GET", f"/2/spaces/{id}", params=params,
            endpoint_parameters=(
                "expansions", "space.fields", "user.fields"
            ), data_type=Space
        )

    async def get_space_buyers(self, id, **params):
        """get_space_buyers( \
            id, *, expansions=None, media_fields=None, place_fields=None, \
            poll_fields=None, tweet_fields=None, user_fields=None \
        )

        Returns a list of user who purchased a ticket to the requested Space.
        You must authenticate the request using the Access Token of the creator
        of the requested Space.

        Parameters
        ----------
        id : str
            Unique identifier of the Space for which you want to request
            Tweets.
        expansions : list[str] | str | None
            :ref:`expansions_parameter`
        media_fields : list[str] | str | None
            :ref:`media_fields_parameter`
        place_fields : list[str] | str | None
            :ref:`place_fields_parameter`
        poll_fields : list[str] | str | None
            :ref:`poll_fields_parameter`
        tweet_fields : list[str] | str | None
            :ref:`tweet_fields_parameter`
        user_fields : list[str] | str | None
            :ref:`user_fields_parameter`

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/spaces/lookup/api-reference/get-spaces-id-buyers
        """
        return await self._make_request(
            "GET", f"/2/spaces/{id}/buyers", params=params,
            endpoint_parameters=(
                "expansions", "media.fields", "place.fields", "poll.fields",
                "tweet.fields", "user.fields"
            ), data_type=User
        )

    async def get_space_tweets(self, id, **params):
        """get_space_tweets( \
            id, *, expansions=None, media_fields=None, place_fields=None, \
            poll_fields=None, tweet_fields=None, user_fields=None \
        )

        Returns Tweets shared in the requested Spaces.

        Parameters
        ----------
        id : str
            Unique identifier of the Space containing the Tweets you'd like to
            access.
        expansions : list[str] | str | None
            :ref:`expansions_parameter`
        media_fields : list[str] | str | None
            :ref:`media_fields_parameter`
        place_fields : list[str] | str | None
            :ref:`place_fields_parameter`
        poll_fields : list[str] | str | None
            :ref:`poll_fields_parameter`
        tweet_fields : list[str] | str | None
            :ref:`tweet_fields_parameter`
        user_fields : list[str] | str | None
            :ref:`user_fields_parameter`

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/spaces/lookup/api-reference/get-spaces-id-tweets
        """
        return await self._make_request(
            "GET", f"/2/spaces/{id}/tweets", params=params,
            endpoint_parameters=(
                "expansions", "media.fields", "place.fields", "poll.fields",
                "tweet.fields", "user.fields"
            ), data_type=Tweet
        )

    # Direct Messages lookup

    async def get_direct_message_events(
        self, *, dm_conversation_id=None, participant_id=None, user_auth=True,
        **params
    ):
        """get_direct_message_events( \
            *, dm_conversation_id=None, participant_id=None, \
            dm_event_fields=None, event_types=None, expansions=None, \
            max_results=None, media_fields=None, pagination_token=None, \
            tweet_fields=None, user_fields=None, user_auth=True \
        )

        If ``dm_conversation_id`` is passed, returns a list of Direct Messages
        within the conversation specified. Messages are returned in reverse
        chronological order.

        If ``participant_id`` is passed, returns a list of Direct Messages (DM)
        events within a 1-1 conversation with the user specified. Messages are
        returned in reverse chronological order.

        If neither is passed, returns a list of Direct Messages for the
        authenticated user, both sent and received. Direct Message events are
        returned in reverse chronological order. Supports retrieving events
        from the previous 30 days.

        .. note::
        
            There is an alias for this method named ``get_dm_events``.

        .. versionadded:: 4.12

        Parameters
        ----------
        dm_conversation_id : str | None
            The ``id`` of the Direct Message conversation for which events are
            being retrieved.
        participant_id : int | str | None
            The ``participant_id`` of the user that the authenicating user is
            having a 1-1 conversation with.
        dm_event_fields : list[str] | str | None
            Extra fields to include in the event payload. ``id`` and
            ``event_type`` are returned by default. The ``text`` value isn't
            included for ``ParticipantsJoin`` and ``ParticipantsLeave`` events.
        event_types : str
            The type of Direct Message event to returm. If not included, all
            types are returned.
        expansions : list[str] | str | None
            :ref:`expansions_parameter`
        max_results : int | None
            The maximum number of results to be returned in a page. Must be
            between 1 and 100. The default is 100.
        media_fields : list[str] | str | None
            :ref:`media_fields_parameter`
        pagination_token : str | None
            Contains either the ``next_token`` or ``previous_token`` value.
        tweet_fields : list[str] | str | None
            :ref:`tweet_fields_parameter`
        user_fields : list[str] | str | None
            :ref:`user_fields_parameter`
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Raises
        ------
        TypeError
            If both ``dm_conversation_id`` and ``participant_id`` are passed

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/direct-messages/lookup/api-reference/get-dm_events
        https://developer.twitter.com/en/docs/twitter-api/direct-messages/lookup/api-reference/get-dm_conversations-with-participant_id-dm_events
        https://developer.twitter.com/en/docs/twitter-api/direct-messages/lookup/api-reference/get-dm_conversations-dm_conversation_id-dm_events
        """
        if dm_conversation_id is not None and participant_id is not None:
            raise TypeError(
                "Expected DM conversation ID or participant ID, not both"
            )
        elif dm_conversation_id is not None:
            path = f"/2/dm_conversations/{dm_conversation_id}/dm_events"
        elif participant_id is not None:
            path = f"/2/dm_conversations/with/{participant_id}/dm_events"
        else:
            path = "/2/dm_events"

        return await self._make_request(
            "GET", path, params=params,
            endpoint_parameters=(
                "dm_event.fields", "event_types", "expansions", "max_results",
                "media.fields", "pagination_token", "tweet.fields",
                "user.fields"
            ), data_type=DirectMessageEvent, user_auth=user_auth
        )

    get_dm_events = get_direct_message_events

    # Manage Direct Messages

    async def create_direct_message(
        self, *, dm_conversation_id=None, participant_id=None, media_id=None,
        text=None, user_auth=True
    ):
        """If ``dm_conversation_id`` is passed, creates a Direct Message on
        behalf of the authenticated user, and adds it to the specified
        conversation.

        If ``participant_id`` is passed, creates a one-to-one Direct Message
        and adds it to the one-to-one conversation. This method either creates
        a new one-to-one conversation or retrieves the current conversation and
        adds the Direct Message to it.

        .. note::
        
            There is an alias for this method named ``create_dm``.

        .. versionadded:: 4.12

        Parameters
        ----------
        dm_conversation_id : str | None
            The ``dm_conversation_id`` of the conversation to add the Direct
            Message to. Supports both 1-1 and group conversations.
        participant_id : int | str | None
            The User ID of the account this one-to-one Direct Message is to be
            sent to.
        media_id : int | str | None
            A single Media ID being attached to the Direct Message. This field
            is required if ``text`` is not present. For this launch, only 1
            attachment is supported.
        text : str | None
            Text of the Direct Message being created. This field is required if
            ``media_id`` is not present. Text messages support up to 10,000
            characters.
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Raises
        ------
        TypeError
            If ``dm_conversation_id`` and ``participant_id`` are not passed or
            both are passed

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/direct-messages/manage/api-reference/post-dm_conversations-dm_conversation_id-messages
        https://developer.twitter.com/en/docs/twitter-api/direct-messages/manage/api-reference/post-dm_conversations-with-participant_id-messages
        """
        if dm_conversation_id is not None and participant_id is not None:
            raise TypeError(
                "Expected DM conversation ID or participant ID, not both"
            )
        elif dm_conversation_id is not None:
            path = f"/2/dm_conversations/{dm_conversation_id}/messages"
        elif participant_id is not None:
            path = f"/2/dm_conversations/with/{participant_id}/messages"
        else:
            raise TypeError("DM conversation ID or participant ID is required")

        json = {}
        if media_id is not None:
            json["attachments"] = [{"media_id": str(media_id)}]
        if text is not None:
            json["text"] = text

        return await self._make_request(
            "POST", path, json=json, user_auth=user_auth
        )

    create_dm = create_direct_message

    async def create_direct_message_conversation(
        self, *, media_id=None, text=None, participant_ids, user_auth=True
    ):
        """Creates a new group conversation and adds a Direct Message to it on
        behalf of the authenticated user.

        .. note::
        
            There is an alias for this method named ``create_dm_conversation``.

        .. versionadded:: 4.12

        Parameters
        ----------
        media_id : int | str | None
            A single Media ID being attached to the Direct Message. This field
            is required if ``text`` is not present. For this launch, only 1
            attachment is supported.
        text : str | None
            Text of the Direct Message being created. This field is required if
            ``media_id`` is not present. Text messages support up to 10,000
            characters.
        participant_ids : list[int | str]
            An array of User IDs that the conversation is created with.
            Conversations can have up to 50 participants.
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/direct-messages/manage/api-reference/post-dm_conversations
        """
        json = {
            "conversation_type": "Group",
            "message": {},
            "participant_ids": list(map(str, participant_ids))
        }
        if media_id is not None:
            json["message"]["attachments"] = [{"media_id": str(media_id)}]
        if text is not None:
            json["message"]["text"] = text

        return await self._make_request(
            "POST", "/2/dm_conversations", json=json, user_auth=user_auth
        )

    create_dm_conversation = create_direct_message_conversation

    # List Tweets lookup

    async def get_list_tweets(self, id, *, user_auth=False, **params):
        """get_list_tweets( \
            id, *, expansions=None, max_results=None, media_fields=None, \
            pagination_token=None, place_fields=None, poll_fields=None, \
            tweet_fields=None, user_fields=None, user_auth=False \
        )

        Returns a list of Tweets from the specified List.

        .. versionchanged:: 4.10.1
            Added ``media_fields``, ``place_fields``, and ``poll_fields``
            parameters

        Parameters
        ----------
        id : list[str] | str
            The ID of the List whose Tweets you would like to retrieve.
        expansions : list[str] | str | None
            :ref:`expansions_parameter`
        max_results : int | None
            The maximum number of results to be returned per page. This can be
            a number between 1 and 100. By default, each page will return 100
            results.
        media_fields : list[str] | str | None
            :ref:`media_fields_parameter`
        pagination_token : str | None
            Used to request the next page of results if all results weren't
            returned with the latest request, or to go back to the previous
            page of results. To return the next page, pass the next_token
            returned in your previous response. To go back one page, pass the
            previous_token returned in your previous response.
        place_fields : list[str] | str | None
            :ref:`place_fields_parameter`
        poll_fields : list[str] | str | None
            :ref:`poll_fields_parameter`
        tweet_fields : list[str] | str | None
            :ref:`tweet_fields_parameter`
        user_fields : list[str] | str | None
            :ref:`user_fields_parameter`
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/lists/list-tweets/api-reference/get-lists-id-tweets
        """
        return await self._make_request(
            "GET", f"/2/lists/{id}/tweets", params=params,
            endpoint_parameters=(
                "expansions", "max_results", "media.fields",
                "pagination_token", "place.fields", "poll.fields",
                "tweet.fields", "user.fields"
            ), data_type=Tweet, user_auth=user_auth
        )

    # List follows

    async def unfollow_list(self, list_id, *, user_auth=True):
        """Enables the authenticated user to unfollow a List.

        .. note::

            When using OAuth 2.0 Authorization Code Flow with PKCE with
            ``user_auth=False``, a request is made beforehand to Twitter's API
            to determine the authenticating user's ID. This is cached and only
            done once per :class:`AsyncClient` instance for each access token
            used.

        Parameters
        ----------
        list_id : int | str
            The ID of the List that you would like the user to unfollow.
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Raises
        ------
        TypeError
            If the access token isn't set

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/lists/list-follows/api-reference/delete-users-id-followed-lists-list_id
        """
        id = await self._get_authenticating_user_id(oauth_1=user_auth)
        route = f"/2/users/{id}/followed_lists/{list_id}"

        return await self._make_request(
            "DELETE", route, user_auth=user_auth
        )

    async def get_list_followers(self, id, *, user_auth=False, **params):
        """get_list_followers( \
            id, *, expansions=None, max_results=None, pagination_token=None, \
            tweet_fields=None, user_fields=None, user_auth=False \
        )

        Returns a list of users who are followers of the specified List.

        .. note::

            The Twitter API endpoint that this method uses has been removed
            from the Basic and Pro tiers [#changelog]_.

        Parameters
        ----------
        id : list[str] | str
            The ID of the List whose followers you would like to retrieve.
        expansions : list[str] | str | None
            :ref:`expansions_parameter`
        max_results : int | None
            The maximum number of results to be returned per page. This can be
            a number between 1 and 100. By default, each page will return 100
            results.
        pagination_token : str | None
            Used to request the next page of results if all results weren't
            returned with the latest request, or to go back to the previous
            page of results. To return the next page, pass the next_token
            returned in your previous response. To go back one page, pass the
            previous_token returned in your previous response.
        tweet_fields : list[str] | str | None
            :ref:`tweet_fields_parameter`
        user_fields : list[str] | str | None
            :ref:`user_fields_parameter`
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/lists/list-follows/api-reference/get-lists-id-followers
        """
        return await self._make_request(
            "GET", f"/2/lists/{id}/followers", params=params,
            endpoint_parameters=(
                "expansions", "max_results", "pagination_token",
                "tweet.fields", "user.fields"
            ), data_type=User, user_auth=user_auth
        )

    async def get_followed_lists(self, id, *, user_auth=False, **params):
        """get_followed_lists( \
            id, *, expansions=None, list_fields=None, max_results=None, \
            pagination_token=None, user_fields=None, user_auth=False \
        )

        Returns all Lists a specified user follows.

        .. note::

            The Twitter API endpoint that this method uses has been removed
            from the Basic and Pro tiers [#changelog]_.

        Parameters
        ----------
        id : list[str] | str
            The user ID whose followed Lists you would like to retrieve.
        expansions : list[str] | str | None
            :ref:`expansions_parameter`
        list_fields : list[str] | str | None
            :ref:`list_fields_parameter`
        max_results : int | None
            The maximum number of results to be returned per page. This can be
            a number between 1 and 100. By default, each page will return 100
            results.
        pagination_token : str | None
            Used to request the next page of results if all results weren't
            returned with the latest request, or to go back to the previous
            page of results. To return the next page, pass the next_token
            returned in your previous response. To go back one page, pass the
            previous_token returned in your previous response.
        user_fields : list[str] | str | None
            :ref:`user_fields_parameter`
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/lists/list-follows/api-reference/get-users-id-followed_lists
        """
        return await self._make_request(
            "GET", f"/2/users/{id}/followed_lists", params=params,
            endpoint_parameters=(
                "expansions", "list.fields", "max_results", "pagination_token",
                "user.fields"
            ), data_type=List, user_auth=user_auth
        )

    async def follow_list(self, list_id, *, user_auth=True):
        """Enables the authenticated user to follow a List.

        .. note::

            When using OAuth 2.0 Authorization Code Flow with PKCE with
            ``user_auth=False``, a request is made beforehand to Twitter's API
            to determine the authenticating user's ID. This is cached and only
            done once per :class:`AsyncClient` instance for each access token
            used.

        Parameters
        ----------
        list_id : int | str
            The ID of the List that you would like the user to follow.
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Raises
        ------
        TypeError
            If the access token isn't set

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/lists/list-follows/api-reference/post-users-id-followed-lists
        """
        id = await self._get_authenticating_user_id(oauth_1=user_auth)
        route = f"/2/users/{id}/followed_lists"

        return await self._make_request(
            "POST", route, json={"list_id": str(list_id)}, user_auth=user_auth
        )

    # List lookup

    async def get_list(self, id, *, user_auth=False, **params):
        """get_list(id, *, expansions=None, list_fields=None, \
                    user_fields=None, user_auth=False)

        Returns the details of a specified List.

        Parameters
        ----------
        id : list[str] | str
            The ID of the List to lookup.
        expansions : list[str] | str | None
            :ref:`expansions_parameter`
        list_fields : list[str] | str | None
            :ref:`list_fields_parameter`
        user_fields : list[str] | str | None
            :ref:`user_fields_parameter`
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/lists/list-lookup/api-reference/get-lists-id
        """
        return await self._make_request(
            "GET", f"/2/lists/{id}", params=params,
            endpoint_parameters=(
                "expansions", "list.fields", "user.fields"
            ), data_type=List, user_auth=user_auth
        )

    async def get_owned_lists(self, id, *, user_auth=False, **params):
        """get_owned_lists( \
            id, *, expansions=None, list_fields=None, max_results=None, \
            pagination_token=None, user_fields=None, user_auth=False \
        )

        Returns all Lists owned by the specified user.

        Parameters
        ----------
        id : list[str] | str
            The user ID whose owned Lists you would like to retrieve.
        expansions : list[str] | str | None
            :ref:`expansions_parameter`
        list_fields : list[str] | str | None
            :ref:`list_fields_parameter`
        max_results : int | None
            The maximum number of results to be returned per page. This can be
            a number between 1 and 100. By default, each page will return 100
            results.
        pagination_token : str | None
            Used to request the next page of results if all results weren't
            returned with the latest request, or to go back to the previous
            page of results. To return the next page, pass the next_token
            returned in your previous response. To go back one page, pass the
            previous_token returned in your previous response.
        user_fields : list[str] | str | None
            :ref:`user_fields_parameter`
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/lists/list-lookup/api-reference/get-users-id-owned_lists
        """
        return await self._make_request(
            "GET", f"/2/users/{id}/owned_lists", params=params,
            endpoint_parameters=(
                "expansions", "list.fields", "max_results", "pagination_token",
                "user.fields"
            ), data_type=List, user_auth=user_auth
        )

    # List members

    async def remove_list_member(self, id, user_id, *, user_auth=True):
        """Enables the authenticated user to remove a member from a List they
        own.

        Parameters
        ----------
        id : int | str
            The ID of the List you are removing a member from.
        user_id : int | str
            The ID of the user you wish to remove as a member of the List.
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/lists/list-members/api-reference/delete-lists-id-members-user_id
        """

        return await self._make_request(
            "DELETE", f"/2/lists/{id}/members/{user_id}", user_auth=user_auth
        )

    async def get_list_members(self, id, *, user_auth=False, **params):
        """get_list_members( \
            id, *, expansions=None, max_results=None, pagination_token=None, \
            tweet_fields=None, user_fields=None, user_auth=False \
        )

        Returns a list of users who are members of the specified List.

        Parameters
        ----------
        id : list[str] | str
            The ID of the List whose members you would like to retrieve.
        expansions : list[str] | str | None
            :ref:`expansions_parameter`
        max_results : int | None
            The maximum number of results to be returned per page. This can be
            a number between 1 and 100. By default, each page will return 100
            results.
        pagination_token : str | None
            Used to request the next page of results if all results weren't
            returned with the latest request, or to go back to the previous
            page of results. To return the next page, pass the next_token
            returned in your previous response. To go back one page, pass the
            previous_token returned in your previous response.
        tweet_fields : list[str] | str | None
            :ref:`tweet_fields_parameter`
        user_fields : list[str] | str | None
            :ref:`user_fields_parameter`
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/lists/list-members/api-reference/get-lists-id-members
        """
        return await self._make_request(
            "GET", f"/2/lists/{id}/members", params=params,
            endpoint_parameters=(
                "expansions", "max_results", "pagination_token",
                "tweet.fields", "user.fields"
            ), data_type=User, user_auth=user_auth
        )

    async def get_list_memberships(self, id, *, user_auth=False, **params):
        """get_list_memberships( \
            id, *, expansions=None, list_fields=None, max_results=None, \
            pagination_token=None, user_fields=None, user_auth=False \
        )

        Returns all Lists a specified user is a member of.

        Parameters
        ----------
        id : list[str] | str
            The user ID whose List memberships you would like to retrieve.
        expansions : list[str] | str | None
            :ref:`expansions_parameter`
        list_fields : list[str] | str | None
            :ref:`list_fields_parameter`
        max_results : int | None
            The maximum number of results to be returned per page. This can be
            a number between 1 and 100. By default, each page will return 100
            results.
        pagination_token : str | None
            Used to request the next page of results if all results weren't
            returned with the latest request, or to go back to the previous
            page of results. To return the next page, pass the next_token
            returned in your previous response. To go back one page, pass the
            previous_token returned in your previous response.
        user_fields : list[str] | str | None
            :ref:`user_fields_parameter`
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/lists/list-members/api-reference/get-users-id-list_memberships
        """
        return await self._make_request(
            "GET", f"/2/users/{id}/list_memberships", params=params,
            endpoint_parameters=(
                "expansions", "list.fields", "max_results", "pagination_token",
                "user.fields"
            ), data_type=List, user_auth=user_auth
        )

    async def add_list_member(self, id, user_id, *, user_auth=True):
        """Enables the authenticated user to add a member to a List they own.

        Parameters
        ----------
        id : int | str
            The ID of the List you are adding a member to.
        user_id : int | str
            The ID of the user you wish to add as a member of the List.
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/lists/list-members/api-reference/post-lists-id-members
        """
        return await self._make_request(
            "POST", f"/2/lists/{id}/members", json={"user_id": str(user_id)},
            user_auth=user_auth
        )

    # Manage Lists

    async def delete_list(self, id, *, user_auth=True):
        """Enables the authenticated user to delete a List that they own.

        Parameters
        ----------
        id : int | str
            The ID of the List to be deleted.
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/lists/manage-lists/api-reference/delete-lists-id
        """

        return await self._make_request(
            "DELETE", f"/2/lists/{id}", user_auth=user_auth
        )

    async def update_list(self, id, *, description=None, name=None,
                          private=None, user_auth=True):
        """Enables the authenticated user to update the meta data of a
        specified List that they own.

        Parameters
        ----------
        id : int | str
            The ID of the List to be updated.
        description : str | None
            Updates the description of the List.
        name : str | None
            Updates the name of the List.
        private : bool | None
            Determines whether the List should be private.
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/lists/manage-lists/api-reference/put-lists-id
        """
        json = {}

        if description is not None:
            json["description"] = description

        if name is not None:
            json["name"] = name

        if private is not None:
            json["private"] = private

        return await self._make_request(
            "PUT", f"/2/lists/{id}", json=json, user_auth=user_auth
        )

    async def create_list(self, name, *, description=None, private=None,
                          user_auth=True):
        """Enables the authenticated user to create a List.

        Parameters
        ----------
        name : str
            The name of the List you wish to create.
        description : str | None
            Description of the List.
        private : bool | None
            Determine whether the List should be private.
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/lists/manage-lists/api-reference/post-lists
        """
        json = {"name": name}

        if description is not None:
            json["description"] = description

        if private is not None:
            json["private"] = private

        return await self._make_request(
            "POST", f"/2/lists", json=json, user_auth=user_auth
        )

    # Pinned Lists

    async def unpin_list(self, list_id, *, user_auth=True):
        """Enables the authenticated user to unpin a List.

        .. note::

            When using OAuth 2.0 Authorization Code Flow with PKCE with
            ``user_auth=False``, a request is made beforehand to Twitter's API
            to determine the authenticating user's ID. This is cached and only
            done once per :class:`AsyncClient` instance for each access token
            used.

        Parameters
        ----------
        list_id : int | str
            The ID of the List that you would like the user to unpin.
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Raises
        ------
        TypeError
            If the access token isn't set

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/lists/pinned-lists/api-reference/delete-users-id-pinned-lists-list_id
        """
        id = await self._get_authenticating_user_id(oauth_1=user_auth)
        route = f"/2/users/{id}/pinned_lists/{list_id}"

        return await self._make_request(
            "DELETE", route, user_auth=user_auth
        )

    async def get_pinned_lists(self, *, user_auth=True, **params):
        """get_pinned_lists(*, expansions=None, list_fields=None, \
                            user_fields=None, user_auth=True)

        Returns the Lists pinned by a specified user.

        .. note::

            When using OAuth 2.0 Authorization Code Flow with PKCE with
            ``user_auth=False``, a request is made beforehand to Twitter's API
            to determine the authenticating user's ID. This is cached and only
            done once per :class:`AsyncClient` instance for each access token
            used.

        Parameters
        ----------
        expansions : list[str] | str | None
            :ref:`expansions_parameter`
        list_fields : list[str] | str | None
            :ref:`list_fields_parameter`
        user_fields : list[str] | str | None
            :ref:`user_fields_parameter`
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Raises
        ------
        TypeError
            If the access token isn't set

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/lists/pinned-lists/api-reference/get-users-id-pinned_lists
        """
        id = await self._get_authenticating_user_id(oauth_1=user_auth)
        route = f"/2/users/{id}/pinned_lists"

        return await self._make_request(
            "GET", route, params=params,
            endpoint_parameters=(
                "expansions", "list.fields", "user.fields"
            ), data_type=List, user_auth=user_auth
        )

    async def pin_list(self, list_id, *, user_auth=True):
        """Enables the authenticated user to pin a List.

        .. note::

            When using OAuth 2.0 Authorization Code Flow with PKCE with
            ``user_auth=False``, a request is made beforehand to Twitter's API
            to determine the authenticating user's ID. This is cached and only
            done once per :class:`AsyncClient` instance for each access token
            used.

        Parameters
        ----------
        list_id : int | str
            The ID of the List that you would like the user to pin.
        user_auth : bool
            Whether or not to use OAuth 1.0a User Context to authenticate

        Raises
        ------
        TypeError
            If the access token isn't set

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/lists/pinned-lists/api-reference/post-users-id-pinned-lists
        """
        id = await self._get_authenticating_user_id(oauth_1=user_auth)
        route = f"/2/users/{id}/pinned_lists"

        return await self._make_request(
            "POST", route, json={"list_id": str(list_id)}, user_auth=user_auth
        )

    # Batch Compliance

    async def get_compliance_jobs(self, type, **params):
        """get_compliance_jobs(type, *, status=None)

        Returns a list of recent compliance jobs.

        Parameters
        ----------
        type : str
            Allows to filter by job type - either by tweets or user ID. Only
            one filter (tweets or users) can be specified per request.
        status : str | None
            Allows to filter by job status. Only one filter can be specified
            per request.
            Default: ``all``

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/compliance/batch-compliance/api-reference/get-compliance-jobs
        """
        params["type"] = type
        return await self._make_request(
            "GET", "/2/compliance/jobs", params=params,
            endpoint_parameters=("type", "status")
        )

    async def get_compliance_job(self, id):
        """Get a single compliance job with the specified ID.

        Parameters
        ----------
        id : int | str
            The unique identifier for the compliance job you want to retrieve.

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/compliance/batch-compliance/api-reference/get-compliance-jobs-id
        """
        return await self._make_request(
            "GET", f"/2/compliance/jobs/{id}"
        )

    async def create_compliance_job(self, type, *, name=None, resumable=None):
        """Creates a new compliance job for Tweet IDs or user IDs.

        A compliance job will contain an ID and a destination URL. The
        destination URL represents the location that contains the list of IDs
        consumed by your app.

        You can run one batch job at a time.

        Parameters
        ----------
        type : str
            Specify whether you will be uploading tweet or user IDs. You can
            either specify tweets or users.
        name : str | None
            A name for this job, useful to identify multiple jobs using a label
            you define.
        resumable : bool | None
            Specifies whether to enable the upload URL with support for
            resumable uploads. If true, this endpoint will return a pre-signed
            URL with resumable uploads enabled.

        Returns
        -------
        dict | aiohttp.ClientResponse | Response

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/compliance/batch-compliance/api-reference/post-compliance-jobs
        """
        json = {"type": type}

        if name is not None:
            json["name"] = name

        if resumable is not None:
            json["resumable"] = resumable

        return await self._make_request(
            "POST", "/2/compliance/jobs", json=json
        )
