.. _logging:

*******
Logging
*******

Tweepy uses the :mod:`logging` standard library module.

The simplest way to set up logging is using :func:`logging.basicConfig`, e.g.::

    import logging
    
    logging.basicConfig(level=logging.DEBUG)

This will output logging from Tweepy, as well as other libraries (like Tweepy's
dependencies) that use the :mod:`logging` module, directly to the console.

The optional ``level`` argument can be any
:ref:`logging level <python:levels>`.

To configure logging for Tweepy (or each individual library) specifically, you
can use :func:`logging.getLogger` to retrieve the logger for the library. For
example::

    import logging
    
    logger = logging.getLogger("tweepy")
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename="tweepy.log")
    logger.addHandler(handler)

More advanced configuration is possible with the :mod:`logging` module.
For more information, see the
:doc:`logging module documentation <python:library/logging>` and
:doc:`tutorials <python:howto/logging>`.
