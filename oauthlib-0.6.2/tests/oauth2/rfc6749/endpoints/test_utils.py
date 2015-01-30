try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse


def get_query_credentials(uri):
    return urlparse.parse_qs(urlparse.urlparse(uri).query,
            keep_blank_values=True)


def get_fragment_credentials(uri):
    return urlparse.parse_qs(urlparse.urlparse(uri).fragment,
            keep_blank_values=True)
