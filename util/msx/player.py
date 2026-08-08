from urllib.parse import urlencode

from config.settings import server
from util.proxy import make_proxy_url, remember_url


def player_action_btn():
    return 'panel:request:player:options'


def play_action(
    video_url,
    proxy: bool = False,
    alternative_player: bool = False
):
    url = make_proxy_url(video_url) if proxy else video_url
    # Remember the CDN domain for the domains file regardless of whether the
    # stream itself is proxied.
    remember_url(video_url)
    if alternative_player:
        # Self-hosted copy of the html5x plugin with proper track names.
        player_url = f'{server.base_url}/html5x.html'
    else:
        # Self-hosted copy of the hlsx plugin (patched track indicators).
        player_url = f'{server.base_url}/hlsx.html'

    return f'video:plugin:{player_url}?' + urlencode({'url': url})
