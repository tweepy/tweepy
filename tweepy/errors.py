# Tweepy
# Copyright 2009-2021 Joshua Roesslein
# See LICENSE for details.

import json


class TweepyException(Exception):
    """Base exception for Tweepy"""
    pass


class HTTPException(TweepyException):
    """Exception raised when an HTTP request fails"""

    def __init__(self, response):
        self.response = response

        self.api_errors = []
        self.api_codes = []
        self.api_messages = []

        try:
            response_json = response.json()
        except json.JSONDecodeError:
            super().__init__(f"{response.status_code} {response.reason}")
        else:
            error_text = []
            # Use := when support for Python 3.7 is dropped
            if "errors" not in response_json:
                super().__init__(f"{response.status_code} {response.reason}")
                return
            for error in response_json["errors"]:
                self.api_errors.append(error)
                if "code" in error:
                    self.api_codes.append(error["code"])
                if "message" in error:
                    self.api_messages.append(error["message"])
                if "code" in error and "message" in error:
                    error_text.append(f"{error['code']} - {error['message']}")
                elif "message" in error:
                    error_text.append(error["message"])
            error_text = '\n'.join(error_text)
            super().__init__(
                f"{response.status_code} {response.reason}\n{error_text}"
            )


class BadRequest(HTTPException):
    """Exception raised for a 400 HTTP status code"""
    pass


class Unauthorized(HTTPException):
    """Exception raised for a 401 HTTP status code"""
    pass


class Forbidden(HTTPException):
    """Exception raised for a 403 HTTP status code"""
    pass


class NotFound(HTTPException):
    """Exception raised for a 404 HTTP status code"""
    pass


class TooManyRequests(HTTPException):
    """Exception raised for a 429 HTTP status code"""
    pass


class TwitterServerError(HTTPException):
    """Exception raised for a 5xx HTTP status code"""
