.. _streaming_guide:

.. currentmodule:: tweepy

*********
Streaming
*********

Streams utilize Streaming HTTP protocol to deliver data through
an open, streaming API connection. Rather than delivering data in batches
through repeated requests by your client app, as might be expected from a REST
API, a single connection is opened between your app and the API, with new
results being sent through that connection whenever new matches occur. This
results in a low-latency delivery mechanism that can support very high
throughput. For further information, see
https://developer.twitter.com/en/docs/tutorials/consuming-streaming-data

:class:`Stream` allows `filtering <v1.1 filtering_>`_ and
`sampling <v1.1 sampling_>`_ of realtime Tweets using Twitter API v1.1.

:class:`StreamingClient` allows `filtering <v2 filtering_>`_ and
`sampling <v2 sampling_>`_ of realtime Tweets using Twitter API v2.

.. _v1.1 filtering: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/filter-realtime/overview
.. _v1.1 sampling: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/sample-realtime/overview
.. _v2 filtering: https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/introduction
.. _v2 sampling: https://developer.twitter.com/en/docs/twitter-api/tweets/volume-streams/introduction

Using :class:`Stream`
=====================

To use :class:`Stream`, an instance of it needs to be initialized with Twitter
API credentials (Consumer Key, Consumer Secret, Access Token, Access Token
Secret)::

    import tweepy

    stream = tweepy.Stream(
        "Consumer Key here", "Consumer Secret here",
        "Access Token here", "Access Token Secret here"
    )

Then, :meth:`Stream.filter` or :meth:`Stream.sample` can be used to connect to
and run a stream::

    stream.filter(track=["Tweepy"])

Data received from the stream is passed to :meth:`Stream.on_data`. This method
handles sending the data to other methods based on the message type. For
example, if a Tweet is received from the stream, the raw data is sent to
:meth:`Stream.on_data`, which constructs a :class:`Status` object and passes it
to :meth:`Stream.on_status`. By default, the other methods, besides
:meth:`Stream.on_data`, that receive the data from the stream, simply log the
data received, with the :ref:`logging level <python:levels>` dependent on the
type of the data.

To customize the processing of the stream data, :class:`Stream` needs to be
subclassed. For example, to print the IDs of every Tweet received::

    class IDPrinter(tweepy.Stream):

        def on_status(self, status):
            print(status.id)


    printer = IDPrinter(
        "Consumer Key here", "Consumer Secret here",
        "Access Token here", "Access Token Secret here"
    )
    printer.sample()

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
:meth:`Stream.filter`, :meth:`Stream.sample`, :meth:`StreamingClient.filter`,
and :meth:`StreamingClient.sample` all have a ``threaded`` parameter. When set
to ``True``, the stream will run in a separate
:ref:`thread <python:thread-objects>`, which is returned by the call to the
method. For example::

    thread = stream.filter(follow=[1072250532645998596], threaded=True)

or::

    thread = streaming_client.sample(threaded=True)

Handling Errors
===============
Both :class:`Stream` and :class:`StreamingClient` have multiple methods to
handle errors during streaming.

:meth:`Stream.on_closed` / :meth:`StreamingClient.on_closed` is called when the
stream is closed by Twitter.

:meth:`Stream.on_connection_error` /
:meth:`StreamingClient.on_connection_error` is called when the stream
encounters a connection error.

:meth:`Stream.on_request_error` / :meth:`StreamingClient.on_request_error` is
called when an error is encountered while trying to connect to the stream.

When these errors are encountered and ``max_retries``, which defaults to
infinite, hasn't been exceeded yet, the :class:`Stream` /
:class:`StreamingClient` instance will attempt to reconnect the stream after an
appropriate amount of time. By default, both versions of all three of these
methods log an error. To customize that handling, they can be overridden in a
subclass::

    class ConnectionTester(tweepy.Stream):

        def on_connection_error(self):
            self.disconnect()

::

    class ConnectionTester(tweepy.StreamingClient):

        def on_connection_error(self):
            self.disconnect()

:meth:`Stream.on_request_error` / :meth:`StreamingClient.on_request_error` is
also passed the HTTP status code that was encountered. The HTTP status codes
reference for the Twitter API can be found at
https://developer.twitter.com/en/support/twitter-api/error-troubleshooting.

:meth:`Stream.on_exception` / :meth:`StreamingClient.on_exception` is called
when an unhandled exception occurs. This is fatal to the stream, and by
default, an exception is logged.
