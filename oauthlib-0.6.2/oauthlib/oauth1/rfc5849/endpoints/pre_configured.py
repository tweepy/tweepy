from __future__ import absolute_import, unicode_literals

from . import RequestTokenEndpoint, AuthorizationEndpoint
from . import AccessTokenEndpoint, ResourceEndpoint


class WebApplicationServer(RequestTokenEndpoint, AuthorizationEndpoint,
        AccessTokenEndpoint, ResourceEndpoint):

    def __init__(self, request_validator):
        RequestTokenEndpoint.__init__(self, request_validator)
        AuthorizationEndpoint.__init__(self, request_validator)
        AccessTokenEndpoint.__init__(self, request_validator)
        ResourceEndpoint.__init__(self, request_validator)
