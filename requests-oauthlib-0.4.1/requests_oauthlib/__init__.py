from .oauth1_auth import OAuth1
from .oauth1_session import OAuth1Session
from .oauth2_auth import OAuth2
from .oauth2_session import OAuth2Session, TokenUpdated

__version__ = '0.4.1'

import requests
if requests.__version__ < '2.0.0':
    msg = ('You are using requests version %s, which is older than '
           'requests-oauthlib expects, please upgrade to 2.0.0 or later.')
    raise Warning(msg % requests.__version__)

import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
   class NullHandler(logging.Handler):
       def emit(self, record):
           pass

logging.getLogger('requests_oauthlib').addHandler(NullHandler())
