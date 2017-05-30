Requests-OAuthlib
=================

This project provides first-class OAuth library support for `Requests <http://python-requests.org>`_.

The OAuth 1 workflow
--------------------

OAuth 1 can seem overly complicated and it sure has its quirks. Luckily,
requests_oauthlib hides most of these and let you focus at the task at hand.

Accessing protected resources using requests_oauthlib is as simple as:

.. code-block:: pycon

    >>> from requests_oauthlib import OAuth1Session
    >>> twitter = OAuth1Session('client_key',
                                client_secret='client_secret',
                                resource_owner_key='resource_owner_key',
                                resource_owner_secret='resource_owner_secret')
    >>> url = 'https://api.twitter.com/1/account/settings.json'
    >>> r = twitter.get(url)

Before accessing resources you will need to obtain a few credentials from your
provider (i.e. Twitter) and authorization from the user for whom you wish to
retrieve resources for. You can read all about this in the full
`OAuth 1 workflow guide on RTD <http://requests-oauthlib.readthedocs.org/en/latest/oauth1_workflow.html>`_.

The OAuth 2 workflow
--------------------

OAuth 2 is generally simpler than OAuth 1 but comes in more flavours. The most
common being the Authorization Code Grant, also known as the WebApplication
flow.

Fetching a protected resource after obtaining an access token can be as simple as:

.. code-block:: pycon

    >>> from requests_oauthlib import OAuth2Session
    >>> google = OAuth2Session(r'client_id', token=r'token')
    >>> url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    >>> r = google.get(url)

Before accessing resources you will need to obtain a few credentials from your
provider (i.e. Google) and authorization from the user for whom you wish to
retrieve resources for. You can read all about this in the full
`OAuth 2 workflow guide on RTD <http://requests-oauthlib.readthedocs.org/en/latest/oauth2_workflow.html>`_.

Installation
-------------

To install requests and requests_oauthlib you can use pip:

.. code-block:: bash

    $ pip install requests requests_oauthlib
