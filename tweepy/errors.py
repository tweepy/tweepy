# Tweepy
# Copyright 2009-2022 Joshua Roesslein
# See LICENSE for details.

import requests


class TweepyException(Exception):
    """Base exception for Tweepy

    .. versionadded:: 4.0
    """
    pass


class HTTPException(TweepyException):
    """HTTPException()

    Exception raised when an HTTP request fails

    .. versionadded:: 4.0

    Attributes
    ----------
    response : requests.Response
        Requests Response from the Twitter API
    api_errors : List[dict[str, Union[int, str]]]
        The errors the Twitter API responded with, if any
    api_codes : List[int]
        The error codes the Twitter API responded with, if any
    api_messages : List[str]
        The error messages the Twitter API responded with, if any
    """

    def __init__(self, response):
        self.response = response

        self.api_errors = []
        self.api_codes = []
        self.api_messages = []

        try:
            response_json = response.json()
        except requests.JSONDecodeError:
            super().__init__(f"{response.status_code} {response.reason}")
        else:
            errors = response_json.get("errors", [])
            # Use := when support for Python 3.7 is dropped
            if "error" in response_json:
                errors.append(response_json["error"])
            error_text = ""
            for error in errors:
                self.api_errors.append(error)
                if "code" in error:
                    self.api_codes.append(error["code"])
                if "message" in error:
                    self.api_messages.append(error["message"])
                if "code" in error and "message" in error:
                    error_text += f"\n{error['code']} - {error['message']}"
                elif "message" in error:
                    error_text += '\n' + error["message"]
            super().__init__(
                f"{response.status_code} {response.reason}{error_text}"
            )


class BadRequest(HTTPException):
    """BadRequest()

    Exception raised for a 400 HTTP status code

    .. versionadded:: 4.0
    """
    pass


class Unauthorized(HTTPException):
    """Unauthorized()

    Exception raised for a 401 HTTP status code

    .. versionadded:: 4.0
    """
    pass


class Forbidden(HTTPException):
    """Forbidden()

    Exception raised for a 403 HTTP status code

    .. versionadded:: 4.0
    """
    pass


class NotFound(HTTPException):
    """NotFound()

    Exception raised for a 404 HTTP status code

    .. versionadded:: 4.0
    """
    pass


class TooManyRequests(HTTPException):
    """TooManyRequests()

    Exception raised for a 429 HTTP status code

    .. versionadded:: 4.0
    """
    pass


class TwitterServerError(HTTPException):
    """TwitterServerError()

    Exception raised for a 5xx HTTP status code

    .. versionadded:: 4.0
    """
    pass
