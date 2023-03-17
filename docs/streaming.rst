.. _streaming_guide:

.. currentmodule:: tweepy

*********
Streaming
*********

Using :class:`StreamingClient`
==============================

To use :class:`StreamingClient`, an instance of it needs to be initialized with
a Twitter API Bearer Token::

    import tweepy

    streaming_client = tweepy.StreamingClient("Bearer Token here")

Then, :meth:`StreamingClient.sample` can be used to connect to and run a
sampling stream::

    streaming_client.sample()

Or :meth:`StreamingClient.add_rules` can be used to add rules before using
:meth:`StreamingClient.filter` to connect to and run a filtered stream::

    streaming_client.add_rules(tweepy.StreamRule("Tweepy"))
    streaming_client.filter()

:meth:`StreamingClient.get_rules` can be used to retrieve existing rules and
:meth:`StreamingClient.delete_rules` can be used to delete rules.

To learn how build rules, refer to the Twitter API
`Building rules for filtered stream`_ documentation.

.. _Building rules for filtered stream: https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/integrate/build-a-rule

Data received from the stream is passed to :meth:`StreamingClient.on_data`.
This method handles sending the data to other methods. Tweets recieved are sent
to :meth:`StreamingClient.on_tweet`, ``includes`` data are sent to
:meth:`StreamingClient.on_includes`, errors are sent to
:meth:`StreamingClient.on_errors`, and matching rules are sent to
:meth:`StreamingClient.on_matching_rules`. A :class:`StreamResponse` instance
containing all four fields is sent to :meth:`StreamingClient.on_response`. By
default, only :meth:`StreamingClient.on_response` logs the data received, at
the ``DEBUG`` :ref:`logging level <python:levels>`.

To customize the processing of the stream data, :class:`StreamingClient` needs to be
subclassed. For example, to print the IDs of every Tweet received::

    class IDPrinter(tweepy.StreamingClient):

        def on_tweet(self, tweet):
            print(tweet.id)


    printer = IDPrinter("Bearer Token here")
    printer.sample()

Threading
=========
:meth:`StreamingClient.filter` and :meth:`StreamingClient.sample` have a
``threaded`` parameter. When set to ``True``, the stream will run in a separate
:ref:`thread <python:thread-objects>`, which is returned by the call to the
method. For example::

    thread = streaming_client.sample(threaded=True)

Handling Errors
===============
:class:`StreamingClient` has multiple methods to handle errors during
streaming.

:meth:`StreamingClient.on_closed` is called when the stream is closed by
Twitter.

:meth:`StreamingClient.on_connection_error` is called when the stream
encounters a connection error.

:meth:`StreamingClient.on_request_error` is called when an error is encountered
while trying to connect to the stream.

When these errors are encountered and ``max_retries``, which defaults to
infinite, hasn't been exceeded yet, the :class:`StreamingClient` instance will
attempt to reconnect the stream after an appropriate amount of time. By
default, all three of these methods log an error. To customize that handling,
they can be overridden in a subclass::

    class ConnectionTester(tweepy.StreamingClient):

        def on_connection_error(self):
            self.disconnect()

:meth:`StreamingClient.on_request_error` is also passed the HTTP status code
that was encountered. The HTTP status codes reference for the Twitter API can
be found at
https://developer.twitter.com/en/support/twitter-api/error-troubleshooting.

:meth:`StreamingClient.on_exception` is called when an unhandled exception
occurs. This is fatal to the stream, and by default, an exception is logged.
