# Tweepy
# Copyright 2009-2021 Joshua Roesslein
# See LICENSE for details.

from collections import namedtuple
import datetime
import logging
from platform import python_version
import time

import requests

import tweepy
from tweepy.auth import OAuthHandler
from tweepy.errors import (
    BadRequest, Forbidden, HTTPException, TooManyRequests, TwitterServerError,
    Unauthorized
)
from tweepy.media import Media
from tweepy.place import Place
from tweepy.poll import Poll
from tweepy.tweet import Tweet
from tweepy.user import User

log = logging.getLogger(__name__)

Response = namedtuple("Response", ("data", "includes", "errors", "meta"))


class Client:
    """Client( \
        bearer_token=None, consumer_key=None, consumer_secret=None, \
        access_token=None, access_token_secret=None, *, return_type=Response, \
        wait_on_rate_limit=False \
    )

    Twitter API v2 Client

    Parameters
    ----------
    bearer_token : Optional[str]
        Twitter API Bearer Token
    consumer_key : Optional[str]
        Twitter API Consumer Key
    consumer_secret : Optional[str]
        Twitter API Consumer Secret
    access_token : Optional[str]
        Twitter API Access Token
    access_token_secret : Optional[str]
        Twitter API Access Token Secret
    return_type : Type[dict, requests.Response, Response]
        Type to return from requests to the API
    wait_on_rate_limit : bool
        Whether to wait when rate limit is reached

    Attributes
    ----------
    session : requests.Session
        Requests Session used to make requests to the API
    user_agent : str
        User agent used when making requests to the API
    """

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

        self.session = requests.Session()
        self.user_agent = (
            f"Python/{python_version()} "
            f"Requests/{requests.__version__} "
            f"Tweepy/{tweepy.__version__}"
        )

    def request(self, method, route, params=None, json=None, user_auth=False):
        host = "https://api.twitter.com"
        headers = {"User-Agent": self.user_agent}
        auth = None
        if user_auth:
            auth = OAuthHandler(self.consumer_key, self.consumer_secret)
            auth.set_access_token(self.access_token, self.access_token_secret)
            auth = auth.apply_auth()
        else:
            headers["Authorization"] = f"Bearer {self.bearer_token}"

        log.debug(
            f"Making API request: {method} {host + route}\n"
            f"Parameters: {params}\n"
            f"Headers: {headers}\n"
            f"Body: {json}"
        )

        with self.session.request(
            method, host + route, params=params, json=json, headers=headers,
            auth=auth
        ) as response:
            log.debug(
                "Received API response: "
                f"{response.status_code} {response.reason}\n"
                f"Headers: {response.headers}\n"
                f"Content: {response.content}"
            )

            if response.status_code == 400:
                raise BadRequest(response)
            if response.status_code == 401:
                raise Unauthorized(response)
            if response.status_code == 403:
                raise Forbidden(response)
            # Handle 404?
            if response.status_code == 429:
                if self.wait_on_rate_limit:
                    reset_time = int(response.headers["x-rate-limit-reset"])
                    sleep_time = reset_time - int(time.time()) + 1
                    if sleep_time > 0:
                        log.warning(
                            "Rate limit exceeded. "
                            f"Sleeping for {sleep_time} seconds."
                        )
                        time.sleep(sleep_time)
                    return self.request(method, route, params, json, user_auth)
                else:
                    raise TooManyRequests(response)
            if response.status_code >= 500:
                raise TwitterServerError(response)
            if not 200 <= response.status_code < 300:
                raise HTTPException(response)

            return response

    def _make_request(self, method, route, params={}, endpoint_parameters=None,
                      json=None, data_type=None, user_auth=False):
        request_params = {}
        for param_name, param_value in params.items():
            if param_name.replace('_', '.') in endpoint_parameters:
                param_name = param_name.replace('_', '.')

            if isinstance(param_value, list):
                request_params[param_name] = ','.join(map(str, param_value))
            elif isinstance(param_value, datetime.datetime):
                if param_value.tzinfo is not None:
                    param_value = param_value.astimezone(datetime.timezone.utc)
                request_params[param_name] = param_value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                # TODO: Constant datetime format string?
            else:
                request_params[param_name] = param_value

            if param_name not in endpoint_parameters:
                log.warn(f"Unexpected parameter: {param_name}")

        response = self.request(method, route, params=request_params,
                                json=json, user_auth=user_auth)

        if self.return_type is requests.Response:
            return response

        response = response.json()

        if self.return_type is dict:
            return response

        data = response.get("data")
        if data_type is not None:
            if isinstance(data, list):
                data = [data_type(result) for result in data]
            elif data is not None:
                data = data_type(data)

        includes = response.get("includes", {})
        if "media" in includes:
            includes["media"] = [Media(media) for media in includes["media"]]
        if "places" in includes:
            includes["places"] = [Place(place) for place in includes["places"]]
        if "poll" in includes:
            includes["polls"] = [Poll(poll) for poll in includes["polls"]]
        if "tweets" in includes:
            includes["tweets"] = [Tweet(tweet) for tweet in includes["tweets"]]
        if "users" in includes:
            includes["users"] = [User(user) for user in includes["users"]]

        errors = response.get("errors", [])
        meta = response.get("meta", {})

        return Response(data, includes, errors, meta)

    # Hide replies

    def hide_reply(self, id):
        """Hides a reply to a Tweet.

        Parameters
        ----------
        id : Union[int, str]
            Unique identifier of the Tweet to hide. The Tweet must belong to a
            conversation initiated by the authenticating user.

        Returns
        -------
        Union[dict, requests.Response, Response]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/hide-replies/api-reference/put-tweets-id-hidden
        """
        return self._make_request(
            "PUT", f"/2/tweets/{id}/hidden", json={"hidden": True},
            user_auth=True
        )

    def unhide_reply(self, id):
        """Unhides a reply to a Tweet.

        Parameters
        ----------
        id : Union[int, str]
            Unique identifier of the Tweet to unhide. The Tweet must belong to
            a conversation initiated by the authenticating user.

        Returns
        -------
        Union[dict, requests.Response, Response]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/hide-replies/api-reference/put-tweets-id-hidden
        """
        return self._make_request(
            "PUT", f"/2/tweets/{id}/hidden", json={"hidden": False},
            user_auth=True
        )

    # Likes

    def unlike(self, tweet_id):
        """Unlike a Tweet.

        The request succeeds with no action when the user sends a request to a
        user they're not liking the Tweet or have already unliked the Tweet.

        Parameters
        ----------
        tweet_id : Union[int, str]
            The ID of the Tweet that you would like to unlike.

        Returns
        -------
        Union[dict, requests.Response, Response]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/likes/api-reference/delete-users-user_id-likes
        """
        id = self.access_token.partition('-')[0]
        route = f"/2/users/{id}/likes/{tweet_id}"

        return self._make_request("DELETE", route, user_auth=True)

    def get_liking_users(self, id, *, user_auth=False, **params):
        """get_liking_users(id, *, expansions, media_fields, place_fields, \
                            poll_fields, tweet_fields, user_fields)

        Allows you to get information about a Tweet’s liking users.

        Parameters
        ----------
        id : Union[int, str]
            Tweet ID of the Tweet to request liking users of.
        expansions : Union[List[str], str]
            :ref:`expansions_parameter`
        media_fields : Union[List[str], str]
            :ref:`media_fields_parameter`
        place_fields : Union[List[str], str]
            :ref:`place_fields_parameter`
        poll_fields : Union[List[str], str]
            :ref:`poll_fields_parameter`
        tweet_fields : Union[List[str], str]
            :ref:`tweet_fields_parameter`
        user_fields : Union[List[str], str]
            :ref:`user_fields_parameter`

        Returns
        -------
        Union[dict, requests.Response, Response]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/likes/api-reference/get-tweets-id-liking_users
        """
        return self._make_request(
            "GET", f"/2/tweets/{id}/liking_users", params=params,
            endpoint_parameters=(
                "expansions", "media.fields", "place.fields", "poll.fields",
                "tweet.fields", "user.fields"
            ), data_type=User, user_auth=user_auth
        )

    def get_liked_tweets(self, id, *, user_auth=False, **params):
        """get_liked_tweets( \
            id, *, expansions, max_results, media_fields, pagination_token, \
            place_fields, poll_fields, tweet_fields, user_fields \
        )

        Allows you to get information about a user’s liked Tweets.

        The Tweets returned by this endpoint count towards the Project-level
        `Tweet cap`_.

        Parameters
        ----------
        id : Union[int, str]
            User ID of the user to request liked Tweets for.
        expansions : Union[List[str], str]
            :ref:`expansions_parameter`
        max_results : int
            The maximum number of results to be returned per page. This can be
            a number between 5 and 100. By default, each page will return 100
            results.
        media_fields : Union[List[str], str]
            :ref:`media_fields_parameter`
        pagination_token : str
            Used to request the next page of results if all results weren't
            returned with the latest request, or to go back to the previous
            page of results. To return the next page, pass the ``next_token``
            returned in your previous response. To go back one page, pass the
            ``previous_token`` returned in your previous response.
        place_fields : Union[List[str], str]
            :ref:`place_fields_parameter`
        poll_fields : Union[List[str], str]
            :ref:`poll_fields_parameter`
        tweet_fields : Union[List[str], str]
            :ref:`tweet_fields_parameter`
        user_fields : Union[List[str], str]
            :ref:`user_fields_parameter`

        Returns
        -------
        Union[dict, requests.Response, Response]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/likes/api-reference/get-users-id-liked_tweets

        .. _Tweet cap: https://developer.twitter.com/en/docs/projects/overview#tweet-cap
        """
        return self._make_request(
            "GET", f"/2/users/{id}/liked_tweets", params=params,
            endpoint_parameters=(
                "expansions", "max_results", "media.fields",
                "pagination_token", "place.fields", "poll.fields",
                "tweet.fields", "user.fields"
            ), data_type=Tweet, user_auth=user_auth
        )

    def like(self, tweet_id):
        """Like a Tweet.

        Parameters
        ----------
        tweet_id : Union[int, str]
            The ID of the Tweet that you would like to Like.

        Returns
        -------
        Union[dict, requests.Response, Response]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/likes/api-reference/post-users-user_id-likes
        """
        id = self.access_token.partition('-')[0]
        route = f"/2/users/{id}/likes"

        return self._make_request(
            "POST", route, json={"tweet_id": str(tweet_id)}, user_auth=True
        )

    # Retweets

    def unretweet(self, source_tweet_id):
        """Allows an authenticated user ID to remove the Retweet of a Tweet.

        The request succeeds with no action when the user sends a request to a
        user they're not Retweeting the Tweet or have already removed the
        Retweet of.

        Parameters
        ----------
        source_tweet_id : Union[int, str]
            The ID of the Tweet that you would like to remove the Retweet of.

        Returns
        -------
        Union[dict, requests.Response, Response]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/retweets/api-reference/delete-users-id-retweets-tweet_id
        """
        id = self.access_token.partition('-')[0]
        route = f"/2/users/{id}/retweets/{source_tweet_id}"

        return self._make_request("DELETE", route, user_auth=True)

    def get_retweeters(self, id, *, user_auth=False, **params):
        """get_retweeters(id, *, expansions, media_fields, place_fields, \
                          poll_fields, tweet_fields, user_fields)

        Allows you to get information about who has Retweeted a Tweet.

        Parameters
        ----------
        id : Union[int, str]
            Tweet ID of the Tweet to request Retweeting users of.
        expansions : Union[List[str], str]
            :ref:`expansions_parameter`
        media_fields : Union[List[str], str]
            :ref:`media_fields_parameter`
        place_fields : Union[List[str], str]
            :ref:`place_fields_parameter`
        poll_fields : Union[List[str], str]
            :ref:`poll_fields_parameter`
        tweet_fields : Union[List[str], str]
            :ref:`tweet_fields_parameter`
        user_fields : Union[List[str], str]
            :ref:`user_fields_parameter`

        Returns
        -------
        Union[dict, requests.Response, Response]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/retweets/api-reference/get-tweets-id-retweeted_by
        """
        return self._make_request(
            "GET", f"/2/tweets/{id}/retweeted_by", params=params,
            endpoint_parameters=(
                "expansions", "media.fields", "place.fields", "poll.fields",
                "tweet.fields", "user.fields"
            ), data_type=User, user_auth=user_auth
        )

    def retweet(self, tweet_id):
        """Causes the user ID to Retweet the target Tweet.

        Parameters
        ----------
        tweet_id : Union[int, str]
            The ID of the Tweet that you would like to Retweet.

        Returns
        -------
        Union[dict, requests.Response, Response]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/retweets/api-reference/post-users-id-retweets
        """
        id = self.access_token.partition('-')[0]
        route = f"/2/users/{id}/retweets"

        return self._make_request(
            "POST", route, json={"tweet_id": str(tweet_id)}, user_auth=True
        )

    # Search Tweets

    def search_all_tweets(self, query, **params):
        """search_all_tweets( \
            query, *, end_time, expansions, max_results, media_fields, \
            next_token, place_fields, poll_fields, since_id, start_time, \
            tweet_fields, until_id, user_fields \
        )

        This endpoint is only available to those users who have been approved
        for the `Academic Research product track`_.

        The full-archive search endpoint returns the complete history of public
        Tweets matching a search query; since the first Tweet was created March
        26, 2006.

        The Tweets returned by this endpoint count towards the Project-level
        `Tweet cap`_.

        Parameters
        ----------
        query : str
            One query for matching Tweets. Up to 1024 characters.
        end_time : Union[datetime.datetime, str]
            YYYY-MM-DDTHH:mm:ssZ (ISO 8601/RFC 3339). Used with ``start_time``.
            The newest, most recent UTC timestamp to which the Tweets will be
            provided. Timestamp is in second granularity and is exclusive (for
            example, 12:00:01 excludes the first second of the minute). If used
            without ``start_time``, Tweets from 30 days before ``end_time``
            will be returned by default. If not specified, ``end_time`` will
            default to [now - 30 seconds].
        expansions : Union[List[str], str]
            :ref:`expansions_parameter`
        max_results : int
            The maximum number of search results to be returned by a request. A
            number between 10 and the system limit (currently 500). By default,
            a request response will return 10 results.
        media_fields : Union[List[str], str]
            :ref:`media_fields_parameter`
        next_token : str
            This parameter is used to get the next 'page' of results. The value
            used with the parameter is pulled directly from the response
            provided by the API, and should not be modified. You can learn more
            by visiting our page on `pagination`_.
        place_fields : Union[List[str], str]
            :ref:`place_fields_parameter`
        poll_fields : Union[List[str], str]
            :ref:`poll_fields_parameter`
        since_id : Union[int, str]
            Returns results with a Tweet ID greater than (for example, more
            recent than) the specified ID. The ID specified is exclusive and
            responses will not include it. If included with the same request as
            a ``start_time`` parameter, only ``since_id`` will be used.
        start_time : Union[datetime.datetime, str]
            YYYY-MM-DDTHH:mm:ssZ (ISO 8601/RFC 3339). The oldest UTC timestamp
            from which the Tweets will be provided. Timestamp is in second
            granularity and is inclusive (for example, 12:00:01 includes the
            first second of the minute). By default, a request will return
            Tweets from up to 30 days ago if you do not include this parameter.
        tweet_fields : Union[List[str], str]
            :ref:`tweet_fields_parameter`
        until_id : Union[int, str]
            Returns results with a Tweet ID less than (that is, older than) the
            specified ID. Used with ``since_id``. The ID specified is exclusive
            and responses will not include it.
        user_fields : Union[List[str], str]
            :ref:`user_fields_parameter`

        Returns
        -------
        Union[dict, requests.Response, Response]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-all

        .. _Academic Research product track: https://developer.twitter.com/en/docs/projects/overview#product-track
        .. _Tweet cap: https://developer.twitter.com/en/docs/projects/overview#tweet-cap
        .. _pagination: https://developer.twitter.com/en/docs/twitter-api/tweets/search/integrate/paginate
        """
        params["query"] = query
        return self._make_request(
            "GET", "/2/tweets/search/all", params=params,
            endpoint_parameters=(
                "end_time", "expansions", "max_results", "media.fields",
                "next_token", "place.fields", "poll.fields", "query",
                "since_id", "start_time", "tweet.fields", "until_id",
                "user.fields"
            ), data_type=Tweet
        )

    def search_recent_tweets(self, query, *, user_auth=False, **params):
        """search_recent_tweets( \
            query, *, user_auth=False, end_time, expansions, max_results, \
            media_fields, next_token, place_fields, poll_fields, since_id, \
            start_time, tweet_fields, until_id, user_fields \
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
        end_time : Union[datetime.datetime, str]
            YYYY-MM-DDTHH:mm:ssZ (ISO 8601/RFC 3339). The newest, most recent
            UTC timestamp to which the Tweets will be provided. Timestamp is in
            second granularity and is exclusive (for example, 12:00:01 excludes
            the first second of the minute). By default, a request will return
            Tweets from as recent as 30 seconds ago if you do not include this
            parameter.
        expansions : Union[List[str], str]
            :ref:`expansions_parameter`
        max_results : int
            The maximum number of search results to be returned by a request. A
            number between 10 and 100. By default, a request response will
            return 10 results.
        media_fields : Union[List[str], str]
            :ref:`media_fields_parameter`
        next_token : str
            This parameter is used to get the next 'page' of results. The value
            used with the parameter is pulled directly from the response
            provided by the API, and should not be modified.
        place_fields : Union[List[str], str]
            :ref:`place_fields_parameter`
        poll_fields : Union[List[str], str]
            :ref:`poll_fields_parameter`
        since_id : Union[int, str]
            Returns results with a Tweet ID greater than (that is, more recent
            than) the specified ID. The ID specified is exclusive and responses
            will not include it. If included with the same request as a
            ``start_time`` parameter, only ``since_id`` will be used.
        start_time : Union[datetime.datetime, str]
            YYYY-MM-DDTHH:mm:ssZ (ISO 8601/RFC 3339). The oldest UTC timestamp
            (from most recent seven days) from which the Tweets will be
            provided. Timestamp is in second granularity and is inclusive (for
            example, 12:00:01 includes the first second of the minute). If
            included with the same request as a ``since_id`` parameter, only
            ``since_id`` will be used. By default, a request will return Tweets
            from up to seven days ago if you do not include this parameter.
        tweet_fields : Union[List[str], str]
            :ref:`tweet_fields_parameter`
        until_id : Union[int, str]
            Returns results with a Tweet ID less than (that is, older than) the
            specified ID. The ID specified is exclusive and responses will not
            include it.
        user_fields : Union[List[str], str]
            :ref:`user_fields_parameter`

        Returns
        -------
        Union[dict, requests.Response, Response]

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
        return self._make_request(
            "GET", "/2/tweets/search/recent", params=params,
            endpoint_parameters=(
                "end_time", "expansions", "max_results", "media.fields",
                "next_token", "place.fields", "poll.fields", "query",
                "since_id", "start_time", "tweet.fields", "until_id",
                "user.fields"
            ), data_type=Tweet, user_auth=user_auth
        )

    # Timelines

    def get_users_mentions(self, id, *, user_auth=False, **params):
        """get_users_mentions( \
            id, *, user_auth=False, end_time, expansions, max_results, \
            media_fields, pagination_token, place_fields, poll_fields, \
            since_id, start_time, tweet_fields, until_id, user_fields \
        )

        Returns Tweets mentioning a single user specified by the requested user
        ID. By default, the most recent ten Tweets are returned per request.
        Using pagination, up to the most recent 800 Tweets can be retrieved.

        The Tweets returned by this endpoint count towards the Project-level
        `Tweet cap`_.

        Parameters
        ----------
        id : Union[int, str]
            Unique identifier of the user for whom to return Tweets mentioning
            the user. User ID can be referenced using the `user/lookup`_
            endpoint. More information on Twitter IDs is `here`_.
        user_auth : bool
            Whether or not to use OAuth 1.0a User context
        end_time : Union[datetime.datetime, str]
            YYYY-MM-DDTHH:mm:ssZ (ISO 8601/RFC 3339). The new UTC timestamp
            from which the Tweets will be provided. Timestamp is in second
            granularity and is inclusive (for example, 12:00:01 includes the
            first second of the minute).

            Please note that this parameter does not support a millisecond
            value.
        expansions : Union[List[str], str]
            :ref:`expansions_parameter`
        max_results : int
            Specifies the number of Tweets to try and retrieve, up to a maximum
            of 100 per distinct request. By default, 10 results are returned if
            this parameter is not supplied. The minimum permitted value is 5.
            It is possible to receive less than the ``max_results`` per request
            throughout the pagination process.
        media_fields : Union[List[str], str]
            :ref:`media_fields_parameter`
        pagination_token : str
            This parameter is used to move forwards or backwards through
            'pages' of results, based on the value of the ``next_token`` or
            ``previous_token`` in the response. The value used with the
            parameter is pulled directly from the response provided by the API,
            and should not be modified.
        place_fields : Union[List[str], str]
            :ref:`place_fields_parameter`
        poll_fields : Union[List[str], str]
            :ref:`poll_fields_parameter`
        since_id : Union[int, str]
            Returns results with a Tweet ID greater than (that is, more recent
            than) the specified 'since' Tweet ID. There are limits to the
            number of Tweets that can be accessed through the API. If the limit
            of Tweets has occurred since the ``since_id``, the ``since_id``
            will be forced to the oldest ID available. More information on
            Twitter IDs is `here`_.
        start_time : Union[datetime.datetime, str]
            YYYY-MM-DDTHH:mm:ssZ (ISO 8601/RFC 3339). The oldest UTC timestamp
            from which the Tweets will be provided. Timestamp is in second
            granularity and is inclusive (for example, 12:00:01 includes the
            first second of the minute).

            Please note that this parameter does not support a millisecond
            value.
        tweet_fields : Union[List[str], str]
            :ref:`tweet_fields_parameter`
        until_id : Union[int, str]
            Returns results with a Tweet ID less less than (that is, older
            than) the specified 'until' Tweet ID. There are limits to the
            number of Tweets that can be accessed through the API. If the limit
            of Tweets has occurred since the ``until_id``, the ``until_id``
            will be forced to the most recent ID available. More information on
            Twitter IDs is `here`_.
        user_fields : Union[List[str], str]
            :ref:`user_fields_parameter`

        Returns
        -------
        Union[dict, requests.Response, Response]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/timelines/api-reference/get-users-id-mentions

        .. _Tweet cap: https://developer.twitter.com/en/docs/projects/overview#tweet-cap
        .. _user/lookup: https://developer.twitter.com/en/docs/twitter-api/users/lookup/introduction
        .. _here: https://developer.twitter.com/en/docs/twitter-ids
        """
        return self._make_request(
            "GET", f"/2/users/{id}/mentions", params=params,
            endpoint_parameters=(
                "end_time", "expansions", "max_results", "media.fields",
                "pagination_token", "place.fields", "poll.fields", "since_id",
                "start_time", "tweet.fields", "until_id", "user.fields"
            ), data_type=Tweet, user_auth=user_auth
        )

    def get_users_tweets(self, id, *, user_auth=False, **params):
        """get_users_tweets( \
            id, *, user_auth=False, end_time, exclude, expansions, \
            max_results, media_fields, pagination_token, place_fields, \
            poll_fields, since_id, start_time, tweet_fields, until_id, \
            user_fields \
        )

        Returns Tweets composed by a single user, specified by the requested
        user ID. By default, the most recent ten Tweets are returned per
        request. Using pagination, the most recent 3,200 Tweets can be
        retrieved.

        The Tweets returned by this endpoint count towards the Project-level
        `Tweet cap`_.

        Parameters
        ----------
        id : Union[int, str]
            Unique identifier of the Twitter account (user ID) for whom to
            return results. User ID can be referenced using the `user/lookup`_
            endpoint. More information on Twitter IDs is `here`_.
        user_auth : bool
            Whether or not to use OAuth 1.0a User context
        end_time : Union[datetime.datetime, str]
            YYYY-MM-DDTHH:mm:ssZ (ISO 8601/RFC 3339). The newest or most recent
            UTC timestamp from which the Tweets will be provided. Only the 3200
            most recent Tweets are available. Timestamp is in second
            granularity and is inclusive (for example, 12:00:01 includes the
            first second of the minute). Minimum allowable time is
            2010-11-06T00:00:01Z

            Please note that this parameter does not support a millisecond
            value.
        exclude : Union[List[str], str]
            Comma-separated list of the types of Tweets to exclude from the
            response. When ``exclude=retweets`` is used, the maximum historical
            Tweets returned is still 3200. When the ``exclude=replies``
            parameter is used for any value, only the most recent 800 Tweets
            are available.
        expansions : Union[List[str], str]
            :ref:`expansions_parameter`
        max_results : int
            Specifies the number of Tweets to try and retrieve, up to a maximum
            of 100 per distinct request. By default, 10 results are returned if
            this parameter is not supplied. The minimum permitted value is 5.
            It is possible to receive less than the ``max_results`` per request
            throughout the pagination process.
        media_fields : Union[List[str], str]
            :ref:`media_fields_parameter`
        pagination_token : str
            This parameter is used to move forwards or backwards through
            'pages' of results, based on the value of the ``next_token`` or
            ``previous_token`` in the response. The value used with the
            parameter is pulled directly from the response provided by the API,
            and should not be modified.
        place_fields : Union[List[str], str]
            :ref:`place_fields_parameter`
        poll_fields : Union[List[str], str]
            :ref:`poll_fields_parameter`
        since_id : Union[int, str]
            Returns results with a Tweet ID greater than (that is, more recent
            than) the specified 'since' Tweet ID. Only the 3200 most recent
            Tweets are available. The result will exclude the ``since_id``. If
            the limit of Tweets has occurred since the ``since_id``, the
            ``since_id`` will be forced to the oldest ID available.
        start_time : Union[datetime.datetime, str]
            YYYY-MM-DDTHH:mm:ssZ (ISO 8601/RFC 3339). The oldest or earliest
            UTC timestamp from which the Tweets will be provided. Only the 3200
            most recent Tweets are available. Timestamp is in second
            granularity and is inclusive (for example, 12:00:01 includes the
            first second of the minute). Minimum allowable time is
            2010-11-06T00:00:00Z

            Please note that this parameter does not support a millisecond
            value.
        tweet_fields : Union[List[str], str]
            :ref:`tweet_fields_parameter`
        until_id : Union[int, str]
            Returns results with a Tweet ID less less than (that is, older
            than) the specified 'until' Tweet ID. Only the 3200 most recent
            Tweets are available. The result will exclude the ``until_id``. If
            the limit of Tweets has occurred since the ``until_id``, the
            ``until_id`` will be forced to the most recent ID available.
        user_fields : Union[List[str], str]
            :ref:`user_fields_parameter`

        Returns
        -------
        Union[dict, requests.Response, Response]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/timelines/api-reference/get-users-id-tweets

        .. _Tweet cap: https://developer.twitter.com/en/docs/projects/overview#tweet-cap
        .. _user/lookup: https://developer.twitter.com/en/docs/twitter-api/users/lookup/introduction
        .. _here: https://developer.twitter.com/en/docs/twitter-ids
        """
        return self._make_request(
            "GET", f"/2/users/{id}/tweets", params=params,
            endpoint_parameters=(
                "end_time", "exclude", "expansions", "max_results",
                "media.fields", "pagination_token", "place.fields",
                "poll.fields", "since_id", "start_time", "tweet.fields",
                "until_id", "user.fields"
            ), data_type=Tweet, user_auth=user_auth
        )

    # Tweet counts

    def get_all_tweets_count(self, query, **params):
        """get_all_tweets_count(query, *, end_time, granularity, next_token, \
                                since_id, start_time, until_id)

        This endpoint is only available to those users who have been approved
        for the `Academic Research product track`_.

        The full-archive search endpoint returns the complete history of public
        Tweets matching a search query; since the first Tweet was created March
        26, 2006.

        Parameters
        ----------
        query : str
            One query for matching Tweets. Up to 1024 characters.
        end_time : Union[datetime.datetime, str]
            YYYY-MM-DDTHH:mm:ssZ (ISO 8601/RFC 3339). Used with ``start_time``.
            The newest, most recent UTC timestamp to which the Tweets will be
            provided. Timestamp is in second granularity and is exclusive (for
            example, 12:00:01 excludes the first second of the minute). If used
            without ``start_time``, Tweets from 30 days before ``end_time``
            will be returned by default. If not specified, ``end_time`` will
            default to [now - 30 seconds].
        granularity : str
            This is the granularity that you want the timeseries count data to
            be grouped by. You can requeset ``minute``, ``hour``, or ``day``
            granularity. The default granularity, if not specified is ``hour``.
        next_token : str
            This parameter is used to get the next 'page' of results. The value
            used with the parameter is pulled directly from the response
            provided by the API, and should not be modified. You can learn more
            by visiting our page on `pagination`_.
        since_id : Union[int, str]
            Returns results with a Tweet ID greater than (for example, more
            recent than) the specified ID. The ID specified is exclusive and
            responses will not include it. If included with the same request as
            a ``start_time`` parameter, only ``since_id`` will be used.
        start_time : Union[datetime.datetime, str]
            YYYY-MM-DDTHH:mm:ssZ (ISO 8601/RFC 3339). The oldest UTC timestamp
            from which the Tweets will be provided. Timestamp is in second
            granularity and is inclusive (for example, 12:00:01 includes the
            first second of the minute). By default, a request will return
            Tweets from up to 30 days ago if you do not include this parameter.
        until_id : Union[int, str]
            Returns results with a Tweet ID less than (that is, older than) the
            specified ID. Used with ``since_id``. The ID specified is exclusive
            and responses will not include it.

        Returns
        -------
        Union[dict, requests.Response, Response]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/counts/api-reference/get-tweets-counts-all

        .. _Academic Research product track: https://developer.twitter.com/en/docs/projects/overview#product-track
        .. _pagination: https://developer.twitter.com/en/docs/twitter-api/tweets/search/integrate/paginate
        """
        params["query"] = query
        return self._make_request(
            "GET", "/2/tweets/counts/all", params=params,
            endpoint_parameters=(
                "end_time", "granularity", "next_token", "query", "since_id",
                "start_time", "until_id"
            )
        )

    def get_recent_tweets_count(self, query, **params):
        """get_recent_tweets_count(query, *, end_time, granularity, since_id, \
                                   start_time, until_id)

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
        end_time : Union[datetime.datetime, str]
            YYYY-MM-DDTHH:mm:ssZ (ISO 8601/RFC 3339). The newest, most recent
            UTC timestamp to which the Tweets will be provided. Timestamp is in
            second granularity and is exclusive (for example, 12:00:01 excludes
            the first second of the minute). By default, a request will return
            Tweets from as recent as 30 seconds ago if you do not include this
            parameter.
        granularity : str
            This is the granularity that you want the timeseries count data to
            be grouped by. You can requeset ``minute``, ``hour``, or ``day``
            granularity. The default granularity, if not specified is ``hour``.
        since_id : Union[int, str]
            Returns results with a Tweet ID greater than (that is, more recent
            than) the specified ID. The ID specified is exclusive and responses
            will not include it. If included with the same request as a
            ``start_time`` parameter, only ``since_id`` will be used.
        start_time : Union[datetime.datetime, str]
            YYYY-MM-DDTHH:mm:ssZ (ISO 8601/RFC 3339). The oldest UTC timestamp
            (from most recent seven days) from which the Tweets will be
            provided. Timestamp is in second granularity and is inclusive (for
            example, 12:00:01 includes the first second of the minute). If
            included with the same request as a ``since_id`` parameter, only
            ``since_id`` will be used. By default, a request will return Tweets
            from up to seven days ago if you do not include this parameter.
        until_id : Union[int, str]
            Returns results with a Tweet ID less than (that is, older than) the
            specified ID. The ID specified is exclusive and responses will not
            include it.

        Returns
        -------
        Union[dict, requests.Response, Response]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/counts/api-reference/get-tweets-counts-recent

        .. _Standard Project: https://developer.twitter.com/en/docs/projects
        .. _access level: https://developer.twitter.com/en/products/twitter-api/early-access/guide.html#na_1
        .. _operators: https://developer.twitter.com/en/docs/twitter-api/tweets/search/integrate/build-a-query
        .. _Academic Research Project: https://developer.twitter.com/en/docs/projects
        """
        params["query"] = query
        return self._make_request(
            "GET", "/2/tweets/counts/recent", params=params,
            endpoint_parameters=(
                "end_time", "granularity", "query", "since_id", "start_time",
                "until_id"
            )
        )

    # Tweet lookup

    def get_tweet(self, id, *, user_auth=False, **params):
        """get_tweet(id, *, user_auth=False, expansions, media_fields, \
                     place_fields, poll_fields, twitter_fields, user_fields)

        Returns a variety of information about a single Tweet specified by
        the requested ID.

        Parameters
        ----------
        id : Union[int, str]
            Unique identifier of the Tweet to request
        user_auth : bool
            Whether or not to use OAuth 1.0a User context
        expansions : Union[List[str], str]
            :ref:`expansions_parameter`
        media_fields : Union[List[str], str]
            :ref:`media_fields_parameter`
        place_fields : Union[List[str], str]
            :ref:`place_fields_parameter`
        poll_fields : Union[List[str], str]
            :ref:`poll_fields_parameter`
        tweet_fields : Union[List[str], str]
            :ref:`tweet_fields_parameter`
        user_fields : Union[List[str], str]
            :ref:`user_fields_parameter`

        Returns
        -------
        Union[dict, requests.Response, Response]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/lookup/api-reference/get-tweets-id
        """
        return self._make_request(
            "GET", f"/2/tweets/{id}", params=params,
            endpoint_parameters=(
                "expansions", "media.fields", "place.fields", "poll.fields",
                "tweet.fields", "user.fields"
            ), data_type=Tweet, user_auth=user_auth
        )

    def get_tweets(self, ids, *, user_auth=False, **params):
        """get_tweets(ids, *, user_auth=False, expansions, media_fields, \
                      place_fields, poll_fields, twitter_fields, user_fields)

        Returns a variety of information about the Tweet specified by the
        requested ID or list of IDs.

        Parameters
        ----------
        ids : Union[List[int, str], str]
            A comma separated list of Tweet IDs. Up to 100 are allowed in a
            single request. Make sure to not include a space between commas and
            fields.
        user_auth : bool
            Whether or not to use OAuth 1.0a User context
        expansions : Union[List[str], str]
            :ref:`expansions_parameter`
        media_fields : Union[List[str], str]
            :ref:`media_fields_parameter`
        place_fields : Union[List[str], str]
            :ref:`place_fields_parameter`
        poll_fields : Union[List[str], str]
            :ref:`poll_fields_parameter`
        tweet_fields : Union[List[str], str]
            :ref:`tweet_fields_parameter`
        user_fields : Union[List[str], str]
            :ref:`user_fields_parameter`

        Returns
        -------
        Union[dict, requests.Response, Response]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/tweets/lookup/api-reference/get-tweets
        """
        params["ids"] = ids
        return self._make_request(
            "GET", "/2/tweets", params=params,
            endpoint_parameters=(
                "ids", "expansions", "media.fields", "place.fields",
                "poll.fields", "tweet.fields", "user.fields"
            ), data_type=Tweet, user_auth=user_auth
        )

    # Blocks

    def unblock(self, target_user_id):
        """Unblock another user.

        The request succeeds with no action when the user sends a request to a
        user they're not blocking or have already unblocked.

        Parameters
        ----------
        target_user_id : Union[int, str]
            The user ID of the user that you would like to unblock.

        Returns
        -------
        Union[dict, requests.Response, Response]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/users/blocks/api-reference/delete-users-user_id-blocking
        """
        source_user_id = self.access_token.partition('-')[0]
        route = f"/2/users/{source_user_id}/blocking/{target_user_id}"

        return self._make_request(
            "DELETE", route, user_auth=True
        )

    def get_blocked(self, **params):
        """get_blocked(*, expansions, max_results, pagination_token, \
                       tweet_fields, user_fields)

        Returns a list of users who are blocked by the authenticating user.

        Parameters
        ----------
        expansions : Union[List[str], str]
            :ref:`expansions_parameter`
        max_results : int
            The maximum number of results to be returned per page. This can be
            a number between 1 and 1000. By default, each page will return 100
            results.
        pagination_token : str
            Used to request the next page of results if all results weren't
            returned with the latest request, or to go back to the previous
            page of results.
        tweet_fields : Union[List[str], str]
            :ref:`tweet_fields_parameter`
        user_fields : Union[List[str], str]
            :ref:`user_fields_parameter`

        Returns
        -------
        Union[dict, requests.Response, Response]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/users/blocks/api-reference/get-users-blocking
        """
        id = self.access_token.partition('-')[0]
        route = f"/2/users/{id}/blocking"

        return self._make_request(
            "GET", route, params=params,
            endpoint_parameters=(
                "expansions", "max_results", "pagination_token",
                "tweet.fields", "user.fields"
            ), data_type=User, user_auth=True
        )

    def block(self, target_user_id):
        """Block another user.

        Parameters
        ----------
        target_user_id : Union[int, str]
            The user ID of the user that you would like to block.

        Returns
        -------
        Union[dict, requests.Response, Response]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/users/blocks/api-reference/post-users-user_id-blocking
        """
        id = self.access_token.partition('-')[0]
        route = f"/2/users/{id}/blocking"

        return self._make_request(
            "POST", route, json={"target_user_id": str(target_user_id)},
            user_auth=True
        )

    # Follows

    def unfollow(self, target_user_id):
        """Allows a user ID to unfollow another user.

        The request succeeds with no action when the authenticated user sends a
        request to a user they're not following or have already unfollowed.

        Parameters
        ----------
        target_user_id : Union[int, str]
            The user ID of the user that you would like to unfollow.

        Returns
        -------
        Union[dict, requests.Response, Response]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/users/follows/api-reference/delete-users-source_id-following
        """
        source_user_id = self.access_token.partition('-')[0]
        route = f"/2/users/{source_user_id}/following/{target_user_id}"

        return self._make_request("DELETE", route, user_auth=True)

    def get_users_followers(self, id, *, user_auth=False, **params):
        """get_users_followers( \
            id, *, user_auth=False, expansions, max_results, \
            pagination_token, tweet_fields, user_fields \
        )

        Returns a list of users who are followers of the specified user ID.

        Parameters
        ----------
        id : Union[int, str]
            The user ID whose followers you would like to retrieve.
        user_auth : bool
            Whether or not to use OAuth 1.0a User context
        expansions : Union[List[str], str]
            :ref:`expansions_parameter`
        max_results : int
            The maximum number of results to be returned per page. This can be
            a number between 1 and the 1000. By default, each page will return
            100 results.
        pagination_token : str
            Used to request the next page of results if all results weren't
            returned with the latest request, or to go back to the previous
            page of results. To return the next page, pass the ``next_token``
            returned in your previous response. To go back one page, pass the
            ``previous_token`` returned in your previous response.
        tweet_fields : Union[List[str], str]
            :ref:`tweet_fields_parameter`
        user_fields : Union[List[str], str]
            :ref:`user_fields_parameter`

        Returns
        -------
        Union[dict, requests.Response, Response]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/users/follows/api-reference/get-users-id-followers
        """
        return self._make_request(
            "GET", f"/2/users/{id}/followers", params=params,
            endpoint_parameters=(
                "expansions", "max_results", "pagination_token",
                "tweet.fields", "user.fields"
            ),
            data_type=User, user_auth=user_auth
        )

    def get_users_following(self, id, *, user_auth=False, **params):
        """get_users_following( \
            id, *, user_auth=False, expansions, max_results, \
            pagination_token, tweet_fields, user_fields \
        )

        Returns a list of users the specified user ID is following.

        Parameters
        ----------
        id : Union[int, str]
            The user ID whose following you would like to retrieve.
        user_auth : bool
            Whether or not to use OAuth 1.0a User context
        expansions : Union[List[str], str]
            :ref:`expansions_parameter`
        max_results : int
            The maximum number of results to be returned per page. This can be
            a number between 1 and the 1000. By default, each page will return
            100 results.
        pagination_token : str
            Used to request the next page of results if all results weren't
            returned with the latest request, or to go back to the previous
            page of results. To return the next page, pass the ``next_token``
            returned in your previous response. To go back one page, pass the
            ``previous_token`` returned in your previous response.
        tweet_fields : Union[List[str], str]
            :ref:`tweet_fields_parameter`
        user_fields : Union[List[str], str]
            :ref:`user_fields_parameter`

        Returns
        -------
        Union[dict, requests.Response, Response]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/users/follows/api-reference/get-users-id-following
        """
        return self._make_request(
            "GET", f"/2/users/{id}/following", params=params,
            endpoint_parameters=(
                "expansions", "max_results", "pagination_token",
                "tweet.fields", "user.fields"
            ), data_type=User, user_auth=user_auth
        )

    def follow(self, target_user_id):
        """Allows a user ID to follow another user.

        If the target user does not have public Tweets, this endpoint will send
        a follow request.

        The request succeeds with no action when the authenticated user sends a
        request to a user they're already following, or if they're sending a
        follower request to a user that does not have public Tweets.

        Parameters
        ----------
        target_user_id : Union[int, str]
            The user ID of the user that you would like to follow.

        Returns
        -------
        Union[dict, requests.Response, Response]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/users/follows/api-reference/post-users-source_user_id-following
        """
        source_user_id = self.access_token.partition('-')[0]
        route = f"/2/users/{source_user_id}/following"

        return self._make_request(
            "POST", route, json={"target_user_id": str(target_user_id)},
            user_auth=True
        )

    # Mutes

    def unmute(self, target_user_id):
        """Allows an authenticated user ID to unmute the target user.

        The request succeeds with no action when the user sends a request to a
        user they're not muting or have already unmuted.

        Parameters
        ----------
        target_user_id : Union[int, str]
            The user ID of the user that you would like to unmute.

        Returns
        -------
        Union[dict, requests.Response, Response]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/users/mutes/api-reference/delete-users-user_id-muting
        """
        source_user_id = self.access_token.partition('-')[0]
        route = f"/2/users/{source_user_id}/muting/{target_user_id}"

        return self._make_request("DELETE", route, user_auth=True)

    def mute(self, target_user_id):
        """Allows an authenticated user ID to mute the target user.

        Parameters
        ----------
        target_user_id : Union[int, str]
            The user ID of the user that you would like to mute.

        Returns
        -------
        Union[dict, requests.Response, Response]

        References
        ----------
        https://developer.twitter.com/en/docs/twitter-api/users/mutes/api-reference/post-users-user_id-muting
        """
        id = self.access_token.partition('-')[0]
        route = f"/2/users/{id}/muting"

        return self._make_request(
            "POST", route, json={"target_user_id": str(target_user_id)},
            user_auth=True
        )

    # User lookup

    def get_user(self, *, id=None, username=None, user_auth=False, **params):
        """get_user(*, id, username, user_auth=False, expansions, \
                    tweet_fields, user_fields)

        Returns a variety of information about a single user specified by the
        requested ID or username.

        Parameters
        ----------
        id : Union[int, str]
            The ID of the user to lookup.
        username : str
            The Twitter username (handle) of the user.
        user_auth : bool
            Whether or not to use OAuth 1.0a User context
        expansions : Union[List[str], str]
            :ref:`expansions_parameter`
        tweet_fields : Union[List[str], str]
            :ref:`tweet_fields_parameter`
        user_fields : Union[List[str], str]
            :ref:`user_fields_parameter`

        Raises
        ------
        TypeError
            If ID and username are not passed or both are passed

        Returns
        -------
        Union[dict, requests.Response, Response]

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

        return self._make_request(
            "GET", route, params=params,
            endpoint_parameters=("expansions", "tweet.fields", "user.fields"),
            data_type=User, user_auth=user_auth
        )

    def get_users(self, *, ids=None, usernames=None, user_auth=False,
                  **params):
        """get_users(*, ids, usernames, user_auth=False, expansions, \
                     tweet_fields, user_fields)

        Returns a variety of information about one or more users specified by
        the requested IDs or usernames.

        Parameters
        ----------
        ids : Union[List[int, str], str]
            A comma separated list of user IDs. Up to 100 are allowed in a
            single request. Make sure to not include a space between commas and
            fields.
        usernames : Union[List[str], str]
            A comma separated list of Twitter usernames (handles). Up to 100
            are allowed in a single request. Make sure to not include a space
            between commas and fields.
        user_auth : bool
            Whether or not to use OAuth 1.0a User context
        expansions : Union[List[str], str]
            :ref:`expansions_parameter`
        tweet_fields : Union[List[str], str]
            :ref:`tweet_fields_parameter`
        user_fields : Union[List[str], str]
            :ref:`user_fields_parameter`

        Raises
        ------
        TypeError
            If IDs and usernames are not passed or both are passed

        Returns
        -------
        Union[dict, requests.Response, Response]

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

        return self._make_request(
            "GET", route, params=params,
            endpoint_parameters=(
                "ids", "usernames", "expansions", "tweet.fields", "user.fields"
            ), data_type=User, user_auth=user_auth
        )
