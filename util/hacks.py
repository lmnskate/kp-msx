from urllib.parse import urlparse

import config


def posters_fix(poster_url):
    if config.POSTERS_HOST_REPLACEMENT is not None and poster_url is not None:
        url = urlparse(poster_url)
        return poster_url.replace(url.hostname, config.POSTERS_HOST_REPLACEMENT)
    return poster_url
