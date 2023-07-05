.. _authentication:

.. currentmodule:: tweepy

**************
Authentication
**************

This supplements Twitter's `Authentication documentation`_.

.. _Authentication documentation: https://developer.twitter.com/en/docs/authentication/overview

Introduction
============

Tweepy supports the OAuth 1.0a User Context, OAuth 2.0 Bearer Token (App-Only),
and OAuth 2.0 Authorization Code Flow with PKCE (User Context) authentication
methods.

Twitter API v1.1
================

OAuth 2.0 Bearer Token (App-Only)
---------------------------------
The simplest way to generate a bearer token is through your app's Keys and
Tokens tab under the `Twitter Developer Portal Projects & Apps page`_.

.. _Twitter Developer Portal Projects & Apps page: https://developer.twitter.com/en/portal/projects-and-apps

You can then initialize :class:`OAuth2BearerHandler` with the bearer token and
initialize :class:`API` with the :class:`OAuth2BearerHandler` instance::

    import tweepy

    auth = tweepy.OAuth2BearerHandler("Bearer Token here")
    api = tweepy.API(auth)

Alternatively, you can use the API / Consumer key and secret that can be found
on the same page and initialize :class:`OAuth2AppHandler` instead::

    import tweepy

    auth = tweepy.OAuth2AppHandler(
        "API / Consumer Key here", "API / Consumer Secret here"
    )
    api = tweepy.API(auth)

OAuth 1.0a User Context
-----------------------
Similarly, the simplest way to authenticate as your developer account is to
generate an access token and access token secret through your app's Keys and
Tokens tab under the `Twitter Developer Portal Projects & Apps page`_.

You'll also need the app's API / consumer key and secret that can be found on
that page.

You can then initialize :class:`OAuth1UserHandler` with all four credentials
and initialize :class:`API` with the :class:`OAuth1UserHandler` instance::

    import tweepy

    auth = tweepy.OAuth1UserHandler(
       "API / Consumer Key here", "API / Consumer Secret here",
       "Access Token here", "Access Token Secret here"
    )
    api = tweepy.API(auth)

To authenticate as a different user, see :ref:`3-legged OAuth`.

Twitter API v2
==============

Tweepy's interface for Twitter API v2, :class:`Client`, handles OAuth 2.0
Bearer Token (application-only) and OAuth 1.0a User Context authentication for
you.

OAuth 2.0 Bearer Token (App-Only)
---------------------------------
The simplest way to generate a bearer token is through your app's Keys and
Tokens tab under the `Twitter Developer Portal Projects & Apps page`_.

You can then simply pass the bearer token to :class:`Client` when initializing
it::

    import tweepy

    client = tweepy.Client("Bearer Token here")

OAuth 1.0a User Context
-----------------------
Similarly, the simplest way to authenticate as your developer account is to
generate an access token and access token secret through your app's Keys and
Tokens tab under the `Twitter Developer Portal Projects & Apps page`_.

You'll also need the app's API / consumer key and secret that can be found on
that page.

You can then simply pass all four credentials to :class:`Client` when
initializing it::

    import tweepy

    client = tweepy.Client(
        consumer_key="API / Consumer Key here",
        consumer_secret="API / Consumer Secret here",
        access_token="Access Token here",
        access_token_secret="Access Token Secret here"
    )

To authenticate as a different user, see :ref:`3-legged OAuth`.

OAuth 2.0 Authorization Code Flow with PKCE (User Context)
----------------------------------------------------------
You can generate an access token to authenticate as a user using
:class:`OAuth2UserHandler`.

You'll need to turn on OAuth 2.0 under the User authentication settings section
of your app's Settings tab under the
`Twitter Developer Portal Projects & Apps page`_. To do this, you'll need to
provide a Callback / Redirect URI / URL.

Then, you'll need to note the app's Client ID, which you can find through your
app's Keys and Tokens tab under the
`Twitter Developer Portal Projects & Apps page`_. If you're using a
confidential client, you'll also need to generate a Client Secret.

You can then initialize :class:`OAuth2UserHandler` with the scopes you need::

    import tweepy

    oauth2_user_handler = tweepy.OAuth2UserHandler(
        client_id="Client ID here",
        redirect_uri="Callback / Redirect URI / URL here",
        scope=["Scope here", "Scope here"],
        # Client Secret is only necessary if using a confidential client
        client_secret="Client Secret here"
    )

For a list of scopes, see the Scopes section of Twitter's
`OAuth 2.0 Authorization Code Flow with PKCE documentation`_.

.. _OAuth 2.0 Authorization Code Flow with PKCE documentation: https://developer.twitter.com/en/docs/authentication/oauth-2-0/authorization-code

Then, you can get the authorization URL::

    print(oauth2_user_handler.get_authorization_url())

This can be used to have a user authenticate your app. Once they've done so,
they'll be redirected to the Callback / Redirect URI / URL you provided. You'll
need to pass that authorization response URL to fetch the access token::

    response = oauth2_user_handler.fetch_token(
        "Authorization Response URL here"
    )
    access_token = response["access_token"]

You can then pass the access token to :class:`Client` when initializing it::

    client = tweepy.Client("Access Token here")

3-legged OAuth
==============
This section supplements Twitter's `3-legged OAuth flow documentation`_.

.. _3-legged OAuth flow documentation: https://developer.twitter.com/en/docs/authentication/oauth-1-0a/obtaining-user-access-tokens

To authenticate as a user other than your developer account, you'll need to
obtain their access tokens through the 3-legged OAuth flow.

First, you'll need to turn on OAuth 1.0 under the User authentication settings
section of your app's Settings tab under the
`Twitter Developer Portal Projects & Apps page`_. To do this, you'll need to
provide a Callback / Redirect URI / URL.

Then, you'll need the app's API / consumer key and secret that can be found
through your app's Keys and Tokens tab under the
`Twitter Developer Portal Projects & Apps page`_.

You can then initialize an instance of :class:`OAuth1UserHandler`::

    import tweepy

    oauth1_user_handler = tweepy.OAuth1UserHandler(
        "API / Consumer Key here", "API / Consumer Secret here",
        callback="Callback / Redirect URI / URL here"
    )

Then, you can get the authorization URL::

    print(oauth1_user_handler.get_authorization_url())

To use Log in with Twitter / Sign in with Twitter, you can set the
``signin_with_twitter`` parameter when getting the authorization URL::

    print(oauth1_user_handler.get_authorization_url(signin_with_twitter=True))

This can be used to have a user authenticate your app. Once they've done so,
they'll be redirected to the Callback / Redirect URI / URL you provided, with
``oauth_token`` and ``oauth_verifier`` parameters.

You can then use the verifier to get the access token and secret::

    access_token, access_token_secret = oauth1_user_handler.get_access_token(
        "Verifier (oauth_verifier) here"
    )

If you need to reinitialize :class:`OAuth1UserHandler`, you can set the request
token and secret afterward, before using the verifier to get the access token
and secret::

    request_token = oauth1_user_handler.request_token["oauth_token"]
    request_secret = oauth1_user_handler.request_token["oauth_token_secret"]

    new_oauth1_user_handler = tweepy.OAuth1UserHandler(
        "API / Consumer Key here", "API / Consumer Secret here",
        callback="Callback / Redirect URI / URL here"
    )
    new_oauth1_user_handler.request_token = {
        "oauth_token": "Request Token (oauth_token) here",
        "oauth_token_secret": request_secret
    }
    access_token, access_token_secret = (
        new_oauth1_user_handler.get_access_token(
            "Verifier (oauth_verifier) here"
        )
    )

Otherwise, you can simply use the old instance of :class:`OAuth1UserHandler`.

You can then use this instance of :class:`OAuth1UserHandler` to initialize
:class:`API`::

    api = tweepy.API(oauth1_user_handler)

You can also use the ``access_token`` and ``access_token_secret`` to initialize
a new instance of :class:`OAuth1UserHandler` to initialize :class:`API`::

    auth = tweepy.OAuth1UserHandler(
       "API / Consumer Key here", "API / Consumer Secret here",
       "Access Token here", "Access Token Secret here"
    )
    api = tweepy.API(auth)

For initializing :class:`Client`, you can pass ``access_token`` and
``access_token_secret`` directly::

    client = tweepy.Client(
        consumer_key="API / Consumer Key here",
        consumer_secret="API / Consumer Secret here",
        access_token="Access Token here",
        access_token_secret="Access Token Secret here"
    )

PIN-based OAuth
---------------
This section supplements Twitter's `PIN-based OAuth documentation`_.

.. _PIN-based OAuth documentation: https://developer.twitter.com/en/docs/authentication/oauth-1-0a/pin-based-oauth

The PIN-based OAuth flow can be used by setting the ``callback`` parameter to
``"oob"``::

    import tweepy

    oauth1_user_handler = tweepy.OAuth1UserHandler(
        "API / Consumer Key here", "API / Consumer Secret here",
        callback="oob"
    )

You can then get the authorization URL the same way::

    print(oauth1_user_handler.get_authorization_url())

When the user authenticates with this URL, they'll be provided a PIN. You can
retrieve this PIN from the user to use as the verifier::

    verifier = input("Input PIN: ")
    access_token, access_token_secret = oauth1_user_handler.get_access_token(
        verifier
    )

You can then use the instance of :class:`OAuth1UserHandler` and/or the
``access_token`` and ``access_token_secret``.

Reference
=========

.. autoclass:: OAuth1UserHandler
   :members:
   :member-order: bysource

.. autoclass:: OAuthHandler

.. autoclass:: OAuth2AppHandler

.. autoclass:: AppAuthHandler

.. autoclass:: OAuth2BearerHandler
   :show-inheritance:

.. autoclass:: OAuth2UserHandler
   :members:
   :member-order: bysource
   :show-inheritance:
