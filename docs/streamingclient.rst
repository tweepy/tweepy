.. _streamingclient_reference:

.. currentmodule:: tweepy

************************
:class:`StreamingClient`
************************

.. autoclass:: StreamingClient
   :members:
   :inherited-members:
   :member-order: bysource

``StreamResponse``
==================
.. autoclass:: StreamResponse

   The :obj:`StreamResponse` returned by :meth:`StreamingClient.on_response` is
   a :class:`collections.namedtuple`, with ``data``, ``includes``, ``errors``,
   and ``matching_rules`` fields, corresponding with the fields in responses
   from Twitter's API.

   .. versionadded:: 4.6

``StreamRule``
==============
.. autoclass:: StreamRule
