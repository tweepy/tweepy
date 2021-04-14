.. API parameters:

.. |additional_owners| replace:: A list of user IDs to set as additional owners allowed to use the returned ``media_id`` in Tweet or Cards. Up to 100 additional owners may be specified.
.. |count| replace:: The number of results to try and retrieve per page.
.. |cursor| replace:: Breaks the results into pages. Provide a value of  -1 to begin paging. Provide values as returned to in the response body's next_cursor and previous_cursor attributes to page back and forth in the list.
.. |date| replace:: Permits specifying a start date for the report. The date should be formatted YYYY-MM-DD.
.. |exclude| replace:: Setting this equal to hashtags will remove all hashtags from the trends list.
.. |exclude_replies| replace:: This parameter will prevent replies from appearing in the returned timeline. Using ``exclude_replies`` with the ``count`` parameter will mean you will receive up-to count Tweets — this is because the ``count`` parameter retrieves that many Tweets before filtering out retweets and replies.
.. |file| replace:: A file object, which will be used instead of opening ``filename``. ``filename`` is still required, for MIME type detection and to use as a form field in the POST data.
.. |filename| replace:: The filename of the image to upload. This will automatically be opened unless ``file`` is specified.
.. |full_text| replace:: A boolean indicating whether or not the full text of a message should be returned. If False the message text returned will be truncated to 140 chars. Defaults to False.
.. |include_card_uri| replace:: A boolean indicating if the retrieved Tweet should include a card_uri attribute when there is an ads card attached to the Tweet and when that card was attached using the card_uri value.
.. |include_entities| replace:: The entities node will not be included when set to false. Defaults to true.
.. |include_ext_alt_text| replace:: If alt text has been added to any attached media entities, this parameter will return an ext_alt_text value in the top-level key for the media entity.
.. |include_user_entities| replace:: The user object entities node will not be included when set to false. Defaults to true.
.. |list_id| replace:: The numerical id of the list.
.. |list_mode| replace:: Whether your list is public or private. Values can be public or private. Lists are public by default if no mode is specified.
.. |list_owner| replace:: the screen name of the owner of the list
.. |media_category| replace:: The category that represents how the media will be used. This field is required when using the media with the Ads API.
.. |max_id| replace:: Returns only statuses with an ID less than (that is, older than) or equal to the specified ID.
.. |owner_id| replace:: The user ID of the user who owns the list being requested by a slug.
.. |owner_screen_name| replace:: The screen name of the user who owns the list being requested by a slug.
.. |page| replace:: Specifies the page of results to retrieve. Note: there are pagination limits.
.. |screen_name| replace:: Specifies the screen name of the user. Helpful for disambiguating when a valid screen name is also a user ID.
.. |sid| replace:: The numerical ID of the status.
.. |since_id| replace:: Returns only statuses with an ID greater than (that is, more recent than) the specified ID.
.. |skip_status| replace:: A boolean indicating whether statuses will not be included in the returned user objects. Defaults to false.
.. |slug| replace:: You can identify a list by its slug instead of its numerical id. If you decide to do so, note that you'll also have to specify the list owner using the owner_id or owner_screen_name parameters.
.. |stringify_ids| replace:: Have IDs returned as strings instead
.. |trim_user| replace:: A boolean indicating if user IDs should be provided, instead of complete user objects. Defaults to False.
.. |uid| replace:: Specifies the ID or screen name of the user.
.. |user_id| replace:: Specifies the ID of the user. Helpful for disambiguating when a valid user ID is also a valid screen name.

