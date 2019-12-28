.. _running_tests:

*************
Running Tests
*************

These steps outline how to run tests for Tweepy:

1. Download Tweepy's source code to a directory.

2. Install from the downloaded source with the ``test`` extra, e.g.
   ``pip install .[test]``. Optionally install the ``dev`` extra as well, for
   ``tox`` and ``coverage``, e.g. ``pip install .[dev,test]``.

3. Run ``python setup.py nosetests`` or simply ``nosetests`` in the source
   directory. With the ``dev`` extra, coverage will be shown, and ``tox`` can
   also be run to test different Python versions.

To record new cassettes, the following environment variables can be used:

``TWITTER_USERNAME``
``CONSUMER_KEY``
``CONSUMER_SECRET``
``ACCESS_KEY``
``ACCESS_SECRET``
``USE_REPLAY``

Simply set ``USE_REPLAY`` to ``False`` and provide the app and account
credentials and username.
