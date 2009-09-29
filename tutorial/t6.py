import tweepy

api = tweepy.API.new(username='', password='')

""" Tutorial 6 -- Pagination

Pagination is used in the API for iterating through
lists of users, statuses, etc. Each segment of items
is called a "page". In the twitter API you control which page
you are currently on with the "page" parameter. To move forward
just increment the parameter. To move backward you just decrement it.
"""

"""
First let's do a simple loop iterating through the first
30 statuses in our "friends" timeline. We will first
do this without the Cursor helper object which we will 
demonstrate later on.
"""
print 'Pagination without Cursor...'
count = 0
current_page = 1
running = True
while running:

    page = api.friends_timeline(page=current_page)
    if len(page) == 0:
        # No more data, stop
        break
    for status in page[:30]:
        if count == 30:
            # We only want 30 statuses
            running = False
            break
        count += 1
        print status.text
    current_page += 1

print ''

"""
While the above works correctly, it does
require that we manage the pagination
manually. This is not a really pretty way to paginate.
Now we will perform the same action, but
using the Cursor object.
"""
print 'Pagination with cursor...'
cursor = tweepy.Cursor(api.friends_timeline)
for status in cursor.items(limit=30):

    print status.text

print ''

"""
As you can see this is much simpler and all the
pagination is managed for us automatically.
We pass into the Cursor constructor the API method
we wish to paginate. Cursor then has two methods that returns
an iterator:
    Cursor.items()  -- iterate item by item until limit is reached
    Cursor.pages()  -- iterate page by page until limit is reached

If limit is not specified iteration will continue until twitter
stops sending us pages (pagination limit reached or no more data).
The limit for items() is the maximum number of items to iterate.
For pages() limit is the maximum number of pages to iterate.
The page size varies for each API method, so read the wiki page
for more details.

Using Cursor also works for both "cursor" and "page" based pagination.
This means you get a standard interface to both methods of pagination
in your code. So if twitter changes future methods to "cursor" based
you only need to update Tweepy.
"""

"""
Let's do one more example, this time iterating by "pages".
"""
print 'Pagination of friends ids page by page...'
cursor = tweepy.Cursor(api.friends_ids)
for page in cursor.pages():

    print page

print ''

# TODO: demo next() and prev()
