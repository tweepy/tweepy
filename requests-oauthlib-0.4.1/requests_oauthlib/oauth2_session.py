from __future__ import unicode_literals

import logging

from oauthlib.common import generate_token, urldecode
from oauthlib.oauth2 import WebApplicationClient, InsecureTransportError
from oauthlib.oauth2 import TokenExpiredError, is_secure_transport
import requests

log = logging.getLogger(__name__)


class TokenUpdated(Warning):
    def __init__(self, token):
        super(TokenUpdated, self).__init__()
        self.token = token


class OAuth2Session(requests.Session):
    """Versatile OAuth 2 extension to :class:`requests.Session`.

    Supports any grant type adhering to :class:`oauthlib.oauth2.Client` spec
    including the four core OAuth 2 grants.

    Can be used to create authorization urls, fetch tokens and access protected
    resources using the :class:`requests.Session` interface you are used to.

    - :class:`oauthlib.oauth2.WebApplicationClient` (default): Authorization Code Grant
    - :class:`oauthlib.oauth2.MobileApplicationClient`: Implicit Grant
    - :class:`oauthlib.oauth2.LegacyApplicationClient`: Password Credentials Grant
    - :class:`oauthlib.oauth2.BackendApplicationClient`: Client Credentials Grant

    Note that the only time you will be using Implicit Grant from python is if
    you are driving a user agent able to obtain URL fragments.
    """

    def __init__(self, client_id=None, client=None, auto_refresh_url=None,
            auto_refresh_kwargs=None, scope=None, redirect_uri=None, token=None,
            state=None, token_updater=None, **kwargs):
        """Construct a new OAuth 2 client session.

        :param client_id: Client id obtained during registration
        :param client: :class:`oauthlib.oauth2.Client` to be used. Default is
                       WebApplicationClient which is useful for any
                       hosted application but not mobile or desktop.
        :param scope: List of scopes you wish to request access to
        :param redirect_uri: Redirect URI you registered as callback
        :param token: Token dictionary, must include access_token
                      and token_type.
        :param state: State string used to prevent CSRF. This will be given
                      when creating the authorization url and must be supplied
                      when parsing the authorization response.
                      Can be either a string or a no argument callable.
        :auto_refresh_url: Refresh token endpoint URL, must be HTTPS. Supply
                           this if you wish the client to automatically refresh
                           your access tokens.
        :auto_refresh_kwargs: Extra arguments to pass to the refresh token
                              endpoint.
        :token_updater: Method with one argument, token, to be used to update
                        your token databse on automatic token refresh. If not
                        set a TokenUpdated warning will be raised when a token
                        has been refreshed. This warning will carry the token
                        in its token argument.
        :param kwargs: Arguments to pass to the Session constructor.
        """
        super(OAuth2Session, self).__init__(**kwargs)
        self.client_id = client_id or client.client_id
        self.scope = scope
        self.redirect_uri = redirect_uri
        self.token = token or {}
        self.state = state or generate_token
        self._state = state
        self.auto_refresh_url = auto_refresh_url
        self.auto_refresh_kwargs = auto_refresh_kwargs or {}
        self.token_updater = token_updater
        self._client = client or WebApplicationClient(client_id, token=token)
        self._client._populate_attributes(token or {})

        # Allow customizations for non compliant providers through various
        # hooks to adjust requests and responses.
        self.compliance_hook = {
            'access_token_response': set([]),
            'refresh_token_response': set([]),
            'protected_request': set([]),
        }

    def new_state(self):
        """Generates a state string to be used in authorizations."""
        try:
            self._state = self.state()
            log.debug('Generated new state %s.', self._state)
        except TypeError:
            self._state = self.state
            log.debug('Re-using previously supplied state %s.', self._state)
        return self._state

    def authorization_url(self, url, state=None, **kwargs):
        """Form an authorization URL.

        :param url: Authorization endpoint url, must be HTTPS.
        :param state: An optional state string for CSRF protection. If not
                      given it will be generated for you.
        :param kwargs: Extra parameters to include.
        :return: authorization_url, state
        """
        state = state or self.new_state()
        return self._client.prepare_request_uri(url,
                redirect_uri=self.redirect_uri,
                scope=self.scope,
                state=state,
                **kwargs), state

    def fetch_token(self, token_url, code=None, authorization_response=None,
            body='', auth=None, username=None, password=None, method='POST',
            verify=True, **kwargs):
        """Generic method for fetching an access token from the token endpoint.

        If you are using the MobileApplicationClient you will want to use
        token_from_fragment instead of fetch_token.

        :param token_url: Token endpoint URL, must use HTTPS.
        :param code: Authorization code (used by WebApplicationClients).
        :param authorization_response: Authorization response URL, the callback
                                       URL of the request back to you. Used by
                                       WebApplicationClients instead of code.
        :param body: Optional application/x-www-form-urlencoded body to add the
                     include in the token request. Prefer kwargs over body.
        :param auth: An auth tuple or method as accepted by requests.
        :param username: Username used by LegacyApplicationClients.
        :param password: Password used by LegacyApplicationClients.
        :param method: The HTTP method used to make the request. Defaults
                       to POST, but may also be GET. Other methods should
                       be added as needed.
        :param verify: Verify SSL certificate.
        :param kwargs: Extra parameters to include in the token request.
        :return: A token dict
        """
        if not is_secure_transport(token_url):
            raise InsecureTransportError()

        if not code and authorization_response:
            self._client.parse_request_uri_response(authorization_response,
                    state=self._state)
            code = self._client.code
        elif not code and isinstance(self._client, WebApplicationClient):
            code = self._client.code
            if not code:
                raise ValueError('Please supply either code or '
                                 'authorization_code parameters.')


        body = self._client.prepare_request_body(code=code, body=body,
                redirect_uri=self.redirect_uri, username=username,
                password=password, **kwargs)

        if method.upper() == 'POST':
            r = self.post(token_url, data=dict(urldecode(body)),
                headers={'Accept': 'application/json'}, auth=auth,
                verify=verify)
            log.debug('Prepared fetch token request body %s', body)
        elif method.upper() == 'GET':
            # if method is not 'POST', switch body to querystring and GET
            r = self.get(token_url, params=dict(urldecode(body)),
                headers={'Accept': 'application/json'}, auth=auth,
                verify=verify)
            log.debug('Prepared fetch token request querystring %s', body)
        else:
            raise ValueError('The method kwarg must be POST or GET.')

        log.debug('Request to fetch token completed with status %s.',
                  r.status_code)
        log.debug('Response headers were %s and content %s.',
                  r.headers, r.text)
        log.debug('Invoking %d token response hooks.',
                  len(self.compliance_hook['access_token_response']))
        for hook in self.compliance_hook['access_token_response']:
            log.debug('Invoking hook %s.', hook)
            r = hook(r)

        self._client.parse_request_body_response(r.text, scope=self.scope)
        self.token = self._client.token
        log.debug('Obtained token %s.', self.token)
        return self.token

    def token_from_fragment(self, authorization_response):
        """Parse token from the URI fragment, used by MobileApplicationClients.

        :param authorization_response: The full URL of the redirect back to you
        :return: A token dict
        """
        self._client.parse_request_uri_response(authorization_response,
                state=self._state)
        self.token = self._client.token
        return self.token

    def refresh_token(self, token_url, refresh_token=None, body='', auth=None,
                      **kwargs):
        """Fetch a new access token using a refresh token.

        :param token_url: The token endpoint, must be HTTPS.
        :param refresh_token: The refresh_token to use.
        :param body: Optional application/x-www-form-urlencoded body to add the
                     include in the token request. Prefer kwargs over body.
        :param auth: An auth tuple or method as accepted by requests.
        :param kwargs: Extra parameters to include in the token request.
        :return: A token dict
        """
        if not token_url:
            raise ValueError('No token endpoint set for auto_refresh.')

        if not is_secure_transport(token_url):
            raise InsecureTransportError()

        # Need to nullify token to prevent it from being added to the request
        refresh_token = refresh_token or self.token.get('refresh_token')
        self.token = {}

        log.debug('Adding auto refresh key word arguments %s.',
                  self.auto_refresh_kwargs)
        kwargs.update(self.auto_refresh_kwargs)
        body = self._client.prepare_refresh_body(body=body,
                refresh_token=refresh_token, scope=self.scope, **kwargs)
        log.debug('Prepared refresh token request body %s', body)
        r = self.post(token_url, data=dict(urldecode(body)), auth=auth)
        log.debug('Request to refresh token completed with status %s.',
                  r.status_code)
        log.debug('Response headers were %s and content %s.',
                  r.headers, r.text)
        log.debug('Invoking %d token response hooks.',
                  len(self.compliance_hook['refresh_token_response']))
        for hook in self.compliance_hook['refresh_token_response']:
            log.debug('Invoking hook %s.', hook)
            r = hook(r)

        self.token = self._client.parse_request_body_response(r.text, scope=self.scope)
        if not 'refresh_token' in self.token:
            log.debug('No new refresh token given. Re-using old.')
            self.token['refresh_token'] = refresh_token
        return self.token

    def request(self, method, url, data=None, headers=None, **kwargs):
        """Intercept all requests and add the OAuth 2 token if present."""
        if not is_secure_transport(url):
            raise InsecureTransportError()
        if self.token:
            log.debug('Invoking %d protected resource request hooks.',
                      len(self.compliance_hook['protected_request']))
            for hook in self.compliance_hook['protected_request']:
                log.debug('Invoking hook %s.', hook)
                url, headers, data = hook(url, headers, data)

            log.debug('Adding token %s to request.', self.token)
            try:
                url, headers, data = self._client.add_token(url,
                        http_method=method, body=data, headers=headers)
            # Attempt to retrieve and save new access token if expired
            except TokenExpiredError:
                if self.auto_refresh_url:
                    log.debug('Auto refresh is set, attempting to refresh at %s.',
                              self.auto_refresh_url)
                    token = self.refresh_token(self.auto_refresh_url)
                    if self.token_updater:
                        log.debug('Updating token to %s using %s.',
                                  token, self.token_updater)
                        self.token_updater(token)
                        url, headers, data = self._client.add_token(url,
                                http_method=method, body=data, headers=headers)
                    else:
                        raise TokenUpdated(token)
                else:
                    raise

        log.debug('Requesting url %s using method %s.', url, method)
        log.debug('Supplying headers %s and data %s', headers, data)
        log.debug('Passing through key word arguments %s.', kwargs)
        return super(OAuth2Session, self).request(method, url,
                headers=headers, data=data, **kwargs)

    def register_compliance_hook(self, hook_type, hook):
        """Register a hook for request/response tweaking.

        Available hooks are:
            access_token_response invoked before token parsing.
            refresh_token_response invoked before refresh token parsing.
            protected_request invoked before making a request.

        If you find a new hook is needed please send a GitHub PR request
        or open an issue.
        """
        if hook_type not in self.compliance_hook:
            raise ValueError('Hook type %s is not in %s.',
                             hook_type, self.compliance_hook)
        self.compliance_hook[hook_type].add(hook)
