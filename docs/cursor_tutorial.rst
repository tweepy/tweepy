.. _cursor_tutorial:

***************
Cursor Tutorial
***************

This tutorial describes details on pagination with Cursor objects.

Introduction
============

We use pagination a lot in Twitter API development. Iterating through
timelines, user lists, direct messages, etc. In order to perform
pagination we must supply a page/cursor parameter with each of our
requests. The problem here is this requires a lot of boiler plate code
just to manage the pagination loop. To help make pagination easier and
require less code Tweepy has the Cursor object.

Old way vs Cursor way
---------------------

First let's demonstrate iterating the statues in the authenticated
user's timeline. Here is how we would do it the "old way" before
Cursor object was introduced::

   page = 1
   while True:
       statuses = api.user_timeline(page=page)
       if statuses:
           for status in statuses:
               # process status here
               process_status(status)
       else:
           # All done
           break
       page += 1  # next page

As you can see we must manage the "page" parameter manually in our
pagination loop. Now here is the version of the code using Cursor
object::

   for status in tweepy.Cursor(api.user_timeline).items():
       # process status here
       process_status(status)

Now that looks much better! Cursor handles all the pagination work for
us behind the scene so our code can now focus entirely on processing
the results.

Passing parameters into the API method
--------------------------------------

What if you need to pass in parameters to the API method?

.. code-block :: python

   api.user_timeline(id="twitter")

Since we pass Cursor the callable, we can not pass the parameters
directly into the method. Instead we pass the parameters into the
Cursor constructor method::

   tweepy.Cursor(api.user_timeline, id="twitter")

Now Cursor will pass the parameter into the method for us when ever it
makes a request.

Items or Pages
--------------

So far we have just demonstrated pagination iterating per an
item. What if instead you want to process per a page of results? You
would use the pages() method::

   for page in tweepy.Cursor(api.user_timeline).pages():
       # page is a list of statuses
       process_page(page)


Limits
------

What if you only want n items or pages returned? You pass into the items() or pages() methods the limit you want to impose.

.. code-block :: python

   # Only iterate through the first 200 statuses
   for status in tweepy.Cursor(api.user_timeline).items(200):
       process_status(status)
   
   # Only iterate through the first 3 pages
   for page in tweepy.Cursor(api.user_timeline).pages(3):
       process_page(page)
