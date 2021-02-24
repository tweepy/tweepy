# Tweepy
# Copyright 2009-2021 Joshua Roesslein
# See LICENSE for details.

from collections import namedtuple
import datetime
import logging
from platform import python_version

import requests

import tweepy
from tweepy.auth import OAuthHandler
from tweepy.media import Media
from tweepy.place import Place
from tweepy.poll import Poll
from tweepy.tweet import Tweet
from tweepy.user import User

log = logging.getLogger(__name__)

Response = namedtuple("Response", ("data", "includes", "errors", "meta"))


class Client:
    """
    Parameters
    ----------
    bearer_token: Optional[:class:`str`]
        Bearer token
    consumer_key: Optional[:class:`str`]
        Consumer key
    consumer_secret: Optional[:class:`str`]
        Consuemr secret
    access_token: Optional[:class:`str`]
        Access token
    access_token_secret: Optional[:class:`str`]
        Access token secret
    """

    def __init__(self, bearer_token=None, consumer_key=None,
                 consumer_secret=None, access_token=None,
                 access_token_secret=None):
        self.bearer_token = bearer_token
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret

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
        # TODO: Ability to choose app or user auth
        if user_auth:
            auth = OAuthHandler(self.consumer_key, self.consumer_secret)
            auth.set_access_token(self.access_token, self.access_token_secret)
            auth = auth.apply_auth()
        else:
            headers["Authorization"] = f"Bearer {self.bearer_token}"
        # TODO: log.debug
        with self.session.request(
            method, host + route, params=params, json=json, headers=headers,
            auth=auth
        ) as response:
            # TODO: log.debug
            if response.status_code in (400, 403):
                print(response.status_code)
                # TODO: Handle
            elif response.status_code != 200:
                print(response.status_code)
                # TODO: Handle
            # TODO: Handle rate limits
            return response.json()

    def _make_request(self, method, route, params={}, allowed_params=None,
                      json=None, data_type=None, user_auth=False):
        request_params = {}
        for param_name, param_value in params.items():
            if param_name in allowed_params:
                if isinstance(param_value, list):
                    request_params[param_name] = ','.join(map(str, param_value))
                elif param_name in ("start_time", "end_time") and isinstance(param_value, datetime.datetime):
                    request_params[param_name] = param_value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                    # TODO: Constant datetime format string?
                else:
                    request_params[param_name] = param_value
            elif param_name.replace('_', '.') in allowed_params:
                # Use := when support for Python 3.7 is dropped
                request_params[param_name.replace('_', '.')] = ','.join(param_value)
            else:
                log.warn(f"'{param_name}' is not an allowed parameter")

        response = self.request(method, route, params=request_params,
                                json=json, user_auth=user_auth)

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

    def follow(self, target_user_id):
        """
        Follow user
        https://developer.twitter.com/en/docs/twitter-api/users/follows/api-reference/post-users-source_user_id-following
        """
        source_user_id = self.access_token.partition('-')[0]
        route = f"/2/users/{source_user_id}/following"

        return self._make_request(
            "POST", route, json={"target_user_id": str(target_user_id)},
            user_auth=True
        )

    def get_tweet(self, id, **params):
        """
        Tweet lookup
        https://developer.twitter.com/en/docs/twitter-api/tweets/lookup/api-reference/get-tweets-id
        """
        return self._make_request(
            "GET", f"/2/tweets/{id}", params=params,
            allowed_params=("expansions", "media.fields", "place.fields",
                            "poll.fields", "tweet.fields", "user.fields"),
            data_type=Tweet
        )

    def get_tweets(self, ids, **params):
        """
        Tweets lookup
        https://developer.twitter.com/en/docs/twitter-api/tweets/lookup/api-reference/get-tweets
        """
        params["ids"] = ids
        return self._make_request(
            "GET", "/2/tweets", params=params,
            allowed_params=("ids", "expansions", "media.fields",
                            "place.fields", "poll.fields", "tweet.fields",
                            "user.fields"),
            data_type=Tweet
        )

    def get_user(self, *, id=None, username=None, **params):
        """
        User lookup
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
            allowed_params=("expansions", "tweet_fields", "user_fields"),
            data_type=User
        )

    def get_users(self, *, ids=None, usernames=None, **params):
        """
        Users lookup
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
            allowed_params=("ids", "usernames", "expansions", "tweet_fields",
                            "user_fields"),
            data_type=User
        )

    def get_users_followers(self, id, **params):
        """
        Followers lookup
        https://developer.twitter.com/en/docs/twitter-api/users/follows/api-reference/get-users-id-followers
        """
        return self._make_request(
            "GET", f"/2/users/{id}/followers", params=params,
            allowed_params=("expansions", "max_results", "pagination_token",
                            "tweet.fields", "user.fields"),
            data_type=User
        )

    def get_users_following(self, id, **params):
        """
        Following lookup
        https://developer.twitter.com/en/docs/twitter-api/users/follows/api-reference/get-users-id-following
        """
        return self._make_request(
            "GET", f"/2/users/{id}/following", params=params,
            allowed_params=("expansions", "max_results", "pagination_token",
                            "tweet.fields", "user.fields"),
            data_type=User
        )

    def get_users_mentions(self, id, **params):
        """
        User mention timeline
        https://developer.twitter.com/en/docs/twitter-api/tweets/timelines/api-reference/get-users-id-mentions
        """
        return self._make_request(
            "GET", f"/2/users/{id}/mentions", params=params,
            allowed_params=("end_time", "expansions", "max_results",
                            "media.fields", "pagination_token", "place.fields",
                            "poll.fields", "since_id", "start_time",
                            "tweet.fields", "until_id", "user.fields"),
            data_type=Tweet
        )

    def get_users_tweets(self, id, **params):
        """
        User Tweet timeline
        https://developer.twitter.com/en/docs/twitter-api/tweets/timelines/api-reference/get-users-id-tweets
        """
        return self._make_request(
            "GET", f"/2/users/{id}/tweets", params=params,
            allowed_params=("end_time", "exclude", "expansions", "max_results",
                            "media.fields", "pagination_token", "place.fields",
                            "poll.fields", "since_id", "start_time",
                            "tweet.fields", "until_id", "user.fields"),
            data_type=Tweet
        )

    def hide_reply(self, id):
        """
        Hide replies
        https://developer.twitter.com/en/docs/twitter-api/tweets/hide-replies/api-reference/put-tweets-id-hidden
        """
        return self._make_request(
            "PUT", f"/2/tweets/{id}/hidden", json={"hidden": True},
            user_auth=True
        )[0]["hidden"]

    def search_all_tweets(self, query, **params):
        return self._make_request(
            "GET", "/2/tweets/search/all", params=params,
            allowed_params=("end_time", "expansions", "max_results",
                            "media.fields", "next_token", "place.fields",
                            "poll.fields", "query", "since_id", "start_time",
                            "tweet.fields", "until_id", "user.fields"),
            data_type=Tweet
        )

    def search_recent_tweets(self, query, **params):
        """
        Search Tweets: recent search
        https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-recent
        """
        params["query"] = query
        return self._make_request(
            "GET", "/2/tweets/search/recent", params=params,
            allowed_params=("end_time", "expansions", "max_results",
                            "media.fields", "next_token", "place.fields",
                            "poll.fields", "query", "since_id", "start_time",
                            "tweet.fields", "until_id", "user.fields"),
            data_type=Tweet
        )

    def unfollow(self, target_user_id):
        """
        Unfollow user
        https://developer.twitter.com/en/docs/twitter-api/users/follows/api-reference/delete-users-source_id-following
        """
        source_user_id = self.access_token.partition('-')[0]
        route = f"/2/users/{source_user_id}/following/{target_user_id}"

        return self._make_request(
            "DELETE", route, user_auth=True
        )

    def unhide_reply(self, tweet_id):
        """
        Unhide replies
        https://developer.twitter.com/en/docs/twitter-api/tweets/hide-replies/api-reference/put-tweets-id-hidden
        """
        return self._make_request(
            "PUT", f"/2/tweets/{tweet_id}/hidden", json={"hidden": False},
            user_auth=True
        )[0]["hidden"]
