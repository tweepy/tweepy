.. _streamresponse:

.. currentmodule:: tweepy

``StreamResponse``
==================
.. autoclass:: StreamResponse
   :class-doc-from: class

   The :obj:`StreamResponse` returned by :meth:`StreamingClient.on_response` is
   a :class:`collections.namedtuple`, with ``data``, ``includes``, ``errors``,
   and ``matching_rules`` fields, corresponding with the fields in responses
   from Twitter's API.

   .. versionadded:: 4.6
