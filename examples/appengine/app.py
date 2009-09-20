from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import sys
sys.path.insert(0, 'tweepy.zip')

import oauth_example.handlers

# Construct the WSGI application
application = webapp.WSGIApplication([

        # OAuth example
        (r'/oauth/', oauth_example.handlers.MainPage),
        (r'/oauth/callback', oauth_example.handlers.CallbackPage),

], debug=True)

def main():
    run_wsgi_app(application)

# Run the WSGI application
if __name__ == '__main__':
    main()
