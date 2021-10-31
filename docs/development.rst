.. _development:

***********
Development
***********

Running Tests
=============

These steps outline how to run tests for Tweepy:

1. Download Tweepy's source code to a directory.

2. Install from the downloaded source with the ``test`` extra, e.g.
   ``pip install .[test]``. Optionally install the ``dev`` extra as well, for
   ``tox`` and ``coverage``, e.g. ``pip install .[dev,test]``.

3. Run tests (e.g. ``python -m unittest discover tests``) in the source
   directory. With the ``dev`` extra, coverage can be measured by using
   ``coverage run`` (e.g. ``coverage run -m unittest discover tests``) and
   ``tox`` can be run to test different Python versions.

To record new cassettes, the following environment variables can be used:

``TWITTER_USERNAME``
``BEARER_TOKEN``
``CONSUMER_KEY``
``CONSUMER_SECRET``
``ACCESS_KEY``
``ACCESS_SECRET``
``USE_REPLAY``

Simply set ``USE_REPLAY`` to ``False`` and provide the app and account
credentials and username.

Contributors
============

Tweepy's contributors can be identified through the `GitHub repository`_'s
`contributors graph page`_, `commit history`_, `issues`_, `pull requests`_, and
`discussions`_.

.. _GitHub repository: https://github.com/tweepy/tweepy
.. _contributors graph page: https://github.com/tweepy/tweepy/graphs/contributors
.. _commit history: https://github.com/tweepy/tweepy/commits/master
.. _issues: https://github.com/tweepy/tweepy/issues?q=is%3Aissue
.. _pull requests: https://github.com/tweepy/tweepy/pulls?q=is%3Apr
.. _discussions: https://github.com/tweepy/tweepy/discussions
