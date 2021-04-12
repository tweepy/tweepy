.. _streaming_guide:

.. currentmodule:: tweepy

*********
Streaming
*********

:class:`Stream` allows `filtering`_ and `sampling`_ of realtime Tweets using
Twitter's API.

.. _filtering: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/filter-realtime/overview
.. _sampling: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/sample-realtime/overview

Streams utilize Streaming HTTP protocol to deliver data through
an open, streaming API connection. Rather than delivering data in batches
through repeated requests by your client app, as might be expected from a REST
API, a single connection is opened between your app and the API, with new
results being sent through that connection whenever new matches occur. This
results in a low-latency delivery mechanism that can support very high
throughput. For futher information, see
https://developer.twitter.com/en/docs/tutorials/consuming-streaming-data

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
data received, with the `logging level`_ dependent on the type of the data.

.. _logging level: https://docs.python.org/3/howto/logging.html#logging-levels

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

Threading
=========
Both :meth:`Stream.filter` and :meth:`Stream.sample` have a ``threaded``
parameter. When set to ``True``, the stream will run in a separate `thread`_,
which is returned by the call to either method. For example::

    thread = stream.filter(follow=[1072250532645998596], threaded=True)

.. _thread: https://docs.python.org/3/library/threading.html#thread-objects

Handling Errors
===============
:class:`Stream` has multiple methods to handle errors during streaming.
:meth:`Stream.on_closed` is called when the stream is closed by Twitter.
:meth:`Stream.on_connection_error` is called when the stream encounters a
connection error. :meth:`Stream.on_request_error` is called when an error is
encountered while trying to connect to the stream. When these errors are
encountered and ``max_retries``, which defaults to infinite, hasn't been
exceeded yet, the :class:`Stream` instance will attempt to reconnect the stream
after an appropriate amount of time. By default, all three of these methods log
an error. To customize that handling, they can be overriden in a subclass::

    class ConnectionTester(tweepy.Stream):

        def on_connection_error(self):
            self.disconnect()

:meth:`Stream.on_request_error` is also passed the HTTP status code that was
encountered. The HTTP status codes reference for the Twitter API can be found
at https://developer.twitter.com/en/support/twitter-api/error-troubleshooting.

:meth:`Stream.on_exception` is called when an unhandled exception occurs. This
is fatal to the stream, and by default, an exception is logged.
