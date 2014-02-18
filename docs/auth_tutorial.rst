.. _auth_tutorial:


***********************
Authentication Tutorial
***********************

Introduction
============

Tweepy supports oauth authentication. Authentication is
handled by the tweepy.AuthHandler class.

OAuth Authentication
====================

Tweepy tries to make OAuth as painless as possible for you. To begin
the process we need to register our client application with
Twitter. Create a new application and once you
are done you should have your consumer token and secret. Keep these
two handy, you'll need them.

The next step is creating an OAuthHandler instance. Into this we pass
our consumer token and secret which was given to us in the previous
paragraph::

   auth = tweepy.OAuthHandler(consumer_token, consumer_secret)

If you have a web application and are using a callback URL that needs
to be supplied dynamically you would pass it in like so::

   auth = tweepy.OAuthHandler(consumer_token, consumer_secret,
   callback_url)

If the callback URL will not be changing, it is best to just configure
it statically on twitter.com when setting up your application's
profile.

Unlike basic auth, we must do the OAuth "dance" before we can start
using the API. We must complete the following steps:

#. Get a request token from twitter

#. Redirect user to twitter.com to authorize our application

#. If using a callback, twitter will redirect the user to
   us. Otherwise the user must manually supply us with the verifier
   code.

#. Exchange the authorized request token for an access token. 

So let's fetch our request token to begin the dance::

   try:
       redirect_url = auth.get_authorization_url()
   except tweepy.TweepError:
       print 'Error! Failed to get request token.'

This call requests the token from twitter and returns to us the
authorization URL where the user must be redirect to authorize us. Now
if this is a desktop application we can just hang onto our
OAuthHandler instance until the user returns back. In a web
application we will be using a callback request. So we must store the
request token in the session since we will need it inside the callback
URL request. Here is a pseudo example of storing the request token in
a session::

   session.set('request_token', (auth.request_token.key,
   auth.request_token.secret))

So now we can redirect the user to the URL returned to us earlier from
the get_authorization_url() method.

If this is a desktop application (or any application not using
callbacks) we must query the user for the "verifier code" that twitter
will supply them after they authorize us. Inside a web application
this verifier value will be supplied in the callback request from
twitter as a GET query parameter in the URL.

.. code-block :: python

   # Example using callback (web app)
   verifier = request.GET.get('oauth_verifier')
   
   # Example w/o callback (desktop)
   verifier = raw_input('Verifier:')

The final step is exchanging the request token for an access
token. The access token is the "key" for opening the Twitter API
treasure box. To fetch this token we do the following::

   # Let's say this is a web app, so we need to re-build the auth handler
   # first...
   auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
   token = session.get('request_token')
   session.delete('request_token')
   auth.set_request_token(token[0], token[1])
   
   try:
       auth.get_access_token(verifier)
   except tweepy.TweepError:
       print 'Error! Failed to get access token.'
   
It is a good idea to save the access token for later use. You do not
need to re-fetch it each time. Twitter currently does not expire the
tokens, so the only time it would ever go invalid is if the user
revokes our application access. To store the access token depends on
your application. Basically you need to store 2 string values: key and
secret::

   auth.access_token.key
   auth.access_token.secret

You can throw these into a database, file, or where ever you store
your data. To re-build an OAuthHandler from this stored access token
you would do this::

   auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
   auth.set_access_token(key, secret)

So now that we have our OAuthHandler equipped with an access token, we
are ready for business::

   api = tweepy.API(auth)
   api.update_status('tweepy + oauth!')
